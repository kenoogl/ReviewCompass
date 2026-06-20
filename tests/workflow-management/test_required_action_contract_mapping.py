"""T-016 required_action to operation contract mapping tests."""

import json
import unittest
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
REQUIRED_ACTION_SCHEMA = REPO_ROOT / ".reviewcompass" / "schema" / "required_action.schema.json"
OPERATION_CONTRACTS = REPO_ROOT / "stages" / "operation-contracts.yaml"
OPERATION_REGISTRY = REPO_ROOT / "stages" / "operation-registry.yaml"

APPROVAL_REQUIRED_SIMPLE_ACTIONS = {
  "commit_stop_point",
  "apply_approved_reopen_plan",
  "run_reopen_start",
  "advance_reopen_after_commit_stop_point",
  "advance_reopen_after_approval_stop_point",
  "finalize_reopen",
  "repair_workflow_state",
}

BRANCHY_ACTIONS = {
  "run_maintenance",
  "run_reopen_pending_gate",
  "run_workflow_stage",
}

REGISTRY_FORBIDDEN_CONTRACT_FIELDS = {
  "effect_kind",
  "approval_required",
  "approval_contract_refs",
  "phase_boundary",
  "preconditions",
  "postconditions",
  "side_effects",
  "approval_aggregation",
  "branching",
  "max_effect_kind",
  "workflow_state_effect",
}


def load_json(path):
  with path.open(encoding="utf-8") as f:
    return json.load(f)


def load_yaml(path):
  with path.open(encoding="utf-8") as f:
    data = yaml.safe_load(f)
  return data or {}


def iter_contracts(data):
  contracts = data.get("operations") or data.get("contracts") or []
  if isinstance(contracts, dict):
    return list(contracts.values())
  return list(contracts)


class RequiredActionContractMappingTests(unittest.TestCase):
  def test_required_action_contract_mapping_covers_required_action_enum(self):
    self.assertTrue(OPERATION_CONTRACTS.exists(), f"missing contracts: {OPERATION_CONTRACTS}")
    required_actions = set(load_json(REQUIRED_ACTION_SCHEMA)["enum"])
    contracts = iter_contracts(load_yaml(OPERATION_CONTRACTS))
    mapped = {contract.get("required_action") for contract in contracts if isinstance(contract, dict)}

    self.assertEqual(required_actions - mapped, set())
    self.assertEqual(mapped - required_actions, set())

  def test_commit_boundary_blocks_bypass_for_irreversible_actions(self):
    self.assertTrue(OPERATION_CONTRACTS.exists(), f"missing contracts: {OPERATION_CONTRACTS}")
    contracts = iter_contracts(load_yaml(OPERATION_CONTRACTS))
    by_action = {contract.get("required_action"): contract for contract in contracts if isinstance(contract, dict)}

    for action in sorted(APPROVAL_REQUIRED_SIMPLE_ACTIONS):
      contract = by_action[action]
      self.assertIs(contract.get("approval_required"), True, action)
      self.assertIs(contract.get("commit_boundary", {}).get("required"), True, action)
      self.assertIn(
        contract.get("phase_boundary"),
        {"commit_boundary", "reopen_boundary", "within_phase"},
        action,
      )

  def test_record_human_decision_does_not_satisfy_target_approval_required(self):
    self.assertTrue(OPERATION_CONTRACTS.exists(), f"missing contracts: {OPERATION_CONTRACTS}")
    contracts = iter_contracts(load_yaml(OPERATION_CONTRACTS))
    by_action = {contract.get("required_action"): contract for contract in contracts if isinstance(contract, dict)}

    record_contract = by_action["record_human_decision"]
    self.assertEqual(record_contract.get("effect_kind"), "state_mutation")
    self.assertIs(record_contract.get("approval_required"), False)
    self.assertEqual(
      record_contract.get("approval_satisfaction"),
      "does_not_satisfy_target_operation",
    )

  def test_branchy_operations_require_branch_and_internal_step_contracts(self):
    self.assertTrue(OPERATION_CONTRACTS.exists(), f"missing contracts: {OPERATION_CONTRACTS}")
    contracts = iter_contracts(load_yaml(OPERATION_CONTRACTS))
    by_action = {contract.get("required_action"): contract for contract in contracts if isinstance(contract, dict)}

    for action in sorted(BRANCHY_ACTIONS):
      contract = by_action[action]
      branching = contract.get("branching") or {}
      self.assertIs(branching.get("has_branches"), True, action)
      branches = branching.get("branches")
      self.assertIsInstance(branches, list, action)
      self.assertGreater(len(branches), 0, action)
      for branch in branches:
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
          self.assertIn(field, branch, f"{action} branch missing {field}")

  def test_branch_internal_steps_preserve_approval_contract_refs_and_phase_boundaries(self):
    self.assertTrue(OPERATION_CONTRACTS.exists(), f"missing contracts: {OPERATION_CONTRACTS}")
    contracts = iter_contracts(load_yaml(OPERATION_CONTRACTS))
    for contract in contracts:
      if contract.get("required_action") not in BRANCHY_ACTIONS:
        continue
      for branch in contract.get("branching", {}).get("branches", []):
        for step in branch.get("internal_steps", []):
          for field in [
            "step_id",
            "effect_kind",
            "approval_required",
            "approval_contract_ref",
            "phase_boundary",
            "source_ref",
          ]:
            self.assertIn(field, step, f"{contract.get('required_action')} step missing {field}")

  def test_registry_references_contract_without_duplicating_contract_fields(self):
    self.assertTrue(OPERATION_REGISTRY.exists(), f"missing registry: {OPERATION_REGISTRY}")
    registry = load_yaml(OPERATION_REGISTRY)
    operations = registry.get("operations") or []
    self.assertGreater(len(operations), 0)

    for operation in operations:
      self.assertIn("operation_contract", operation, operation.get("operation_id"))
      reference = operation.get("operation_contract")
      self.assertIsInstance(reference, dict)
      for field in ["operation_id", "schema_version", "digest"]:
        self.assertIn(field, reference, operation.get("operation_id"))
      duplicated = REGISTRY_FORBIDDEN_CONTRACT_FIELDS.intersection(operation)
      self.assertEqual(duplicated, set(), operation.get("operation_id"))


if __name__ == "__main__":
  unittest.main()
