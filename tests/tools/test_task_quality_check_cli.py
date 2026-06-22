"""task-quality-check CLI tests for task/checklist derivation quality."""

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


class TaskQualityCheckCliTests(unittest.TestCase):
  def setUp(self):
    self.tmpdir = Path(tempfile.mkdtemp())
    self.addCleanup(shutil.rmtree, self.tmpdir)

  def _write_todo_item(self):
    index_path = self.tmpdir / ".reviewcompass/backlog/index.yaml"
    item_path = self.tmpdir / ".reviewcompass/backlog/todos/todo-task-quality.yaml"
    index_path.parent.mkdir(parents=True, exist_ok=True)
    item_path.parent.mkdir(parents=True, exist_ok=True)
    index = {
      "schema_version": "reviewcompass-backlog-index-v1",
      "items": [
        {
          "id": "todo-task-quality",
          "kind": "todo",
          "title": "Add task quality check",
          "status": "promoted",
          "path": ".reviewcompass/backlog/todos/todo-task-quality.yaml",
          "source_unit_id": "unit-test",
          "created_at": "2026-06-22T00:00:00+00:00",
        },
      ],
    }
    item = {
      "schema_version": "reviewcompass-backlog-item-v1",
      "id": "todo-task-quality",
      "kind": "todo",
      "title": "Add task quality check",
      "status": "promoted",
      "source_unit_id": "unit-test",
      "created_at": "2026-06-22T00:00:00+00:00",
      "index_path": ".reviewcompass/backlog/index.yaml",
      "provenance": {
        "created_by": "llm",
        "source_ref": "conversation:user",
        "reason": "task/checklist 品質を検査する",
      },
      "implementation_plan": {
        "phases": [
          {
            "id": "TQG",
            "title": "Implementation",
            "tasks": [
              {
                "id": "TQG-1",
                "title": "task-quality-check CLI の機械監査項目を追加する",
              },
              {
                "id": "TQG-2",
                "title": "checklist item の粒度と順序に関する機械ヒントを出す",
              },
            ],
          },
        ],
      },
      "todos": {
        "review": [
          {
            "id": "TQG-3",
            "title": "メイン LLM preanalysis の材料 bundle を生成する",
            "status": "candidate",
          },
        ],
      },
      "red_tests": [
        {
          "id": "TQG-RT-1",
          "title": "空項目・重複・TODO 対応漏れを検出する",
        },
      ],
    }
    index_path.write_text(
      yaml.safe_dump(index, allow_unicode=True, sort_keys=False),
      encoding="utf-8",
    )
    item_path.write_text(
      yaml.safe_dump(item, allow_unicode=True, sort_keys=False),
      encoding="utf-8",
    )

  def _write_checklist(self, items, source_backlog_item_id="todo-task-quality"):
    checklist_path = (
      self.tmpdir
      / ".reviewcompass/runtime/work-units/checklists/checklist-task-quality.yaml"
    )
    checklist_path.parent.mkdir(parents=True, exist_ok=True)
    checklist = {
      "schema_version": "work-checklist-v1",
      "checklist_id": "checklist-task-quality",
      "unit_id": "unit-test",
      "title": "Add task quality check",
      "status": "active",
      "created_at": "2026-06-22T00:00:00+00:00",
      "provenance": {
        "created_by": "llm",
        "source_ref": ".reviewcompass/backlog/todos/todo-task-quality.yaml",
        "reason": "backlog TODO から runtime checklist を機械生成する",
      },
      "items": items,
    }
    if source_backlog_item_id is not None:
      checklist["source_backlog_item_id"] = source_backlog_item_id
      checklist["source_backlog_path"] = (
        ".reviewcompass/backlog/todos/todo-task-quality.yaml"
      )
    checklist_path.write_text(
      yaml.safe_dump(checklist, allow_unicode=True, sort_keys=False),
      encoding="utf-8",
    )

  def test_audit_rejects_empty_duplicate_and_missing_todo_coverage(self):
    self._write_todo_item()
    self._write_checklist([
      {
        "id": "TQG-1",
        "title": "task-quality-check CLI の機械監査項目を追加する",
        "status": "pending",
      },
      {
        "id": "TQG-1",
        "title": "duplicate implementation item",
        "status": "pending",
      },
      {
        "id": "EMPTY",
        "title": "",
        "status": "pending",
      },
    ])

    result = run_script(
      [
        "task-quality-check",
        "audit",
        "--backlog-id", "todo-task-quality",
        "--checklist-id", "checklist-task-quality",
        "--json",
      ],
      cwd=self.tmpdir,
    )

    assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["verdict"], "DEVIATION")
    self.assertIn("duplicate item ids: TQG-1", data["reasons"])
    self.assertIn("empty item titles: EMPTY", data["reasons"])
    self.assertIn("missing backlog-derived checklist items: TQG-2, TQG-3, TQG-RT-1", data["reasons"])
    self.assertEqual(data["quality"]["missing_item_ids"], ["TQG-2", "TQG-3", "TQG-RT-1"])

  def test_audit_accepts_generated_checklist_with_backlog_source(self):
    self._write_todo_item()
    self._write_checklist([
      {
        "id": "TQG-1",
        "title": "task-quality-check CLI の機械監査項目を追加する",
        "status": "pending",
      },
      {
        "id": "TQG-2",
        "title": "checklist item の粒度と順序に関する機械ヒントを出す",
        "status": "pending",
      },
      {
        "id": "TQG-3",
        "title": "メイン LLM preanalysis の材料 bundle を生成する",
        "status": "pending",
      },
      {
        "id": "TQG-RT-1",
        "title": "空項目・重複・TODO 対応漏れを検出する",
        "status": "pending",
      },
    ])

    result = run_script(
      [
        "task-quality-check",
        "audit",
        "--backlog-id", "todo-task-quality",
        "--checklist-id", "checklist-task-quality",
        "--json",
      ],
      cwd=self.tmpdir,
    )

    assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["verdict"], "OK")
    self.assertEqual(data["quality"]["expected_count"], 4)
    self.assertEqual(data["quality"]["actual_count"], 4)
    self.assertEqual(data["quality"]["missing_item_ids"], [])


if __name__ == "__main__":
  unittest.main()
