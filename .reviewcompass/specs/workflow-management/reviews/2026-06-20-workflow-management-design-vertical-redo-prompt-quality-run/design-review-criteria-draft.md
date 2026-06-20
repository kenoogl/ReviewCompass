---
criteria_id: workflow-management-design-vertical-redo-review-criteria-draft
phase: design
gate: stages/design.yaml#triad-review
intended_review_target:
  - .reviewcompass/specs/workflow-management/design.md
source_materials:
  note: "This front matter records provenance only. The model-readable source material is embedded in the body below."
  embedded:
    - requirement_12_registry_preflight_context
    - requirements_13_16_summary
    - vertical_intent_transfer_rule_summary
status: approved_by_prompt_quality_review
---

# Workflow-management Design Vertical Redo Review Criteria Draft

## Review Task

Review `.reviewcompass/specs/workflow-management/design.md` for the design triad-review gate.

The review question is:

Does the current `design.md` carry Requirement 13 through Requirement 16 from `requirements.md` into design-level decisions without omission, weakening, contradiction, unsupported addition, or drift?

Return findings only when the design target itself is deficient for this design-phase question.

## Why This Review Exists

This is not a general design review and not a reuse of the earlier design run. The current R-0 reopen exists because a tasks-granularity reopen exposed upstream design-authority problems. The active question moved upward: before tasks can be trusted, design must clearly authorize the operation contract / registry boundary and proxy / human decision boundary.

The earlier no-findings run from `2026-06-20-workflow-management-design-vertical-redo-review-run` is not sufficient as gate-completion evidence because its generated prompt used `review-target.md` as both criteria and target. That caused the models to review an author-written summary rather than `design.md` as the target document.

For this review, the reviewing model must use `.reviewcompass/specs/workflow-management/design.md` as the sole review target. Do not treat this criteria file, any review-target wrapper, or any author-written summary as a substitute for the target document.

## Required Discipline

Apply these prompt and review disciplines:

- `docs/disciplines/discipline_llm_as_judge_prompting.md`: judge prompts must include appropriate information, an appropriate non-leading question, an appropriate scope, a fixed output contract, and must avoid sending sensitive material.
- `docs/operations/SESSION_WORKFLOW_GUIDE.md#vertical-intent-transfer-review`: design review must check `requirements.md -> design.md`. The prompt must not list source materials by path only; it must include upstream material or a structured upstream summary that lets the model judge without guessing.

For this criteria file, the source materials are provided as structured summaries below. The path references in front matter are provenance only, not a request for the model to infer missing content.

## Review Target

The review target is only:

- `.reviewcompass/specs/workflow-management/design.md`

The model may use the source materials below only to check vertical intent transfer into the target. Do not judge `requirements.md`, `tasks.md`, implementation code, or other feature documents as targets in this review.

## Source Materials For Vertical Intent Transfer

### Requirement 12 context: operation registry / preflight

Requirement 12 is background context for Required Check 9. It requires operation preflight to be read-only and to inspect operation start conditions before execution. Its relevant expectations are:

- Operation registry / preflight covers review-run, post-write verification, triage, reopen, commit approval, session-record, deployment, export, and similar workflow operations.
- Preflight checks canonical command, inputs, artifacts, ordering, pending conflicts, worktree state, overwrite policy, and feature impact review scope before an operation starts.
- Preflight is a read-only confirmation layer. It must not update `spec.json`, workflow phase state, decision records, approval records, or the target operation itself.
- Workflow-management owns the operation contract / registry / preflight contract, but other features may be consumer / derivative impact review targets.
- Review should detect a contradiction if `design.md` makes registry / preflight an executor, approval consumer, state mutator, or separate source of truth from the operation contract.

### Requirement 13: operation contract vocabulary and required_action mapping

Purpose:

Maintainers must execute the one action selected by `next --json` based on operation contracts, not memory or precedent. The selection layer says what to do; the execution layer defines how through side effects, approval, preconditions, and postconditions.

Required transfer into design:

