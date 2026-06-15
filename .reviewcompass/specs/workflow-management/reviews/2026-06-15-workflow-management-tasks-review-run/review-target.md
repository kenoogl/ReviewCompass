---
feature: workflow-management
phase: tasks
stage: triad-review
date: 2026-06-15
reopen: R-0
reopen_topic: commit-approval-nonce
target_documents:
  - .reviewcompass/specs/workflow-management/requirements.md
  - .reviewcompass/specs/workflow-management/design.md
  - .reviewcompass/specs/workflow-management/tasks.md
---

# Review Target：workflow-management tasks commit approval nonce

## Scope

This triad-review covers the tasks drafting update for reopen R-0 `commit-approval-nonce`.

Review whether `.reviewcompass/specs/workflow-management/tasks.md` correctly and sufficiently translates:

- Requirement 4 acceptance criteria 6 and 7
- design.md §不可逆操作の直前ゲートモデル §2.1
- design approval evidence for commit approval nonce

Do not re-review unrelated historic tasks except where the new text conflicts with them.

## Requirements Basis

Requirement 4 acceptance 6:

- Commit approval must be recorded through a nonce challenge bound to staged file set and staged content.
- Challenge stores staged files, per-file `target_sha256`, whole target digest, nonce, expiry, and consumed state.
- Approval record creation and commit gate must check nonce match, unexpired challenge, unconsumed state, staged file set/content match, and approval/challenge target digest match.
- Missing, malformed, expired, mismatched, or consumed state must fail closed.

Requirement 4 acceptance 7:

- Commit approval nonce judgment must not depend on controlling LLM, provider, or model.
- Inputs are staged file set, staged blob hash, target digest, nonce, expiry, and consumed state.
- Model/provider differences are limited to user-facing explanation text.
- The guarantee is staged-content binding, not cryptographic proof of a UI utterance.

## Design Basis

design.md §2.1 defines:

- Challenge path: `.reviewcompass/runtime/approvals/commit-approval-challenge.json`
- Approval record path: `.reviewcompass/runtime/approvals/commit-approval.json`
- `commit-approval prepare --json`
- `commit-approval record --nonce <nonce> --source-text-stdin --json`
- `commit-approval record --nonce <nonce> --no-source-text --json`
- `commit-approval invalidate --json`
- Canonical digest `commit-approval-v1`
- UTC ISO-8601 `created_at` / `expires_at`, TTL 10 minutes, `now_utc` test injection, clock rollback fail-closed
- Malformed challenge / approval record fail-closed with no partial inference
- Schema rejection for `llm`, `provider`, `model`, `model_id`, `proxy_model_id`
- `attestation_type=staged_content_nonce_binding`
- `guarantee_scope=staged_content_binding_not_ui_utterance_proof`
- stdin or no-store approval source text only, no argv source text
- Redaction with `tools.session_record_extractor.redact.redact_text`
- Residual secret detection with `find_residual_secrets`
- `source_omission_reason` enum: `source_not_provided`, `unsafe_source_omitted`, `redaction_failed`, `residual_secret_detected`
- Commit path validates the exact index
- Security validation failure invalidates challenge/approval
- Successful commit consumes challenge/approval
- Consume persistence failure rejects later reuse

## Tasks Drafting Changes To Review

tasks.md now states:

- The total remains 13 tasks; commit-approval-nonce does not add a new task.
- T-004 includes commit approval nonce subcommands:
  - `commit-approval prepare --json`
  - `commit-approval record --nonce <nonce> --source-text-stdin --json`
  - `commit-approval record --nonce <nonce> --no-source-text --json`
  - `commit-approval invalidate --json`
  - no argv source text input
- T-006 now covers Requirement 4 acceptance 1-7.
- T-006 owns `tools/check_workflow_action/commit_approval.py`.
- T-006 validation covers challenge / approval read, nonce, expiry, consumed state, staged file set/content, target digest, schema forbidden LLM/provider/model fields, redaction, invalidation, consume, and retry behavior.
- Requirements traceability now maps Requirement 4 acceptance 5, 6, and 7 to T-004 / T-006 / T-011.
- Change intent and XDI-WM-001 now mention commit-approval-nonce.

## Review Questions

1. Does tasks.md sufficiently translate Requirement 4 acceptance 6-7 into implementable tasks and tests?
2. Does the decision not to create a new task preserve task ownership and avoid hiding required implementation work?
3. Are T-004, T-006, and T-011 the correct task owners?
4. Are any required design details missing from task responsibilities, completion conditions, tests, traceability, or XDI notes?
5. Does the tasks update introduce contradictions with existing T-004/T-006/T-011 or with decision-source-lint T-013?

## Expected Output

Return findings with severity and evidence. Classify issues as:

- `must-fix`: tasks approval should not proceed before correction.
- `should-fix`: correction is recommended before approval unless explicitly accepted.
- `leave-as-is`: no change needed.
