from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
REPORT = REPO_ROOT / ".reviewcompass" / "specs" / "workflow-management" / "implementation-drafting.md"


def test_workflow_management_implementation_drafting_report_exists():
  assert REPORT.exists()


def test_workflow_management_implementation_drafting_report_tracks_autonomous_helpers():
  text = REPORT.read_text(encoding="utf-8")
  required_fragments = [
    "# workflow-management implementation drafting 棚卸し",
    "## 実装済み",
    "autonomous-plan",
    "autonomous-plan-template",
    "autonomous-plan-record-integration",
    "## 未充足",
    "## drafting 完了判断",
  ]
  for fragment in required_fragments:
    assert fragment in text


def test_workflow_management_implementation_drafting_report_mentions_verification():
  text = REPORT.read_text(encoding="utf-8")
  assert "python3 -m unittest tests.tools.test_check_workflow_action -v" in text
  assert "python3 -m pytest tests/tools/test_session_record_contract.py -q" in text
