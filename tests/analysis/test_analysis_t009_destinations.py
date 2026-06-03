"""T-009 のテスト：出力先別の派生。"""
import importlib
import json
from pathlib import Path

import jsonschema
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]


def _deriver_class():
  module = importlib.import_module("analysis.destinations.destination_deriver")
  return module.DestinationDeriver


def _manifest_schema_path():
  return REPO_ROOT / "analysis" / "destinations" / "manifest.schema.json"


def _evidence(evidence_id, review_mode):
  return {
    "evidence_id": evidence_id,
    "review_mode": review_mode,
  }


def _rich_evidence(evidence_id, review_mode="runtime_mediated"):
  return {
    "evidence_id": evidence_id,
    "review_mode": review_mode,
    "finding_id": f"f-{evidence_id}",
    "severity": "ERROR",
    "phase": "implementation",
    "claim_id": f"c-{evidence_id}",
    "treatment": "triad_review",
    "mode": review_mode,
    "generated_at": "2026-06-01T00:00:00Z",
  }


def test_destination_manifest_schema_is_valid_json_schema():
  """destination manifest schema は JSON Schema として妥当。"""
  schema = json.loads(_manifest_schema_path().read_text(encoding="utf-8"))
  jsonschema.Draft202012Validator.check_schema(schema)


def test_destination_deriver_writes_four_required_outputs(tmp_path):
  """4 出力先それぞれの最低限必須成果物を書く。"""
  created = _deriver_class()().derive(
    tmp_path,
    analysis_logic_version="analysis-1",
    derivation_contract_version="1.0.0",
    evidences=[_evidence("e1", "runtime_mediated")],
    caveats=[],
  )

  assert set(created) >= {
    "destinations/dashboard/operations_summary.json",
    "destinations/weekly/trend_summary.json",
    "destinations/audit/invalidation_index.json",
    "destinations/audit/validator_failure_trace.json",
    "destinations/audit/discipline_violation_index.json",
    "destinations/reports/claim_evidence_trace.json",
    "destinations/reports/treatment_comparison_report.json",
    "destinations/reports/mode_comparison_report.json",
  }


def test_destination_payloads_include_required_contract_fields(tmp_path):
  """4 出力先 payload は設計で求める最小構造を持つ。"""
  _deriver_class()().derive(
    tmp_path,
    analysis_logic_version="analysis-1",
    derivation_contract_version="1.0.0",
    evidences=[_rich_evidence("e1")],
    caveats=[],
  )

  dashboard = json.loads(
    (tmp_path / "destinations" / "dashboard" / "operations_summary.json").read_text(
      encoding="utf-8"
    )
  )
  assert set(dashboard) >= {
    "findings_by_severity",
    "findings_by_phase",
    "in_progress_procedure_states",
    "derived_at",
    "coverage_period",
  }

  weekly = json.loads(
    (tmp_path / "destinations" / "weekly" / "trend_summary.json").read_text(
      encoding="utf-8"
    )
  )
  assert set(weekly) >= {
    "weekly_deltas",
    "top_findings",
    "compliance_rate_change",
    "period",
  }

  invalidation = json.loads(
    (tmp_path / "destinations" / "audit" / "invalidation_index.json").read_text(
      encoding="utf-8"
    )
  )
  assert "invalidation_markers" in invalidation

  validator = json.loads(
    (tmp_path / "destinations" / "audit" / "validator_failure_trace.json").read_text(
      encoding="utf-8"
    )
  )
  assert "validator_failures" in validator

  discipline = json.loads(
    (
      tmp_path / "destinations" / "audit" / "discipline_violation_index.json"
    ).read_text(encoding="utf-8")
  )
  assert "discipline_violations" in discipline

  claim_trace = json.loads(
    (tmp_path / "destinations" / "reports" / "claim_evidence_trace.json").read_text(
      encoding="utf-8"
    )
  )
  assert "claim_evidence_trace" in claim_trace

  treatment = json.loads(
    (
      tmp_path / "destinations" / "reports" / "treatment_comparison_report.json"
    ).read_text(encoding="utf-8")
  )
  assert "treatment_comparisons" in treatment

  mode = json.loads(
    (tmp_path / "destinations" / "reports" / "mode_comparison_report.json").read_text(
      encoding="utf-8"
    )
  )
  assert "mode_comparisons" in mode


def test_mode_comparison_report_counts_review_mode_not_mode_alias(tmp_path):
  """mode_comparison_report は foundation 正本 review_mode を集計する。"""
  _deriver_class()().derive(
    tmp_path,
    analysis_logic_version="analysis-1",
    derivation_contract_version="1.0.0",
    evidences=[
      {"evidence_id": "e1", "review_mode": "runtime_mediated", "mode": "wrong"},
      {"evidence_id": "e2", "review_mode": "manual_dogfooding"},
    ],
    caveats=[],
  )

  mode = json.loads(
    (tmp_path / "destinations" / "reports" / "mode_comparison_report.json").read_text(
      encoding="utf-8"
    )
  )
  assert mode["mode_comparisons"] == {
    "manual_dogfooding": 1,
    "runtime_mediated": 1,
  }


