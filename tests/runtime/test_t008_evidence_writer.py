"""T-008 のテスト：evidence writer（証拠書き出し器と不変性担保）。

対応タスク：runtime tasks.md T-008
対応設計節：design.md §証拠出力モデル §生証拠と派生証拠の分離、§不変性の担保
対応要件：Requirement 4 受入 4・7、Requirement 6 受入 3、Requirement 7 受入 5

テスト要件（tasks.md T-008 より）：
- 投影規約 7 項目のテスト
- 凍結後書き込み拒否テスト
- review_case.json の foundation スキーマ準拠テスト
- failure_observation スキーマ準拠テスト
"""
import json
from pathlib import Path

import pytest
import yaml
from jsonschema import Draft202012Validator

from runtime_core.evidence_writer.writer import EvidenceWriter
from runtime_core.evidence_writer.immutability_guard import ImmutabilityGuard, FrozenEvidenceError
from runtime_core.evidence_writer.failure_observation_writer import FailureObservationWriter

REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_DIR = REPO_ROOT / "runtime/schemas"
PROJECTION_RULES = REPO_ROOT / "runtime/runtime_core/evidence_writer/projection_rules.yaml"

REVIEW_CASE_SCHEMA = json.loads((SCHEMA_DIR / "review_case.schema.json").read_text(encoding="utf-8"))
FAILURE_OBS_SCHEMA = json.loads((SCHEMA_DIR / "failure_observation.schema.json").read_text(encoding="utf-8"))


def _finding(fid, step_id, source_role):
  return {
    "finding_id": fid, "step_id": step_id, "source_role": source_role,
    "severity": "ERROR", "summary": f"所見{fid}", "source_refs": ["doc#R1"],
    "counter_evidence_refs": [], "judgment_ref": "", "decision_unit_id": "",
    "human_decision_ref": "", "counter_status": "not_assessed",
  }


def _populated_run(tmp_path, with_validation=False):
  run_dir = tmp_path / "experiments" / "runs" / "run-1"
  (run_dir / "steps").mkdir(parents=True)
  (run_dir / "decisions").mkdir(parents=True)
  # run_manifest.yaml
  (run_dir / "run_manifest.yaml").write_text(
    yaml.safe_dump({"run_id": "run-1", "target_id": "doc-001", "run_status": "in_progress"},
                   allow_unicode=True), encoding="utf-8")
  # steps
  (run_dir / "steps" / "step_a_primary_detection.json").write_text(json.dumps({
    "step_id": "step_a", "step_name": "primary_detection", "step_outcome": "executed",
    "review_mode": "runtime_mediated", "prompt_id": "primary_reviewer",
    "step_started_at": "t0", "step_closed_at": "t1",
    "findings": [_finding("step_a-f0", "step_a", "primary_reviewer")],
  }, ensure_ascii=False), encoding="utf-8")
  (run_dir / "steps" / "step_b_adversarial_review.json").write_text(json.dumps({
    "step_id": "step_b", "step_name": "adversarial_review", "step_outcome": "executed",
    "review_mode": "runtime_mediated", "prompt_id": "adversarial_reviewer",
    "step_started_at": "t0", "step_closed_at": "t1",
    "findings": [_finding("step_b-f0", "step_b", "adversarial_reviewer")],
  }, ensure_ascii=False), encoding="utf-8")
  (run_dir / "steps" / "step_c_judgment.json").write_text(json.dumps({
    "step_id": "step_c", "step_name": "judgment", "step_outcome": "executed",
    "review_mode": "runtime_mediated", "prompt_id": "judgment_reviewer",
    "step_started_at": "t0", "step_closed_at": "t1",
    "judgments": [{"requirement_link": "R1", "final_label": "must-fix", "recommended_action": "x",
                   "ignored_impact": "中", "fix_cost": "low", "scope_expansion": "none", "uncertainty": "low"}],
  }, ensure_ascii=False), encoding="utf-8")
  (run_dir / "steps" / "step_d_integration.json").write_text(json.dumps({
    "step_id": "step_d", "step_name": "integration", "step_outcome": "executed",
    "review_mode": "runtime_mediated", "integration_summary": "統合：所見 2 件、決定単位 1 件",
  }, ensure_ascii=False), encoding="utf-8")
  # decisions
  (run_dir / "decisions" / "decision_units.json").write_text(json.dumps({
    "decision_units": [
      {"decision_unit_id": "du-001", "finding_refs": ["step_a-f0", "step_b-f0"],
       "judgment_refs": ["judgment-0"], "proposed_action": "fix_required",
       "human_decision": None, "human_decision_timestamp": None, "human_decision_note": ""},
    ]
  }, ensure_ascii=False), encoding="utf-8")
  if with_validation:
    (run_dir / "validation").mkdir(parents=True)
    (run_dir / "validation" / "validator_result.json").write_text(json.dumps({
      "run_id": "run-1", "validator_status": "passed", "checked_contract": "x",
      "error_list": [], "validated_by": "v", "validated_at": "t"}), encoding="utf-8")
    (run_dir / "validation" / "invalidation_markers.json").write_text(
      json.dumps({"markers": []}), encoding="utf-8")
  return run_dir


def test_projection_rules_declares_7_items():
  """projection_rules.yaml が投影規約 7 項目を宣言する（完了条件 1）。"""
  spec = yaml.safe_load(PROJECTION_RULES.read_text(encoding="utf-8"))
  assert len(spec["projections"]) == 7


