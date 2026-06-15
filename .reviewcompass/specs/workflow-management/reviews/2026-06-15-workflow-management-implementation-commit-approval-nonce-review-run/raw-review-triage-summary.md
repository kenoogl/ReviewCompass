# workflow-management implementation triad-review summary：commit approval nonce

## Review Run

- Run ID: `2026-06-15-workflow-management-implementation-commit-approval-nonce-review-run`
- Gate: `stages/implementation.yaml#triad-review`
- Variant: `implementation_review_independent_3way_codex_operator`
- Target: `.reviewcompass/specs/workflow-management/reviews/2026-06-15-workflow-management-implementation-commit-approval-nonce-review-run/review-target.md`
- Commit under review: `3498e67c Add commit approval nonce guard`

## Role Assignments

| role | path | provider | model | raw |
| --- | --- | --- | --- | --- |
| primary | api | openai-api | gpt-5.4 | `raw/gpt-5.4.round-1.txt` |
| adversarial | api | anthropic-api | claude-opus-4-8 | `raw/claude-opus-4-8.round-1.txt` |
| judgment | api | gemini-api | gemini-3.1-pro-preview | `raw/gemini-3.1-pro-preview.round-1.txt` |

## Model Result Summary

| model | parse_status | findings | severity |
| --- | --- | ---: | --- |
| gpt-5.4 | parsed | 4 | ERROR:1, WARN:2, INFO:1 |
| claude-opus-4-8 | parsed | 9 | CRITICAL:1, ERROR:3, WARN:4, INFO:1 |
| gemini-3.1-pro-preview | parsed | 5 | ERROR:2, WARN:3 |

All three raw responses were read by the main session LLM before this summary.

## Same-Root Clusters And Triage Proposal

### C1 challenge consumption is incomplete

- Proposed label: `must-fix`
- Source findings:
  - `gpt-5.4-primary-001` ERROR
  - `claude-opus-4-8-adversarial-001` CRITICAL
  - `claude-opus-4-8-adversarial-002` ERROR
  - `gemini-3.1-pro-preview-judgment-002` ERROR
- Summary: successful commit consumes the approval record, but the challenge record is not durably consumed. This weakens the single-use nonce guarantee and can leave replay or inconsistent-state risk.
- Candidate options:
  - A: consume both approval and challenge after successful commit, and fail closed if consume persistence fails.
  - B: make approval record the sole authoritative nonce state and remove challenge reuse paths after record creation.
  - C: leave as-is and document that approval consumption is sufficient.
- Recommendation: A. Requirement 4 acceptance 6 describes challenge consumed state, so challenge consumption should be first-class and tested.

### C2 execution_delegation is embedded by default in nonce approval records

- Proposed label: `must-fix`
- Source findings:
  - `gpt-5.4-primary-002` WARN
  - `claude-opus-4-8-adversarial-003` ERROR
  - `gemini-3.1-pro-preview-judgment-001` ERROR
- Summary: `commit-approval record` writes `execution_delegation` with `delegated_to: llm` by default. This conflates staged-content approval with LLM commit execution delegation.
- Candidate options:
  - A: remove execution delegation from `commit-approval record`; require a separate explicit delegation record or field supplied by guarded commit flow.
  - B: keep the field but make it optional and never default to LLM delegation.
  - C: leave as-is and rely on current explicit instruction string.
- Recommendation: A or B. The nonce approval record should remain LLM/provider/model independent.

### C3 exact-index digest edge cases are under-tested and may be incomplete

- Proposed label: `must-fix`
- Source findings:
  - `gpt-5.4-primary-003` WARN
  - `claude-opus-4-8-adversarial-004` ERROR
  - `gemini-3.1-pro-preview-judgment-003` WARN
- Summary: nonce-specific tests do not cover rename/copy/mode/submodule/unusual path cases. Reviewers also flagged possible `git diff --cached --name-status -z` parsing issues for rename/copy outputs.
- Candidate options:
  - A: add nonce-specific red tests for rename, copy, deletion, mode change, path order, and unusual paths, then adjust canonicalization as needed.
  - B: simplify canonicalization to rely on `git diff --cached --raw -z` or another single source of exact index data.
  - C: defer edge cases because normal blob add/modify/delete passes current tests.
- Recommendation: A, with B considered if tests expose parser fragility.

### C4 malformed/no-partial-inference coverage is insufficient

- Proposed label: `must-fix`
- Source findings:
  - `gpt-5.4-primary-003` WARN
  - `claude-opus-4-8-adversarial-008` WARN
  - `gemini-3.1-pro-preview-judgment-005` WARN
- Summary: tests do not yet prove that malformed challenge/approval JSON and structurally partial records fail closed without inference.
- Candidate options:
  - A: add malformed challenge and malformed approval tests for non-object, missing required fields, wrong types, duplicate/unknown paths, wrong digest shape, wrong nonce, and invalid timestamps.
  - B: only add tests for the fields most directly used by current validation.
  - C: leave as-is because JSON/object parsing already exists.
- Recommendation: A. The design explicitly requires no partial inference.

### C5 source_omission_reason null is ambiguous

- Proposed label: `should-fix`
- Source findings:
  - `claude-opus-4-8-adversarial-006` WARN
  - `gemini-3.1-pro-preview-judgment-004` WARN
- Summary: when redacted source text is stored, `source_omission_reason` is `null`. The enum contract is clearer if the key is omitted when source is stored, or if a separate explicit value is added.
- Candidate options:
  - A: omit `source_omission_reason` when source text is stored.
  - B: extend the enum with a stored-source value.
  - C: keep `null` and document the convention.
- Recommendation: A. It preserves the omission enum as an omission-only field.

### C6 legacy fallback invalidation interaction is unclear

