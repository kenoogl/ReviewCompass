"""T-010 のテスト：他機能との接合面。

対応タスク：self-improvement tasks.md T-010
対応設計節：design.md §13.1〜§13.6
対応要件：Boundary Context 隣接期待
"""
import json

import yaml

from tools.self_improvement.interfaces import (
  InterfaceAdapter,
  assert_commit_fields_are_independent,
  foundation_reference_contract,
)


def _write_yaml(path, data):
  path.parent.mkdir(parents=True, exist_ok=True)
  path.write_text(
    yaml.safe_dump(data, allow_unicode=True, sort_keys=False),
    encoding="utf-8",
  )


def test_t010_foundation_vocabularies_are_referenced_not_redefined():
  contract = foundation_reference_contract()

  assert contract == {
    "discipline_check_schema": "foundation",
    "review_mode_vocabulary": "foundation",
    "state_axis_vocabulary": "foundation",
    "policy": "reference_only_no_redefinition",
  }
  assert "api_mediated" not in json.dumps(contract, ensure_ascii=False)
  assert "runtime_mediated" not in json.dumps(contract, ensure_ascii=False)


def test_t010_reads_evaluation_role_diff_report(tmp_path):
  report_path = tmp_path / "evaluation" / "roles" / "role_diff_report.json"
  report_path.parent.mkdir(parents=True)
  report_path.write_text(
    json.dumps({"report_id": "role-diff-001", "items": [{"role": "primary"}]}),
    encoding="utf-8",
  )

  result = InterfaceAdapter(tmp_path).read_evaluation_role_diff_report(report_path)

  assert result == {"report_id": "role-diff-001", "items": [{"role": "primary"}]}


def test_t010_writes_analysis_metrics_output(tmp_path):
  path = InterfaceAdapter(tmp_path).write_analysis_metrics(metric_date="2026-06-04")

  assert path == tmp_path / "learning" / "workflow" / "metrics" / "2026-06-04.yaml"
  data = yaml.safe_load(path.read_text(encoding="utf-8"))
  assert data["metric_date"] == "2026-06-04"
  assert "adoption_rate" in data


def test_t010_workflow_management_contract_and_git_mv_path(tmp_path):
  proposal_path = tmp_path / "learning" / "workflow" / "proposals" / "WP-001.yaml"
  _write_yaml(
    proposal_path,
    {
      "proposal_id": "WP-001",
      "status": "approved",
      "target_discipline_path": ".reviewcompass/guidance/discipline_update.md",
      "materialized_at": None,
      "materialization_commit_hash": None,
    },
  )

  contract = InterfaceAdapter(tmp_path).workflow_management_input_contract(proposal_path)

  assert contract == {
    "proposal_id": "WP-001",
    "approved_state_owner": "self-improvement",
    "materialization_owner": "workflow-management",
    "source_path": "learning/workflow/proposals/WP-001.yaml",
    "approved_updates_path": "learning/workflow/approved-updates/WP-001.yaml",
    "move_operation": "git_mv_required",
    "approved_means": "self_improvement_approval_time",
    "materialized_at_means": "workflow_management_completion_time",
  }


def test_t010_conformance_target_commit_is_independent_from_materialization_commit():
  result = assert_commit_fields_are_independent(
    target_commit="abc123",
    materialization_commit_hash="def456",
  )

  assert result == {
    "target_commit_owner": "conformance-evaluation",
    "materialization_commit_hash_owner": "self-improvement",
    "independent": True,
  }


def test_t010_approved_updates_readme_documents_workflow_management_route():
  text = (
    InterfaceAdapter.project_root()
    / "learning"
    / "workflow"
    / "approved-updates"
    / "README.md"
  ).read_text(encoding="utf-8")

  assert "workflow-management" in text
  assert "git mv" in text
  assert "materialized_at" in text
  assert "materialization_commit_hash" in text


def test_t010_self_improvement_operations_document_proposal_authority_only():
  text = (
    InterfaceAdapter.project_root()
    / "docs"
    / "operations"
    / "SELF_IMPROVEMENT.md"
  ).read_text(encoding="utf-8")

  assert "提案権のみ" in text
  assert "実体変更は workflow-management 経由" in text
  assert "- docs/disciplines/ の規律更新" not in text
