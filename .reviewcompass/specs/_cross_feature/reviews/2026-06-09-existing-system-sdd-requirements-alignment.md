---
feature: all_features
phase: requirements
stage: alignment
date: 2026-06-09
status: completed_pending_state_update_approval
run_id: 2026-06-09-existing-system-sdd-requirements-alignment
---

# Existing System SDD Requirements Alignment

## Scope

- Reopen: `reopen-procedure-2026-06-09-existing-system-sdd-code-drift`
- Gate: `stages/requirements.yaml#alignment`
- Target feature set: foundation, runtime, evaluation, analysis, workflow-management, self-improvement, conformance-evaluation
- Direct impact features: conformance-evaluation, workflow-management
- Indirect check features: foundation, runtime, evaluation, analysis, self-improvement

## Inputs

- Intent: `intent/INTENT.md`
- Feature partitioning: `stages/feature-partitioning/2026-05-24-proposal.md`
- Reopen state: `stages/in-progress/reopen-procedure-2026-06-09-existing-system-sdd-code-drift.yaml`
- Requirements triad-review r2 summary: `.reviewcompass/specs/_cross_feature/reviews/2026-06-09-existing-system-sdd-requirements-all-features-review-run-r2/raw-review-triage-summary.md`
- Requirements review-wave: `.reviewcompass/specs/_cross_feature/reviews/2026-06-09-existing-system-sdd-requirements-review-wave.md`
- Direct requirements documents:
  - `.reviewcompass/specs/conformance-evaluation/requirements.md`
  - `.reviewcompass/specs/workflow-management/requirements.md`

## Alignment Checks

| Check | Result | Evidence |
| --- | --- | --- |
| Intent coverage | pass | Intent §3.7 / §4.7 says review collection must be based on actual LLM judgment and must not become a fixed prompt/rule mapping. CE Requirement 10 and WM Requirement 9 express the existing-system SDD path needed to support that intent. |
| Feature partitioning consistency | pass | No new feature is needed. The 7-feature partition remains unchanged; CE owns extraction of code-derived candidates and WM owns reopen procedure management. |
| Direct feature responsibility boundary | pass | CE extracts candidates and conflict signals; WM owns formal downstream reopen, approval stops, and `downstream_impact_decisions`. |
| Indirect feature handling | pass | Foundation, runtime, evaluation, analysis, and self-improvement are included in feature impact scope as indirect checks, with no requirements body change needed at this gate. |
| Review-wave carry-forward | pass | Requirements review-wave found no same-root requirements blocker and no unresolved carry-forward item. |
| Downstream chain preservation | pass | Reopen state keeps design, tasks, and implementation gates pending, so requirements completion does not skip downstream checks. |

## Decision

Requirements alignment passes.

The updated requirements remain aligned with the added intent and the existing feature partitioning. The requirements layer now states the new capability at the correct ownership boundary:

- `conformance-evaluation` owns code-derived requirements/design candidate extraction for existing systems.
- `workflow-management` owns the formal reopen and downstream propagation process.

No requirements-level conflict remains. The next state update is to mark `requirements.alignment` complete for the direct reopen features and move to `stages/requirements.yaml#approval`.

Spec-state update is an irreversible workflow-state operation, so this artifact stops before changing `spec.json`.
