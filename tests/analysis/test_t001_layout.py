"""T-001 のテスト：analysis 成果物配置の準備。

対応タスク：analysis tasks.md T-001
対応設計節：design.md §分析向け成果物配置、§配置の根拠
対応要件：Requirement 8 受入 1、3

テスト要件（tasks.md T-001 より）：
- ディレクトリ存在検査
- README 存在検査
- tests/analysis/.gitkeep 存在検査
- docs/operations/ANALYSIS.md のアプリ側規約記述検査
"""
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]

EXPECTED_DIRS = [
  "analysis/shared",
  "analysis/shared/conformance",
  "analysis/shared/convergence",
  "analysis/shared/manifests",
  "analysis/destinations",
  "analysis/destinations/dashboard",
  "analysis/destinations/weekly",
  "analysis/destinations/audit",
  "analysis/destinations/reports",
  "analysis/figures_tables",
  "analysis/figures_tables/table_source_bundles",
  "analysis/figures_tables/figure_source_bundles",
]

EXPECTED_READMES = [
  "analysis/README.md",
  "analysis/shared/README.md",
  "analysis/shared/conformance/README.md",
  "analysis/shared/convergence/README.md",
  "analysis/shared/manifests/README.md",
  "analysis/destinations/README.md",
  "analysis/figures_tables/README.md",
]

MANIFEST_TEMPLATE = REPO_ROOT / "analysis/shared/manifests/analysis_manifest.yaml"
MANIFEST_SCHEMA = REPO_ROOT / "analysis/shared/manifests/analysis_manifest.schema.json"
ANALYSIS_DOC = REPO_ROOT / "docs/operations/ANALYSIS.md"


@pytest.mark.parametrize("rel_dir", EXPECTED_DIRS)
def test_analysis_layout_directory_exists(rel_dir):
  """analysis 配下の必須ディレクトリが存在する。"""
  assert (REPO_ROOT / rel_dir).is_dir(), f"ディレクトリが存在しない：{rel_dir}"


@pytest.mark.parametrize("rel_path", EXPECTED_READMES)
def test_analysis_layout_readme_exists(rel_path):
  """analysis 配下の必須 README が存在する。"""
  assert (REPO_ROOT / rel_path).is_file(), f"README が存在しない：{rel_path}"


def test_analysis_manifest_template_exists():
  """analysis_manifest.yaml の空雛形が存在する。"""
  assert MANIFEST_TEMPLATE.is_file(), "analysis_manifest.yaml が存在しない"


def test_analysis_manifest_schema_exists():
  """analysis_manifest.schema.json が存在する。"""
  assert MANIFEST_SCHEMA.is_file(), "analysis_manifest.schema.json が存在しない"


def test_tests_analysis_gitkeep_exists():
  """tests/analysis/.gitkeep が存在する。"""
  assert (REPO_ROOT / "tests/analysis/.gitkeep").is_file(), (
    "tests/analysis/.gitkeep が存在しない"
  )


def test_analysis_operations_doc_describes_app_side_analysis_convention():
  """ANALYSIS.md にアプリ側 .reviewcompass/analysis/ 規約が記述されている。"""
  text = ANALYSIS_DOC.read_text(encoding="utf-8")
  assert ".reviewcompass/analysis/" in text
  assert "analysis/shared/" in text
  assert "analysis/destinations/" in text
  assert "analysis/figures_tables/" in text
