# workflow-management requirements triad-review user-visible summary

## Variant And Role Assignment

- variant: `implementation_review_independent_3way_codex_operator`
- primary: `openai-api` / `gpt-5.4`
- adversarial: `anthropic-api` / `claude-sonnet-4-6`
- judgment: `gemini-api` / `gemini-3.1-pro-preview`

## Raw Result Summary

- `gpt-5.4`: parsed, 1 finding, WARN 1
- `claude-sonnet-4-6`: parsed, 4 findings, WARN 3 / INFO 1
- `gemini-3.1-pro-preview`: parsed, findings 0

## Same-Root Clusters

- C1 fail-closed detection layering: primary 001 and adversarial 002 both point out that `next --json` and `reopen-finalize` should be normal early detectors, while commit preflight should remain the final guard rather than the first expected detector.
- C2 superseding reopen full-gate chain: adversarial 001 says a superseding reopen record must also satisfy the full edited-phase gate chain, not merely record a replacement rationale.
- C3 downstream no-change decision evidence: adversarial 003 says even no-change downstream decisions must explicitly carry gate, feature scope, decision, rationale, and evidence.
- C4 feature-scope traceability: adversarial 004 says Requirement 5 could cross-reference Requirement 16's consumer/derivative feature-scope distinction. This is INFO.

## Three-Level Triage Proposal

- must-fix: C1, C2, C3
- should-fix: C4
- leave-as-is: none proposed

## Must-Fix Candidates

- C1: Clarify in requirements that `next --json` detects missing gates or decisions before normal completion, `reopen-finalize` recomputes before completed record creation, and commit preflight is only the final guard.
- C2: Clarify that a superseding reopen record covering edited phases must still run triad-review, review-wave, alignment, and approval for those edited phases.
- C3: Clarify that downstream no-change decisions also require gate, feature scope, decision, rationale, and evidence.

## Stop Point

Before proxy_model, requirements edits, `spec.json` updates, phase movement, or gate completion, present this summary to the user and stop.
