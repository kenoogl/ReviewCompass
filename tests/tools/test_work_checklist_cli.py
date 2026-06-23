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
    self.assertEqual(checklist["progress"], {
      "total": 0,
      "done": 0,
      "active": 0,
      "pending": 0,
      "blocked": 0,
      "active_item_ids": [],
      "blocked_item_ids": [],
    })
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
        "checked": False,
        "child_checklist_id": None,
      }
    ])
    self.assertEqual(checklist["progress"], {
      "total": 1,
      "done": 0,
      "active": 1,
      "pending": 0,
      "blocked": 0,
      "active_item_ids": ["C1"],
      "blocked_item_ids": [],
    })

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
    checklist = yaml.safe_load(
      (
        self.tmpdir
        / ".reviewcompass/runtime/work-units/checklists/checklist-test.yaml"
      ).read_text(encoding="utf-8")
    )
    self.assertEqual(checklist["progress"], data["progress"])
    self.assertEqual(
      [(item["id"], item["checked"]) for item in checklist["items"]],
      [
        ("C1", True),
        ("C2", False),
        ("C3", False),
        ("C4", False),
      ],
    )

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

  def test_show_backfills_human_readable_progress_into_existing_yaml(self):
    checklist_path = (
      self.tmpdir
      / ".reviewcompass/runtime/work-units/checklists/checklist-legacy.yaml"
    )
    checklist_path.parent.mkdir(parents=True)
    checklist_path.write_text(
      yaml.safe_dump(
        {
          "schema_version": "work-checklist-v1",
          "checklist_id": "checklist-legacy",
          "unit_id": "unit-test",
          "title": "Legacy checklist",
          "status": "active",
          "created_at": "2026-06-22T00:00:00+00:00",
          "provenance": {
            "created_by": "llm",
            "source_ref": "conversation:user",
            "reason": "古い形式の補完を確認する",
          },
          "items": [
            {
              "id": "C1",
              "title": "完了済み項目",
              "status": "done",
              "child_checklist_id": None,
            },
            {
              "id": "C2",
              "title": "未完了項目",
              "status": "pending",
              "child_checklist_id": None,
            },
          ],
        },
        allow_unicode=True,
        sort_keys=False,
      ),
      encoding="utf-8",
    )

    result = run_script(
      [
        "work-checklist",
        "show",
        "--checklist-id", "checklist-legacy",
        "--json",
      ],
      cwd=self.tmpdir,
    )

    assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
    checklist = yaml.safe_load(checklist_path.read_text(encoding="utf-8"))
    self.assertEqual(checklist["progress"], {
      "total": 2,
      "done": 1,
      "active": 0,
      "pending": 1,
      "blocked": 0,
      "active_item_ids": [],
      "blocked_item_ids": [],
    })
    self.assertEqual(
      [(item["id"], item["checked"]) for item in checklist["items"]],
      [("C1", True), ("C2", False)],
    )

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
    self.assertEqual(parent["items"][0]["checked"], False)
    self.assertEqual(parent["progress"], {
      "total": 1,
      "done": 0,
      "active": 0,
      "pending": 0,
      "blocked": 1,
      "active_item_ids": [],
      "blocked_item_ids": ["C2"],
    })
    child = yaml.safe_load(
      (
        self.tmpdir
        / ".reviewcompass/runtime/work-units/checklists/checklist-child.yaml"
      ).read_text(encoding="utf-8")
    )
    self.assertEqual(child["unit_id"], "unit-test")
    self.assertEqual(child["parent_checklist_id"], "checklist-parent")
    self.assertEqual(child["parent_item_id"], "C2")
    self.assertEqual(child["progress"], {
      "total": 0,
      "done": 0,
      "active": 0,
      "pending": 0,
      "blocked": 0,
      "active_item_ids": [],
      "blocked_item_ids": [],
    })

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
    runtime_path = (
      self.tmpdir
      / ".reviewcompass/runtime/work-units/checklists/checklist-test.yaml"
    )
    self.assertFalse(runtime_path.exists())
    evidence_path = (
      self.tmpdir
      / ".reviewcompass/evidence/work-units/checklists/checklist-test.yaml"
    )
    evidence = yaml.safe_load(evidence_path.read_text(encoding="utf-8"))
    self.assertEqual(evidence["status"], "completed")
    self.assertEqual(evidence["completion_summary"], "Phase 1 red tests completed")
    self.assertEqual(evidence["progress"], {
      "total": 1,
      "done": 1,
      "active": 0,
      "pending": 0,
      "blocked": 0,
      "active_item_ids": [],
      "blocked_item_ids": [],
    })
    self.assertEqual(evidence["items"][0]["checked"], True)

  def test_audit_runtime_completed_reports_and_repairs_completed_runtime_checklist(self):
    runtime_path = (
      self.tmpdir
      / ".reviewcompass/runtime/work-units/checklists/checklist-completed.yaml"
    )
    runtime_path.parent.mkdir(parents=True)
    runtime_path.write_text(
      yaml.safe_dump(
        {
          "schema_version": "work-checklist-v1",
          "checklist_id": "checklist-completed",
          "unit_id": "unit-test",
          "title": "Completed checklist",
          "status": "completed",
          "created_at": "2026-06-22T00:00:00+00:00",
          "completed_at": "2026-06-22T00:05:00+00:00",
          "completion_summary": "already complete",
          "provenance": {
            "created_by": "llm",
            "source_ref": "conversation:user",
            "reason": "runtime completed audit",
          },
          "items": [
            {
              "id": "C1",
              "title": "done",
              "status": "done",
              "checked": True,
              "child_checklist_id": None,
            },
          ],
        },
        allow_unicode=True,
        sort_keys=False,
      ),
      encoding="utf-8",
    )

    audit = run_script(
      ["work-checklist", "audit-runtime-completed", "--json"],
      cwd=self.tmpdir,
    )
    self.assertEqual(audit.returncode, 2, audit.stdout + audit.stderr)
    self.assertIn("completed runtime checklist", audit.stdout)

    repaired = run_script(
      ["work-checklist", "audit-runtime-completed", "--repair", "--json"],
      cwd=self.tmpdir,
    )

    assert_script_invoked(self, repaired)
    self.assertEqual(repaired.returncode, 0, repaired.stdout + repaired.stderr)
    self.assertFalse(runtime_path.exists())
    evidence_path = (
      self.tmpdir
      / ".reviewcompass/evidence/work-units/checklists/checklist-completed.yaml"
    )
    self.assertTrue(evidence_path.exists())

  def test_normalize_checklist_reports_dry_run_and_writes_when_requested(self):
    checklist_path = (
      self.tmpdir
      / ".reviewcompass/runtime/work-units/checklists/checklist-legacy.yaml"
    )
    checklist_path.parent.mkdir(parents=True)
    checklist_path.write_text(
      yaml.safe_dump(
        {
          "schema_version": "work-checklist-v1",
          "checklist_id": "checklist-legacy",
          "unit_id": "unit-test",
          "title": "Legacy checklist",
          "status": "active",
          "created_at": "2026-06-22T00:00:00+00:00",
          "provenance": {
            "created_by": "llm",
            "source_ref": "conversation:user",
            "reason": "normalize audit",
          },
          "items": [
            {
              "id": "C1",
              "title": "done",
              "status": "done",
              "child_checklist_id": None,
            },
          ],
        },
        allow_unicode=True,
        sort_keys=False,
      ),
      encoding="utf-8",
    )

    dry_run = run_script(
      [
        "work-checklist",
        "normalize",
        "--checklist-id", "checklist-legacy",
        "--json",
      ],
      cwd=self.tmpdir,
    )
    self.assertEqual(dry_run.returncode, 0, dry_run.stdout + dry_run.stderr)
    data = json.loads(dry_run.stdout)
    self.assertTrue(data["changed"])
    self.assertTrue(data["dry_run"])
    unchanged = yaml.safe_load(checklist_path.read_text(encoding="utf-8"))
    self.assertNotIn("progress", unchanged)

    written = run_script(
      [
        "work-checklist",
        "normalize",
        "--checklist-id", "checklist-legacy",
        "--write",
        "--json",
      ],
      cwd=self.tmpdir,
    )

    assert_script_invoked(self, written)
    self.assertEqual(written.returncode, 0, written.stdout + written.stderr)
    normalized = yaml.safe_load(checklist_path.read_text(encoding="utf-8"))
    self.assertEqual(normalized["progress"]["done"], 1)
    self.assertTrue(normalized["items"][0]["checked"])

  def test_audit_duplicates_reports_runtime_and_evidence_overlap(self):
    runtime_path = (
      self.tmpdir
      / ".reviewcompass/runtime/work-units/checklists/checklist-dup.yaml"
    )
    evidence_path = (
      self.tmpdir
      / ".reviewcompass/evidence/work-units/checklists/checklist-dup.yaml"
    )
    for path, status in [(runtime_path, "active"), (evidence_path, "completed")]:
      path.parent.mkdir(parents=True, exist_ok=True)
      path.write_text(
        yaml.safe_dump(
          {
            "schema_version": "work-checklist-v1",
            "checklist_id": "checklist-dup",
            "unit_id": "unit-test",
            "title": "Duplicate checklist",
            "status": status,
            "created_at": "2026-06-22T00:00:00+00:00",
            "provenance": {
              "created_by": "llm",
              "source_ref": "conversation:user",
              "reason": "duplicate audit",
            },
            "items": [],
          },
          allow_unicode=True,
          sort_keys=False,
        ),
        encoding="utf-8",
      )

    result = run_script(
      ["work-checklist", "audit-duplicates", "--json"],
      cwd=self.tmpdir,
    )

    assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["duplicates"][0]["checklist_id"], "checklist-dup")
    self.assertIn("active", data["reasons"][0])

  def test_audit_close_postcondition_checks_evidence_and_runtime_state(self):
    evidence_path = (
      self.tmpdir
      / ".reviewcompass/evidence/work-units/checklists/checklist-done.yaml"
    )
    evidence_path.parent.mkdir(parents=True)
    evidence_path.write_text(
      yaml.safe_dump(
        {
          "schema_version": "work-checklist-v1",
          "checklist_id": "checklist-done",
          "unit_id": "unit-test",
          "title": "Closed checklist",
          "status": "completed",
          "created_at": "2026-06-22T00:00:00+00:00",
          "completed_at": "2026-06-22T00:05:00+00:00",
          "completion_summary": "closed",
          "provenance": {
            "created_by": "llm",
            "source_ref": "conversation:user",
            "reason": "postcondition audit",
          },
          "items": [
            {
              "id": "C1",
              "title": "done",
              "status": "done",
              "checked": True,
              "child_checklist_id": None,
            },
          ],
          "progress": {
            "total": 1,
            "done": 1,
            "active": 0,
            "pending": 0,
            "blocked": 0,
            "active_item_ids": [],
            "blocked_item_ids": [],
          },
        },
        allow_unicode=True,
        sort_keys=False,
      ),
      encoding="utf-8",
    )

    ok = run_script(
      [
        "work-checklist",
        "audit-close-postcondition",
        "--checklist-id", "checklist-done",
        "--json",
      ],
      cwd=self.tmpdir,
    )
    self.assertEqual(ok.returncode, 0, ok.stdout + ok.stderr)

    runtime_path = (
      self.tmpdir
      / ".reviewcompass/runtime/work-units/checklists/checklist-done.yaml"
    )
    runtime_path.parent.mkdir(parents=True)
    runtime_path.write_text(evidence_path.read_text(encoding="utf-8"), encoding="utf-8")
    failed = run_script(
      [
        "work-checklist",
        "audit-close-postcondition",
        "--checklist-id", "checklist-done",
        "--json",
      ],
      cwd=self.tmpdir,
    )
    self.assertEqual(failed.returncode, 2, failed.stdout + failed.stderr)
    self.assertIn("runtime checklist still exists", failed.stdout)

  def test_audit_evidence_rejects_active_or_incomplete_evidence_checklist(self):
    evidence_path = (
      self.tmpdir
      / ".reviewcompass/evidence/work-units/checklists/checklist-active.yaml"
    )
    evidence_path.parent.mkdir(parents=True)
    evidence_path.write_text(
      yaml.safe_dump(
        {
          "schema_version": "work-checklist-v1",
          "checklist_id": "checklist-active",
          "unit_id": "unit-test",
          "title": "Misplaced active checklist",
          "status": "active",
          "created_at": "2026-06-24T00:00:00+00:00",
          "provenance": {
            "created_by": "llm",
            "source_ref": "conversation:user",
            "reason": "misplaced evidence fixture",
          },
          "items": [],
        },
        allow_unicode=True,
        sort_keys=False,
      ),
      encoding="utf-8",
    )

    result = run_script(
      ["work-checklist", "audit-evidence", "--json"],
      cwd=self.tmpdir,
    )

    assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["verdict"], "DEVIATION")
    self.assertEqual(data["findings"][0]["status"], "active")
    self.assertIn("evidence checklist status must be completed", data["reasons"][0])
    self.assertIn("evidence checklist missing completed_at", data["reasons"])
    self.assertIn("evidence checklist missing completion_summary", data["reasons"])

  def test_repair_misplaced_evidence_moves_only_non_completed_checklists(self):
    active_path = (
      self.tmpdir
      / ".reviewcompass/evidence/work-units/checklists/checklist-active.yaml"
    )
    completed_path = (
      self.tmpdir
      / ".reviewcompass/evidence/work-units/checklists/checklist-completed.yaml"
    )
    active_path.parent.mkdir(parents=True)
    active_path.write_text(
      yaml.safe_dump(
        {
          "schema_version": "work-checklist-v1",
          "checklist_id": "checklist-active",
          "unit_id": "unit-test",
          "title": "Misplaced active checklist",
          "status": "active",
          "created_at": "2026-06-24T00:00:00+00:00",
          "provenance": {"created_by": "llm", "source_ref": "x", "reason": "x"},
          "items": [{"id": "A1", "title": "active", "status": "active"}],
        },
        allow_unicode=True,
        sort_keys=False,
      ),
      encoding="utf-8",
    )
    completed_path.write_text(
      yaml.safe_dump(
        {
          "schema_version": "work-checklist-v1",
          "checklist_id": "checklist-completed",
          "unit_id": "unit-test",
          "title": "Completed checklist",
          "status": "completed",
          "created_at": "2026-06-24T00:00:00+00:00",
          "completed_at": "2026-06-24T00:05:00+00:00",
          "completion_summary": "done",
          "provenance": {"created_by": "llm", "source_ref": "x", "reason": "x"},
          "items": [],
        },
        allow_unicode=True,
        sort_keys=False,
      ),
      encoding="utf-8",
    )

    result = run_script(
      [
        "work-checklist",
        "repair-misplaced-evidence",
        "--checklist-id", "checklist-active",
        "--json",
      ],
      cwd=self.tmpdir,
    )

    assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
    runtime_path = (
      self.tmpdir
      / ".reviewcompass/runtime/work-units/checklists/checklist-active.yaml"
    )
    self.assertTrue(runtime_path.exists())
    self.assertFalse(active_path.exists())
    self.assertTrue(completed_path.exists())
    moved = yaml.safe_load(runtime_path.read_text(encoding="utf-8"))
    self.assertEqual(moved["progress"]["active"], 1)

  def test_audit_reflection_requires_backlog_item_and_reference(self):
    missing = run_script(
      ["work-checklist", "audit-reflection", "--json"],
      cwd=self.tmpdir,
    )
    self.assertEqual(missing.returncode, 2, missing.stdout + missing.stderr)
    self.assertIn("backlog_id が必要です", missing.stdout)

    item_path = self.tmpdir / ".reviewcompass/backlog/todos/todo-reflect.yaml"
    item_path.parent.mkdir(parents=True)
    item_path.write_text(
      yaml.safe_dump(
        {
          "schema_version": "reviewcompass-backlog-item-v1",
          "id": "todo-reflect",
          "kind": "todo",
          "title": "Reflect checklist change",
          "status": "candidate",
        },
        allow_unicode=True,
        sort_keys=False,
      ),
      encoding="utf-8",
    )
    reference = self.tmpdir / "docs/notes/checklist-change.md"
    reference.parent.mkdir(parents=True)
    reference.write_text("checklist change reflected\n", encoding="utf-8")

    ok = run_script(
      [
        "work-checklist",
        "audit-reflection",
        "--backlog-id", "todo-reflect",
        "--reference", "docs/notes/checklist-change.md",
        "--json",
      ],
      cwd=self.tmpdir,
    )

    assert_script_invoked(self, ok)
    self.assertEqual(ok.returncode, 0, ok.stdout + ok.stderr)


if __name__ == "__main__":
  unittest.main()
