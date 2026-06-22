"""work-unit CLI tests for mechanized blocking-unit entry and exit."""

import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "tools" / "check-workflow-action.py"


def run_script(args, cwd):
  return subprocess.run(
    ["python3", str(SCRIPT)] + list(args),
    cwd=str(cwd),
    capture_output=True,
    text=True,
    timeout=10,
  )


def assert_script_invoked(testcase, result):
  for marker in ("No such file or directory", "can't open file"):
    testcase.assertNotIn(marker, result.stderr)


class WorkUnitCliTests(unittest.TestCase):
  def setUp(self):
    self.tmpdir = Path(tempfile.mkdtemp())
    self.addCleanup(shutil.rmtree, self.tmpdir)

  def _enter_blocking(self, unit_id="unit-blocking-test", parent_unit_id="unit-parent-test"):
    return run_script(
      [
        "work-unit",
        "enter-blocking",
        "--unit-id", unit_id,
        "--parent-unit-id", parent_unit_id,
        "--title", "mechanize declarations",
        "--reason", "manual declarations are easy to forget",
        "--return-condition", "implementation committed",
        "--json",
      ],
      cwd=self.tmpdir,
    )

  def test_enter_blocking_records_active_runtime_frame(self):
    result = run_script(
      [
        "work-unit",
        "enter-blocking",
        "--unit-id", "unit-blocking-test",
        "--parent-unit-id", "unit-parent-test",
        "--title", "deploy policy red test",
        "--reason", "backlog deploy exclusion must be fixed first",
        "--return-condition", "red test committed",
        "--return-condition", "push completed",
        "--json",
      ],
      cwd=self.tmpdir,
    )

    assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["verdict"], "OK")
    self.assertEqual(data["current"]["unit_id"], "unit-blocking-test")
    stack_path = self.tmpdir / ".reviewcompass/runtime/work-units/stack.yaml"
    stack = yaml.safe_load(stack_path.read_text(encoding="utf-8"))
    self.assertEqual(stack["schema_version"], "work-unit-stack-v1")
    self.assertEqual(stack["frames"][-1]["kind"], "blocking")
    self.assertEqual(stack["frames"][-1]["parent_unit_id"], "unit-parent-test")
    self.assertEqual(stack["frames"][-1]["return_conditions"], [
      "red test committed",
      "push completed",
    ])

  def test_current_reports_active_blocking_unit(self):
    enter = run_script(
      [
        "work-unit",
        "enter-blocking",
        "--unit-id", "unit-blocking-test",
        "--parent-unit-id", "unit-parent-test",
        "--title", "mechanize declarations",
        "--reason", "manual declarations are easy to forget",
        "--return-condition", "exit command tested",
        "--json",
      ],
      cwd=self.tmpdir,
    )
    self.assertEqual(enter.returncode, 0, enter.stdout + enter.stderr)

    result = run_script(["work-unit", "current", "--json"], cwd=self.tmpdir)

    assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["verdict"], "OK")
    self.assertEqual(data["current"]["kind"], "blocking")
    self.assertEqual(data["current"]["unit_id"], "unit-blocking-test")

  def test_next_reports_active_blocking_unit_before_normal_workflow(self):
    enter = run_script(
      [
        "work-unit",
        "enter-blocking",
        "--unit-id", "unit-blocking-test",
        "--parent-unit-id", "unit-parent-test",
        "--title", "mechanize declarations",
        "--reason", "manual declarations are easy to forget",
        "--return-condition", "exit command tested",
        "--json",
      ],
      cwd=self.tmpdir,
    )
    self.assertEqual(enter.returncode, 0, enter.stdout + enter.stderr)

    result = run_script(["next", "--json"], cwd=self.tmpdir)

    assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["next_action"]["kind"], "blocking_unit_in_progress")
    self.assertEqual(data["next_action"]["unit_id"], "unit-blocking-test")
    self.assertEqual(data["current_state"]["active_work_units"][0]["unit_id"], "unit-blocking-test")

  def test_exit_blocking_removes_frame_and_writes_evidence(self):
    enter = run_script(
      [
        "work-unit",
        "enter-blocking",
        "--unit-id", "unit-blocking-test",
        "--parent-unit-id", "unit-parent-test",
        "--title", "mechanize declarations",
        "--reason", "manual declarations are easy to forget",
        "--return-condition", "implementation committed",
        "--json",
      ],
      cwd=self.tmpdir,
    )
    self.assertEqual(enter.returncode, 0, enter.stdout + enter.stderr)

    result = run_script(
      [
        "work-unit",
        "exit-blocking",
        "--unit-id", "unit-blocking-test",
        "--completion-summary", "enter/current/exit implemented",
        "--json",
      ],
      cwd=self.tmpdir,
    )

    assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["verdict"], "OK")
    self.assertEqual(data["returned_to"]["unit_id"], "unit-parent-test")
    current = json.loads(
      run_script(["work-unit", "current", "--json"], cwd=self.tmpdir).stdout
    )
    self.assertIsNone(current["current"])
    evidence_path = (
      self.tmpdir
      / ".reviewcompass/evidence/work-units/blocking-units/unit-blocking-test.yaml"
    )
    evidence = yaml.safe_load(evidence_path.read_text(encoding="utf-8"))
    self.assertEqual(evidence["status"], "completed")
    self.assertEqual(evidence["completion_summary"], "enter/current/exit implemented")

  def test_exit_blocking_rejects_non_top_unit(self):
    enter = run_script(
      [
        "work-unit",
        "enter-blocking",
        "--unit-id", "unit-blocking-test",
        "--parent-unit-id", "unit-parent-test",
        "--title", "mechanize declarations",
        "--reason", "manual declarations are easy to forget",
        "--return-condition", "implementation committed",
        "--json",
      ],
      cwd=self.tmpdir,
    )
    self.assertEqual(enter.returncode, 0, enter.stdout + enter.stderr)

    result = run_script(
      [
        "work-unit",
        "exit-blocking",
        "--unit-id", "unit-other",
        "--completion-summary", "wrong unit",
        "--json",
      ],
      cwd=self.tmpdir,
    )

    assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["verdict"], "DEVIATION")
    self.assertIn("top", "\n".join(data["reasons"]))

  def test_enter_blocking_rejects_nested_blocking_without_preflight_decision(self):
    enter = self._enter_blocking(
      unit_id="unit-blocking-parent",
      parent_unit_id="unit-mainline",
    )
    self.assertEqual(enter.returncode, 0, enter.stdout + enter.stderr)

    result = run_script(
      [
        "work-unit",
        "enter-blocking",
        "--unit-id", "unit-blocking-child",
        "--parent-unit-id", "unit-blocking-parent",
        "--title", "nested blocking",
        "--reason", "another interruption appeared",
        "--return-condition", "child completed",
        "--json",
      ],
      cwd=self.tmpdir,
    )

    assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["verdict"], "DEVIATION")
    self.assertIn("active blocking unit", "\n".join(data["reasons"]))

  def test_exit_blocking_records_parent_resume_pending_for_next(self):
    enter = self._enter_blocking(parent_unit_id="unit-parent-resume")
    self.assertEqual(enter.returncode, 0, enter.stdout + enter.stderr)
    exit_result = run_script(
      [
        "work-unit",
        "exit-blocking",
        "--unit-id", "unit-blocking-test",
        "--completion-summary", "blocking unit complete",
        "--json",
      ],
      cwd=self.tmpdir,
    )
    self.assertEqual(exit_result.returncode, 0, exit_result.stdout + exit_result.stderr)

    marker_path = (
      self.tmpdir
      / ".reviewcompass/runtime/work-units/resume-pending.yaml"
    )
    marker = yaml.safe_load(marker_path.read_text(encoding="utf-8"))
    self.assertEqual(marker["kind"], "parent_resume_pending")
    self.assertEqual(marker["parent_unit_id"], "unit-parent-resume")

    next_result = run_script(["next", "--json"], cwd=self.tmpdir)
    assert_script_invoked(self, next_result)
    self.assertEqual(next_result.returncode, 0, next_result.stdout + next_result.stderr)
    data = json.loads(next_result.stdout)
    self.assertEqual(data["next_action"]["kind"], "parent_resume_pending")
    self.assertEqual(data["next_action"]["parent_unit_id"], "unit-parent-resume")

  def test_preflight_start_reports_active_unit_before_new_work(self):
    enter = self._enter_blocking(
      unit_id="unit-existing-blocking",
      parent_unit_id="unit-mainline",
    )
    self.assertEqual(enter.returncode, 0, enter.stdout + enter.stderr)

    result = run_script(
      [
        "work-unit",
        "preflight-start",
        "--proposed-unit-id", "unit-new-work",
        "--title", "new work",
        "--reason", "user asked to switch tasks",
        "--json",
      ],
      cwd=self.tmpdir,
    )

    assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["verdict"], "DEVIATION")
    self.assertFalse(data["start_allowed"])
    self.assertIn("unit-existing-blocking", "\n".join(data["blocking_reasons"]))


if __name__ == "__main__":
  unittest.main()
