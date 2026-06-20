"""T-017 workflow snapshot CLI red tests."""

import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "tools" / "check-workflow-action.py"


def run(args, cwd=REPO_ROOT):
  return subprocess.run(
    ["python3", str(SCRIPT)] + list(args),
    cwd=str(cwd),
    capture_output=True,
    text=True,
    timeout=30,
  )


class WorkflowSnapshotCliTests(unittest.TestCase):
  def test_workflow_snapshot_json_is_read_only_and_has_minimum_shape(self):
    with tempfile.TemporaryDirectory() as tmp:
      tmp_path = Path(tmp)
      shutil.copytree(REPO_ROOT / ".reviewcompass", tmp_path / ".reviewcompass", dirs_exist_ok=True)
      shutil.copytree(REPO_ROOT / "stages", tmp_path / "stages", dirs_exist_ok=True)
      before = sorted(str(p.relative_to(tmp_path)) for p in tmp_path.rglob("*") if p.is_file())

      result = run(["workflow-snapshot", "--json"], cwd=tmp_path)

      self.assertEqual(result.returncode, 0, result.stderr)
      data = json.loads(result.stdout)
      self.assertEqual(data["verdict"], "OK")
      snapshot = data["snapshot"]
      for field in [
        "schema_version",
        "generated_by",
        "generated_at",
        "source_next_action_sha256",
        "current_work",
        "active_side_tracks",
        "git_tree_summary",
        "post_write_manifest_summary",
        "workflow_state_summary",
      ]:
        self.assertIn(field, snapshot)
      after = sorted(str(p.relative_to(tmp_path)) for p in tmp_path.rglob("*") if p.is_file())
      self.assertEqual(before, after)

  def test_side_track_stack_current_json_is_read_only(self):
    result = run(["side-track-stack", "current", "--json"])

    self.assertEqual(result.returncode, 0, result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["verdict"], "OK")
    self.assertIn("stack", data)
    self.assertEqual(data["operation_mode"], "read_only")


if __name__ == "__main__":
  unittest.main()
