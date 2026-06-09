---
feature: all_features
phase: design
stage: approval
date: 2026-06-09
status: pending_human_approval
run_id: 2026-06-09-existing-system-sdd-design-approval
---

# Existing System SDD Design Approval

## Scope

- Reopen: `reopen-procedure-2026-06-09-existing-system-sdd-code-drift`
- Gate: `stages/design.yaml#approval`
- Target feature set: foundation, runtime, evaluation, analysis, workflow-management, self-improvement, conformance-evaluation
- Direct impact features: conformance-evaluation, workflow-management
- Indirect check features: foundation, runtime, evaluation, analysis, self-improvement

## Completed Design Gates

| Gate | Status | Evidence |
| --- | --- | --- |
| `stages/design.yaml#drafting` | completed | CE and WM design.md were updated. |
| `stages/design.yaml#triad-review` | approved | `.reviewcompass/specs/_cross_feature/reviews/2026-06-09-existing-system-sdd-design-all-features-review-run-r2/raw-review-triage-summary.md` |
| `stages/design.yaml#review-wave` | approved | `.reviewcompass/specs/_cross_feature/reviews/2026-06-09-existing-system-sdd-design-review-wave.md` |
| `stages/design.yaml#alignment` | approved | `.reviewcompass/specs/_cross_feature/reviews/2026-06-09-existing-system-sdd-design-alignment.md` |

## Design Changes Being Approved

### conformance-evaluation

Design now covers Requirement 10:

- Existing-system difference extraction mode for post-hoc intent.
- Inputs: added intent, existing feature partitioning, existing requirements/design/tasks, implementation code.
- Candidate fields: `feature`, `phase`, `classification`, `code_refs`, `existing_spec_refs`, `reasoning_summary`, `needs_human_decision`.
- Classification values: `existing_sufficient`, `spec_update_candidate`, `design_conflict_candidate`, `downstream_impact_candidate`, `implementation_change_candidate`.
- Tasks boundary: tasks are reference input and downstream impact candidates only.
- Handoff to workflow-management for formal downstream updates.
- Traceability through `XDI-CE-002`.

### workflow-management

Design now covers Requirement 9:

- Feature receptacle decisions for post-hoc intent on an existing system.
- Downstream redeployment through requirements/design/tasks/implementation.
- Drafting-before-review guard through `drafting_completed_gates`.
- CE candidate intake contract.
- `downstream_impact_decisions` record shape.
- Human blockers and side-track separation.
- Traceability through `XDI-WM-002`.

## Cross-Feature Judgment

The design phase is ready for approval.

- Added intent, feature partitioning, requirements, and design documents are aligned.
- CE and WM responsibilities are complementary and do not overlap incorrectly.
- Foundation/runtime/evaluation/analysis/self-improvement were checked as indirect features, and no design.md body update is required now.
- Foundation-owned shared schema remains a watch item only. The new CE/WM structures are feature-local contracts unless later tasks or implementation make them reusable shared schema.

## Approval Question

Approve `stages/design.yaml#approval` for this reopen chain.

If approved, the next workflow step is `tasks.triad-review`.
