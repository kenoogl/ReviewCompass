"""T-003 のテスト：主張対応図と参照書式。

対応タスク：analysis tasks.md T-003
対応設計節：design.md §主張対応モデル §1〜§3
対応要件：Requirement 1 受入 5、6
"""
import importlib
import json
from pathlib import Path

import jsonschema

REPO_ROOT = Path(__file__).resolve().parents[2]


def _claim_builder_class():
  module = importlib.import_module("analysis.claim_mapping.claim_map_builder")
  return module.ClaimMapBuilder


def _reference_module():
  return importlib.import_module("analysis.common.reference_format")


def test_claim_map_schema_is_valid_json_schema():
  """claim_map.schema.json は JSON Schema として妥当。"""
  schema_path = REPO_ROOT / "analysis" / "claim_mapping" / "claim_map.schema.json"
  schema = json.loads(schema_path.read_text(encoding="utf-8"))
  jsonschema.Draft202012Validator.check_schema(schema)


def test_reference_format_builds_structured_reference():
  """参照書式は ref_type / target_path / target_id の構造化参照を作る。"""
  ref = _reference_module().artifact_ref(
    ref_type="treatment_comparison",
    target_path="comparisons/treatment_comparisons.json",
    target_id="run-001",
  )

  assert ref == {
    "ref_type": "treatment_comparison",
    "target_path": "comparisons/treatment_comparisons.json",
    "target_id": "run-001",
  }


def test_reference_format_resolves_evaluation_artifact(tmp_path):
  """構造化参照は evaluation 成果物配置に対して解決できる。"""
  evaluation_root = tmp_path / "experiments" / "analysis"
  target = evaluation_root / "comparisons" / "treatment_comparisons.json"
  target.parent.mkdir(parents=True)
  target.write_text("{}", encoding="utf-8")
  ref = {
    "ref_type": "treatment_comparison",
    "target_path": "comparisons/treatment_comparisons.json",
    "target_id": None,
  }

  resolved = _reference_module().resolve_artifact_ref(ref, base_dir=evaluation_root)

  assert resolved == target


def test_claim_map_builder_writes_required_claim_fields(tmp_path):
  """claim_map builder は必須 5 項目を持つ claim_map.json を書き出す。"""
  output_root = tmp_path / "analysis-output"
  source_ref = {
    "ref_type": "treatment_comparison",
    "target_path": "comparisons/treatment_comparisons.json",
    "target_id": "run-001",
  }

  path = _claim_builder_class()().write(
    output_root,
    claims=[
      {
        "claim_id": "claim-001",
        "claim_text": "judgment treatment raises counter evidence.",
        "supporting_artifact_refs": [source_ref],
        "maturity_label": "mature",
        "stale": False,
      },
    ],
  )

  payload = json.loads(path.read_text(encoding="utf-8"))
  claim = payload["claims"][0]
  assert set(claim) >= {
    "claim_id",
    "claim_text",
    "supporting_artifact_refs",
    "maturity_label",
    "stale",
  }
  assert claim["supporting_artifact_refs"] == [source_ref]


def test_claim_map_builder_rejects_stale_claim_without_stale_source():
  """stale=true の claim は stale_reason と stale_source_ref を必須にする。"""
  try:
    _claim_builder_class()().write(
      Path("/tmp/unused-analysis-output"),
      claims=[
        {
          "claim_id": "claim-stale",
          "claim_text": "stale claim",
          "supporting_artifact_refs": [],
          "maturity_label": "preliminary",
          "stale": True,
        },
      ],
    )
  except ValueError as exc:
    assert "stale_reason" in str(exc)
    assert "stale_source_ref" in str(exc)
  else:
    raise AssertionError("stale=true で条件付き必須を欠く claim が受理された")
