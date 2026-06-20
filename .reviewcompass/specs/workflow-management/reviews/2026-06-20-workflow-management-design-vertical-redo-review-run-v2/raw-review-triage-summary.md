# Raw Review Triage Summary

review_run_id: `2026-06-20-workflow-management-design-vertical-redo-review-run-v2`
variant: `implementation_review_independent_3way_codex_operator`
phase: design
gate: `stages/design.yaml#triad-review`
triage_status: user_visible_gate_ready
prompt_quality_gate: `.reviewcompass/specs/workflow-management/reviews/2026-06-20-workflow-management-design-vertical-redo-prompt-quality-run/prompt-quality-summary.md`
approval_source: pending

## Role Assignments

| role | path | provider | model | raw | parse |
|---|---|---|---|---|---|
| primary | api | openai-api | gpt-5.4 | `raw/gpt-5.4.round-1.txt` | parsed |
| adversarial | api | anthropic-api | claude-sonnet-4-6 | `raw/claude-sonnet-4-6.round-1.txt` | parsed |
| judgment | api | gemini-api | gemini-3.1-pro-preview | `raw/gemini-3.1-pro-preview.round-1.txt` | parsed |

## Model Result Summary

| model | parse_status | findings | severity |
|---|---|---:|---|
| gpt-5.4 | parsed | 6 | ERROR:5, WARN:1 |
| claude-sonnet-4-6 | parsed | 9 | ERROR:5, WARN:3, INFO:1 |
| gemini-3.1-pro-preview | parsed | 0 | - |

Target manifest:

- `.reviewcompass/specs/workflow-management/design.md`

This v2 run corrects the earlier prompt-target problem. The actual review target is `design.md`, and the prompt criteria were approved by the prompt-quality side-track.

## Same-Root Finding Clusters

### C1: operation contract / registry / preflight authority boundary is not settled

Proposed label: `must-fix candidate`

Findings:

- `2026-06-20-workflow-management-design-vertical-redo-review-run-v2-gpt-5.4-primary-001`
- `2026-06-20-workflow-management-design-vertical-redo-review-run-v2-gpt-5.4-primary-002`
- related: `2026-06-20-workflow-management-design-vertical-redo-review-run-v2-claude-sonnet-4-6-adversarial-008`

Plain explanation:

The models found that design still has conflicting or weak authority boundaries between operation contracts, registry, preflight, operations docs, and implementation. GPT says the design points to both `stages/operation-registry.yaml` and `stages/operation-contracts.yaml` as contract authority in different places. It also says vocabulary / output contracts appear to be owned by docs and code rather than the machine-readable contract/registry model. Claude adds that the registry schema boundary is not explicit enough: it says duplication is invalid, but does not clearly say whether registry fields are structurally forbidden or merely rejected later by checks.

Why it matters:

Requirement 13 exists specifically to prevent tasks from inventing this source-of-truth split. If design leaves the boundary ambiguous, downstream tasks will recreate the same problem.

### C2: 19 required_action mapping and compound operation details are incomplete

Proposed label: `must-fix candidate`

Findings:

- `2026-06-20-workflow-management-design-vertical-redo-review-run-v2-claude-sonnet-4-6-adversarial-001`
- `2026-06-20-workflow-management-design-vertical-redo-review-run-v2-claude-sonnet-4-6-adversarial-002`

Plain explanation:

Claude says design does not individually map all 19 `required_action` values to operation contract fields. It also says `run_maintenance` and `run_workflow_stage` are called compound operations, but the design does not give their concrete branch conditions, internal steps, max effect, or approval aggregation rules.

Why it matters:

Requirement 13 forbids representative values for branchy actions. If the detailed mapping is not a design decision, tasks must invent it.

### C3: approval record binding and proxy / human boundary remain under-specified or contradictory

Proposed label: `must-fix candidate`

Findings:

- `2026-06-20-workflow-management-design-vertical-redo-review-run-v2-gpt-5.4-primary-003`
- `2026-06-20-workflow-management-design-vertical-redo-review-run-v2-gpt-5.4-primary-004`
- `2026-06-20-workflow-management-design-vertical-redo-review-run-v2-claude-sonnet-4-6-adversarial-003`
- `2026-06-20-workflow-management-design-vertical-redo-review-run-v2-claude-sonnet-4-6-adversarial-004`
- related: `2026-06-20-workflow-management-design-vertical-redo-review-run-v2-claude-sonnet-4-6-adversarial-009`

