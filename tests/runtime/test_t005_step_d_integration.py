"""T-005 のテスト：Step D 実行器（機械統合、言語モデル非依存）。

対応タスク：runtime tasks.md T-005
対応設計節：design.md §ステップ実行モデル Step D Integration（統合手順 6 ステップ）
対応要件：Requirement 1 受入 1〜3、Requirement 4 受入 2〜5、Requirement 5 受入 1

テスト要件（tasks.md T-005 より）：
- 固定入力に対する決定的出力テスト
- treatment 別の挙動テスト（Step C 非実行時の判定紐付けスキップ等）
- integration_summary の foundation スキーマ準拠テスト
"""
import inspect
import json
from pathlib import Path

from runtime_core.step_executors import step_d_integration as step_d


def _finding(fid, source_role, source_ref):
  return {
    "finding_id": fid, "step_id": "step_a", "source_role": source_role,
    "severity": "ERROR", "summary": f"所見{fid}", "source_refs": [source_ref],
    "counter_evidence_refs": [], "judgment_ref": "", "decision_unit_id": "",
    "human_decision_ref": "", "counter_status": "not_assessed",
  }


def _step_a_output():
  return {
    "step_id": "step_a", "step_name": "primary_detection", "step_outcome": "executed",
    "review_mode": "runtime_mediated",
    "findings": [
      _finding("step_a-f0", "primary_reviewer", "doc#R1"),
      _finding("step_a-f1", "primary_reviewer", "doc#R2"),
    ],
  }


def _step_b_output():
  f = _finding("step_b-f0", "adversarial_reviewer", "doc#R1")
  f["counter_status"] = "counter_evidence_raised"
  return {
    "step_id": "step_b", "step_name": "adversarial_review", "step_outcome": "executed",
    "review_mode": "runtime_mediated", "findings": [f],
  }


def _step_c_output():
  return {
    "step_id": "step_c", "step_name": "judgment", "step_outcome": "executed",
    "review_mode": "runtime_mediated",
    "judgments": [
      {
        "requirement_link": "R1", "ignored_impact": "中", "fix_cost": "low",
        "scope_expansion": "none", "uncertainty": "low", "final_label": "must-fix",
        "recommended_action": "修正", "finding_refs": ["step_a-f0", "step_b-f0"],
      },
      {
        "requirement_link": "R2", "ignored_impact": "小", "fix_cost": "low",
        "scope_expansion": "none", "uncertainty": "low", "final_label": "should-fix",
        "recommended_action": "改善", "finding_refs": ["step_a-f1"],
      },
    ],
  }


def _skip_marker(step_id, step_name):
  return {
    "step_id": step_id, "step_name": step_name, "step_outcome": "skipped_by_treatment",
    "reason": "treatment", "treatment": "adversarial", "review_mode": "runtime_mediated",
  }


def _run_dir(tmp_path):
  d = tmp_path / "experiments" / "runs" / "run-1"
  (d / "steps").mkdir(parents=True)
  (d / "decisions").mkdir(parents=True)
  return d


def test_step_d_has_no_llm_boundary_param():
  """Step D は言語モデル呼び出しを含まない（差し替え点を引数に取らない）。"""
  sig = inspect.signature(step_d.run)
  assert "llm_boundary" not in sig.parameters, "Step D が llm_boundary を受けている"


def test_step_d_writes_outputs(tmp_path):
  """Step D が step_d_integration.json と decisions/decision_units.json を出力する。"""
  run_dir = _run_dir(tmp_path)
  out = step_d.run(
    run_dir=run_dir, step_a_output=_step_a_output(), step_b_output=_step_b_output(),
    step_c_output=_step_c_output(), treatment="judgment", started_at="t0", closed_at="t1",
  )
  assert (run_dir / "steps" / "step_d_integration.json").is_file()
  assert (run_dir / "decisions" / "decision_units.json").is_file()
  assert out["step_outcome"] == "executed"


def test_step_d_aggregates_by_requirement_link(tmp_path):
  """所見を requirement_link で決定単位に集約する（統合手順 ステップ 3）。"""
  run_dir = _run_dir(tmp_path)
  out = step_d.run(
    run_dir=run_dir, step_a_output=_step_a_output(), step_b_output=_step_b_output(),
    step_c_output=_step_c_output(), treatment="judgment", started_at="t0", closed_at="t1",
  )
  units = out["decision_units"]
  # R1（step_a-f0 と step_b-f0）と R2（step_a-f1）の 2 決定単位
  assert len(units) == 2
  r1 = next(u for u in units if "step_a-f0" in u["finding_refs"])
  assert set(r1["finding_refs"]) == {"step_a-f0", "step_b-f0"}


