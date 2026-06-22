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


if __name__ == "__main__":
  unittest.main()
