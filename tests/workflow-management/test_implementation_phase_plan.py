"""T-019 implementation phase plan red tests."""

import importlib
import json
import sys
import unittest
from pathlib import Path

import jsonschema
import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "tools"))
PLAN_PATH = REPO_ROOT / "stages" / "workflow-management-implementation-phases.yaml"
SCHEMA_PATH = REPO_ROOT / ".reviewcompass" / "schema" / "implementation_phase.schema.json"


def load_yaml(path):
  with path.open(encoding="utf-8") as f:
    return yaml.safe_load(f)


def load_json(path):
  with path.open(encoding="utf-8") as f:
    return json.load(f)


class ImplementationPhasePlanTests(unittest.TestCase):
  def test_implementation_phase_plan_covers_phase_0_to_6(self):
    self.assertTrue(SCHEMA_PATH.exists(), f"missing schema: {SCHEMA_PATH}")
    self.assertTrue(PLAN_PATH.exists(), f"missing plan: {PLAN_PATH}")
    schema = load_json(SCHEMA_PATH)
    plan = load_yaml(PLAN_PATH)

    errors = list(jsonschema.Draft202012Validator(schema).iter_errors(plan))
    self.assertEqual(errors, [])

    phases = plan["phases"]
    self.assertEqual([phase["phase"] for phase in phases], list(range(7)))
    for phase in phases:
      for field in [
        "name",
        "entry_criteria",
        "exit_criteria",
        "allowed_operations",
        "forbidden_operations",
        "required_tests",
        "commit_boundary",
      ]:
        self.assertIn(field, phase, f"phase {phase.get('phase')} missing {field}")
      self.assertTrue(phase["entry_criteria"], phase)
      self.assertTrue(phase["exit_criteria"], phase)

  def test_phase_checker_uses_entry_exit_and_forbidden_operations(self):
    module = importlib.import_module("check_workflow_action.implementation_phases")
    plan = {
      "schema_version": "workflow-management-implementation-phases-v1",
      "feature": "workflow-management",
      "phases": [
        {
          "phase": 0,
          "name": "phase-zero",
          "entry_criteria": [{"id": "entry", "satisfied": False}],
          "exit_criteria": [{"id": "exit", "satisfied": False}],
          "allowed_operations": ["operation-list"],
          "forbidden_operations": ["spec-set"],
          "required_tests": ["pytest tests/workflow-management/test_x.py"],
          "commit_boundary": {"required": True},
        }
      ],
    }

    result = module.check_phase_plan(
      plan,
      feature="workflow-management",
      current_phase=0,
      executed_operations=["spec-set"],
    )

    self.assertEqual(result["verdict"], "DEVIATION")
    joined = "\n".join(result["reasons"])
    self.assertIn("entry", joined)
    self.assertIn("exit", joined)
    self.assertIn("forbidden", joined.lower())

  def test_phase_checker_rejects_missing_required_snapshot_evidence_and_boundary_detail(self):
    module = importlib.import_module("check_workflow_action.implementation_phases")
    plan = {
      "schema_version": "workflow-management-implementation-phases-v1",
      "feature": "workflow-management",
      "phases": [
        {
          "phase": 0,
          "name": "phase-zero",
          "entry_criteria": [{"id": "entry", "satisfied": True}],
          "exit_criteria": [{"id": "exit", "satisfied": True}],
          "allowed_operations": ["operation-list"],
          "forbidden_operations": [],
          "required_tests": ["pytest tests/workflow-management/test_x.py"],
          "required_snapshot_evidence": [
            {"id": "next-json-snapshot", "path": "", "fresh": False}
          ],
          "commit_boundary": {"required": True},
        }
      ],
    }

    result = module.check_phase_plan(
      plan,
      feature="workflow-management",
      current_phase=0,
    )

    self.assertEqual(result["verdict"], "DEVIATION")
    joined = "\n".join(result["reasons"])
    self.assertIn("snapshot", joined)
    self.assertIn("commit", joined)


if __name__ == "__main__":
  unittest.main()
