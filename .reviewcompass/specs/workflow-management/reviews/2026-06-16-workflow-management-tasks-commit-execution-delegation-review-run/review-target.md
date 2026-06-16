---
feature: workflow-management
phase: tasks
stage: triad-review
date: 2026-06-16
reopen: R-0
reopen_topic: commit-execution-delegation-formal-cli
target_documents:
  - .reviewcompass/specs/workflow-management/requirements.md
  - .reviewcompass/specs/workflow-management/design.md
  - .reviewcompass/specs/workflow-management/tasks.md
---

# Review Target：workflow-management tasks commit execution delegation formal CLI

## Scope

This triad-review covers the tasks drafting update for reopen R-0 `commit-execution-delegation-formal-cli`.

Review whether `.reviewcompass/specs/workflow-management/tasks.md` correctly and sufficiently translates:

- Requirement 4 acceptance criterion 8
- design.md §不可逆操作の直前ゲートモデル §2.2
- design triad-review C1〜C6 resolution, including user-selected Option A
- design review-wave no-impact decision
- design alignment decision

Do not re-review unrelated historic tasks except where the new text conflicts with them.

## Requirements Basis

Requirement 4 acceptance 8 requires:

- LLM commit execution delegation is recorded through a formal CLI, not by manual runtime JSON editing.
- Delegation requires an existing valid challenge and staged content approval record for the same nonce.
- Delegation must fail closed before staged content approval, on malformed / empty / oversized / unsafe input, on existing unexpired delegation, and on residual secret detection.
- Delegation must be bound to the same staged file set and staged content approval context.
- The judgment must not depend on LLM, provider, or model identity.

## Design Basis

design.md §2.2 defines:

- Formal CLI: `tools/check-workflow-action.py commit-approval delegate-execution --nonce <nonce> --source-text-stdin --json`
- No argv source text input.
- `commit-approval.json` remains staged-content approval only.
- Delegation is stored separately in `.reviewcompass/runtime/approvals/commit-execution-delegation.json`.
- Delegation record must bind to nonce, target digest, staged file set digest, staged content approval digest, challenge path, approval record path, expiry, instruction hash, `attestation_type`, and `guarantee_scope`.
- Strict schema rejects unknown fields and LLM/provider/model identity fields.
- stdin normalization allows one trailing POSIX LF only, rejects CR / CRLF / internal newline / multiple final LF / NUL / empty / whitespace-only / oversized input, lowercases ASCII only, strips one trailing Japanese period, and rejects full-width Latin variants by exact match failure.
- Allowed phrases are exact-match only: `コミット`, `コミットして`, `コミットを実行`, `commit`, `commitして`.
- Secret redaction uses `redact_text` and `find_residual_secrets`; failure or residual secret prevents delegation record creation.
- Delegation write requires revalidation immediately before write and atomic write.
- Commit gate with `--execution-actor llm` requires delegation and revalidates challenge, staged approval, delegation, and current index.
- Commit gate with `--execution-actor human` does not require delegation.
- `commit-approval invalidate --json` invalidates challenge, staged content approval record, and delegation record together.

## Tasks Drafting Changes To Review

tasks.md now states:

- The total remains 13 tasks; commit-execution-delegation-formal-cli does not add a new task.
- T-004 includes `commit-approval delegate-execution --nonce <nonce> --source-text-stdin --json`.
- T-004 requires no argv source text, JSON-only happy path output, valid challenge / staged content approval prerequisite, and stdin input edge-case handling.
- T-006 now covers Requirement 4 acceptance 1-8.
- T-006 owns delegation record generation, validation, invalidate, consume, `--execution-actor llm` gate, and human actor exemption.
- T-006 completion conditions and test requirements cover strict schema, staged content binding, stdin normalization, redaction failure, residual secret detection, atomic write, expiry race, malformed / duplicate delegation, and invalidate / consume.
- Requirements traceability maps Requirement 4 acceptance 8 to T-004 / T-006 / T-011.
- Task design notes and XDI-WM-001 mention commit execution delegation.

## Review Questions

1. Does tasks.md sufficiently translate Requirement 4 acceptance 8 into implementable tasks and tests?
2. Does the decision not to create a new task preserve task ownership and avoid hiding required implementation work?
3. Are T-004, T-006, and T-011 the correct task owners?
4. Are any design details missing from task responsibilities, completion conditions, tests, traceability, or XDI notes?
5. Does the tasks update preserve separation between staged content approval and LLM execution delegation?
6. Does the tasks update preserve LLM / provider / model independence?
7. Does the tasks update introduce contradictions with existing nonce challenge tasks or decision-source-lint T-013?

## Expected Output

Return findings with severity and evidence. Classify issues as:

- `must-fix`: tasks approval should not proceed before correction.
- `should-fix`: correction is recommended before approval unless explicitly accepted.
- `leave-as-is`: no change needed.
