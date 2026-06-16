# workflow-management implementation triad-review R2 summary：commit execution delegation formal CLI

## Review Run

- Run: `2026-06-16-r2-workflow-management-implementation-review-run`
- Variant: `implementation_review_independent_3way_codex_operator`
- Phase: `implementation`
- Gate: `stages/implementation.yaml#triad-review`
- Target: `.reviewcompass/specs/workflow-management/reviews/2026-06-16-r2-workflow-management-implementation-review-run/review-target.md`
- Criteria: `workflow_management_commit_execution_delegation_implementation_reopen_triad_review_r2`

## Role Assignments

| role | provider | model | raw |
| --- | --- | --- | --- |
| primary | openai-api | gpt-5.4 | `raw/gpt-5.4.round-1.txt` |
| adversarial | anthropic-api | claude-opus-4-8 | `raw/claude-opus-4-8.round-1.txt` |
| judgment | gemini-api | gemini-3.1-pro-preview | `raw/gemini-3.1-pro-preview.round-1.txt` |

## Model Result Summary

| model | findings | severity |
| --- | ---: | --- |
| gpt-5.4 | 3 | WARN 2, INFO 1 |
| claude-opus-4-8 | 6 | ERROR 1, WARN 3, INFO 2 |
| gemini-3.1-pro-preview | 1 | WARN 1 |

## Same-Root Clusters And Proposed Triage

### C1: malformed existing delegation can be overwritten instead of fail-closed

- Sources: adversarial-001
- Proposed label: `must-fix`
- Summary: `delegate_execution` checks an existing delegation record and allows overwrite when `expires_at` is missing or unparseable because `_parse_datetime(...)` returns `None` and the duplicate guard only blocks when `(expires_at is None or expires_at > utc_now())` was intended but currently needs explicit malformed-record handling. A malformed, unconsumed delegation record should fail closed instead of being treated as overwrite-eligible.
- Plain explanation: if a previous delegation file is broken or tampered with, the safe behavior is to stop. Replacing it silently makes it harder to know whether the commit authorization path was clean.
- Proposed handling: add a failing test for an existing unconsumed delegation with missing/invalid `expires_at`, then change `delegate_execution` to reject malformed existing records unless they are explicitly consumed or invalidated.

### C2: strict-schema / identity-field negative tests are missing

- Sources: primary-001, adversarial-004, judgment-001
- Proposed label: `should-fix`
- Summary: implementation rejects unknown fields and forbidden LLM/provider/model fields, but tests only prove generated records omit those fields. A negative test should mutate `commit-execution-delegation.json` with an unknown field and an identity field and assert commit precheck returns 2.
- Proposed handling: add focused tests before approval.

### C3: redaction failure / residual-secret negative tests are missing

- Sources: primary-002, adversarial-004, judgment-001
- Proposed label: `should-fix`
- Summary: `delegate_execution` aborts when `_redact_source` reports failure or findings, but tests do not force that path. Since this is a fail-closed security path, focused unit tests should monkeypatch or otherwise force redaction failure / residual findings.
- Proposed handling: add focused tests before approval, or explicitly approve as a follow-up if exact phrase matching is considered enough for now.

### C4: pre-write digest revalidation should recompute all persisted digests from one fresh snapshot

- Sources: adversarial-002
- Proposed label: `should-fix`
- Summary: pre-write revalidation compares the fresh aggregate canonical digest to the earlier snapshot, but `staged_file_set_digest` is not recomputed from the fresh snapshot immediately before write. The practical risk is narrow because the aggregate digest covers entries, but recomputing all persisted digests from one fresh canonical target would make the implementation cleaner and easier to audit.
- Proposed handling: recompute fresh canonical target just before write and derive both `target_digest` and `staged_file_set_digest` from that snapshot.

### C5: legacy embedded execution_delegation branch remains under-explained

- Sources: adversarial-003
- Proposed label: `should-fix`
- Summary: nonce-based formal approval uses the new separate delegation file. However, the legacy non-nonce branch still accepts embedded `execution_delegation` for simple approval records. Review target did not show enough evidence that this cannot bypass the formal nonce path.
- Proposed handling: either add a test documenting that nonce approvals always require the separate file even if `execution_delegation` is embedded, or record the legacy branch as compatibility-only and defer its removal/rework.

### C6: argparse-required `--source-text-stdin` makes the runtime flag effectively ceremonial

- Sources: primary-003
- Proposed label: `leave-as-is`
- Summary: the subcommand parser requires `--source-text-stdin`, while the command branch always reads stdin. This is acceptable because argparse blocks accidental invocation without the flag.

### C7: trailing LF and byte-limit behavior is sound

- Sources: adversarial-005
- Proposed label: `leave-as-is`
- Summary: trailing LF handling and pre-normalization byte limit are conservative and match fail-closed intent.

### C8: runtime path portability depends on `.reviewcompass/runtime/` ignore setup

- Sources: adversarial-006
- Proposed label: `leave-as-is`
- Summary: the project already ignores `.reviewcompass/runtime/`. For external deployments, initial setup guidance already instructs adding that ignore entry. No implementation change is proposed in this reopen item.

## Stop Point

This is the user-visible triage gate. Do not ask proxy_model, edit implementation, update spec.json, move the phase, or commit this reopen implementation bundle until the triage decisions are approved by the user or proxy_model under an approved proxy-mode request.

## User Decision And Resolution

- Approval source: 2026-06-16 利用者発言「次へ」
- Decision: C1 は `must-fix`、C2〜C5 は `should-fix`、C6〜C8 は `leave-as-is` として対処する。
- C1 resolution: malformed `expires_at` を持つ未消費 delegation record は既存実装で既に fail-closed だった。`test_commit_approval_delegate_execution_rejects_malformed_existing_delegation` を追加し、上書きされず exit 2 になることを回帰テストで固定した。
- C2 resolution: `test_commit_rejects_execution_delegation_with_unknown_field` と `test_commit_rejects_execution_delegation_with_identity_field` を追加し、unknown field と LLM/provider/model 系 field の混入が commit gate で遮断されることを固定した。
- C3 resolution: `test_commit_approval_delegate_execution_redaction_failure_does_not_write_record` を追加し、redaction failure では delegation record を作らず fail-closed することを固定した。
- C4 resolution: `delegate_execution` の保存直前処理を修正し、fresh canonical target から `target_digest` と `staged_file_set_digest` を再設定してから atomic write するようにした。
- C5 resolution: `test_nonce_commit_rejects_embedded_execution_delegation_without_separate_record` を追加し、nonce 承認では embedded `execution_delegation` があっても別 record なしなら遮断することを固定した。
- Verification: `.venv/bin/python3 -m unittest tests.tools.test_check_workflow_action.CommitExitCodeTests -v`、`.venv/bin/python3 -m unittest tests.tools.test_guarded_git_commit -v`、`PYTHONPYCACHEPREFIX=/tmp/reviewcompass-pycache python3 -m py_compile tools/check-workflow-action.py tools/check_workflow_action/commit_approval.py tools/guarded-git-commit.py`、`git diff --check` が通過した。
