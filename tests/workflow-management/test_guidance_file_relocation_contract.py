from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]

GUIDANCE_FILENAMES = [
  "WORKFLOW_DISCIPLINE_MAP.yaml",
  "WORKFLOW_NAVIGATION.md",
  "WORKFLOW_PRECHECK.md",
  "WORKFLOW_PRECHECK_DETAILS.md",
  "REOPEN_PROCEDURE.md",
  "SESSION_WORKFLOW_GUIDE.md",
  "API_REVIEW_PROMPT_QUALITY.md",
  "COMMIT_OPERATION_CARD.md",
  "INITIAL_SETUP_LLM_GUIDE.md",
  "discipline_approval_operation.md",
  "discipline_llm_as_judge_prompting.md",
  "discipline_post_write_verification.md",
  "discipline_workflow_state_truth_source.md",
  "discipline_yaml_audit.md",
  "discipline_avoid_compound_bash.md",
  "discipline_concise_complete_report.md",
  "discipline_facts_vs_interpretation.md",
  "discipline_implementation_autonomy.md",
  "discipline_intent_conformance_is_the_acceptance_gate.md",
  "discipline_must_fix_discussion_obligation.md",
  "discipline_no_redundant_workflow_questions.md",
  "discipline_normal_output_minimization.md",
  "discipline_options_presentation.md",
  "discipline_plain_explanation_each_step.md",
  "discipline_plain_japanese.md",
  "discipline_pre_action_precheck.md",
  "discipline_reopen_procedure_for_settled_topics.md",
  "discipline_standing_directives_are_hard_constraints.md",
  "discipline_workflow_precheck_invocation.md",
]

LEGACY_GUIDANCE_PATHS = [
  "docs/operations/WORKFLOW_DISCIPLINE_MAP.yaml",
  "docs/operations/WORKFLOW_NAVIGATION.md",
  "docs/operations/WORKFLOW_PRECHECK.md",
  "docs/operations/WORKFLOW_PRECHECK_DETAILS.md",
  "docs/operations/REOPEN_PROCEDURE.md",
  "docs/operations/SESSION_WORKFLOW_GUIDE.md",
  "docs/operations/API_REVIEW_PROMPT_QUALITY.md",
  "docs/operations/COMMIT_OPERATION_CARD.md",
  "docs/operations/INITIAL_SETUP_LLM_GUIDE.md",
  "docs/disciplines/discipline_approval_operation.md",
  "docs/disciplines/discipline_llm_as_judge_prompting.md",
  "docs/disciplines/discipline_post_write_verification.md",
  "docs/disciplines/discipline_workflow_state_truth_source.md",
  "docs/disciplines/discipline_yaml_audit.md",
  "docs/disciplines/discipline_avoid_compound_bash.md",
  "docs/disciplines/discipline_concise_complete_report.md",
  "docs/disciplines/discipline_facts_vs_interpretation.md",
  "docs/disciplines/discipline_implementation_autonomy.md",
  "docs/disciplines/discipline_intent_conformance_is_the_acceptance_gate.md",
  "docs/disciplines/discipline_must_fix_discussion_obligation.md",
  "docs/disciplines/discipline_no_redundant_workflow_questions.md",
  "docs/disciplines/discipline_normal_output_minimization.md",
  "docs/disciplines/discipline_options_presentation.md",
  "docs/disciplines/discipline_plain_explanation_each_step.md",
  "docs/disciplines/discipline_plain_japanese.md",
  "docs/disciplines/discipline_pre_action_precheck.md",
  "docs/disciplines/discipline_reopen_procedure_for_settled_topics.md",
  "docs/disciplines/discipline_standing_directives_are_hard_constraints.md",
  "docs/disciplines/discipline_workflow_precheck_invocation.md",
]

ACTIVE_REFERENCE_SURFACES = [
  "AGENTS.md",
  "TODO_NEXT_SESSION.md",
  ".codex/hooks",
  ".claude/hooks",
  "templates",
  "docs/operations",
  "docs/disciplines",
  "tools/check-workflow-action.py",
  "tools/document_link_lint.py",
  "deploy-manifest.yaml",
]


def _read_text(path: Path) -> str:
  return path.read_text(encoding="utf-8")


@pytest.mark.parametrize("filename", GUIDANCE_FILENAMES)
def test_moved_guidance_files_exist_only_in_reviewcompass_guidance(filename):
  assert (ROOT / ".reviewcompass" / "guidance" / filename).is_file()
  assert not (ROOT / "docs" / "operations" / filename).exists()
  assert not (ROOT / "docs" / "disciplines" / filename).exists()


def test_active_surfaces_do_not_reference_moved_legacy_guidance_paths():
  findings = []
  for surface in ACTIVE_REFERENCE_SURFACES:
    path = ROOT / surface
    files = [path] if path.is_file() else sorted(p for p in path.rglob("*") if p.is_file())
    for file_path in files:
      text = _read_text(file_path)
      for legacy_path in LEGACY_GUIDANCE_PATHS:
        if legacy_path in text:
          findings.append(f"{file_path.relative_to(ROOT)} -> {legacy_path}")

  assert findings == []


def test_review_prompt_guide_hooks_read_canonical_guidance_path():
  expected = ".reviewcompass/guidance/discipline_llm_as_judge_prompting.md"
  forbidden = "docs/disciplines/discipline_llm_as_judge_prompting.md"

  for relpath in [
    ".codex/hooks/review-prompt-guide-inject.sh",
    ".claude/hooks/review-prompt-guide-inject.sh",
  ]:
    text = _read_text(ROOT / relpath)
    assert expected in text
    assert forbidden not in text


def test_deploy_facing_templates_do_not_point_to_moved_legacy_guidance_paths():
  findings = []
  for file_path in sorted((ROOT / "templates").rglob("*")):
    if not file_path.is_file():
      continue
    text = _read_text(file_path)
    for legacy_path in LEGACY_GUIDANCE_PATHS:
      if legacy_path in text:
        findings.append(f"{file_path.relative_to(ROOT)} -> {legacy_path}")

  assert findings == []
