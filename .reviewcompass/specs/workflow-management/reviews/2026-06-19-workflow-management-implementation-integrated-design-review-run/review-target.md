# Implementation Triad Review Target

criteria_id: workflow_management_integrated_design_implementation_triad_review
phase: implementation
gate: stages/implementation.yaml#triad-review

## Review Purpose

Review whether `workflow-management` implementation drafting correctly and sufficiently prepares implementation work for approved Requirement 13 through Requirement 16 and tasks T-016 through T-019.

## Target Files

- `.reviewcompass/specs/workflow-management/implementation-drafting.md`
- `.reviewcompass/specs/workflow-management/tasks.md`
- `.reviewcompass/specs/workflow-management/design.md`
- `.reviewcompass/specs/workflow-management/requirements.md`
- `.reviewcompass/specs/workflow-management/spec.json`
- `stages/in-progress/reopen-procedure-2026-06-19.yaml`
- `docs/operations/SESSION_WORKFLOW_GUIDE.md`
- `AGENTS.md`

## Required Checks

1. Check traceability from Requirement 13 and T-016 to implementation drafting for operation contract vocabulary, `required_action` mapping, `effect_kind`, `phase_boundary`, preconditions, postconditions, side effects, and commit boundary enforcement.
2. Check traceability from Requirement 14 and T-017 to implementation drafting for approval gate records, proxy_model / human decision boundary, side track stack push / pop / current behavior, return conditions, workflow-state snapshot, staged file set / digest checks, and drift detection.
3. Check traceability from Requirement 15 and T-018 to implementation drafting for structured effective prompt manifest, language task I/O schema, prompt audit, source digest coverage, machine task separation, `on_completion` constraints, and review-run recording.
4. Check traceability from Requirement 16 and T-019 to implementation drafting for Phase 0 through Phase 6 implementation plan, phase entry / exit criteria, forbidden operation checks, proxy_model triage decision mechanization, human-required decision boundary, and review-wave consumer impact blocking.
5. Check whether the implementation drafting stays scoped as implementation preparation and does not claim implementation completion before code, schema, tests, and workflow guards are actually changed.
6. Check whether implementation drafting has enough TDD-ready detail: expected tests, owned files, prerequisites, completion conditions, dependency ordering, and stopping conditions for newly discovered judgment problems.
7. Check whether the current workflow records accurately reflect implementation drafting completion without prematurely marking implementation triad-review, review-wave, alignment, approval, implementation completion, commit, or push complete.
8. Check whether the newly added progress-reporting discipline is correctly scoped as a conversation/reporting rule and does not conflict with the workflow state source-of-truth rules.

## Out Of Scope

- Do not request implementation code changes in this triad-review.
- Do not judge unrelated wording outside the Requirement 13 through 16 implementation preparation unless it creates a direct contradiction.
- Do not require edits to other features during this gate; cross-feature impact belongs to implementation review-wave.

## Finding Policy

- Report `must-fix` for missing implementation preparation for approved requirements, broken traceability, stale state that falsely claims an uncompleted gate, contradictions that would make implementation unsafe, or text that bypasses required commit / approval / review boundaries.
- Report `should-fix` for ambiguity that could cause repeated manual judgment, unclear implementation ownership, weak TDD completion criteria, or weak traceability to requirements / design / tasks.
- Return no findings when the implementation drafting is traceable, internally consistent, and correctly scoped as an implementation preparation artifact.