- Define `effect_kind`, `approval_required`, `phase_boundary`, `sequence`, `preconditions`, and `postconditions`.
- Keep `approval_required` independent from `effect_kind`.
- Define Phase 1 schemas for operation contract, effect kind, phase boundary, workflow-state snapshot, and language task I/O.
- Map all 19 `required_action` values without hiding branchy operations behind representative values.
- Include required_action, effect_kind, approval_required, phase_boundary, sequence, actor, branching, and referenced pre/postconditions.
- Treat `commit_stop_point`, `apply_approved_reopen_plan`, `run_reopen_start`, `advance_reopen_after_commit_stop_point`, `advance_reopen_after_approval_stop_point`, `finalize_reopen`, and `repair_workflow_state` as approval-required simple operations.
- Keep `record_human_decision` as a decision-record operation that does not itself satisfy target-operation approval.
- Split `run_reopen_pending_gate` by active gate and keep drafting separate as `run_reopen_drafting`.
- Treat `run_maintenance` and `run_workflow_stage` as compound operations with branch conditions, internal steps, max side effect, and approval aggregation.
- Establish a single machine-readable source-of-truth boundary between operation contract and operation registry / preflight.
- Ensure registry / preflight reads contract and does not execute, update, or consume approvals.
- Require detection of missing contract refs, stale digests, version drift, or duplicated source-of-truth fields.

Forbidden or high-risk drift:

- Do not duplicate side-effect / approval / phase-boundary fields across registry and contract as separate authorities.
- Do not let `record_human_decision` completion satisfy an approval-required target operation.
- Do not downgrade required commit / approval boundaries to advisory warnings in runner-enabled paths.

### Requirement 14: approval gate, side-track stack, and workflow-state snapshot

Purpose:

Approval, unexpected side tracks, and current-state visibility must be machine-readable state, not implicit LLM interpretation.

Required transfer into design:

- Model approval gate as `wait_for_human_decision`, `record_human_decision`, and subsequent `next --json` branching.
- Record approved, rejected, deferred, and changes_requested distinctly.
- Bind each decision to target operation ID, required_action, artifact or staged file set digest, actor, timestamp, and source.
- Treat side track as a stack. Frames include frame ID, kind, parent, pusher, allowed scope/files, completion conditions, return_to, title, spawned_from, staged file set, and staged file digest.
- Capture staged file set/digest on push, before pop, and before commit/push.
- Only top frame can pop; `next --json` resumes the immediate parent or mainline.
- Default `max_depth` is 2; Phase 3 warns and Phase 5 blocks.
- Treat `.reviewcompass/runtime/workflow-state-snapshot.yaml` as a `next --json` byproduct, not an authority replacing `next --json`.
- Include schema_version, generated_by, generated_at, current_work, active_side_tracks, git_tree_summary, post_write_manifest_summary, and workflow_state_summary in the snapshot.
- Mechanically distinguish proxy decisions and human-only decisions.
- Treat commit, push, spec.json update, phase approval, reopen finalize, and approval_required irreversible operation execution as human-only.
- Keep read-only operations and mutating operations separate.

Forbidden or high-risk drift:

- Do not let proxy_model replace human-only approval.
- Do not let stale snapshots authorize operations.
- Do not return to mainline after side-track pop if return_to or staged state cannot be verified.

### Requirement 15: structured effective prompt and audit

Purpose:

Effective prompts should be language-task specifications, not long unstructured instructions that smuggle machine operations into LLM text.

Required transfer into design:

- Define prompt structure with decision_point, preconditions_checked, language_task, postconditions, and on_completion.
- Define language_task with document_kind, input, output_format, and constraints.
- Keep machine tasks in operation contract, preflight, runner, and guard, not prompt instructions.
- Preserve `next_action.effective_prompt.effective_prompt_path` while Phase 4 generates structured prompts from DISCIPLINE_MAP or successor registry.
- Define first-layer prompt checks for file/anchor existence, mandatory sections, length, unknown action kind, review-target/manifest match, output/postcondition consistency, machine-checked preconditions, and on_completion compatibility.
- Keep Phase 6 LLM judge audit auxiliary and never final approval.

Forbidden or high-risk drift:

- Do not put commit, push, spec.json mutation, approval consumption, review-run artifact creation, or side-track mutation into the LLM language task.
- Do not treat semantic LLM judge audit as final approval.

### Requirement 16: Phase 0-6 implementation plan

Purpose:

Mechanization of the selection and execution layers must be implemented in order without mixing future phases into one risky change.

Required transfer into design:

- Phase 0 is D-003 selection-layer work: 19-step priority, one required_action, invariant checks, and reopen plan compiler.
- Phase 0 starts after the minimum schemas from Requirement 2 AC10-11; other operation contract schemas can proceed in parallel.
- Phase 0 completion requires the six D-003 failure tests and mechanical workflow-state repair detection.
- Phase 1 defines vocabularies and schemas without changing behavior.
- Phase 2 introduces read-only registry.
- Phase 3 introduces advisory preflight.
- Phase 4 structures effective prompts.
- Phase 5 turns selected warnings into blocks.
- Phase 6 adds optional LLM judge audit.
- Each Phase ends only after `next --json` can return normal work or an explicit stop state.
- Do not mix phases in one commit.
- Distinguish active reopen scope from historical `spec.json.reopened`.
- Check consumer / derivative impacts to other features during review-wave.
- Base proxy_model triage application on evidence completeness, finding/cluster coverage, approval gate records, operation contract approval_required, review-wave evidence, and human-only boundaries, not provider/model names.
- Human-required evidence always outranks proxy approval.

Forbidden or high-risk drift:

- Do not use `spec.json.reopened` alone as active reopen scope.
- Do not let proxy_model decisions pass human-required gates.
- Do not complete a phase with unresolved review-wave impact evidence or missing active-scope evidence.

## Required Checks

1. Check whether Requirement 13's purpose, responsibility boundaries, acceptance criteria, and forbidden actions are carried into `design.md`.
2. Check whether `design.md` settles the operation registry / operation contract source-of-truth boundary enough that tasks do not need to invent it later.
3. Check whether `record_human_decision` remains a decision-record operation and does not satisfy target operation approval by itself.
4. Check whether `run_reopen_pending_gate`, `run_reopen_drafting`, `run_maintenance`, and `run_workflow_stage` have enough branching / compound-operation structure to avoid LLM inference.
5. Check whether Requirement 14's approval gate, side-track stack, workflow-state snapshot, proxy/human boundary, and read-only/mutating boundary are carried into `design.md`.
6. Check whether `design.md` gives a clear enough human-only / proxy-allowed boundary for downstream tasks and implementation, especially commit, push, spec.json update, phase approval, reopen finalize, and approval_required operation execution.
7. Check whether Requirement 15's structured effective prompt model keeps machine operations outside language tasks and makes prompt audit mechanically checkable.
8. Check whether Requirement 16's Phase 0-6 sequencing, active reopen scope distinction, impact review scope, and proxy triage decision predicates are design-level decisions rather than task-level guesses.
9. Check whether `design.md` contradicts Requirement 12 operation registry / preflight.
10. Check whether `design.md` overclaims implementation that has not happened yet.
11. Check whether `design.md` accurately represents design drafting status without implying design triad-review, review-wave, alignment, approval, commit, or push are complete.

## Out Of Scope

- Do not request implementation code changes during this design triad-review.
- Do not judge `tasks.md` correctness except when a design omission would force tasks to invent design authority.
- Do not decide cross-feature impact; that belongs to design review-wave.
- The reviewing model must not itself approve or authorize commit, push, spec.json mutation, phase transition, or reopen gate completion. This does not prevent findings about whether `design.md` correctly preserves those boundaries.
- Do not treat source-material defects as findings unless they cause a design transfer defect in `design.md`.

## Finding Policy

- Report `CRITICAL` when the design would allow bypassing human-only approval, commit/push/spec.json/phase approval boundaries, or active reopen-scope evidence.
- Report `ERROR` when a requirement purpose, responsibility boundary, acceptance criterion, or forbidden action is missing, weakened, contradicted, or replaced by unsupported design behavior.
- Report `ERROR` when `design.md` adds a design behavior that is unsupported by Requirement 13 through Requirement 16 or by the provided Requirement 12 context, if that addition would constrain downstream tasks or implementation.
- Report `ERROR` when design leaves registry/contract authority, proxy/human authority, or active reopen scope ambiguous enough that tasks or implementation must invent policy.
- Report `WARN` for ambiguity likely to force repeated manual judgment, weak traceability, unclear schema/state boundaries, or overclaiming implementation completion.
- Report `INFO` only for non-blocking traceability improvements.
- Return `findings: []` only when `design.md` is traceable, internally consistent, correctly scoped for design drafting, and sufficiently grounded for downstream tasks.
