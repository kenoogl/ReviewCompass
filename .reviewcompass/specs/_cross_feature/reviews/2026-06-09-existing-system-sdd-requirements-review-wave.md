---
feature: all_features
phase: requirements
stage: review-wave
date: 2026-06-09
status: completed_pending_state_update_approval
run_id: 2026-06-09-existing-system-sdd-requirements-review-wave
---

# Existing System SDD Requirements Review-Wave

## Scope

- Reopen: `reopen-procedure-2026-06-09-existing-system-sdd-code-drift`
- Gate: `stages/requirements.yaml#review-wave`
- Target feature set: foundation, runtime, evaluation, analysis, workflow-management, self-improvement, conformance-evaluation
- Direct impact features: conformance-evaluation, workflow-management
- Indirect check features: foundation, runtime, evaluation, analysis, self-improvement
- Entry command: `.venv/bin/python3 tools/check-workflow-action.py next --json`
- Entry next action: `reopen_in_progress`, `requirements.review-wave`

## Inputs

- Carry-forward register: `learning/workflow/carry-forward-register/reviewcompass-import.yaml`
- Carry-forward unresolved count: 0
- Feature impact decisions: `stages/in-progress/reopen-procedure-2026-06-09-existing-system-sdd-code-drift.yaml`
- Requirements triad-review r2 summary: `.reviewcompass/specs/_cross_feature/reviews/2026-06-09-existing-system-sdd-requirements-all-features-review-run-r2/raw-review-triage-summary.md`
- Requirements triad-review r2 triage: `.reviewcompass/specs/_cross_feature/reviews/2026-06-09-existing-system-sdd-requirements-all-features-review-run-r2/triage.yaml`
- Direct requirements documents:
  - `.reviewcompass/specs/conformance-evaluation/requirements.md`
  - `.reviewcompass/specs/workflow-management/requirements.md`

## Review-Wave Checks

| Check | Result | Evidence |
| --- | --- | --- |
| Feature scope coverage | pass | `feature_impact_decisions` covers all 7 features and separates direct from indirect impact. |
| Carry-forward unresolved items | pass | `next --json` reported `unresolved_cross_scope_items.unresolved_count: 0`. |
| Direct feature requirements consistency | pass | CE Requirement 10 and WM Requirement 9 describe complementary responsibilities: CE extracts code-derived candidates; WM runs formal reopen and downstream decisions. |
| CE task responsibility boundary | pass | R2 review found the prior tasks-scope must-fix resolved. tasks are reference input only for CE. |
| CE output candidate structure | pass | R2 review found the prior output-structure should-fix resolved. Candidate fields and classification values are named at requirements level. |
| WM stop and handoff rules | pass | R2 review found the prior stop/handoff should-fix resolved. Conflict stop and release records are now externally visible requirements. |
| Indirect feature requirements changes | pass | R2 review found no requirements body changes are needed for foundation, runtime, evaluation, analysis, or self-improvement in this reopen. |
| New feature need | pass | `new_feature_decision.decision: no_new_feature`; the intent is handled by existing CE and WM responsibilities. |

## Cross-Feature Judgment

The requirements review-wave passes.

The direct feature requirements changes are complementary, not conflicting:

- `conformance-evaluation` owns code-derived candidate extraction from existing implementation and existing specs.
- `workflow-management` owns formal reopen progression, downstream phase decisions, conflict stops, and human approval records.

The indirect features remain part of the recorded impact scope, but no requirements body update is needed at this gate. Their later design, tasks, and implementation checks remain pending through the reopen chain.

## Decision

No same-root requirements issue or cross-feature blocker remains at `stages/requirements.yaml#review-wave`.

Recommended next action:

1. Mark `requirements.review-wave` complete for the direct reopen features after approval of the state update.
2. Remove `stages/requirements.yaml#review-wave` from `pending_gates`.
3. Add this gate to `completed_gates`.
4. Record a `downstream_impact_decisions` entry for `stages/requirements.yaml#review-wave`.
5. Proceed to `stages/requirements.yaml#alignment`.

Spec-state update is an irreversible workflow-state operation, so this artifact stops before changing `spec.json`.
