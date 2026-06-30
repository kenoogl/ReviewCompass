"""ORP-3 red tests for the serial-only operation runner plan CLI."""

import json
import subprocess
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "tools" / "check-workflow-action.py"


def run(args):
  return subprocess.run(
    [sys.executable, str(SCRIPT)] + list(args),
    cwd=str(REPO_ROOT),
    capture_output=True,
    text=True,
    timeout=30,
  )


class OperationSerialRunnerPlanCliTests(unittest.TestCase):
  def test_commit_operation_plan_exposes_ordered_serial_steps(self):
    result = run(["operation-serial-runner-plan", "--operation-id", "commit", "--json"])

    self.assertEqual(result.returncode, 0, result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["verdict"], "OK")
    self.assertEqual(data["operation_mode"], "read_only")
    self.assertEqual(data["operation_id"], "commit")
    self.assertEqual(data["sequence_mode"], "serial_only")
    self.assertEqual(data["next_step"], "stop_for_user_approval")

    step_ids = [step["id"] for step in data["steps"]]
    self.assertEqual(
      [
        "commit-preflight",
        "approval-input",
        "guarded-commit",
        "postcondition-check",
      ],
      step_ids,
    )
    for step in data["steps"]:
      self.assertEqual(step["execution_mode"], "not_executed")

  def test_non_serial_operation_is_rejected_by_serial_runner_plan(self):
    result = run([
      "operation-serial-runner-plan",
      "--operation-id",
      "session-record",
      "--json",
    ])

    self.assertEqual(result.returncode, 2, result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["verdict"], "DEVIATION")
    self.assertEqual(data["operation_mode"], "read_only")
    self.assertEqual(data["operation_id"], "session-record")
    self.assertIn("serial_only_required", {finding["kind"] for finding in data["findings"]})
    self.assertTrue(
      any("parallel" in reason or "serial_only" in reason for reason in data["reasons"]),
      data["reasons"],
    )

  def test_commit_plan_reports_approval_freshness_and_staged_digest_checkpoints(self):
    result = run(["operation-serial-runner-plan", "--operation-id", "commit", "--json"])

    self.assertEqual(result.returncode, 0, result.stderr)
    data = json.loads(result.stdout)
    checkpoints = {checkpoint["id"]: checkpoint for checkpoint in data["checkpoints"]}

    self.assertEqual(
      {
        "nonce",
        "ttl",
        "consumed",
        "target_digest",
        "staged_file_set_digest",
        "staged_content_approval_digest",
      },
      set(checkpoints),
    )
    for checkpoint in checkpoints.values():
      self.assertEqual(checkpoint["execution_mode"], "not_executed")


if __name__ == "__main__":
  unittest.main()
