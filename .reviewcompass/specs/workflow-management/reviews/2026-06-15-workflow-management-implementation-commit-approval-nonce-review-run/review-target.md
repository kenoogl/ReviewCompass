---
feature: workflow-management
phase: implementation
stage: triad-review
date: 2026-06-15
reopen: R-0
reopen_topic: commit-approval-nonce
commit_under_review: 3498e67c
variant: implementation_review_independent_3way_codex_operator
target_documents:
  - .reviewcompass/specs/workflow-management/requirements.md
  - .reviewcompass/specs/workflow-management/design.md
  - .reviewcompass/specs/workflow-management/tasks.md
  - .reviewcompass/specs/workflow-management/implementation-drafting.md
target_code:
  - tools/check_workflow_action/commit_approval.py
  - tools/check-workflow-action.py
  - tools/guarded-git-commit.py
  - tests/tools/test_check_workflow_action.py
---

# Review Target：workflow-management implementation commit approval nonce

## Scope

This triad-review covers implementation drafting for reopen R-0
`commit-approval-nonce`, committed as `3498e67c Add commit approval nonce guard`.

Review whether the implementation sufficiently satisfies:

- Requirement 4 acceptance 6: commit approval must be recorded through a nonce
  challenge bound to the staged file set and staged content.
- Requirement 4 acceptance 7: nonce judgment must be independent of the
  controlling LLM, provider, or model.
- design.md irreversible-operation gate model §2.1.
- tasks.md T-004, T-006, and T-011 additions for commit-approval nonce.

Do not re-review unrelated historical workflow-management work except where this
implementation conflicts with it.

## Variant And Role Assignment

Variant: `implementation_review_independent_3way_codex_operator`

| role | path | provider | model |
| --- | --- | --- | --- |
| primary | api | openai-api | gpt-5.4 |
| adversarial | api | anthropic-api | claude-opus-4-8 |
| judgment | api | gemini-api | gemini-3.1-pro-preview |

## Implementation Summary

New module:

- `tools/check_workflow_action/commit_approval.py`

Changed integration points:

- `tools/check-workflow-action.py`
  - imports `check_workflow_action.commit_approval`
  - validates nonce records from `validate_commit_approval`
  - adds `commit-approval prepare/record/invalidate`
  - allows reopen stop-point commit through `commit_stop_point: true`
- `tests/tools/test_check_workflow_action.py`
  - adds nonce CLI, validation, redaction, expiry, forbidden metadata, staged
    mutation, and explicit reopen commit stop-point tests
- `.reviewcompass/specs/workflow-management/implementation-drafting.md`
  - records implementation drafting status and known triad-review targets
- `stages/in-progress/reopen-procedure-2026-06-15-commit-approval-nonce.yaml`
  - records implementation drafting completion and next step

## Behavior Implemented

`commit-approval prepare --json`:

- reads the current staged index
- creates `.reviewcompass/runtime/approvals/commit-approval-challenge.json`
- writes `nonce`, `created_at`, `expires_at`, `ttl_seconds=600`,
  `target_files`, `target_digest`, canonical target entries, `consumed=false`,
  and `invalidated=false`

`commit-approval record --nonce <nonce> --source-text-stdin --json`:

- reads the challenge
- checks nonce, invalidated/consumed state, UTC timestamps, clock rollback, and
  expiry
- recomputes current staged canonical target and compares it with the challenge
  digest
- handles approval source text only through stdin
- calls `redact_text`
- calls `find_residual_secrets`
- writes `.reviewcompass/runtime/approvals/commit-approval.json`

`commit-approval record --nonce <nonce> --no-source-text --json`:

- writes the same nonce-bound approval record without storing source text
- records `source_omission_reason=source_not_provided`

`commit-approval invalidate --json`:

- marks challenge and approval records invalidated when present

`tools/check-workflow-action.py commit`:

- keeps old `target_sha256` approval records as compatibility input
- if an approval record has `nonce`, additionally validates:
  - forbidden fields: `llm`, `provider`, `model`, `model_id`,
    `proxy_model_id`
  - `invalidated` and `consumed`
  - `attestation_type=staged_content_nonce_binding`
  - `guarantee_scope=staged_content_binding_not_ui_utterance_proof`
  - timestamp shape, TTL 10 minutes, clock rollback, and expiry
  - challenge existence and nonce match
  - approval target digest against current staged exact index
  - challenge target digest against current staged exact index
  - approval/challenge target digest equality

