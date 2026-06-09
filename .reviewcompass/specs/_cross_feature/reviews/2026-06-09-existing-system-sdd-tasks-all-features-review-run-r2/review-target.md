---
run_id: 2026-06-09-existing-system-sdd-tasks-all-features-review-run-r2
phase: tasks.triad-review
features:
  - foundation
  - runtime
  - evaluation
  - analysis
  - workflow-management
  - self-improvement
  - conformance-evaluation
reopen_procedure: stages/in-progress/reopen-procedure-2026-06-09-existing-system-sdd-code-drift.yaml
supersedes_review_run: .reviewcompass/specs/_cross_feature/reviews/2026-06-09-existing-system-sdd-tasks-all-features-review-run
prior_design_review_run: .reviewcompass/specs/_cross_feature/reviews/2026-06-09-existing-system-sdd-design-all-features-review-run-r2
---

# Tasks triad-review target r2: existing-system SDD code drift

## Review Purpose

Review whether the tasks-stage fixes after the first tasks triad-review are sufficient to complete `stages/tasks.yaml#triad-review`.

## Prior Tasks Review Findings

The prior review produced these clusters:

- C1 must-fix: all seven features need explicit tasks-stage impact determinations.
- C2 should-fix: clarify whether foundation owns the new state/schema contract.
- C3 should-fix: clarify whether analysis must consume the new T-016 candidate output.
- C4 should-fix: clarify CE T-016 to WM T-007 handoff, especially for tasks-phase candidates.
- C5/C6 leave-as-is: review-target formatting and positive confirmations.

## Fixes Under Review

### Cross-feature impact evidence

New artifact:

- `.reviewcompass/specs/_cross_feature/reviews/2026-06-09-existing-system-sdd-tasks-all-features-review-run/tasks-impact-decisions.md`

It records all seven feature determinations:

- conformance-evaluation: tasks.md updated.
- workflow-management: tasks.md updated.
- foundation: no tasks.md body change required because `stages/in-progress.schema.json` remains workflow-management-owned and is not promoted to foundation shared schemas in this reopen chain.
- runtime: no tasks.md body change required.
- evaluation: no tasks.md body change required.
- analysis: no tasks.md body change required because T-016 candidate flow is CE to WM for workflow propagation, not a reporting intake requirement in this reopen chain.
- self-improvement: no tasks.md body change required.

### conformance-evaluation tasks.md

T-016 now says:

- When `downstream_impact_candidate` or `implementation_change_candidate` points to tasks phase, CE still does not update tasks.md directly.
- CE passes candidate ID and evidence references to workflow-management reopen.
- Completion criteria explicitly keep tasks phase candidates on the same WM handoff path.

### workflow-management tasks.md

T-007 now says:

- CE-origin `downstream_impact_candidate` or `implementation_change_candidate` for tasks phase is read by candidate ID, target feature, target phase, and evidence refs.
- T-007 performs the receptacle decision and converts the candidate to reopen `pending_gates`.
- It does not directly implement the candidate.

T-008 now says:

- `completed_gates`, `drafting_completed_gates`, and `downstream_impact_decisions` are owned by workflow-management `stages/in-progress.schema.json`.
- Foundation tasks.md is not changed unless these fields are later promoted to shared schemas.

## Review Criteria

Classify findings as CRITICAL, ERROR, WARN, or INFO.

Use these labels in rationale when applicable:

- `must-fix`: blocks tasks triad-review completion.
- `should-fix`: should be considered in this reopen chain but may be handled before later tasks gates.
- `leave-as-is`: record only.

Check especially:

1. Whether C1 is resolved by explicit all-feature tasks-stage determinations.
2. Whether C2 is resolved by a clear WM-owned schema boundary or whether foundation must still be reopened.
3. Whether C3 is resolved by a clear analysis no-change rationale or whether analysis must still be reopened.
4. Whether C4 is resolved by the CE T-016 and WM T-007/T-008 tasks changes.
5. Whether all seven features remain in review scope.
6. Whether tasks triad-review can complete now, or whether another must-fix remains.

Return YAML-compatible findings with at least:

- severity
- target_location
- description
- rationale
- verifying_commands
