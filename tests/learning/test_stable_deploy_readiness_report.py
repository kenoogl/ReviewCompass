"""Stable deploy readiness final gate report の契約テスト。"""
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
REPORT_PATH = (
  REPO_ROOT
  / "learning"
  / "workflow"
  / "deployment-readiness"
  / "2026-06-09-stable-deploy-readiness.json"
)

REQUIRED_GATE_IDS = [
  "D-021",
  "D-020",
  "D-023",
]


def _load_report():
  return json.loads(REPORT_PATH.read_text(encoding="utf-8"))


def test_stable_deploy_readiness_report_declares_candidate_verdict():
  report = _load_report()

  assert report["record_type"] == "stable_deploy_readiness"
  assert report["verdict"] == "stable_deploy_candidate"
  assert report["blocking_gap_refs"] == []


def test_stable_deploy_readiness_report_has_required_gates():
  report = _load_report()

  gate_ids = [gate["gate_id"] for gate in report["gates"]]
  assert gate_ids == REQUIRED_GATE_IDS

  for gate in report["gates"]:
    assert gate["status"] in {"ready_with_gaps", "passed"}
    assert gate["evidence_refs"]
    assert all(not ref.startswith("/") for ref in gate["evidence_refs"])


def test_stable_deploy_readiness_report_keeps_followups_non_blocking():
  report = _load_report()

  assert report["non_blocking_followups"]
  assert all(item["blocks_stable_deploy"] is False for item in report["non_blocking_followups"])
