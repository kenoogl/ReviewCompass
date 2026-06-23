"""work-backlog CLI tests for workflow candidate backlog records."""

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


class WorkBacklogCliTests(unittest.TestCase):
  def setUp(self):
    self.tmpdir = Path(tempfile.mkdtemp())
    self.addCleanup(shutil.rmtree, self.tmpdir)

  def _write_todo_item(self, item_id="todo-bridge", status="candidate"):
    index_path = self.tmpdir / ".reviewcompass/backlog/index.yaml"
    item_path = self.tmpdir / f".reviewcompass/backlog/todos/{item_id}.yaml"
    index_path.parent.mkdir(parents=True, exist_ok=True)
    item_path.parent.mkdir(parents=True, exist_ok=True)
    index = {
      "schema_version": "reviewcompass-backlog-index-v1",
      "items": [
        {
          "id": item_id,
          "kind": "todo",
          "title": "Bridge backlog TODO to checklist",
          "status": status,
          "path": f".reviewcompass/backlog/todos/{item_id}.yaml",
          "source_unit_id": "unit-test",
          "created_at": "2026-06-22T00:00:00+00:00",
        },
      ],
    }
    item = {
      "schema_version": "reviewcompass-backlog-item-v1",
      "id": item_id,
      "kind": "todo",
      "title": "Bridge backlog TODO to checklist",
      "status": status,
      "source_unit_id": "unit-test",
      "created_at": "2026-06-22T00:00:00+00:00",
      "index_path": ".reviewcompass/backlog/index.yaml",
      "provenance": {
        "created_by": "llm",
        "source_ref": "conversation:user",
        "reason": "分断を検査する",
      },
      "implementation_plan": {
        "phases": [
          {
            "id": "P1",
            "title": "red tests",
            "tasks": [
              "TODO から checklist を生成する",
              "close 後に backlog へ履歴を戻す",
            ],
          },
        ],
      },
      "todos": {
        "cli": [
          {
            "id": "BCB-3",
            "title": "work-backlog start-checklist 導線を追加する",
            "status": "candidate",
          },
        ],
      },
      "red_tests": [
        {
          "id": "BCB-RT-1",
          "title": "backlog TODO から checklist を生成する",
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
    return item_path

  def _write_plan_item(self, item_id="plan-bridge", status="candidate"):
    index_path = self.tmpdir / ".reviewcompass/backlog/index.yaml"
    item_path = self.tmpdir / f".reviewcompass/backlog/plans/{item_id}.yaml"
    index_path.parent.mkdir(parents=True, exist_ok=True)
    item_path.parent.mkdir(parents=True, exist_ok=True)
    index = {
      "schema_version": "reviewcompass-backlog-index-v1",
      "items": [
        {
          "id": item_id,
          "kind": "plan",
          "title": "Plan to bridge into TODO",
          "status": status,
          "path": f".reviewcompass/backlog/plans/{item_id}.yaml",
          "source_unit_id": "unit-test",
          "created_at": "2026-06-23T00:00:00+00:00",
        },
      ],
    }
    item = {
      "schema_version": "reviewcompass-backlog-item-v1",
      "id": item_id,
      "kind": "plan",
      "title": "Plan to bridge into TODO",
      "status": status,
      "source_unit_id": "unit-test",
      "created_at": "2026-06-23T00:00:00+00:00",
      "index_path": ".reviewcompass/backlog/index.yaml",
      "provenance": {
        "created_by": "llm",
        "source_ref": "conversation:user",
        "reason": "plan から TODO への証跡を検査する",
      },
      "implementation_plan": {
        "phases": [
          {
            "id": "P1",
            "title": "plan work",
            "tasks": [
              "plan の作業を TODO 化する",
            ],
          },
        ],
      },
    }
    index_path.write_text(
      yaml.safe_dump(index, allow_unicode=True, sort_keys=False),
      encoding="utf-8",
    )
    item_path.write_text(
      yaml.safe_dump(item, allow_unicode=True, sort_keys=False),
      encoding="utf-8",
    )
    return item_path

  def test_add_plan_creates_index_and_item_yaml(self):
    result = run_script(
      [
        "work-backlog",
        "add-plan",
        "--id", "plan-test",
        "--title", "checklist 機構導入計画",
        "--source-unit-id", "unit-test",
        "--source-ref", "conversation:user",
        "--reason", "workflow に乗せる前の計画候補",
        "--json",
      ],
      cwd=self.tmpdir,
    )

    assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["verdict"], "OK")
    self.assertEqual(data["item"]["id"], "plan-test")

    index_path = self.tmpdir / ".reviewcompass/backlog/index.yaml"
    index = yaml.safe_load(index_path.read_text(encoding="utf-8"))
    self.assertEqual(index["schema_version"], "reviewcompass-backlog-index-v1")
    self.assertEqual(index["items"], [
      {
        "id": "plan-test",
        "kind": "plan",
        "title": "checklist 機構導入計画",
        "status": "candidate",
        "path": ".reviewcompass/backlog/plans/plan-test.yaml",
        "source_unit_id": "unit-test",
        "created_at": index["items"][0]["created_at"],
      }
    ])

    item_path = self.tmpdir / ".reviewcompass/backlog/plans/plan-test.yaml"
    item = yaml.safe_load(item_path.read_text(encoding="utf-8"))
    self.assertEqual(item["schema_version"], "reviewcompass-backlog-item-v1")
    self.assertEqual(item["id"], "plan-test")
    self.assertEqual(item["kind"], "plan")
    self.assertEqual(item["status"], "candidate")
    self.assertEqual(item["index_path"], ".reviewcompass/backlog/index.yaml")
    self.assertEqual(item["provenance"]["created_by"], "llm")
    self.assertEqual(item["provenance"]["source_ref"], "conversation:user")
    self.assertEqual(item["provenance"]["reason"], "workflow に乗せる前の計画候補")

  def test_add_plan_accepts_body_file_for_concrete_plan_fields(self):
    body_path = self.tmpdir / "plan-body.yaml"
    body_path.write_text(
      yaml.safe_dump(
        {
          "summary": "blocking unit control improvements",
          "background": [
            "completed state hid a pending parent resume",
          ],
          "problem": [
            "return conditions were plain strings",
          ],
          "implementation_plan": [
            {
              "phase": "red-test",
              "items": ["add preflight-start tests"],
            },
          ],
          "acceptance_criteria": [
            "exit-blocking rejects unmet structured return conditions",
          ],
          "non_goals": [
            "do not solve full natural language classification",
          ],
        },
        allow_unicode=True,
        sort_keys=False,
      ),
      encoding="utf-8",
    )

    result = run_script(
      [
        "work-backlog",
        "add-plan",
        "--id", "plan-detailed",
        "--title", "Detailed plan",
        "--source-unit-id", "unit-test",
        "--source-ref", "conversation:user",
        "--reason", "詳細計画を backlog item に保持する",
        "--body-file", str(body_path),
        "--json",
      ],
      cwd=self.tmpdir,
    )

    assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
    item = yaml.safe_load(
      (
        self.tmpdir
        / ".reviewcompass/backlog/plans/plan-detailed.yaml"
      ).read_text(encoding="utf-8")
    )
    self.assertEqual(item["summary"], "blocking unit control improvements")
    self.assertEqual(item["background"], [
      "completed state hid a pending parent resume",
    ])
    self.assertEqual(item["problem"], [
      "return conditions were plain strings",
    ])
    self.assertEqual(item["implementation_plan"][0]["phase"], "red-test")
    self.assertEqual(item["acceptance_criteria"], [
      "exit-blocking rejects unmet structured return conditions",
    ])
    self.assertEqual(item["non_goals"], [
      "do not solve full natural language classification",
    ])

  def test_add_issue_and_todo_create_kind_specific_item_yaml(self):
    for command, item_id, kind, directory in [
      ("add-issue", "issue-test", "issue", "issues"),
      ("add-todo", "todo-test", "todo", "todos"),
    ]:
      result = run_script(
        [
          "work-backlog",
          command,
          "--id", item_id,
          "--title", f"{kind} candidate",
          "--source-unit-id", "unit-test",
          "--source-ref", "conversation:user",
          "--reason", f"{kind} を後で検討する",
          "--json",
        ],
        cwd=self.tmpdir,
      )

      assert_script_invoked(self, result)
      self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
      item_path = self.tmpdir / f".reviewcompass/backlog/{directory}/{item_id}.yaml"
      item = yaml.safe_load(item_path.read_text(encoding="utf-8"))
      self.assertEqual(item["kind"], kind)
      self.assertEqual(item["status"], "candidate")
      self.assertEqual(item["index_path"], ".reviewcompass/backlog/index.yaml")

    index = yaml.safe_load(
      (self.tmpdir / ".reviewcompass/backlog/index.yaml").read_text(encoding="utf-8")
    )
    self.assertEqual(
      [(item["id"], item["kind"], item["path"]) for item in index["items"]],
      [
        ("issue-test", "issue", ".reviewcompass/backlog/issues/issue-test.yaml"),
        ("todo-test", "todo", ".reviewcompass/backlog/todos/todo-test.yaml"),
      ],
    )

  def test_add_todo_accepts_body_file_for_plan_linkage(self):
    body_path = self.tmpdir / "todo-body.yaml"
    body_path.write_text(
      yaml.safe_dump(
        {
          "source_plan_id": "plan-source",
          "source_plan_path": ".reviewcompass/backlog/plans/plan-source.yaml",
          "implementation_plan": {
            "phases": [
              {
                "id": "GRC-1",
                "title": "Inventory only",
                "tasks": [
                  "docs/operations と docs/disciplines を一覧化する",
                ],
              },
            ],
          },
          "acceptance_criteria": [
            "inventory table exists without moving files",
          ],
        },
        allow_unicode=True,
        sort_keys=False,
      ),
      encoding="utf-8",
    )

    result = run_script(
      [
        "work-backlog",
        "add-todo",
        "--id", "todo-from-plan",
        "--title", "Create inventory table",
        "--source-unit-id", "main-completed",
        "--source-ref", ".reviewcompass/backlog/plans/plan-source.yaml",
        "--reason", "plan の GRC-1 を実行対象化する",
        "--body-file", str(body_path),
        "--json",
      ],
      cwd=self.tmpdir,
    )

    assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
    item = yaml.safe_load(
      (
        self.tmpdir
        / ".reviewcompass/backlog/todos/todo-from-plan.yaml"
      ).read_text(encoding="utf-8")
    )
    self.assertEqual(item["source_plan_id"], "plan-source")
    self.assertEqual(
      item["source_plan_path"],
      ".reviewcompass/backlog/plans/plan-source.yaml",
    )
    self.assertEqual(item["implementation_plan"]["phases"][0]["id"], "GRC-1")

  def test_show_and_list_read_backlog_records(self):
    add = run_script(
      [
        "work-backlog",
        "add-plan",
        "--id", "plan-test",
        "--title", "checklist 機構導入計画",
        "--source-unit-id", "unit-test",
        "--source-ref", "conversation:user",
        "--reason", "workflow に乗せる前の計画候補",
        "--json",
      ],
      cwd=self.tmpdir,
    )
    self.assertEqual(add.returncode, 0, add.stdout + add.stderr)

    list_result = run_script(["work-backlog", "list", "--json"], cwd=self.tmpdir)
    show_result = run_script(
      ["work-backlog", "show", "--id", "plan-test", "--json"],
      cwd=self.tmpdir,
    )

    assert_script_invoked(self, list_result)
    assert_script_invoked(self, show_result)
    self.assertEqual(list_result.returncode, 0, list_result.stdout + list_result.stderr)
    self.assertEqual(show_result.returncode, 0, show_result.stdout + show_result.stderr)
    listed = json.loads(list_result.stdout)
    shown = json.loads(show_result.stdout)
    self.assertEqual(listed["index"]["items"][0]["id"], "plan-test")
    self.assertEqual(shown["item"]["id"], "plan-test")
    self.assertEqual(shown["item"]["index_path"], ".reviewcompass/backlog/index.yaml")

  def test_promote_and_reject_record_decision_history(self):
    for item_id in ("plan-promote", "todo-reject"):
      add = run_script(
        [
          "work-backlog",
          "add-plan" if item_id == "plan-promote" else "add-todo",
          "--id", item_id,
          "--title", item_id,
          "--source-unit-id", "unit-test",
          "--source-ref", "conversation:user",
          "--reason", "判断履歴を検査する",
          "--json",
        ],
        cwd=self.tmpdir,
      )
      self.assertEqual(add.returncode, 0, add.stdout + add.stderr)

    promoted = run_script(
      [
        "work-backlog",
        "promote",
        "--id", "plan-promote",
        "--decision-ref", "conversation:user",
        "--reason", "正式 workflow に進める",
        "--json",
      ],
      cwd=self.tmpdir,
    )
    rejected = run_script(
      [
        "work-backlog",
        "reject",
        "--id", "todo-reject",
        "--decision-ref", "conversation:user",
        "--reason", "今回は扱わない",
        "--json",
      ],
      cwd=self.tmpdir,
    )

    assert_script_invoked(self, promoted)
    assert_script_invoked(self, rejected)
    self.assertEqual(promoted.returncode, 0, promoted.stdout + promoted.stderr)
    self.assertEqual(rejected.returncode, 0, rejected.stdout + rejected.stderr)
    promoted_item = yaml.safe_load(
      (self.tmpdir / ".reviewcompass/backlog/plans/plan-promote.yaml").read_text(
        encoding="utf-8",
      )
    )
    rejected_item = yaml.safe_load(
      (self.tmpdir / ".reviewcompass/backlog/todos/todo-reject.yaml").read_text(
        encoding="utf-8",
      )
    )
    self.assertEqual(promoted_item["status"], "promoted")
    self.assertEqual(promoted_item["decisions"][-1]["decision"], "promoted")
    self.assertEqual(promoted_item["decisions"][-1]["reason"], "正式 workflow に進める")
    self.assertEqual(rejected_item["status"], "rejected")
    self.assertEqual(rejected_item["decisions"][-1]["decision"], "rejected")
    self.assertEqual(rejected_item["decisions"][-1]["reason"], "今回は扱わない")

    index = yaml.safe_load(
      (self.tmpdir / ".reviewcompass/backlog/index.yaml").read_text(encoding="utf-8")
    )
    self.assertEqual(
      [(item["id"], item["status"]) for item in index["items"]],
      [("plan-promote", "promoted"), ("todo-reject", "rejected")],
    )

  def test_complete_records_decision_history_and_updates_index(self):
    add = run_script(
      [
        "work-backlog",
        "add-todo",
        "--id", "todo-complete",
        "--title", "completed backlog item",
        "--source-unit-id", "unit-test",
        "--source-ref", "conversation:user",
        "--reason", "完了操作を検査する",
        "--json",
      ],
      cwd=self.tmpdir,
    )
    self.assertEqual(add.returncode, 0, add.stdout + add.stderr)

    completed = run_script(
      [
        "work-backlog",
        "complete",
        "--id", "todo-complete",
        "--decision-ref", "git:abc1234",
        "--reason", "既存 commit で完了済み",
        "--json",
      ],
      cwd=self.tmpdir,
    )

    assert_script_invoked(self, completed)
    self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
    item = yaml.safe_load(
      (
        self.tmpdir
        / ".reviewcompass/backlog/todos/todo-complete.yaml"
      ).read_text(encoding="utf-8")
    )
    index = yaml.safe_load(
      (self.tmpdir / ".reviewcompass/backlog/index.yaml").read_text(
        encoding="utf-8",
      )
    )
    self.assertEqual(item["status"], "completed")
    self.assertEqual(item["decisions"][-1]["decision"], "completed")
    self.assertEqual(item["decisions"][-1]["decision_ref"], "git:abc1234")
    self.assertEqual(item["decisions"][-1]["reason"], "既存 commit で完了済み")
    self.assertEqual(index["items"][0]["status"], "completed")

  def test_start_checklist_generates_runtime_checklist_from_backlog_todo(self):
    self._write_todo_item()

    result = run_script(
      [
        "work-backlog",
        "start-checklist",
        "--id", "todo-bridge",
        "--checklist-id", "checklist-bridge",
        "--unit-id", "unit-test",
        "--json",
      ],
      cwd=self.tmpdir,
    )

    assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["verdict"], "OK")
    checklist_path = (
      self.tmpdir
      / ".reviewcompass/runtime/work-units/checklists/checklist-bridge.yaml"
    )
    checklist = yaml.safe_load(checklist_path.read_text(encoding="utf-8"))
    self.assertEqual(checklist["source_backlog_item_id"], "todo-bridge")
    self.assertEqual(
      checklist["source_backlog_path"],
      ".reviewcompass/backlog/todos/todo-bridge.yaml",
    )
    self.assertEqual(
      [(item["id"], item["title"], item["status"]) for item in checklist["items"]],
      [
        ("P1-1", "TODO から checklist を生成する", "pending"),
        ("P1-2", "close 後に backlog へ履歴を戻す", "pending"),
        ("BCB-3", "work-backlog start-checklist 導線を追加する", "pending"),
        ("BCB-RT-1", "backlog TODO から checklist を生成する", "pending"),
      ],
    )

  def test_start_checklist_generates_items_from_top_level_tasks(self):
    item_path = self._write_todo_item(item_id="todo-tasks")
    item = yaml.safe_load(item_path.read_text(encoding="utf-8"))
    item.pop("implementation_plan")
    item.pop("todos")
    item.pop("red_tests")
    item["tasks"] = [
      {
        "id": "T1",
        "title": "top-level task を checklist item にする",
        "status": "candidate",
      },
      {
        "id": "T2",
        "title": "二つ目の task も保持する",
        "status": "candidate",
      },
    ]
    item_path.write_text(
      yaml.safe_dump(item, allow_unicode=True, sort_keys=False),
      encoding="utf-8",
    )

    result = run_script(
      [
        "work-backlog",
        "start-checklist",
        "--id", "todo-tasks",
        "--checklist-id", "checklist-tasks",
        "--unit-id", "unit-test",
        "--json",
      ],
      cwd=self.tmpdir,
    )

    assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
    checklist = yaml.safe_load(
      (
        self.tmpdir
        / ".reviewcompass/runtime/work-units/checklists/checklist-tasks.yaml"
      ).read_text(encoding="utf-8")
    )
    self.assertEqual(
      [(item["id"], item["title"]) for item in checklist["items"]],
      [
        ("T1", "top-level task を checklist item にする"),
        ("T2", "二つ目の task も保持する"),
      ],
    )

  def test_checklist_close_marks_top_level_tasks_done(self):
    item_path = self._write_todo_item(item_id="todo-tasks")
    item = yaml.safe_load(item_path.read_text(encoding="utf-8"))
    item.pop("implementation_plan")
    item.pop("todos")
    item.pop("red_tests")
    item["tasks"] = [
      {
        "id": "T1",
        "title": "top-level task を完了に戻す",
        "status": "candidate",
      },
    ]
    item_path.write_text(
      yaml.safe_dump(item, allow_unicode=True, sort_keys=False),
      encoding="utf-8",
    )
    start = run_script(
      [
        "work-backlog",
        "start-checklist",
        "--id", "todo-tasks",
        "--checklist-id", "checklist-tasks",
        "--unit-id", "unit-test",
        "--json",
      ],
      cwd=self.tmpdir,
    )
    self.assertEqual(start.returncode, 0, start.stdout + start.stderr)
    done = run_script(
      [
        "work-checklist",
        "set-status",
        "--checklist-id", "checklist-tasks",
        "--item-id", "T1",
        "--status", "done",
        "--json",
      ],
      cwd=self.tmpdir,
    )
    self.assertEqual(done.returncode, 0, done.stdout + done.stderr)

    closed = run_script(
      [
        "work-checklist",
        "close",
        "--checklist-id", "checklist-tasks",
        "--completion-summary", "top-level tasks complete",
        "--json",
      ],
      cwd=self.tmpdir,
    )

    self.assertEqual(closed.returncode, 0, closed.stdout + closed.stderr)
    completed = yaml.safe_load(item_path.read_text(encoding="utf-8"))
    self.assertEqual(completed["tasks"][0]["status"], "done")

  def test_checklist_close_records_evidence_back_to_source_backlog_todo(self):
    self._write_todo_item()
    start = run_script(
      [
        "work-backlog",
        "start-checklist",
        "--id", "todo-bridge",
        "--checklist-id", "checklist-bridge",
        "--unit-id", "unit-test",
        "--json",
      ],
      cwd=self.tmpdir,
    )
    self.assertEqual(start.returncode, 0, start.stdout + start.stderr)
    for item_id in ("P1-1", "P1-2", "BCB-3", "BCB-RT-1"):
      result = run_script(
        [
          "work-checklist",
          "set-status",
          "--checklist-id", "checklist-bridge",
          "--item-id", item_id,
          "--status", "done",
          "--json",
        ],
        cwd=self.tmpdir,
      )
      self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    result = run_script(
      [
        "work-checklist",
        "close",
        "--checklist-id", "checklist-bridge",
        "--completion-summary", "bridge checklist completed",
        "--json",
      ],
      cwd=self.tmpdir,
    )

    assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
    item = yaml.safe_load(
      (
        self.tmpdir
        / ".reviewcompass/backlog/todos/todo-bridge.yaml"
      ).read_text(encoding="utf-8")
    )
    self.assertEqual(item["execution_history"][-1]["checklist_id"], "checklist-bridge")
    self.assertEqual(
      item["execution_history"][-1]["evidence_path"],
      ".reviewcompass/evidence/work-units/checklists/checklist-bridge.yaml",
    )
    self.assertEqual(
      item["execution_history"][-1]["completion_summary"],
      "bridge checklist completed",
    )

  def test_checklist_close_marks_source_backlog_todo_completed(self):
    self._write_todo_item(status="promoted")
    start = run_script(
      [
        "work-backlog",
        "start-checklist",
        "--id", "todo-bridge",
        "--checklist-id", "checklist-bridge",
        "--unit-id", "unit-test",
        "--json",
      ],
      cwd=self.tmpdir,
    )
    self.assertEqual(start.returncode, 0, start.stdout + start.stderr)
    for item_id in ("P1-1", "P1-2", "BCB-3", "BCB-RT-1"):
      result = run_script(
        [
          "work-checklist",
          "set-status",
          "--checklist-id", "checklist-bridge",
          "--item-id", item_id,
          "--status", "done",
          "--json",
        ],
        cwd=self.tmpdir,
      )
      self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    result = run_script(
      [
        "work-checklist",
        "close",
        "--checklist-id", "checklist-bridge",
        "--completion-summary", "bridge checklist completed",
        "--json",
      ],
      cwd=self.tmpdir,
    )

    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
    item = yaml.safe_load(
      (
        self.tmpdir
        / ".reviewcompass/backlog/todos/todo-bridge.yaml"
      ).read_text(encoding="utf-8")
    )
    index = yaml.safe_load(
      (self.tmpdir / ".reviewcompass/backlog/index.yaml").read_text(
        encoding="utf-8",
      )
    )
    self.assertEqual(item["status"], "completed")
    self.assertEqual(index["items"][0]["status"], "completed")

    second_start = run_script(
      ["work-backlog", "start-checklist", "--json"],
      cwd=self.tmpdir,
    )
    self.assertEqual(second_start.returncode, 2, second_start.stdout)
    data = json.loads(second_start.stdout)
    self.assertIn("no promoted todo item found", data["reasons"])

  def test_checklist_close_requires_backlog_index_completion_update(self):
    self._write_todo_item(status="promoted")
    start = run_script(
      [
        "work-backlog",
        "start-checklist",
        "--id", "todo-bridge",
        "--checklist-id", "checklist-bridge",
        "--unit-id", "unit-test",
        "--json",
      ],
      cwd=self.tmpdir,
    )
    self.assertEqual(start.returncode, 0, start.stdout + start.stderr)
    index_path = self.tmpdir / ".reviewcompass/backlog/index.yaml"
    index = yaml.safe_load(index_path.read_text(encoding="utf-8"))
    index["items"] = []
    index_path.write_text(
      yaml.safe_dump(index, allow_unicode=True, sort_keys=False),
      encoding="utf-8",
    )
    for item_id in ("P1-1", "P1-2", "BCB-3", "BCB-RT-1"):
      result = run_script(
        [
          "work-checklist",
          "set-status",
          "--checklist-id", "checklist-bridge",
          "--item-id", item_id,
          "--status", "done",
          "--json",
        ],
        cwd=self.tmpdir,
      )
      self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    result = run_script(
      [
        "work-checklist",
        "close",
        "--checklist-id", "checklist-bridge",
        "--completion-summary", "bridge checklist completed",
        "--json",
      ],
      cwd=self.tmpdir,
    )

    self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["verdict"], "DEVIATION")
    self.assertIn("backlog index item not found: todo-bridge", data["reasons"])

  def test_audit_checklist_bridge_rejects_promoted_todo_without_runtime_or_evidence(self):
    self._write_todo_item(status="promoted")

    result = run_script(
      [
        "work-backlog",
        "audit-checklist-bridge",
        "--json",
      ],
      cwd=self.tmpdir,
    )

    assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["verdict"], "DEVIATION")
    self.assertIn("todo-bridge", data["reasons"][0])

  def test_audit_plan_todo_bridge_rejects_promoted_plan_without_todo_or_checklist(self):
    self._write_plan_item(status="promoted")

    result = run_script(
      [
        "work-backlog",
        "audit-plan-todo-bridge",
        "--json",
      ],
      cwd=self.tmpdir,
    )

    assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["verdict"], "DEVIATION")
    self.assertIn("plan-bridge has no linked TODO/checklist evidence", data["reasons"][0])

  def test_plan_todo_bridge_rejects_plan_without_linked_todo_and_suggests_creation(self):
    self._write_plan_item()

    result = run_script(
      [
        "work-backlog",
        "plan-todo-bridge",
        "--plan-id", "plan-bridge",
        "--json",
      ],
      cwd=self.tmpdir,
    )

    assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["verdict"], "DEVIATION")
    self.assertIn("linked backlog TODO not found", data["reasons"])
    self.assertEqual(data["plan"]["id"], "plan-bridge")
    self.assertEqual(data["linked_todo_ids"], [])
    self.assertIn("work-backlog add-todo", data["next_steps"][0])
    self.assertIn("source_plan_id", data["next_steps"][0])

  def test_plan_todo_bridge_accepts_linked_todo_and_suggests_checklist_audit_flow(self):
    self._write_plan_item()
    todo_path = self._write_todo_item(item_id="todo-from-plan")
    todo = yaml.safe_load(todo_path.read_text(encoding="utf-8"))
    todo["source_plan_id"] = "plan-bridge"
    todo["source_plan_path"] = ".reviewcompass/backlog/plans/plan-bridge.yaml"
    todo_path.write_text(
      yaml.safe_dump(todo, allow_unicode=True, sort_keys=False),
      encoding="utf-8",
    )
    index_path = self.tmpdir / ".reviewcompass/backlog/index.yaml"
    index = yaml.safe_load(index_path.read_text(encoding="utf-8"))
    index["items"].insert(0, {
      "id": "plan-bridge",
      "kind": "plan",
      "title": "Plan to bridge into TODO",
      "status": "candidate",
      "path": ".reviewcompass/backlog/plans/plan-bridge.yaml",
      "source_unit_id": "unit-test",
      "created_at": "2026-06-23T00:00:00+00:00",
    })
    index_path.write_text(
      yaml.safe_dump(index, allow_unicode=True, sort_keys=False),
      encoding="utf-8",
    )

    result = run_script(
      [
        "work-backlog",
        "plan-todo-bridge",
        "--plan-id", "plan-bridge",
        "--json",
      ],
      cwd=self.tmpdir,
    )

    assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["verdict"], "OK")
    self.assertEqual(data["linked_todo_ids"], ["todo-from-plan"])
    self.assertIn(
      "work-backlog start-checklist --id todo-from-plan",
      data["next_steps"][0],
    )
    self.assertIn(
      "work-backlog audit-checklist-coverage --id todo-from-plan",
      data["next_steps"][1],
    )

  def test_start_checklist_derives_ids_from_backlog_todo_and_active_unit(self):
    self._write_todo_item()
    stack_path = self.tmpdir / ".reviewcompass/runtime/work-units/stack.yaml"
    stack_path.parent.mkdir(parents=True, exist_ok=True)
    stack_path.write_text(
      yaml.safe_dump(
        {
          "schema_version": "work-unit-stack-v1",
          "frames": [
            {
              "unit_id": "unit-active",
              "kind": "blocking",
              "status": "active",
              "title": "Active unit",
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
        "work-backlog",
        "start-checklist",
        "--id", "todo-bridge",
        "--json",
      ],
      cwd=self.tmpdir,
    )

    assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
    checklist = yaml.safe_load(
      (
        self.tmpdir
        / ".reviewcompass/runtime/work-units/checklists/checklist-todo-bridge.yaml"
      ).read_text(encoding="utf-8")
    )
    self.assertEqual(checklist["checklist_id"], "checklist-todo-bridge")
    self.assertEqual(checklist["unit_id"], "unit-active")

  def test_start_checklist_without_id_selects_single_promoted_todo(self):
    self._write_todo_item(item_id="todo-promoted", status="promoted")

    result = run_script(
      [
        "work-backlog",
        "start-checklist",
        "--json",
      ],
      cwd=self.tmpdir,
    )

    assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
    checklist = yaml.safe_load(
      (
        self.tmpdir
        / ".reviewcompass/runtime/work-units/checklists/checklist-todo-promoted.yaml"
      ).read_text(encoding="utf-8")
    )
    self.assertEqual(checklist["source_backlog_item_id"], "todo-promoted")

  def test_start_checklist_without_id_rejects_multiple_promoted_todos(self):
    first = self._write_todo_item(item_id="todo-one", status="promoted")
    second = self.tmpdir / ".reviewcompass/backlog/todos/todo-two.yaml"
    second.write_text(
      first.read_text(encoding="utf-8")
      .replace("todo-one", "todo-two")
      .replace("Bridge backlog TODO to checklist", "Second promoted TODO"),
      encoding="utf-8",
    )
    index = yaml.safe_load(
      (self.tmpdir / ".reviewcompass/backlog/index.yaml").read_text(encoding="utf-8")
    )
    index["items"].append({
      "id": "todo-two",
      "kind": "todo",
      "title": "Second promoted TODO",
      "status": "promoted",
      "path": ".reviewcompass/backlog/todos/todo-two.yaml",
      "source_unit_id": "unit-test",
      "created_at": "2026-06-22T00:00:00+00:00",
    })
    (self.tmpdir / ".reviewcompass/backlog/index.yaml").write_text(
      yaml.safe_dump(index, allow_unicode=True, sort_keys=False),
      encoding="utf-8",
    )

    result = run_script(
      [
        "work-backlog",
        "start-checklist",
        "--json",
      ],
      cwd=self.tmpdir,
    )

    assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
    data = json.loads(result.stdout)
    self.assertIn("multiple promoted todo items", data["reasons"][0])

  def test_checklist_close_marks_matching_backlog_todo_items_done(self):
    self._write_todo_item()
    start = run_script(
      [
        "work-backlog",
        "start-checklist",
        "--id", "todo-bridge",
        "--checklist-id", "checklist-bridge",
        "--unit-id", "unit-test",
        "--json",
      ],
      cwd=self.tmpdir,
    )
    self.assertEqual(start.returncode, 0, start.stdout + start.stderr)
    for item_id in ("P1-1", "P1-2", "BCB-3", "BCB-RT-1"):
      result = run_script(
        [
          "work-checklist",
          "set-status",
          "--checklist-id", "checklist-bridge",
          "--item-id", item_id,
          "--status", "done",
          "--json",
        ],
        cwd=self.tmpdir,
      )
      self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    result = run_script(
      [
        "work-checklist",
        "close",
        "--checklist-id", "checklist-bridge",
        "--completion-summary", "bridge checklist completed",
        "--json",
      ],
      cwd=self.tmpdir,
    )

    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
    item = yaml.safe_load(
      (
        self.tmpdir
        / ".reviewcompass/backlog/todos/todo-bridge.yaml"
      ).read_text(encoding="utf-8")
    )
    self.assertEqual(item["todos"]["cli"][0]["status"], "done")
    self.assertEqual(item["red_tests"][0]["status"], "done")

  def test_audit_checklist_coverage_rejects_missing_generated_items(self):
    self._write_todo_item()
    checklist_dir = self.tmpdir / ".reviewcompass/runtime/work-units/checklists"
    checklist_dir.mkdir(parents=True, exist_ok=True)
    (checklist_dir / "checklist-bridge.yaml").write_text(
      yaml.safe_dump(
        {
          "schema_version": "work-checklist-v1",
          "checklist_id": "checklist-bridge",
          "unit_id": "unit-test",
          "title": "Bridge backlog TODO to checklist",
          "status": "active",
          "created_at": "2026-06-22T00:00:00+00:00",
          "source_backlog_item_id": "todo-bridge",
          "source_backlog_path": ".reviewcompass/backlog/todos/todo-bridge.yaml",
          "provenance": {
            "created_by": "llm",
            "source_ref": ".reviewcompass/backlog/todos/todo-bridge.yaml",
            "reason": "coverage test",
          },
          "items": [
            {
              "id": "P1-1",
              "title": "TODO から checklist を生成する",
              "status": "pending",
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
        "work-backlog",
        "audit-checklist-coverage",
        "--id", "todo-bridge",
        "--checklist-id", "checklist-bridge",
        "--json",
      ],
      cwd=self.tmpdir,
    )

    assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["verdict"], "DEVIATION")
    self.assertIn("missing checklist items", data["reasons"][0])

  def test_audit_checklist_coverage_accepts_generated_checklist(self):
    self._write_todo_item()
    start = run_script(
      [
        "work-backlog",
        "start-checklist",
        "--id", "todo-bridge",
        "--checklist-id", "checklist-bridge",
        "--unit-id", "unit-test",
        "--json",
      ],
      cwd=self.tmpdir,
    )
    self.assertEqual(start.returncode, 0, start.stdout + start.stderr)

    result = run_script(
      [
        "work-backlog",
        "audit-checklist-coverage",
        "--id", "todo-bridge",
        "--checklist-id", "checklist-bridge",
        "--json",
      ],
      cwd=self.tmpdir,
    )

    assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["coverage"]["expected_count"], 4)
    self.assertEqual(data["coverage"]["missing_item_ids"], [])

  def test_checklist_close_generates_completion_summary_when_omitted(self):
    self._write_todo_item()
    start = run_script(
      [
        "work-backlog",
        "start-checklist",
        "--id", "todo-bridge",
        "--checklist-id", "checklist-bridge",
        "--unit-id", "unit-test",
        "--json",
      ],
      cwd=self.tmpdir,
    )
    self.assertEqual(start.returncode, 0, start.stdout + start.stderr)
    for item_id in ("P1-1", "P1-2", "BCB-3", "BCB-RT-1"):
      result = run_script(
        [
          "work-checklist",
          "set-status",
          "--checklist-id", "checklist-bridge",
          "--item-id", item_id,
          "--status", "done",
          "--json",
        ],
        cwd=self.tmpdir,
      )
      self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    result = run_script(
      [
        "work-checklist",
        "close",
        "--checklist-id", "checklist-bridge",
        "--json",
      ],
      cwd=self.tmpdir,
    )

    assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
    evidence = yaml.safe_load(
      (
        self.tmpdir
        / ".reviewcompass/evidence/work-units/checklists/checklist-bridge.yaml"
      ).read_text(encoding="utf-8")
    )
    self.assertEqual(
      evidence["completion_summary"],
      "checklist-bridge completed 4/4 items",
    )


if __name__ == "__main__":
  unittest.main()
