prompt_id: gemini_review
provider: gemini-api
model_id: gemini-3.5-flash

# Task
Review the target document for the requested phase and criteria.

# Phase
post_write_verification

# Criteria
# Post-write Review Target

criteria_id: post_write_policy_violation_canonical_prompt_map
phase: post_write_verification
generated_at: 2026-06-21T15:09:29.724724+00:00

## Change Summary

post_write_policy_violation の判定点に canonical effective prompt path を追加し、API review-run へ誤進行しない停止点 prompt を固定する。

## Review Question

docs/operations/WORKFLOW_DISCIPLINE_MAP.yaml の変更は、post_write_policy_violation 判定点に canonical effective prompt を対応付ける目的に対して過不足なく、既存の post-write verification 運用や他の判定点を壊していないか。

## Target Files

- docs/operations/WORKFLOW_DISCIPLINE_MAP.yaml sha256=4b5a00603c209cc53c8a0c0815e17a24190b695b48357b21592185eb1fbf6ddc

## Target File Contents

### docs/operations/WORKFLOW_DISCIPLINE_MAP.yaml

content_mode: full_text
content_sha256: 4b5a00603c209cc53c8a0c0815e17a24190b695b48357b21592185eb1fbf6ddc

```text
# next_action ごとの直前必読規律マップ。
# `tools/check-workflow-action.py next --json` はこの内容を
# `next_action.required_disciplines` として返す。
# 作業対象の状態台帳や持ち越し一覧は規律ではないため、
# `required_inputs` の抽象入力として返す。
# `decision_points` は機械可読な判定点の全体カタログである。
# `by_kind`、`by_stage`、`required_inputs` は既存実装が読む実行時マップとして維持する。
default:
  - docs/operations/WORKFLOW_NAVIGATION.md
default_prompt_length_bounds:
  min_chars: 400
  max_chars: 20000
  failure_verdict: WARN
decision_points:
  next_action_kind:
    - id: stage
      prompt_source_refs:
        - docs/operations/WORKFLOW_NAVIGATION.md
        - docs/disciplines/discipline_workflow_state_truth_source.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: cross_feature_stage
      prompt_source_refs:
        - docs/operations/WORKFLOW_NAVIGATION.md
        - docs/disciplines/discipline_workflow_state_truth_source.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: commit_stop_point
      prompt_source_refs:
        - docs/operations/WORKFLOW_NAVIGATION.md#commit_stop_point
        - docs/disciplines/discipline_approval_operation.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: upstream_recheck
      prompt_source_refs:
        - docs/operations/WORKFLOW_NAVIGATION.md
        - docs/operations/REOPEN_PROCEDURE.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: reopen_classification_required
      prompt_source_refs:
        - docs/operations/WORKFLOW_NAVIGATION.md
        - docs/operations/REOPEN_PROCEDURE.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: completed
      prompt_source_refs:
        - docs/operations/WORKFLOW_NAVIGATION.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: unknown
      prompt_source_refs:
        - docs/operations/WORKFLOW_NAVIGATION.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: feature_definition_required
      prompt_source_refs:
        - docs/operations/WORKFLOW_NAVIGATION.md#feature_definition_required
        - docs/operations/INITIAL_SETUP_LLM_GUIDE.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: post_write_verification
      prompt_source_refs:
        - docs/operations/WORKFLOW_NAVIGATION.md#post_write_verification
        - docs/disciplines/discipline_post_write_verification.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: lightweight_self_check
      prompt_source_refs:
        - docs/operations/WORKFLOW_NAVIGATION.md#lightweight_self_check
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: post_write_policy_violation
      prompt_source_refs:
        - docs/operations/WORKFLOW_NAVIGATION.md#post_write_policy_violation
        - docs/disciplines/discipline_post_write_verification.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
      canonical_effective_prompt_path: .reviewcompass/guidance/effective-prompts/next-action-post-write-policy-violation.prompt.md
    - id: post_write_human_decision_required
      prompt_source_refs:
        - docs/operations/WORKFLOW_NAVIGATION.md#post_write_human_decision_required
        - docs/disciplines/discipline_post_write_verification.md
        - docs/disciplines/discipline_approval_operation.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: reopen_in_progress
      prompt_source_refs:
        - docs/operations/WORKFLOW_NAVIGATION.md#reopen_in_progress
        - docs/operations/REOPEN_PROCEDURE.md
        - docs/disciplines/discipline_approval_operation.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: maintenance_in_progress
      prompt_source_refs:
        - docs/operations/WORKFLOW_NAVIGATION.md#maintenance_in_progress
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: resume_in_progress
      prompt_source_refs:
        - docs/operations/WORKFLOW_NAVIGATION.md#resume_in_progress
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: reopen_started
      prompt_source_refs:
        - docs/operations/WORKFLOW_PRECHECK.md#reopen-start
        - docs/operations/WORKFLOW_PRECHECK_DETAILS.md#commit
        - docs/operations/REOPEN_PROCEDURE.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: reopen_start_failed
      prompt_source_refs:
        - docs/operations/WORKFLOW_PRECHECK.md#reopen-start
        - docs/operations/WORKFLOW_PRECHECK_DETAILS.md#commit
        - docs/operations/REOPEN_PROCEDURE.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
  workflow_stage:
    - id: candidate-proposal
      prompt_source_refs:
        - docs/operations/WORKFLOW_NAVIGATION.md
        - stages/feature-partitioning/2026-05-24-proposal.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: review
      prompt_source_refs:
        - docs/operations/WORKFLOW_NAVIGATION.md
        - stages/intent.yaml
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: drafting
      prompt_source_refs:
        - docs/operations/WORKFLOW_NAVIGATION.md
        - docs/operations/REOPEN_PROCEDURE.md
        - docs/disciplines/discipline_workflow_state_truth_source.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: triad-review
      prompt_source_refs:
        - docs/operations/WORKFLOW_NAVIGATION.md
        - docs/operations/SESSION_WORKFLOW_GUIDE.md#3.3-a-2
        - docs/operations/SESSION_WORKFLOW_GUIDE.md#vertical-intent-transfer-review
        - docs/operations/API_REVIEW_PROMPT_QUALITY.md
        - docs/disciplines/discipline_llm_as_judge_prompting.md
        - docs/disciplines/discipline_approval_operation.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
      prompt_length_bounds:
        min_chars: 1200
        max_chars: 60000
        failure_verdict: DEVIATION
    - id: review-wave
      prompt_source_refs:
        - docs/operations/WORKFLOW_NAVIGATION.md
        - docs/operations/SESSION_WORKFLOW_GUIDE.md#vertical-intent-transfer-review
        - learning/workflow/carry-forward-register/reviewcompass-import.yaml
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: alignment
      prompt_source_refs:
        - docs/operations/WORKFLOW_NAVIGATION.md
        - docs/operations/SESSION_WORKFLOW_GUIDE.md#vertical-intent-transfer-review
        - docs/disciplines/discipline_workflow_state_truth_source.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: approval
      prompt_source_refs:
        - docs/operations/WORKFLOW_NAVIGATION.md
        - docs/operations/WORKFLOW_PRECHECK.md#spec-set
        - docs/operations/WORKFLOW_PRECHECK_DETAILS.md#spec-set
        - docs/disciplines/discipline_approval_operation.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
      prompt_length_bounds:
        min_chars: 400
        max_chars: 12000
        failure_verdict: DEVIATION
  precheck_subcommand:
    - id: spec-set
      prompt_source_refs:
        - docs/operations/WORKFLOW_PRECHECK.md#spec-set
        - docs/operations/WORKFLOW_PRECHECK_DETAILS.md#spec-set
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: commit
      prompt_source_refs:
        - docs/operations/WORKFLOW_PRECHECK.md#commit
        - docs/operations/WORKFLOW_PRECHECK_DETAILS.md#commit
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: push
      prompt_source_refs:
        - docs/operations/WORKFLOW_PRECHECK.md#push
        - docs/operations/WORKFLOW_PRECHECK_DETAILS.md#push
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: autonomous-plan
      prompt_source_refs:
        - docs/operations/WORKFLOW_PRECHECK.md
        - docs/operations/WORKFLOW_PRECHECK_DETAILS.md#autonomous-plan
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: autonomous-plan-template
      prompt_source_refs:
        - docs/operations/WORKFLOW_PRECHECK.md
        - docs/operations/WORKFLOW_PRECHECK_DETAILS.md#autonomous-plan-template
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: autonomous-plan-record-integration
      prompt_source_refs:
        - docs/operations/WORKFLOW_PRECHECK.md
        - docs/operations/WORKFLOW_PRECHECK_DETAILS.md#autonomous-plan-record-integration
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: autonomous-ledger-audit
      prompt_source_refs:
        - docs/operations/WORKFLOW_PRECHECK.md
        - docs/operations/WORKFLOW_PRECHECK_DETAILS.md#autonomous-ledger-audit
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: audit-commit
      prompt_source_refs:
        - docs/operations/WORKFLOW_PRECHECK.md#audit-commit
        - docs/operations/WORKFLOW_PRECHECK_DETAILS.md#audit-commit
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: next
      prompt_source_refs:
        - docs/operations/WORKFLOW_NAVIGATION.md
        - docs/operations/WORKFLOW_DISCIPLINE_MAP.yaml
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: reopen-start
      prompt_source_refs:
        - docs/operations/WORKFLOW_PRECHECK.md#reopen-start
        - docs/operations/WORKFLOW_PRECHECK_DETAILS.md#commit
        - docs/operations/REOPEN_PROCEDURE.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
  operation_prompt:
    - id: commit
      prompt_source_refs:
        - docs/operations/COMMIT_OPERATION_CARD.md#commit-operation-card
      effective_prompt_policy: one_effective_prompt_per_decision_point
  reopen_required_action:
    - id: classify_and_rollback_flags
      prompt_source_refs:
        - docs/operations/REOPEN_PROCEDURE.md
        - docs/operations/WORKFLOW_NAVIGATION.md#reopen_in_progress
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: repair_canonical_documents
      prompt_source_refs:
        - docs/operations/REOPEN_PROCEDURE.md
        - docs/operations/WORKFLOW_NAVIGATION.md#reopen_in_progress
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: rerun_alignment_approval_chain
      prompt_source_refs:
        - docs/operations/REOPEN_PROCEDURE.md
        - docs/operations/WORKFLOW_NAVIGATION.md#reopen_in_progress
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: run_reopen_pending_gate
      prompt_source_refs:
        - docs/operations/REOPEN_PROCEDURE.md
        - docs/operations/WORKFLOW_NAVIGATION.md#reopen_in_progress
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: run_reopen_drafting
      prompt_source_refs:
        - docs/operations/REOPEN_PROCEDURE.md
        - docs/operations/WORKFLOW_NAVIGATION.md#reopen_in_progress
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: wait_for_human_approval
      prompt_source_refs:
        - docs/operations/REOPEN_PROCEDURE.md
        - docs/disciplines/discipline_approval_operation.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: finalize_reopen
      prompt_source_refs:
        - docs/operations/REOPEN_PROCEDURE.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: reopen_completed
      prompt_source_refs:
        - docs/operations/REOPEN_PROCEDURE.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: inspect_reopen_state
      prompt_source_refs:
        - docs/operations/WORKFLOW_NAVIGATION.md#reopen_in_progress
        - docs/operations/REOPEN_PROCEDURE.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
  review_run_triage_command:
    - id: list-pending
      prompt_source_refs:
        - docs/operations/SESSION_WORKFLOW_GUIDE.md#3.3-a-2
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: decide
      prompt_source_refs:
        - docs/operations/SESSION_WORKFLOW_GUIDE.md#3.3-a-2
        - docs/disciplines/discipline_approval_operation.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: manifest-template
      prompt_source_refs:
        - docs/operations/SESSION_WORKFLOW_GUIDE.md#3.3-a-2
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: write-manifest
      prompt_source_refs:
        - docs/operations/SESSION_WORKFLOW_GUIDE.md#3.3-a-2
        - docs/disciplines/discipline_post_write_verification.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: assert-apply-fixes-ready
      prompt_source_refs:
        - docs/operations/SESSION_WORKFLOW_GUIDE.md#3.3-a-2
        - docs/disciplines/discipline_approval_operation.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: assert-review-report-ready
      prompt_source_refs:
        - docs/operations/SESSION_WORKFLOW_GUIDE.md#3.3-a-2
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: generate-review-report
      prompt_source_refs:
        - docs/operations/SESSION_WORKFLOW_GUIDE.md#3.3-a-2
      effective_prompt_policy: one_effective_prompt_per_decision_point
  post_write_manifest_gate:
    - id: post_write_manifest_completed
      prompt_source_refs:
        - docs/operations/WORKFLOW_NAVIGATION.md#post_write_verification
        - docs/disciplines/discipline_post_write_verification.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: post_write_manifest_human_required
      prompt_source_refs:
        - docs/operations/WORKFLOW_NAVIGATION.md#post_write_human_decision_required
        - docs/disciplines/discipline_post_write_verification.md
        - docs/disciplines/discipline_approval_operation.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: post_write_manifest_missing_or_invalid
      prompt_source_refs:
        - docs/operations/WORKFLOW_NAVIGATION.md#post_write_verification
        - docs/disciplines/discipline_post_write_verification.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: post_write_policy_violation
      prompt_source_refs:
        - docs/operations/WORKFLOW_NAVIGATION.md#post_write_policy_violation
        - docs/disciplines/discipline_post_write_verification.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
      canonical_effective_prompt_path: .reviewcompass/guidance/effective-prompts/next-action-post-write-policy-violation.prompt.md
  proxy_model_decision_gate:
    - id: user_visible_triage_gate
      prompt_source_refs:
        - docs/operations/SESSION_WORKFLOW_GUIDE.md#3.3-a-2
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: proxy_decision_prompt
      prompt_source_refs:
        - docs/operations/SESSION_WORKFLOW_GUIDE.md#3.3-a-2
        - docs/operations/API_REVIEW_PROMPT_QUALITY.md
        - docs/disciplines/discipline_llm_as_judge_prompting.md
        - docs/disciplines/discipline_approval_operation.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: proxy_decision_file
      prompt_source_refs:
        - docs/operations/SESSION_WORKFLOW_GUIDE.md#3.3-a-2
        - docs/operations/API_REVIEW_PROMPT_QUALITY.md
        - docs/disciplines/discipline_llm_as_judge_prompting.md
        - docs/disciplines/discipline_approval_operation.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: proxy_approval_record
      prompt_source_refs:
        - docs/operations/SESSION_WORKFLOW_GUIDE.md#3.3-a-2
        - docs/disciplines/discipline_approval_operation.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
  conformance_evaluation_gate:
    - id: mv6_prompt_isolation
      prompt_source_refs:
        - docs/operations/WORKFLOW_NAVIGATION.md
        - .reviewcompass/specs/conformance-evaluation/tasks.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: reopen_handoff_package
      prompt_source_refs:
        - docs/operations/REOPEN_PROCEDURE.md
        - .reviewcompass/specs/conformance-evaluation/design.md
        - .reviewcompass/specs/conformance-evaluation/tasks.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
  yaml_audit_gate:
    - id: yaml_audit_scope
      prompt_source_refs:
        - docs/disciplines/discipline_yaml_audit.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: yaml_audit_post_write_check
      prompt_source_refs:
        - docs/disciplines/discipline_yaml_audit.md
        - docs/disciplines/discipline_post_write_verification.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
by_kind:
  stage:
    - docs/disciplines/discipline_workflow_state_truth_source.md
  cross_feature_stage:
    - docs/disciplines/discipline_workflow_state_truth_source.md
  post_write_verification:
    - docs/operations/WORKFLOW_NAVIGATION.md#post_write_verification
    - docs/disciplines/discipline_post_write_verification.md
  lightweight_self_check:
    - docs/operations/WORKFLOW_NAVIGATION.md#lightweight_self_check
  post_write_policy_violation:
    - docs/operations/WORKFLOW_NAVIGATION.md#post_write_policy_violation
    - docs/disciplines/discipline_post_write_verification.md
  post_write_human_decision_required:
    - docs/operations/WORKFLOW_NAVIGATION.md#post_write_human_decision_required
    - docs/disciplines/discipline_post_write_verification.md
    - docs/disciplines/discipline_approval_operation.md
  reopen_in_progress:
    - docs/operations/REOPEN_PROCEDURE.md
    - docs/disciplines/discipline_approval_operation.md
  maintenance_in_progress:
    - docs/operations/WORKFLOW_NAVIGATION.md#maintenance_in_progress
  resume_in_progress:
    - docs/operations/WORKFLOW_NAVIGATION.md#resume_in_progress
  feature_definition_required:
    - docs/operations/WORKFLOW_NAVIGATION.md#feature_definition_required
    - docs/operations/INITIAL_SETUP_LLM_GUIDE.md
by_stage:
  drafting:
    - docs/operations/REOPEN_PROCEDURE.md
    - docs/disciplines/discipline_workflow_state_truth_source.md
  triad-review:
    - docs/operations/SESSION_WORKFLOW_GUIDE.md#3.3-a-2
    - docs/operations/SESSION_WORKFLOW_GUIDE.md#vertical-intent-transfer-review
    - docs/operations/API_REVIEW_PROMPT_QUALITY.md
    - docs/disciplines/discipline_llm_as_judge_prompting.md
    - docs/disciplines/discipline_approval_operation.md
  review-wave:
    - docs/operations/SESSION_WORKFLOW_GUIDE.md#vertical-intent-transfer-review
  alignment:
    - docs/operations/SESSION_WORKFLOW_GUIDE.md#vertical-intent-transfer-review
    - docs/disciplines/discipline_workflow_state_truth_source.md
  approval:
    - docs/disciplines/discipline_approval_operation.md
    - docs/operations/WORKFLOW_PRECHECK.md#spec-set
    - docs/operations/WORKFLOW_PRECHECK_DETAILS.md#spec-set
required_inputs:
  by_stage:
    drafting:
      - id: target_feature_documents
        role: stage_entry_context
        source_type: feature_document_set
        purpose: Read the current feature state and phase documents before updating the phase artifact.
        resolver:
          kind: next_action_template
          paths:
            - .reviewcompass/specs/{feature}/spec.json
            - .reviewcompass/specs/{feature}/requirements.md
            - .reviewcompass/specs/{feature}/design.md
            - .reviewcompass/specs/{feature}/tasks.md
        read_policy: current_feature_documents
      - id: reopen_procedure_state
        role: workflow_state_context
        source_type: reopen_in_progress_file
        purpose: Read the reopen state and downstream impact decisions before drafting.
        resolver:
          kind: next_action_template
          paths:
            - "{file}"
        read_policy: reopen_state
    triad-review:
      - id: target_feature_documents
        role: stage_entry_context
        source_type: feature_document_set
        purpose: Read the current feature state and phase documents before starting triad-review, including upstream intent transfer from requirements to design to tasks to implementation as applicable.
        resolver:
          kind: next_action_template
          paths:
            - .reviewcompass/specs/{feature}/spec.json
            - .reviewcompass/specs/{feature}/requirements.md
            - .reviewcompass/specs/{feature}/design.md
            - .reviewcompass/specs/{feature}/tasks.md
        read_policy: current_feature_documents
      - id: triad_review_run_artifacts
        role: review_run_context
        source_type: review_run_artifact_set
        purpose: Prepare or read the review-run bundle, raw responses, model summaries, variant/role assignments, same-root finding clusters, and three-level triage records for this triad-review. Before proxy_model, implementation edits, spec.json updates, or phase movement, present the user-visible triage gate described in SESSION_WORKFLOW_GUIDE.md#3.3-a-2 and stop.
        resolver:
          kind: next_action_template
          base_path_pattern: .reviewcompass/specs/{feature}/reviews/*-{feature}-{phase}-review-run
        required_artifacts:
          - review-target.md
          - raw/
          - rounds.yaml
          - model-result-summary.yaml
          - triage.yaml
          - raw-review-triage-summary.md
          - variant-role-assignment
          - user-visible-triage-gate
        read_policy: review_run_bundle_and_triage
      - id: vertical_intent_transfer_check
        role: review_prompt_requirement
        source_type: upstream_intent_transfer_contract
        purpose: Ensure triad-review checks that upstream purpose, responsibility boundaries, acceptance criteria, and forbidden actions are inherited into the target phase without omission, weakening, unsupported additions, or drift.
        resolver:
          kind: static_reference
          path: docs/operations/SESSION_WORKFLOW_GUIDE.md#vertical-intent-transfer-review
        phase_chains:
          requirements:
            - upstream_decision_materials
            - requirements.md
          design:
            - requirements.md
            - design.md
          tasks:
            - requirements.md
            - design.md
            - tasks.md
          implementation:
            - requirements.md
            - design.md
            - tasks.md
            - implementation
        review_target_by_phase:
          requirements:
            review_target: requirements.md
            source_materials:
              - upstream_decision_materials
              - reopen_classification_record
              - planning_notes
              - user_decisions
            out_of_scope:
              - downstream_artifacts_not_review_target
              - design.md correctness
              - tasks.md correctness
        prompt_materialization_contract:
          source_materials_must_not_be_path_only: true
          required_prompt_material:
            - upstream_excerpt_or_structured_summary
            - target_phase_artifact_excerpt
            - review_target
            - out_of_scope
          upstream_summary_fields:
            - purpose
            - responsibility_boundaries
            - acceptance_criteria
            - forbidden_actions
            - unresolved_or_design_deferred_items
            - intended_target_phase_transfer
          blocking_conditions:
            - block_review_run_when_upstream_material_unread
            - block_review_run_when_prompt_contains_only_source_paths
            - block_review_run_when_upstream_summary_omits_required_fields
        required_question: upstream目的・責務境界・受入条件・禁止事項が対象成果物へ欠落・弱体化・逸脱・未根拠追加なく引き継がれているか。
        read_policy: include_in_review_prompt
    review-wave:
      - id: cross_feature_stage_artifacts
        role: stage_output_contract
        source_type: artifact_location_contract
        purpose: Record cross-feature stage evidence under the cross-feature namespace instead of any single feature. Standard path is .reviewcompass/specs/_cross_feature/reviews/{date}-{phase}-{stage}.md.
        resolver:
          kind: static_path_template
          path: .reviewcompass/specs/_cross_feature/reviews/{date}-{phase}-{stage}.md
        read_policy: create_or_update_stage_artifact
      - id: unresolved_cross_scope_items
        role: stage_entry_context
        source_type: carry_forward_register
        purpose: Read unresolved items carried forward from prior reviews or adjacent scopes before starting this stage.
        resolver:
          kind: project_state
          path: learning/workflow/carry-forward-register/reviewcompass-import.yaml
        read_policy: unresolved_items_only
      - id: vertical_intent_transfer_check
        role: review_prompt_requirement
        source_type: upstream_intent_transfer_contract
        purpose: Ensure review-wave preserves upstream intent while resolving cross-feature findings, and does not weaken or add unsupported requirements when carrying fixes across features.
        resolver:
          kind: static_reference
          path: docs/operations/SESSION_WORKFLOW_GUIDE.md#vertical-intent-transfer-review
        required_question: 上流の目的・責務境界・受入条件・禁止事項が、横断対処後の対象成果物へ欠落・弱体化・逸脱・未根拠追加なく引き継がれているか。
        read_policy: include_in_review_prompt
```