def test_review_case_conforms_to_foundation_schema(tmp_path):
  """投影した review_case.json が foundation review_case スキーマに準拠する（テスト要件）。"""
  run_dir = _populated_run(tmp_path)
  EvidenceWriter(run_dir).project_to_review_case()
  review_case = json.loads((run_dir / "review_case.json").read_text(encoding="utf-8"))
  Draft202012Validator(REVIEW_CASE_SCHEMA).validate(review_case)


def test_projection_step_outcome_to_step_status(tmp_path):
  """投影 1：step_outcome → step_records[].step_status（完了条件 1）。"""
  run_dir = _populated_run(tmp_path)
  EvidenceWriter(run_dir).project_to_review_case()
  rc = json.loads((run_dir / "review_case.json").read_text(encoding="utf-8"))
  statuses = {r["step_id"]: r["step_status"] for r in rc["step_records"]}
  assert statuses["step_a"] == "executed"


def test_projection_findings_collected(tmp_path):
  """投影 3：各段の findings → review_case.findings[]（完了条件 1）。"""
  run_dir = _populated_run(tmp_path)
  EvidenceWriter(run_dir).project_to_review_case()
  rc = json.loads((run_dir / "review_case.json").read_text(encoding="utf-8"))
  fids = {f["finding_id"] for f in rc["findings"]}
  assert fids == {"step_a-f0", "step_b-f0"}


def test_projection_decision_unit_link(tmp_path):
  """投影 4：decision_units → review_case.findings[].decision_unit_id（完了条件 1）。"""
  run_dir = _populated_run(tmp_path)
  EvidenceWriter(run_dir).project_to_review_case()
  rc = json.loads((run_dir / "review_case.json").read_text(encoding="utf-8"))
  for f in rc["findings"]:
    assert f["decision_unit_id"] == "du-001"


def test_projection_integration_summary(tmp_path):
  """投影 7：Step D の integration_summary → review_case.integration_summary（完了条件 1）。"""
  run_dir = _populated_run(tmp_path)
  EvidenceWriter(run_dir).project_to_review_case()
  rc = json.loads((run_dir / "review_case.json").read_text(encoding="utf-8"))
  assert "統合" in rc["integration_summary"]


def test_projection_validation_refs(tmp_path):
  """投影 5・6：validator_result／invalidation_markers への参照を保持（完了条件 1）。"""
  run_dir = _populated_run(tmp_path, with_validation=True)
  EvidenceWriter(run_dir).project_to_review_case()
  rc = json.loads((run_dir / "review_case.json").read_text(encoding="utf-8"))
  assert rc["validator_result_refs"], "validator_result_refs が空"
  assert isinstance(rc["invalidation_marker_refs"], list)


def test_validation_refs_empty_when_absent(tmp_path):
  """検証成果物が無い段階では参照は空配列（投影は欠落を捏造しない）。"""
  run_dir = _populated_run(tmp_path, with_validation=False)
  EvidenceWriter(run_dir).project_to_review_case()
  rc = json.loads((run_dir / "review_case.json").read_text(encoding="utf-8"))
  assert rc["validator_result_refs"] == []
  assert rc["invalidation_marker_refs"] == []


def test_immutability_guard_blocks_write_after_freeze(tmp_path):
  """凍結後の生段証拠書き込みを拒否する（完了条件 2）。"""
  run_dir = _populated_run(tmp_path)
  guard = ImmutabilityGuard(run_dir)
  assert guard.is_frozen() is False
  # 凍結前は書ける
  guard.guarded_write_step("steps/extra.json", "{}")
  guard.freeze(closed_at="2026-06-02T12:00")
  assert guard.is_frozen() is True
  with pytest.raises(FrozenEvidenceError):
    guard.guarded_write_step("steps/step_a_primary_detection.json", "{}")


def test_freeze_records_closed_at_in_manifest(tmp_path):
  """凍結マーカーは run_manifest.yaml の closed_at に記録される（design.md §不変性の担保）。"""
  run_dir = _populated_run(tmp_path)
  ImmutabilityGuard(run_dir).freeze(closed_at="2026-06-02T12:00")
  manifest = yaml.safe_load((run_dir / "run_manifest.yaml").read_text(encoding="utf-8"))
  assert manifest["closed_at"] == "2026-06-02T12:00"


def test_failure_observation_conforms_to_schema(tmp_path):
  """failure_observation が foundation スキーマに準拠して書き出される（完了条件 3）。"""
  run_dir = tmp_path / "experiments" / "runs" / "run-1"
  (run_dir / "failures" / "failure_observations").mkdir(parents=True)
  writer = FailureObservationWriter()
  obs = {
    "observation_id": "obs-001", "run_ref": "run-1", "related_finding_ref": "step_a-f0",
    "failure_type": "review_miss", "missed_by_role": "primary_reviewer", "detected_at_step": "step_b",
  }
  path = writer.write(run_dir, obs)
  assert path.is_file()
  data = json.loads(path.read_text(encoding="utf-8"))
  Draft202012Validator(FAILURE_OBS_SCHEMA).validate(data)
  assert path.name == "obs-001.json"


def test_failure_observation_rejects_invalid(tmp_path):
  """必須項目を欠く failure_observation を拒否する（スキーマ準拠）。"""
  run_dir = tmp_path / "experiments" / "runs" / "run-1"
  (run_dir / "failures" / "failure_observations").mkdir(parents=True)
  writer = FailureObservationWriter()
  with pytest.raises(Exception):
    writer.write(run_dir, {"observation_id": "obs-002"})  # 必須項目欠落
