"""T-016 operation contract schema tests.

These tests are intentionally written before the implementation. They pin the
Requirement 13 vocabulary and contract shape that implementation must satisfy.
"""

import json
import unittest
from pathlib import Path

import jsonschema


REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_DIR = REPO_ROOT / ".reviewcompass" / "schema"
EFFECT_KIND_SCHEMA = SCHEMA_DIR / "effect_kind.schema.json"
PHASE_BOUNDARY_SCHEMA = SCHEMA_DIR / "phase_boundary.schema.json"
OPERATION_CONTRACT_SCHEMA = SCHEMA_DIR / "operation_contract.schema.json"

EXPECTED_EFFECT_KINDS = [
  "read",
  "write",
  "state_mutation",
  "external_call",
]

EXPECTED_PHASE_BOUNDARIES = [
  "none",
  "within_phase",
  "phase_transition",
  "reopen_boundary",
  "commit_boundary",
  "push_boundary",
  "external_boundary",
]

REQUIRED_CONTRACT_FIELDS = [
  "schema_version",
  "operation_id",
  "required_action",
  "effect_kind",
  "approval_required",
  "approval_contract_refs",
  "phase_boundary",
  "sequence",
  "actor",
  "branching",
  "max_effect_kind",
  "preconditions",
  "postconditions",
  "side_effects",
  "commit_boundary",
  "workflow_state_effect",
  "canonical_invocation",
]


def load_json(path):
  with path.open(encoding="utf-8") as f:
    return json.load(f)


class OperationContractSchemaTests(unittest.TestCase):
  def test_effect_kind_schema_defines_exact_four_values(self):
    self.assertTrue(EFFECT_KIND_SCHEMA.exists(), f"missing schema: {EFFECT_KIND_SCHEMA}")
    schema = load_json(EFFECT_KIND_SCHEMA)
    self.assertEqual(schema.get("type"), "string")
    self.assertEqual(schema.get("enum"), EXPECTED_EFFECT_KINDS)

    validator = jsonschema.Draft202012Validator(schema)
    for value in EXPECTED_EFFECT_KINDS:
      self.assertEqual(list(validator.iter_errors(value)), [])
    self.assertNotEqual(list(validator.iter_errors("")), [])
    self.assertNotEqual(list(validator.iter_errors("network")), [])

  def test_phase_boundary_schema_defines_required_boundaries(self):
    self.assertTrue(PHASE_BOUNDARY_SCHEMA.exists(), f"missing schema: {PHASE_BOUNDARY_SCHEMA}")
    schema = load_json(PHASE_BOUNDARY_SCHEMA)
    self.assertEqual(schema.get("type"), "string")
    self.assertEqual(schema.get("enum"), EXPECTED_PHASE_BOUNDARIES)

    validator = jsonschema.Draft202012Validator(schema)
    for value in EXPECTED_PHASE_BOUNDARIES:
      self.assertEqual(list(validator.iter_errors(value)), [])
    self.assertNotEqual(list(validator.iter_errors("")), [])
    self.assertNotEqual(list(validator.iter_errors("approval_boundary")), [])

  def test_operation_contract_schema_requires_contract_shape(self):
    self.assertTrue(OPERATION_CONTRACT_SCHEMA.exists(), f"missing schema: {OPERATION_CONTRACT_SCHEMA}")
    schema = load_json(OPERATION_CONTRACT_SCHEMA)
    self.assertEqual(schema.get("$schema"), "https://json-schema.org/draft/2020-12/schema")
    self.assertEqual(schema.get("type"), "object")

    required = schema.get("required", [])
    for field in REQUIRED_CONTRACT_FIELDS:
      self.assertIn(field, required, f"operation contract field is not required: {field}")

  def test_operation_contract_schema_requires_branch_internal_step_shape(self):
    self.assertTrue(OPERATION_CONTRACT_SCHEMA.exists(), f"missing schema: {OPERATION_CONTRACT_SCHEMA}")
    schema = load_json(OPERATION_CONTRACT_SCHEMA)
    branching = schema["properties"]["branching"]
    branches = branching["properties"]["branches"]["items"]
    branch_required = branches.get("required", [])
    for field in [
      "branch_id",
      "condition",
      "internal_steps",
      "max_effect_kind",
      "approval_aggregation",
      "human_only_override_applies",
      "precondition_ids",
      "postcondition_ids",
    ]:
      self.assertIn(field, branch_required, f"branch field is not required: {field}")

    step = branches["properties"]["internal_steps"]["items"]
    step_required = step.get("required", [])
    for field in [
      "step_id",
      "effect_kind",
      "approval_required",
      "approval_contract_ref",
      "phase_boundary",
      "source_ref",
    ]:
      self.assertIn(field, step_required, f"branch internal step field is not required: {field}")


if __name__ == "__main__":
  unittest.main()
