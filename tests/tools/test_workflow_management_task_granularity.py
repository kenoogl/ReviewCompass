from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
TASKS = REPO_ROOT / ".reviewcompass" / "specs" / "workflow-management" / "tasks.md"
SESSION_GUIDE = REPO_ROOT / "docs" / "operations" / "SESSION_WORKFLOW_GUIDE.md"


def test_implementation_drafting_artifacts_are_not_adopted():
  assert not list((REPO_ROOT / ".reviewcompass" / "specs").glob("**/implementation-drafting.md"))


def test_tasks_define_implementation_ready_granularity():
  text = TASKS.read_text(encoding="utf-8")
  required_fragments = [
    "implementation drafting へ直接入れる粒度",
    "実装対象ファイル",
    "最初に書く失敗テスト",
    "実装順序",
    "検証コマンド",
    "禁止事項",
    "停止条件",
    "implementation-drafting.md は正本成果物として採用しない",
  ]
  for fragment in required_fragments:
    assert fragment in text


def test_session_guide_defines_implementation_drafting_as_code_generation():
  text = SESSION_GUIDE.read_text(encoding="utf-8")
  required_fragments = [
    "requirements／design／tasks の drafting は文書起草を意味する",
    "implementation の drafting は文書起草ではなく",
    "テストと実装コードの生成",
    "implementation-plan.md や implementation-drafting.md",
    "正本成果物として要求しない",
  ]
  for fragment in required_fragments:
    assert fragment in text