- Proposed label: `should-fix`
- Source findings:
  - `gpt-5.4-primary-004` INFO
  - `claude-opus-4-8-adversarial-005` WARN
- Summary: reviewers asked whether invalidation on nonce security failure can unexpectedly mutate fallback legacy approval records or leave failed records reusable.
- Candidate options:
  - A: add regression tests proving nonce invalidation writes only runtime nonce records and does not mutate frozen legacy records.
  - B: remove legacy fallback for nonce validation paths.
  - C: leave as-is because nonce validation only runs when `nonce` is present.
- Recommendation: A. This is lower priority than C1-C4 but important for deployment compatibility.

### C7 commit_stop_point is under-constrained

- Proposed label: `should-fix`
- Source findings:
  - `claude-opus-4-8-adversarial-007` WARN
- Summary: `commit_stop_point: true` now allows reopen in-progress files through commit, but only the allow path is visible in the test summary.
- Candidate options:
  - A: add negative tests requiring `process_id: reopen-procedure`, staged in-progress file inclusion, and legitimate staged scope; document the field.
  - B: remove the field and use only `next_step` text.
  - C: keep as-is.
- Recommendation: A. The field is useful because it preserves `next_step`, but it should be tightly scoped.

### C8 normal git execution failure conditional retry

- Proposed label: `leave-as-is` for this gate, track as follow-up
- Source findings:
  - `claude-opus-4-8-adversarial-009` INFO
- Summary: conditional retry after normal git execution failure remains incomplete, but reviewers rated it lower priority than consume/binding issues.
- Recommendation: track after C1-C4 unless implementation approval criteria require completing all retry semantics now.

## User-Visible Triage Gate

Implementation triad-review should not be marked complete yet.

Proposed blocking set:

- `must-fix`: C1, C2, C3, C4
- `should-fix`: C5, C6, C7
- `leave-as-is / follow-up`: C8

## Proxy Model Decision

Proxy model decision was requested after the user explicitly approved external API use.

- Proxy model: `gemini-3.1-pro-preview`
- Prompt: `proxy-decision-prompts/C1-C8.prompt.md`
- Raw response: `proxy-decisions/C1-C8.raw.yaml`
- Decisions input: `proxy-decisions/C1-C8.decisions-input.yaml`
- Approval record: `proxy-approval.yaml`
- Important proxy decision files: `decisions/*.yaml` for 12 important findings
- Verification: `tools/make-proxy-approval.py` generated `proxy-approval.yaml` and passed canonical `_approval_errors` validation

Final proxy labels:

- `must-fix`: C1, C2, C3, C4
- `should-fix`: C5, C6, C7
- `leave-as-is / follow-up`: C8

Implementation triad-review should still not be marked complete until the must-fix set is addressed and rechecked. No implementation changes have been made after the review-run.

## Must-Fix Implementation Pass

After the proxy decision, C1-C4 were addressed with TDD.

- C1: `tools/guarded-git-commit.py` now consumes both the approval record and nonce challenge after successful guarded commit. If consumption persistence fails, the wrapper returns failure instead of silently succeeding.
- C2: `commit-approval record` no longer embeds `execution_delegation` by default. Content approval and LLM commit execution delegation remain separate concerns.
- C3: nonce canonical target collection now uses the parsed staged status map, so rename source deletion is included in the exact-index digest. Gitlink mode/object id preservation is covered by regression test.
- C4: malformed challenge `target_files` and malformed `target_digest` are rejected before record creation; `target_files` must also match the current canonical staged entries.

Tests:

- `.venv/bin/python3 -m unittest tests.tools.test_guarded_git_commit.GuardedGitCommitTests.test_guarded_commit_consumes_nonce_challenge_after_success tests.tools.test_check_workflow_action.CommitExitCodeTests.test_commit_approval_record_does_not_embed_execution_delegation_by_default tests.tools.test_check_workflow_action.CommitExitCodeTests.test_commit_approval_record_rejects_malformed_challenge_target_files tests.tools.test_check_workflow_action.CommitExitCodeTests.test_commit_approval_prepare_preserves_staged_gitlink_entry tests.tools.test_check_workflow_action.CommitExitCodeTests.test_commit_approval_prepare_includes_rename_source_deletion -v`: red before implementation, green after implementation.
- `.venv/bin/python3 -m unittest tests.tools.test_check_workflow_action.CommitExitCodeTests tests.tools.test_guarded_git_commit -v`: pass.

## Should-Fix Implementation Pass

C5-C7 were also addressed with TDD.

- C5: when redacted source text is stored, `source_omission_reason` is now omitted instead of emitted as `null`.
- C6: when a nonce approval loaded through legacy fallback fails validation, the frozen legacy record remains unchanged and an invalidated runtime copy is written. The runtime challenge is invalidated as well.
- C7: `commit_stop_point: true` is now constrained to the implementation drafting stop point shape instead of acting as a broad in-progress bypass.

Tests:

- `.venv/bin/python3 -m unittest tests.tools.test_check_workflow_action.CommitExitCodeTests.test_commit_approval_record_source_text_is_redacted tests.tools.test_check_workflow_action.CommitExitCodeTests.test_commit_approval_invalidates_runtime_copy_when_legacy_nonce_fails tests.tools.test_check_workflow_action.CommitExitCodeTests.test_commit_blocks_reopen_commit_stop_point_with_unscoped_reason -v`: red before implementation, green after implementation.
- `.venv/bin/python3 -m unittest tests.tools.test_check_workflow_action.CommitExitCodeTests tests.tools.test_guarded_git_commit tests.tools.test_runtime_placement_freeze.CommitApprovalPlacementTests -v`: pass.

Remaining:

- C8 conditional retry remains follow-up / leave-as-is for this gate.
- A triad-review recheck is still needed before marking the implementation triad-review gate complete.
