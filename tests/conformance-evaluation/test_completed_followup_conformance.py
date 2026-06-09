from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
RECORD_PATH = (
  ROOT
  / ".reviewcompass"
  / "specs"
  / "conformance-evaluation"
  / "conformance"
  / "2026-06-09-completed-followup-conformance.md"
)
SUMMARY_PATH = (
  ROOT
  / "docs"
  / "notes"
  / "2026-06-09-formal-completed-followup-summary.md"
)

EXPECTED_CANDIDATES = [
  "D-021",
  "D-004",
  "D-005",
  "D-025",
  "D-027",
  "D-008",
  "D-019",
  "D-020",
  "D-023",
]


def _front_matter_and_body(path):
  text = path.read_text(encoding="utf-8")
  _, front_matter, body = text.split("---", 2)
  return yaml.safe_load(front_matter), body


def test_completed_followup_conformance_record_exists_and_is_check_record():
  front_matter, body = _front_matter_and_body(RECORD_PATH)

  assert front_matter["type"] == "conformance_evaluation"
  assert front_matter["mode_internal"] == "completed_followup_conformance"
  assert front_matter["status"] == "gap_found"
  assert "## Verdict" in body
  assert "implementation-first formal follow-up" in body


def test_completed_followup_conformance_covers_expected_candidates():
  _, body = _front_matter_and_body(RECORD_PATH)

  for candidate_id in EXPECTED_CANDIDATES:
    assert f"- {candidate_id}:" in body


def test_completed_followup_conformance_records_spec_and_design_gaps():
  _, body = _front_matter_and_body(RECORD_PATH)

  assert "## Conformance Gaps" in body
  assert "specification gap" in body
  assert "design gap" in body
  assert "実アプリ pilot" in body


def test_formal_completed_followup_summary_records_scope_and_next_issue():
  text = SUMMARY_PATH.read_text(encoding="utf-8")

  assert "将来計画候補から昇格した正式な completed follow-up 成果物" in text
  assert "conformance result: `gap_found`" in text
  assert "実アプリ pilot はこのサマリの対象外" in text
  for candidate_id in EXPECTED_CANDIDATES:
    assert f"| {candidate_id} |" in text
