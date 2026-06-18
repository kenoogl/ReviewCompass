# workflow-management requirements triad-review target: integrated design requirements

## Review context

This is a formal requirements triad-review for `workflow-management` during reopen procedure:

- Reopen state: `stages/in-progress/reopen-procedure-2026-06-19.yaml`
- Active gate: `stages/requirements.yaml#triad-review`
- Classification basis: `docs/reviews/reopen-classification-2026-06-19-wm-integrated-design-requirements.md`
- Main requirements document: `.reviewcompass/specs/workflow-management/requirements.md`
- Current workflow state: `.reviewcompass/specs/workflow-management/spec.json`

The reopen was started because integrated design notes were reflected into `intent/INTENT.md` and `requirements.md`, but the workflow state had still marked downstream phases as complete. The state has been rolled back so that the formal workflow resumes at requirements triad-review.

## Source design inputs

Review the requirements additions against these source notes:

- `docs/notes/2026-06-18-integrated-design-selection-execution-layers.md`
- `docs/notes/working/2026-06-18-mechanized-workflow-execution-design.md`
- `docs/notes/working/2026-06-19-integrated-design-requirements-missing.md`

The relevant source concepts include:

- Separation between the selection layer (`next --json` / one `required_action`) and execution layer (operation contract).
- Mapping of `required_action` vocabulary to operation contracts.
- `effect_kind`, `approval_required`, `phase_boundary`, `sequence`, preconditions, postconditions.
- Approval gates and the distinction between recording a human decision and authorizing the target operation.
- Side-track stack and commit-mixing prevention.
- Workflow-state snapshot as a derived visibility/audit artifact, not the truth source.
- Structured effective prompt as a language-task specification.
- Phase 0 through Phase 6 implementation plan.
- LLM judge audit as an auxiliary semantic audit, not automatic final approval.

## Requirements additions under review

The main additions are in `.reviewcompass/specs/workflow-management/requirements.md`:

- Requirement 13: operation contract vocabulary and `required_action` mapping.
- Requirement 14: approval gate, side-track stack, workflow-state snapshot.
- Requirement 15: structured effective prompt and audit.
- Requirement 16: staged implementation plan Phase 0 through Phase 6.
- Change Intent entry for 2026-06-19.
- `XDI-WM-005`.

## Review question

Analyze whether the current requirements additions are sufficient, internally consistent, and ready to proceed to downstream design/tasks/implementation work.

Do not limit yourself to confirming or rejecting a proposed answer. Identify any substantive gaps, contradictions, hidden assumptions, or downstream risks you find. Consider both under-specification and over-specification.

Focus especially on:

1. Traceability from the source design notes to Requirement 13 through Requirement 16.
2. Whether requirements are stated at the right level for requirements phase, leaving design choices to design while still giving enough acceptance criteria.
3. Whether approval gates, `record_human_decision`, and irreversible operation authorization are unambiguous.
4. Whether side-track stack, staged file set/digest, and return behavior are specified enough to prevent workflow drift and commit mixing.
5. Whether operation contract vocabulary can cover all 19 `required_action` values without relying on LLM interpretation.
6. Whether Phase 0 through Phase 6 ordering is coherent and testable.
7. Whether the current reopen state and `spec.json` rollback correctly represent the actual workflow position.
8. Whether there are cross-feature impacts that should be carried to review-wave rather than handled only inside workflow-management.

## Output format

Return findings as structured YAML:

```yaml
findings:
  - id: <stable-id>
    severity: ERROR | WARN | INFO
    summary: <short summary>
    target_file: <path>
    target_location: <section or line if known>
    finding_type: requirement_gap | contradiction | traceability_gap | workflow_state_gap | downstream_risk | cross_feature_impact | other
    rationale: <why this matters>
    recommendation: <what should be changed or checked>
    suggested_label: must-fix | should-fix | leave-as-is
```

If there are no substantive findings, return:

```yaml
findings: []
```