## Scope

- Check whether the changed target files clearly state the intended contract.
- Check whether related instructions are mutually consistent across targets.
- Check whether the documented procedure is actionable before API review, triage, manifest, or commit steps continue.

## Out Of Scope

- Do not request unrelated refactors or style-only rewrites.
- Do not judge files that are not listed in Target Files.
- Do not treat missing implementation work as a document defect unless the target text claims it already exists.

## Finding Policy

- Report must-fix findings for contradictions, missing required gates, or instructions that would allow an unsafe workflow action.
- Report should-fix findings for ambiguity that could cause repeated manual judgment or unnecessary API review loops.
- Return findings: [] when the target files are internally consistent for this review question.

## Sensitive Information Check

- status: passed
- External API review must not proceed if this section reports potential secrets.


# Output contract
Return YAML only.
The response must include the top-level key findings.
Additional top-level keys are allowed only when the criteria explicitly defines them.
Do not add wrapper keys such as review, result, metadata, or summary.
Do not wrap the YAML in Markdown code fences.
Do not write prose before or after the YAML.

Each finding must include these keys:
- severity
- target_location
- description
- rationale

Use only these severity values:
- CRITICAL
- ERROR
- WARN
- INFO

If there are no findings and the criteria does not define additional top-level keys, return exactly:

findings: []

Valid shape example:

findings:
  - severity: WARN
    target_location: "path or section"
    description: "Plain finding summary"
    rationale: "Why this matters"

# Prior findings
なし

# Target path
docs/operations/WORKFLOW_DISCIPLINE_MAP.yaml

# Target document
# next_action ごとの直前必読規律マップ。
# `tools/check-workflow-action.py next --json` はこの内容を
# `next_action.required_disciplines` として返す。
# 作業対象の状態台帳や持ち越し一覧は規律ではないため、
# `required_inputs` の抽象入力として返す。
# `decision_points` は機械可読な判定点の全体カタログである。
# `by_kind`、`by_stage`、`required_inputs` は既存実装が読む実行時マップとして維持する。
default:
  - docs/operations/WORKFLOW_NAVIGATION.md
default_prompt_length_bounds:
  min_chars: 400
  max_chars: 20000
  failure_verdict: WARN
decision_points:
  next_action_kind:
    - id: stage
      prompt_source_refs:
        - docs/operations/WORKFLOW_NAVIGATION.md
        - docs/disciplines/discipline_workflow_state_truth_source.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: cross_feature_stage
      prompt_source_refs:
        - docs/operations/WORKFLOW_NAVIGATION.md
        - docs/disciplines/discipline_workflow_state_truth_source.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: commit_stop_point
      prompt_source_refs:
        - docs/operations/WORKFLOW_NAVIGATION.md#commit_stop_point
        - docs/disciplines/discipline_approval_operation.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: upstream_recheck
      prompt_source_refs:
        - docs/operations/WORKFLOW_NAVIGATION.md
        - docs/operations/REOPEN_PROCEDURE.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: reopen_classification_required
      prompt_source_refs:
        - docs/operations/WORKFLOW_NAVIGATION.md
        - docs/operations/REOPEN_PROCEDURE.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: completed
      prompt_source_refs:
        - docs/operations/WORKFLOW_NAVIGATION.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: unknown
      prompt_source_refs:
        - docs/operations/WORKFLOW_NAVIGATION.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: feature_definition_required
      prompt_source_refs:
        - docs/operations/WORKFLOW_NAVIGATION.md#feature_definition_required
        - docs/operations/INITIAL_SETUP_LLM_GUIDE.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: post_write_verification
      prompt_source_refs:
        - docs/operations/WORKFLOW_NAVIGATION.md#post_write_verification
        - docs/disciplines/discipline_post_write_verification.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: lightweight_self_check
      prompt_source_refs:
        - docs/operations/WORKFLOW_NAVIGATION.md#lightweight_self_check
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: post_write_policy_violation
      prompt_source_refs:
        - docs/operations/WORKFLOW_NAVIGATION.md#post_write_policy_violation
        - docs/disciplines/discipline_post_write_verification.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
      canonical_effective_prompt_path: .reviewcompass/guidance/effective-prompts/next-action-post-write-policy-violation.prompt.md
    - id: post_write_human_decision_required
      prompt_source_refs:
        - docs/operations/WORKFLOW_NAVIGATION.md#post_write_human_decision_required
        - docs/disciplines/discipline_post_write_verification.md
        - docs/disciplines/discipline_approval_operation.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: reopen_in_progress
      prompt_source_refs:
        - docs/operations/WORKFLOW_NAVIGATION.md#reopen_in_progress
        - docs/operations/REOPEN_PROCEDURE.md
        - docs/disciplines/discipline_approval_operation.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: maintenance_in_progress
      prompt_source_refs:
        - docs/operations/WORKFLOW_NAVIGATION.md#maintenance_in_progress
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: resume_in_progress
      prompt_source_refs:
        - docs/operations/WORKFLOW_NAVIGATION.md#resume_in_progress
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: reopen_started
      prompt_source_refs:
        - docs/operations/WORKFLOW_PRECHECK.md#reopen-start
        - docs/operations/WORKFLOW_PRECHECK_DETAILS.md#commit
        - docs/operations/REOPEN_PROCEDURE.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: reopen_start_failed
      prompt_source_refs:
        - docs/operations/WORKFLOW_PRECHECK.md#reopen-start
        - docs/operations/WORKFLOW_PRECHECK_DETAILS.md#commit
        - docs/operations/REOPEN_PROCEDURE.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
  workflow_stage:
    - id: candidate-proposal
      prompt_source_refs:
        - docs/operations/WORKFLOW_NAVIGATION.md
        - stages/feature-partitioning/2026-05-24-proposal.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: review
      prompt_source_refs:
        - docs/operations/WORKFLOW_NAVIGATION.md
        - stages/intent.yaml
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: drafting
      prompt_source_refs:
        - docs/operations/WORKFLOW_NAVIGATION.md
        - docs/operations/REOPEN_PROCEDURE.md
        - docs/disciplines/discipline_workflow_state_truth_source.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: triad-review
      prompt_source_refs:
        - docs/operations/WORKFLOW_NAVIGATION.md
        - docs/operations/SESSION_WORKFLOW_GUIDE.md#3.3-a-2
        - docs/operations/SESSION_WORKFLOW_GUIDE.md#vertical-intent-transfer-review
        - docs/operations/API_REVIEW_PROMPT_QUALITY.md
        - docs/disciplines/discipline_llm_as_judge_prompting.md
        - docs/disciplines/discipline_approval_operation.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
      prompt_length_bounds:
        min_chars: 1200
        max_chars: 60000
        failure_verdict: DEVIATION
    - id: review-wave
      prompt_source_refs:
        - docs/operations/WORKFLOW_NAVIGATION.md
        - docs/operations/SESSION_WORKFLOW_GUIDE.md#vertical-intent-transfer-review
        - learning/workflow/carry-forward-register/reviewcompass-import.yaml
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: alignment
      prompt_source_refs:
        - docs/operations/WORKFLOW_NAVIGATION.md
        - docs/operations/SESSION_WORKFLOW_GUIDE.md#vertical-intent-transfer-review
        - docs/disciplines/discipline_workflow_state_truth_source.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: approval
      prompt_source_refs:
        - docs/operations/WORKFLOW_NAVIGATION.md
        - docs/operations/WORKFLOW_PRECHECK.md#spec-set
        - docs/operations/WORKFLOW_PRECHECK_DETAILS.md#spec-set
        - docs/disciplines/discipline_approval_operation.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
      prompt_length_bounds:
        min_chars: 400
        max_chars: 12000
        failure_verdict: DEVIATION
  precheck_subcommand:
    - id: spec-set
      prompt_source_refs:
        - docs/operations/WORKFLOW_PRECHECK.md#spec-set
        - docs/operations/WORKFLOW_PRECHECK_DETAILS.md#spec-set
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: commit
      prompt_source_refs:
        - docs/operations/WORKFLOW_PRECHECK.md#commit
        - docs/operations/WORKFLOW_PRECHECK_DETAILS.md#commit
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: push
      prompt_source_refs:
        - docs/operations/WORKFLOW_PRECHECK.md#push
        - docs/operations/WORKFLOW_PRECHECK_DETAILS.md#push
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: autonomous-plan
      prompt_source_refs:
        - docs/operations/WORKFLOW_PRECHECK.md
        - docs/operations/WORKFLOW_PRECHECK_DETAILS.md#autonomous-plan
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: autonomous-plan-template
      prompt_source_refs:
        - docs/operations/WORKFLOW_PRECHECK.md
        - docs/operations/WORKFLOW_PRECHECK_DETAILS.md#autonomous-plan-template
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: autonomous-plan-record-integration
      prompt_source_refs:
        - docs/operations/WORKFLOW_PRECHECK.md
        - docs/operations/WORKFLOW_PRECHECK_DETAILS.md#autonomous-plan-record-integration
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: autonomous-ledger-audit
      prompt_source_refs:
        - docs/operations/WORKFLOW_PRECHECK.md
        - docs/operations/WORKFLOW_PRECHECK_DETAILS.md#autonomous-ledger-audit
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: audit-commit
      prompt_source_refs:
        - docs/operations/WORKFLOW_PRECHECK.md#audit-commit
        - docs/operations/WORKFLOW_PRECHECK_DETAILS.md#audit-commit
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: next
      prompt_source_refs:
        - docs/operations/WORKFLOW_NAVIGATION.md
        - docs/operations/WORKFLOW_DISCIPLINE_MAP.yaml
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: reopen-start
      prompt_source_refs:
        - docs/operations/WORKFLOW_PRECHECK.md#reopen-start
        - docs/operations/WORKFLOW_PRECHECK_DETAILS.md#commit
        - docs/operations/REOPEN_PROCEDURE.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
  operation_prompt:
    - id: commit
      prompt_source_refs:
        - docs/operations/COMMIT_OPERATION_CARD.md#commit-operation-card
      effective_prompt_policy: one_effective_prompt_per_decision_point
  reopen_required_action:
    - id: classify_and_rollback_flags
      prompt_source_refs:
        - docs/operations/REOPEN_PROCEDURE.md
        - docs/operations/WORKFLOW_NAVIGATION.md#reopen_in_progress
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: repair_canonical_documents
      prompt_source_refs:
        - docs/operations/REOPEN_PROCEDURE.md
        - docs/operations/WORKFLOW_NAVIGATION.md#reopen_in_progress
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: rerun_alignment_approval_chain
      prompt_source_refs:
        - docs/operations/REOPEN_PROCEDURE.md
        - docs/operations/WORKFLOW_NAVIGATION.md#reopen_in_progress
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: run_reopen_pending_gate
      prompt_source_refs:
        - docs/operations/REOPEN_PROCEDURE.md
        - docs/operations/WORKFLOW_NAVIGATION.md#reopen_in_progress
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: run_reopen_drafting
      prompt_source_refs:
        - docs/operations/REOPEN_PROCEDURE.md
        - docs/operations/WORKFLOW_NAVIGATION.md#reopen_in_progress
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: wait_for_human_approval
      prompt_source_refs:
        - docs/operations/REOPEN_PROCEDURE.md
        - docs/disciplines/discipline_approval_operation.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: finalize_reopen
      prompt_source_refs:
        - docs/operations/REOPEN_PROCEDURE.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: reopen_completed
      prompt_source_refs:
        - docs/operations/REOPEN_PROCEDURE.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: inspect_reopen_state
      prompt_source_refs:
        - docs/operations/WORKFLOW_NAVIGATION.md#reopen_in_progress
        - docs/operations/REOPEN_PROCEDURE.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
  review_run_triage_command:
    - id: list-pending
      prompt_source_refs:
        - docs/operations/SESSION_WORKFLOW_GUIDE.md#3.3-a-2
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: decide
      prompt_source_refs:
        - docs/operations/SESSION_WORKFLOW_GUIDE.md#3.3-a-2
        - docs/disciplines/discipline_approval_operation.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: manifest-template
      prompt_source_refs:
        - docs/operations/SESSION_WORKFLOW_GUIDE.md#3.3-a-2
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: write-manifest
      prompt_source_refs:
        - docs/operations/SESSION_WORKFLOW_GUIDE.md#3.3-a-2
        - docs/disciplines/discipline_post_write_verification.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: assert-apply-fixes-ready
      prompt_source_refs:
        - docs/operations/SESSION_WORKFLOW_GUIDE.md#3.3-a-2
        - docs/disciplines/discipline_approval_operation.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: assert-review-report-ready
      prompt_source_refs:
        - docs/operations/SESSION_WORKFLOW_GUIDE.md#3.3-a-2
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: generate-review-report
      prompt_source_refs:
        - docs/operations/SESSION_WORKFLOW_GUIDE.md#3.3-a-2
      effective_prompt_policy: one_effective_prompt_per_decision_point
  post_write_manifest_gate:
    - id: post_write_manifest_completed
      prompt_source_refs:
        - docs/operations/WORKFLOW_NAVIGATION.md#post_write_verification
        - docs/disciplines/discipline_post_write_verification.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: post_write_manifest_human_required
      prompt_source_refs:
        - docs/operations/WORKFLOW_NAVIGATION.md#post_write_human_decision_required
        - docs/disciplines/discipline_post_write_verification.md
        - docs/disciplines/discipline_approval_operation.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: post_write_manifest_missing_or_invalid
      prompt_source_refs:
        - docs/operations/WORKFLOW_NAVIGATION.md#post_write_verification
        - docs/disciplines/discipline_post_write_verification.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: post_write_policy_violation
      prompt_source_refs:
        - docs/operations/WORKFLOW_NAVIGATION.md#post_write_policy_violation
        - docs/disciplines/discipline_post_write_verification.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
      canonical_effective_prompt_path: .reviewcompass/guidance/effective-prompts/next-action-post-write-policy-violation.prompt.md
  proxy_model_decision_gate:
    - id: user_visible_triage_gate
      prompt_source_refs:
        - docs/operations/SESSION_WORKFLOW_GUIDE.md#3.3-a-2
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: proxy_decision_prompt
      prompt_source_refs:
        - docs/operations/SESSION_WORKFLOW_GUIDE.md#3.3-a-2
        - docs/operations/API_REVIEW_PROMPT_QUALITY.md
        - docs/disciplines/discipline_llm_as_judge_prompting.md
        - docs/disciplines/discipline_approval_operation.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: proxy_decision_file
      prompt_source_refs:
        - docs/operations/SESSION_WORKFLOW_GUIDE.md#3.3-a-2
        - docs/operations/API_REVIEW_PROMPT_QUALITY.md
        - docs/disciplines/discipline_llm_as_judge_prompting.md
        - docs/disciplines/discipline_approval_operation.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: proxy_approval_record
      prompt_source_refs:
        - docs/operations/SESSION_WORKFLOW_GUIDE.md#3.3-a-2
        - docs/disciplines/discipline_approval_operation.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
  conformance_evaluation_gate:
    - id: mv6_prompt_isolation
      prompt_source_refs:
        - docs/operations/WORKFLOW_NAVIGATION.md
        - .reviewcompass/specs/conformance-evaluation/tasks.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: reopen_handoff_package
      prompt_source_refs:
        - docs/operations/REOPEN_PROCEDURE.md
        - .reviewcompass/specs/conformance-evaluation/design.md
        - .reviewcompass/specs/conformance-evaluation/tasks.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
  yaml_audit_gate:
    - id: yaml_audit_scope
      prompt_source_refs:
        - docs/disciplines/discipline_yaml_audit.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: yaml_audit_post_write_check
      prompt_source_refs:
        - docs/disciplines/discipline_yaml_audit.md
        - docs/disciplines/discipline_post_write_verification.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
