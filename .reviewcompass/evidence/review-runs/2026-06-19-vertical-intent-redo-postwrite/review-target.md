# Post-write Review Target

criteria_id: vertical_intent_redo_reopen_post_write
phase: post_write_verification
generated_at: 2026-06-19T12:51:10.404794+00:00

## Change Summary

Add vertical intent transfer review discipline, wire it into workflow discipline map, and record the Requirement 13-16 R-0 reopen classification used to restart requirements/design/tasks regeneration.

## Review Question

Verify that the post-write documents accurately reflect the user-agreed vertical intent transfer discipline and the Requirement 13-16 reopen decision without contradicting existing workflow or approval rules.

## Target Files

- docs/operations/SESSION_WORKFLOW_GUIDE.md sha256=e5f4685948f01a41e4a26682d822726ec6dc56c7ee831853fba2a63ef5a45b03
- docs/operations/WORKFLOW_DISCIPLINE_MAP.yaml sha256=e87d5572185ca09f8d37e6faf0c4c40f7ecbcad11b9463cb8d3c8be6d301d7e7
- docs/reviews/reopen-classification-2026-06-19-wm-requirement-13-16-vertical-redo.md sha256=a0b5f927a68f02648bb1c9277a7efb9909ffdcff0e230f20e0d6f15e30f96f9a

## Scope

- Check whether the changed target files clearly state the intended contract.
- Check whether related instructions are mutually consistent across targets.
- Check whether the documented procedure is actionable before API review, triage, manifest, or commit steps continue.

## Out Of Scope

- Do not request unrelated refactors or style-only rewrites.
- Do not judge files that are not listed in Target Files.
- Do not treat missing implementation work as a document defect unless the target text claims it already exists.

## Finding Policy

- Report must-fix findings for contradictions, missing required gates, or instructions that would allow an unsafe workflow action.
- Report should-fix findings for ambiguity that could cause repeated manual judgment or unnecessary API review loops.
- Return findings: [] when the target files are internally consistent for this review question.

## Sensitive Information Check

- status: passed
- External API review must not proceed if this section reports potential secrets.
