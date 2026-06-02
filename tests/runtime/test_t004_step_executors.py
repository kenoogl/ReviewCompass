"""T-004 のテスト：Step A／B／C 実行器（言語モデル呼び出しを含む 3 段）。

対応タスク：runtime tasks.md T-004
対応設計節：design.md §ステップ実行モデル Step A／B／C、§プロンプト解決モデル、
          §treatment × 段実行マトリクス
対応要件：Requirement 1 受入 1〜3、Requirement 4 受入 1〜6、Requirement 6 受入 6

テスト要件（tasks.md T-004 より）：
- 3 段の入出力テスト（固定応答による決定的検証）
- Step B の counter_status 必須テスト
- Step C の final_label foundation 3 値正本テスト
"""
import json
from pathlib import Path

import pytest
import yaml
from jsonschema import Draft202012Validator

from runtime_core.step_executors.llm_invocation_boundary import (
  LLMInvocationBoundary,
  FixedResponseBoundary,
)
from runtime_core.step_executors import step_a_primary_detection as step_a
from runtime_core.step_executors import step_b_adversarial_review as step_b
from runtime_core.step_executors import step_c_judgment as step_c

REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_DIR = REPO_ROOT / "runtime/schemas"
STEP_OUTCOME_VOCAB = REPO_ROOT / "runtime/runtime_core/step_executors/step_outcome_vocab.yaml"

FINDING_SCHEMA = json.loads((SCHEMA_DIR / "finding.schema.json").read_text(encoding="utf-8"))
NECESSITY_SCHEMA = json.loads((SCHEMA_DIR / "necessity_judgment.schema.json").read_text(encoding="utf-8"))

EXPECTED_STEP_OUTCOMES = {"executed", "skipped_by_treatment", "failed"}
COUNTER_STATUS_3 = {"counter_evidence_raised", "no_counter_evidence_after_challenge", "not_assessed"}
FINAL_LABEL_3 = {"must-fix", "should-fix", "leave-as-is"}


def _prompt_identity(role):
  return {
    "prompt_artifact_path": f"runtime/prompts/{role}.prompt.md",
    "prompt_id": role,
    "prompt_version": "B1.0",
    "role": role,
  }


def _boundary():
  return FixedResponseBoundary({
    "primary_reviewer": {
      "findings": [
        {"summary": "目標が曖昧", "severity": "WARN", "source_refs": ["doc#1"]},
        {"summary": "範囲外の漏れ込み", "severity": "ERROR", "source_refs": ["doc#2"]},
      ]
    },
    "adversarial_reviewer": {
      "findings": [
        {
          "summary": "主役所見1への反証あり",
          "severity": "ERROR",
          "source_refs": ["doc#1"],
          "counter_status": "counter_evidence_raised",
          "counter_evidence_refs": ["ce#1"],
        },
        {
          "summary": "主役所見2は反証なし（挑戦後）",
          "severity": "WARN",
          "source_refs": ["doc#2"],
          "counter_status": "no_counter_evidence_after_challenge",
          "counter_evidence_refs": [],
        },
      ]
    },
    "judgment_reviewer": {
      "judgments": [
        {
          "requirement_link": "R1",
          "ignored_impact": "中",
          "fix_cost": "low",
          "scope_expansion": "none",
          "uncertainty": "low",
          "final_label": "must-fix",
          "recommended_action": "設計を修正する",
        }
      ]
    },
  })


def _run_dir(tmp_path):
  d = tmp_path / "experiments" / "runs" / "run-1"
  (d / "steps").mkdir(parents=True)
  return d


def test_step_outcome_vocab_declares_3_values():
  """step_outcome 3 値正本が宣言されている（T-011 連動）。"""
  spec = yaml.safe_load(STEP_OUTCOME_VOCAB.read_text(encoding="utf-8"))
  assert set(spec["step_outcome"]) == EXPECTED_STEP_OUTCOMES


def test_fixed_boundary_is_llm_boundary():
  """FixedResponseBoundary が差し替え点（LLMInvocationBoundary）の実装である。"""
  assert isinstance(FixedResponseBoundary({}), LLMInvocationBoundary)


def test_step_a_writes_output(tmp_path):
  """Step A が step_a_primary_detection.json を出力する（決定的検証）。"""
  run_dir = _run_dir(tmp_path)
  out = step_a.run(
    run_dir=run_dir, prompt_identity=_prompt_identity("primary_reviewer"),
    llm_boundary=_boundary(), target_artifact="本文", treatment="judgment",
    started_at="t0", closed_at="t1",
  )
  path = run_dir / "steps" / "step_a_primary_detection.json"
  assert path.is_file()
  assert out["step_outcome"] == "executed"
  assert len(out["findings"]) == 2


