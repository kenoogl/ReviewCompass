prompt_id: anthropic_review
provider: anthropic-api
model_id: claude-sonnet-4-6

# Task
Review the target document for the requested phase and criteria.

# Phase
design

# Criteria
---
review_target: workflow-management design vertical redo
phase: design
gate: stages/design.yaml#triad-review
feature: workflow-management
date: 2026-06-20
source_documents:
  - .reviewcompass/specs/workflow-management/requirements.md
  - .reviewcompass/specs/workflow-management/design.md
  - .reviewcompass/specs/workflow-management/spec.json
  - stages/in-progress/reopen-procedure-2026-06-19.yaml
  - docs/reviews/reopen-classification-2026-06-19-wm-requirement-13-16-vertical-redo.md
  - docs/operations/SESSION_WORKFLOW_GUIDE.md#vertical-intent-transfer-review
effective_prompt:
  path: .reviewcompass/runtime/effective-prompts/next_action_kind-reopen_in_progress__workflow_stage-triad-review__reopen_required_action-run_reopen_pending_gate.prompt.md
  sha256: 6d4374ac39164c2001ca6a34fb9029ee3a6816febd15a5da7b26208ca17b4a11
---

# Review Target: workflow-management design / Requirement 13-16 vertical redo

## Review Purpose

Review whether the current `workflow-management` design document correctly carries approved Requirement 13 through Requirement 16 into design-level decisions. This is a vertical intent transfer review, not a reuse of the older design run.

The current reopen exists because a tasks-granularity reopen exposed upstream design authority problems. The review must therefore check whether requirements purpose, responsibility boundaries, acceptance criteria, forbidden actions, and unresolved design decisions are present in `design.md` without omission, weakening, unsupported additions, or drift.

## Current Run Inputs

Current file digests at review-target preparation:

| path | sha256 |
|---|---|
| `.reviewcompass/specs/workflow-management/requirements.md` | `e7621e6d56a3ef42085e2864a88366d670e55c304668dd21f48dde32411e13f3` |
| `.reviewcompass/specs/workflow-management/design.md` | `cc668ad714baf00bb6edd5e108cd6e1b3a9a673dac88e0cfe947e58fa8643ef8` |
| `.reviewcompass/specs/workflow-management/spec.json` | `ae674dec950ea5c0e5f8a1dea9935c489c54d9d0da0c85a46b96b0b3a617d9da` |
| `stages/in-progress/reopen-procedure-2026-06-19.yaml` | `65af6cb1368fa7be978234bce32bc990cf71c3efc52ac0d83f20d64bf33ba9e0` |
| effective prompt | `6d4374ac39164c2001ca6a34fb9029ee3a6816febd15a5da7b26208ca17b4a11` |

## Why This Review Is Being Re-run

The older design run used stale inputs. Since then, requirements triad-review changed `requirements.md`, requirements review-wave / alignment / approval advanced the reopen, the effective prompt changed to include vertical-intent transfer requirements, and the current in-progress YAML now records design drafting completion. This run must therefore use the current requirements/design/spec/reopen state.

Classification record summary:

- The current R-0 reopen is based on Requirement 13-16.
- The earlier tasks-granularity reopen was superseded because vertical intent review showed the issue was not only task detail.
- Two design-authority questions must be checked at design level:
  - Whether the operation registry / operation contract source-of-truth split, digest/version synchronization, and read-only preflight boundary are design-authorized rather than task-invented.
  - Whether proxy / human decision boundaries are settled across Requirement 14, Requirement 16, and approval discipline rather than left for tasks or implementation to infer.

## Upstream Requirements Summary

### Requirement 13: operation contract vocabulary and required_action mapping

Purpose: a maintainer should execute the one action selected by `next --json` based on operation contracts, not memory or precedent. The selection layer says what to do; the execution layer defines how to do it through side effects, approval, preconditions, and postconditions.

Responsibility boundaries and acceptance criteria:

