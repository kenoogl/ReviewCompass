"""T-011 のテスト：統合テスト（design.md §テスト戦略の 5 項目を縫い合わせる）。

対応タスク：runtime tasks.md T-011
対応設計節：design.md §テスト戦略（5 項目の縫い目）
対応要件：Requirement 1 受入 1〜6 の網羅検証

5 項目の縫い目を 1 回の実行で縫い合わせて検証する：
1. 言語モデル差し替え点（FixedResponseBoundary）
2. 段入出力分離点（各段が独立にファイルを出力）
3. 決定単位生成の検証方針（Step D の機械統合）
4. 実行終了境界の順序検証（人間署名 → 凍結 → 検証器 → 終了）
5. 検証ブリッジ起動点（ValidationBridge.close_run）
"""
import json
from pathlib import Path

from jsonschema import Draft202012Validator

from runtime_core.session_controller import SessionController
from runtime_core.prompt_resolver.resolver import PromptResolver
from runtime_core.step_executors.llm_invocation_boundary import FixedResponseBoundary
from runtime_core.step_executors import step_a_primary_detection as step_a
from runtime_core.step_executors import step_b_adversarial_review as step_b
from runtime_core.step_executors import step_c_judgment as step_c
from runtime_core.step_executors import step_d_integration as step_d
from runtime_core.decisions.human_signoff_writer import HumanSignoffWriter
from runtime_core.evidence_writer.writer import EvidenceWriter
from runtime_core.validation_bridge.bridge import ValidationBridge

REPO_ROOT = Path(__file__).resolve().parents[2]
REVIEW_CASE_SCHEMA = json.loads(
  (REPO_ROOT / "runtime/schemas/review_case.schema.json").read_text(encoding="utf-8"))


def _inputs():
  return {
    "target_id": "doc-001", "target_artifact_hash": "sha256:abc",
    "source_repository_id": "repo-x", "source_revision": "rev-1",
    "phase_profile": "design", "treatment": "judgment", "review_mode": "runtime_mediated",
    "protocol_version": "p1", "runtime_version": "r1", "prompt_set_version": "ps1",
    "schema_set_version": "ss1", "config_version": "c1", "config_hash": "sha256:cfg",
    "operator_id": "operator-1",
  }


def _boundary():
  return FixedResponseBoundary({
    "primary_reviewer": {"findings": [
      {"summary": "責務境界が曖昧", "severity": "ERROR", "source_refs": ["doc#R1"]}]},
    "adversarial_reviewer": {"findings": [
      {"summary": "反証あり", "severity": "WARN", "source_refs": ["doc#R1"],
       "counter_status": "counter_evidence_raised", "counter_evidence_refs": ["ce#1"]}]},
    "judgment_reviewer": {"judgments": [
      {"requirement_link": "R1", "ignored_impact": "中", "fix_cost": "low",
       "scope_expansion": "none", "uncertainty": "low", "final_label": "must-fix",
       "recommended_action": "修正", "finding_refs": ["step_a-f0", "step_b-f0"]}]},
  })


def _validator(run_dir):
  return {"run_id": "run-int", "validator_status": "passed", "checked_contract": "review_case",
          "error_list": [], "validated_by": "validator", "validated_at": "t2"}


