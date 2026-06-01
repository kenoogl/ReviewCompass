"""T-004 のテスト：共有スキーマ群（5 ファイル）。

対応タスク：foundation tasks.md T-004
対応設計節：design.md §4 共有スキーマの関係、§5 段別再演モデル
対応要件：Requirement 3（共通スキーマ集合）、Requirement 1 受入 4（counter_status 必須化）

テスト要件（tasks.md T-004 より）：
- 5 スキーマの meta-schema 検証
- 必須項目数テスト（review_case 必須 8 項目ほか）
- enum 値テスト（severity 4 値・counter_status 3 値・final_label 3 値）
"""
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_DIR = REPO_ROOT / "runtime/schemas"

SCHEMA_FILES = [
  "review_case.schema.json",
  "finding.schema.json",
  "impact_score.schema.json",
  "failure_observation.schema.json",
  "necessity_judgment.schema.json",
]

# design.md §4 各スキーマの必須項目
EXPECTED_REQUIRED = {
  "review_case.schema.json": [
    "run_id", "target_id", "run_metadata_ref", "step_records", "findings",
    "validator_result_refs", "invalidation_marker_refs", "integration_summary",
  ],
  "finding.schema.json": [
    "finding_id", "step_id", "source_role", "severity", "summary",
    "source_refs", "counter_evidence_refs", "judgment_ref",
    "decision_unit_id", "human_decision_ref", "counter_status",
  ],
  "impact_score.schema.json": [
    "finding_ref", "severity_axis", "fix_cost_axis", "downstream_scope_axis",
  ],
  "failure_observation.schema.json": [
    "observation_id", "run_ref", "related_finding_ref",
    "failure_type", "missed_by_role", "detected_at_step",
  ],
  "necessity_judgment.schema.json": [
    "requirement_link", "ignored_impact", "fix_cost", "scope_expansion",
    "uncertainty", "final_label", "recommended_action",
  ],
}

# design.md §4 の enum 正本値
SEVERITY_ENUM = ["CRITICAL", "ERROR", "WARN", "INFO"]
COUNTER_STATUS_ENUM = [
  "counter_evidence_raised",
  "no_counter_evidence_after_challenge",
  "not_assessed",
]
FINAL_LABEL_ENUM = ["must-fix", "should-fix", "leave-as-is"]


def _load(filename):
  path = SCHEMA_DIR / filename
  if not path.is_file():
    pytest.fail(f"スキーマが存在しない：{filename}")
  with path.open(encoding="utf-8") as f:
    return json.load(f)


@pytest.mark.parametrize("filename", SCHEMA_FILES)
def test_schema_is_valid_json(filename):
  """5 スキーマが JSON として解析可能。"""
  _load(filename)


@pytest.mark.parametrize("filename", SCHEMA_FILES)
def test_schema_passes_meta_schema(filename):
  """5 スキーマが JSON Schema meta-schema 検証を通る。"""
  schema = _load(filename)
  # check_schema は不適合なら例外を投げる
  Draft202012Validator.check_schema(schema)


@pytest.mark.parametrize("filename", SCHEMA_FILES)
def test_required_fields_match(filename):
  """各スキーマの required 配列が design.md §4 と一致する。"""
  schema = _load(filename)
  required = schema.get("required", [])
  assert set(required) == set(EXPECTED_REQUIRED[filename]), (
    f"{filename} の required が design.md §4 と一致しない：{required}"
  )


def test_review_case_required_count_is_8():
  """review_case の必須項目が 8 件（topic-01 で 9→8 訂正、failure_observations 削除）。"""
  schema = _load("review_case.schema.json")
  assert len(schema.get("required", [])) == 8


def test_finding_severity_enum():
  """finding.severity の enum が正本 4 値と一致する。"""
  schema = _load("finding.schema.json")
  enum = schema["properties"]["severity"].get("enum")
  assert enum == SEVERITY_ENUM, f"severity enum が一致しない：{enum}"


def test_finding_counter_status_enum():
  """finding.counter_status の enum が正本 3 値と一致する。"""
  schema = _load("finding.schema.json")
  enum = schema["properties"]["counter_status"].get("enum")
  assert enum == COUNTER_STATUS_ENUM, f"counter_status enum が一致しない：{enum}"


def test_necessity_judgment_final_label_enum():
  """necessity_judgment.final_label の enum が正本 3 値と一致する。"""
  schema = _load("necessity_judgment.schema.json")
  enum = schema["properties"]["final_label"].get("enum")
  assert enum == FINAL_LABEL_ENUM, f"final_label enum が一致しない：{enum}"


def test_necessity_judgment_override_reason_optional():
  """necessity_judgment.override_reason は任意（required に含めない、design.md §4）。"""
  schema = _load("necessity_judgment.schema.json")
  assert "override_reason" not in schema.get("required", []), (
    "override_reason は任意項目だが required に含まれている"
  )