Plain explanation:

GPT says approval records allow both artifact digest and staged file-set digest to be nullable without an operation-type rule that requires one. GPT also says an older approval-stage example still permits `proxy_model` approval, while Requirement 14 says phase approval is human-only. Claude says the design states the human-only set, but does not define a machine-checkable rule for assigning `decision_scope` per operation or required_action. Claude also says the proxy triage predicate is prose, not connected strongly enough to operation contract preconditions.

Why it matters:

This is the exact human/proxy boundary problem that caused the tasks-level reopen to become an upstream design redo.

### C4: active reopen scope has no clear authoritative state structure

Proposed label: `must-fix candidate`

Findings:

- `2026-06-20-workflow-management-design-vertical-redo-review-run-v2-claude-sonnet-4-6-adversarial-005`

Plain explanation:

Claude says design correctly says `spec.json.reopened` is historical and not active scope, but does not define where active reopen scope actually lives, how `next --json` reads it, or how it is initialized and cleared.

Why it matters:

Requirement 16 requires active reopen scope and historical reopened flags to be distinct. Without an authoritative active-scope structure, tasks or implementation must choose one.

### C5: Phase 0 completion criteria and D-003 traceability are not fully design-level

Proposed label: `must-fix candidate`

Findings:

- `2026-06-20-workflow-management-design-vertical-redo-review-run-v2-gpt-5.4-primary-005`
- related: `2026-06-20-workflow-management-design-vertical-redo-review-run-v2-claude-sonnet-4-6-adversarial-007`

Plain explanation:

GPT says Phase 0 omits mechanical workflow-state repair detection. Claude says the design references the six D-003 failure tests but does not enumerate them in the design, leaving weak traceability to a working note.

Why it matters:

Requirement 16 requires Phase 0 completion to be a clear design-level gate, not something tasks later reconstruct from unstable references.

### C6: structured prompt length-bound check lacks an implementable source of truth

Proposed label: `should-fix candidate`

Findings:

- `2026-06-20-workflow-management-design-vertical-redo-review-run-v2-claude-sonnet-4-6-adversarial-006`

Plain explanation:

Claude says the design requires prompt length to be within decision-point-specific bounds, but does not say where those bounds are stored, who sets them, or what failure verdict applies.

Why it matters:

This is likely implementable later, but leaving it unspecified will force task-level policy invention.

### C7: design overclaims or blurs current drafting status versus implemented status

Proposed label: `should-fix candidate`

Findings:

- `2026-06-20-workflow-management-design-vertical-redo-review-run-v2-gpt-5.4-primary-006`

Plain explanation:

GPT says some sections describe implementation-first contracts as already established or design追認, while other sections correctly say Requirement 13〜16 work remains future tasks / implementation. This can blur design drafting status with implementation completion.

Why it matters:

The review gate must not imply review-wave, alignment, approval, implementation, commit, or push completion.

## Proposed Three-Level Triage

| cluster | proposed triage | reason |
|---|---|---|
| C1 | must-fix | Contract / registry / preflight authority is central to Requirement 13 and affects downstream task authority. |
| C2 | must-fix | Required_action mapping and compound operation details are core design obligations, not task guesses. |
| C3 | must-fix | Human/proxy boundary and approval binding are safety boundaries and were a root cause of this reopen. |
| C4 | must-fix | Active reopen scope needs an authoritative state structure for Requirement 16. |
| C5 | must-fix | Phase 0 completion criteria must include repair detection / stable D-003 traceability at design level. |
| C6 | should-fix | Prompt length-bound source of truth should be specified to avoid later manual judgment. |
| C7 | should-fix | Current design status wording should avoid overclaiming implementation or approval completion. |

## Stop Point

This user-visible triage gate is ready for user review. Do not ask proxy_model, edit `design.md`, update `spec.json`, move the reopen gate, commit, or push until the user decides how to handle these clusters.
