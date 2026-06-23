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

  def test_audit_reports_missing_red_test_items_as_specific_deviation(self):
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
    self.assertIn("missing red test checklist items: TQG-RT-1", data["reasons"])
    self.assertEqual(data["quality"]["missing_red_test_item_ids"], ["TQG-RT-1"])

  def test_audit_warns_when_red_tests_are_after_implementation_items(self):
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
    self.assertIn(
      "red test items appear after implementation items: TQG-RT-1",
      data["warnings"],
    )
    self.assertEqual(data["quality"]["ordering_warning_item_ids"], ["TQG-RT-1"])

  def test_prepare_review_materials_writes_embedded_sources_and_split_questions(self):
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
    output_dir = (
      self.tmpdir
      / ".reviewcompass/runtime/task-quality-review-materials/run"
    )

    result = run_script(
      [
        "task-quality-check",
        "prepare-review-materials",
        "--backlog-id", "todo-task-quality",
        "--checklist-id", "checklist-task-quality",
        "--output-dir", str(output_dir),
        "--json",
      ],
      cwd=self.tmpdir,
    )

    assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["verdict"], "OK")
    materials_path = Path(data["materials_path"])
    self.assertTrue(materials_path.is_file())
    materials = yaml.safe_load(materials_path.read_text(encoding="utf-8"))
    self.assertEqual(
      materials["schema_version"],
      "task-quality-review-materials-v1",
    )
    source_materials = materials["source_materials"]
    self.assertEqual(
      [entry["content_mode"] for entry in source_materials],
      ["full_text", "full_text"],
    )
    self.assertIn("Add task quality check", source_materials[0]["content"])
    self.assertIn("checklist-task-quality", source_materials[1]["content"])
    self.assertEqual(materials["audit_result"]["verdict"], "OK")
    self.assertIn("data_sources", materials["main_preanalysis"])
    self.assertIn("observations", materials["main_preanalysis"])
    self.assertEqual(
      [question["id"] for question in materials["review_questions"]],
      [
        "granularity",
        "ordering",
        "upstream_connection",
        "red_test_sufficiency",
      ],
    )
    for question in materials["review_questions"]:
      self.assertNotIn("\n", question["question"])
      self.assertNotIn(" and ", question["id"])

  def test_prepare_review_materials_defines_review_result_contract(self):
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
    output_dir = (
      self.tmpdir
      / ".reviewcompass/runtime/task-quality-review-materials/run"
    )

    result = run_script(
      [
        "task-quality-check",
        "prepare-review-materials",
        "--backlog-id", "todo-task-quality",
        "--checklist-id", "checklist-task-quality",
        "--output-dir", str(output_dir),
        "--json",
      ],
      cwd=self.tmpdir,
    )

    assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
    data = json.loads(result.stdout)
    materials = yaml.safe_load(Path(data["materials_path"]).read_text(encoding="utf-8"))
    contract = materials["review_result_contract"]
    self.assertEqual(contract["roles"], ["primary", "adversarial", "judgment"])
    self.assertEqual(
      contract["paths"],
      {
        "prompt_materials": str(output_dir / "review-materials.yaml"),
        "review_run_dir": ".reviewcompass/evidence/task-quality-review-runs/run",
        "prompts_dir": ".reviewcompass/evidence/task-quality-review-runs/run/prompts",
        "raw_results_dir": ".reviewcompass/evidence/task-quality-review-runs/run/raw-results",
        "normalized_results_dir": ".reviewcompass/evidence/task-quality-review-runs/run/normalized-results",
        "triage_decision_path": ".reviewcompass/evidence/task-quality-review-runs/run/triage-decision.yaml",
        "summary_path": ".reviewcompass/evidence/task-quality-review-runs/run/review-summary.yaml",
      },
    )
    boundary = materials["decision_boundary"]
    self.assertEqual(boundary["mechanical_gate"], "audit_result.verdict must be OK")
    self.assertEqual(boundary["blocking_finding_levels"], ["critical", "major"])
    self.assertTrue(boundary["review_output_does_not_authorize_changes"])
    self.assertEqual(
      boundary["accepted_when"],
      [
        "audit_result.verdict == OK",
        "no unresolved critical/major findings",
        "judgment role does not request changes",
      ],
    )

  def test_prepare_review_materials_fails_when_audit_has_deviation(self):
    self._write_todo_item()
    self._write_checklist([
      {
        "id": "TQG-1",
        "title": "task-quality-check CLI の機械監査項目を追加する",
        "status": "pending",
      },
    ])
    output_dir = (
      self.tmpdir
      / ".reviewcompass/runtime/task-quality-review-materials/run"
    )

    result = run_script(
      [
        "task-quality-check",
        "prepare-review-materials",
        "--backlog-id", "todo-task-quality",
        "--checklist-id", "checklist-task-quality",
        "--output-dir", str(output_dir),
        "--json",
      ],
      cwd=self.tmpdir,
    )

    assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["verdict"], "DEVIATION")
    self.assertIn("audit must be OK before preparing review materials", data["reasons"])
    self.assertFalse((output_dir / "review-materials.yaml").exists())

  def test_prepare_review_criteria_generates_task_quality_prompt_from_materials(self):
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
    materials_dir = (
      self.tmpdir
      / ".reviewcompass/runtime/task-quality-review-materials/run"
    )
    materials_result = run_script(
      [
        "task-quality-check",
        "prepare-review-materials",
        "--backlog-id", "todo-task-quality",
        "--checklist-id", "checklist-task-quality",
        "--output-dir", str(materials_dir),
        "--json",
      ],
      cwd=self.tmpdir,
    )
    self.assertEqual(
      materials_result.returncode,
      0,
      materials_result.stdout + materials_result.stderr,
    )
    materials_path = json.loads(materials_result.stdout)["materials_path"]
    review_run_dir = (
      self.tmpdir
      / ".reviewcompass/evidence/task-quality-review-runs/run"
    )

    result = run_script(
      [
        "task-quality-check",
        "prepare-review-criteria",
        "--materials-path", materials_path,
        "--review-run-dir", str(review_run_dir),
        "--json",
      ],
      cwd=self.tmpdir,
    )

    assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["verdict"], "OK")
    criteria_path = Path(data["criteria_path"])
    metadata_path = Path(data["metadata_path"])
    self.assertTrue(criteria_path.is_file())
    self.assertTrue(metadata_path.is_file())
    criteria = criteria_path.read_text(encoding="utf-8")
    self.assertIn("# Task Quality Review Criteria: Add task quality check", criteria)
    self.assertIn("todo-task-quality", criteria)
    self.assertIn("checklist-task-quality", criteria)
    self.assertIn(
      "`red test items appear after implementation items: TQG-RT-1`",
      criteria,
    )
    self.assertIn("Are checklist items concrete, non-overlapping", criteria)
    self.assertIn("Do red test items cover the task quality risks", criteria)
    self.assertIn("Do not authorize commit, push", criteria)
    self.assertIn("Respond as YAML", criteria)
    metadata = yaml.safe_load(metadata_path.read_text(encoding="utf-8"))
    self.assertEqual(metadata["schema_version"], "task-quality-review-criteria-v1")
    self.assertEqual(metadata["materials_path"], materials_path)
    self.assertEqual(metadata["backlog_id"], "todo-task-quality")
    self.assertEqual(metadata["checklist_id"], "checklist-task-quality")
    self.assertEqual(
      metadata["recommended_run_review_args"]["default_variant_for"],
      "task_quality_review",
    )

  def test_prepare_review_criteria_rejects_path_only_materials(self):
    review_run_dir = (
      self.tmpdir
      / ".reviewcompass/evidence/task-quality-review-runs/run"
    )
    materials_path = self.tmpdir / "review-materials.yaml"
    materials_path.write_text(
      yaml.safe_dump(
        {
          "schema_version": "task-quality-review-materials-v1",
          "review_target": {
            "backlog_id": "todo-task-quality",
            "checklist_id": "checklist-task-quality",
          },
          "source_materials": [
            {
              "id": "backlog_todo",
              "path": ".reviewcompass/backlog/todos/todo-task-quality.yaml",
              "content_mode": "path_only",
            },
          ],
          "audit_result": {"verdict": "OK", "warnings": []},
          "main_preanalysis": {"observations": []},
          "review_questions": [],
        },
        allow_unicode=True,
        sort_keys=False,
      ),
      encoding="utf-8",
    )

    result = run_script(
      [
        "task-quality-check",
        "prepare-review-criteria",
        "--materials-path", str(materials_path),
        "--review-run-dir", str(review_run_dir),
        "--json",
      ],
      cwd=self.tmpdir,
    )

    assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["verdict"], "DEVIATION")
    self.assertIn("source materials must be embedded full_text", data["reasons"])
    self.assertFalse((review_run_dir / "review-criteria.md").exists())


if __name__ == "__main__":
  unittest.main()
