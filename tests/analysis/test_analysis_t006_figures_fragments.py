"""T-006 のテスト：図表束と報告断片。"""
import importlib
import json
from pathlib import Path

import jsonschema

REPO_ROOT = Path(__file__).resolve().parents[2]


def _table_builder_class():
  module = importlib.import_module("analysis.figures_tables.table_bundle_builder")
  return module.TableBundleBuilder


def _figure_builder_class():
  module = importlib.import_module("analysis.figures_tables.figure_bundle_builder")
  return module.FigureBundleBuilder


def _fragment_builder_module():
  return importlib.import_module("analysis.fragments.fragment_builder")


def _artifact_ref(target_id="claim-001"):
  return {
    "ref_type": "claim_entry",
    "target_path": "shared/claim_map.json",
    "target_id": target_id,
  }


def _caveat_ref(target_id="caveat-001"):
  return {
    "ref_type": "caveat_entry",
    "target_path": "analysis/caveat_register.json",
    "target_id": target_id,
  }


def test_table_bundle_schema_is_valid_json_schema():
  """table_bundle.schema.json は JSON Schema として妥当。"""
  schema_path = REPO_ROOT / "analysis" / "figures_tables" / "table_bundle.schema.json"
  schema = json.loads(schema_path.read_text(encoding="utf-8"))
  jsonschema.Draft202012Validator.check_schema(schema)


def test_figure_bundle_schema_is_valid_json_schema():
  """figure_bundle.schema.json は JSON Schema として妥当。"""
  schema_path = REPO_ROOT / "analysis" / "figures_tables" / "figure_bundle.schema.json"
  schema = json.loads(schema_path.read_text(encoding="utf-8"))
  jsonschema.Draft202012Validator.check_schema(schema)


def test_fragment_schema_is_valid_json_schema():
  """fragment.schema.json は JSON Schema として妥当。"""
  schema_path = REPO_ROOT / "analysis" / "fragments" / "fragment.schema.json"
  schema = json.loads(schema_path.read_text(encoding="utf-8"))
  jsonschema.Draft202012Validator.check_schema(schema)


def test_fragment_type_vocab_is_analysis_owned_five_values():
  """fragment_type は analysis 所有の 5 値正本。"""
  assert _fragment_builder_module().FRAGMENT_TYPES == {
    "claim_summary",
    "method_note",
    "limitation_note",
    "comparison_summary",
    "trend_summary",
  }


def test_table_bundle_builder_writes_required_fields(tmp_path):
  """table bundle builder は必須 5 項目を持つ表データ束を書く。"""
  path = _table_builder_class()().write(
    tmp_path,
    table_id="table-001",
    source_artifact_refs=[_artifact_ref()],
    field_projection={"columns": ["claim_id", "maturity_label"]},
    maturity_label="mature",
    applicable_destinations=["reports", "weekly"],
  )

  payload = json.loads(path.read_text(encoding="utf-8"))
  assert path.name == "table-001.json"
  assert payload["table_id"] == "table-001"
  assert payload["source_artifact_refs"] == [_artifact_ref()]
  assert payload["field_projection"]["columns"] == ["claim_id", "maturity_label"]
  assert payload["maturity_label"] == "mature"
  assert payload["applicable_destinations"] == ["reports", "weekly"]


def test_table_bundle_builder_preserves_optional_caveat_refs(tmp_path):
  """table bundle builder は任意の caveat_refs を保持する。"""
  path = _table_builder_class()().write(
    tmp_path,
    table_id="table-caveat",
    source_artifact_refs=[_artifact_ref()],
    field_projection={"columns": ["claim_id", "maturity_label"]},
    maturity_label="preliminary",
    applicable_destinations=["reports"],
    caveat_refs=[_caveat_ref()],
  )

  payload = json.loads(path.read_text(encoding="utf-8"))
  schema_path = REPO_ROOT / "analysis" / "figures_tables" / "table_bundle.schema.json"
  schema = json.loads(schema_path.read_text(encoding="utf-8"))
  jsonschema.Draft202012Validator(schema).validate(payload)
  assert payload["caveat_refs"] == [_caveat_ref()]


