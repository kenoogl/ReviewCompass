# C5 Post-Fix Recheck

## Scope

- Target artifact: `.reviewcompass/specs/workflow-management/design.md`
- Cluster: C5
- Source findings:
  - `2026-06-20-workflow-management-design-vertical-redo-review-run-v2-gpt-5.4-primary-005`
  - `2026-06-20-workflow-management-design-vertical-redo-review-run-v2-claude-sonnet-4-6-adversarial-007`
- Recheck date: 2026-06-20

## Issue Summary

C5 said Phase 0 completion criteria were not fully design-level. The design omitted mechanical workflow-state repair detection from the Phase 0 row and referenced D-003 failure tests by working-note section instead of enumerating the tests in the design.

## Applied Design Response

`design.md` Requirement 16 now states:

- Phase 0 completion requires mechanical workflow-state repair detection.
- Phase 0 completion does not depend on the section number of the D-003 working note.
- The six D-003 failure tests are enumerated directly in the design:
  1. `commit_stop_point=true` returns `commit_stop_point` with no active gate.
  2. `current_blocker` returns `wait_for_human_decision` with no active gate.
  3. Missing full gates for `canonical_update_phases` returns `DEVIATION` and `repair_workflow_state`.
  4. `phase` / `stage` are non-null only when a reopen step 3 active gate exists.
  5. After a committed stop point is present in clean HEAD, `advance_reopen_after_commit_stop_point` is returned and the same stop point is not repeated.
  6. Required-action JSON mutual exclusion is validated by fixture.
- Repair detection must also cover active scope missing / inconsistent cases before Phase 0 is complete.

## Verification

The following checks were run:

```text
rg -n 'mechanical workflow-state repair detection|commit_stop_point=true|current_blocker.*wait_for_human_decision|canonical_update_phases|advance_reopen_after_commit_stop_point|JSON 相互排他|active scope 欠落|repair detection' .reviewcompass/specs/workflow-management/design.md

.venv/bin/python3 -m pytest tools/api_providers/tests -q
```

Outcome:

- The Phase 0 row includes mechanical workflow-state repair detection.
- The six D-003 failure tests are present in `design.md`.
- Repair detection for active scope missing / inconsistent cases is present.
- `tools/api_providers/tests`: 152 passed.

## Result

C5 is addressed by the current `design.md` edits.

## Remaining Limits

This recheck addresses C5 only. It does not decide C6-C7, does not authorize `spec.json` mutation, does not complete the design gate, and does not authorize commit, push, phase transition, or reopen finalization.
