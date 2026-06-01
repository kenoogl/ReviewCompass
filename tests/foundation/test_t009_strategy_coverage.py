"""T-009 のテスト：テスト戦略全体の整備。

対応タスク：foundation tasks.md T-009
対応設計節：design.md §テスト戦略（7 項目）
対応要件：Requirement 3 受入 9、Requirement 6 受入 4

テスト要件（tasks.md T-009 より）：
- design.md §テスト戦略の 7 項目が、tests/foundation/ のテストで網羅されている
- すべての pytest が pass（回帰なし）は、グループ全体の緑で担保
"""
from pathlib import Path

TESTS_DIR = Path(__file__).resolve().parent

# design.md §テスト戦略の 7 項目 → 対応テストファイルのマッピング
STRATEGY_COVERAGE = {
  "スキーマ整合": ["test_t004_schemas.py", "test_t005_validator_contracts.py"],
  "符号化規約整合": ["test_t008_encoding.py"],
  "枠組み整合": ["test_t002_framework.py"],
  "メタデータ整合": ["test_t003_metadata.py"],
  "語彙正本整合": ["test_t003_metadata.py", "test_t004_schemas.py"],
  "プロンプト整合": ["test_t006_prompts.py"],
  "雛形整合": ["test_t007_config_templates.py"],
}


def test_strategy_has_exactly_7_items():
  """テスト戦略が 7 項目ちょうどである。"""
  assert len(STRATEGY_COVERAGE) == 7


def test_each_strategy_item_has_existing_test_files():
  """7 項目それぞれに、実在するテストファイルが対応している。"""
  for item, files in STRATEGY_COVERAGE.items():
    for filename in files:
      path = TESTS_DIR / filename
      assert path.is_file(), f"戦略項目「{item}」の対応テストが存在しない：{filename}"


def test_no_strategy_item_is_unmapped():
  """すべての戦略項目が 1 つ以上のテストファイルにマップされている。"""
  for item, files in STRATEGY_COVERAGE.items():
    assert len(files) >= 1, f"戦略項目「{item}」にテストが対応していない"


# --- A-003 対処：語彙正本整合の 7 語彙を実体で網羅検査（design.md §テスト戦略「語彙正本整合」）---

import json  # noqa: E402

import yaml  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]

# design.md §テスト戦略「語彙正本整合」が網羅を求める 7 語彙と、その所在
# （metadata_contract.yaml の vocabularies、または対応スキーマの enum）
SEVEN_VOCABULARIES = [
  "counter_status",       # finding スキーマ
  "validator_status",     # metadata_contract
  "evidence_class",       # metadata_contract
  "review_mode",          # metadata_contract
  "severity",             # finding スキーマ
  "final_label",          # necessity_judgment スキーマ
  "confidence_label",     # metadata_contract
]


def _metadata_vocabularies():
  path = REPO_ROOT / "runtime/foundation/metadata_contract.yaml"
  with path.open(encoding="utf-8") as f:
    return yaml.safe_load(f).get("vocabularies", {})


def _schema_enum(rel_path, prop):
  path = REPO_ROOT / rel_path
  with path.open(encoding="utf-8") as f:
    return json.load(f)["properties"][prop].get("enum")


def test_seven_vocabularies_are_actually_defined():
  """7 語彙すべてが実体（metadata_contract または対応スキーマの enum）に定義されている。

  ファイル単位のマッピング存在だけでなく、語彙の中身が実在することを確認する（A-003 対処）。
  """
  meta_vocabs = _metadata_vocabularies()
  located = []
  # metadata_contract に置かれる 4 語彙
  for name in ["validator_status", "evidence_class", "review_mode", "confidence_label"]:
    assert name in meta_vocabs and meta_vocabs[name], f"metadata_contract に語彙 {name} がない"
    located.append(name)
  # スキーマの enum に置かれる 3 語彙
  assert _schema_enum("runtime/schemas/finding.schema.json", "counter_status"), "counter_status enum がない"
  located.append("counter_status")
  assert _schema_enum("runtime/schemas/finding.schema.json", "severity"), "severity enum がない"
  located.append("severity")
  assert _schema_enum("runtime/schemas/necessity_judgment.schema.json", "final_label"), "final_label enum がない"
  located.append("final_label")

  assert set(located) == set(SEVEN_VOCABULARIES), (
    f"7 語彙の網羅が確認できない：{set(SEVEN_VOCABULARIES) - set(located)}"
  )