def test_destination_manifest_records_required_eight_fields(tmp_path):
  """各出力先 manifest は必須 8 項目を持つ。"""
  _deriver_class()().derive(
    tmp_path,
    analysis_logic_version="analysis-1",
    derivation_contract_version="1.0.0",
    evidences=[_evidence("e1", "runtime_mediated")],
    caveats=[],
  )

  manifest = yaml.safe_load(
    (tmp_path / "destinations" / "dashboard" / "manifest.yaml").read_text(
      encoding="utf-8"
    )
  )
  assert set(manifest) >= {
    "destination",
    "analysis_logic_version",
    "derivation_contract_version",
    "included_evidence_refs",
    "included_caveat_refs",
    "granularity_profile",
    "summary_level",
    "review_mode_mixed",
  }
  assert manifest["destination"] == "dashboard"


def test_destination_deriver_writes_yaml_manifest_contract(tmp_path):
  """各出力先 manifest は仕様どおり manifest.yaml として書く。"""
  created = _deriver_class()().derive(
    tmp_path,
    analysis_logic_version="analysis-1",
    derivation_contract_version="1.0.0",
    evidences=[_evidence("e1", "runtime_mediated")],
    caveats=[],
  )

  assert "destinations/dashboard/manifest.yaml" in created
  assert (tmp_path / "destinations" / "dashboard" / "manifest.yaml").is_file()
  assert not (tmp_path / "destinations" / "dashboard" / "manifest.json").exists()

  manifest = yaml.safe_load(
    (tmp_path / "destinations" / "dashboard" / "manifest.yaml").read_text(
      encoding="utf-8"
    )
  )
  assert manifest["destination"] == "dashboard"


def test_destination_deriver_appends_mixed_review_mode_caveat(tmp_path):
  """review_mode が混在すると caveat_register に mixed_review_mode を追加する。"""
  _deriver_class()().derive(
    tmp_path,
    analysis_logic_version="analysis-1",
    derivation_contract_version="1.0.0",
    evidences=[
      _evidence("e1", "manual_dogfooding"),
      _evidence("e2", "runtime_mediated"),
    ],
    caveats=[],
  )

  caveat_register = json.loads(
    (tmp_path / "shared" / "caveat_register.json").read_text(encoding="utf-8")
  )
  assert caveat_register["entries"][0]["limitation_type"] == "mixed_review_mode"


def test_destination_deriver_writes_empty_caveat_register(tmp_path):
  """caveat が 0 件でも downstream 用の caveat_register を書く。"""
  created = _deriver_class()().derive(
    tmp_path,
    analysis_logic_version="analysis-1",
    derivation_contract_version="1.0.0",
    evidences=[_evidence("e1", "runtime_mediated")],
    caveats=[],
  )

  assert "shared/caveat_register.json" in created
  caveat_register = json.loads(
    (tmp_path / "shared" / "caveat_register.json").read_text(encoding="utf-8")
  )
  assert caveat_register == {"entries": []}


def test_destination_deriver_preserves_existing_caveat_register_entries(tmp_path):
  """caveat_register は既存 entries を消さず追加する。"""
  _deriver_class()().derive(
    tmp_path,
    analysis_logic_version="analysis-1",
    derivation_contract_version="1.0.0",
    evidences=[_evidence("e1", "runtime_mediated")],
    caveats=[
      {
        "caveat_id": "caveat-1",
        "limitation_type": "partial_evidence",
        "description": "First caveat",
      }
    ],
  )
  _deriver_class()().derive(
    tmp_path,
    analysis_logic_version="analysis-1",
    derivation_contract_version="1.0.0",
    evidences=[_evidence("e1", "runtime_mediated")],
    caveats=[
      {
        "caveat_id": "caveat-2",
        "limitation_type": "methodological_limitation",
        "description": "Second caveat",
      }
    ],
  )

  caveat_register = json.loads(
    (tmp_path / "shared" / "caveat_register.json").read_text(encoding="utf-8")
  )
  assert [entry["caveat_id"] for entry in caveat_register["entries"]] == [
    "caveat-1",
    "caveat-2",
  ]


def test_destination_deriver_records_superseded_versions(tmp_path):
  """derivation_contract_version 更新時は前版 ref を superseded_versions に残す。"""
  _deriver_class()().derive(
    tmp_path,
    analysis_logic_version="analysis-1",
    derivation_contract_version="1.0.0",
    evidences=[_evidence("e1", "runtime_mediated")],
    caveats=[],
  )
  _deriver_class()().derive(
    tmp_path,
    analysis_logic_version="analysis-1",
    derivation_contract_version="1.1.0",
    evidences=[_evidence("e1", "runtime_mediated")],
    caveats=[],
  )

  manifest = yaml.safe_load(
    (tmp_path / "destinations" / "dashboard" / "manifest.yaml").read_text(
      encoding="utf-8"
    )
  )
  assert manifest["derivation_contract_version"] == "1.1.0"
  assert manifest["superseded_versions"] == [
    {
      "version": "1.0.0",
      "manifest_path": "destinations/dashboard/manifest.yaml",
    }
  ]
