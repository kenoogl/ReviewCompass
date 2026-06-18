"""Phase 1 最小スキーマ定義のテスト

対象：
  .reviewcompass/schema/required_action.schema.json
  .reviewcompass/schema/next_action_response.schema.json

TDD 規律（AGENTS.md）に従い、スキーマファイル作成前に本テストを作成。
"""

import json
import subprocess
import sys
import unittest
from pathlib import Path

import jsonschema

REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_DIR = REPO_ROOT / ".reviewcompass" / "schema"
REQUIRED_ACTION_SCHEMA_PATH = SCHEMA_DIR / "required_action.schema.json"
NEXT_RESPONSE_SCHEMA_PATH = SCHEMA_DIR / "next_action_response.schema.json"

# D-003 §6 で定義された19段階優先順位の required_action 語彙（優先順位順）
EXPECTED_REQUIRED_ACTIONS = [
  "repair_workflow_state",
  "run_post_write_verification",
  "wait_for_human_decision",
  "record_human_decision",
  "run_maintenance",
  "advance_reopen_after_commit_stop_point",
  "commit_stop_point",
  "draft_reopen_plan_candidates",
  "apply_approved_reopen_plan",
  "advance_reopen_after_approval_stop_point",
  "repair_canonical_documents",
  "run_reopen_drafting",
  "run_reopen_pending_gate",
  "collect_required_decisions",
  "finalize_reopen",
  "draft_reopen_classification",
  "run_reopen_start",
  "run_workflow_stage",
  "completed",
]


class TestRequiredActionSchema(unittest.TestCase):
  """required_action.schema.json の内容テスト"""

  def _load(self):
    self.assertTrue(
      REQUIRED_ACTION_SCHEMA_PATH.exists(),
      f"スキーマファイルが存在しない: {REQUIRED_ACTION_SCHEMA_PATH}",
    )
    with REQUIRED_ACTION_SCHEMA_PATH.open(encoding="utf-8") as f:
      return json.load(f)

  def test_file_exists(self):
    self.assertTrue(
      REQUIRED_ACTION_SCHEMA_PATH.exists(),
      "required_action.schema.json が存在しない",
    )

  def test_valid_json(self):
    schema = self._load()
    self.assertIsInstance(schema, dict)

  def test_has_schema_id(self):
    schema = self._load()
    self.assertIn("$schema", schema)
    self.assertIn("$id", schema)

  def test_type_is_string(self):
    schema = self._load()
    self.assertEqual(schema.get("type"), "string")

  def test_enum_has_exactly_19_values(self):
    schema = self._load()
    enum = schema.get("enum", [])
    self.assertEqual(
      len(enum),
      19,
      f"enum の要素数が19ではない: {len(enum)}",
    )

  def test_all_expected_values_present(self):
    schema = self._load()
    enum = schema.get("enum", [])
    for value in EXPECTED_REQUIRED_ACTIONS:
      self.assertIn(value, enum, f"required_action 語彙が欠落: {value}")

  def test_no_extra_values(self):
    schema = self._load()
    enum = schema.get("enum", [])
    extra = [v for v in enum if v not in EXPECTED_REQUIRED_ACTIONS]
    self.assertEqual(extra, [], f"定義外の語彙が含まれている: {extra}")

  def test_each_value_validates(self):
    schema = self._load()
    validator = jsonschema.Draft202012Validator(schema)
    for value in EXPECTED_REQUIRED_ACTIONS:
      errors = list(validator.iter_errors(value))
      self.assertEqual(
        errors, [],
        f"'{value}' がスキーマを満たさない: {errors}",
      )

  def test_invalid_value_rejected(self):
    schema = self._load()
    validator = jsonschema.Draft202012Validator(schema)
    errors = list(validator.iter_errors("not_a_valid_action"))
    self.assertGreater(len(errors), 0, "不正な値がスキーマを通過した")


class TestNextActionResponseSchema(unittest.TestCase):
  """next_action_response.schema.json の内容テスト"""

  def _load(self):
    self.assertTrue(
      NEXT_RESPONSE_SCHEMA_PATH.exists(),
      f"スキーマファイルが存在しない: {NEXT_RESPONSE_SCHEMA_PATH}",
    )
    with NEXT_RESPONSE_SCHEMA_PATH.open(encoding="utf-8") as f:
      return json.load(f)

  def test_file_exists(self):
    self.assertTrue(
      NEXT_RESPONSE_SCHEMA_PATH.exists(),
      "next_action_response.schema.json が存在しない",
    )

  def test_valid_json(self):
    schema = self._load()
    self.assertIsInstance(schema, dict)

  def test_has_schema_id(self):
    schema = self._load()
    self.assertIn("$schema", schema)
    self.assertIn("$id", schema)

  def test_top_level_is_object(self):
    schema = self._load()
    self.assertEqual(schema.get("type"), "object")

  def test_required_top_level_fields(self):
    schema = self._load()
    required = schema.get("required", [])
    for field in ("verdict", "exit_code", "next_action", "reasons", "current_state"):
      self.assertIn(field, required, f"必須フィールドが定義されていない: {field}")

  def test_next_action_required_fields(self):
    schema = self._load()
    props = schema.get("properties", {})
    self.assertIn("next_action", props)
    next_action_schema = props["next_action"]
    next_action_required = next_action_schema.get("required", [])
    for field in (
      "kind", "required_action", "active_gate", "feature",
      "phase", "stage", "required_feature_scope",
      "blocked_by", "future_gates", "state_refs",
    ):
      self.assertIn(
        field,
        next_action_required,
        f"next_action の必須フィールドが定義されていない: {field}",
      )

  def test_required_action_ref_or_enum(self):
    """next_action.required_action が required_action スキーマを参照しているか enum を持つか"""
    schema = self._load()
    props = schema.get("properties", {})
    next_action_schema = props.get("next_action", {})
    next_action_props = next_action_schema.get("properties", {})
    ra_schema = next_action_props.get("required_action", {})
    has_ref = "$ref" in ra_schema
    has_enum = "enum" in ra_schema
    self.assertTrue(
      has_ref or has_enum,
      "next_action.required_action に $ref または enum がない",
    )

  def test_current_next_json_output_validates(self):
    """現在の next --json 出力がスキーマのうち定義済みフィールドを満たすか（部分検証）"""
    result = subprocess.run(
      [
        sys.executable,
        str(REPO_ROOT / "tools" / "check-workflow-action.py"),
        "next",
        "--json",
      ],
      capture_output=True,
      text=True,
      cwd=str(REPO_ROOT),
    )
    self.assertEqual(result.returncode, 0, f"next --json が失敗: {result.stderr}")
    output = json.loads(result.stdout)
    schema = self._load()

    # verdict / exit_code / next_action / reasons / current_state は現在も存在する
    for field in ("verdict", "exit_code", "next_action", "reasons", "current_state"):
      self.assertIn(field, output, f"next --json の出力に {field} がない")


if __name__ == "__main__":
  unittest.main()
