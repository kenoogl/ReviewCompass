# Tasks Triad Review Target

criteria_id: workflow_management_tasks_vertical_intent_review_req_13_16
phase: tasks
gate: stages/tasks.yaml#triad-review
run_id: 2026-06-20-workflow-management-tasks-vertical-redo-review-run

## Review Purpose

Review whether `workflow-management/tasks.md` correctly translates approved Requirement 13 through Requirement 16, through the approved design decisions, into implementation-ready tasks T-016 through T-019.

This is a vertical intent transfer review:

`requirements.md -> design.md -> tasks.md`

The review target is `tasks.md`. `requirements.md`, `design.md`, `spec.json`, and `stages/in-progress/reopen-procedure-2026-06-19.yaml` are source materials for intent transfer and state consistency. Do not judge downstream implementation correctness in this gate.

## Source Materials Summary

### Requirement 13

purpose:
- `next --json` must return one selected action, and execution must be governed by operation contract rather than memory or precedent.

responsibility_boundaries:
- `stages/operation-contracts.yaml` is the operation contract source of truth.
- `stages/operation-registry.yaml` is registry / preflight binding source of truth.
- Registry / preflight may read contract and state evidence, but must not update contracts, run operations, consume approvals, create workflow state, or create review-run artifacts.
- Operation contract owns effect kind, approval requirement, phase boundary, sequence, branch/internal step semantics, preconditions, postconditions, side effects, max effect, output / side-effect fields, and approval aggregation.
- T-014 remains registry / preflight reference-side work; T-016 owns operation contract vocabulary, schema, and mapping.

acceptance_criteria:
- Define common schemas for effect kind, phase boundary, operation contract, workflow-state snapshot, and language task I/O.
- Map all 19 `required_action` values to operation contracts.
- Detect unmapped actions, unknown actions, duplicated source-of-truth fields, registry / contract digest drift, and missing contract IDs fail-closed.
- Model branchy operations including `run_maintenance`, `run_reopen_pending_gate`, and `run_workflow_stage`.

forbidden_actions:
- Do not duplicate operation contract fields into registry / preflight as a second source of truth.
- Do not make `approval_required` anything other than boolean.
- Do not treat preflight as mutating.
- Do not weaken commit-boundary or approval-boundary checks to WARN where design requires fail-closed.

unresolved_or_design_deferred_items:
- Detailed contract YAML and CLI implementation are tasks / implementation work, not design completion.

intended_target_phase_transfer:
- T-016 must name the owned files, first failing tests, implementation order, completion criteria, verification commands, and stopping conditions that preserve the contract / registry boundary and 19-action coverage.

### Requirement 14

purpose:
- Approval, side tracks, and workflow-state visibility must be machine-readable state, not conversational memory.

responsibility_boundaries:
- Approval gate record is the decision source of truth.
- Side track stack is side-track state source of truth.
- Workflow-state snapshot is audit / visualization support, not operation authority.
- Human-only approvals cannot be replaced by proxy_model.
- Read-only stack operations (`current` / `inspect`) must be separated from mutating operations (`push` / `pop` / `repair`).

acceptance_criteria:
- Approval gate records carry decision, decision_scope, target operation, target required_action, target digest / staged digest binding, source evidence, rationale, and consumed state.
- `decision_scope` is derived from operation contract and human-only override set, not freely chosen.
- Side track stack carries frame, parent, allowed files, return target, staged file set / digest, and max depth.
- Snapshot carries `next --json` source digest, workflow state, in-progress state, side tracks, staged / unstaged summaries, and post-write summary.

forbidden_actions:
- Do not allow proxy_model to approve commit, push, `spec.json` update, phase approval, reopen finalize, or `approval_required=true` irreversible operation execution.
- Do not treat stale or manually edited snapshot as authority.
- Do not allow non-LIFO side track pop or unresolved return-to state to continue normally.

unresolved_or_design_deferred_items:
- Exact runtime storage may evolve from existing maintenance in-progress files toward a stack schema, but read-only / mutating boundaries must remain stable.

intended_target_phase_transfer:
- T-017 must decompose approval gate, side track stack, and snapshot into TDD-ready tasks, with explicit human-only / proxy-allowed boundary tests and snapshot drift tests.

### Requirement 15

purpose:
- Effective prompts must be structured language-task artifacts, while machine tasks are handled by operation contract, preflight, runner, and guard.

responsibility_boundaries:
- `docs/operations/WORKFLOW_DISCIPLINE_MAP.yaml` owns prompt length bounds and decision-point source mapping.
- Prompt audit checks structure and source coverage, but does not own side-track depth, commit mixing, or operation preflight semantics.
- Review-run / role-run must record prompt manifest path / digest without deleting existing text prompt compatibility fields.

acceptance_criteria:
- Define language task I/O and effective prompt manifest schemas.
- Record source artifacts and SHA-256 coverage.
- Detect direct state mutation instructions, missing source digests, output schema mismatch, machine-task leakage, and forbidden on-completion routing.
- LLM judge audit is Phase 6 only and must not automate final approval.

forbidden_actions:
- Do not put commit, push, `spec.json` update, phase transition, review-run artifact creation, approval consume, side-track mutation, or operation execution into prompt on-completion instructions.
- Do not change prompt length bounds ad hoc in a task-specific review-run.

unresolved_or_design_deferred_items:
- Structured prompt manifest is additive during migration; text-only effective prompt compatibility remains.

