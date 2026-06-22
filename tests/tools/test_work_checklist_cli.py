"""work-checklist CLI tests for per-unit execution checklists."""

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


class WorkChecklistCliTests(unittest.TestCase):
  def setUp(self):
    self.tmpdir = Path(tempfile.mkdtemp())
    self.addCleanup(shutil.rmtree, self.tmpdir)

  def test_start_creates_runtime_checklist_with_provenance(self):
    result = run_script(
      [
        "work-checklist",
        "start",
        "--checklist-id", "checklist-test",
        "--unit-id", "unit-test",
        "--title", "Phase 1 red tests",
        "--source-ref", "conversation:user",
        "--reason", "作業の見通しと抜け漏れ防止",
        "--json",
      ],
      cwd=self.tmpdir,
    )

    assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["verdict"], "OK")
    self.assertEqual(data["checklist"]["checklist_id"], "checklist-test")
    checklist_path = (
      self.tmpdir
      / ".reviewcompass/runtime/work-units/checklists/checklist-test.yaml"
    )
    checklist = yaml.safe_load(checklist_path.read_text(encoding="utf-8"))
    self.assertEqual(checklist["schema_version"], "work-checklist-v1")
    self.assertEqual(checklist["status"], "active")
    self.assertEqual(checklist["unit_id"], "unit-test")
    self.assertEqual(checklist["provenance"]["created_by"], "llm")
    self.assertEqual(checklist["provenance"]["source_ref"], "conversation:user")
    self.assertEqual(checklist["provenance"]["reason"], "作業の見通しと抜け漏れ防止")
    self.assertEqual(checklist["items"], [])

  def test_add_item_and_set_status_update_runtime_checklist(self):
    start = run_script(
      [
        "work-checklist",
        "start",
        "--checklist-id", "checklist-test",
        "--unit-id", "unit-test",
        "--title", "Phase 1 red tests",
        "--source-ref", "conversation:user",
        "--reason", "作業の見通しと抜け漏れ防止",
        "--json",
      ],
      cwd=self.tmpdir,
    )
    self.assertEqual(start.returncode, 0, start.stdout + start.stderr)

    add = run_script(
      [
        "work-checklist",
        "add-item",
        "--checklist-id", "checklist-test",
        "--item-id", "C1",
        "--title", "red test を作成する",
        "--json",
      ],
      cwd=self.tmpdir,
    )
    self.assertEqual(add.returncode, 0, add.stdout + add.stderr)

    result = run_script(
      [
        "work-checklist",
        "set-status",
        "--checklist-id", "checklist-test",
        "--item-id", "C1",
        "--status", "active",
        "--json",
      ],
      cwd=self.tmpdir,
    )

    assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
    checklist = yaml.safe_load(
      (
        self.tmpdir
        / ".reviewcompass/runtime/work-units/checklists/checklist-test.yaml"
      ).read_text(encoding="utf-8")
    )
    self.assertEqual(checklist["items"], [
      {
        "id": "C1",
        "title": "red test を作成する",
        "status": "active",
        "child_checklist_id": None,
      }
    ])

  def test_show_reports_progress_and_checkbox_lines(self):
    run_script(
      [
        "work-checklist",
        "start",
        "--checklist-id", "checklist-test",
        "--unit-id", "unit-test",
        "--title", "Progress display",
        "--source-ref", "conversation:user",
        "--reason", "人間が進捗を把握できる表示を確認する",
        "--json",
      ],
      cwd=self.tmpdir,
    )
    for item_id, title, status in [
      ("C1", "red test を作成する", "done"),
      ("C2", "実装する", "active"),
      ("C3", "確認する", "pending"),
      ("C4", "別作業待ち", "blocked"),
    ]:
      add = run_script(
        [
          "work-checklist",
          "add-item",
          "--checklist-id", "checklist-test",
          "--item-id", item_id,
          "--title", title,
          "--json",
        ],
        cwd=self.tmpdir,
      )
      self.assertEqual(add.returncode, 0, add.stdout + add.stderr)
      set_status = run_script(
        [
          "work-checklist",
          "set-status",
          "--checklist-id", "checklist-test",
          "--item-id", item_id,
          "--status", status,
          "--json",
        ],
        cwd=self.tmpdir,
      )
      self.assertEqual(set_status.returncode, 0, set_status.stdout + set_status.stderr)

    result = run_script(
      [
        "work-checklist",
        "show",
        "--checklist-id", "checklist-test",
        "--json",
      ],
      cwd=self.tmpdir,
    )

    assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["progress"], {
      "total": 4,
      "done": 1,
      "active": 1,
      "pending": 1,
      "blocked": 1,
      "active_item_ids": ["C2"],
      "blocked_item_ids": ["C4"],
    })
    self.assertEqual(data["display_lines"], [
      "[x] C1 red test を作成する",
      "[>] C2 実装する",
      "[ ] C3 確認する",
      "[!] C4 別作業待ち",
    ])

  def test_show_human_output_prints_checkbox_lines(self):
    run_script(
      [
        "work-checklist",
        "start",
        "--checklist-id", "checklist-test",
        "--unit-id", "unit-test",
        "--title", "Progress display",
        "--source-ref", "conversation:user",
        "--reason", "人間向け表示を確認する",
        "--json",
      ],
      cwd=self.tmpdir,
    )
    run_script(
      [
        "work-checklist",
        "add-item",
        "--checklist-id", "checklist-test",
        "--item-id", "C1",
        "--title", "red test を作成する",
        "--json",
      ],
      cwd=self.tmpdir,
    )
    run_script(
      [
        "work-checklist",
        "set-status",
        "--checklist-id", "checklist-test",
        "--item-id", "C1",
        "--status", "done",
        "--json",
      ],
      cwd=self.tmpdir,
    )

    result = run_script(
      [
        "work-checklist",
        "show",
        "--checklist-id", "checklist-test",
      ],
      cwd=self.tmpdir,
    )

    assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
    self.assertIn("[PROGRESS] done=1 active=0 pending=0 blocked=0 total=1", result.stdout)
    self.assertIn("[x] C1 red test を作成する", result.stdout)

  def test_branch_records_child_checklist_on_blocked_item(self):
    run_script(
      [
        "work-checklist",
        "start",
        "--checklist-id", "checklist-parent",
        "--unit-id", "unit-test",
        "--title", "Parent checklist",
        "--source-ref", "conversation:user",
        "--reason", "分岐作業を追跡する",
        "--json",
      ],
      cwd=self.tmpdir,
    )
    run_script(
      [
        "work-checklist",
        "add-item",
        "--checklist-id", "checklist-parent",
        "--item-id", "C2",
        "--title", "blocking unit を実装する",
        "--json",
      ],
      cwd=self.tmpdir,
    )
    run_script(
      [
        "work-checklist",
        "set-status",
        "--checklist-id", "checklist-parent",
        "--item-id", "C2",
        "--status", "blocked",
        "--json",
      ],
      cwd=self.tmpdir,
    )

    result = run_script(
      [
        "work-checklist",
        "branch",
        "--checklist-id", "checklist-parent",
        "--item-id", "C2",
        "--child-checklist-id", "checklist-child",
        "--child-title", "Blocking unit implementation",
        "--source-ref", "conversation:user",
        "--reason", "C2 の先行 blocker を処理する",
        "--json",
      ],
      cwd=self.tmpdir,
    )

    assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
    parent = yaml.safe_load(
      (
        self.tmpdir
        / ".reviewcompass/runtime/work-units/checklists/checklist-parent.yaml"
      ).read_text(encoding="utf-8")
    )
    self.assertEqual(parent["items"][0]["child_checklist_id"], "checklist-child")
    child = yaml.safe_load(
      (
        self.tmpdir
        / ".reviewcompass/runtime/work-units/checklists/checklist-child.yaml"
      ).read_text(encoding="utf-8")
    )
    self.assertEqual(child["unit_id"], "unit-test")
    self.assertEqual(child["parent_checklist_id"], "checklist-parent")
    self.assertEqual(child["parent_item_id"], "C2")

  def test_close_rejects_pending_items_and_writes_evidence_when_complete(self):
    run_script(
      [
        "work-checklist",
        "start",
        "--checklist-id", "checklist-test",
        "--unit-id", "unit-test",
        "--title", "Close checklist",
        "--source-ref", "conversation:user",
        "--reason", "完了条件を機械的に検査する",
        "--json",
      ],
      cwd=self.tmpdir,
    )
    run_script(
      [
        "work-checklist",
        "add-item",
        "--checklist-id", "checklist-test",
        "--item-id", "C1",
        "--title", "red test を作成する",
        "--json",
      ],
      cwd=self.tmpdir,
    )

    rejected = run_script(
      [
        "work-checklist",
        "close",
        "--checklist-id", "checklist-test",
        "--completion-summary", "should fail",
        "--json",
      ],
      cwd=self.tmpdir,
    )
    self.assertEqual(rejected.returncode, 2, rejected.stdout + rejected.stderr)
    self.assertIn("unfinished", rejected.stdout)

    run_script(
      [
        "work-checklist",
        "set-status",
        "--checklist-id", "checklist-test",
        "--item-id", "C1",
        "--status", "done",
        "--json",
      ],
      cwd=self.tmpdir,
    )
    result = run_script(
      [
        "work-checklist",
        "close",
        "--checklist-id", "checklist-test",
        "--completion-summary", "Phase 1 red tests completed",
        "--json",
      ],
      cwd=self.tmpdir,
    )

    assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
    evidence_path = (
      self.tmpdir
      / ".reviewcompass/evidence/work-units/checklists/checklist-test.yaml"
    )
    evidence = yaml.safe_load(evidence_path.read_text(encoding="utf-8"))
    self.assertEqual(evidence["status"], "completed")
    self.assertEqual(evidence["completion_summary"], "Phase 1 red tests completed")


if __name__ == "__main__":
  unittest.main()
