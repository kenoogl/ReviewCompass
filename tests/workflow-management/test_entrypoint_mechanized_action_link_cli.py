"""Entrypoint mechanized action link red tests for ECA-5.

These tests define the read-only action-link contract before implementation.
Coverage audit must report command, preflight, output schema, and evidence
coverage per entrypoint without executing commands.
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


class EntrypointMechanizedActionLinkCliTests(unittest.TestCase):
  def _audit(self):
    result = run(["entrypoint-coverage-audit", "--json"])
    self.assertEqual(result.returncode, 0, result.stderr)
    data = json.loads(result.stdout)
    self.assertIn(data["verdict"], ["OK", "WARN", "DEVIATION"])
    self.assertEqual(data["operation_mode"], "read_only")
    self.assertIsInstance(data["mechanized_action_links"], list)
    self.assertTrue(data["mechanized_action_links"])
    return data

  def test_coverage_audit_exposes_mechanized_action_links(self):
    data = self._audit()

    summary = data["coverage_summary"]
    self.assertIn("mechanized_action_link_count", summary)
    self.assertEqual(
      summary["mechanized_action_link_count"],
      len(data["mechanized_action_links"]),
    )

  def test_mechanized_action_links_expose_execution_contract_fields(self):
    data = self._audit()

    required_fields = [
      "entrypoint_id",
      "required_action",
      "mechanized_command",
      "preflight_status",
      "output_schema_status",
      "evidence_contract_status",
    ]
    for link in data["mechanized_action_links"]:
      for field in required_fields:
        self.assertIn(field, link, link)
      for status_field in [
        "preflight_status",
        "output_schema_status",
        "evidence_contract_status",
      ]:
        self.assertIn(
          link[status_field],
          ["covered", "missing", "not_applicable", "unknown"],
        )

  def test_missing_action_link_fields_become_warning_candidates(self):
    data = self._audit()

    missing_links = [
      link
      for link in data["mechanized_action_links"]
      if "missing" in {
        link.get("mechanized_command_status"),
        link.get("preflight_status"),
        link.get("output_schema_status"),
        link.get("evidence_contract_status"),
      }
    ]
    self.assertTrue(missing_links)

    action_findings = [
      finding
      for finding in data["findings"]
      if finding.get("field") in {
        "mechanized_command_status",
        "preflight_status",
        "output_schema_status",
        "evidence_contract_status",
      }
    ]
    self.assertTrue(action_findings)
    for finding in action_findings:
      self.assertEqual(finding["severity"], "WARN")
      self.assertIn("entrypoint_id", finding)


if __name__ == "__main__":
  unittest.main()
