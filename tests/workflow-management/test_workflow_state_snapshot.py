"""T-017 workflow state snapshot red tests."""

import importlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "tools"))
SNAPSHOT_SCHEMA = REPO_ROOT / ".reviewcompass" / "schema" / "workflow_state_snapshot.schema.json"

MINIMUM_TOP_LEVEL = [
  "schema_version",
  "generated_by",
  "generated_at",
  "source_next_action_sha256",
  "current_work",
  "active_work_units",
  "active_side_tracks",
  "git_tree_summary",
  "post_write_manifest_summary",
  "workflow_state_summary",
]

MINIMUM_CURRENT_WORK = [
  "required_action",
  "title",
  "outer_node",
  "inner_node",
  "active_gate",
]


class WorkflowStateSnapshotTests(unittest.TestCase):
  def _module(self):
    return importlib.import_module("check_workflow_action.workflow_state_snapshot")

  def test_workflow_snapshot_schema_matches_design_minimum_structure(self):
    self.assertTrue(SNAPSHOT_SCHEMA.exists(), f"missing schema: {SNAPSHOT_SCHEMA}")
    module = self._module()

    snapshot = module.build_snapshot(REPO_ROOT)

    for field in MINIMUM_TOP_LEVEL:
      self.assertIn(field, snapshot)
    for field in MINIMUM_CURRENT_WORK:
      self.assertIn(field, snapshot["current_work"])

  def test_workflow_snapshot_includes_reopen_and_worktree_digests(self):
    module = self._module()

    snapshot = module.build_snapshot(REPO_ROOT)
    summary = snapshot["workflow_state_summary"]

    self.assertIn("spec_json", summary)
    self.assertIn("workflow_state", summary["spec_json"])
    self.assertIn("recheck", summary["spec_json"])
    self.assertIn("in_progress_files", summary)
    self.assertIn("pending_gates", summary)
    self.assertIn("drafting_completed_gates", summary)
    self.assertIn("completed_gates", summary)
    self.assertIn("operation_contract", summary)
    self.assertIn("staged_file_set_digest", snapshot["git_tree_summary"])
    self.assertIn("worktree_dirty_path_digest", snapshot["git_tree_summary"])

  def test_workflow_snapshot_includes_active_work_unit_stack(self):
    module = self._module()
    with tempfile.TemporaryDirectory() as tmp:
      stack = {
        "schema_version": "work-unit-stack-v1",
        "frames": [
          {
            "unit_id": "unit-blocking-test",
            "kind": "blocking",
            "parent_unit_id": "unit-parent-test",
            "title": "mechanize declarations",
            "reason": "manual declarations are easy to forget",
            "status": "active",
            "entered_at": "2026-06-22T00:00:00+00:00",
            "return_conditions": ["exit command tested"],
          },
        ],
      }
      path = Path(tmp) / ".reviewcompass/runtime/work-units/stack.yaml"
      path.parent.mkdir(parents=True)
      path.write_text(yaml.safe_dump(stack, allow_unicode=True), encoding="utf-8")

      snapshot = module.build_snapshot(Path(tmp))

      self.assertEqual(snapshot["active_work_units"], stack["frames"])

  def test_snapshot_drift_reports_pending_gate_change(self):
    module = self._module()
    with tempfile.TemporaryDirectory() as tmp:
      path = Path(tmp) / "snapshot.yaml"
      snapshot = {
        "schema_version": "workflow-state-snapshot-v1",
        "source_next_action_sha256": "sha256:old",
        "workflow_state_summary": {
          "pending_gates": ["stages/design.yaml#triad-review"],
        },
        "git_tree_summary": {
          "staged_file_set_digest": "sha256:old",
          "worktree_dirty_path_digest": "sha256:old",
        },
      }
      path.write_text(yaml.safe_dump(snapshot), encoding="utf-8")

      result = module.detect_drift(
        path,
        current_next_action={"pending_gates": ["stages/design.yaml#approval"]},
        current_next_action_sha256="sha256:old",
        current_git_tree_summary={
          "staged_file_set_digest": "sha256:old",
          "worktree_dirty_path_digest": "sha256:old",
        },
      )

      self.assertEqual(result["verdict"], "DEVIATION")
      self.assertIn("pending_gates", "\n".join(result["reasons"]))

  def test_snapshot_is_not_trusted_without_matching_next_action_digest(self):
    module = self._module()
    with tempfile.TemporaryDirectory() as tmp:
      path = Path(tmp) / "snapshot.yaml"
      path.write_text(
        yaml.safe_dump(
          {
            "schema_version": "workflow-state-snapshot-v1",
            "source_next_action_sha256": "sha256:old",
            "current_work": {},
            "workflow_state_summary": {},
          }
        ),
        encoding="utf-8",
      )

      result = module.detect_drift(
        path,
        current_next_action=json.loads('{"kind": "stage"}'),
        current_next_action_sha256="sha256:new",
        current_git_tree_summary={},
      )

      self.assertEqual(result["verdict"], "DEVIATION")
      self.assertIn("source_next_action_sha256", "\n".join(result["reasons"]))

  def test_snapshot_drift_reports_completed_gate_and_contract_digest_change(self):
    module = self._module()
    with tempfile.TemporaryDirectory() as tmp:
      path = Path(tmp) / "snapshot.yaml"
      snapshot = {
        "schema_version": "workflow-state-snapshot-v1",
        "source_next_action_sha256": "sha256:same",
        "workflow_state_summary": {
          "pending_gates": [],
          "drafting_completed_gates": ["stages/design.yaml#drafting"],
          "completed_gates": ["stages/design.yaml#triad-review"],
          "operation_contract": {"digest": "sha256:old"},
        },
        "git_tree_summary": {
          "staged_file_set_digest": "sha256:same",
          "worktree_dirty_path_digest": "sha256:same",
        },
      }
      path.write_text(yaml.safe_dump(snapshot), encoding="utf-8")

      result = module.detect_drift(
        path,
        current_next_action={
          "pending_gates": [],
          "drafting_completed_gates": ["stages/design.yaml#drafting"],
          "completed_gates": ["stages/design.yaml#alignment"],
          "operation_contract": {"digest": "sha256:new"},
        },
        current_next_action_sha256="sha256:same",
        current_git_tree_summary={
          "staged_file_set_digest": "sha256:same",
          "worktree_dirty_path_digest": "sha256:same",
        },
      )

      self.assertEqual(result["verdict"], "DEVIATION")
      reasons = "\n".join(result["reasons"])
      self.assertIn("completed_gates", reasons)
      self.assertIn("operation_contract", reasons)


if __name__ == "__main__":
  unittest.main()