def _run_full_pipeline(tmp_path):
  """全コンポーネントを縫い合わせて 1 実行を完走させ、中間結果を返す。"""
  controller = SessionController(run_root_base=tmp_path)
  run_dir = controller.start_session(session_inputs=_inputs(), run_id="run-int",
                                     started_at="2026-06-02T00:00:00+09:00")
  controller.transition_status(run_dir, "in_progress")

  resolver = PromptResolver(repo_root=REPO_ROOT)
  boundary = _boundary()
  pa = resolver.resolve("primary_reviewer", phase_profile="design")
  pb = resolver.resolve("adversarial_reviewer", phase_profile="design")
  pc = resolver.resolve("judgment_reviewer", phase_profile="design")

  out_a = step_a.run(run_dir=run_dir, prompt_identity=pa, llm_boundary=boundary,
                     target_artifact="本文", treatment="judgment", started_at="t0", closed_at="t1")
  out_b = step_b.run(run_dir=run_dir, prompt_identity=pb, llm_boundary=boundary,
                     target_artifact="本文", prior_findings=out_a["findings"],
                     treatment="judgment", started_at="t0", closed_at="t1")
  out_c = step_c.run(run_dir=run_dir, prompt_identity=pc, llm_boundary=boundary,
                     prior_findings=out_a["findings"] + out_b["findings"],
                     treatment="judgment", started_at="t0", closed_at="t1")
  out_d = step_d.run(run_dir=run_dir, step_a_output=out_a, step_b_output=out_b,
                     step_c_output=out_c, treatment="judgment", started_at="t0", closed_at="t1")

  HumanSignoffWriter().write(run_dir, run_id="run-int", human_signoff_status="approved",
                             signed_off_by="operator-1", signed_off_at="t1.5",
                             covered_decision_unit_ids=[u["decision_unit_id"] for u in out_d["decision_units"]])

  bridge = ValidationBridge(run_dir, validator_callable=_validator)
  result = bridge.close_run()

  review_case = EvidenceWriter(run_dir).project_to_review_case()
  return {"run_dir": run_dir, "out_a": out_a, "out_b": out_b, "out_c": out_c,
          "out_d": out_d, "close_result": result, "review_case": review_case, "boundary": boundary}


def test_full_pipeline_reaches_valid(tmp_path):
  """全段を縫い合わせた実行が evidence_class=valid・run_status=closed に到達する。"""
  r = _run_full_pipeline(tmp_path)
  assert r["close_result"]["evidence_class"] == "valid"
  assert r["close_result"]["run_status"] == "closed"


def test_seam_step_io_separation(tmp_path):
  """縫い目2：各段が独立に steps/ へファイルを出力する。"""
  r = _run_full_pipeline(tmp_path)
  steps = r["run_dir"] / "steps"
  for name in ("step_a_primary_detection.json", "step_b_adversarial_review.json",
               "step_c_judgment.json", "step_d_integration.json"):
    assert (steps / name).is_file(), f"段ファイル欠落：{name}"


def test_seam_decision_units_generated(tmp_path):
  """縫い目3：Step D の機械統合で決定単位が生成される。"""
  r = _run_full_pipeline(tmp_path)
  assert r["out_d"]["decision_units"], "決定単位が空"
  assert (r["run_dir"] / "decisions" / "decision_units.json").is_file()


def test_seam_run_close_order(tmp_path):
  """縫い目4：実行終了境界の順序（署名 → 凍結 → 検証 → 終了）が観測可能。"""
  r = _run_full_pipeline(tmp_path)
  run_dir = r["run_dir"]
  import yaml
  manifest = yaml.safe_load((run_dir / "run_manifest.yaml").read_text(encoding="utf-8"))
  # 署名 → 検証器結果 → 終了 の痕跡がすべて残る
  assert (run_dir / "decisions" / "human_signoff.json").is_file()  # 署名
  assert manifest.get("closed_at")                                  # 凍結マーカー
  assert (run_dir / "validation" / "validator_result.json").is_file()  # 検証器結果
  assert manifest["run_status"] == "closed"                         # 終了


def test_seam_review_case_schema_conformance(tmp_path):
  """縫い目（総合）：最終 review_case.json が foundation スキーマに準拠する。"""
  r = _run_full_pipeline(tmp_path)
  Draft202012Validator(REVIEW_CASE_SCHEMA).validate(r["review_case"])
  # 検証器結果への参照が投影されている
  assert r["review_case"]["validator_result_refs"]


def test_seam_llm_boundary_swappable(tmp_path):
  """縫い目1：言語モデル呼び出しが差し替え点経由（固定応答で決定的）。"""
  r = _run_full_pipeline(tmp_path)
  # review_mode は runtime_mediated（実モデルでなく差し替え点を通っても付与は同じ契約）
  assert r["out_a"]["review_mode"] == "runtime_mediated"
  # 固定応答により主役所見が決定的に 1 件
  assert len(r["out_a"]["findings"]) == 1