by_kind:
  stage:
    - docs/disciplines/discipline_workflow_state_truth_source.md
  cross_feature_stage:
    - docs/disciplines/discipline_workflow_state_truth_source.md
  post_write_verification:
    - docs/operations/WORKFLOW_NAVIGATION.md#post_write_verification
    - docs/disciplines/discipline_post_write_verification.md
  lightweight_self_check:
    - docs/operations/WORKFLOW_NAVIGATION.md#lightweight_self_check
  post_write_policy_violation:
    - docs/operations/WORKFLOW_NAVIGATION.md#post_write_policy_violation
    - docs/disciplines/discipline_post_write_verification.md
  post_write_human_decision_required:
    - docs/operations/WORKFLOW_NAVIGATION.md#post_write_human_decision_required
    - docs/disciplines/discipline_post_write_verification.md
    - docs/disciplines/discipline_approval_operation.md
  reopen_in_progress:
    - docs/operations/REOPEN_PROCEDURE.md
    - docs/disciplines/discipline_approval_operation.md
  maintenance_in_progress:
    - docs/operations/WORKFLOW_NAVIGATION.md#maintenance_in_progress
  resume_in_progress:
    - docs/operations/WORKFLOW_NAVIGATION.md#resume_in_progress
  feature_definition_required:
    - docs/operations/WORKFLOW_NAVIGATION.md#feature_definition_required
    - docs/operations/INITIAL_SETUP_LLM_GUIDE.md
