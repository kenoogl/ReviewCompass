# Proxy approval request: workflow-management design approval

You are acting as `proxy_model` for a ReviewCompass workflow approval gate.

## Gate

- Gate: `stages/design.yaml#approval`
- Feature: `workflow-management`
- Reopen: `R-0`
- Topic: `commit-approval-nonce`
- Date: `2026-06-15`

## Question

Decide whether the workflow may approve `stages/design.yaml#approval` for the commit approval nonce reopen chain.

Return YAML only:

```yaml
decision: approve | reject
final_label: approved | rejected
rationale: "<short reason>"
conditions: []
```

## Evidence summary

### Requirements basis

Requirement 4 acceptance criteria 6 and 7 were added for commit approval nonce handling.

- Acceptance 6 requires commit approval to be recorded via nonce challenge bound to staged file set and staged content.
- Acceptance 6 requires commit approval record creation and the commit gate to check nonce match, unexpired challenge, unconsumed state, staged file set/content match, and target digest match.
- Acceptance 6 requires missing, malformed, expired, mismatched, or consumed approval state to fail closed.
- Acceptance 7 requires nonce judgment to be independent of the controlling LLM, provider, or model.
- Acceptance 7 limits the guarantee to staged-content binding, not cryptographic proof that the user spoke in the UI.

Requirements alignment result:

- `decision: existing_sufficient`
- Requirement 4 acceptance 6-7 is inside the existing irreversible-operation pre-gate responsibility.
- Downstream design/tasks/implementation recheck remains required.

### Design changes

Design now defines commit approval nonce challenge under the irreversible-operation pre-gate model.

Key design points:

- Challenge path: `.reviewcompass/runtime/approvals/commit-approval-challenge.json`
- Approval record path: `.reviewcompass/runtime/approvals/commit-approval.json`
- `commit-approval prepare --json` creates challenge only when staged files exist.
- Existing unconsumed challenge blocks prepare; abandoned challenge replacement requires explicit `commit-approval invalidate --json`.
- Challenge stores staged paths, per-file target sha, whole target digest, nonce, UTC ISO-8601 `created_at`/`expires_at`, TTL 10 minutes, consumed state.
- Canonical digest format is versioned as `commit-approval-v1`, with sorted repo-relative POSIX paths, git index mode, staged object id, and per-file target sha.
- Malformed challenge or approval record fails closed, with no partial inference.
- Approval text is supplied by stdin or omitted via no-store mode; no source text is accepted through argv.
- Stored approval source text is redacted with `tools.session_record_extractor.redact.redact_text` and checked with `find_residual_secrets`.
- Redaction targets secret-like values only; ordinary text is not treated as secret by default.
- Safe omission reasons are restricted to `source_not_provided`, `unsafe_source_omitted`, `redaction_failed`, `residual_secret_detected`.
- Schema rejects LLM/provider/model fields: `llm`, `provider`, `model`, `model_id`, `proxy_model_id`.
- Approval record includes `attestation_type=staged_content_nonce_binding` and `guarantee_scope=staged_content_binding_not_ui_utterance_proof`.
- Commit path validates the exact index before commit.
- Security validation failure invalidates challenge/approval; ordinary git execution failure may retry only while index and approval state remain valid.
- Commit success consumes challenge/approval; consume persistence failure makes later gates reject the approval/challenge.

### Design triad-review

The design triad-review found C1-C8.

- C1-C4 were approved by the user and applied.
- C5-C8 were decided by proxy_model and applied.
- The triage no longer has human-required or undecided findings for this design review run.

### Review-wave

`review-wave-summary` was re-run after fixing an unrelated existing YAML quoting defect.

- Result: `status: ok`
- Evidence: `.reviewcompass/specs/_cross_feature/reviews/2026-06-15-design-commit-approval-nonce-review-wave.md`

### Design alignment

Design alignment result:

- `decision: existing_sufficient`
- The design addition is consistent with Requirement 4 acceptance 6-7 and existing design sections.
- No further design edit is required.
- tasks and implementation recheck remain required.

## Approval criterion

Approve only if the design phase has completed drafting, triad-review, review-wave, and alignment, and no unresolved design-level blocker remains.

Reject if approval would hide an unresolved design-level contradiction, missing required gate, or unresolved must-fix/should-fix design finding.
