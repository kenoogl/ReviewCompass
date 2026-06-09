---
feature: all_features
phase: design
stage: alignment
date: 2026-06-09
status: completed_pending_state_update_approval
run_id: 2026-06-09-existing-system-sdd-design-alignment
---

# Existing System SDD Design Alignment

## Scope

- Reopen: `reopen-procedure-2026-06-09-existing-system-sdd-code-drift`
- Gate: `stages/design.yaml#alignment`
- Target feature set: foundation, runtime, evaluation, analysis, workflow-management, self-improvement, conformance-evaluation
- Direct impact features: conformance-evaluation, workflow-management
- Indirect check features: foundation, runtime, evaluation, analysis, self-improvement
- Entry command: `.venv/bin/python3 tools/check-workflow-action.py next --json`
- Entry next action: `reopen_in_progress`, `design.alignment`

## Inputs

- Intent: `intent/INTENT.md`
- Feature partitioning: `stages/feature-partitioning/2026-05-24-proposal.md`
- Requirements alignment: `.reviewcompass/specs/_cross_feature/reviews/2026-06-09-existing-system-sdd-requirements-alignment.md`
- Design review-wave: `.reviewcompass/specs/_cross_feature/reviews/2026-06-09-existing-system-sdd-design-review-wave.md`
- Direct requirements:
  - `.reviewcompass/specs/conformance-evaluation/requirements.md`
  - `.reviewcompass/specs/workflow-management/requirements.md`
- Direct designs:
  - `.reviewcompass/specs/conformance-evaluation/design.md`
  - `.reviewcompass/specs/workflow-management/design.md`
- Reopen state: `stages/in-progress/reopen-procedure-2026-06-09-existing-system-sdd-code-drift.yaml`

## Alignment Checks

| Check | Result | Evidence |
| --- | --- | --- |
| Intent alignment | pass | Added intent requires existing-system SDD after post-hoc intent and code-derived drift detection. CE/WM design documents now model that flow. |
| Feature partitioning alignment | pass | Existing feature split remains valid. CE owns extraction/classification. WM owns formal reopen propagation. No new feature is required. |
| Requirements to design alignment: CE | pass | CE Requirement 10 is represented in CE design by existing-system difference extraction mode, candidate schema, classification values, tasks boundary, and WM handoff. |
| Requirements to design alignment: WM | pass | WM Requirement 9 is represented in WM design by receptacle decisions, downstream redeployment, CE candidate intake, drafting-before-review guard, downstream decision records, blockers, and side-track separation. |
| CE/WM boundary alignment | pass | CE does not directly update specs. WM does not generate code-derived candidates. The handoff boundary is explicit. |
| tasks boundary alignment | pass | CE can emit downstream impact candidates but does not infer or recreate tasks.md. Formal tasks reflection remains WM reopen responsibility. |
| indirect feature alignment | pass | Design review-wave confirmed no design.md body update is required for foundation, runtime, evaluation, analysis, or self-improvement at this gate. |
| foundation watch item alignment | pass | Candidate schema and reopen state fields remain feature-local CE/WM contracts for now. If they become reusable shared schema later, foundation reopen should be reconsidered. |
| workflow-state alignment | pass | `drafting_completed_gates` records design drafting before design triad-review. `completed_gates` and `downstream_impact_decisions` record requirements and design triad/review-wave decisions. |

## Cross-Spec Judgment

The design alignment passes.

The intent, feature partitioning, requirements, and design documents are mutually consistent for this reopen chain:

- The added intent is handled by existing direct features.
- `conformance-evaluation` owns evidence-backed extraction of code-derived differences for post-hoc intent on an existing system.
- `workflow-management` owns formal propagation through requirements, design, tasks, and implementation gates.
- The indirect features remain in scope for recorded checks, but no design body update is required now.

## Decision

No design alignment blocker remains at `stages/design.yaml#alignment`.

Recommended next action:

1. Mark `design.alignment` complete after approval of the state update.
2. Remove `stages/design.yaml#alignment` from `pending_gates`.
3. Add this gate to `completed_gates`.
4. Record a `downstream_impact_decisions` entry for `stages/design.yaml#alignment`.
5. Proceed to `stages/design.yaml#approval`.

Spec-state update is an irreversible workflow-state operation, so this artifact stops before changing `spec.json`.