def test_figure_bundle_builder_writes_required_fields(tmp_path):
  """figure bundle builder は必須 5 項目を持つ図データ束を書く。"""
  path = _figure_builder_class()().write(
    tmp_path,
    figure_id="figure-001",
    source_artifact_refs=[_artifact_ref()],
    plot_contract={"mark": "bar", "x": "review_mode", "y": "count"},
    maturity_label="preliminary",
    applicable_destinations=["dashboard"],
  )

  payload = json.loads(path.read_text(encoding="utf-8"))
  assert path.name == "figure-001.json"
  assert payload["figure_id"] == "figure-001"
  assert payload["plot_contract"]["mark"] == "bar"
  assert payload["maturity_label"] == "preliminary"


def test_figure_bundle_builder_preserves_optional_caveat_refs(tmp_path):
  """figure bundle builder は任意の caveat_refs を保持する。"""
  path = _figure_builder_class()().write(
    tmp_path,
    figure_id="figure-caveat",
    source_artifact_refs=[_artifact_ref()],
    plot_contract={"mark": "bar", "x": "review_mode", "y": "count"},
    maturity_label="exploratory",
    applicable_destinations=["dashboard"],
    caveat_refs=[_caveat_ref()],
  )

  payload = json.loads(path.read_text(encoding="utf-8"))
  schema_path = REPO_ROOT / "analysis" / "figures_tables" / "figure_bundle.schema.json"
  schema = json.loads(schema_path.read_text(encoding="utf-8"))
  jsonschema.Draft202012Validator(schema).validate(payload)
  assert payload["caveat_refs"] == [_caveat_ref()]


def test_fragment_builder_uses_conservative_maturity_and_keeps_sources(tmp_path):
  """断片は複数出典のうち保守的な maturity_label を採り、出典別も保持する。"""
  path = _fragment_builder_module().FragmentBuilder().write(
    tmp_path,
    fragment_id="fragment-001",
    fragment_type="comparison_summary",
    source_artifact_refs=[
      {**_artifact_ref("claim-001"), "maturity_label": "mature"},
      {**_artifact_ref("claim-002"), "maturity_label": "exploratory"},
    ],
    text_stub="runtime mediated evidence is preliminary.",
    applicable_destinations=["reports"],
  )

  payload = json.loads(path.read_text(encoding="utf-8"))
  assert payload["fragment_id"] == "fragment-001"
  assert payload["fragment_type"] == "comparison_summary"
  assert payload["maturity_label"] == "exploratory"
  assert payload["source_maturity_labels"] == {
    "claim-001": "mature",
    "claim-002": "exploratory",
  }


def test_fragment_builder_preserves_optional_caveat_refs(tmp_path):
  """fragment builder は任意の caveat_refs を保持する。"""
  path = _fragment_builder_module().FragmentBuilder().write(
    tmp_path,
    fragment_id="fragment-caveat",
    fragment_type="limitation_note",
    source_artifact_refs=[_artifact_ref()],
    text_stub="exploratory evidence needs a caveat.",
    applicable_destinations=["reports"],
    caveat_refs=[_caveat_ref()],
  )

  payload = json.loads(path.read_text(encoding="utf-8"))
  schema_path = REPO_ROOT / "analysis" / "fragments" / "fragment.schema.json"
  schema = json.loads(schema_path.read_text(encoding="utf-8"))
  jsonschema.Draft202012Validator(schema).validate(payload)
  assert payload["caveat_refs"] == [_caveat_ref()]


def test_fragment_builder_rejects_unknown_fragment_type(tmp_path):
  """未知の fragment_type は許容しない。"""
  try:
    _fragment_builder_module().FragmentBuilder().write(
      tmp_path,
      fragment_id="fragment-unknown",
      fragment_type="unknown",
      source_artifact_refs=[_artifact_ref()],
      text_stub="bad fragment",
      applicable_destinations=["reports"],
    )
  except ValueError as exc:
    assert "fragment_type" in str(exc)
  else:
    raise AssertionError("未知の fragment_type が受理された")