by_stage:
  drafting:
    - docs/operations/REOPEN_PROCEDURE.md
    - docs/disciplines/discipline_workflow_state_truth_source.md
  triad-review:
    - docs/operations/SESSION_WORKFLOW_GUIDE.md#3.3-a-2
    - docs/operations/SESSION_WORKFLOW_GUIDE.md#vertical-intent-transfer-review
    - docs/operations/API_REVIEW_PROMPT_QUALITY.md
    - docs/disciplines/discipline_llm_as_judge_prompting.md
    - docs/disciplines/discipline_approval_operation.md
  review-wave:
    - docs/operations/SESSION_WORKFLOW_GUIDE.md#vertical-intent-transfer-review
  alignment:
    - docs/operations/SESSION_WORKFLOW_GUIDE.md#vertical-intent-transfer-review
    - docs/disciplines/discipline_workflow_state_truth_source.md
  approval:
    - docs/disciplines/discipline_approval_operation.md
    - docs/operations/WORKFLOW_PRECHECK.md#spec-set
    - docs/operations/WORKFLOW_PRECHECK_DETAILS.md#spec-set
required_inputs:
  by_stage:
    drafting:
      - id: target_feature_documents
        role: stage_entry_context
        source_type: feature_document_set
        purpose: Read the current feature state and phase documents before updating the phase artifact.
        resolver:
          kind: next_action_template
          paths:
            - .reviewcompass/specs/{feature}/spec.json
            - .reviewcompass/specs/{feature}/requirements.md
            - .reviewcompass/specs/{feature}/design.md
            - .reviewcompass/specs/{feature}/tasks.md
        read_policy: current_feature_documents
      - id: reopen_procedure_state
        role: workflow_state_context
        source_type: reopen_in_progress_file
        purpose: Read the reopen state and downstream impact decisions before drafting.
        resolver:
          kind: next_action_template
          paths:
            - "{file}"
        read_policy: reopen_state
    triad-review:
      - id: target_feature_documents
        role: stage_entry_context
        source_type: feature_document_set
        purpose: Read the current feature state and phase documents before starting triad-review, including upstream intent transfer from requirements to design to tasks to implementation as applicable.
        resolver:
          kind: next_action_template
          paths:
            - .reviewcompass/specs/{feature}/spec.json
            - .reviewcompass/specs/{feature}/requirements.md
            - .reviewcompass/specs/{feature}/design.md
            - .reviewcompass/specs/{feature}/tasks.md
        read_policy: current_feature_documents
      - id: triad_review_run_artifacts
        role: review_run_context
        source_type: review_run_artifact_set
        purpose: Prepare or read the review-run bundle, raw responses, model summaries, variant/role assignments, same-root finding clusters, and three-level triage records for this triad-review. Before proxy_model, implementation edits, spec.json updates, or phase movement, present the user-visible triage gate described in SESSION_WORKFLOW_GUIDE.md#3.3-a-2 and stop.
        resolver:
          kind: next_action_template
          base_path_pattern: .reviewcompass/specs/{feature}/reviews/*-{feature}-{phase}-review-run
        required_artifacts:
          - review-target.md
          - raw/
          - rounds.yaml
          - model-result-summary.yaml
          - triage.yaml
          - raw-review-triage-summary.md
          - variant-role-assignment
          - user-visible-triage-gate
        read_policy: review_run_bundle_and_triage
      - id: vertical_intent_transfer_check
        role: review_prompt_requirement
        source_type: upstream_intent_transfer_contract
        purpose: Ensure triad-review checks that upstream purpose, responsibility boundaries, acceptance criteria, and forbidden actions are inherited into the target phase without omission, weakening, unsupported additions, or drift.
        resolver:
          kind: static_reference
          path: docs/operations/SESSION_WORKFLOW_GUIDE.md#vertical-intent-transfer-review
        phase_chains:
          requirements:
            - upstream_decision_materials
            - requirements.md
          design:
            - requirements.md
            - design.md
          tasks:
            - requirements.md
            - design.md
            - tasks.md
          implementation:
            - requirements.md
            - design.md
            - tasks.md
            - implementation
        review_target_by_phase:
          requirements:
            review_target: requirements.md
            source_materials:
              - upstream_decision_materials
              - reopen_classification_record
              - planning_notes
              - user_decisions
            out_of_scope:
              - downstream_artifacts_not_review_target
              - design.md correctness
              - tasks.md correctness
        prompt_materialization_contract:
          source_materials_must_not_be_path_only: true
          required_prompt_material:
            - upstream_excerpt_or_structured_summary
            - target_phase_artifact_excerpt
            - review_target
            - out_of_scope
          upstream_summary_fields:
            - purpose
            - responsibility_boundaries
            - acceptance_criteria
            - forbidden_actions
            - unresolved_or_design_deferred_items
            - intended_target_phase_transfer
          blocking_conditions:
            - block_review_run_when_upstream_material_unread
            - block_review_run_when_prompt_contains_only_source_paths
            - block_review_run_when_upstream_summary_omits_required_fields
        required_question: upstream目的・責務境界・受入条件・禁止事項が対象成果物へ欠落・弱体化・逸脱・未根拠追加なく引き継がれているか。
        read_policy: include_in_review_prompt
    review-wave:
      - id: cross_feature_stage_artifacts
        role: stage_output_contract
        source_type: artifact_location_contract
        purpose: Record cross-feature stage evidence under the cross-feature namespace instead of any single feature. Standard path is .reviewcompass/specs/_cross_feature/reviews/{date}-{phase}-{stage}.md.
        resolver:
          kind: static_path_template
          path: .reviewcompass/specs/_cross_feature/reviews/{date}-{phase}-{stage}.md
        read_policy: create_or_update_stage_artifact
      - id: unresolved_cross_scope_items
        role: stage_entry_context
        source_type: carry_forward_register
        purpose: Read unresolved items carried forward from prior reviews or adjacent scopes before starting this stage.
        resolver:
          kind: project_state
          path: learning/workflow/carry-forward-register/reviewcompass-import.yaml
        read_policy: unresolved_items_only
      - id: vertical_intent_transfer_check
        role: review_prompt_requirement
        source_type: upstream_intent_transfer_contract
        purpose: Ensure review-wave preserves upstream intent while resolving cross-feature findings, and does not weaken or add unsupported requirements when carrying fixes across features.
        resolver:
          kind: static_reference
          path: docs/operations/SESSION_WORKFLOW_GUIDE.md#vertical-intent-transfer-review
        required_question: 上流の目的・責務境界・受入条件・禁止事項が、横断対処後の対象成果物へ欠落・弱体化・逸脱・未根拠追加なく引き継がれているか。
        read_policy: include_in_review_prompt
