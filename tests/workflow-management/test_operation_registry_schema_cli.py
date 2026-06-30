"""Operation registry schema red tests for ORP-1.

These tests define the read-only operation registry contract before the CLI
exists. Implementation must expose schema and inventory data without running
any side-effecting operation.
"""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml


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


class OperationRegistrySchemaCliTests(unittest.TestCase):
  def _schema(self):
    result = run(["operation-registry-schema", "--json"])
    self.assertEqual(result.returncode, 0, result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["verdict"], "OK")
    self.assertEqual(data["operation_mode"], "read_only")
    self.assertEqual(data["schema_version"], "operation-registry-schema-v1")
    self.assertIsInstance(data["registry_contract"], dict)
    return data

  def test_operation_registry_schema_is_exposed_as_json(self):
    data = self._schema()

    contract = data["registry_contract"]
    self.assertIn("required_fields", contract)
    self.assertIn("inventory_contract", contract)
    self.assertIn("validation_contract", contract)

  def test_operation_registry_schema_declares_required_contract_fields(self):
    data = self._schema()

    required_fields = set(data["registry_contract"]["required_fields"])

    self.assertEqual(
      {
        "operation_id",
        "kind",
        "canonical_commands",
        "required_args",
        "outputs",
        "serial_only",
        "conflicting_states",
      },
      required_fields,
    )

  def test_operation_registry_inventory_includes_core_operations(self):
    result = run(["operation-registry-inventory", "--json"])
    self.assertEqual(result.returncode, 0, result.stderr)
    data = json.loads(result.stdout)

    self.assertEqual(data["verdict"], "OK")
    self.assertEqual(data["operation_mode"], "read_only")
    operations = {item["operation_id"]: item for item in data["operations"]}
    for operation_id in [
      "commit",
      "push",
      "post-write-manifest",
      "review-run",
      "reopen",
      "session-record",
    ]:
      self.assertIn(operation_id, operations)
      self.assertTrue(operations[operation_id]["canonical_commands"])

  def test_missing_canonical_command_path_is_reported(self):
    with tempfile.TemporaryDirectory() as tmp:
      registry_path = Path(tmp) / "operation-registry.yaml"
      registry_path.write_text(
        yaml.safe_dump(
          {
            "schema_version": "operation-registry-v1",
            "operations": [
              {
                "operation_id": "broken-operation",
                "kind": "test",
                "canonical_commands": [
                  {
                    "entrypoint": "tools/does-not-exist.py",
                    "argv": ["--json"],
                  },
                ],
                "required_args": [],
                "outputs": [],
                "serial_only": False,
                "conflicting_states": [],
              },
            ],
          },
          allow_unicode=True,
          sort_keys=False,
        ),
        encoding="utf-8",
      )

      result = run([
        "operation-registry-validate",
        "--registry-file",
        str(registry_path),
        "--json",
      ])

    self.assertEqual(result.returncode, 2, result.stderr)
    self.assertTrue(result.stdout, result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["verdict"], "DEVIATION")
    self.assertEqual(data["operation_mode"], "read_only")
    self.assertIn("missing_command_path", {finding["kind"] for finding in data["findings"]})


if __name__ == "__main__":
  unittest.main()
