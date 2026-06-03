"""T-008 のテスト：conformance-evaluation 取り込み。"""
import importlib
import json
from pathlib import Path

import jsonschema

REPO_ROOT = Path(__file__).resolve().parents[2]


def _builder_class():
  module = importlib.import_module(
    "analysis.conformance_intake.conformance_intake_builder"
  )
  return module.ConformanceIntakeBuilder


def _audit_writer_class():
  module = importlib.import_module("analysis.conformance_intake.derived_audit_writer")
  return module.DerivedAuditWriter


def _reports_writer_class():
  module = importlib.import_module("analysis.conformance_intake.derived_reports_writer")
  return module.DerivedReportsWriter


def _guards():
  return importlib.import_module("analysis.traceability.completion_guards")


def _run_ref():
  return {
    "ref_type": "conformance_run",
    "target_path": "conformance_run.json",
    "target_id": "conf-001",
  }


def test_conformance_intake_schema_is_valid_json_schema():
  """conformance_intake.schema.json は JSON Schema として妥当。"""
  schema_path = (
    REPO_ROOT
    / "analysis"
    / "conformance_intake"
    / "conformance_intake.schema.json"
  )
  schema = json.loads(schema_path.read_text(encoding="utf-8"))
  jsonschema.Draft202012Validator.check_schema(schema)


def test_conformance_intake_builder_writes_required_six_fields(tmp_path):
  """conformance intake builder は必須 6 項目を持つ正本を書く。"""
  path = _builder_class()().write(
    tmp_path,
    conformance_run_ref=_run_ref(),
    assessment_summary={"passed": 9, "failed": 1},
    violation_findings=[{"finding_id": "v-001"}],
    compliance_rate=0.9,
    included_disciplines=["approval-operation"],
    intake_at="2026-06-03T14:00:00+09:00",
  )

  payload = json.loads(path.read_text(encoding="utf-8"))
  assert payload["conformance_run_ref"] == _run_ref()
  assert payload["assessment_summary"] == {"passed": 9, "failed": 1}
  assert payload["violation_findings"] == [{"finding_id": "v-001"}]
  assert payload["compliance_rate"] == 0.9
  assert payload["included_disciplines"] == ["approval-operation"]
  assert payload["intake_at"] == "2026-06-03T14:00:00+09:00"


def test_derived_audit_writer_references_canonical_intake(tmp_path):
  """監査用加工版は正本 conformance_run_ref を参照する。"""
  intake_path = _builder_class()().write(
    tmp_path,
    conformance_run_ref=_run_ref(),
    assessment_summary={"passed": 9, "failed": 1},
    violation_findings=[{"finding_id": "v-001"}],
    compliance_rate=0.9,
    included_disciplines=["approval-operation"],
    intake_at="2026-06-03T14:00:00+09:00",
  )

  path = _audit_writer_class()().write(tmp_path, intake_path=intake_path)

  payload = json.loads(path.read_text(encoding="utf-8"))
  assert payload["conformance_run_ref"] == _run_ref()
  assert payload["source_intake_ref"] == {
    "ref_type": "analysis_artifact",
    "target_path": "shared/conformance/conformance_intake.json",
    "target_id": None,
  }
  assert payload["violation_findings"] == [{"finding_id": "v-001"}]


def test_derived_reports_writer_references_canonical_intake(tmp_path):
  """報告書向け加工版は正本 conformance_run_ref を参照する。"""
  intake_path = _builder_class()().write(
    tmp_path,
    conformance_run_ref=_run_ref(),
    assessment_summary={"passed": 9, "failed": 1},
    violation_findings=[{"finding_id": "v-001"}],
    compliance_rate=0.9,
    included_disciplines=["approval-operation"],
    intake_at="2026-06-03T14:00:00+09:00",
  )

  path = _reports_writer_class()().write(tmp_path, intake_path=intake_path)

  payload = json.loads(path.read_text(encoding="utf-8"))
  assert payload["conformance_run_ref"] == _run_ref()
  assert payload["source_intake_ref"] == {
    "ref_type": "analysis_artifact",
    "target_path": "shared/conformance/conformance_intake.json",
    "target_id": None,
  }
  assert payload["compliance_rate"] == 0.9


def test_conformance_intake_code_does_not_write_conformance_evaluation_outputs():
  """analysis 側実装は conformance-evaluation 判定結果を上書きする経路を持たない。"""
  assert _guards().evaluation_write_violations(
    REPO_ROOT / "analysis" / "conformance_intake"
  ) == []
