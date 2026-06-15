# workflow-management design triad-review target

run_id: 2026-06-15-workflow-management-design-review-run
phase: design
gate: stages/design.yaml#triad-review
criteria: workflow_management_commit_approval_nonce_design_reopen_triad_review

## Review Scope

This triad-review covers the 2026-06-15 R-0 reopen for commit approval nonce binding.

Review the workflow-management design update for whether it sufficiently implements the approved requirements delta:

- Requirement 4 acceptance 6: commit approval must be recorded through a nonce challenge bound to the staged file set and staged contents.
- Requirement 4 acceptance 7: nonce validation must not depend on the operating LLM, provider, or model name.
- The design must preserve the existing pre-operation gate model and fail-closed behavior.
- The design must preserve the existing policy that API keys, tokens, secrets, passwords, and credentials are not stored raw in logs or approval records.

## Source Documents

- `.reviewcompass/specs/workflow-management/requirements.md`
- `.reviewcompass/specs/workflow-management/design.md`
- `stages/in-progress/reopen-procedure-2026-06-15-commit-approval-nonce.yaml`

## Requirements Delta

Requirement 4 now includes:

1. Commit approval challenge stores staged file list, per-file `target_sha256`, whole-target digest, nonce, expiry, and consumed state.
2. Approval record creation and commit gate both check nonce match, challenge not expired, challenge not consumed, staged files/content unchanged, and approval record target digest matching the challenge.
3. Missing, malformed, expired, mismatched, or consumed state fails closed.
4. Validation inputs are limited to staged file set, staged blob hash, target digest, nonce, expiry, and consumed state.
5. LLM/provider/model names are not validation inputs.
6. This mechanism guarantees binding approval to staged content; it does not cryptographically prove that the user uttered the nonce in the UI.

## Design Delta

The design adds `§不可逆操作の直前ゲートモデル §2.1 commit 承認 nonce challenge（Req 4 受入 6〜7）`:

- Challenge path: `.reviewcompass/runtime/approvals/commit-approval-challenge.json`
- Approval record path: `.reviewcompass/runtime/approvals/commit-approval.json`
- Prepare command: `tools/check-workflow-action.py commit-approval prepare --json`
- Record command: `tools/check-workflow-action.py commit-approval record --nonce <nonce> --source-text <user text> --json`
- Target digest is computed from normalized staged paths and staged blob hashes in stable order.
- Record creation checks challenge existence, nonce match, not expired, not consumed, and current staged content matching challenge.
- Commit gate checks both approval record and challenge: nonce, expiry, consumed state, target digest, staged file set, and staged content.
- Commit success consumes challenge and approval record; commit failure does not consume them.
- Source text is stored only after the existing sensitive-information removal policy; unsafe source text is omitted with an omission reason.
- Validation does not depend on LLM/provider/model.
- UI signature/runtime event signature is explicitly out of scope for this reopen.

## Review Questions

1. Does the design satisfy Requirement 4 acceptance 6 and 7 without contradicting existing Requirement 4 acceptance 1〜5?
2. Is the command/API surface specific enough for tasks and TDD implementation to proceed?
3. Are fail-closed cases complete enough for missing challenge, malformed challenge, expired nonce, consumed challenge, staged content mismatch, approval record mismatch, and unsafe source text?
4. Is the LLM/provider/model non-dependence explicit and enforceable from the design?
5. Is the guarantee boundary clear enough, especially that this binds approval to staged content but does not cryptographically prove a UI utterance?
6. Does the design preserve the existing secret/API-key redaction policy when logging approval source text?

## Expected Output

Return structured findings only. Use severity `ERROR` for blockers, `WARN` for corrections that should be made before design review-wave, and `INFO` for non-blocking observations.
