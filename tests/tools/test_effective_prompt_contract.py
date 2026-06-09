from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]


def _read(path):
  return (ROOT / path).read_text(encoding="utf-8")


def _yaml(path):
  return yaml.safe_load((ROOT / path).read_text(encoding="utf-8"))


def test_workflow_navigation_defines_one_effective_prompt_per_decision_point():
  text = _read("docs/operations/WORKFLOW_NAVIGATION.md")

  assert "判定点ごとに 1 本の effective prompt" in text
  assert "prompt_source_refs" in text
  assert "effective_prompt_path" in text
  assert "effective_prompt_sha256" in text
  assert "effective_prompt_loaded" in text
  assert "複数の元資料" in text
  assert "巨大な共通プロンプト" in text


def test_conformance_reopen_handoff_uses_effective_next_task_prompt():
  for path in [
    ".reviewcompass/specs/conformance-evaluation/requirements.md",
    ".reviewcompass/specs/conformance-evaluation/design.md",
    ".reviewcompass/specs/conformance-evaluation/tasks.md",
  ]:
    text = _read(path)

    assert "next_task_prompt_refs" in text
    assert "effective_next_task_prompt_path" in text
    assert "effective_next_task_prompt_sha256" in text
    assert "effective_next_task_prompt_loaded" in text
    assert "判定点ごとに 1 本" in text


def test_workflow_management_tracks_decision_prompt_map_as_canonical_artifact():
  for path in [
    ".reviewcompass/specs/workflow-management/requirements.md",
    ".reviewcompass/specs/workflow-management/design.md",
    ".reviewcompass/specs/workflow-management/tasks.md",
  ]:
    text = _read(path)

    assert "WORKFLOW_DISCIPLINE_MAP.yaml" in text
    assert "判定点" in text
    assert "required_disciplines" in text
    assert "required_inputs" in text
    assert "effective prompt" in text


def test_workflow_discipline_map_catalogs_all_current_decision_points():
  data = _yaml("docs/operations/WORKFLOW_DISCIPLINE_MAP.yaml")
  catalog = data["decision_points"]

  expected = {
    "next_action_kind": {
      "stage",
      "cross_feature_stage",
      "upstream_recheck",
      "reopen_classification_required",
      "completed",
      "unknown",
      "post_write_verification",
      "post_write_policy_violation",
      "post_write_human_decision_required",
      "reopen_in_progress",
      "maintenance_in_progress",
      "resume_in_progress",
      "reopen_started",
      "reopen_start_failed",
    },
    "workflow_stage": {
      "candidate-proposal",
      "review",
      "drafting",
      "triad-review",
      "review-wave",
      "alignment",
      "approval",
    },
    "precheck_subcommand": {
      "spec-set",
      "commit",
      "push",
      "autonomous-plan",
      "autonomous-plan-template",
      "autonomous-plan-record-integration",
      "autonomous-ledger-audit",
      "audit-commit",
      "next",
      "reopen-start",
    },
    "reopen_required_action": {
      "classify_and_rollback_flags",
      "repair_canonical_documents",
      "rerun_alignment_approval_chain",
      "run_reopen_pending_gate",
      "run_reopen_drafting",
      "wait_for_human_approval",
      "finalize_reopen",
      "reopen_completed",
      "inspect_reopen_state",
    },
    "review_run_triage_command": {
      "list-pending",
      "decide",
      "manifest-template",
      "write-manifest",
      "assert-apply-fixes-ready",
      "assert-review-report-ready",
      "generate-review-report",
    },
    "post_write_manifest_gate": {
      "post_write_manifest_completed",
      "post_write_manifest_human_required",
      "post_write_manifest_missing_or_invalid",
      "post_write_policy_violation",
    },
    "proxy_model_decision_gate": {
      "user_visible_triage_gate",
      "proxy_decision_prompt",
      "proxy_decision_file",
      "proxy_approval_record",
    },
    "conformance_evaluation_gate": {
      "mv6_prompt_isolation",
      "reopen_handoff_package",
    },
    "yaml_audit_gate": {
      "yaml_audit_scope",
      "yaml_audit_post_write_check",
    },
  }

  assert set(catalog) == set(expected)
  for group_name, expected_ids in expected.items():
    actual = {item["id"] for item in catalog[group_name]}
    assert actual == expected_ids
    for item in catalog[group_name]:
      assert item["effective_prompt_policy"] == "one_effective_prompt_per_decision_point"
      assert item["prompt_source_refs"]
