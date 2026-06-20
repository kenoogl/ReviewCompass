"""T-018 language task I/O schema red tests."""

import json
import unittest
from pathlib import Path

import jsonschema


REPO_ROOT = Path(__file__).resolve().parents[2]
LANGUAGE_TASK_SCHEMA = (
  REPO_ROOT / ".reviewcompass" / "schema" / "language_task_io.schema.json"
)


def load_json(path):
  with path.open(encoding="utf-8") as f:
    return json.load(f)


def valid_language_task(**overrides):
  task = {
    "document_kind": "review",
    "input": {
      "required_files": ["docs/operations/WORKFLOW_NAVIGATION.md"],
      "state_refs": [".reviewcompass/specs/workflow-management/spec.json"],
      "source_refs": ["docs/operations/WORKFLOW_DISCIPLINE_MAP.yaml"],
    },
    "output_format": {
      "kind": "markdown",
      "required_sections": ["Findings", "Decision"],
      "schema_ref": None,
    },
    "constraints": [
      "Do not execute git operations.",
      "Do not mutate workflow state.",
    ],
  }
  task.update(overrides)
  return task


class LanguageTaskIoSchemaTests(unittest.TestCase):
  def test_language_task_io_schema_exists_and_requires_design_vocabulary(self):
    self.assertTrue(LANGUAGE_TASK_SCHEMA.exists(), f"missing schema: {LANGUAGE_TASK_SCHEMA}")
    schema = load_json(LANGUAGE_TASK_SCHEMA)
    self.assertEqual(schema.get("$schema"), "https://json-schema.org/draft/2020-12/schema")
    self.assertEqual(schema.get("type"), "object")
    for field in ["document_kind", "input", "output_format", "constraints"]:
      self.assertIn(field, schema.get("required", []), field)

  def test_language_task_io_rejects_unknown_or_machine_action_fields(self):
    schema = load_json(LANGUAGE_TASK_SCHEMA)
    validator = jsonschema.Draft202012Validator(schema)

    valid_errors = list(validator.iter_errors(valid_language_task()))
    self.assertEqual(valid_errors, [])

    unknown_errors = list(validator.iter_errors(valid_language_task(allowed_actions=["commit"])))
    self.assertNotEqual(unknown_errors, [])

    machine_task = valid_language_task()
    machine_task["input"]["operation_execution"] = "git commit"
    machine_errors = list(validator.iter_errors(machine_task))
    self.assertNotEqual(machine_errors, [])


if __name__ == "__main__":
  unittest.main()