- Defines `effect_kind`, `approval_required`, `phase_boundary`, `sequence`, `preconditions`, and `postconditions`.
- `effect_kind` has baseline values `read`, `write`, `state_mutation`, and `external_call`.
- `approval_required` is independent from `effect_kind`.
- Phase 1 schema files must include operation contract, effect kind, phase boundary, workflow-state snapshot, and language task common I/O.
- All 19 `required_action` values must map to operation contract metadata without hiding branchy actions behind a representative value.
- The mapping must include required_action, effect_kind, approval_required, phase_boundary, sequence, actor, branching, and referenced pre/postconditions.
- Simple approval-required operations include `commit_stop_point`, `apply_approved_reopen_plan`, `run_reopen_start`, `advance_reopen_after_commit_stop_point`, `advance_reopen_after_approval_stop_point`, `finalize_reopen`, and `repair_workflow_state`.
- `record_human_decision` records a decision and is not itself approval for the target operation.
- `run_reopen_pending_gate` branches by active gate; drafting is separate as `run_reopen_drafting`.
- `run_maintenance` and `run_workflow_stage` are compound operations with branch conditions, internal steps, max side effect, and approval aggregation.
- Operation contract and operation registry / preflight must have one machine-readable source-of-truth boundary. Registry/preflight reads contract and does not execute, update, or consume approvals.
- Missing contract refs, stale digests, version drift, or duplicated source-of-truth fields must be detected.

Forbidden or high-risk actions:

- Do not duplicate side-effect / approval / phase-boundary fields across registry and contract as separate authorities.
- Do not treat `record_human_decision` completion as satisfying approval-required target operations.
- Do not downgrade required commit / approval boundaries to advisory warnings in runner-enabled paths.

### Requirement 14: approval gate, side-track stack, and workflow-state snapshot

Purpose: approval, unexpected side tracks, and current-state visibility must be machine-readable state, not implicit LLM interpretation.

Responsibility boundaries and acceptance criteria:

- Approval gate consists of `wait_for_human_decision`, `record_human_decision`, and subsequent `next --json` branching.
- Decision records distinguish approved, rejected, deferred, and changes_requested.
- Each decision binds target operation ID, required_action, artifact or staged file set digest, actor, timestamp, and source.
- Side track is a stack. Frames include frame ID, kind, parent, pusher, allowed scope/files, completion conditions, return_to, title, spawned_from, staged_file_set, and staged_file_digest.
- Staged file set/digest is captured on push, before pop, and before commit/push.
- Only top frame can pop; `next --json` resumes the immediate parent or mainline.
- `max_depth` is 2 by default; Phase 3 warns and Phase 5 blocks.
- `.reviewcompass/runtime/workflow-state-snapshot.yaml` is a `next --json` byproduct, not an authority replacing `next --json`.
- Snapshot includes schema_version, generated_by, generated_at, current_work, active_side_tracks, git_tree_summary, post_write_manifest_summary, and workflow_state_summary.
- Proxy decisions and human-only decisions must be mechanically distinct. Commit, push, spec.json update, phase approval, reopen finalize, and approval_required irreversible operation execution are human-only.
- Read-only operations and mutating operations must not be represented as the same operation.

Forbidden or high-risk actions:

- Do not let proxy_model replace human-only approval.
- Do not let stale snapshots authorize operations.
- Do not return to mainline after side-track pop if return_to or staged state cannot be verified.

### Requirement 15: structured effective prompt and audit

Purpose: effective prompts should be language-task specifications, not long unstructured instructions that smuggle machine operations into LLM text.

Responsibility boundaries and acceptance criteria:

- Prompt structure includes decision_point, preconditions_checked, language_task, postconditions, and on_completion.
- `language_task` includes document_kind, input, output_format, and constraints.
- Machine tasks belong to operation contract, preflight, runner, and guard, not prompt instructions.
- Phase 4 generates structured prompts from DISCIPLINE_MAP or successor registry while preserving `next_action.effective_prompt.effective_prompt_path`.
- First-layer prompt checks cover file/anchor existence, mandatory sections, length, unknown action kind, review-target/manifest match, output/postcondition consistency, machine-checked preconditions, and on_completion compatibility.
- Phase 6 LLM judge audit is auxiliary and must not automate final approval.

