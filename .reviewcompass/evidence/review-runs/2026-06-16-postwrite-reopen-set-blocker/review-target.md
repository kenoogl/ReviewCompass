# Post-write verification target: reopen set blocker docs

## User Decision

- The user asked to execute the reopen approval gate blocker structuring task after reviewing source materials.
- The chosen approach is to add a dedicated `reopen-set-blocker` operation rather than overloading `reopen-advance-gate`.

## Intended Documentation Changes

- `TODO_NEXT_SESSION.md`
  - Mark reopen approval blocker structuring as completed.
  - Record that `reopen-set-blocker` writes structured `current_blocker` records for approval gates.
- `docs/operations/WORKFLOW_PRECHECK.md`
  - Add `reopen-set-blocker` to the precheck command list and summary.
- `docs/operations/WORKFLOW_PRECHECK_DETAILS.md`
  - Add the detailed invocation and validation contract for `reopen-set-blocker`.

## Implementation Context

- `reopen-set-blocker` only targets the head `pending_gates` entry when it is `stages/<phase>.yaml#approval`.
- It requires `--actor human|proxy_model`, `--rationale`, and at least one `--evidence`.
- It writes `current_blocker` as a structured object with `blocker_type`, `gate`, `actor`, `status`, `rationale`, and `evidence`.
- Existing string `current_blocker` values remain compatible with `next --json`.

## Verification Criteria

- The documentation matches the implementation behavior above.
- The documentation does not imply that `reopen-advance-gate` creates blockers.
- The remaining-task list no longer presents this task as unimplemented.
