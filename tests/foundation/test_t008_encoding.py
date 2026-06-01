"""T-008 のテスト：符号化規約整合検証スクリプト。

対応タスク：foundation tasks.md T-008
対応設計節：design.md §4「mandatory／deferred の JSON Schema 符号化規約」
対応要件：Requirement 3 受入 9

テスト要件（tasks.md T-008 より）：
- 規約準拠スキーマでの pass テスト
- 非準拠スキーマでの fail テスト（fixture）
- 実 7 スキーマがすべて準拠
"""
import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "tools" / "foundation_validators"))

import check_encoding_convention as cec  # noqa: E402

# 実 7 スキーマ
ALL_SCHEMAS = [
  REPO_ROOT / "runtime/schemas/review_case.schema.json",
  REPO_ROOT / "runtime/schemas/finding.schema.json",
  REPO_ROOT / "runtime/schemas/impact_score.schema.json",
  REPO_ROOT / "runtime/schemas/failure_observation.schema.json",
  REPO_ROOT / "runtime/schemas/necessity_judgment.schema.json",
  REPO_ROOT / "runtime/validators/contracts/validator_result.schema.json",
  REPO_ROOT / "runtime/validators/contracts/invalidation_marker.schema.json",
]


def test_compliant_schema_passes():
  """required を持ち deferred 注記のないスキーマは準拠（エラー 0）。"""
  schema = {
    "description": "テスト用",
    "required": ["a"],
    "properties": {"a": {"type": "string"}},
  }
  assert cec.check_schema_encoding(schema) == []


def test_missing_required_fails():
  """required 配列がないスキーマは非準拠（mandatory を表現できない）。"""
  schema = {"description": "x", "properties": {"a": {}}}
  errors = cec.check_schema_encoding(schema)
  assert errors, "required 欠落が検出されない"


def test_x_deferred_without_description_fails():
  """x-deferred があるのに description がないスキーマは非準拠。"""
  schema = {"required": ["a"], "x-deferred": "委譲先を示す"}
  errors = cec.check_schema_encoding(schema)
  assert errors, "x-deferred ＋ description 欠落が検出されない"


def test_x_deferred_with_description_passes():
  """x-deferred と description が揃えば準拠。"""
  schema = {
    "required": ["a"],
    "x-deferred": "評価仕様に委譲",
    "description": "説明",
  }
  assert cec.check_schema_encoding(schema) == []


def test_empty_x_deferred_fails():
  """x-deferred が空文字列なら非準拠（委譲先を文章で示す義務）。"""
  schema = {"required": ["a"], "x-deferred": "", "description": "x"}
  errors = cec.check_schema_encoding(schema)
  assert errors, "空の x-deferred が検出されない"


def test_staleness_propagation_alias_accepted():
  """検証器側契約は x-staleness-propagation を x-deferred の代替注記として許容する。"""
  schema = {
    "required": ["a"],
    "x-staleness-propagation": "evaluation／analysis に委譲",
    "description": "説明",
  }
  assert cec.check_schema_encoding(schema) == []


@pytest.mark.parametrize("schema_path", ALL_SCHEMAS, ids=lambda p: p.name)
def test_real_schemas_compliant(schema_path):
  """実 7 スキーマがすべて符号化規約に準拠する。"""
  with schema_path.open(encoding="utf-8") as f:
    schema = json.load(f)
  errors = cec.check_schema_encoding(schema)
  assert errors == [], f"{schema_path.name} が非準拠：{errors}"


def test_main_returns_zero_for_all_real_schemas():
  """main を実 7 スキーマに対して実行すると exit 0。"""
  argv = [str(p) for p in ALL_SCHEMAS]
  assert cec.main(argv) == 0


def test_main_returns_nonzero_for_noncompliant(tmp_path):
  """非準拠スキーマを渡すと main は非ゼロを返す。"""
  bad = tmp_path / "bad.schema.json"
  bad.write_text(json.dumps({"properties": {"a": {}}}), encoding="utf-8")
  assert cec.main([str(bad)]) != 0


# --- P-002 対処：入れ子 object・配列 items 内の required 検査（design.md §4 行311）---

def test_nested_object_missing_required_fails():
  """properties を持つ入れ子 object に required がなければ非準拠（入れ子の mandatory 未表現）。"""
  schema = {
    "required": ["a"],
    "description": "x",
    "properties": {
      "a": {"type": "object", "properties": {"b": {"type": "string"}}},
    },
  }
  errors = cec.check_schema_encoding(schema)
  assert errors, "入れ子 object の required 欠落が検出されない"


def test_nested_object_with_required_passes():
  """properties を持つ入れ子 object が required を持てば準拠。"""
  schema = {
    "required": ["a"],
    "description": "x",
    "properties": {
      "a": {
        "type": "object",
        "required": ["b"],
        "properties": {"b": {"type": "string"}},
      },
    },
  }
  assert cec.check_schema_encoding(schema) == []


def test_array_items_object_missing_required_fails():
  """配列 items が properties を持つ object なのに required がなければ非準拠。"""
  schema = {
    "required": ["a"],
    "description": "x",
    "properties": {
      "a": {
        "type": "array",
        "items": {"type": "object", "properties": {"b": {"type": "string"}}},
      },
    },
  }
  errors = cec.check_schema_encoding(schema)
  assert errors, "配列 items 内 object の required 欠落が検出されない"


def test_empty_object_items_passes():
  """properties を持たない空 object（保持方法を runtime に委ねる items）は required 不要で準拠。"""
  schema = {
    "required": ["a"],
    "description": "x",
    "properties": {
      "a": {"type": "array", "items": {"type": "object"}},
    },
  }
  assert cec.check_schema_encoding(schema) == []
