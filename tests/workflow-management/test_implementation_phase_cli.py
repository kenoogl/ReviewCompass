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


if __name__ == "__main__":
  unittest.main()