def test_step_d_maps_final_label_to_proposed_action(tmp_path):
  """final_label を推奨措置に写像する（統合手順 ステップ 4）。"""
  run_dir = _run_dir(tmp_path)
  out = step_d.run(
    run_dir=run_dir, step_a_output=_step_a_output(), step_b_output=_step_b_output(),
    step_c_output=_step_c_output(), treatment="judgment", started_at="t0", closed_at="t1",
  )
  r1 = next(u for u in out["decision_units"] if "step_a-f0" in u["finding_refs"])
  assert r1["proposed_action"] == "fix_required"  # must-fix → fix_required


def test_decision_units_have_unset_human_decision(tmp_path):
  """Step D の決定単位は人間決定が未確定（design.md §決定単位モデル）。"""
  run_dir = _run_dir(tmp_path)
  out = step_d.run(
    run_dir=run_dir, step_a_output=_step_a_output(), step_b_output=_step_b_output(),
    step_c_output=_step_c_output(), treatment="judgment", started_at="t0", closed_at="t1",
  )
  for u in out["decision_units"]:
    assert u["human_decision"] is None
    for key in ("decision_unit_id", "finding_refs", "judgment_refs",
                "proposed_action", "human_decision_timestamp", "human_decision_note"):
      assert key in u, f"決定単位に {key} が欠落"


def test_step_c_not_executed_skips_judgment_linking(tmp_path):
  """treatment が Step C を含まない場合、判定紐付けをスキップする（テスト要件）。"""
  run_dir = _run_dir(tmp_path)
  out = step_d.run(
    run_dir=run_dir, step_a_output=_step_a_output(), step_b_output=_step_b_output(),
    step_c_output=_skip_marker("step_c", "judgment"), treatment="adversarial",
    started_at="t0", closed_at="t1",
  )
  for u in out["decision_units"]:
    assert u["judgment_refs"] == []
    assert u["proposed_action"] == "human_review_required"  # 判定なし時の既定


def test_step_d_is_deterministic(tmp_path):
  """同じ入力で決定的に同じ出力（完了条件、決定的再現）。"""
  out1 = step_d.run(
    run_dir=_run_dir(tmp_path / "a"), step_a_output=_step_a_output(),
    step_b_output=_step_b_output(), step_c_output=_step_c_output(),
    treatment="judgment", started_at="t0", closed_at="t1",
  )
  out2 = step_d.run(
    run_dir=_run_dir(tmp_path / "b"), step_a_output=_step_a_output(),
    step_b_output=_step_b_output(), step_c_output=_step_c_output(),
    treatment="judgment", started_at="t0", closed_at="t1",
  )
  assert out1 == out2


def test_integration_summary_is_string(tmp_path):
  """integration_summary が文字列（review_case スキーマ integration_summary type:string 準拠）。"""
  run_dir = _run_dir(tmp_path)
  out = step_d.run(
    run_dir=run_dir, step_a_output=_step_a_output(), step_b_output=_step_b_output(),
    step_c_output=_step_c_output(), treatment="judgment", started_at="t0", closed_at="t1",
  )
  assert isinstance(out["integration_summary"], str) and out["integration_summary"]


def test_run_close_readiness_signal(tmp_path):
  """実行終了準備信号を必須段出力の充足で機械判定する（統合手順 ステップ 5）。"""
  run_dir = _run_dir(tmp_path)
  out = step_d.run(
    run_dir=run_dir, step_a_output=_step_a_output(), step_b_output=_step_b_output(),
    step_c_output=_step_c_output(), treatment="judgment", started_at="t0", closed_at="t1",
  )
  assert out["run_close_ready"] is True


# ---- triad-review 機能内対処（2026-06-02、A-004）----

def test_readiness_false_when_skip_marker_missing(tmp_path):
  """A-004：省略段のマーカーが欠落（事故的欠落）なら run_close_ready=False。"""
  run_dir = _run_dir(tmp_path)
  out = step_d.run(
    run_dir=run_dir, step_a_output=_step_a_output(),
    step_b_output=None, step_c_output=None,
    treatment="primary", started_at="t0", closed_at="t1",
  )
  assert out["run_close_ready"] is False


def test_readiness_true_when_skip_marker_present(tmp_path):
  """A-004：省略段に skipped_by_treatment マーカーがあれば run_close_ready=True。"""
  run_dir = _run_dir(tmp_path)
  out = step_d.run(
    run_dir=run_dir, step_a_output=_step_a_output(),
    step_b_output=_skip_marker("step_b", "adversarial_review"),
    step_c_output=_skip_marker("step_c", "judgment"),
    treatment="primary", started_at="t0", closed_at="t1",
  )
  assert out["run_close_ready"] is True
