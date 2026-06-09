---
run_id: 2026-06-09-existing-system-sdd-tasks-all-features-review-run
phase: tasks.triad-review
status: post_triage_fix_evidence
created_at: 2026-06-09
decision_actor: codex
approval_source: 2026-06-09 user message "承認"
---

# Tasks Stage Feature Impact Decisions

## Purpose

This record closes the tasks triad-review finding that all seven features must have explicit tasks-stage impact determinations.

## Decisions

| Feature | Decision | Rationale | Evidence |
|---|---|---|---|
| conformance-evaluation | tasks.md updated | This feature owns post-hoc intent difference extraction from added intent, existing specs, and implementation code. T-016 and T-013 now cover Requirement 10 and XDI-CE-002. | `.reviewcompass/specs/conformance-evaluation/tasks.md` |
| workflow-management | tasks.md updated | This feature owns formal reopen propagation, feature receptacle decisions, drafting-before-review enforcement, downstream decision records, and CE candidate intake. T-004, T-007, T-008, and T-011 now cover Requirement 9 and XDI-WM-002. | `.reviewcompass/specs/workflow-management/tasks.md` |
| foundation | no tasks.md body change required | The new `completed_gates`, `drafting_completed_gates`, and `downstream_impact_decisions` fields are workflow-management in-progress state fields. Their authoritative schema remains `stages/in-progress.schema.json` owned by workflow-management T-008. They are not promoted to foundation shared schemas in this reopen chain. | `.reviewcompass/specs/foundation/tasks.md`, `.reviewcompass/specs/workflow-management/tasks.md` |
| runtime | no tasks.md body change required | Runtime may execute review/provider calls, but this reopen adds no new runtime execution contract, provider contract, prompt resolution contract, or raw evidence output contract. | `.reviewcompass/specs/runtime/tasks.md` |
| evaluation | no tasks.md body change required | Evaluation may analyze review outputs, but this reopen adds no new metric, aggregation, run validity, or evaluation evidence bundle contract. | `.reviewcompass/specs/evaluation/tasks.md` |
| analysis | no tasks.md body change required | Analysis consumes conformance-evaluation results for reporting, but this reopen's new T-016 candidate flow is CE to WM for workflow propagation, not a reporting intake requirement. If T-016 outputs are later promoted to reportable analysis inputs, analysis T-008 should be reopened then. | `.reviewcompass/specs/analysis/tasks.md`, `.reviewcompass/specs/conformance-evaluation/tasks.md`, `.reviewcompass/specs/workflow-management/tasks.md` |
| self-improvement | no tasks.md body change required | Self-improvement may later consume workflow improvement signals, but this reopen does not add a new self-improvement proposal, discipline update, or learning workflow contract. | `.reviewcompass/specs/self-improvement/tasks.md` |

## Follow-up Rule

If the T-016 output format is later promoted from workflow propagation input to a reportable analysis artifact, reopen `analysis` for tasks impact. If `downstream_impact_decisions` is later promoted from workflow-management state to a shared schema, reopen `foundation` for schema ownership.
