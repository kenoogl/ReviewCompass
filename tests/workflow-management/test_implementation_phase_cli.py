"""T-019 implementation phase CLI red tests."""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "tools" / "check-workflow-action.py"


class ImplementationPhaseCliTests(unittest.TestCase):
  def test_implementation_phase_check_cli_returns_json(self):
    result = subprocess.run(
      [
        sys.executable,
        str(SCRIPT),
        "implementation-phase-check",
        "--feature",
        "workflow-management",
        "--json",
      ],
      cwd=str(REPO_ROOT),
      capture_output=True,
      text=True,
      timeout=30,
    )

    self.assertEqual(result.returncode, 0, result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["verdict"], "OK")
    self.assertEqual(data["current_state"]["feature"], "workflow-management")
    self.assertIn("phase", data["current_state"])

  def test_proxy_triage_decision_check_cli_returns_json(self):
    with tempfile.TemporaryDirectory() as tmp:
      run = Path(tmp) / "review-run"
      run.mkdir()
      (run / "proxy-triage-decision.yaml").write_text(
        yaml.safe_dump(
          {
            "schema_version": "proxy-triage-decision-v1",
            "decision_id": "proxy-decision-001",
            "target_findings": ["finding-001"],
          },
          sort_keys=False,
        ),
        encoding="utf-8",
      )

      result = subprocess.run(
        [
          sys.executable,
          str(SCRIPT),
          "proxy-triage-decision-check",
          "--run",
          str(run),
          "--json",
        ],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        timeout=30,
      )

    self.assertEqual(result.returncode, 2, result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["verdict"], "DEVIATION")
    self.assertIn("proxy-triage-decision", data["action"]["subcommand"])

  def test_proxy_triage_decision_check_cli_accepts_complete_record(self):
    with tempfile.TemporaryDirectory() as tmp:
      run = Path(tmp) / "review-run"
      run.mkdir()
      (run / "proxy-triage-decision.yaml").write_text(
        yaml.safe_dump(
          {
            "schema_version": "proxy-triage-decision-v1",
            "decision_id": "proxy-decision-001",
            "target_findings": ["finding-001"],
            "target_clusters": ["cluster-001"],
            "source_triage_path": "review-run/triage.yaml",
            "raw_response_path": "review-run/raw/model.txt",
            "parsed_finding_paths": ["review-run/parsed/model.yaml"],
            "decision_prompt_path": "review-run/prompts/proxy.prompt.md",
            "proxy_raw_response_path": "review-run/raw/proxy.txt",
            "candidate_decisions": [
              {"id": "fix", "final_label": "must-fix", "finding_ids": ["finding-001"]}
            ],
            "selected_decision": {
              "id": "fix",
              "final_label": "must-fix",
              "finding_ids": ["finding-001"],
            },
            "reasoning_summary": "Complete evidence and no human-required predicate applies.",
            "final_application_target": {
              "operation_id": "proxy_triage_apply_batch",
              "triage_path": "review-run/triage.yaml",
              "finding_ids": ["finding-001"],
            },
            "approval_scope": {
              "review_triage_decide": ["finding-001"],
              "apply_fixes": ["finding-001"],
              "operation_scope": "proxy_triage_apply_batch",
            },
            "evidence_completeness": {
              "raw_response": True,
              "parsed_findings": True,
              "source_triage": True,
              "approval_gate": True,
              "operation_contract": True,
              "review_wave_impact": True,
            },
            "finding_operation_map": [
              {"finding_id": "finding-001", "operation_id": "proxy_triage_apply_batch"}
            ],
            "approval_gate_record_refs": ["review-run/approval.yaml"],
            "operation_contract_refs": ["stages/operation-contracts.yaml#proxy_triage_apply_batch"],
            "review_wave_impact_evidence": {
              "status": "no_downstream_impact",
              "evidence_refs": ["review-run/triage.yaml"],
            },
            "evidence_conflicts": [],
            "operation_contract": {
              "operation_id": "proxy_triage_apply_batch",
              "approval_required": False,
            },
            "approval_gate": {"decision_scope": "proxy_allowed", "decision": "approved"},
            "review_wave_impact": {"unresolved": False},
          },
          sort_keys=False,
        ),
        encoding="utf-8",
      )

      result = subprocess.run(
        [
          sys.executable,
          str(SCRIPT),
          "proxy-triage-decision-check",
          "--run",
          str(run),
          "--json",
        ],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        timeout=30,
      )

    self.assertEqual(result.returncode, 0, result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["verdict"], "OK")


if __name__ == "__main__":
  unittest.main()
