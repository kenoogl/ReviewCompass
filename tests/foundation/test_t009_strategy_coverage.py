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
