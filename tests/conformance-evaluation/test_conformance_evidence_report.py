from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REPORT_PATH = (
  ROOT
  / "docs"
  / "experiments"
  / "2026-06-09-conformance-evaluation-evidence-report.md"
)


def test_conformance_evaluation_evidence_report_records_paper_evidence():
  text = REPORT_PATH.read_text(encoding="utf-8")

  assert "# Conformance Evaluation 論文用エビデンスレポート" in text
  assert "## 論文用エビデンスの範囲" in text
  assert "## 証跡一覧" in text
  assert "## 有用性" in text
  assert "## 限界と課題" in text
  assert "## 論文での使い方" in text


def test_conformance_evaluation_evidence_report_links_key_artifacts():
  text = REPORT_PATH.read_text(encoding="utf-8")

  for path in [
    ".reviewcompass/specs/conformance-evaluation/conformance/2026-06-09-completed-followup-conformance.md",
    ".reviewcompass/specs/conformance-evaluation/conformance/2026-06-09-completed-followup-contract-confirmation.md",
    ".reviewcompass/specs/conformance-evaluation/requirements.md",
    ".reviewcompass/specs/conformance-evaluation/design.md",
    "docs/notes/2026-06-09-formal-completed-followup-summary.md",
  ]:
    assert path in text


def test_conformance_evaluation_evidence_report_keeps_claims_bounded():
  text = REPORT_PATH.read_text(encoding="utf-8")

  assert "主張しない" in text
  assert "単一プロジェクトの dogfooding evidence" in text
  assert "implementation-first" in text
  assert "requirements gap: resolved" in text
  assert "design gap: resolved" in text
