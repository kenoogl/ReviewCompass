"""T-005 のテスト：注意点と限界の台帳。"""
import importlib
import json
from pathlib import Path

import jsonschema

REPO_ROOT = Path(__file__).resolve().parents[2]


def _builder_class():
  module = importlib.import_module("analysis.caveat_register.caveat_register_builder")
  return module.CaveatRegisterBuilder


def _detector_module():
  return importlib.import_module("analysis.caveat_register.mixed_review_mode_detector")


def _artifact_ref(target_id="evidence-001"):
  return {
    "ref_type": "evidence_entry",
    "target_path": "shared/evidence_register.json",
    "target_id": target_id,
  }


def _claim_ref(target_id="claim-001"):
  return {
    "ref_type": "claim_entry",
    "target_path": "shared/claim_map.json",
    "target_id": target_id,
  }


def test_caveat_register_schema_is_valid_json_schema():
  """caveat_register.schema.json は JSON Schema として妥当。"""
  schema_path = REPO_ROOT / "analysis" / "caveat_register" / "caveat_register.schema.json"
  schema = json.loads(schema_path.read_text(encoding="utf-8"))
  jsonschema.Draft202012Validator.check_schema(schema)


def test_limitation_type_vocab_is_analysis_owned_four_values():
  """limitation_type は analysis 所有の 4 値正本。"""
  assert _detector_module().LIMITATION_TYPES == {
    "invalid_data_exclusion",
    "partial_evidence",
    "methodological_limitation",
    "mixed_review_mode",
  }


def test_mixed_review_mode_detector_does_not_fire_for_single_mode():
  """単一 review_mode の報告集合では mixed_review_mode は発火しない。"""
  result = _detector_module().detect_mixed_review_mode(
    [{"evidence_id": "e1", "review_mode": "runtime_mediated"}]
  )

  assert result is None


def test_mixed_review_mode_detector_fires_for_two_modes():
  """2 値混在で mixed_review_mode caveat を返す。"""
  result = _detector_module().detect_mixed_review_mode(
    [
      {"evidence_id": "e1", "review_mode": "manual_dogfooding"},
      {"evidence_id": "e2", "review_mode": "runtime_mediated"},
    ],
    caveat_id="mixed-001",
  )

  assert result["caveat_id"] == "mixed-001"
  assert result["limitation_type"] == "mixed_review_mode"
  assert "manual_dogfooding" in result["narrative_note"]
  assert "runtime_mediated" in result["narrative_note"]


def test_mixed_review_mode_detector_fires_for_three_modes():
  """3 値混在でも mixed_review_mode caveat を返す。"""
  result = _detector_module().detect_mixed_review_mode(
    [
      {"evidence_id": "e1", "review_mode": "manual_dogfooding"},
      {"evidence_id": "e2", "review_mode": "runtime_mediated"},
      {"evidence_id": "e3", "review_mode": "api_mediated"},
    ],
    caveat_id="mixed-002",
  )

  assert result["limitation_type"] == "mixed_review_mode"
  assert sorted(result["review_modes"]) == [
    "api_mediated",
    "manual_dogfooding",
    "runtime_mediated",
  ]


def test_caveat_register_builder_writes_required_fields(tmp_path):
  """caveat register builder は必須 3 項目と適用先を持つ台帳を書き出す。"""
  path = _builder_class()().write(
    tmp_path,
    caveats=[
      {
        "caveat_id": "caveat-001",
        "limitation_type": "partial_evidence",
        "narrative_note": "partial evidence only",
        "applies_to_claim_refs": [_claim_ref()],
        "applies_to_artifact_refs": [_artifact_ref()],
      },
    ],
  )

  payload = json.loads(path.read_text(encoding="utf-8"))
  caveat = payload["entries"][0]
  assert caveat["caveat_id"] == "caveat-001"
  assert caveat["limitation_type"] == "partial_evidence"
  assert caveat["narrative_note"] == "partial evidence only"


def test_caveat_register_rejects_caveat_without_apply_target(tmp_path):
  """claim/artifact のどちらにも適用されない caveat は許容しない。"""
  try:
    _builder_class()().write(
      tmp_path,
      caveats=[
        {
          "caveat_id": "targetless",
          "limitation_type": "methodological_limitation",
          "narrative_note": "no target",
        },
      ],
    )
  except ValueError as exc:
    assert "applies_to_claim_refs" in str(exc)
    assert "applies_to_artifact_refs" in str(exc)
  else:
    raise AssertionError("適用先のない caveat が受理された")