def test_step_a_findings_conform_to_finding_schema(tmp_path):
  """Step A の findings が foundation finding スキーマに準拠する（完了条件 1）。"""
  run_dir = _run_dir(tmp_path)
  out = step_a.run(
    run_dir=run_dir, prompt_identity=_prompt_identity("primary_reviewer"),
    llm_boundary=_boundary(), target_artifact="本文", treatment="judgment",
    started_at="t0", closed_at="t1",
  )
  validator = Draft202012Validator(FINDING_SCHEMA)
  for f in out["findings"]:
    validator.validate(f)
    assert f["source_role"] == "primary_reviewer"
    assert f["counter_status"] == "not_assessed"  # Step A では未評価


def test_review_mode_runtime_mediated_in_each_step(tmp_path):
  """各段の出力に review_mode=runtime_mediated が付与される（完了条件 3）。"""
  run_dir = _run_dir(tmp_path)
  out_a = step_a.run(
    run_dir=run_dir, prompt_identity=_prompt_identity("primary_reviewer"),
    llm_boundary=_boundary(), target_artifact="本文", treatment="judgment",
    started_at="t0", closed_at="t1",
  )
  out_b = step_b.run(
    run_dir=run_dir, prompt_identity=_prompt_identity("adversarial_reviewer"),
    llm_boundary=_boundary(), target_artifact="本文", prior_findings=out_a["findings"],
    treatment="judgment", started_at="t0", closed_at="t1",
  )
  out_c = step_c.run(
    run_dir=run_dir, prompt_identity=_prompt_identity("judgment_reviewer"),
    llm_boundary=_boundary(), prior_findings=out_a["findings"] + out_b["findings"],
    treatment="judgment", started_at="t0", closed_at="t1",
  )
  for out in (out_a, out_b, out_c):
    assert out["review_mode"] == "runtime_mediated"


def test_step_b_sets_counter_status_on_all_findings(tmp_path):
  """Step B が全所見に counter_status を 3 値正本から設定する（完了条件 2）。"""
  run_dir = _run_dir(tmp_path)
  out_b = step_b.run(
    run_dir=run_dir, prompt_identity=_prompt_identity("adversarial_reviewer"),
    llm_boundary=_boundary(), target_artifact="本文", prior_findings=[],
    treatment="adversarial", started_at="t0", closed_at="t1",
  )
  assert out_b["findings"], "Step B の findings が空"
  for f in out_b["findings"]:
    assert f["counter_status"] in COUNTER_STATUS_3, f"counter_status が 3 値外：{f['counter_status']}"


def test_step_b_rejects_missing_counter_status(tmp_path):
  """Step B は counter_status を欠く所見を拒否する（曖昧さの排除、設計 Step B）。"""
  run_dir = _run_dir(tmp_path)
  bad = FixedResponseBoundary({
    "adversarial_reviewer": {"findings": [{"summary": "x", "severity": "WARN", "source_refs": []}]}
  })
  with pytest.raises(ValueError):
    step_b.run(
      run_dir=run_dir, prompt_identity=_prompt_identity("adversarial_reviewer"),
      llm_boundary=bad, target_artifact="本文", prior_findings=[],
      treatment="adversarial", started_at="t0", closed_at="t1",
    )


def test_step_c_final_label_in_3_values(tmp_path):
  """Step C の final_label が foundation 3 値正本に属する（完了条件、テスト要件）。"""
  run_dir = _run_dir(tmp_path)
  out_c = step_c.run(
    run_dir=run_dir, prompt_identity=_prompt_identity("judgment_reviewer"),
    llm_boundary=_boundary(), prior_findings=[], treatment="judgment",
    started_at="t0", closed_at="t1",
  )
  validator = Draft202012Validator(NECESSITY_SCHEMA)
  assert out_c["judgments"]
  for j in out_c["judgments"]:
    validator.validate(j)
    assert j["final_label"] in FINAL_LABEL_3


def test_primary_treatment_skips_step_b_and_c(tmp_path):
  """primary treatment では Step B／C が省略マーカーを残す（言語モデル非起動）。"""
  run_dir = _run_dir(tmp_path)
  # 起動されたら例外を投げる空応答（included_steps 検査が先行するため起動されない）
  empty = FixedResponseBoundary({})
  out_b = step_b.run(
    run_dir=run_dir, prompt_identity=_prompt_identity("adversarial_reviewer"),
    llm_boundary=empty, target_artifact="本文", prior_findings=[],
    treatment="primary", started_at="t0", closed_at="t1",
  )
  out_c = step_c.run(
    run_dir=run_dir, prompt_identity=_prompt_identity("judgment_reviewer"),
    llm_boundary=empty, prior_findings=[], treatment="primary",
    started_at="t0", closed_at="t1",
  )
  assert out_b["step_outcome"] == "skipped_by_treatment"
  assert out_c["step_outcome"] == "skipped_by_treatment"
  assert out_b["treatment"] == "primary"
  # 省略マーカーにも理由が記録される
  assert out_b.get("reason")