Forbidden or high-risk actions:

- Do not put commit, push, spec.json mutation, approval consumption, review-run artifact creation, or side-track mutation into the LLM language task.
- Do not treat semantic LLM judge audit as final approval.

### Requirement 16: Phase 0-6 implementation plan

Purpose: mechanization of the selection and execution layers must be implemented in order without mixing future phases into one risky change.

Responsibility boundaries and acceptance criteria:

- Phase 0 is D-003 selection-layer work: 19-step priority, one required_action, invariant checks, and reopen plan compiler.
- Phase 0 starts after the minimum schemas from Requirement 2 AC10-11; other operation contract schemas can proceed in parallel.
- Phase 0 completion requires the six D-003 failure tests and mechanical workflow-state repair detection.
- Phase 1 defines vocabularies and schemas without changing behavior.
- Phase 2 introduces read-only registry.
- Phase 3 introduces advisory preflight.
- Phase 4 structures effective prompts.
- Phase 5 turns selected warnings into blocks.
- Phase 6 adds optional LLM judge audit.
- Each Phase ends only after `next --json` can return normal work or an explicit stop state. Do not mix phases in one commit.
- The current active reopen scope is workflow-management requirements to design/tasks/implementation. `spec.json.reopened` is history, not active scope.
- Consumer / derivative impacts to other features must be checked during review-wave.
- proxy_model triage application depends on evidence completeness, finding/cluster coverage, approval gate records, operation contract approval_required, review-wave evidence, and human-only boundaries, not provider/model names.
- Human-required evidence always outranks proxy approval.

Forbidden or high-risk actions:

- Do not use `spec.json.reopened` alone as active reopen scope.
- Do not let proxy_model decisions pass human-required gates.
- Do not complete a phase with unresolved review-wave impact evidence or missing active-scope evidence.

## Current Design Summary

### Requirement 13 design mapping

`design.md` defines five Phase 1 schema files, separates `effect_kind` from `approval_required`, sets the logical operation contract structure, chooses `stages/operation-contracts.yaml` as the operation contract physical authority, and assigns `stages/operation-registry.yaml` to registry / preflight binding. It states that registry/preflight references contract ID plus digest/version and must not redefine contract fields. It branches `run_reopen_pending_gate` by active gate, separates `run_reopen_drafting`, and represents compound operations with a single `effect_kind`, `max_effect_kind`, `sequence.internal_steps[]`, and `branching.branches[]`.

### Requirement 14 design mapping

`design.md` defines approval gate records, decision values, target binding, decision_scope values (`human_only`, `proxy_allowed`, `advisory_only`), the initial human-only set, side-track frame fields, LIFO pop rule, staged file digest checks, max depth policy, snapshot structure, snapshot non-authority, and read-only versus mutating storage boundaries.

### Requirement 15 design mapping

`design.md` keeps existing Markdown effective prompts as compatibility output and defines a structured prompt schema for Phase 4. It separates `preconditions_checked` from LLM work, defines `language_task`, lists first-layer prompt checks, and limits LLM judge audit to an auxiliary gap-finding role.

### Requirement 16 design mapping

`design.md` defines Phase 0-6 anchors and completion conditions, distinguishes active reopen scope from `spec.json.reopened`, requires review-wave impact checks for consumer features, and defines proxy triage operation family plus human-required predicate priority.

## Required Checks

