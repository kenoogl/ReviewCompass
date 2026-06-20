"""T-017 approval gate red tests.

These tests define the approval gate behavior before implementation. They
should fail until approval gate schema and validation logic are added.
"""

import copy
import json
import importlib
import sys
import unittest
from pathlib import Path

import jsonschema


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "tools"))
APPROVAL_GATE_SCHEMA = REPO_ROOT / ".reviewcompass" / "schema" / "approval_gate.schema.json"

REQUIRED_RECORD_FIELDS = [
  "decision_id",
  "decision",
  "decision_scope",
  "target_operation_id",
  "target_required_action",
  "target_artifact",
  "target_artifact_digest",
  "staged_file_set_digest",
  "binding_kind",
  "decided_by",
  "decided_at",
  "source_ref",
  "source_digest",
  "rationale",
  "next_action_expectation",
  "consumed",
]


def valid_record(**overrides):
  record = {
    "schema_version": "approval-gate-v1",
    "decision_id": "D-001",
    "decision": "approved",
    "decision_scope": "human_only",
    "target_operation_id": "commit_stop_point",
    "target_required_action": "commit_stop_point",
    "target_artifact": None,
    "target_artifact_digest": None,
    "staged_file_set_digest": "sha256:" + "a" * 64,
    "binding_kind": "staged_file_set_digest",
    "decided_by": "user",
    "decided_at": "2026-06-20T00:00:00+09:00",
    "source_ref": "conversation:user:commit",
    "source_digest": "sha256:" + "b" * 64,
    "rationale": "user approved commit",
    "next_action_expectation": "proceed",
    "consumed": False,
  }
  record.update(overrides)
  return record


def approval_gate_schema():
  schema = json.loads(APPROVAL_GATE_SCHEMA.read_text(encoding="utf-8"))
  schema["properties"]["target_required_action"] = {"type": "string", "minLength": 1}
  return schema


