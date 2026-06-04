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
    ".reviewcompass/specs/workflow-management/requirements.md",
    ".reviewcompass/specs/workflow-management/design.md",
    ".reviewcompass/specs/workflow-management/tasks.md",
    ".reviewcompass/specs/workflow-management/spec.json",
    "tools/check-workflow-action.py",
    "tools/api_providers/run_review.py",
    "tools/api_providers/run_role.py",
    "tools/api_providers/review_triage.py",
    "tests/tools/test_check_workflow_action.py",
    "tests/tools/test_workflow_management_implementation_drafting.py",
    "tools/api_providers/tests/test_run_review.py",
    "tools/api_providers/tests/test_run_role.py",
    "tools/api_providers/tests/test_review_triage.py",
    ".reviewcompass/specs/workflow-management/implementation-drafting.md",
    "docs/operations/WORKFLOW_PRECHECK.md",
    "docs/operations/SESSION_WORKFLOW_GUIDE.md",
    "docs/notes/2026-06-04-proxy-review-parallel-implementation-plan.md",
  ]

  for target in required_targets:
    assert target in text


def test_workflow_management_implementation_triad_prep_records_review_discipline():
  text = PREP_PATH.read_text(encoding="utf-8")
  required_phrases = [
    "target-manifest.yaml",
    "rounds.yaml",
    "model-result-summary.yaml",
    "triage.yaml",
    "review_summary.md",
    "docs/logs/autonomous-parallel/",
    "raw response",
    "三段階トリアージ",
    "重要所見",
    "承認",
    "proxy decision",
    "main session LLM",
  ]

  for phrase in required_phrases:
    assert phrase in text
