---
feature: all_features
phase: implementation
stage: review-wave
date: 2026-06-09
status: completed_pending_state_update_approval
run_id: 2026-06-09-existing-system-sdd-implementation-review-wave
---

# Existing System SDD Implementation Review-Wave

## Scope

- Reopen: `reopen-procedure-2026-06-09-existing-system-sdd-code-drift`
- Gate: `stages/implementation.yaml#review-wave`
- Target feature set: foundation, runtime, evaluation, analysis, workflow-management, self-improvement, conformance-evaluation
- Direct impact features: conformance-evaluation, workflow-management
- Indirect check features: foundation, runtime, evaluation, analysis, self-improvement
- Entry command: `.venv/bin/python3 tools/check-workflow-action.py next --json`
- Entry next action: `reopen_in_progress`, `implementation.review-wave`

## Inputs

- Carry-forward register: `learning/workflow/carry-forward-register/reviewcompass-import.yaml`
- Carry-forward unresolved count: 0
- Feature impact decisions: `stages/in-progress/reopen-procedure-2026-06-09-existing-system-sdd-code-drift.yaml`
- Requirements review-wave: `.reviewcompass/specs/_cross_feature/reviews/2026-06-09-existing-system-sdd-requirements-review-wave.md`
- Design review-wave: `.reviewcompass/specs/_cross_feature/reviews/2026-06-09-existing-system-sdd-design-review-wave.md`
- Tasks review-wave: `.reviewcompass/specs/_cross_feature/reviews/2026-06-09-existing-system-sdd-tasks-review-wave.md`
- Implementation drafting: `.reviewcompass/specs/_cross_feature/reviews/2026-06-09-existing-system-sdd-implementation-drafting.md`
- Implementation triad-review r2 summary: `.reviewcompass/specs/_cross_feature/reviews/2026-06-09-existing-system-sdd-implementation-review-run-r2/raw-review-triage-summary.md`
- Direct implementation evidence:
  - `tools/conformance_evaluation/post_hoc_intent_diff.py`
  - `tools/conformance_evaluation/schemas/post_hoc_intent_diff.schema.json`
  - `tests/conformance-evaluation/test_conformance_evaluation.py`
  - `tools/check-workflow-action.py`
  - `tests/tools/test_check_workflow_action.py`
- Direct implementation drafting documents:
  - `.reviewcompass/specs/conformance-evaluation/implementation-drafting.md`
  - `.reviewcompass/specs/workflow-management/implementation-drafting.md`

## Review-Wave Checks

| Check | Result | Evidence |
| --- | --- | --- |
| Feature scope coverage | pass | `feature_impact_decisions` covers all 7 features and separates direct from indirect impact. |
| Carry-forward unresolved items | pass | `next --json` reported `unresolved_cross_scope_items.unresolved_count: 0`. |
| Direct CE implementation coverage | pass | T-016 is implemented by `PostHocIntentDiff`, schema, T-016 tests, and the trial conformance record. |
| Direct WM implementation coverage | pass | Requirement 9 / XDI-WM-002 is covered by existing `next`, reopen state handling, drafting-before-review guard, and downstream decision coverage checks. |
| CE/WM responsibility boundary | pass | CE emits candidates and does not mutate tasks.md or reopen YAML; WM owns formal gate decisions and `downstream_impact_decisions`. |
| T-016 output contract | pass | Candidate fields, classification values, `phase: tasks`, `needs_human_decision`, and schema-code enum synchronization are tested and documented. |
| triad-review residual findings | pass | r2 C3/C7 were fixed; remaining r2 findings were approved as leave-as-is because they ask for optional provenance or inline excerpts, not implementation blockers. |
| foundation implementation impact | pass | No shared foundation schema or vocabulary implementation changes are introduced in this reopen chain. |
| runtime implementation impact | pass | No provider, prompt execution, raw response, or runtime persistence implementation changes are required. |
| evaluation implementation impact | pass | No evaluation metric, aggregation, or run-validity implementation changes are required. |
| analysis implementation impact | pass | T-016 output is not yet a reportable analysis intake artifact; no analysis implementation change is required in this chain. |
| self-improvement implementation impact | pass | No proposal, learning history, rollback, or discipline-update implementation change is required. |

## Direct Feature Judgment

The implementation review-wave passes for the direct features.

conformance-evaluation:

- Implements existing-system post-hoc intent difference extraction.
- Writes a conformance evaluation record under `.reviewcompass/specs/conformance-evaluation/conformance/`.
- Keeps tasks.md and reopen YAML read-only from CE.

workflow-management:

- Receives CE candidates as reopen decision inputs, not direct execution commands.
- Enforces drafting-before-review through `run_reopen_drafting`.
- Requires downstream decision coverage before completed reopen state can be committed.

## Indirect Feature Judgment

No implementation body changes are needed for foundation, runtime, evaluation, analysis, or self-improvement at this gate.

Rationale:

- The new executable behavior lives in CE and WM.
- Indirect features are consumers or later-stage observers in this reopen chain.
- If T-016 output later becomes a shared schema, runtime artifact, evaluation metric, analysis report input, or self-improvement proposal input, that future change should trigger a new reopen judgment then.

## Decision

No same-root implementation issue or cross-feature blocker remains at `stages/implementation.yaml#review-wave`.

Recommended next action:

1. Mark `implementation.review-wave` complete after approval of the state update.
2. Remove `stages/implementation.yaml#review-wave` from `pending_gates`.
3. Add this gate to `completed_gates`.
4. Record a `downstream_impact_decisions` entry for `stages/implementation.yaml#review-wave`.
5. Proceed to `stages/implementation.yaml#alignment`.

Spec-state update is an irreversible workflow-state operation, so this artifact stops before changing `spec.json`.
