# Tasks Triad Review Target

criteria_id: workflow_management_integrated_design_tasks_triad_review
phase: tasks
gate: stages/tasks.yaml#triad-review

## Review Purpose

Review whether `workflow-management` tasks drafting correctly and sufficiently reflects approved Requirement 13 through Requirement 16 from the integrated design follow-up.

## Target Files

- `.reviewcompass/specs/workflow-management/tasks.md`
- `.reviewcompass/specs/workflow-management/design.md`
- `.reviewcompass/specs/workflow-management/requirements.md`
- `.reviewcompass/specs/workflow-management/spec.json`
- `stages/in-progress/reopen-procedure-2026-06-19.yaml`
- `docs/notes/2026-06-18-integrated-design-selection-execution-layers.md`
- `docs/notes/working/2026-06-18-mechanized-workflow-execution-design.md`
- `docs/notes/working/2026-06-19-integrated-design-requirements-missing.md`
- `docs/notes/working/2026-06-19-proxy-model-triage-cost-issues.md`

## Required Checks

1. Check traceability from Requirement 13 to tasks for operation contract vocabulary, `required_action` mapping, `effect_kind`, `phase_boundary`, preconditions / postconditions, side effects, and commit boundary enforcement.
2. Check traceability from Requirement 14 to tasks for approval gate records, proxy_model / human decision boundary, side track stack push / pop / current behavior, return conditions, workflow-state snapshot, staged file set / digest checks, and drift detection.
3. Check traceability from Requirement 15 to tasks for structured effective prompt manifest, language task I/O schema, prompt audit, source digest coverage, machine task separation, `on_completion` constraints, and review-run recording.
4. Check traceability from Requirement 16 to tasks for Phase 0 through Phase 6 implementation plan, phase entry / exit criteria, forbidden operation checks, proxy_model triage decision mechanization, human-required decision boundary, and review-wave consumer impact blocking.
5. Check whether T-016 through T-019 have enough task-level implementation detail: owned files, prerequisites, completion conditions, and TDD-oriented test requirements.
6. Check whether the tasks document still has stale counts, stale completion criteria, missing traceability rows, or inconsistent references after adding T-016 through T-019.
7. Check whether the tasks contradict existing T-014 operation registry / preflight responsibilities or incorrectly move implementation behavior into a tasks drafting artifact.
8. Check whether `spec.json` and `stages/in-progress/reopen-procedure-2026-06-19.yaml` accurately reflect tasks drafting completion without prematurely marking tasks triad-review, review-wave, alignment, approval, implementation, commit, or push complete.

## Out Of Scope

- Do not request implementation changes in this tasks triad-review.
- Do not judge unrelated wording outside the Requirement 13 through 16 tasks expansion unless it creates a direct contradiction.
- Do not require edits to other features during this gate; cross-feature impact belongs to tasks review-wave.

## Finding Policy

- Report `must-fix` for missing task coverage for approved requirements, broken requirement traceability, stale state that falsely claims an uncompleted gate, contradictions that would make implementation unsafe, or task text that bypasses required commit / approval / review boundaries.
- Report `should-fix` for ambiguity that could cause repeated manual judgment, unclear task ownership, weak TDD completion criteria, or weak traceability to requirements / design.
- Return no findings when the tasks are traceable, internally consistent, and correctly scoped for a tasks drafting artifact.
