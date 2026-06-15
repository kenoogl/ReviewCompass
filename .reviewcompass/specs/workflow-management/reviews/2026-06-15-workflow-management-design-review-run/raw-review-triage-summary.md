# raw review triage summary: commit approval nonce design

run_id: 2026-06-15-workflow-management-design-review-run
variant: implementation_review_independent_3way
status: user_visible_triage_gate

## Role Assignments

| role | provider | model | raw |
|---|---|---|---|
| primary | anthropic-api | claude-sonnet-4-6 | raw/claude-sonnet-4-6.round-1.txt |
| adversarial | openai-api | gpt-5.5 | raw/gpt-5.5.round-1.txt |
| judgment | gemini-api | gemini-3.1-pro-preview | raw/gemini-3.1-pro-preview.round-1.txt |

## Model Result Summary

| model | parse | findings | severity |
|---|---|---:|---|
| claude-sonnet-4-6 | parsed | 8 | ERROR:1, WARN:3, INFO:4 |
| gpt-5.5 | parsed | 5 | ERROR:1, WARN:4 |
| gemini-3.1-pro-preview | parsed | 2 | ERROR:1, WARN:1 |

## Same-Root Clusters And Triage Draft

| cluster | source findings | draft label | plain summary |
|---|---|---|---|
| C1 source text input channel | gemini-001, gpt-005, claude-004 | must-fix | `--source-text <user text>` passes raw user text through argv before redaction, so secrets can leak to process listings, shell history, or audit logs. |
| C2 expiry and clock contract | claude-008 | must-fix | Expiry is required but duration, timestamp format, clock source, and clock rollback handling are not defined. |
| C3 malformed runtime state | gpt-001 | must-fix | Invalid JSON, missing fields, wrong types, duplicate paths, and malformed approval records are not explicitly fail-closed at both record and commit gate. |
| C4 canonical target digest | claude-003, gpt-002 | should-fix | Path normalization, sort order, serialization bytes, digest version, and file-mode/submodule handling are underspecified. |
| C5 validation/commit race and consumption | claude-002, gpt-003, gpt-004, gemini-002 | should-fix | The design must distinguish security validation failure from git execution failure, and define what happens if index changes or consumption persistence fails around commit. |
| C6 redaction reference and omission schema | claude-004 | should-fix | The design cites an existing sensitive-information policy without a precise reference, and does not define `source_omission_reason` values. |
| C7 singleton challenge concurrency | claude-005 | should-fix | Fixed singleton challenge files can be overwritten by interleaved sessions unless `prepare` fails on an existing unconsumed challenge. |
| C8 schema guardrails and audit semantics | claude-001, claude-006, claude-007 | should-fix | Source text length/encoding, explicit exclusion of LLM/provider/model fields, and machine-readable guarantee scope are not yet pinned. |

## User Decisions

| cluster | decision_at | decision | applied files |
|---|---|---|---|
| C1 source text input channel | 2026-06-15T18:11:55+09:00 | User approved the recommended direction: remove argv source-text input, use stdin for source text when stored, and allow a no-store mode that records only an omission reason. | `.reviewcompass/specs/workflow-management/design.md` |
| C2 expiry and clock contract | 2026-06-15T18:13:54+09:00 | User approved the recommended direction: store `created_at` and `expires_at` as UTC ISO-8601 timestamps, use a fixed 10 minute TTL, inject `now_utc` for tests, and fail closed on clock rollback or expiry. | `.reviewcompass/specs/workflow-management/design.md` |
| C3 malformed runtime state | 2026-06-15T18:15:43+09:00 | User approved option A: define required fields and fail closed for invalid JSON, missing fields, wrong types, duplicate paths, invalid repo-relative paths, digest format mismatch, and malformed approval records. | `.reviewcompass/specs/workflow-management/design.md` |
| C4 canonical target digest | 2026-06-15T18:17:47+09:00 | User approved option A: define a versioned canonical digest format with sorted repo-relative POSIX paths, git index mode, staged object id, per-file target sha, and fixed JSON-line serialization. | `.reviewcompass/specs/workflow-management/design.md` |

## Proxy Decisions

Proxy model: `gpt-5.5`

Decision prompt: `proxy-decision-prompts/C5-C8.prompt.md`

Raw response: `proxy-decisions/C5-C8.raw.yaml`

Approval record: `proxy-approval.yaml`

| cluster | final label | selected option | applied files |
|---|---|---|---|
| C5 validation/commit race and consumption | must-fix | A | `.reviewcompass/specs/workflow-management/design.md` |
| C6 redaction reference and omission schema | must-fix | A | `.reviewcompass/specs/workflow-management/design.md` |
| C7 singleton challenge concurrency | must-fix | A | `.reviewcompass/specs/workflow-management/design.md` |
| C8 schema guardrails and audit semantics | should-fix | A | `.reviewcompass/specs/workflow-management/design.md` |

## Must-Fix Candidate Details

### C1 source text input channel

Problem: the proposed `commit-approval record --source-text <user text>` command can leak raw text before application redaction.

Candidate options:

- A: Remove source text capture entirely and store only `source_omission_reason: no_source_text_stored`.
- B: Replace argv input with stdin, for example `commit-approval record --nonce <nonce> --source-text-stdin --json`, then redact before persistence.
- C: Accept a protected temporary file path and read source text from that file.

