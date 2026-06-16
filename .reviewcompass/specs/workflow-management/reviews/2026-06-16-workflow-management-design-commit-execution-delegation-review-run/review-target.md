# workflow-management design triad-review target

run_id: 2026-06-16-workflow-management-design-commit-execution-delegation-review-run
phase: design
gate: stages/design.yaml#triad-review
criteria: workflow_management_commit_execution_delegation_design_reopen_triad_review

## Review Scope

This triad-review covers the 2026-06-16 R-0 reopen for formal CLI support for LLM commit execution delegation.

Review the workflow-management design update for whether it sufficiently implements the approved requirements delta:

- Requirement 4 acceptance 8: LLM commit execution delegation must be recorded separately from staged content approval.
- The formal CLI must not require runtime JSON hand editing.
- The delegation record must be bound to the same nonce challenge, target digest, staged file set, and expiry as the staged content approval.
- Delegation must require an existing valid staged-content challenge and staged-content approval record.
- Ambiguous continuation, preparation, or broad autonomy phrases must fail closed.
- Secret/API-key/token/password/credential-like values must not be stored raw; residual secret detection must fail closed.
- The design must preserve Requirement 4 acceptance 6 and 7: staged-content nonce binding and LLM/provider/model independence.

## Source Documents

- `.reviewcompass/specs/workflow-management/requirements.md`
- `.reviewcompass/specs/workflow-management/design.md`
- `docs/reviews/reopen-classification-2026-06-16-wm-commit-execution-delegation.md`
- `.reviewcompass/specs/_cross_feature/reviews/2026-06-16-requirements-commit-execution-delegation-reopen-alignment.md`
- `stages/in-progress/reopen-procedure-2026-06-16.yaml`

## Requirements Delta

Requirement 4 acceptance 8 now requires:

1. LLM commit execution delegation is separate from staged content approval.
2. Formal CLI accepts source text only through stdin and writes a machine-readable delegation record co-located with or referenced by the commit approval record.
3. Runtime JSON hand editing is not a formal path.
4. Delegation record creation requires a valid, unexpired, unconsumed staged-content challenge and staged-content approval record for the same nonce.
5. Out-of-order delegation, missing/expired/consumed challenge, target digest mismatch, staged-content mismatch, and existing unexpired delegation record fail closed.
6. Empty, whitespace-only, non-UTF-8, non-text/binary, and byte-limit-exceeding inputs fail closed.
7. Redaction failure or residual-secret detection fails closed without creating a delegation record.
8. Explicit commit execution phrases are allowed; preparation/continuation/autonomy/general approval phrases are rejected.

## Design Delta

The design adds `§不可逆操作の直前ゲートモデル §2.2 commit 実行代行承認（Req 4 受入 8）`:

- CLI: `tools/check-workflow-action.py commit-approval delegate-execution --nonce <nonce> --source-text-stdin --json`
- `commit-approval record` continues not to write `execution_delegation` by default.
- `delegate-execution` appends `execution_delegation` to `.reviewcompass/runtime/approvals/commit-approval.json`.
- The command succeeds only when the same nonce challenge and staged content approval record exist, are unexpired/unconsumed/not invalidated, and still match the current staged content and target digest.
- Abandoned delegation replacement requires `commit-approval invalidate --json` followed by a new `prepare`.
- `execution_delegation` fields include delegated action, delegated actor, user approval, nonce, target digest, timestamps, normalized instruction, instruction sha256, attestation type, and guarantee scope.
- Delegation expiry equals the challenge expiry and cannot exceed it.
- LLM/provider/model fields are banned from schema and are not validation inputs.
- Stdin payload must be single-line UTF-8 text, non-empty, no NUL, no newline, and at most 256 UTF-8 bytes.
- Normalization trims ASCII/full-width edge spaces, lowercases English, and removes one trailing Japanese period.
- Allowed normalized phrases are exact matches: `コミット`, `コミットして`, `コミットを実行`, `commit`, `commitして`.
- Rejected examples include `次のコミットまで`, `コミット点まで`, `コミット準備`, `コミット可能なところまで`, `自律実行`, `進めて`, `続けて`, `OK`, `承認`.
- Redaction uses `redact_text` and `find_residual_secrets`; redaction failure or residual secret detection fails closed without writing a delegation record.
- Commit gate requires `execution_delegation` when `--execution-actor llm`; `--execution-actor human` does not require delegation.
- Commit success makes delegation non-reusable through the same commit approval consumption path.

## Review Questions

1. Does the design satisfy Requirement 4 acceptance 8 without weakening acceptance 5〜7?
2. Is appending `execution_delegation` to the existing commit approval record compatible with the stated separation between staged content approval and execution delegation?
3. Is the formal CLI specific enough for tasks and TDD implementation to proceed?
4. Are fail-closed cases complete enough for ordering, replay, malformed records, payload boundaries, redaction, residual secret detection, and staged content changes?
5. Is LLM/provider/model independence preserved and mechanically enforceable?
6. Are matching and normalization rules clear enough, and do they avoid treating broad work-continuation phrases as commit execution delegation?
7. Is the guarantee boundary clear enough, especially that this is not cryptographic proof of a UI utterance?
8. Does the design preserve the existing secret/API-key redaction policy?

## Expected Output

Return structured findings only. Use severity `ERROR` for blockers, `WARN` for corrections that should be made before design review-wave, and `INFO` for non-blocking observations.
