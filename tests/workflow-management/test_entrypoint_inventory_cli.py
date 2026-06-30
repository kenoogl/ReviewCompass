"""Entrypoint inventory red tests for ECA-1.

These tests intentionally describe the read-only inventory contract before the
CLI exists. Implementation must make the inventory machine-readable without
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


class EntrypointInventoryCliTests(unittest.TestCase):
  def _inventory(self):
    result = run(["entrypoint-inventory", "--json"])
    self.assertEqual(result.returncode, 0, result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["verdict"], "OK")
    self.assertEqual(data["operation_mode"], "read_only")
    self.assertIsInstance(data["entrypoints"], list)
    self.assertTrue(data["entrypoints"])
    return data

  def test_inventory_lists_current_next_action_kinds_with_prompt_coverage(self):
    data = self._inventory()

    next_action_entries = [
      entry
      for entry in data["entrypoints"]
      if entry.get("kind") == "next_action_kind"
    ]
    ids = {entry.get("entrypoint_id") for entry in next_action_entries}

    self.assertIn("next_action_kind:completed", ids)
    for entry in next_action_entries:
      self.assertIn("decision_point_ref", entry)
      self.assertIn("expected_effective_prompt", entry)

  def test_inventory_lists_major_cli_subcommands_without_llm_memory(self):
    data = self._inventory()

    cli_commands = {
      entry.get("mechanized_command")
      for entry in data["entrypoints"]
      if entry.get("kind") == "cli_subcommand"
    }

    self.assertIn("tools/check-workflow-action.py next --json", cli_commands)
    self.assertIn("tools/check-workflow-action.py commit-preflight --json", cli_commands)
    self.assertIn("tools/check-workflow-action.py work-backlog start-checklist", cli_commands)
    self.assertIn("tools/check-workflow-action.py work-checklist show", cli_commands)

  def test_inventory_records_connection_fields_for_each_entrypoint(self):
    data = self._inventory()

    required_fields = [
      "entrypoint_id",
      "kind",
      "trigger",
      "required_action",
      "expected_effective_prompt",
      "mechanized_command",
      "evidence_path",
    ]
    for entry in data["entrypoints"]:
      for field in required_fields:
        self.assertIn(field, entry, entry)


if __name__ == "__main__":
  unittest.main()
