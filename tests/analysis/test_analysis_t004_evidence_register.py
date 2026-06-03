"""T-004 のテスト：証拠台帳とレビューモード保持。

対応タスク：analysis tasks.md T-004
対応設計節：design.md §証拠台帳モデル §1〜§3
対応要件：Requirement 5、Requirement 6 受入 1〜5
"""
import importlib
import json
from pathlib import Path

import jsonschema
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]


def _builder_class():
  module = importlib.import_module("analysis.evidence_register.evidence_register_builder")
  return module.EvidenceRegisterBuilder


def _binding_module():
  return importlib.import_module("analysis.evidence_register.binding_rules")


def _artifact_ref(target_id="run-001"):
  return {
    "ref_type": "treatment_comparison",
    "target_path": "comparisons/treatment_comparisons.json",
    "target_id": target_id,
  }


def _manifest_ref():
  return {
    "ref_type": "analysis_manifest",
    "target_path": "manifests/analysis_run_manifest.yaml",
    "target_id": "analysis-001",
  }


def _run_set_ref():
  return {
    "ref_type": "input_run_set",
    "target_path": "manifests/analysis_run_manifest.yaml",
    "target_id": "run-001",
  }


def _base_evidence(**overrides):
  evidence = {
    "evidence_id": "evidence-001",
    "artifact_ref": _artifact_ref(),
    "source_analysis_manifest_ref": _manifest_ref(),
    "input_run_set_ref": _run_set_ref(),
    "evidence_class": "valid",
    "review_mode": "runtime_mediated",
    "eligible_for_standard_comparison": True,
    "stale": False,
    "generated_at": "2026-06-03T13:00:00+09:00",
  }
  evidence.update(overrides)
  return evidence


def test_evidence_register_schema_is_valid_json_schema():
  """evidence_register.schema.json は JSON Schema として妥当。"""
  schema_path = REPO_ROOT / "analysis" / "evidence_register" / "evidence_register.schema.json"
  schema = json.loads(schema_path.read_text(encoding="utf-8"))
  jsonschema.Draft202012Validator.check_schema(schema)


def test_maturity_label_vocab_is_analysis_owned_three_values():
  """maturity_label は analysis 所有の 3 値正本。"""
  assert _binding_module().MATURITY_LABELS == {
    "mature",
    "preliminary",
    "exploratory",
  }


def test_binding_rules_cover_five_evidence_class_cases():
  """evidence_class から maturity_label への束縛規則 5 ケースを網羅する。"""
  classify = _binding_module().maturity_for_evidence
  assert classify("valid", eligible_for_standard_comparison=True) == "mature"
  assert classify("valid", eligible_for_standard_comparison=False) == "preliminary"
  assert classify("exploratory", eligible_for_standard_comparison=False) == "exploratory"
  assert classify("invalid", eligible_for_standard_comparison=False) is None
  assert classify("analysis_blocked", eligible_for_standard_comparison=False) is None


def test_exploratory_evidence_gets_caveat_ref_automatically(tmp_path):
  """evidence_class=exploratory には予備的証拠 caveat が自動付与される。"""
  path = _builder_class()().write(
    tmp_path,
    evidences=[
      _base_evidence(
        evidence_id="exploratory-001",
        evidence_class="exploratory",
        eligible_for_standard_comparison=False,
      ),
    ],
  )

  payload = json.loads(path.read_text(encoding="utf-8"))
  entry = payload["entries"][0]
  assert entry["maturity_label"] == "exploratory"
  assert entry["caveat_refs"] == [
    {
      "ref_type": "caveat_entry",
      "target_path": "shared/caveat_register.json",
      "target_id": "preliminary-evidence",
    }
  ]


def test_invalid_and_analysis_blocked_evidence_are_not_report_entries(tmp_path):
  """invalid / analysis_blocked は evidence_register の報告対象から除外する。"""
  path = _builder_class()().write(
    tmp_path,
    evidences=[
      _base_evidence(evidence_id="invalid-001", evidence_class="invalid"),
      _base_evidence(
        evidence_id="blocked-001",
        evidence_class="analysis_blocked",
        eligible_for_standard_comparison=False,
      ),
    ],
  )

  payload = json.loads(path.read_text(encoding="utf-8"))
  assert payload["entries"] == []


def test_evidence_register_preserves_review_mode_and_lineage(tmp_path):
  """review_mode と supersedes / superseded_by の置換系譜を保持する。"""
  path = _builder_class()().write(
    tmp_path,
    evidences=[
      _base_evidence(
        review_mode="api_mediated",
        supersedes=[_artifact_ref("manual-evidence")],
        superseded_by=[_artifact_ref("runtime-evidence")],
      ),
    ],
  )

  payload = json.loads(path.read_text(encoding="utf-8"))
  entry = payload["entries"][0]
  assert entry["review_mode"] == "api_mediated"
  assert entry["supersedes"][0]["target_id"] == "manual-evidence"
  assert entry["superseded_by"][0]["target_id"] == "runtime-evidence"


def test_foundation_vocabularies_are_referenced_not_redefined():
  """evidence_class / review_mode は foundation 正本値を参照する。"""
  metadata = yaml.safe_load(
    (REPO_ROOT / "runtime" / "foundation" / "metadata_contract.yaml").read_text(
      encoding="utf-8",
    )
  )
  foundation = metadata["vocabularies"]
  assert _binding_module().foundation_vocabulary("evidence_class") == set(
    foundation["evidence_class"]
  )
  assert _binding_module().foundation_vocabulary("review_mode") == set(
    foundation["review_mode"]
  )
