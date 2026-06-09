---
run_id: 2026-06-09-existing-system-sdd-design-all-features-review-run-r2
phase: design.triad-review
features:
  - foundation
  - runtime
  - evaluation
  - analysis
  - workflow-management
  - self-improvement
  - conformance-evaluation
reopen_procedure: stages/in-progress/reopen-procedure-2026-06-09-existing-system-sdd-code-drift.yaml
supersedes_review_run: .reviewcompass/specs/_cross_feature/reviews/2026-06-09-existing-system-sdd-design-all-features-review-run
prior_requirements_review_run: .reviewcompass/specs/_cross_feature/reviews/2026-06-09-existing-system-sdd-requirements-all-features-review-run-r2
---

# Design triad-review target: existing-system SDD code drift, all features, post-drafting

## Review Purpose

Review whether the design-stage drafting for the 2026-06-09 reopen procedure is sufficient to complete `stages/design.yaml#triad-review`.

This run supersedes the earlier design review-run because that run was executed before the formal design drafting was completed. The current reopen state records `drafting_completed_gates: stages/design.yaml#drafting`, and the next mechanical action is `run_reopen_pending_gate` for `stages/design.yaml#triad-review`.

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
- completed gates: requirements triad-review, requirements review-wave, requirements alignment, requirements approval
- completed drafting gate: design drafting
- next gate: `stages/design.yaml#triad-review`

## Requirements Stage Result

The approved requirements stage added direct requirements in two features:

- `conformance-evaluation` Requirement 10: existing-system post-hoc intent code-derived difference extraction.
- `workflow-management` Requirement 9: downstream propagation when intent is added to an existing system.

The approved requirements review-wave decided that CE Requirement 10 and WM Requirement 9 are complementary:

- CE extracts evidence-backed candidates from implementation code and existing specs.
- WM consumes CE evaluation records through the formal reopen workflow.
- Indirect features do not need requirements.md body changes at the requirements stage, but remain in scope for downstream checks.

## Design Drafting Changes Under Review

### conformance-evaluation design.md

The design drafting now adds:

- Requirement count 9 -> 10.
- Goal for an existing-system difference extraction model.
- Mode table row for `既存システム差分抽出（後追い intent）`.
- §7.10 existing-system difference extraction mode.
- Candidate fields: `feature`, `phase`, `classification`, `code_refs`, `existing_spec_refs`, `reasoning_summary`, `needs_human_decision`.
- Classification values: `existing_sufficient`, `spec_update_candidate`, `design_conflict_candidate`, `downstream_impact_candidate`, `implementation_change_candidate`.
- Boundary that tasks are reference input and downstream impact candidates only; formal tasks.md updates remain WM reopen responsibility.
- §13.7 handoff to workflow-management.
- §14.4 output interface to workflow-management.
- Req 10 traceability and `XDI-CE-002`.

Review whether this design is sufficient and whether it stays within CE responsibility.

### workflow-management design.md

The design drafting now adds:

- Requirement count 8 -> 9.
- Goal and ownership model for post-hoc intent downstream propagation.
- §reopen 機械強制モデル §6: post-hoc intent downstream redeployment.
- Feature receptacle decisions: `reopen_existing_feature`, `new_feature_required`, `human_decision_required`.
- Rule that existing requirements similarity does not end processing.
- Rule that `pending_gates` pointing to triad-review still requires drafting first unless `drafting_completed_gates` or `completed_gates` contains `stages/<phase>.yaml#drafting`.
- CE candidate intake contract with minimum fields.
- `downstream_impact_decisions` record shape and existing decision vocabulary.
- Side-track handling through `process_id: maintenance`.
- Session state fields for `completed_gates`, `drafting_completed_gates`, `downstream_impact_decisions`, and `current_blocker`.
- Req 9 traceability and `XDI-WM-002`.

Review whether this design is sufficient and whether it stays within WM responsibility.

## Indirect Feature Scope

The design review should check whether indirect design changes are necessary now:

- foundation: shared metadata, evidence, vocabulary, schema, and state contracts.
- runtime: review execution, prompt resolution, evidence output, provider execution.
- evaluation: run validity, metrics, aggregation, evidence bundle handling.
- analysis: conformance output consumption and reporting, but not conformance judgment.
- self-improvement: workflow improvement signals, but not direct mutation of workflow files.

The expected baseline is `indirect_check_only` unless the design drafting creates a new contract that these features must own directly.

## Review Criteria

Classify findings as CRITICAL, ERROR, WARN, or INFO.

Use these labels in rationale when applicable:

- `must-fix`: blocks design triad-review completion.
- `should-fix`: should be considered in this reopen chain but may be handled before later design gates.
- `leave-as-is`: record only.

Check especially:

1. Whether all seven features are properly included in design-stage impact review.
2. Whether CE design.md now covers Requirement 10 and `XDI-CE-002`.
3. Whether WM design.md now covers Requirement 9 and `XDI-WM-002`.
4. Whether CE and WM boundaries remain clear: CE extracts/classifies evidence-backed candidates; WM consumes them through formal reopen.
5. Whether tasks handling is correctly bounded.
6. Whether `drafting_completed_gates` closes the earlier drafting-before-review workflow hole.
7. Whether indirect features need design.md changes now.
8. Whether design triad-review can complete, or whether design drafting needs must-fix correction first.

Return YAML-compatible findings with at least:

- severity
- target_location
- description
- rationale
- verifying_commands
