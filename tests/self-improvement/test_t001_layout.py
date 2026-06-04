"""self-improvement T-001 成果物配置のテスト。"""
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


WORKFLOW_DIRS = [
  "learning/workflow/proposals",
  "learning/workflow/approved-updates",
  "learning/workflow/rejected-updates",
  "learning/workflow/rollback",
  "learning/workflow/metrics",
  "learning/workflow/schemas",
]

FUTURE_LAYER_DIRS = [
  "learning/findings",
  "learning/backtests",
  "learning/templates",
]


def _read(path):
  return (REPO_ROOT / path).read_text(encoding="utf-8")


def test_t001_workflow_directories_have_readme_and_gitkeep():
  """learning/workflow 配下 6 ディレクトリは README と .gitkeep を持つ。"""
  for relpath in WORKFLOW_DIRS:
    directory = REPO_ROOT / relpath
    assert directory.is_dir(), relpath
    assert (directory / ".gitkeep").is_file(), relpath
    readme = directory / "README.md"
    assert readme.is_file(), relpath
    text = readme.read_text(encoding="utf-8")
    assert relpath in text
    assert "self-improvement" in text


def test_t001_future_layer_directories_are_marked_as_phase1_empty():
  """他 4 層用の空置き 3 ディレクトリは第 1 期空置き注記を持つ。"""
  required = "第 1 期空置き、所有権はフェーズ 4 完了後に確定"
  for relpath in FUTURE_LAYER_DIRS:
    directory = REPO_ROOT / relpath
    assert directory.is_dir(), relpath
    assert (directory / ".gitkeep").is_file(), relpath
    text = (directory / "README.md").read_text(encoding="utf-8")
    assert required in text


def test_t001_related_directories_have_readmes():
  """関連ディレクトリは配置目的 README を持つ。"""
  compliance = _read("docs/discipline-compliance-reports/README.md")
  archive = _read("docs/disciplines/archive/README.md")
  assert "docs/discipline-compliance-reports/" in compliance
  assert "遵守検査" in compliance
  assert "docs/disciplines/archive/" in archive
  assert "撤廃" in archive


def test_t001_tools_namespace_and_naming_policy_are_present():
  """tools 配下の self-improvement namespace と命名規約が存在する。"""
  schemas_dir = REPO_ROOT / "tools" / "self_improvement" / "schemas"
  assert schemas_dir.is_dir()
  assert (schemas_dir / ".gitkeep").is_file()
  text = _read("tools/README.md")
  assert "tools/self_improvement/" in text
  assert "tools/self-improvement-check.py" in text
  assert "パッケージ／モジュールはアンダースコア" in text
  assert "単独実行 CLI スクリプトはハイフン" in text


def test_t001_tests_directory_is_tracked():
  """tests/self-improvement は .gitkeep で追跡可能にする。"""
  tests_dir = REPO_ROOT / "tests" / "self-improvement"
  assert tests_dir.is_dir()
  assert (tests_dir / ".gitkeep").is_file()