class ApprovalGateTests(unittest.TestCase):
  def _module(self):
    return importlib.import_module("check_workflow_action.approval_gate")

  def test_approval_gate_record_requires_target_binding_fields(self):
    self.assertTrue(APPROVAL_GATE_SCHEMA.exists(), f"missing schema: {APPROVAL_GATE_SCHEMA}")
    module = self._module()

    for field in REQUIRED_RECORD_FIELDS:
      record = valid_record()
      record.pop(field)
      result = module.validate_approval_gate_record(record)
      self.assertEqual(result["verdict"], "DEVIATION", field)
      self.assertIn(field, "\n".join(result["reasons"]))

  def test_approval_record_non_approved_decisions_block_irreversible_operation(self):
    module = self._module()

    for decision in ["rejected", "deferred", "changes_requested"]:
      result = module.allows_target_operation(
        valid_record(decision=decision),
        operation_contract={
          "required_action": "commit_stop_point",
          "approval_required": True,
          "phase_boundary": "commit_boundary",
          "effect_kind": "state_mutation",
          "actor": {"kind": "human"},
        },
      )
      self.assertFalse(result["allowed"], decision)
      self.assertEqual(result["verdict"], "DEVIATION", decision)

  def test_proxy_model_cannot_approve_human_only_decision_scope(self):
    module = self._module()

    result = module.allows_target_operation(
      valid_record(decided_by="proxy_model", decision_scope="human_only"),
      operation_contract={
        "required_action": "commit_stop_point",
        "approval_required": True,
        "phase_boundary": "commit_boundary",
        "effect_kind": "state_mutation",
        "actor": {"kind": "human"},
      },
    )

    self.assertFalse(result["allowed"])
    self.assertEqual(result["verdict"], "DEVIATION")
    self.assertIn("human_only", "\n".join(result["reasons"]))

  def test_llm_cannot_approve_human_only_decision_scope(self):
    module = self._module()

    result = module.allows_target_operation(
      valid_record(decided_by="llm", decision_scope="human_only"),
      operation_contract={
        "required_action": "commit_stop_point",
        "approval_required": True,
        "phase_boundary": "commit_boundary",
        "effect_kind": "state_mutation",
        "actor": {"kind": "human"},
      },
    )

    self.assertFalse(result["allowed"])
    self.assertEqual(result["verdict"], "DEVIATION")
    self.assertIn("human_only", "\n".join(result["reasons"]))

  def test_invalid_actor_and_empty_source_metadata_are_rejected(self):
    module = self._module()

    cases = [
      valid_record(decided_by="unknown_actor"),
      valid_record(source_ref=""),
      valid_record(source_digest=""),
      valid_record(source_digest="not-a-sha256"),
    ]
    for record in cases:
      result = module.validate_approval_gate_record(record)
      self.assertEqual(result["verdict"], "DEVIATION", record)

  def test_authorization_requires_current_digest_check(self):
    module = self._module()

    result = module.allows_target_operation(
      valid_record(
        binding_kind="staged_file_set_digest",
        staged_file_set_digest="sha256:" + "a" * 64,
      ),
      operation_contract={
        "operation_id": "commit_stop_point",
        "required_action": "commit_stop_point",
        "approval_required": True,
        "phase_boundary": "commit_boundary",
        "effect_kind": "state_mutation",
        "actor": {"kind": "human"},
      },
      current_staged_file_set_digest="sha256:" + "f" * 64,
    )

    self.assertFalse(result["allowed"])
    self.assertEqual(result["verdict"], "DEVIATION")
    self.assertIn("digest", "\n".join(result["reasons"]))

  def test_authorization_fails_closed_when_required_current_digest_is_missing(self):
    module = self._module()

    result = module.allows_target_operation(
      valid_record(
        binding_kind="staged_file_set_digest",
        staged_file_set_digest="sha256:" + "a" * 64,
      ),
      operation_contract={
        "operation_id": "commit_stop_point",
        "required_action": "commit_stop_point",
        "approval_required": True,
        "phase_boundary": "commit_boundary",
        "effect_kind": "state_mutation",
        "actor": {"kind": "human"},
      },
    )

    self.assertFalse(result["allowed"])
    self.assertEqual(result["verdict"], "DEVIATION")
    self.assertIn("current", "\n".join(result["reasons"]))

  def test_decision_scope_is_derived_from_operation_contract(self):
    module = self._module()

    result = module.validate_approval_gate_record(
      valid_record(decision_scope="proxy_allowed"),
      operation_contract={
        "required_action": "commit_stop_point",
        "approval_required": True,
        "phase_boundary": "commit_boundary",
        "effect_kind": "state_mutation",
        "actor": {"kind": "human"},
      },
    )

    self.assertEqual(result["verdict"], "DEVIATION")
    self.assertIn("decision_scope", "\n".join(result["reasons"]))

  def test_binding_kind_requires_matching_digest_fields(self):
    module = self._module()

    cases = [
      valid_record(binding_kind="artifact_digest", target_artifact_digest=None),
      valid_record(binding_kind="staged_file_set_digest", staged_file_set_digest=None),
      valid_record(binding_kind="both", target_artifact_digest=None),
      valid_record(binding_kind="both", staged_file_set_digest=None),
      valid_record(binding_kind="none"),
    ]
    for record in cases:
      result = module.validate_approval_gate_record(
        record,
        operation_contract={
          "required_action": "commit_stop_point",
          "approval_required": True,
          "phase_boundary": "commit_boundary",
          "effect_kind": "state_mutation",
          "actor": {"kind": "human"},
        },
      )
      self.assertEqual(result["verdict"], "DEVIATION", record["binding_kind"])

  def test_binding_kind_none_is_allowed_only_for_wait_only_operations(self):
    module = self._module()

    wait_only = module.validate_approval_gate_record(
      valid_record(
        target_operation_id="wait_for_human_decision",
        target_required_action="wait_for_human_decision",
        decision_scope="advisory_only",
        binding_kind="none",
        target_artifact_digest=None,
        staged_file_set_digest=None,
      ),
      operation_contract={
        "operation_id": "wait_for_human_decision",
        "required_action": "wait_for_human_decision",
        "approval_required": False,
        "phase_boundary": "none",
        "effect_kind": "read",
        "actor": {"kind": "tool"},
      },
    )
    self.assertEqual(wait_only["verdict"], "OK", wait_only.get("reasons"))

    irreversible = module.validate_approval_gate_record(
      valid_record(
        decision_scope="human_only",
        binding_kind="none",
        target_artifact_digest=None,
        staged_file_set_digest=None,
      ),
      operation_contract={
        "operation_id": "commit_stop_point",
        "required_action": "commit_stop_point",
        "approval_required": True,
        "phase_boundary": "commit_boundary",
        "effect_kind": "state_mutation",
        "actor": {"kind": "human"},
      },
    )
    self.assertEqual(irreversible["verdict"], "DEVIATION")

  def test_target_operation_id_must_match_operation_contract(self):
    module = self._module()

    result = module.allows_target_operation(
      valid_record(target_operation_id="wrong_operation_id"),
      operation_contract={
        "operation_id": "commit_stop_point",
        "required_action": "commit_stop_point",
        "approval_required": True,
        "phase_boundary": "commit_boundary",
        "effect_kind": "state_mutation",
        "actor": {"kind": "human"},
      },
    )

    self.assertFalse(result["allowed"])
    self.assertEqual(result["verdict"], "DEVIATION")
    self.assertIn("target_operation_id", "\n".join(result["reasons"]))

  def test_digest_mismatch_fails_closed(self):
    module = self._module()

    result = module.validate_approval_gate_record(
      valid_record(
        binding_kind="both",
        target_artifact_digest="sha256:" + "c" * 64,
        staged_file_set_digest="sha256:" + "d" * 64,
      ),
      operation_contract={
        "operation_id": "commit_stop_point",
        "required_action": "commit_stop_point",
        "approval_required": True,
        "phase_boundary": "commit_boundary",
        "effect_kind": "state_mutation",
        "actor": {"kind": "human"},
      },
      current_target_artifact_digest="sha256:" + "e" * 64,
      current_staged_file_set_digest="sha256:" + "f" * 64,
    )

    self.assertEqual(result["verdict"], "DEVIATION")
    self.assertIn("digest", "\n".join(result["reasons"]))

  def test_schema_enforces_binding_kind_digest_requirements(self):
    schema = approval_gate_schema()
    jsonschema.Draft202012Validator.check_schema(schema)
    validator = jsonschema.Draft202012Validator(schema)

    invalid_cases = [
      valid_record(binding_kind="artifact_digest", target_artifact_digest=None),
      valid_record(binding_kind="staged_file_set_digest", staged_file_set_digest=None),
      valid_record(binding_kind="both", target_artifact_digest=None),
      valid_record(binding_kind="both", staged_file_set_digest=None),
      valid_record(binding_kind="none", staged_file_set_digest="sha256:" + "a" * 64),
    ]
    for record in invalid_cases:
      self.assertNotEqual(list(validator.iter_errors(record)), [], record)

    valid = copy.deepcopy(valid_record())
    self.assertEqual(list(validator.iter_errors(valid)), [])


if __name__ == "__main__":
  unittest.main()