1. Check whether Requirement 13's purpose, responsibility boundaries, acceptance criteria, and forbidden actions are carried into design without omission, weakening, unsupported additions, or drift.
2. Check whether design settles the operation registry / operation contract source-of-truth boundary enough that tasks do not need to invent it later.
3. Check whether `record_human_decision` remains a decision-record operation and does not satisfy target operation approval by itself.
4. Check whether `run_reopen_pending_gate`, `run_reopen_drafting`, `run_maintenance`, and `run_workflow_stage` are designed with enough branching/compound-operation structure to avoid LLM inference.
5. Check whether Requirement 14's approval gate, side-track stack, workflow-state snapshot, proxy/human boundary, and read-only/mutating boundary are carried into design without omission or drift.
6. Check whether design gives a clear enough human-only / proxy-allowed boundary for downstream tasks and implementation, especially commit, push, spec.json update, phase approval, reopen finalize, and approval_required operation execution.
7. Check whether Requirement 15's structured effective prompt model keeps machine operations outside language tasks and makes prompt audit mechanically checkable.
8. Check whether Requirement 16's Phase 0-6 sequencing, active reopen scope distinction, impact review scope, and proxy triage decision predicates are design-level decisions rather than task-level guesses.
9. Check whether design contradicts Requirement 12 operation registry / preflight.
10. Check whether design overclaims implementation that has not happened yet.
11. Check whether current state records accurately say design drafting is complete while leaving design triad-review, review-wave, alignment, approval, commit, and push incomplete.

## Out Of Scope

- Do not request implementation code changes during this design triad-review.
- Do not judge `tasks.md` correctness except when a design omission would force tasks to invent design authority.
- Do not decide cross-feature impact; that belongs to design review-wave.
- Do not approve commit, push, spec.json mutation beyond the review target, or phase transition.

## Finding Policy

- Report `must-fix` when a requirement purpose, responsibility boundary, acceptance criterion, or forbidden action is missing, weakened, contradicted, or replaced by unsupported design behavior.
- Report `must-fix` when design leaves registry/contract authority, proxy/human authority, or active reopen scope ambiguous enough that tasks or implementation must invent policy.
- Report `must-fix` when state records falsely complete an uncompleted gate or allow bypassing required human approval.
- Report `should-fix` for ambiguity likely to force repeated manual judgment, weak traceability, or unclear schema/state boundaries.
- Return no finding when design is traceable, internally consistent, and correctly scoped for design drafting.


