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


def test_workflow_management_implementation_drafting_tracks_integrated_design_reopen():
  text = REPORT.read_text(encoding="utf-8")
  required_fragments = [
    "2026-06-19 integrated design Requirement 13〜16 implementation drafting",
    "T-016",
    "T-017",
    "T-018",
    "T-019",
    "Phase 0〜6",
    "operation contract",
    "side track stack",
    "workflow-state snapshot",
    "proxy_model triage decision",
  ]
  for fragment in required_fragments:
    assert fragment in text


def test_workflow_management_implementation_drafting_tracks_proxy_review_fixes():
  text = REPORT.read_text(encoding="utf-8")
  required_fragments = [
    "proxy_model implementation triad-review C1〜C6 対応",
    "drafting 完了は triad-review 開始準備の記録であり、implementation triad-review 完了ではない",
    "staged file set digest",
    "human-only decision",
    "proxy_model decision",
    "preconditions",
    "postconditions",
    "side_effects",
    "workflow_state_effect",
    "text-only 互換 WARN",
    "manifest 不一致 DEVIATION",
    "review-wave consumer impact blocking",
    "実行済み検証",
    "実装時に追加する予定の検証",
  ]
  for fragment in required_fragments:
    assert fragment in text
