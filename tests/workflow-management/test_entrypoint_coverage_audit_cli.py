"""Entrypoint coverage audit red tests for ECA-3.

These tests define the read-only audit contract before the CLI exists.
Implementation must report entrypoint coverage without changing workflow state.
"""

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


class EntrypointCoverageAuditCliTests(unittest.TestCase):
  def _audit(self):
    result = run(["entrypoint-coverage-audit", "--json"])
    self.assertEqual(result.returncode, 0, result.stderr)
    data = json.loads(result.stdout)
    self.assertIn(data["verdict"], ["OK", "WARN", "DEVIATION"])
    self.assertEqual(data["operation_mode"], "read_only")
    self.assertIsInstance(data["coverage_summary"], dict)
    self.assertIsInstance(data["entrypoint_coverage"], list)
    self.assertIsInstance(data["findings"], list)
    return data

  def test_coverage_audit_is_exposed_as_machine_readable_json(self):
    data = self._audit()

    summary = data["coverage_summary"]
    self.assertIn("total_entrypoints", summary)
    self.assertIn("covered_entrypoints", summary)
    self.assertIn("warning_candidate_count", summary)

  def test_coverage_entries_are_entrypoint_scoped(self):
    data = self._audit()

    self.assertTrue(data["entrypoint_coverage"])
    required_fields = [
      "entrypoint_id",
      "registry_status",
      "discipline_map_status",
      "effective_prompt_status",
      "mechanized_action_status",
    ]
    for entry in data["entrypoint_coverage"]:
      for field in required_fields:
        self.assertIn(field, entry, entry)

  def test_unregistered_entrypoints_are_warn_candidates(self):
    data = self._audit()

    policy = data["finding_policy"]
    self.assertEqual(policy["unregistered_entrypoint_severity"], "WARN")
    for finding in data["findings"]:
      self.assertIn("severity", finding)
      self.assertIn(finding["severity"], ["WARN", "DEVIATION"])
      self.assertIn("entrypoint_id", finding)


if __name__ == "__main__":
  unittest.main()
