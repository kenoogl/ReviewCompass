"""T-007 のテスト：レビュー収束過程の可視化。"""
import importlib
import json
from pathlib import Path

import jsonschema
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]


def _role_builder_class():
  module = importlib.import_module("analysis.convergence.role_diff_builder")
  return module.RoleDiffBuilder


def _mode_builder_class():
  module = importlib.import_module("analysis.convergence.mode_diff_builder")
  return module.ModeDiffBuilder


def _guards():
  return importlib.import_module("analysis.traceability.completion_guards")


def _evidence_ref(target_id):
  return {
    "ref_type": "evidence_entry",
    "target_path": "shared/evidence_register.json",
    "target_id": target_id,
  }


def test_role_diff_schema_is_valid_json_schema():
  """role_diff.schema.json は JSON Schema として妥当。"""
  schema_path = REPO_ROOT / "analysis" / "convergence" / "role_diff.schema.json"
  schema = json.loads(schema_path.read_text(encoding="utf-8"))
  jsonschema.Draft202012Validator.check_schema(schema)


def test_mode_diff_schema_is_valid_json_schema():
  """mode_diff.schema.json は JSON Schema として妥当。"""
  schema_path = REPO_ROOT / "analysis" / "convergence" / "mode_diff.schema.json"
  schema = json.loads(schema_path.read_text(encoding="utf-8"))
  jsonschema.Draft202012Validator.check_schema(schema)


def test_role_diff_builder_requires_judgment_final_label_summary(tmp_path):
  """judgment role では by_final_label が条件付き必須。"""
  try:
    _role_builder_class()().write(
      tmp_path,
      entries=[
        {
          "feature": "runtime",
          "role": "judgment",
          "findings_summary": {},
          "target": "runtime/design.md",
        },
      ],
    )
  except ValueError as exc:
    assert "by_final_label" in str(exc)
  else:
    raise AssertionError("judgment の by_final_label 欠落が受理された")


def test_role_diff_builder_requires_adversarial_counter_status_summary(tmp_path):
  """adversarial role では by_counter_status が条件付き必須。"""
  try:
    _role_builder_class()().write(
      tmp_path,
      entries=[
        {
          "feature": "runtime",
          "role": "adversarial",
          "findings_summary": {},
          "target": "runtime/design.md",
        },
      ],
    )
  except ValueError as exc:
    assert "by_counter_status" in str(exc)
  else:
    raise AssertionError("adversarial の by_counter_status 欠落が受理された")


def test_role_diff_schema_requires_by_severity():
  """role_diff schema は findings_summary.by_severity を必須にする。"""
  schema_path = REPO_ROOT / "analysis" / "convergence" / "role_diff.schema.json"
  schema = json.loads(schema_path.read_text(encoding="utf-8"))
  validator = jsonschema.Draft202012Validator(schema)

  errors = list(
    validator.iter_errors(
      {
        "entries": [
          {
            "feature": "runtime",
            "role": "primary",
            "findings_summary": {"total": 1},
            "target": "runtime/design.md",
          },
        ],
      }
    )
  )

  assert any("by_severity" in error.message for error in errors)


def test_role_diff_schema_requires_judgment_final_label_summary():
  """role_diff schema は judgment の by_final_label を条件付き必須にする。"""
  schema_path = REPO_ROOT / "analysis" / "convergence" / "role_diff.schema.json"
  schema = json.loads(schema_path.read_text(encoding="utf-8"))
  validator = jsonschema.Draft202012Validator(schema)

  errors = list(
    validator.iter_errors(
      {
        "entries": [
          {
            "feature": "runtime",
            "role": "judgment",
            "findings_summary": {"by_severity": {"ERROR": 1}},
            "target": "runtime/design.md",
          },
        ],
      }
    )
  )

  assert any("by_final_label" in error.message for error in errors)


def test_role_diff_schema_requires_adversarial_counter_status_summary():
  """role_diff schema は adversarial の by_counter_status を条件付き必須にする。"""
  schema_path = REPO_ROOT / "analysis" / "convergence" / "role_diff.schema.json"
  schema = json.loads(schema_path.read_text(encoding="utf-8"))
  validator = jsonschema.Draft202012Validator(schema)

  errors = list(
    validator.iter_errors(
      {
        "entries": [
          {
            "feature": "runtime",
            "role": "adversarial",
            "findings_summary": {"by_severity": {"WARN": 1}},
            "target": "runtime/design.md",
          },
        ],
      }
    )
  )

  assert any("by_counter_status" in error.message for error in errors)