intended_target_phase_transfer:
- T-018 must define schema files, prompt builder / audit files, first failing tests, review-run rounds recording requirements, and migration compatibility constraints.

### Requirement 16

purpose:
- Selection-layer and execution-layer mechanization must be implemented in Phase 0 through Phase 6 without mixing incompatible changes in one step.

responsibility_boundaries:
- Active reopen scope comes from reopen in-progress / completed records and downstream impact decisions, not from `spec.json.reopened` alone.
- Impact review scope is distinct from active reopen scope.
- Proxy_model decisions are evaluated by evidence completeness, coverage, approval gate, operation contract, review-wave evidence, and human-required predicate, not by provider/model name.
- Human-required evidence overrides proxy-approved or leave-as-is triage labels.

acceptance_criteria:
- Phase 0 covers D-003 unique action selection, 19-action priority, invariant checks, workflow-state repair detection, and reopen plan compiler / recompile behavior.
- Phase 1 covers schemas.
- Phase 2 covers read-only registry.
- Phase 3 covers advisory preflight.
- Phase 4 covers structured effective prompt.
- Phase 5 promotes selected advisory warnings to mechanical blocking.
- Phase 6 covers LLM judge audit.
- Human-required predicate includes human-only decision boundary, unresolved approval gate, `approval_required=true`, unresolved review-wave impact evidence, and downstream impact / scope consistency.

forbidden_actions:
- Do not treat `spec.json.reopened` as active reopen scope.
- Do not let proxy_model decision satisfy human-required decisions.
- Do not mark review-wave consumer impact complete without review-wave / carry-forward / downstream impact evidence.
- Do not mix phase exit criteria from multiple phases into one implementation commit.

unresolved_or_design_deferred_items:
- Phase plan schema, proxy triage decision schema, and consumer impact checker are tasks / implementation work.

intended_target_phase_transfer:
- T-019 must define phase-plan and proxy-decision artifacts, first failing tests, CLI checks, human-required priority tests, consumer impact tests, and explicit stopping conditions for scope or proxy-decision ambiguity.

## Required Checks

1. Check whether T-016 fully transfers Requirement 13 and design §Requirement 13 into task-level work, including operation contract / registry source-of-truth boundaries, all 19 `required_action` mappings, branch/internal step semantics, approval aggregation, side effects, pre/postconditions, and read-only preflight boundaries.
2. Check whether T-017 fully transfers Requirement 14 and design §Requirement 14 into task-level work, including approval gate record schema, human-only / proxy-allowed / advisory boundaries, digest binding, side track stack LIFO / return rules, snapshot drift detection, and read-only vs mutating operation separation.
3. Check whether T-018 fully transfers Requirement 15 and design §Requirement 15 into task-level work, including structured effective prompt manifest, language task I/O, source digest coverage, prompt audit, machine-task leakage checks, rounds recording, migration compatibility, and Phase 6 judge-audit limits.
4. Check whether T-019 fully transfers Requirement 16 and design §Requirement 16 into task-level work, including Phase 0-6 order, entry / exit criteria, forbidden operations, active reopen scope vs impact review scope, proxy triage decision completeness, human-required predicate precedence, and review-wave consumer impact blocking.
5. Check whether each task T-016 through T-019 has implementation-ready detail: owned files, prerequisite tasks, first failing tests, implementation order, completion conditions, verification commands, forbidden actions, and stop conditions.
6. Check whether tasks.md has stale counts, stale traceability rows, missing Requirement 13-16 coverage, inconsistent task IDs, or contradictory completion criteria.
7. Check whether tasks.md contradicts existing T-014 registry / preflight responsibilities, existing T-015 schema work, or design constraints by moving the wrong source of truth into the wrong task.
8. Check whether `spec.json` and `stages/in-progress/reopen-procedure-2026-06-19.yaml` show the correct state: requirements and design complete, tasks drafting complete, tasks triad-review / review-wave / alignment / approval incomplete, implementation incomplete, and recheck still pending for tasks / implementation.

## Out Of Scope

- Do not request implementation code changes in this tasks triad-review.
- Do not judge downstream implementation correctness.
- Do not require other features to be edited during this gate; cross-feature consumer impact belongs to tasks review-wave.
- Do not reopen requirements or design unless tasks.md exposes a real contradiction that cannot be fixed at tasks level.
- Do not judge unrelated wording outside Requirement 13 through Requirement 16 unless it directly breaks these tasks.

## Finding Policy

- Report `must-fix` for missing task coverage of approved requirements or approved design decisions, broken requirement-to-design-to-task traceability, stale workflow state that falsely claims an uncompleted gate, source-of-truth inversions that would make implementation unsafe, human/proxy boundary violations, or tasks that bypass required commit / approval / review boundaries.
- Report `should-fix` for ambiguity likely to cause repeated manual judgment, weak TDD completion criteria, unclear file ownership, weak phase ordering, or traceability that exists but is too coarse for implementation.
- Report `leave-as-is` or no finding when tasks are traceable, internally consistent, implementation-ready, and correctly scoped for a tasks drafting artifact.

## Output Requirements

Return findings as structured YAML-compatible content with these fields for each finding:

- `severity`: `ERROR`, `WARN`, or `INFO`
- `target_location`: file path and section
- `description`: plain-language problem statement
- `rationale`: why the issue matters for requirements -> design -> tasks transfer
- `recommendation`: the smallest scoped correction

If there are no substantive findings, return an explicit no-findings result and briefly state which checks passed.
