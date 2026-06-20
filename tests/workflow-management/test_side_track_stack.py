"""T-017 side track stack red tests."""

import importlib
import sys
import tempfile
import unittest
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "tools"))
SIDE_TRACK_SCHEMA = REPO_ROOT / ".reviewcompass" / "schema" / "side_track_stack.schema.json"


def frame(frame_id, parent_frame_id=None, staged_file_digest="sha256:base"):
  return {
    "frame_id": frame_id,
    "kind": "maintenance",
    "parent_frame_id": parent_frame_id,
    "pushed_by": "llm",
    "title": f"Frame {frame_id}",
    "spawned_from": {
      "required_action": "run_maintenance",
      "active_gate": None,
      "state_file": None,
    },
    "allowed_scope": "local",
    "allowed_files": ["docs/notes/working/example.md"],
    "completion_conditions": ["record decision basis"],
    "return_to": {
      "required_action": "run_workflow_stage",
      "active_gate": None,
      "state_refs": ["stages/in-progress/example.yaml"],
    },
    "staged_file_set": ["docs/notes/working/example.md"],
    "staged_file_digest": staged_file_digest,
    "pushed_at": "2026-06-20T00:00:00+09:00",
    "max_depth": 2,
  }


class SideTrackStackTests(unittest.TestCase):
  def _module(self):
    return importlib.import_module("check_workflow_action.side_track_stack")

  def test_side_track_stack_schema_exists(self):
    self.assertTrue(SIDE_TRACK_SCHEMA.exists(), f"missing schema: {SIDE_TRACK_SCHEMA}")

  def test_side_track_stack_rejects_non_lifo_pop(self):
    module = self._module()
    stack = {"schema_version": "side-track-stack-v1", "frames": [frame("A"), frame("B", "A")]}

    result = module.pop_frame(stack, frame_id="A")

    self.assertEqual(result["verdict"], "DEVIATION")
    self.assertIn("LIFO", "\n".join(result["reasons"]))

  def test_side_track_push_pop_are_mutating_but_current_is_read_only(self):
    module = self._module()
    with tempfile.TemporaryDirectory() as tmp:
      path = Path(tmp) / "side-track-stack.yaml"
      path.write_text(yaml.safe_dump({"schema_version": "side-track-stack-v1", "frames": []}), encoding="utf-8")
      before = path.read_text(encoding="utf-8")

      current = module.current(path)
      after_current = path.read_text(encoding="utf-8")
      pushed = module.push_frame(path, frame("A"))
      after_push = path.read_text(encoding="utf-8")

      self.assertEqual(current["verdict"], "OK")
      self.assertEqual(before, after_current)
      self.assertEqual(pushed["verdict"], "OK")
      self.assertNotEqual(after_current, after_push)

  def test_side_track_pop_unresolved_return_to_routes_to_repair(self):
    module = self._module()
    stack = {
      "schema_version": "side-track-stack-v1",
      "frames": [
        frame("A", staged_file_digest="sha256:old"),
      ],
    }
    stack["frames"][0]["return_to"]["state_refs"] = ["missing-state.yaml"]

    result = module.pop_frame(stack, frame_id="A", current_staged_file_digest="sha256:new")

    self.assertEqual(result["verdict"], "DEVIATION")
    self.assertEqual(result["next_required_action"], "repair_workflow_state")

  def test_side_track_push_rejects_allowed_files_drift(self):
    module = self._module()
    with tempfile.TemporaryDirectory() as tmp:
      path = Path(tmp) / "side-track-stack.yaml"
      path.write_text(yaml.safe_dump({"schema_version": "side-track-stack-v1", "frames": []}), encoding="utf-8")
      next_frame = frame("A")
      next_frame["allowed_files"] = ["docs/notes/working/example.md"]
      next_frame["staged_file_set"] = [
        "docs/notes/working/example.md",
        "tools/unapproved.py",
      ]

      result = module.push_frame(path, next_frame)

      self.assertEqual(result["verdict"], "DEVIATION")
      self.assertIn("allowed_files", "\n".join(result["reasons"]))

  def test_side_track_push_rejects_max_depth_exceeded(self):
    module = self._module()
    with tempfile.TemporaryDirectory() as tmp:
      path = Path(tmp) / "side-track-stack.yaml"
      stack = {
        "schema_version": "side-track-stack-v1",
        "frames": [
          frame("A"),
          frame("B", "A"),
        ],
      }
      path.write_text(yaml.safe_dump(stack), encoding="utf-8")

      result = module.push_frame(path, frame("C", "B"))

      self.assertEqual(result["verdict"], "DEVIATION")
      self.assertIn("max_depth", "\n".join(result["reasons"]))


if __name__ == "__main__":
  unittest.main()
