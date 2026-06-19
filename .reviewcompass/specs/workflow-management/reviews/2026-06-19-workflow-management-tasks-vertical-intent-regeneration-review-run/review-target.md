---
review_target: workflow-management tasks vertical intent regeneration
phase: tasks
gate: stages/tasks.yaml#triad-review
feature: workflow-management
date: 2026-06-19
baseline_review_run: .reviewcompass/specs/workflow-management/reviews/2026-06-19-workflow-management-tasks-granularity-regeneration-review-run.baseline-before-vertical-intent
source_documents:
  - .reviewcompass/specs/workflow-management/requirements.md
  - .reviewcompass/specs/workflow-management/design.md
  - .reviewcompass/specs/workflow-management/tasks.md
  - .reviewcompass/specs/workflow-management/spec.json
  - docs/operations/SESSION_WORKFLOW_GUIDE.md#vertical-intent-transfer-review
  - docs/operations/WORKFLOW_DISCIPLINE_MAP.yaml
---

# Review Target: workflow-management tasks / vertical intent regeneration

## Review Purpose

Review whether the regenerated `workflow-management` tasks now preserve upstream intent vertically from requirements to design to tasks, not merely whether `tasks.md` is detailed.

This review follows the new discipline in `SESSION_WORKFLOW_GUIDE.md#vertical-intent-transfer-review`: each phase review must check that upstream purpose, responsibility boundaries, acceptance criteria, and forbidden actions are inherited into the target artifact without omission, weakening, unsupported additions, or drift.

## Baseline For Comparison

The baseline review run is:

- `.reviewcompass/specs/workflow-management/reviews/2026-06-19-workflow-management-tasks-granularity-regeneration-review-run.baseline-before-vertical-intent`

Baseline same-root clusters were:

- C1: T-016 operation contract / registry ownership boundary.
- C2: T-017 approval / side track / snapshot persistence and mutation boundary.
- C3: T-019 human-required decision predicate.
- C4: tasks granularity, traceability, and state records adequate.

This review should identify whether the regenerated tasks reduce, resolve, or expose new issues compared with those baseline clusters.

## Target Files

- `.reviewcompass/specs/workflow-management/requirements.md`
- `.reviewcompass/specs/workflow-management/design.md`
- `.reviewcompass/specs/workflow-management/tasks.md`
- `.reviewcompass/specs/workflow-management/spec.json`
- `docs/operations/SESSION_WORKFLOW_GUIDE.md`
- `docs/operations/WORKFLOW_DISCIPLINE_MAP.yaml`
- `stages/in-progress/reopen-procedure-2026-06-19.yaml`

## Required Vertical Checks

1. Check whether T-016 carries Requirement 13's intent through design.md into tasks.md: `next --json` selected action must connect to operation contract; operation registry / preflight remains read-only confirmation; operation contract owns side effects, approval need, sequence, preconditions, and postconditions.
2. Check whether T-016 now avoids omission, weakening, drift, and unsupported additions in the relationship between `stages/operation-contracts.yaml` and `stages/operation-registry.yaml`, including the single-source-of-truth and digest / version synchronization rule.
3. Check whether T-017 carries Requirement 14's intent through design.md into tasks.md: approval, side track, and state visualization must be machine-readable state rather than conversation context; snapshot is not canonical; read-only and mutating operations are separated.
4. Check whether T-017 now defines enough implementation-ready tests and completion conditions for approval decision states, side track stack storage, push / pop / current mutation boundaries, return conditions, staged file digest checks, and snapshot staleness.
5. Check whether T-018 still carries Requirement 15's intent: structured effective prompt remains a language task specification, not a place for machine execution steps; prompt audit and review-run recording remain implementation-ready.
6. Check whether T-019 carries Requirement 16's intent through design.md into tasks.md: Phase 0-6 sequencing, active reopen scope vs history flag, impact review scope, proxy_model triage evidence completeness, and human-required boundary are machine-checkable.
7. Check whether T-019 now defines a concrete human-required predicate without allowing proxy_model to pass human-only decisions, and without tying the judgment to provider / model names.
8. Check whether the new discipline itself is wired into `WORKFLOW_DISCIPLINE_MAP.yaml` so future `next --json` / effective prompt generation includes vertical intent transfer checks for triad-review, review-wave, and alignment.
9. Check whether the regenerated tasks remain implementation-ready: target files, first failing tests, implementation order, completion conditions, verification commands, forbidden actions, and stop conditions.

## Out Of Scope

- Do not request implementation code changes during this tasks triad-review.
- Do not judge unrelated older tasks unless they directly affect Requirement 13 through 16 vertical intent transfer.
- Do not decide proxy_model triage or apply fixes; this review only reports findings for comparison.

## Finding Policy

- Report `must-fix` for any upstream intent that is missing, weakened, contradicted, or replaced by unsupported task-level behavior.
- Report `must-fix` for any stale state that falsely claims an uncompleted gate, or any bypass of required human approval / commit / review boundaries.
- Report `should-fix` for ambiguity likely to force implementation-time design judgment, weak red tests, unclear ownership, or weak machine-checkable predicates.
- Report `leave-as-is` or no finding when the regenerated tasks preserve vertical intent, remain implementation-ready, and improve on the baseline issues.
