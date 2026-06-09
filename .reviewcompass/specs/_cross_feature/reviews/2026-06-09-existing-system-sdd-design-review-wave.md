---
feature: all_features
phase: design
stage: review-wave
date: 2026-06-09
status: completed_pending_state_update_approval
run_id: 2026-06-09-existing-system-sdd-design-review-wave
---

# Existing System SDD Design Review-Wave

## Scope

- Reopen: `reopen-procedure-2026-06-09-existing-system-sdd-code-drift`
- Gate: `stages/design.yaml#review-wave`
- Target feature set: foundation, runtime, evaluation, analysis, workflow-management, self-improvement, conformance-evaluation
- Direct impact features: conformance-evaluation, workflow-management
- Indirect check features: foundation, runtime, evaluation, analysis, self-improvement
- Entry command: `.venv/bin/python3 tools/check-workflow-action.py next --json`
- Entry next action: `reopen_in_progress`, `design.review-wave`

## Inputs

- Carry-forward register: `learning/workflow/carry-forward-register/reviewcompass-import.yaml`
- Carry-forward unresolved count: 0
- Feature impact decisions: `stages/in-progress/reopen-procedure-2026-06-09-existing-system-sdd-code-drift.yaml`
- Requirements review-wave: `.reviewcompass/specs/_cross_feature/reviews/2026-06-09-existing-system-sdd-requirements-review-wave.md`
- Design triad-review r2 summary: `.reviewcompass/specs/_cross_feature/reviews/2026-06-09-existing-system-sdd-design-all-features-review-run-r2/raw-review-triage-summary.md`
- Design triad-review r2 triage: `.reviewcompass/specs/_cross_feature/reviews/2026-06-09-existing-system-sdd-design-all-features-review-run-r2/triage.yaml`
- Direct design documents:
  - `.reviewcompass/specs/conformance-evaluation/design.md`
  - `.reviewcompass/specs/workflow-management/design.md`
- Indirect design documents:
  - `.reviewcompass/specs/foundation/design.md`
  - `.reviewcompass/specs/runtime/design.md`
  - `.reviewcompass/specs/evaluation/design.md`
  - `.reviewcompass/specs/analysis/design.md`
  - `.reviewcompass/specs/self-improvement/design.md`

## Review-Wave Checks

| Check | Result | Evidence |
| --- | --- | --- |
| Feature scope coverage | pass | `feature_impact_decisions` covers all 7 features and separates direct from indirect impact. |
| Carry-forward unresolved items | pass | `next --json` reported `unresolved_cross_scope_items.unresolved_count: 0`. |
| Direct CE design coverage | pass | CE design now contains Requirement 10, existing-system difference extraction mode, candidate fields, classification values, tasks boundary, WM handoff, and `XDI-CE-002`. |
| Direct WM design coverage | pass | WM design now contains Requirement 9, post-hoc intent downstream redeployment, feature receptacle decisions, drafting-before-review guard, CE intake contract, `downstream_impact_decisions`, side-track separation, and `XDI-WM-002`. |
| CE/WM responsibility boundary | pass | CE owns evidence-backed candidate extraction and draft-only outputs; WM owns formal reopen progression, downstream gate decisions, blockers, and approvals. |
| tasks boundary | pass | CE treats tasks as reference input and downstream impact candidates only. Formal tasks.md changes remain WM reopen responsibility. |
| foundation schema ownership watch item | pass | Foundation owns common review evidence schema, metadata, and shared review vocabularies. The new CE candidate classifications and WM reopen state fields are currently feature-local CE/WM contracts, not general review evidence schema. No foundation design.md body update is required at this gate. |
| runtime design impact | pass | No new runtime execution, provider, prompt resolution, or evidence production behavior is required by the design changes. |
| evaluation design impact | pass | No new evaluation metric, validity classification, or aggregation contract is required. CE evaluation records remain CE-owned artifacts for this reopen chain. |
| analysis design impact | pass | No immediate report or evidence transform change is required. Future consumption of CE outputs can be handled after CE/WM tasks and implementation settle. |
| self-improvement design impact | pass | Workflow-defect side-track learning remains WM-owned procedure evidence in this chain; self-improvement does not directly mutate workflow files here. |

## Foundation Ownership Judgment

The design triad-review raised a watch item: whether CE candidate schema or WM reopen state fields should move to foundation.

Review-wave judgment: no foundation design.md body change is needed now.

Rationale:

- Foundation currently owns common review evidence schemas, execution metadata, and selected shared vocabularies such as `severity`, `final_label`, `review_mode`, `validator_status`, `evidence_class`, and `confidence_label`.
- CE Requirement 10 introduces a feature-local candidate output contract for conformance evaluation.
- WM Requirement 9 introduces a workflow-local reopen state contract for procedure management.
- These contracts are used between CE and WM in this reopen chain, but they are not yet general review evidence schemas consumed uniformly by runtime, evaluation, analysis, self-improvement, and conformance-evaluation.
- If later tasks or implementation make the CE candidate schema a reusable cross-feature artifact, that should trigger a new foundation reopen judgment at that time.

## Cross-Feature Judgment

The design review-wave passes.

The direct design changes are complementary:

- `conformance-evaluation` owns code-derived difference candidate extraction for existing systems after post-hoc intent.
- `workflow-management` owns the formal downstream propagation procedure and gate decisions.

The indirect features remain part of the recorded impact scope, but no design.md body update is needed at this gate.

## Decision

No same-root design issue or cross-feature blocker remains at `stages/design.yaml#review-wave`.

Recommended next action:

1. Mark `design.review-wave` complete after approval of the state update.
2. Remove `stages/design.yaml#review-wave` from `pending_gates`.
3. Add this gate to `completed_gates`.
4. Record a `downstream_impact_decisions` entry for `stages/design.yaml#review-wave`.
5. Proceed to `stages/design.yaml#alignment`.

Spec-state update is an irreversible workflow-state operation, so this artifact stops before changing `spec.json`.
