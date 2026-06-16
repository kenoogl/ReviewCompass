# workflow-management requirements triad-review target

run_id: 2026-06-16-workflow-management-requirements-operation-registry-preflight-review-run
phase: requirements
gate: stages/requirements.yaml#triad-review
criteria: workflow_management_operation_registry_preflight_requirements_reopen_triad_review

## Review Scope

This triad-review covers the 2026-06-16 R-0 reopen for operation registry / preflight.

Review whether the workflow-management requirements update captures the approved requirements delta:

- Operation registry / preflight should be a cross-cutting workflow-management contract, not a collection of ad hoc helpers.
- All features are in impact review scope, but workflow-management is the only direct owner at this phase.
- The requirements should cover read-only preflight before creating review-run, post-write, triage, reopen, commit approval, session-record, deployment / export related artifacts.
- The requirements should prevent the recurrent handback patterns recorded in the smell inventory: guessed commands, wrong entrypoints, staged / unstaged diff mixups, approval record gaps, manifest / review target coverage drift, serial approval chain parallelization, current-session formal record creation, and nested issue scope drift.
- The requirement must remain LLM/provider/model independent.

## Source Documents

- `.reviewcompass/specs/workflow-management/requirements.md`
- `docs/reviews/reopen-classification-2026-06-16-wm-operation-registry-preflight.md`
- `stages/in-progress/reopen-procedure-2026-06-16.yaml`
- `docs/notes/2026-06-16-operation-registry-preflight-design.md`
- `docs/notes/2026-06-16-workflow-recovery-smell-inventory.md`
- `docs/notes/2026-06-16-nested-issue-handling-smell.md`

## Requirements Delta

The requirements now add:

```text
Requirement 12: operation registry / preflight
```

The new requirement states that workflow-management must provide a machine-readable operation registry and read-only operation preflight so maintainers start operations from canonical contracts rather than memory, examples, or abbreviated command names.

Acceptance criteria currently require:

1. A registry entry for each operation with operation id, kind, canonical command, required inputs, target identity, planned outputs, sequence mode, worktree policy, pending conflicts, artifact policy, and existing workflow vocabulary references.
2. A read-only operation preflight that creates no artifacts and returns operation availability, missing inputs, pending / dirty / staged conflicts, planned outputs, canonical commands, sequence mode, and the next human-readable step.
3. A common preflight response shape with `OK` / `WARN` / `DEVIATION` verdicts.
4. Command validation before execution, including canonical entrypoint, subcommand, option, required option, and positional argument checks.
5. Worktree / pending conflict checks before mixing post-write pending, reopen in-progress, maintenance in-progress, staged / unstaged changes, unrelated diffs, or stale commit approvals.
6. Review artifact preflight for post-write review, review-run creation, triage decide, document-type preflight, review criteria preflight, and post-write manifest coverage preflight.
7. Serial-only handling for commit approval chain operations.
8. Current-session guard for formal session-record output.
9. Nested issue handling as a preflight target.
10. LLM/provider/model independence.

The change history now records the 2026-06-16 R-0 reopen and the implementation-derived contract trace `XDI-WM-003`.

## Existing Context

The requirements already have these adjacent contracts:

- Requirement 2: `next --json`, post-write target detection, manifest verification, and effective prompt loading.
- Requirement 4: irreversible operation gates, commit approval nonce, and LLM execution delegation.
- Requirement 5: reopen procedure enforcement.
- Requirement 6: session-spanning state and maintenance side tracks.
- Requirement 8: feature dependency map.
- Requirement 9: downstream re-expansion for post-hoc intent.
- Requirement 10: review-wave summary command.
- Requirement 11: decision-source-lint.

The new Requirement 12 should connect these existing parts into operation-level preflight without duplicating their detailed implementation contracts.

## Review Questions

1. Does Requirement 12 state an externally visible requirement rather than design-only detail?
2. Are the operation registry fields sufficient to prevent the recorded handback patterns before artifacts are created?
3. Is read-only Phase 1 preflight clear enough, including what it must not write?
4. Is the command validation requirement strong enough to prevent guessed subcommands, wrong options, and wrong script paths?
5. Is the review artifact preflight scope broad enough to cover review-run, post-write manifest, bundle, triage approval, document type, and review criteria issues?
6. Does the requirement correctly include current-session formal record prevention and nested issue handling without overfitting to one incident?
7. Does the requirement preserve workflow-management ownership while keeping all features in impact review scope?
8. Does the requirement remain LLM/provider/model independent?
9. Are deployment / export operations adequately included as operation registry candidates without forcing premature implementation details?
10. Are any acceptance-level fail-closed cases missing before moving to design?

## Expected Output

Return structured findings only. Use severity `ERROR` for blockers, `WARN` for corrections that should be made before requirements review-wave, and `INFO` for non-blocking observations.
