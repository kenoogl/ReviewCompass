# workflow-management requirements triad-review target

run_id: 2026-06-16-workflow-management-requirements-commit-execution-delegation-review-run
phase: requirements
gate: stages/requirements.yaml#triad-review
criteria: workflow_management_commit_execution_delegation_requirements_reopen_triad_review

## Review Scope

This triad-review covers the 2026-06-16 R-0 reopen for formal CLI support for LLM commit execution delegation.

Review the workflow-management requirements update for whether it sufficiently captures the approved requirements delta:

- Requirement 4 acceptance 8 must keep staged content approval and LLM commit execution delegation as separate approvals.
- LLM commit execution delegation must be recordable through a formal CLI path, not by manually editing runtime JSON.
- The delegation approval must be bound to the same nonce challenge, target digest, staged file set, and expiry as the staged content approval.
- The delegation source text must be accepted only through stdin, not argv, and secret/API-key/token/password/credential-like values must not be stored raw.
- Only short explicit commit execution instructions should pass; ambiguous continuation, preparation, or broad autonomy phrases must fail closed.
- The requirement must preserve Requirement 4 acceptance 6 and 7, especially staged-content nonce binding and LLM/provider/model independence.

## Source Documents

- `.reviewcompass/specs/workflow-management/requirements.md`
- `docs/reviews/reopen-classification-2026-06-16-wm-commit-execution-delegation.md`
- `stages/in-progress/reopen-procedure-2026-06-16.yaml`
- `docs/operations/WORKFLOW_PRECHECK_DETAILS.md`
- `tools/check-workflow-action.py`
- `tests/tools/test_check_workflow_action.py`

## Requirements Delta

Requirement 4 now includes acceptance 8:

> 本機能は LLM が `git commit` 実行を代行する場合、staged 内容承認とは別に、LLM への commit 実行代行承認を正式 CLI で記録できなければならない。実行代行承認は、同じ nonce challenge、target digest、staged ファイル集合、有効期限に束縛し、runtime JSON の手編集を正規経路として扱わない。承認文は標準入力からのみ受け取り、argv には載せず、保存する場合は秘匿性のある文字列を redaction し、残留 secret 検出時は本文を保存しない。承認文言は `コミット`、`コミットして`、`コミットを実行`、`commit`、`commitして` のような commit 実行を明示する短い文言に限定し、`次のコミットまで`、`コミット点まで`、`コミット準備`、`自律実行`、`進めて`、`続けて`、`OK`、`承認` のような曖昧または準備・継続を表す文言では fail-closed にする。

The requirements change history also adds:

- 2026-06-16 の reopen R-0（commit-execution-delegation-formal-cli）により、Requirement 4 受入 8 を追加し、staged content approval と LLM commit 実行代行承認を分離したまま、実行代行承認を正式 CLI で記録・検査することを要件化した。既存「不可逆操作の直前ゲート」の commit 承認レコード強化であり、runtime JSON 手編集を正規経路にしない（根拠は `docs/reviews/reopen-classification-2026-06-16-wm-commit-execution-delegation.md`）。本改訂は仕様確定後に TDD で実装する正順の手続きである。

## Existing Context

Requirement 4 acceptance 6 already requires nonce challenge binding for LLM-mediated commit approval:

- Challenge stores staged file list, per-file `target_sha256`, whole-target digest, nonce, expiry, and consumed state.
- Approval record creation and commit gate both check nonce match, challenge not expired, challenge not consumed, staged files/content unchanged, and approval record target digest matching the challenge.
- Missing, malformed, expired, mismatched, or consumed state fails closed.

Requirement 4 acceptance 7 already requires LLM/provider/model independence:

- Validation inputs are limited to staged file set, staged blob hash, target digest, nonce, expiry, and consumed state.
- LLM/provider/model names are not validation inputs.
- The mechanism binds approval to staged content; it does not cryptographically prove that the user uttered the nonce in the UI.

Current implementation context:

- `commit-approval record` intentionally does not embed `execution_delegation` by default.
- `guarded-git-commit.py` / `check-workflow-action.py commit` require `execution_delegation` when `--execution-actor llm`.
- Existing tests already cover that missing execution delegation blocks LLM commit execution and that broad phrases like `自律実行して` are insufficient.
- The gap is that no formal CLI records a valid `execution_delegation`, so manual runtime JSON editing became the only workaround.

## Review Questions

1. Does Requirement 4 acceptance 8 clearly state the externally visible requirement, without over-specifying implementation details that belong in design?
2. Does it preserve the separation between staged content approval and LLM execution delegation?
3. Is it clear that runtime JSON hand editing is not a valid formal path?
4. Is nonce/challenge/target digest/staged file set/expiry binding explicit enough for design and tasks to implement mechanically?
5. Is the stdin-only and redaction requirement sufficient to preserve the existing secret/API-key handling policy?
6. Are the allowed/disallowed instruction examples appropriate at the requirements level, or should any be moved to design?
7. Does the requirement remain LLM/provider/model independent?
8. Are there missing acceptance-level fail-closed cases that must be added before moving to design?

## Expected Output

Return structured findings only. Use severity `ERROR` for blockers, `WARN` for corrections that should be made before requirements review-wave, and `INFO` for non-blocking observations.
