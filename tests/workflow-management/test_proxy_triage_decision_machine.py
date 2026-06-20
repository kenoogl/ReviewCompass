"""T-019 proxy triage decision machine red tests."""

import importlib
import json
import sys
import unittest
from pathlib import Path

import jsonschema


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "tools"))
SCHEMA_PATH = REPO_ROOT / ".reviewcompass" / "schema" / "proxy_triage_decision.schema.json"


def load_json(path):
  with path.open(encoding="utf-8") as f:
    return json.load(f)


def valid_decision(**overrides):
  decision = {
    "schema_version": "proxy-triage-decision-v1",
    "decision_id": "proxy-decision-001",
    "target_findings": ["finding-001"],
    "target_clusters": ["cluster-001"],
    "source_triage_path": "review-run/triage.yaml",
    "raw_response_path": "review-run/raw/proxy.txt",
    "parsed_finding_paths": ["review-run/parsed/model.yaml"],
    "decision_prompt_path": "review-run/prompts/proxy.prompt.md",
    "proxy_raw_response_path": "review-run/raw/proxy-decision.txt",
    "candidate_decisions": [
      {"id": "leave-as-is", "final_label": "leave-as-is", "finding_ids": ["finding-001"]}
    ],
    "selected_decision": {
      "id": "leave-as-is",
      "final_label": "leave-as-is",
      "finding_ids": ["finding-001"],
    },
    "reasoning_summary": "Evidence is complete and no human-required predicate applies.",
    "final_application_target": {
      "operation_id": "proxy_triage_apply_batch",
      "triage_path": "review-run/triage.yaml",
      "finding_ids": ["finding-001"],
    },
    "approval_scope": {
      "review_triage_decide": ["finding-001"],
      "apply_fixes": ["finding-001"],
    },
  }
  decision.update(overrides)
  return decision


class ProxyTriageDecisionMachineTests(unittest.TestCase):
  def _module(self):
    return importlib.import_module("check_workflow_action.proxy_triage_decisions")

  def test_proxy_triage_decision_requires_raw_prompt_candidate_selected_reason_target(self):
    self.assertTrue(SCHEMA_PATH.exists(), f"missing schema: {SCHEMA_PATH}")
    schema = load_json(SCHEMA_PATH)
    validator = jsonschema.Draft202012Validator(schema)
    self.assertEqual(list(validator.iter_errors(valid_decision())), [])

    for field in [
      "raw_response_path",
      "decision_prompt_path",
      "candidate_decisions",
      "selected_decision",
      "reasoning_summary",
      "final_application_target",
    ]:
      broken = valid_decision()
      broken.pop(field)
      self.assertNotEqual(list(validator.iter_errors(broken)), [], field)

  def test_human_required_decision_blocks_proxy_application(self):
    module = self._module()
    result = module.evaluate_human_required(
      decision=valid_decision(),
      operation_contract={"operation_id": "repair_workflow_state", "approval_required": True},
      approval_gate=None,
      review_wave_impact={"unresolved": False},
    )

    self.assertEqual(result["verdict"], "DEVIATION")
    self.assertTrue(result["blocks_proxy_apply"])
    self.assertIn("approval_required", "\n".join(result["blocking_reasons"]))

  def test_human_required_priority_overrides_proxy_approved_leave_as_is(self):
    module = self._module()
    decision = valid_decision(
      selected_decision={
        "id": "proxy-approved",
        "final_label": "leave-as-is",
        "finding_ids": ["finding-001"],
      }
    )

    result = module.evaluate_human_required(
      decision=decision,
      operation_contract={"operation_id": "record_human_decision", "approval_required": False},
      approval_gate={"decision_scope": "human_only", "decision": "approved", "consumed": False},
      review_wave_impact={"unresolved": False},
    )

    self.assertEqual(result["verdict"], "DEVIATION")
    self.assertTrue(result["blocks_proxy_apply"])
    self.assertIn("human_only", "\n".join(result["blocking_reasons"]))

  def test_proxy_triage_requires_complete_finding_cluster_coverage(self):
    module = self._module()
    decision = valid_decision(
      target_findings=["finding-001", "finding-002"],
      selected_decision={
        "id": "leave-as-is",
        "final_label": "leave-as-is",
        "finding_ids": ["finding-001"],
      },
    )

    result = module.validate_coverage(decision)

    self.assertEqual(result["verdict"], "DEVIATION")
    self.assertIn("coverage", "\n".join(result["reasons"]).lower())

  def test_proxy_triage_rejects_review_and_apply_scope_mismatch(self):
    module = self._module()
    decision = valid_decision(
      approval_scope={
        "review_triage_decide": ["finding-001"],
        "apply_fixes": ["finding-002"],
      }
    )

    result = module.validate_approval_scope(decision)

    self.assertEqual(result["verdict"], "DEVIATION")
    self.assertIn("scope", "\n".join(result["reasons"]).lower())

  def test_human_required_predicate_evaluation_order_is_fixed(self):
    module = self._module()
    order = module.human_required_evaluation_order()

    self.assertEqual(
      order,
      [
        "coverage_and_evidence",
        "finding_to_operation_mapping",
        "operation_contract",
        "approval_gate_record",
        "review_wave_impact",
        "priority_resolution",
      ],
    )


if __name__ == "__main__":
  unittest.main()
