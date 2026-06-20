# Tasks Triad Review Target

criteria_id: workflow_management_tasks_vertical_intent_review_req_13_16_v3
phase: tasks
gate: stages/tasks.yaml#triad-review
run_id: 2026-06-20-workflow-management-tasks-vertical-redo-review-run-v3

## Scope Rule

Do not use full `requirements.md` or full `design.md` as review targets.

Use the verbatim source excerpt files listed below. They are original excerpts from the approved source documents, not LLM-authored restatements.

## Review Purpose

Review whether `workflow-management/tasks.md` correctly translates Requirement 13 through Requirement 16, through the approved design decisions, into implementation-ready tasks T-016 through T-019.

This is a vertical intent transfer review:

`requirements verbatim excerpts -> design verbatim excerpts -> tasks.md`

The review target is `tasks.md`. The requirements/design excerpt files are source materials for intent transfer only. `spec.json` and the reopen state file are source materials for workflow state consistency only.

## Target Files For Execution

Pass these as `--target` files:

- `.reviewcompass/specs/workflow-management/tasks.md`
- `.reviewcompass/specs/workflow-management/reviews/2026-06-20-workflow-management-tasks-vertical-redo-review-run-v3/source-excerpts/requirements-req13-16.verbatim.md`
- `.reviewcompass/specs/workflow-management/reviews/2026-06-20-workflow-management-tasks-vertical-redo-review-run-v3/source-excerpts/design-req13-16.verbatim.md`
- `.reviewcompass/specs/workflow-management/spec.json`
- `stages/in-progress/reopen-procedure-2026-06-19.yaml`

Do not pass full `.reviewcompass/specs/workflow-management/requirements.md`.
Do not pass full `.reviewcompass/specs/workflow-management/design.md`.

## Source Material Contract

- `requirements-req13-16.verbatim.md` is the original text of `requirements.md` lines 217-297.
- `design-req13-16.verbatim.md` is the original text of `design.md` lines 1563-2087.
- These files must be treated as source materials, not review targets.
- Do not evaluate whether the requirements or design text should be changed unless `tasks.md` exposes a contradiction that cannot be resolved at the tasks level.
- Do not infer missing upstream intent from memory, previous conversations, or LLM-authored restatements.

## Source Field Index

This section is an index into the verbatim excerpt files, not a restatement of their content.

purpose:
- Read the Objective paragraphs in `requirements-req13-16.verbatim.md`.
- Read the opening paragraphs of each Requirement 13-16 design model in `design-req13-16.verbatim.md`.

responsibility_boundaries:
- Read the source-of-truth, read-only / mutating, approval, side-track, prompt, phase, and proxy boundary statements in the verbatim excerpt files.

acceptance_criteria:
- Read the numbered acceptance criteria in `requirements-req13-16.verbatim.md`.
- Read the schema, table, baseline, and phase-plan requirements in `design-req13-16.verbatim.md`.

forbidden_actions:
- Treat prohibitions in the verbatim excerpt files as binding when judging `tasks.md`.
- Do not infer additional prohibitions from memory or prior conversation.

unresolved_or_design_deferred_items:
- Treat implementation-phase schema, contract, checker, and CLI work that the verbatim excerpts leave to tasks / implementation as deferred source material.

intended_target_phase_transfer:
- Judge only whether `tasks.md` carries the verbatim excerpt requirements and design decisions into T-016 through T-019 at implementation-ready task granularity.

## Required Checks

1. Check whether T-016 transfers Requirement 13 and the approved design excerpt into implementation-ready task work, including operation contract / registry boundaries, all 19 `required_action` mappings, branch/internal step semantics, approval aggregation, side effects, preconditions / postconditions, and read-only preflight boundaries.
2. Check whether T-017 transfers Requirement 14 and the approved design excerpt into implementation-ready task work, including approval gate record schema, human-only / proxy-allowed / advisory boundaries, digest binding, side track stack LIFO / return rules, snapshot drift detection, and read-only vs mutating operation separation.
3. Check whether T-018 transfers Requirement 15 and the approved design excerpt into implementation-ready task work, including structured effective prompt manifest, language task I/O, source digest coverage, prompt audit, machine-task leakage checks, rounds recording, migration compatibility, and Phase 6 judge-audit limits.
4. Check whether T-019 transfers Requirement 16 and the approved design excerpt into implementation-ready task work, including Phase 0-6 order, entry / exit criteria, forbidden operations, active reopen scope vs impact review scope, proxy triage decision completeness, human-required predicate precedence, and review-wave consumer impact blocking.
5. Check whether T-016 through T-019 each have task-level implementation detail: owned files, prerequisite tasks, first failing tests, implementation order, completion conditions, verification commands, forbidden actions, and stop conditions.
6. Check whether tasks.md has stale counts, stale traceability rows, missing Requirement 13-16 coverage, inconsistent task IDs, or contradictory completion criteria.
7. Check whether tasks.md contradicts existing T-014 registry / preflight responsibilities, existing T-015 schema work, or the approved design excerpt by moving the wrong source of truth into the wrong task.
8. Check whether `spec.json` and `stages/in-progress/reopen-procedure-2026-06-19.yaml` show the correct state: requirements and design complete, tasks drafting complete, tasks triad-review / review-wave / alignment / approval incomplete, implementation incomplete, and recheck still pending for tasks / implementation.

## Out Of Scope

- Do not review full requirements.md.
- Do not review full design.md.
- Do not request implementation code changes in this tasks triad-review.
- Do not judge downstream implementation correctness.
- Do not require other features to be edited during this gate; cross-feature consumer impact belongs to tasks review-wave.
- Do not reopen requirements or design unless tasks.md exposes a real contradiction that cannot be fixed at tasks level.
- Do not judge unrelated wording outside Requirement 13 through Requirement 16 unless it directly breaks these tasks.

## Finding Policy

- Report `must-fix` for missing task coverage of approved upstream excerpts or approved design excerpts, broken requirement-to-design-to-task traceability, stale workflow state that falsely claims an uncompleted gate, source-of-truth inversions that would make implementation unsafe, human/proxy boundary violations, or tasks that bypass required commit / approval / review boundaries.
- Report `should-fix` for ambiguity likely to cause repeated manual judgment, weak TDD completion criteria, unclear file ownership, weak phase ordering, or traceability that exists but is too coarse for implementation.
- Report `leave-as-is` or no finding when tasks are traceable, internally consistent, implementation-ready, and correctly scoped for a tasks drafting artifact.

## Output Requirements

Return findings as structured YAML-compatible content with these fields for each finding:

- `severity`: `ERROR`, `WARN`, or `INFO`
- `target_location`: file path and section
- `description`: plain-language problem statement
- `rationale`: why the issue matters for requirements excerpt -> design excerpt -> tasks transfer
- `recommendation`: the smallest scoped correction

If there are no substantive findings, return an explicit no-findings result and briefly state which checks passed.