Recommended draft: B. It preserves auditability while keeping raw text out of argv. It should also allow A as an explicit no-store mode for high-risk sessions.

Downstream impact: tasks and tests must cover argv rejection, stdin redaction, omitted-source records, and no raw secret persistence.

Applied resolution: `commit-approval record --nonce <nonce> --source-text-stdin --json` reads approval text from stdin. `--no-source-text` records `source_omission_reason=source_not_provided`. The design explicitly forbids `--source-text <user text>` style argv input, stores only `source_text_redacted` when safe, and records `source_omission_reason=unsafe_source_omitted` when safe redaction is not possible.

### C2 expiry and clock contract

Problem: expiry checks cannot be tested or enforced deterministically without a fixed contract.

Candidate options:

- A: Store `created_at` and `expires_at` as UTC ISO-8601 timestamps, use a fixed short TTL, and allow the checker clock to be injected in tests.
- B: Use a monotonic clock only. This is unsuitable for persisted challenge files across processes.
- C: Remove expiry. This contradicts the approved requirement.

Recommended draft: A. Also reject records when `now_utc < created_at` or `now_utc > expires_at`, so obvious system-clock rollback fails closed.

Downstream impact: implementation tests need normal, expired, malformed timestamp, and clock-rollback cases.

Applied resolution: challenge records hold UTC ISO-8601 `created_at` and `expires_at`; TTL is fixed at 10 minutes. Tests can inject checker `now_utc`. The gate fails closed when `now_utc < created_at`, `now_utc > expires_at`, timestamps are missing or unparsable, `expires_at <= created_at`, or the stored TTL is not 10 minutes.

### C3 malformed runtime state

Problem: malformed challenge/approval files can otherwise be interpreted inconsistently.

Candidate options:

- A: Define required fields and fail closed for invalid JSON, missing field, wrong type, duplicate path, non repo-relative path, digest format mismatch, and malformed approval record.
- B: Accept partial records and infer missing fields where possible.
- C: Ignore malformed fields that are not directly used by the current check.

Recommended draft: A. It matches the fail-closed requirement and gives TDD a clear contract.

Downstream impact: tasks must include schema validation tests for both record creation and commit gate.

Applied resolution: challenge and approval records are never repaired or partially inferred. Invalid JSON, non-object values, missing required fields, wrong field types, duplicate file paths, invalid repo-relative POSIX paths, repo-outside paths, empty paths, malformed `target_sha256`, unknown path entries, and challenge/approval file-set mismatch all fail closed at both record creation and commit gate.

## Should-Fix Draft Direction

- C4: Define a canonical digest serialization such as `commit-approval-v1\n` plus sorted repo-relative POSIX path entries and staged object identifiers from the index. The exact byte format must be fixed before tests are written.
- C5: Validate immediately in the commit path against the exact index being committed. Security validation failure should invalidate the challenge; ordinary git execution failure may require a new approval unless the design explicitly permits retry under unchanged index and unexpired challenge.
- C6: Cite the concrete redaction policy/helper and define a closed set of omission reasons, for example `redacted`, `unsafe_source_omitted`, `source_not_provided`.
- C7: `prepare` should fail closed when an unconsumed challenge already exists unless the caller explicitly invalidates it through a separate command.
- C8: Add source text length/UTF-8 constraints, forbid LLM/provider/model fields from validation schemas, and add a fixed `attestation_type` or `guarantee_scope` value to prevent overclaiming cryptographic proof.

C4 applied resolution: target digest uses canonical format `commit-approval-v1`. Digest input starts with `commit-approval-v1\n`; entries are sorted by repo-relative POSIX path UTF-8 byte order; each entry is a fixed-key JSON object containing `mode`, `object_id`, `path`, and `target_sha256`; deleted staged entries use `DELETED`; and the whole byte sequence is hashed with SHA-256 hex.

C5 applied resolution: commit validation runs inside the commit execution path against the exact index being committed. Security validation failure invalidates challenge/approval. Ordinary git execution failure may retry only when the index is unchanged and the approval state remains unexpired, unconsumed, and non-invalidated. If consume persistence fails after successful commit, later gates reject the approval/challenge until fresh approval is made.

C6 applied resolution: redaction references `tools.session_record_extractor.redact.redact_text` and `find_residual_secrets` with builtin rules. `source_omission_reason` is closed to `source_not_provided`, `unsafe_source_omitted`, `redaction_failed`, and `residual_secret_detected`.

C7 applied resolution: singleton challenge files remain, but `prepare` fails closed when an unconsumed challenge exists. Replacing an abandoned challenge requires explicit `commit-approval invalidate --json` before a new `prepare`.

C8 applied resolution: approval source text must be UTF-8 and at most 4096 bytes after decoding. Challenge/approval schemas reject LLM/provider/model fields. Approval records include `attestation_type=staged_content_nonce_binding` and `guarantee_scope=staged_content_binding_not_ui_utterance_proof`.

## Gate Status

This summary records the user-visible gate, user decisions for C1-C4, and proxy_model decisions for C5-C8. It does not approve commit, push, spec.json update, or phase movement.