## Important Code Shape

The canonical target uses `git diff --cached --name-only -z`, `git diff
--cached --name-status -z`, `git ls-files -s -- <path>`, and `git show :<path>`.
It emits sorted entries:

```python
{
  "path": path,
  "status": "D" if deleted else status,
  "mode": None if deleted else index_entry["mode"],
  "object_id": "DELETED" if deleted else index_entry["object_id"],
  "sha256": "DELETED" if deleted else blob_sha,
}
```

The digest is `sha256(json.dumps(data, sort_keys=True, separators=(",", ":")))`
over:

```python
{
  "algorithm": "commit-approval-v1",
  "entries": entries,
}
```

Approval record contains:

```yaml
approved_action: commit
approved_by: user
nonce: <challenge nonce>
target_digest:
  algorithm: commit-approval-v1
  digest: <current staged digest>
attestation_type: staged_content_nonce_binding
guarantee_scope: staged_content_binding_not_ui_utterance_proof
execution_delegation:
  delegated_to: llm
  approved_by: user
  explicit_instruction: コミット代行も含めて自律実行
```

## Tests Added Or Updated

Added coverage includes:

- `test_commit_approval_prepare_outputs_nonce_challenge_json`
- `test_commit_approval_record_no_source_json_validates_for_commit`
- `test_commit_approval_record_source_text_is_redacted`
- `test_commit_approval_record_residual_secret_omits_source`
- `test_commit_approval_rejects_staged_change_after_record`
- `test_commit_approval_rejects_expired_record`
- `test_commit_approval_rejects_llm_metadata_fields`
- `test_commit_allows_reopen_explicit_commit_stop_point_field`

Regression suite run before commit:

- `.venv/bin/python3 -m unittest tests.tools.test_check_workflow_action.CommitExitCodeTests tests.tools.test_guarded_git_commit tests.tools.test_runtime_placement_freeze.CommitApprovalPlacementTests -v`
- result: pass, 52 tests

## Known Concerns To Review

The implementation-drafting note explicitly lists these as triad-review targets:

- consume persistence failure after commit is not fully proven by tests
- normal git execution failure conditional retry is not fully implemented
- malformed record no-partial-inference coverage is incomplete
- deletion staged and path-order-independence have old compatibility coverage,
  but nonce-specific regression coverage is limited

Also review whether:

- `commit-approval record` should embed execution delegation by default, or
  whether that conflates approval record creation with LLM commit execution
  delegation
- `source_omission_reason: null` when redacted source text is stored is acceptable
  under the source omission enum contract
- `record` invalidates malformed or mismatched challenges consistently enough
- `validate` invalidation on security failure is safe when the record was loaded
  from a legacy fallback path
- challenge consumption is complete: guarded commit currently consumes the
  approval record, while challenge consumption may not be persisted
- the exact index check covers renames, copies, delete/add pairs, mode changes,
  submodules, and unusual paths
- automatic `commit_stop_point: true` support is sufficiently constrained and
  documented for reopen stop-point commits

## Review Questions

1. Does the implementation satisfy Requirement 4 acceptance 6 and 7 at the
   behavior boundary?
2. Does the implementation preserve LLM/provider/model independence in the
   machine validation path?
3. Are malformed challenge/approval records rejected without partial inference?
4. Are redaction and residual secret handling safe enough for source-text
   evidence?
5. Is the staged exact index digest stable and complete enough for deployable
   use?
6. Are consume/invalidate/retry semantics sufficiently implemented, or are
   there must-fix gaps before implementation approval?
7. Do the tests cover the risky behavior implied by design.md and tasks.md?

## Expected Output

Return findings with severity and evidence. Classify issues as:

- `must-fix`: implementation triad-review should not complete before correction.
- `should-fix`: correction is recommended before approval unless explicitly accepted.
- `leave-as-is`: no change needed.

Prefer concrete references to files, functions, and behavior. If a finding is
already listed in Known Concerns, still report it if it should block or shape
the next implementation step.
