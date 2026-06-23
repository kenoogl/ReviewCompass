"""T-007 のテスト：履歴とロールバックモデル。

対応タスク：self-improvement tasks.md T-007
対応設計節：design.md §11.1〜§11.6
対応要件：Requirement 7 受入 1〜5
"""
import json
from pathlib import Path

import pytest
import yaml

from tools.self_improvement.rollback_model import (
  RollbackError,
  RollbackModel,
  validate_rollback_record,
)


def _write_yaml(path, data):
  path.parent.mkdir(parents=True, exist_ok=True)
  path.write_text(
    yaml.safe_dump(data, allow_unicode=True, sort_keys=False),
    encoding="utf-8",
  )


def _read_yaml(path):
  return yaml.safe_load(Path(path).read_text(encoding="utf-8"))


def test_t007_creates_three_rollback_method_records(tmp_path):
  model = RollbackModel(tmp_path)

  records = [
    model.create_rollback_record(
      target_proposal_id="WP-001",
      rollback_method="archive_restoration",
      rollback_reason="archive から規律を復活する",
      rollback_date="2026-06-04",
      related_artifacts=["docs/disciplines/archive/README.md"],
    ),
    model.create_rollback_record(
      target_proposal_id="WP-002",
      rollback_method="status_downgrade",
      rollback_reason="enforced から aspirational に戻す",
      rollback_date="2026-06-04",
      related_artifacts=["learning/workflow/approved-updates/WP-002.yaml"],
    ),
    model.create_rollback_record(
      target_proposal_id="WP-003",
      rollback_method="git_revert",
      rollback_reason="規律更新 commit を取り消す",
      rollback_date="2026-06-04",
      related_artifacts=["commit:abc123"],
    ),
  ]

  assert [record["rollback_method"] for record in records] == [
    "archive_restoration",
    "status_downgrade",
    "git_revert",
  ]
  assert [record["rollback_id"] for record in records] == ["RB-001", "RB-002", "RB-003"]
  assert (tmp_path / "learning" / "workflow" / "rollback" / "2026-06-04-RB-003.yaml").is_file()


def test_t007_rejects_unknown_rollback_method_fail_closed():
  with pytest.raises(RollbackError, match="unknown_rollback_method"):
    validate_rollback_record({
      "rollback_id": "RB-001",
      "target_proposal_id": "WP-001",
      "rollback_method": "manual_fix",
      "rollback_reason": "未知の方法",
      "rollback_date": "2026-06-04",
      "related_artifacts": [],
    })


def test_t007_next_rb_id_scans_existing_rollback_records(tmp_path):
  _write_yaml(
    tmp_path / "learning" / "workflow" / "rollback" / "2026-06-03-RB-099.yaml",
    {"rollback_id": "RB-099"},
  )

  assert RollbackModel(tmp_path).next_rollback_id() == "RB-100"


def test_t007_next_rb_id_scans_all_four_workflow_directories(tmp_path):
  for directory, rollback_id in [
    ("proposals", "RB-010"),
    ("approved-updates", "RB-099"),
    ("rejected-updates", "RB-100"),
    ("rollback", "RB-003"),
  ]:
    _write_yaml(
      tmp_path / "learning" / "workflow" / directory / f"{rollback_id}.yaml",
      {"rollback_id": rollback_id},
    )

  assert RollbackModel(tmp_path).next_rollback_id() == "RB-101"


def test_t007_symlink_recreation_plan_has_five_steps(tmp_path):
  plan = RollbackModel(tmp_path).symlink_recreation_plan(
    memory_link="memory/feedback_x.md",
    repo_target=".reviewcompass/guidance/discipline_x.md",
  )

  assert [step["step"] for step in plan["steps"]] == [1, 2, 3, 4, 5]
  assert plan["memory_link"] == "memory/feedback_x.md"
  assert plan["repo_target"] == ".reviewcompass/guidance/discipline_x.md"
  assert all(step["machine_check"] for step in plan["steps"])


def test_t007_traces_proposal_approval_and_rollback_history(tmp_path):
  _write_yaml(
    tmp_path / "learning" / "workflow" / "approved-updates" / "WP-001.yaml",
    {"proposal_id": "WP-001", "status": "approved"},
  )
  _write_yaml(
    tmp_path / "learning" / "workflow" / "rollback" / "2026-06-04-RB-001.yaml",
    {
      "rollback_id": "RB-001",
      "target_proposal_id": "WP-001",
      "rollback_method": "status_downgrade",
      "rollback_reason": "戻す",
      "rollback_date": "2026-06-04",
      "related_artifacts": [],
    },
  )

  trace = RollbackModel(tmp_path).trace_history("WP-001")

  assert trace["proposal"]["path"] == "learning/workflow/approved-updates/WP-001.yaml"
  assert trace["proposal"]["status"] == "approved"
  assert trace["rollbacks"] == [
    {
      "path": "learning/workflow/rollback/2026-06-04-RB-001.yaml",
      "rollback_id": "RB-001",
      "rollback_method": "status_downgrade",
    }
  ]


def test_t007_archive_restoration_integrity_checks_and_report(tmp_path):
  restored = tmp_path / ".reviewcompass" / "guidance" / "discipline_restored.md"
  restored.parent.mkdir(parents=True)
  restored.write_text(
    "---\nname: restored\nstatus: enforced\n---\n# Restored\n[[discipline_related]]\n",
    encoding="utf-8",
  )
  archive_readme = tmp_path / "docs" / "disciplines" / "archive" / "README.md"
  archive_readme.parent.mkdir(parents=True)
  archive_readme.write_text("restored rollback approved\n", encoding="utf-8")

  result = RollbackModel(tmp_path).check_archive_restoration_integrity(
    restored_discipline_path=".reviewcompass/guidance/discipline_restored.md",
    archive_readme_path="docs/disciplines/archive/README.md",
    report_date="2026-06-04",
  )

  report = tmp_path / "docs" / "discipline-compliance-reports" / "2026-06-04-rollback.yaml"
  assert result["front_matter_valid"] is True
  assert result["internal_links"] == ["discipline_related"]
  assert result["archive_readme_consistent"] is True
  assert _read_yaml(report)["check"] == "archive_restoration_integrity"


def test_t007_rollback_schema_documents_owned_constraints():
  schema = json.loads(
    (RollbackModel.project_root() / "learning" / "workflow" / "schemas" / "rollback.schema.json")
    .read_text(encoding="utf-8")
  )

  assert schema["properties"]["rollback_method"]["enum"] == [
    "archive_restoration",
    "status_downgrade",
    "git_revert",
  ]
  assert schema["required"] == [
    "rollback_id",
    "target_proposal_id",
    "rollback_method",
    "rollback_reason",
    "rollback_date",
    "related_artifacts",
  ]
