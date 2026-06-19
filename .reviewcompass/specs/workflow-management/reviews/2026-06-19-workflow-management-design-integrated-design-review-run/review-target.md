# Design Triad Review Target

criteria_id: workflow_management_integrated_design_design_triad_review
phase: design
gate: stages/design.yaml#triad-review

## Review Purpose

Review whether `workflow-management` design drafting correctly and sufficiently reflects approved Requirement 13 through Requirement 16 from the integrated design follow-up.

## Target Files

- `.reviewcompass/specs/workflow-management/design.md`
- `.reviewcompass/specs/workflow-management/requirements.md`
- `.reviewcompass/specs/workflow-management/spec.json`
- `stages/in-progress/reopen-procedure-2026-06-19.yaml`
- `docs/notes/working/2026-06-19-integrated-design-manual-workflow-progress.md`
- `docs/notes/2026-06-18-integrated-design-selection-execution-layers.md`
- `docs/notes/working/2026-06-18-mechanized-workflow-execution-design.md`
- `docs/notes/working/2026-06-19-integrated-design-requirements-missing.md`
- `docs/notes/working/2026-06-19-proxy-model-triage-cost-issues.md`

## Required Checks

1. Check traceability from Requirement 13 to design sections for operation contract vocabulary, `required_action` mapping, compound operation representation, `record_human_decision`, and preconditions / postconditions.
2. Check traceability from Requirement 14 to design sections for approval gate records, side track stack frame schema, push / pop behavior, `return_to`, staged file set / digest checks, max depth policy, and workflow-state snapshot.
3. Check traceability from Requirement 15 to design sections for structured effective prompt schema, language task I/O, machine task separation, first-layer prompt checks, and LLM judge audit.
4. Check traceability from Requirement 16 to design sections for Phase 0 through Phase 6, D-003 anchor, Phase 0 prerequisites, Phase completion conditions, active reopen scope vs `spec.json.reopened`, impact review scope, and proxy_model triage decision mechanization.
5. Check whether the design introduces contradictions with existing Requirement 12 operation registry / preflight design.
6. Check whether the design overclaims implementation that has not been implemented yet. It may define future schema and tasks, but must not state that runtime behavior already exists unless it does.
7. Check whether the manual progress note and reopen in-progress record accurately reflect design drafting completion without prematurely marking triad-review, review-wave, alignment, approval, spec.json workflow_state, commit, or push complete.

## Out Of Scope

- Do not request implementation changes in this design triad-review.
- Do not judge unrelated wording outside the Requirement 13 through 16 design expansion unless it creates a direct contradiction.
- Do not require edits to other features during this gate; cross-feature impact belongs to design review-wave.

## Finding Policy

- Report `must-fix` for contradictions, missing design coverage for approved requirements, state records that falsely claim an uncompleted gate, or design text that would allow unsafe workflow actions.
- Report `should-fix` for ambiguity that could cause repeated manual judgment, unclear schema boundaries, or weak traceability to requirements.
- Return no findings when the design is traceable, internally consistent, and correctly scoped for a design drafting artifact.
