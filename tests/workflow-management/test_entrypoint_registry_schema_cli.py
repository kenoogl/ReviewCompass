"""Entrypoint registry schema red tests for ECA-2.

These tests define the read-only schema contract before the CLI exists.
Implementation must expose the registry schema and responsibility boundary
without changing workflow state.
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


class EntrypointRegistrySchemaCliTests(unittest.TestCase):
  def _schema(self):
    result = run(["entrypoint-registry-schema", "--json"])
    self.assertEqual(result.returncode, 0, result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["verdict"], "OK")
    self.assertEqual(data["operation_mode"], "read_only")
    self.assertEqual(data["schema_version"], "entrypoint-registry-schema-v1")
    self.assertIsInstance(data["registry_contract"], dict)
    return data

  def test_registry_schema_is_exposed_as_machine_readable_json(self):
    data = self._schema()

    contract = data["registry_contract"]
    self.assertIn("required_fields", contract)
    self.assertIn("responsibility_boundary", contract)
    self.assertIn("coverage_audit_contract", contract)

  def test_registry_schema_declares_required_entrypoint_fields(self):
    data = self._schema()

    required_fields = set(data["registry_contract"]["required_fields"])

    self.assertEqual(
      {
        "entrypoint_id",
        "kind",
        "trigger",
        "decision_point_ref",
        "effective_prompt_ref",
        "required_action",
        "mechanized_command",
        "evidence_contract",
      },
      required_fields,
    )

  def test_registry_schema_declares_discipline_map_boundary(self):
    data = self._schema()

    boundary = data["registry_contract"]["responsibility_boundary"]
    self.assertEqual(
      boundary["discipline_map"]["source_ref"],
      ".reviewcompass/guidance/WORKFLOW_DISCIPLINE_MAP.yaml",
    )
    self.assertEqual(
      boundary["discipline_map"]["owns"],
      ["decision_point_ref", "effective_prompt_ref"],
    )
    self.assertEqual(
      boundary["entrypoint_registry"]["owns"],
      [
        "entrypoint_id",
        "kind",
        "trigger",
        "required_action",
        "mechanized_command",
        "evidence_contract",
      ],
    )


if __name__ == "__main__":
  unittest.main()
