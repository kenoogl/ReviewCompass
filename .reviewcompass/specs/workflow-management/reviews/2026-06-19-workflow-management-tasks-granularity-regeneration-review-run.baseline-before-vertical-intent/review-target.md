---
review_target: workflow-management tasks granularity regeneration
phase: tasks
gate: stages/tasks.yaml#triad-review
feature: workflow-management
date: 2026-06-19
source_commit: e239f6f4
source_documents:
  - .reviewcompass/specs/workflow-management/requirements.md
  - .reviewcompass/specs/workflow-management/design.md
  - .reviewcompass/specs/workflow-management/tasks.md
  - .reviewcompass/specs/workflow-management/spec.json
  - stages/in-progress/reopen-procedure-2026-06-19.yaml
  - docs/reviews/reopen-classification-2026-06-19-wm-task-granularity-regeneration.md
---

# Review Target: workflow-management tasks / granularity regeneration

## Review Purpose

Review whether the regenerated `workflow-management` tasks are now detailed enough to enter implementation drafting directly without a separate `implementation-drafting.md` canonical artifact.

This review is limited to the 2026-06-19 A-0 reopen scope: tasks.md task granularity for T-016 through T-019, plus the state files that mark tasks drafting complete and keep later gates pending.

## Background

- User requested continuation from `TODO_NEXT_SESSION.md`.
- Reopen classification was recorded as A-0 in `docs/reviews/reopen-classification-2026-06-19-wm-task-granularity-regeneration.md`.
- Commit `e239f6f4` saved the regenerated tasks and reopen state at the commit stop point.
- After the stop point was consumed, `spec.json` now marks only `workflow_state.tasks.drafting=true`; tasks triad-review, review-wave, alignment, approval, and all implementation stages remain false.
- `stages/in-progress/reopen-procedure-2026-06-19.yaml` now records `drafting_completed_gates: [stages/tasks.yaml#drafting]` and keeps the next gate at `stages/tasks.yaml#triad-review`.

## Target Files

- `.reviewcompass/specs/workflow-management/requirements.md`
- `.reviewcompass/specs/workflow-management/design.md`
- `.reviewcompass/specs/workflow-management/tasks.md`
- `.reviewcompass/specs/workflow-management/spec.json`
- `stages/in-progress/reopen-procedure-2026-06-19.yaml`
- `docs/reviews/reopen-classification-2026-06-19-wm-task-granularity-regeneration.md`

## Required Checks

1. Check whether T-016 through T-019 each contain enough implementation-ready detail: implementation target files, first failing tests, implementation order, completion conditions, verification commands, forbidden actions, and stop conditions.
2. Check whether the regenerated tasks let implementation drafting proceed by writing tests and implementation code directly from `tasks.md`, without requiring a separate canonical `implementation-drafting.md`.
3. Check whether T-016 correctly owns operation contract vocabulary, `required_action` mapping, `effect_kind`, `phase_boundary`, operation contract schema, preconditions / postconditions, side effects, and commit boundary enforcement without overwriting T-014's operation registry / preflight responsibilities.
4. Check whether T-017 gives implementation-ready coverage for approval gates, proxy_model / human decision boundary, side track stack push / pop / current behavior, return conditions, workflow-state snapshots, staged file set / digest checks, and drift detection.
5. Check whether T-018 gives implementation-ready coverage for structured effective prompt manifests, language task I/O schema, prompt audit, source digest coverage, machine task separation, `on_completion` constraints, and review-run recording compatibility.
6. Check whether T-019 gives implementation-ready coverage for Phase 0 through Phase 6 implementation plan, phase entry / exit criteria, forbidden operation checks, proxy_model triage decision mechanization, human-required decision boundary, and review-wave consumer impact blocking.
7. Check whether T-016 through T-019 remain traceable to requirements / design Requirement 13 through Requirement 16 and do not introduce behavior that contradicts approved upstream documents.
8. Check whether `spec.json` and `stages/in-progress/reopen-procedure-2026-06-19.yaml` accurately reflect only tasks drafting completion, without prematurely marking tasks triad-review, review-wave, alignment, approval, implementation, commit, or push complete.
9. Check whether the task granularity discipline stated near the top of `tasks.md` is actually satisfied by T-016 through T-019, including the rule that each task can be worked from test to implementation to commit as a coherent unit.

## Out Of Scope

- Do not request implementation code changes during this tasks triad-review.
- Do not judge unrelated older tasks unless they directly contradict T-016 through T-019 or the task granularity policy.
- Do not reopen requirements or design unless T-016 through T-019 are untraceable or contradictory against the already approved upstream documents.
- Do not decide proxy_model triage or apply fixes; this review only reports findings for human presentation.

## Finding Policy

- Report `must-fix` for missing Requirement 13 through 16 task coverage, task text that is not implementation-ready, stale state that falsely claims an uncompleted gate, contradictions with approved requirements / design, or any bypass of commit / approval / review boundaries.
- Report `should-fix` for ambiguity that is likely to cause manual judgment during implementation, unclear task ownership, weak TDD starting tests, weak verification commands, or responsibility overlap with earlier tasks.
- Report `leave-as-is` or no finding when the regenerated tasks are traceable, implementation-ready, and correctly scoped for a tasks drafting artifact.
