"""T-010 のテスト：陳腐化伝播と再生成登録。"""
import importlib
import json
from pathlib import Path

import jsonschema

REPO_ROOT = Path(__file__).resolve().parents[2]


def _checker_class():
  module = importlib.import_module("analysis.staleness.staleness_checker")
  return module.StalenessChecker


def _schema_path():
  return REPO_ROOT / "analysis" / "staleness" / "staleness_register.schema.json"


def _ref(target_path, target_id=None):
  return {
    "ref_type": "artifact",
    "target_path": target_path,
    "target_id": target_id,
  }


def _derived(path, generated_at="2026-05-01T00:00:00Z"):
  return {
    "derived_artifact_ref": _ref(path),
    "generated_at": generated_at,
  }


def test_staleness_register_schema_is_valid_json_schema():
  """staleness register schema は JSON Schema として妥当。"""
  schema = json.loads(_schema_path().read_text(encoding="utf-8"))
  jsonschema.Draft202012Validator.check_schema(schema)


def test_regeneration_status_enum_is_four_values():
  """regeneration_status は analysis 所有正本として 4 値。"""
  module = importlib.import_module("analysis.staleness.staleness_checker")
  assert module.REGENERATION_STATUSES == {
    "pending",
    "in_progress",
    "completed",
    "failed",
  }


def test_checker_registers_evaluation_staleness_entry_by_timestamp(tmp_path):
  """evaluation staleness_register の新規エントリが新しければ登録する。"""
  path = _checker_class()().write_register(
    tmp_path,
    derived_artifacts=[_derived("destinations/dashboard/operations_summary.json")],
    evaluation_staleness_entries=[
      {
        "stale_source_ref": _ref("evaluation/manifests/staleness_register.json", "s1"),
        "updated_at": "2026-05-02T00:00:00Z",
      }
    ],
    dependency_artifacts=[],
    conformance_results=[],
    detected_at="2026-05-03T00:00:00Z",
  )

  register = json.loads(path.read_text(encoding="utf-8"))
  assert register["entries"][0]["regeneration_status"] == "pending"
  assert register["entries"][0]["stale_source_ref"]["target_id"] == "s1"


def test_checker_registers_dependency_stale_true_by_timestamp(tmp_path):
  """依存成果物の stale=true が派生成果物より新しければ登録する。"""
  path = _checker_class()().write_register(
    tmp_path,
    derived_artifacts=[_derived("destinations/reports/claim_evidence_trace.json")],
    evaluation_staleness_entries=[],
    dependency_artifacts=[
      {
        "artifact_ref": _ref("evaluation/treatment_comparisons.json", "tc1"),
        "stale": True,
        "updated_at": "2026-05-02T00:00:00Z",
      }
    ],
    conformance_results=[],
    detected_at="2026-05-03T00:00:00Z",
  )

  register = json.loads(path.read_text(encoding="utf-8"))
  assert register["entries"][0]["stale_source_ref"]["target_path"] == (
    "evaluation/treatment_comparisons.json"
  )


def test_checker_registers_dependency_update_even_when_stale_false(tmp_path):
  """依存成果物が stale=false でも更新時刻が新しければ登録する。"""
  path = _checker_class()().write_register(
    tmp_path,
    derived_artifacts=[_derived("destinations/reports/claim_evidence_trace.json")],
    evaluation_staleness_entries=[],
    dependency_artifacts=[
      {
        "artifact_ref": _ref("evaluation/treatment_comparisons.json", "tc1"),
        "stale": False,
        "updated_at": "2026-05-02T00:00:00Z",
      }
    ],
    conformance_results=[],
    detected_at="2026-05-03T00:00:00Z",
  )

  register = json.loads(path.read_text(encoding="utf-8"))
  assert register["entries"][0]["stale_source_ref"]["target_id"] == "tc1"


def test_checker_registers_conformance_result_update_by_timestamp(tmp_path):
  """conformance-evaluation 結果が派生成果物より新しければ登録する。"""
  path = _checker_class()().write_register(
    tmp_path,
    derived_artifacts=[_derived("destinations/audit/conformance_violations_detail.json")],
    evaluation_staleness_entries=[],
    dependency_artifacts=[],
    conformance_results=[
      {
        "result_ref": _ref("conformance/results/latest.json", "run1"),
        "updated_at": "2026-05-02T00:00:00Z",
      }
    ],
    detected_at="2026-05-03T00:00:00Z",
  )

  register = json.loads(path.read_text(encoding="utf-8"))
  assert register["entries"][0]["stale_source_ref"]["target_id"] == "run1"


def test_checker_does_not_register_when_input_is_not_newer(tmp_path):
  """入力側更新時刻が古い場合は再生成対象にしない。"""
  path = _checker_class()().write_register(
    tmp_path,
    derived_artifacts=[_derived("destinations/weekly/trend_summary.json")],
    evaluation_staleness_entries=[
      {
        "stale_source_ref": _ref("evaluation/manifests/staleness_register.json", "old"),
        "updated_at": "2026-04-30T00:00:00Z",
      }
    ],
    dependency_artifacts=[],
    conformance_results=[],
    detected_at="2026-05-03T00:00:00Z",
  )

  assert json.loads(path.read_text(encoding="utf-8"))["entries"] == []


def test_checker_propagates_stale_marker_to_derived_artifacts():
  """派生成果物へ stale / stale_reason / stale_source_ref を伝播する。"""
  stale_source_ref = _ref("evaluation/manifests/staleness_register.json", "s1")

  propagated = _checker_class().propagate_stale(
    [
      {"evidence_id": "e1", "stale": False},
      {"claim_id": "c1", "stale": False},
      {"fragment_id": "f1"},
      {"table_id": "t1"},
    ],
    stale_source_ref=stale_source_ref,
    stale_reason="upstream_invalidation",
  )

  assert all(entry["stale"] is True for entry in propagated)
  assert all(entry["stale_reason"] == "upstream_invalidation" for entry in propagated)
  assert all(entry["stale_source_ref"] == stale_source_ref for entry in propagated)
