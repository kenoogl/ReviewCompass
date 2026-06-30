"""Entrypoint freshness audit bridge red tests for ECA-4.

These tests define the read-only bridge contract before implementation.
Coverage audit must expose entrypoint-scoped freshness targets without
changing workflow state.
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


class EntrypointFreshnessAuditBridgeCliTests(unittest.TestCase):
  def _audit(self):
    result = run(["entrypoint-coverage-audit", "--json"])
    self.assertEqual(result.returncode, 0, result.stderr)
    data = json.loads(result.stdout)
    self.assertIn(data["verdict"], ["OK", "WARN", "DEVIATION"])
    self.assertEqual(data["operation_mode"], "read_only")
    self.assertIsInstance(data["freshness_audit_targets"], list)
    self.assertTrue(data["freshness_audit_targets"])
    return data

  def test_coverage_audit_exposes_freshness_audit_targets(self):
    data = self._audit()

    summary = data["coverage_summary"]
    self.assertIn("freshness_target_count", summary)
    self.assertEqual(
      summary["freshness_target_count"],
      len(data["freshness_audit_targets"]),
    )

  def test_freshness_targets_are_entrypoint_scoped(self):
    data = self._audit()

    required_fields = [
      "entrypoint_id",
      "effective_prompt_ref",
      "effective_prompt_path",
      "freshness_status",
    ]
    for target in data["freshness_audit_targets"]:
      for field in required_fields:
        self.assertIn(field, target, target)
      self.assertIn(
        target["freshness_status"],
        ["fresh", "stale", "missing", "not_applicable", "unknown"],
      )

  def test_missing_effective_prompt_becomes_freshness_warning_candidate(self):
    data = self._audit()

    missing_targets = [
      target
      for target in data["freshness_audit_targets"]
      if target.get("freshness_status") == "missing"
    ]
    self.assertTrue(missing_targets)

    freshness_findings = [
      finding
      for finding in data["findings"]
      if finding.get("field") == "freshness_status"
    ]
    self.assertTrue(freshness_findings)
    for finding in freshness_findings:
      self.assertEqual(finding["severity"], "WARN")
      self.assertIn("entrypoint_id", finding)


if __name__ == "__main__":
  unittest.main()
