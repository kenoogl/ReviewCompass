"""T-001 のテスト：共有資産ディレクトリ構造とアプリ側規約の準備。

対応タスク：foundation tasks.md T-001
対応設計節：design.md §共有資産配置、§配置決定
対応要件：Requirement 5（パターン定義依存の除外）、Requirement 7（リポジトリ内資産の規則）

テスト要件（tasks.md T-001 より）：
- ディレクトリ存在検査（5 ディレクトリ）
- README 存在検査（5 README）
- tests/foundation/.gitkeep 存在検査
- docs/operations/FOUNDATION.md にアプリ側 .reviewcompass/config.yaml 規約が記述されている
"""
from pathlib import Path

import pytest

# リポジトリルート（tests/foundation/ から 2 階層上）
REPO_ROOT = Path(__file__).resolve().parents[2]

# design.md §共有資産配置で正本とされた 5 ディレクトリ
EXPECTED_DIRS = [
  "runtime/foundation",
  "runtime/schemas",
  "runtime/prompts",
  "runtime/config",
  "runtime/validators/contracts",
]


@pytest.mark.parametrize("rel_dir", EXPECTED_DIRS)
def test_directory_exists(rel_dir):
  """5 つの共有資産ディレクトリが存在する。"""
  target = REPO_ROOT / rel_dir
  assert target.is_dir(), f"ディレクトリが存在しない：{rel_dir}"


@pytest.mark.parametrize("rel_dir", EXPECTED_DIRS)
def test_readme_exists(rel_dir):
  """5 つのディレクトリそれぞれに README.md が存在する。"""
  readme = REPO_ROOT / rel_dir / "README.md"
  assert readme.is_file(), f"README.md が存在しない：{rel_dir}/README.md"


def test_tests_foundation_gitkeep_exists():
  """tests/foundation/.gitkeep が存在し Git 追跡可能（topic-15 採用）。"""
  gitkeep = REPO_ROOT / "tests/foundation/.gitkeep"
  assert gitkeep.is_file(), "tests/foundation/.gitkeep が存在しない"


def test_foundation_operations_doc_exists():
  """docs/operations/FOUNDATION.md が存在する。"""
  doc = REPO_ROOT / "docs/operations/FOUNDATION.md"
  assert doc.is_file(), "docs/operations/FOUNDATION.md が存在しない"


def test_foundation_doc_describes_app_side_config_convention():
  """FOUNDATION.md にアプリ側 .reviewcompass/config.yaml の規約が記述されている。

  完了条件 1（tasks.md T-001）：「アプリ側 .reviewcompass/config.yaml」の規約が記述されている。
  """
  doc = REPO_ROOT / "docs/operations/FOUNDATION.md"
  if not doc.is_file():
    pytest.fail("docs/operations/FOUNDATION.md が存在しない")
  text = doc.read_text(encoding="utf-8")
  assert ".reviewcompass/config.yaml" in text, (
    "FOUNDATION.md に '.reviewcompass/config.yaml' の規約記述がない"
  )
