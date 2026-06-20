"""T-019 operation-list read-only red tests."""

import json
import subprocess
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "tools" / "check-workflow-action.py"


class OperationListReadOnlyTests(unittest.TestCase):
  def _next_json(self):
    result = subprocess.run(
      [sys.executable, str(SCRIPT), "next", "--json"],
      cwd=str(REPO_ROOT),
      capture_output=True,
      text=True,
      timeout=30,
    )
    self.assertEqual(result.returncode, 0, result.stderr)
    return json.loads(result.stdout)

  def test_phase2_operation_list_returns_read_only_registry_fields_without_changing_next_json(self):
    before = self._next_json()
    result = subprocess.run(
      [sys.executable, str(SCRIPT), "operation-list", "--json"],
      cwd=str(REPO_ROOT),
      capture_output=True,
      text=True,
      timeout=30,
    )
    after = self._next_json()

    self.assertEqual(result.returncode, 0, result.stderr)
    self.assertEqual(before, after)
    data = json.loads(result.stdout)
    self.assertEqual(data["verdict"], "OK")
    self.assertEqual(data["operation_mode"], "read_only")
    self.assertTrue(data["operations"])
    for operation in data["operations"]:
      for field in [
        "operation_id",
        "canonical_commands",
        "effect_kind",
        "approval_required",
        "sequence",
        "pending_conflicts",
      ]:
        self.assertIn(field, operation, operation)


if __name__ == "__main__":
  unittest.main()
