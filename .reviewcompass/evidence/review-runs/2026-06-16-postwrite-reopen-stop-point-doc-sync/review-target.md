# Post-write verification target: reopen stop point doc sync

## User Decision

- The user asked to perform consistency corrections after confirming source materials for structured reopen stop point commit judgment.
- Scope is documentation consistency only, not implementation changes.

## Intended Changes

- `TODO_NEXT_SESSION.md`
  - Mark reopen stop point commit judgment as already migrated away from `next_step` text matching.
  - Record that the remaining reopen hand-edit reduction task is approval blocker structuring.
- `docs/operations/WORKFLOW_PRECHECK_DETAILS.md`
  - Add the omitted structured fields saved by `reopen-advance-step --from-step 2`: `commit_stop_point_step: 2` and `commit_stop_point_kind: canonical_update_complete`.

## Verification Criteria

- The written notes should match current implementation behavior:
  - `is_reopen_stop_point_commit_allowed` relies on structured fields, not only `next_step` text.
  - `reopen-advance-step --from-step 2` writes the structured stop point fields.
- The notes should not claim new implementation work was performed in this turn.
- The remaining task should not continue to list stop point commit judgment structuring as undone.
