---
feature: all_features
phase: tasks
stage: review-wave
date: 2026-06-09
status: completed_pending_state_update_approval
run_id: 2026-06-09-existing-system-sdd-tasks-review-wave
---

# Existing System SDD Tasks Review-Wave

## Scope

- Reopen: `reopen-procedure-2026-06-09-existing-system-sdd-code-drift`
- Gate: `stages/tasks.yaml#review-wave`
- Target feature set: foundation, runtime, evaluation, analysis, workflow-management, self-improvement, conformance-evaluation
- Direct impact features: conformance-evaluation, workflow-management
- Indirect check features: foundation, runtime, evaluation, analysis, self-improvement
- Entry command: `.venv/bin/python3 tools/check-workflow-action.py next --json`
- Entry next action: `reopen_in_progress`, `tasks.review-wave`

## Inputs

- Carry-forward register: `learning/workflow/carry-forward-register/reviewcompass-import.yaml`
- Carry-forward unresolved count: 0
- Feature impact decisions: `stages/in-progress/reopen-procedure-2026-06-09-existing-system-sdd-code-drift.yaml`
- Requirements review-wave: `.reviewcompass/specs/_cross_feature/reviews/2026-06-09-existing-system-sdd-requirements-review-wave.md`
- Design review-wave: `.reviewcompass/specs/_cross_feature/reviews/2026-06-09-existing-system-sdd-design-review-wave.md`
- Tasks triad-review r2 summary: `.reviewcompass/specs/_cross_feature/reviews/2026-06-09-existing-system-sdd-tasks-all-features-review-run-r2/raw-review-triage-summary.md`
- Tasks triad-review impact decisions: `.reviewcompass/specs/_cross_feature/reviews/2026-06-09-existing-system-sdd-tasks-all-features-review-run/tasks-impact-decisions.md`
- Direct tasks documents:
  - `.reviewcompass/specs/conformance-evaluation/tasks.md`
  - `.reviewcompass/specs/workflow-management/tasks.md`
- Indirect tasks documents:
  - `.reviewcompass/specs/foundation/tasks.md`
  - `.reviewcompass/specs/runtime/tasks.md`
  - `.reviewcompass/specs/evaluation/tasks.md`
  - `.reviewcompass/specs/analysis/tasks.md`
  - `.reviewcompass/specs/self-improvement/tasks.md`

## Review-Wave Checks

| Check | Result | Evidence |
| --- | --- | --- |
| Feature scope coverage | pass | `feature_impact_decisions` and `tasks-impact-decisions.md` cover all 7 features. |
| Carry-forward unresolved items | pass | `next --json` reported `unresolved_cross_scope_items.unresolved_count: 0`. |
| Direct CE tasks coverage | pass | CE tasks now contain T-016 for existing-system difference extraction, Requirement 10, `XDI-CE-002`, T-013 integration coverage, and CE→WM handoff for tasks-phase candidates. |
| Direct WM tasks coverage | pass | WM tasks now contain Requirement 9 and `XDI-WM-002` across T-004, T-007, T-008, and T-011. |
| CE/WM responsibility boundary | pass | CE extracts and classifies evidence-backed candidates; WM consumes CE candidates through formal reopen and owns receptacle decisions and pending gates. |
| tasks boundary | pass | CE treats tasks.md as reference input and does not directly rewrite tasks.md. WM owns the formal tasks-phase reopen gate conversion. |
| foundation tasks impact | pass | New reopen state fields remain WM-owned in `stages/in-progress.schema.json`; no foundation shared schema promotion occurs in this reopen chain. |
| runtime tasks impact | pass | No new runtime execution, provider, prompt resolution, or raw evidence output task is required. |
| evaluation tasks impact | pass | No new evaluation metric, aggregation, run validity, or evidence bundle task is required. |
| analysis tasks impact | pass | T-016 output is CE→WM workflow propagation input, not an analysis reporting intake requirement in this reopen chain. |
| self-improvement tasks impact | pass | Workflow procedure improvements remain WM-owned evidence in this chain; no self-improvement proposal or discipline-update task is introduced. |
| Triad-review residual finding | pass | The only r2 residual finding concerned review-target output wording and was approved as leave-as-is; no tasks.md blocker remains. |

## Foundation Ownership Judgment

The tasks triad-review raised whether `completed_gates`, `drafting_completed_gates`, and `downstream_impact_decisions` should require foundation tasks work.

Review-wave judgment: no foundation tasks.md body change is needed now.

Rationale:

- T-008 explicitly owns `stages/in-progress.schema.json`.
- The new fields are workflow-management procedure state, not shared review evidence schema.
- Foundation should only be reopened if those fields are later promoted to general shared schema used across feature implementations.

## Analysis Consumption Judgment

The tasks triad-review raised whether analysis must consume the new T-016 candidate output.

Review-wave judgment: no analysis tasks.md body change is needed now.

Rationale:

- This reopen chain uses T-016 candidate output as input to workflow-management reopen propagation.
- The output is not yet a reporting intake requirement for analysis.
- If T-016 outputs later become reportable analysis artifacts, analysis T-008 or a related analysis intake task should be reopened then.

## Cross-Feature Judgment

The tasks review-wave passes.

The direct tasks changes are complementary:

- `conformance-evaluation` owns code-derived difference candidate extraction and handoff.
- `workflow-management` owns formal downstream propagation, gate ordering, state tracking, and human approval records.

The indirect features remain part of the recorded impact scope, but no tasks.md body update is needed at this gate.

## Decision

No same-root tasks issue or cross-feature blocker remains at `stages/tasks.yaml#review-wave`.

Recommended next action:

1. Mark `tasks.review-wave` complete after approval of the state update.
2. Remove `stages/tasks.yaml#review-wave` from `pending_gates`.
3. Add this gate to `completed_gates`.
4. Record a `downstream_impact_decisions` entry for `stages/tasks.yaml#review-wave`.
5. Proceed to `stages/tasks.yaml#alignment`.

Spec-state update is an irreversible workflow-state operation, so this artifact stops before changing `spec.json`.