def test_role_diff_builder_writes_entries(tmp_path):
  """role_diff builder は最低限 4 要素を持つ role_diff.json を書く。"""
  path = _role_builder_class()().write(
    tmp_path,
    entries=[
        {
          "feature": "runtime",
          "role": "primary",
          "findings_summary": {"total": 3, "by_severity": {"WARN": 3}},
          "target": "runtime/design.md",
          "evidence_refs": [_evidence_ref("primary-001")],
        },
        {
          "feature": "runtime",
          "role": "judgment",
          "findings_summary": {
            "total": 2,
            "by_severity": {"ERROR": 1, "INFO": 1},
            "by_final_label": {"must-fix": 1},
          },
          "target": "runtime/design.md",
          "evidence_refs": [_evidence_ref("judgment-001")],
        },
    ],
  )

  payload = json.loads(path.read_text(encoding="utf-8"))
  assert payload["entries"][0]["role"] == "primary"
  assert payload["entries"][0]["evidence_refs"] == [_evidence_ref("primary-001")]
  assert payload["entries"][1]["findings_summary"]["by_final_label"] == {"must-fix": 1}
  assert payload["entries"][1]["evidence_refs"] == [_evidence_ref("judgment-001")]


def test_role_diff_schema_rejects_string_evidence_refs():
  """role_diff evidence_refs は裸文字列ではなく構造化参照。"""
  schema_path = REPO_ROOT / "analysis" / "convergence" / "role_diff.schema.json"
  schema = json.loads(schema_path.read_text(encoding="utf-8"))
  validator = jsonschema.Draft202012Validator(schema)

  errors = list(
    validator.iter_errors(
      {
        "entries": [
          {
            "feature": "runtime",
            "role": "primary",
            "findings_summary": {"by_severity": {"WARN": 1}},
            "target": "runtime/design.md",
            "evidence_refs": ["raw/runtime-primary.txt"],
          },
        ],
      }
    )
  )

  assert errors


def test_mode_diff_builder_preserves_foundation_review_mode_values(tmp_path):
  """mode_diff は foundation 正本 review_mode 値だけを許容する。"""
  foundation = yaml.safe_load(
    (REPO_ROOT / "runtime" / "foundation" / "metadata_contract.yaml").read_text(
      encoding="utf-8",
    )
  )
  review_mode = foundation["vocabularies"]["review_mode"][0]

  path = _mode_builder_class()().write(
    tmp_path,
    entries=[
        {
          "feature": "runtime",
          "review_mode": review_mode,
          "findings_summary": {"total": 1, "by_severity": {"INFO": 1}},
          "target": "runtime/design.md",
          "evidence_refs": [_evidence_ref("mode-001")],
        },
    ],
  )

  payload = json.loads(path.read_text(encoding="utf-8"))
  assert payload["entries"][0]["review_mode"] == review_mode
  assert payload["entries"][0]["evidence_refs"] == [_evidence_ref("mode-001")]


def test_mode_diff_schema_rejects_string_evidence_refs():
  """mode_diff evidence_refs は裸文字列ではなく構造化参照。"""
  schema_path = REPO_ROOT / "analysis" / "convergence" / "mode_diff.schema.json"
  schema = json.loads(schema_path.read_text(encoding="utf-8"))
  validator = jsonschema.Draft202012Validator(schema)

  errors = list(
    validator.iter_errors(
      {
        "entries": [
          {
            "feature": "runtime",
            "review_mode": "manual_dogfooding",
            "findings_summary": {"by_severity": {"WARN": 1}},
            "target": "runtime/design.md",
            "evidence_refs": ["raw/runtime-mode.txt"],
          },
        ],
      }
    )
  )

  assert errors


def test_mode_diff_schema_requires_by_severity():
  """mode_diff schema は findings_summary.by_severity を必須にする。"""
  schema_path = REPO_ROOT / "analysis" / "convergence" / "mode_diff.schema.json"
  schema = json.loads(schema_path.read_text(encoding="utf-8"))
  validator = jsonschema.Draft202012Validator(schema)

  errors = list(
    validator.iter_errors(
      {
        "entries": [
          {
            "feature": "runtime",
            "review_mode": "manual_dogfooding",
            "findings_summary": {"total": 1},
            "target": "runtime/design.md",
          },
        ],
      }
    )
  )

  assert any("by_severity" in error.message for error in errors)


def test_mode_diff_builder_rejects_unknown_review_mode(tmp_path):
  """foundation 正本にない review_mode は許容しない。"""
  try:
    _mode_builder_class()().write(
      tmp_path,
      entries=[
        {
          "feature": "runtime",
          "review_mode": "unknown_mode",
          "findings_summary": {"total": 1},
          "target": "runtime/design.md",
        },
      ],
    )
  except ValueError as exc:
    assert "review_mode" in str(exc)
  else:
    raise AssertionError("未知の review_mode が受理された")


def test_convergence_implementation_does_not_write_evaluation_artifacts():
  """T-007 収束処理は evaluation 成果物へ書き込まない。"""
  assert _guards().evaluation_write_violations(
    REPO_ROOT / "analysis" / "convergence"
  ) == []
