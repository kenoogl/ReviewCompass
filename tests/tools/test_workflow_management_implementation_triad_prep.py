from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
PREP_PATH = (
  REPO_ROOT
  / ".reviewcompass"
  / "specs"
  / "workflow-management"
  / "reviews"
  / "2026-06-04-implementation-triad-review-prep.md"
)


def test_workflow_management_implementation_triad_prep_exists():
  assert PREP_PATH.exists()


def test_workflow_management_implementation_triad_prep_lists_review_targets():
  text = PREP_PATH.read_text(encoding="utf-8")
  required_targets = [
    "tools/check-workflow-action.py",
    "tests/tools/test_check_workflow_action.py",
    "tests/tools/test_workflow_management_implementation_drafting.py",
    ".reviewcompass/specs/workflow-management/implementation-drafting.md",
    "docs/operations/WORKFLOW_PRECHECK.md",
    "docs/notes/2026-06-04-proxy-review-parallel-implementation-plan.md",
  ]

  for target in required_targets:
    assert target in text


def test_workflow_management_implementation_triad_prep_records_review_discipline():
  text = PREP_PATH.read_text(encoding="utf-8")
  required_phrases = [
    "raw response",
    "三段階トリアージ",
    "重要所見",
    "承認",
    "proxy decision",
    "main session LLM",
  ]

  for phrase in required_phrases:
    assert phrase in text
