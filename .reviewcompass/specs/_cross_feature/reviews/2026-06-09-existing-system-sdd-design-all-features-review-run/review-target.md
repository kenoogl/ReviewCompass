---
run_id: 2026-06-09-existing-system-sdd-design-all-features-review-run
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
prior_requirements_review_run: .reviewcompass/specs/_cross_feature/reviews/2026-06-09-existing-system-sdd-requirements-all-features-review-run-r2
---

# Design triad-review target: existing-system SDD code drift, all features

## Review Purpose

Review the design-stage impact of the 2026-06-09 reopen procedure across all ReviewCompass features.

The requirements stage is approved. The current gate is `stages/design.yaml#triad-review`. This review should decide whether design-stage handling is complete enough to proceed to design review-wave, or whether design.md files / impact decisions need must-fix correction first.

## User Clarification

The user clarified:

- The added intent is to support specification-driven development for an existing system after intent is added post hoc.
- The work must proceed from intent through requirements, design, tasks, and implementation, even when existing downstream artifacts already exist.
- When direct and indirect impact are both included, all seven features are target features.
- Existing design, tasks, and implementation must be checked for conflicts while new requirements and designs are detailed.

## Current Reopen State

The reopen procedure has:

- `classification: N-0`
- direct reopen features: `conformance-evaluation`, `workflow-management`
- indirect check features: `foundation`, `runtime`, `evaluation`, `analysis`, `self-improvement`
- `impacted_downstream_phases`: requirements, design, tasks, implementation
- completed gates: requirements triad-review, requirements review-wave, requirements alignment, requirements approval
- next gate: `stages/design.yaml#triad-review`

## Requirements Stage Result

The requirements stage added direct requirements in two features:

- `conformance-evaluation` Requirement 10: existing-system post-hoc intent code-derived difference extraction.
- `workflow-management` Requirement 9: downstream propagation when intent is added to an existing system.

The approved requirements review-wave decided that CE Requirement 10 and WM Requirement 9 are complementary:

- CE extracts evidence-backed candidates from implementation code and existing specs.
- WM consumes CE evaluation records through the formal reopen workflow.
- Indirect features do not need requirements.md body changes at the requirements stage, but remain in scope for downstream impact checks.

## Direct Design Evidence

### conformance-evaluation design.md

Current observed state:

- The overview still says requirements.md has 9 Requirements.
- Goals stop at Requirement 9 contract ownership map / spec update proposals.
- Section 13.6 covers Requirement 9 only.
- Requirement traceability table stops at Req 8 in the observed excerpt and does not show a Requirement 10 row.
- The implementation-derived trace only contains `XDI-CE-001`; `XDI-CE-002` is not represented in design.md.

Design question:

Should conformance-evaluation design.md add a design model for Requirement 10, including:

- an explicit existing-system / post-hoc intent mode or submode;
- inputs: added intent, existing feature partitioning, existing requirements/design/tasks as comparison inputs, implementation code;
- code-derived candidate output structure with `feature`, `phase`, `classification`, `code_refs`, `existing_spec_refs`, `reasoning_summary`, `needs_human_decision`;
- classification values: `existing_sufficient`, `spec_update_candidate`, `design_conflict_candidate`, `downstream_impact_candidate`, `implementation_change_candidate`;
- boundaries around tasks: tasks are reference inputs and downstream impact candidates, not an inferred tasks.md recreation target;
- handoff to workflow-management for official requirements/design/tasks/implementation changes;
- traceability for `XDI-CE-002`.

### workflow-management design.md

Current observed state:

- The overview still says requirements.md has 8 Requirements.
- Goals do not include post-hoc intent downstream propagation for existing systems.
- The architecture and reopen model predate Requirement 9.
- The design does not yet define how a CE evaluation record is accepted into reopen procedure decisions.
- The design does not yet define the record shape for `downstream_impact_decisions` required by Requirement 9.
- The design does not yet represent `XDI-WM-002`.

Design question:

Should workflow-management design.md add a design model for Requirement 9, including:

- machine-readable detection that post-hoc intent on an existing system creates reopen work rather than ending at existing requirements;
- feature receptacle decision: reopen existing feature when a receiving feature exists, otherwise new feature candidate;
- downstream phase sequence requirements/design/tasks/implementation;
- per-gate decision records for `existing_sufficient`, `spec_update_required`, `conflict_candidate`, or equivalent;
- required evidence for `downstream_impact_decisions`: gate, feature scope, decision, reason, evidence, actor, source;
- conflict handling and human stop points through `current_blocker` or phase approval;
- CE evaluation record intake contract with minimum candidate fields;
- side-track distinction when workflow defects are discovered during a dogfooding run;
- traceability for `XDI-WM-002`.

## Indirect Feature Evidence

The requirements stage kept the five indirect features as `indirect_check_only`. The design review should re-check whether this remains sufficient at design stage.

### foundation

Foundation owns shared metadata, evidence, vocabulary, schema, and state contracts. CE Requirement 10 references foundation vocabulary for evidence and metadata. Review whether CE/WM can reference existing foundation design contracts without changing foundation design.md.

### runtime

Runtime owns review execution, prompt resolution, evidence output, and LLM/provider execution plumbing. Review whether the post-hoc intent / code-derived extraction design needs new runtime behavior, or whether existing runtime interfaces are sufficient.

### evaluation

Evaluation owns run validity, metrics, aggregation, and evidence bundle handling. It does not own upstream document conformance. Review whether CE evaluation records can remain CE-owned without requiring evaluation design changes.

### analysis

Analysis reads conformance outputs for reports and evidence mapping, but should not perform conformance judgment. Review whether new CE output candidates require analysis design changes now or can be handled later as downstream consumption.

### self-improvement

Self-improvement may consume workflow improvement signals but does not directly mutate workflow files. Review whether the workflow-defect side-track lessons require self-improvement design changes now, or whether WM ownership is sufficient.

## Review Criteria

Classify findings as CRITICAL, ERROR, WARN, or INFO.

Use the following proposed labels in rationale when applicable:

- `must-fix`: blocks design triad-review completion and must be fixed before design review-wave.
- `should-fix`: should be fixed in this reopen chain, but may be discussed before deciding whether it blocks this gate.
- `leave-as-is`: record only.

Check especially:

1. Whether all seven features are properly included in design-stage impact review.
2. Whether CE design.md is stale relative to Requirement 10 and `XDI-CE-002`.
3. Whether WM design.md is stale relative to Requirement 9 and `XDI-WM-002`.
4. Whether CE and WM design boundaries remain clear: CE extracts/classifies evidence-backed candidates; WM consumes them through formal reopen.
5. Whether tasks handling is correctly bounded: CE may use tasks as reference input and emit downstream impact candidates, but should not infer or recreate tasks.md as a formal output.
6. Whether indirect features need design.md changes, or whether indirect check only is sufficient.
7. Whether design triad-review can complete after fixes, or whether feature-partitioning / requirements must be reopened again.
8. Whether the current pending gates remain appropriate after material design changes.

Return YAML-compatible findings with at least:

- severity
- target_location
- description
- rationale
- verifying_commands