# Output contract
Return YAML only.
The top-level key must be exactly findings.
Do not use review: as a wrapper.
Do not use result:, metadata:, or summary: as wrappers.
Do not wrap the YAML in Markdown code fences.
Do not include ```yaml or any other fence marker.
Do not write explanatory prose before or after the YAML.

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

If there are no findings, return exactly:

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
.reviewcompass/specs/workflow-management/reviews/2026-06-20-workflow-management-design-vertical-redo-review-run/review-target.md

# Target document
---
review_target: workflow-management design vertical redo
phase: design
gate: stages/design.yaml#triad-review
feature: workflow-management
date: 2026-06-20
source_documents:
  - .reviewcompass/specs/workflow-management/requirements.md
  - .reviewcompass/specs/workflow-management/design.md
  - .reviewcompass/specs/workflow-management/spec.json
  - stages/in-progress/reopen-procedure-2026-06-19.yaml
  - docs/reviews/reopen-classification-2026-06-19-wm-requirement-13-16-vertical-redo.md
  - docs/operations/SESSION_WORKFLOW_GUIDE.md#vertical-intent-transfer-review
effective_prompt:
  path: .reviewcompass/runtime/effective-prompts/next_action_kind-reopen_in_progress__workflow_stage-triad-review__reopen_required_action-run_reopen_pending_gate.prompt.md
  sha256: 6d4374ac39164c2001ca6a34fb9029ee3a6816febd15a5da7b26208ca17b4a11
---

# Review Target: workflow-management design / Requirement 13-16 vertical redo

## Review Purpose

Review whether the current `workflow-management` design document correctly carries approved Requirement 13 through Requirement 16 into design-level decisions. This is a vertical intent transfer review, not a reuse of the older design run.

The current reopen exists because a tasks-granularity reopen exposed upstream design authority problems. The review must therefore check whether requirements purpose, responsibility boundaries, acceptance criteria, forbidden actions, and unresolved design decisions are present in `design.md` without omission, weakening, unsupported additions, or drift.

## Current Run Inputs

Current file digests at review-target preparation:

| path | sha256 |
|---|---|
| `.reviewcompass/specs/workflow-management/requirements.md` | `e7621e6d56a3ef42085e2864a88366d670e55c304668dd21f48dde32411e13f3` |
| `.reviewcompass/specs/workflow-management/design.md` | `cc668ad714baf00bb6edd5e108cd6e1b3a9a673dac88e0cfe947e58fa8643ef8` |
| `.reviewcompass/specs/workflow-management/spec.json` | `ae674dec950ea5c0e5f8a1dea9935c489c54d9d0da0c85a46b96b0b3a617d9da` |
| `stages/in-progress/reopen-procedure-2026-06-19.yaml` | `65af6cb1368fa7be978234bce32bc990cf71c3efc52ac0d83f20d64bf33ba9e0` |
| effective prompt | `6d4374ac39164c2001ca6a34fb9029ee3a6816febd15a5da7b26208ca17b4a11` |

## Why This Review Is Being Re-run

The older design run used stale inputs. Since then, requirements triad-review changed `requirements.md`, requirements review-wave / alignment / approval advanced the reopen, the effective prompt changed to include vertical-intent transfer requirements, and the current in-progress YAML now records design drafting completion. This run must therefore use the current requirements/design/spec/reopen state.

Classification record summary:

- The current R-0 reopen is based on Requirement 13-16.
- The earlier tasks-granularity reopen was superseded because vertical intent review showed the issue was not only task detail.
- Two design-authority questions must be checked at design level:
  - Whether the operation registry / operation contract source-of-truth split, digest/version synchronization, and read-only preflight boundary are design-authorized rather than task-invented.
  - Whether proxy / human decision boundaries are settled across Requirement 14, Requirement 16, and approval discipline rather than left for tasks or implementation to infer.

## Upstream Requirements Summary

### Requirement 13: operation contract vocabulary and required_action mapping

Purpose: a maintainer should execute the one action selected by `next --json` based on operation contracts, not memory or precedent. The selection layer says what to do; the execution layer defines how to do it through side effects, approval, preconditions, and postconditions.

Responsibility boundaries and acceptance criteria:

- Defines `effect_kind`, `approval_required`, `phase_boundary`, `sequence`, `preconditions`, and `postconditions`.
- `effect_kind` has baseline values `read`, `write`, `state_mutation`, and `external_call`.
- `approval_required` is independent from `effect_kind`.
- Phase 1 schema files must include operation contract, effect kind, phase boundary, workflow-state snapshot, and language task common I/O.
- All 19 `required_action` values must map to operation contract metadata without hiding branchy actions behind a representative value.
- The mapping must include required_action, effect_kind, approval_required, phase_boundary, sequence, actor, branching, and referenced pre/postconditions.
- Simple approval-required operations include `commit_stop_point`, `apply_approved_reopen_plan`, `run_reopen_start`, `advance_reopen_after_commit_stop_point`, `advance_reopen_after_approval_stop_point`, `finalize_reopen`, and `repair_workflow_state`.
- `record_human_decision` records a decision and is not itself approval for the target operation.
- `run_reopen_pending_gate` branches by active gate; drafting is separate as `run_reopen_drafting`.
- `run_maintenance` and `run_workflow_stage` are compound operations with branch conditions, internal steps, max side effect, and approval aggregation.
- Operation contract and operation registry / preflight must have one machine-readable source-of-truth boundary. Registry/preflight reads contract and does not execute, update, or consume approvals.
- Missing contract refs, stale digests, version drift, or duplicated source-of-truth fields must be detected.

Forbidden or high-risk actions:

- Do not duplicate side-effect / approval / phase-boundary fields across registry and contract as separate authorities.
- Do not treat `record_human_decision` completion as satisfying approval-required target operations.
- Do not downgrade required commit / approval boundaries to advisory warnings in runner-enabled paths.

### Requirement 14: approval gate, side-track stack, and workflow-state snapshot

Purpose: approval, unexpected side tracks, and current-state visibility must be machine-readable state, not implicit LLM interpretation.

Responsibility boundaries and acceptance criteria:

- Approval gate consists of `wait_for_human_decision`, `record_human_decision`, and subsequent `next --json` branching.
- Decision records distinguish approved, rejected, deferred, and changes_requested.
- Each decision binds target operation ID, required_action, artifact or staged file set digest, actor, timestamp, and source.
- Side track is a stack. Frames include frame ID, kind, parent, pusher, allowed scope/files, completion conditions, return_to, title, spawned_from, staged_file_set, and staged_file_digest.
- Staged file set/digest is captured on push, before pop, and before commit/push.
- Only top frame can pop; `next --json` resumes the immediate parent or mainline.
- `max_depth` is 2 by default; Phase 3 warns and Phase 5 blocks.
- `.reviewcompass/runtime/workflow-state-snapshot.yaml` is a `next --json` byproduct, not an authority replacing `next --json`.
- Snapshot includes schema_version, generated_by, generated_at, current_work, active_side_tracks, git_tree_summary, post_write_manifest_summary, and workflow_state_summary.
- Proxy decisions and human-only decisions must be mechanically distinct. Commit, push, spec.json update, phase approval, reopen finalize, and approval_required irreversible operation execution are human-only.
- Read-only operations and mutating operations must not be represented as the same operation.

Forbidden or high-risk actions:

- Do not let proxy_model replace human-only approval.
- Do not let stale snapshots authorize operations.
- Do not return to mainline after side-track pop if return_to or staged state cannot be verified.

### Requirement 15: structured effective prompt and audit

Purpose: effective prompts should be language-task specifications, not long unstructured instructions that smuggle machine operations into LLM text.

Responsibility boundaries and acceptance criteria:

- Prompt structure includes decision_point, preconditions_checked, language_task, postconditions, and on_completion.
- `language_task` includes document_kind, input, output_format, and constraints.
- Machine tasks belong to operation contract, preflight, runner, and guard, not prompt instructions.
- Phase 4 generates structured prompts from DISCIPLINE_MAP or successor registry while preserving `next_action.effective_prompt.effective_prompt_path`.
- First-layer prompt checks cover file/anchor existence, mandatory sections, length, unknown action kind, review-target/manifest match, output/postcondition consistency, machine-checked preconditions, and on_completion compatibility.
- Phase 6 LLM judge audit is auxiliary and must not automate final approval.

Forbidden or high-risk actions:

- Do not put commit, push, spec.json mutation, approval consumption, review-run artifact creation, or side-track mutation into the LLM language task.
- Do not treat semantic LLM judge audit as final approval.

### Requirement 16: Phase 0-6 implementation plan

Purpose: mechanization of the selection and execution layers must be implemented in order without mixing future phases into one risky change.

Responsibility boundaries and acceptance criteria:

- Phase 0 is D-003 selection-layer work: 19-step priority, one required_action, invariant checks, and reopen plan compiler.
- Phase 0 starts after the minimum schemas from Requirement 2 AC10-11; other operation contract schemas can proceed in parallel.
- Phase 0 completion requires the six D-003 failure tests and mechanical workflow-state repair detection.
- Phase 1 defines vocabularies and schemas without changing behavior.
- Phase 2 introduces read-only registry.
- Phase 3 introduces advisory preflight.
- Phase 4 structures effective prompts.
- Phase 5 turns selected warnings into blocks.
- Phase 6 adds optional LLM judge audit.
- Each Phase ends only after `next --json` can return normal work or an explicit stop state. Do not mix phases in one commit.
- The current active reopen scope is workflow-management requirements to design/tasks/implementation. `spec.json.reopened` is history, not active scope.
- Consumer / derivative impacts to other features must be checked during review-wave.
- proxy_model triage application depends on evidence completeness, finding/cluster coverage, approval gate records, operation contract approval_required, review-wave evidence, and human-only boundaries, not provider/model names.
- Human-required evidence always outranks proxy approval.

Forbidden or high-risk actions:

- Do not use `spec.json.reopened` alone as active reopen scope.
- Do not let proxy_model decisions pass human-required gates.
- Do not complete a phase with unresolved review-wave impact evidence or missing active-scope evidence.

## Current Design Summary

### Requirement 13 design mapping

`design.md` defines five Phase 1 schema files, separates `effect_kind` from `approval_required`, sets the logical operation contract structure, chooses `stages/operation-contracts.yaml` as the operation contract physical authority, and assigns `stages/operation-registry.yaml` to registry / preflight binding. It states that registry/preflight references contract ID plus digest/version and must not redefine contract fields. It branches `run_reopen_pending_gate` by active gate, separates `run_reopen_drafting`, and represents compound operations with a single `effect_kind`, `max_effect_kind`, `sequence.internal_steps[]`, and `branching.branches[]`.

### Requirement 14 design mapping

`design.md` defines approval gate records, decision values, target binding, decision_scope values (`human_only`, `proxy_allowed`, `advisory_only`), the initial human-only set, side-track frame fields, LIFO pop rule, staged file digest checks, max depth policy, snapshot structure, snapshot non-authority, and read-only versus mutating storage boundaries.

### Requirement 15 design mapping

`design.md` keeps existing Markdown effective prompts as compatibility output and defines a structured prompt schema for Phase 4. It separates `preconditions_checked` from LLM work, defines `language_task`, lists first-layer prompt checks, and limits LLM judge audit to an auxiliary gap-finding role.

### Requirement 16 design mapping

`design.md` defines Phase 0-6 anchors and completion conditions, distinguishes active reopen scope from `spec.json.reopened`, requires review-wave impact checks for consumer features, and defines proxy triage operation family plus human-required predicate priority.

## Required Checks

1. Check whether Requirement 13's purpose, responsibility boundaries, acceptance criteria, and forbidden actions are carried into design without omission, weakening, unsupported additions, or drift.
2. Check whether design settles the operation registry / operation contract source-of-truth boundary enough that tasks do not need to invent it later.
3. Check whether `record_human_decision` remains a decision-record operation and does not satisfy target operation approval by itself.
4. Check whether `run_reopen_pending_gate`, `run_reopen_drafting`, `run_maintenance`, and `run_workflow_stage` are designed with enough branching/compound-operation structure to avoid LLM inference.
5. Check whether Requirement 14's approval gate, side-track stack, workflow-state snapshot, proxy/human boundary, and read-only/mutating boundary are carried into design without omission or drift.
6. Check whether design gives a clear enough human-only / proxy-allowed boundary for downstream tasks and implementation, especially commit, push, spec.json update, phase approval, reopen finalize, and approval_required operation execution.
7. Check whether Requirement 15's structured effective prompt model keeps machine operations outside language tasks and makes prompt audit mechanically checkable.
8. Check whether Requirement 16's Phase 0-6 sequencing, active reopen scope distinction, impact review scope, and proxy triage decision predicates are design-level decisions rather than task-level guesses.
9. Check whether design contradicts Requirement 12 operation registry / preflight.
10. Check whether design overclaims implementation that has not happened yet.
11. Check whether current state records accurately say design drafting is complete while leaving design triad-review, review-wave, alignment, approval, commit, and push incomplete.

## Out Of Scope

- Do not request implementation code changes during this design triad-review.
- Do not judge `tasks.md` correctness except when a design omission would force tasks to invent design authority.
- Do not decide cross-feature impact; that belongs to design review-wave.
- Do not approve commit, push, spec.json mutation beyond the review target, or phase transition.

## Finding Policy

- Report `must-fix` when a requirement purpose, responsibility boundary, acceptance criterion, or forbidden action is missing, weakened, contradicted, or replaced by unsupported design behavior.
- Report `must-fix` when design leaves registry/contract authority, proxy/human authority, or active reopen scope ambiguous enough that tasks or implementation must invent policy.
- Report `must-fix` when state records falsely complete an uncompleted gate or allow bypassing required human approval.
- Report `should-fix` for ambiguity likely to force repeated manual judgment, weak traceability, or unclear schema/state boundaries.
- Return no finding when design is traceable, internally consistent, and correctly scoped for design drafting.

