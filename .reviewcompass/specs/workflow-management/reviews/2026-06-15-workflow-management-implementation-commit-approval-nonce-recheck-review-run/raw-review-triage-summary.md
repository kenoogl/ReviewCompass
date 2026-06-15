# workflow-management implementation triad-review recheck summary：commit approval nonce fixes

## Review Run

- Run ID: `2026-06-15-workflow-management-implementation-commit-approval-nonce-recheck-review-run`
- Gate: `stages/implementation.yaml#triad-review`
- Variant: `implementation_review_independent_3way_codex_operator`
- Target: `.reviewcompass/specs/workflow-management/reviews/2026-06-15-workflow-management-implementation-commit-approval-nonce-recheck-review-run/review-target.md`
- Scope: C1-C7 fix recheck after proxy_model decision and TDD implementation

## Role Assignments

| role | path | provider | model | raw |
| --- | --- | --- | --- | --- |
| primary | api | openai-api | gpt-5.4 | `raw/gpt-5.4.round-1.txt` |
| adversarial | api | anthropic-api | claude-opus-4-8 | `raw/claude-opus-4-8.round-1.txt` |
| judgment | api | gemini-api | gemini-3.1-pro-preview | `raw/gemini-3.1-pro-preview.round-1.txt` |

## Model Result Summary

| model | parse_status | findings | severity |
| --- | --- | ---: | --- |
| gpt-5.4 | parsed | 0 | - |
| claude-opus-4-8 | parsed | 7 | ERROR:1, WARN:4, INFO:2 |
| gemini-3.1-pro-preview | parsed | 0 | - |

All three raw responses were read by the main session LLM before this summary.

## Same-Root Clusters And Triage Proposal

### R1 consumption is still not fail-closed enough

- Proposed label: `must-fix`
- Source findings:
  - `claude-opus-4-8-adversarial-001` ERROR
  - `claude-opus-4-8-adversarial-002` WARN
  - `claude-opus-4-8-adversarial-007` INFO
- Summary: the current guarded commit consumes the approval record first, then consumes the nonce challenge. If the challenge consume fails after the approval record was already written as consumed, the commit has already landed and the runtime records can become inconsistent. More importantly, a still-unconsumed challenge may be reusable for a fresh approval record.
- Candidate options:
  - A: consume the challenge first, then the approval record. If either write fails after commit success, return failure but ensure the resulting persisted state rejects future reuse.
  - B: add a single authoritative combined nonce state file and stop treating approval/challenge as separately consumable records.
  - C: leave as-is because approval consumed state already blocks the original approval.
- Recommendation: A. It is smaller than B and directly prevents replay through a live challenge.

### R2 rename/copy trailing-entry concern appears to be a false positive

- Proposed label: `leave-as-is`
- Source findings:
  - `claude-opus-4-8-adversarial-003` WARN
- Summary: the finding says `i + 2 < len(parts)` wrongly rejects a trailing R/C entry. In Python, an index `i + 2` is valid exactly when `i + 2 < len(parts)`. The added rename test is also a single trailing rename entry and passed.
- Candidate options:
  - A: leave as-is and document that the recheck finding is based on an off-by-one misunderstanding.
  - B: add an extra copy test for confidence.
  - C: rewrite parsing again despite the current evidence.
- Recommendation: A, with B as optional hardening if desired.

### R3 digest lowercase canonical diagnostic can be stricter

- Proposed label: `should-fix`
- Source findings:
  - `claude-opus-4-8-adversarial-004` WARN
- Summary: uppercase 64-char hex would pass `_require_target_digest` shape validation and then fail as a digest mismatch. This is already fail-closed, but the malformed-vs-mismatch diagnostic is looser than the canonical lowercase digest contract.
- Candidate options:
  - A: require lowercase hex with an explicit regex or character-set check.
  - B: leave as-is because later string equality rejects uppercase.
  - C: normalize uppercase to lowercase.
- Recommendation: A. It is small and better matches no-partial-inference diagnostics. Do not choose C because normalization is inference.

### R4 runtime invalidated-copy early return appears to be a false positive

- Proposed label: `leave-as-is`
- Source findings:
  - `claude-opus-4-8-adversarial-005` WARN
- Summary: the finding says `_write_runtime_invalidated_approval` skips an existing runtime path. However, `invalidate(cwd)` runs immediately before it and marks an existing runtime approval invalidated. In true legacy fallback, runtime approval is absent because the resolver would otherwise choose runtime.
- Candidate options:
  - A: leave as-is and document the reasoning.
  - B: add a regression test proving existing runtime path is invalidated by `invalidate(cwd)`.
  - C: remove the early return and overwrite runtime again.
- Recommendation: A or B. This does not appear to be a blocker.

### R5 commit_stop_point constraint is intentionally narrow

- Proposed label: `leave-as-is`
- Source findings:
  - `claude-opus-4-8-adversarial-006` INFO
- Summary: the implementation now hardcodes the accepted implementation drafting stop-point shape. This is brittle if workflow labels change, but that tightness is the point of the current safety fix: avoid a broad bypass.
- Candidate options:
  - A: leave as-is for this gate.
  - B: replace hardcoded text with a named field such as `commit_stop_point_kind`.
  - C: loosen matching.
- Recommendation: A for this gate. B can be a follow-up design improvement; C would weaken the safety fix.

## User-Visible Triage Gate

Human decision completed at `2026-06-15T12:38:00Z`.

Decision set:

- R1: A / `must-fix`
- R2: A / `leave-as-is`
- R3: A / `should-fix`
- R4: A / `leave-as-is`
- R5: A / `leave-as-is`

Implementation triad-review should not be marked complete until R1 and R3 fixes pass verification.

Proxy_model decision was attempted for R1-R5, but external Gemini disclosure was rejected by the environment policy. Human decision was used instead.