def test_skip_marker_written_to_file(tmp_path):
  """省略マーカーも steps/ にファイルとして残る（実行記録での区別）。"""
  run_dir = _run_dir(tmp_path)
  step_b.run(
    run_dir=run_dir, prompt_identity=_prompt_identity("adversarial_reviewer"),
    llm_boundary=FixedResponseBoundary({}), target_artifact="本文", prior_findings=[],
    treatment="primary", started_at="t0", closed_at="t1",
  )
  path = run_dir / "steps" / "step_b_adversarial_review.json"
  assert path.is_file()
  data = json.loads(path.read_text(encoding="utf-8"))
  assert data["step_outcome"] == "skipped_by_treatment"


def test_steps_run_independently(tmp_path):
  """各段は前後段なしで単体実行できる（段入出力分離点）。"""
  run_dir = _run_dir(tmp_path)
  # Step B を Step A の出力なし（prior_findings=[]）で実行できる
  out_b = step_b.run(
    run_dir=run_dir, prompt_identity=_prompt_identity("adversarial_reviewer"),
    llm_boundary=_boundary(), target_artifact="本文", prior_findings=[],
    treatment="adversarial", started_at="t0", closed_at="t1",
  )
  assert out_b["step_outcome"] == "executed"


# ---- triad-review 機能内対処（2026-06-02、P-005／P-006）----

class _RaisingBoundary(LLMInvocationBoundary):
  """invoke で必ず例外を投げる（段実行失敗の注入）。"""

  def invoke(self, *, role, prompt=None, target_artifact=None, context=None):
    raise RuntimeError("LLM 呼び出しに失敗")


def _run_dir_with_manifest(tmp_path):
  d = _run_dir(tmp_path)
  (d / "run_manifest.yaml").write_text(
    yaml.safe_dump({"run_id": "run-1"}, allow_unicode=True), encoding="utf-8"
  )
  return d


def test_step_a_failure_writes_failed_marker(tmp_path):
  """P-005：段実行が失敗したら step_outcome=failed のマーカーを残す。"""
  run_dir = _run_dir_with_manifest(tmp_path)
  out = step_a.run(
    run_dir=run_dir, prompt_identity=_prompt_identity("primary_reviewer"),
    llm_boundary=_RaisingBoundary(), target_artifact="本文", treatment="judgment",
    started_at="t0", closed_at="t1",
  )
  assert out["step_outcome"] == "failed"
  data = json.loads((run_dir / "steps" / "step_a_primary_detection.json").read_text(encoding="utf-8"))
  assert data["step_outcome"] == "failed"


def test_step_a_failure_writes_failure_observation(tmp_path):
  """P-006：段失敗時に failure_observation を独立成果物として書き出す。"""
  run_dir = _run_dir_with_manifest(tmp_path)
  step_a.run(
    run_dir=run_dir, prompt_identity=_prompt_identity("primary_reviewer"),
    llm_boundary=_RaisingBoundary(), target_artifact="本文", treatment="judgment",
    started_at="t0", closed_at="t1",
  )
  fobs = list((run_dir / "failures" / "failure_observations").glob("*.json"))
  assert fobs, "failure_observation が書き出されていない"


def test_step_b_failure_writes_failed_marker(tmp_path):
  """P-005：Step B も実行失敗で failed マーカーを残す。"""
  run_dir = _run_dir_with_manifest(tmp_path)
  out = step_b.run(
    run_dir=run_dir, prompt_identity=_prompt_identity("adversarial_reviewer"),
    llm_boundary=_RaisingBoundary(), target_artifact="本文", prior_findings=[],
    treatment="adversarial", started_at="t0", closed_at="t1",
  )
  assert out["step_outcome"] == "failed"


def test_step_c_failure_writes_failed_marker(tmp_path):
  """P-005：Step C も実行失敗で failed マーカーを残す。"""
  run_dir = _run_dir_with_manifest(tmp_path)
  out = step_c.run(
    run_dir=run_dir, prompt_identity=_prompt_identity("judgment_reviewer"),
    llm_boundary=_RaisingBoundary(), prior_findings=[],
    treatment="judgment", started_at="t0", closed_at="t1",
  )
  assert out["step_outcome"] == "failed"
