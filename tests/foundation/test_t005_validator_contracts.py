"""T-005 のテスト：検証器側契約スキーマ（2 ファイル）。

対応タスク：foundation tasks.md T-005
対応設計節：design.md §8 検証と無効化のモデル
対応要件：Requirement 6 受入 3（無効化マーカー）、受入 4、受入 9

テスト要件（tasks.md T-005 より）：
- 2 スキーマの meta-schema 検証
- 必須項目数テスト
- scope enum テスト
"""
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

REPO_ROOT = Path(__file__).resolve().parents[2]
CONTRACT_DIR = REPO_ROOT / "runtime/validators/contracts"

SCHEMA_FILES = [
  "validator_result.schema.json",
  "invalidation_marker.schema.json",
]

# design.md §8 各スキーマの必須項目（各 6 項目）
EXPECTED_REQUIRED = {
  "validator_result.schema.json": [
    "run_id", "validator_status", "checked_contract",
    "error_list", "validated_by", "validated_at",
  ],
  "invalidation_marker.schema.json": [
    "run_id", "reason_code", "reason_detail",
    "scope", "issued_by", "issued_at",
  ],
}

# design.md §8 の scope enum 正本値
SCOPE_ENUM = ["run", "step", "finding"]


def _load(filename):
  path = CONTRACT_DIR / filename
  if not path.is_file():
    pytest.fail(f"スキーマが存在しない：{filename}")
  with path.open(encoding="utf-8") as f:
    return json.load(f)


@pytest.mark.parametrize("filename", SCHEMA_FILES)
def test_schema_is_valid_json(filename):
  """2 スキーマが JSON として解析可能。"""
  _load(filename)


@pytest.mark.parametrize("filename", SCHEMA_FILES)
def test_schema_passes_meta_schema(filename):
  """2 スキーマが JSON Schema meta-schema 検証を通る。"""
  schema = _load(filename)
  Draft202012Validator.check_schema(schema)


@pytest.mark.parametrize("filename", SCHEMA_FILES)
def test_required_fields_match(filename):
  """各スキーマの required 配列が design.md §8 と一致する（各 6 項目）。"""
  schema = _load(filename)
  required = schema.get("required", [])
  assert set(required) == set(EXPECTED_REQUIRED[filename]), (
    f"{filename} の required が design.md §8 と一致しない：{required}"
  )
  assert len(required) == 6, f"{filename} の必須項目が 6 件でない：{len(required)}"


def test_invalidation_marker_scope_enum():
  """invalidation_marker.scope の enum が正本 3 値と一致する。"""
  schema = _load("invalidation_marker.schema.json")
  enum = schema["properties"]["scope"].get("enum")
  assert enum == SCOPE_ENUM, f"scope enum が一致しない：{enum}"
