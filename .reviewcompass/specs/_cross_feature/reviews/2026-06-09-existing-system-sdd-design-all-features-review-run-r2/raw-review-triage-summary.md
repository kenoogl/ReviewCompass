# Design triad-review user-visible triage summary

Run: `2026-06-09-existing-system-sdd-design-all-features-review-run-r2`

Phase: `design.triad-review`

## Role assignments

| Role | Provider | Model |
|---|---|---|
| primary | anthropic-api | claude-sonnet-4-6 |
| adversarial | openai-api | gpt-5.4 |
| judgment | gemini-api | gemini-3.1-pro-preview |

## Raw result summary

| Model | Findings | Severity |
|---|---:|---|
| claude-sonnet-4-6 | 7 | INFO: 7 |
| gpt-5.4 | 1 | ERROR: 1 |
| gemini-3.1-pro-preview | 4 | ERROR: 1, WARN: 1, INFO: 2 |

## Same-root clusters and proposed triage

### Cluster 1: CE/WM direct design coverage is sufficient

Sources:

- Claude INFO 1-5, 7
- Gemini INFO 3-4

Plain explanation:

CE design now says how to extract code-derived candidates from an existing system after post-hoc intent. WM design now says how to receive those candidates and reopen downstream phases. The tasks boundary is also clear: CE may point to downstream impact, but does not rewrite tasks.md.

Proposed decision: `leave-as-is`

Reason:

The direct features now cover Requirement 10 and Requirement 9 at design level. No direct CE/WM must-fix remains in these findings.

### Cluster 2: Review-target output contract inconsistency

Source:

- GPT ERROR 1

Plain explanation:

GPT says the review target requires `verifying_commands`, while another output contract permits only four fields. The actual target says findings should include fields "at least" including `verifying_commands`, and Claude successfully returned `verifying_commands` without parse failure.

Proposed decision: `leave-as-is`

Reason:

This is about the review-target artifact wording, not about CE/WM design correctness. The review run parsed successfully. It does not block design triad-review completion.

### Cluster 3: Foundation ownership of shared schema/vocabulary

Sources:

- Gemini ERROR 1
- Gemini WARN 2
- Claude INFO 6 disagrees

Plain explanation:

Gemini argues that CE candidate classifications and WM reopen state fields are shared contracts, so foundation design.md must be reopened too. Claude argues the new structures are feature-local: CE owns candidate extraction schema, WM owns reopen state fields, and no foundation design change is needed now.

Proposed decision: `leave-as-is for this design gate`, with a watch item for later review-wave.

Reason:

Foundation owns common review evidence schemas, review metadata, and selected shared vocabularies. The new CE/WM fields are currently feature-local contracts between CE and WM, not general review evidence schema or foundation-owned metadata. Moving them to foundation now would broaden the feature impact beyond the approved requirements-stage boundary. However, design review-wave should explicitly re-check whether any of these fields are becoming reusable common schema.

### Cluster 4: Indirect features

Sources:

- Claude INFO 6
- Gemini ERROR 1 as dissent

Plain explanation:

The indirect features remain in scope, but the direct design edits do not currently force their design.md bodies to change.

Proposed decision: `leave-as-is`

Reason:

No model identified concrete runtime, evaluation, analysis, or self-improvement design text that must change now. Foundation is the only disputed indirect feature, covered in Cluster 3.

## Recommended gate decision

Approve design triad-review as complete with no immediate design edits.

## Human decision

Decision: approved

Decision source: 2026-06-09 user message `承認`

Applied triage:

- All findings are treated as `leave-as-is` for the design triad-review gate.
- The foundation ownership concern remains as a design review-wave watch item, not as a blocker for this gate.

Next workflow step after approval:

1. Record `stages/design.yaml#triad-review` as completed.
2. Add a `downstream_impact_decisions` record for design triad-review.
3. Proceed to `stages/design.yaml#review-wave`.

Suggested watch item for design review-wave:

- Re-check whether CE candidate schema or WM reopen state fields should remain feature-local or become foundation-owned reusable schema.
