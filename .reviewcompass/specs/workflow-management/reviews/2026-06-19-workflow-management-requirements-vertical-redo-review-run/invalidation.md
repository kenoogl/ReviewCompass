# Review Run Invalidation

status: invalid_for_vertical_intent_transfer_review
date: 2026-06-19
invalidated_by: Codex session user correction

## Scope

This review-run must not be used as the formal requirements triad-review evidence for the Requirement 13-16 vertical redo.

It may be retained only as evidence of the failed review-prompt construction pattern.

## Reason

The generated model prompts included `.reviewcompass/specs/workflow-management/requirements.md` as the target document, but the upstream decision materials were included only as path references.

That is insufficient for a vertical intent-transfer review. The models could not directly inspect the upstream purpose, responsibility boundaries, acceptance criteria, forbidden actions, unresolved items, or intended transfer decisions from:

- `docs/reviews/reopen-classification-2026-06-19-wm-requirement-13-16-vertical-redo.md`
- `docs/notes/2026-06-18-integrated-design-selection-execution-layers.md`
- `docs/notes/working/2026-06-18-mechanized-workflow-execution-design.md`
- `docs/notes/working/2026-06-19-integrated-design-requirements-missing.md`
- `docs/operations/SESSION_WORKFLOW_GUIDE.md#vertical-intent-transfer-review`

As a result, findings in this run are not valid evidence that upstream intent was or was not correctly inherited into Requirement 13-16. They may still be read as informal requirements-only observations.

## Invalidated Artifacts

- `review-target.md`
- `prompts/*.prompt.md`
- `raw/*.txt`
- `parsed/*.yaml`
- `rounds.yaml`
- `model-result-summary.yaml`
- `triage.yaml`
- `review_summary.md`
- `proxy-decision-prompt.md`

## Corrective Discipline

The discipline has been updated so that future vertical intent-transfer review prompts must not list source materials only by path. They must materialize the upstream content as excerpts or structured summaries that include purpose, responsibility boundaries, acceptance criteria, forbidden actions, unresolved or design-deferred items, and the intended transfer into the target phase.
