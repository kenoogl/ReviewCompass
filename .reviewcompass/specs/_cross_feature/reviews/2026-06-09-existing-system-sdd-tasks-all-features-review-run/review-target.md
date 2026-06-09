---
run_id: 2026-06-09-existing-system-sdd-tasks-all-features-review-run
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
prior_requirements_review_run: .reviewcompass/specs/_cross_feature/reviews/2026-06-09-existing-system-sdd-requirements-all-features-review-run-r2
prior_design_review_run: .reviewcompass/specs/_cross_feature/reviews/2026-06-09-existing-system-sdd-design-all-features-review-run-r2
---

# Tasks triad-review target: existing-system SDD code drift, all features, post-drafting

## Review Purpose

Review whether the tasks-stage drafting for the 2026-06-09 reopen procedure is sufficient to complete `stages/tasks.yaml#triad-review`.

The current reopen state records `drafting_completed_gates: stages/tasks.yaml#drafting`, and the next mechanical action is `run_reopen_pending_gate` for `stages/tasks.yaml#triad-review`.

## User Clarification

The user clarified:

- The added intent is to support specification-driven development for an existing system after intent is added post hoc.
- Existing requirements, design, tasks, and implementation do not end the process; they are checked for conflict while the intent is propagated downward.
- If an existing feature can receive the intent, that feature is reopened. If not, feature-partitioning must create a new feature candidate.
- Direct and indirect feature impact means all seven features are in review scope.
- Workflow procedure defects discovered during dogfooding must be handled as side track work, then the mainline reopen must resume.

## Current Reopen State

The reopen procedure has:

- `classification: N-0`
- direct reopen features: `conformance-evaluation`, `workflow-management`
- indirect check features: `foundation`, `runtime`, `evaluation`, `analysis`, `self-improvement`
- `impacted_downstream_phases`: requirements, design, tasks, implementation
- completed gates: requirements triad-review, requirements review-wave, requirements alignment, requirements approval, design triad-review, design review-wave, design alignment, design approval
- completed drafting gates: design drafting, tasks drafting
- next gate: `stages/tasks.yaml#triad-review`

## Approved Upstream Result

The approved requirements stage added direct requirements in two features:

- `conformance-evaluation` Requirement 10: existing-system post-hoc intent code-derived difference extraction.
- `workflow-management` Requirement 9: downstream propagation when intent is added to an existing system.

The approved design stage added direct design in the same two features:

- CE owns evidence-backed candidate extraction from added intent, existing specs, and implementation code.
- WM owns formal reopen propagation, feature receptacle decisions, drafting-before-review enforcement, downstream impact decision records, and side-track separation.
- Indirect features remained in scope for checks but did not require body changes at design stage.

## Tasks Drafting Changes Under Review

### conformance-evaluation tasks.md

The tasks drafting now adds:

- Overview ownership for `既存システム差分抽出モード（§7.10）`.
- Task count 14 -> 16.
- New `T-016：既存システム差分抽出モード（Post-hoc Intent Difference Extraction）`.
- T-016 maps to design §7.10, §13.7, §14.4, Requirement 10 acceptance 1-8, and `XDI-CE-002`.
- T-016 accepts added intent, existing feature partitioning, existing requirements/design/tasks, and implementation code.
- T-016 treats tasks as reference input and does not generate or rewrite tasks.md.
- T-016 outputs candidates with fields `feature`, `phase`, `classification`, `code_refs`, `existing_spec_refs`, `reasoning_summary`, `needs_human_decision`.
- T-016 classification values are `existing_sufficient`, `spec_update_candidate`, `design_conflict_candidate`, `downstream_impact_candidate`, and `implementation_change_candidate`.
- T-013 integration test responsibility now includes T-016 and ReviewCompass itself as a trial target.
- Requirement 10 traceability and `XDI-CE-002` are added.

Review whether this is sufficient and whether CE stays within its responsibility.

### workflow-management tasks.md

The tasks drafting now adds:

- Overview and policy references for post-hoc intent downstream propagation.
- T-004 next-action responsibility for drafting-before-review: if triad-review is pending but `stages/<phase>.yaml#drafting` is not completed, next must return `run_reopen_drafting`.
- T-007 reopen responsibility for feature receptacle decisions: `reopen_existing_feature`, `new_feature_required`, `human_decision_required`.
- T-008 in-progress state responsibility for `completed_gates`, `drafting_completed_gates`, and `downstream_impact_decisions`.
- `downstream_impact_decisions` minimum fields: `gate`, `feature_scope`, `decision`, `rationale`, `evidence`, `decision_actor`, `decision_source`.
- T-011 integration responsibility for `XDI-WM-002`: downstream redeployment, CE candidate intake, drafting-before-review, side-track separation, and decision evidence.
- Requirement 9 traceability and `XDI-WM-002` are added.

Review whether this is sufficient and whether WM stays within its responsibility.

## Indirect Feature Scope

The tasks review should check whether indirect tasks.md changes are necessary now:

- foundation: shared metadata, evidence, vocabulary, schema, and state contracts.
- runtime: review execution, prompt resolution, evidence output, provider execution.
- evaluation: run validity, metrics, aggregation, evidence bundle handling.
- analysis: conformance output consumption and reporting, but not conformance judgment.
- self-improvement: workflow improvement signals, but not direct mutation of workflow files.

The expected baseline is `indirect_check_only` unless the tasks drafting creates implementation work that these features must own directly.

## Review Criteria

Classify findings as CRITICAL, ERROR, WARN, or INFO.

Use these labels in rationale when applicable:

- `must-fix`: blocks tasks triad-review completion.
- `should-fix`: should be considered in this reopen chain but may be handled before later tasks gates.
- `leave-as-is`: record only.

Check especially:

1. Whether all seven features are properly included in tasks-stage impact review.
2. Whether CE tasks.md now covers Requirement 10 and `XDI-CE-002`.
3. Whether WM tasks.md now covers Requirement 9 and `XDI-WM-002`.
4. Whether CE and WM boundaries remain clear: CE extracts/classifies evidence-backed candidates; WM consumes them through formal reopen.
5. Whether tasks handling is correctly bounded.
6. Whether `drafting_completed_gates` and T-004/T-008 close the drafting-before-review workflow hole.
7. Whether indirect features need tasks.md changes now.
8. Whether tasks triad-review can complete, or whether tasks drafting needs must-fix correction first.

Return YAML-compatible findings with at least:

- severity
- target_location
- description
- rationale
- verifying_commands
