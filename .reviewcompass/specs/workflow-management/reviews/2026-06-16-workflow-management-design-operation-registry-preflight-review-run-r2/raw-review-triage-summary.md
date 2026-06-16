# raw review triage summary r2

run_id: 2026-06-16-workflow-management-design-operation-registry-preflight-review-run-r2
variant: implementation_review_independent_3way_codex_operator
phase: design
gate: stages/design.yaml#triad-review

## Role assignments

| role | path | provider | model | parse | findings |
| --- | --- | --- | --- | --- | ---: |
| primary | api | openai-api | gpt-5.4 | parsed | 5 |
| adversarial | api | anthropic-api | claude-opus-4-8 | parsed | 8 |
| judgment | api | gemini-api | gemini-3.1-pro-preview | parsed | 0 |

## Severity summary

- ERROR: 0
- WARN: 8
- INFO: 5

## Same-root clusters and recommended triage

### Cluster A: `next_action` / active state schema is under-typed

Findings:

- `gpt-5.4-primary-001`（WARN）

Recommended label: should-fix.

Plain explanation: The design says `state_refs.next_action` contains active workflow dimensions, but leaves the object itself untyped. Since state uniqueness is central, the design should define required subfields or point to the exact `next_action` schema.

Recommended action: add a small required schema for `state_refs.next_action` or explicitly bind it to Requirement 2 `next --json` output fields.

### Cluster B: verdict semantics need deterministic hard-stop behavior

Findings:

- `gpt-5.4-primary-002`（WARN）
- `claude-opus-4-8-adversarial-001`（WARN）
- `claude-opus-4-8-adversarial-002`（WARN）
- `claude-opus-4-8-adversarial-003`（WARN）

Recommended label: should-fix.

Plain explanation: The design lists `OK / WARN / DEVIATION`, but reviewers want clearer rules: what `allowed_verdicts` means, which conflicts are always hard-stop, and what happens when `feature_impact_decisions`, `spec.json`, and pending gates disagree.

Recommended action: define `allowed_verdicts`, state that `DEVIATION` is a mandatory hard stop, and explicitly classify cross-source inconsistency as `DEVIATION`.

### Cluster C: operation family invariants are too policy-string based

Findings:

- `gpt-5.4-primary-003`（WARN）

Recommended label: should-fix.

Plain explanation: Generic fields like `artifact_policy` are useful, but review artifact and deployment/export families need required checks so registry entries do not drift or omit coverage.

Recommended action: add family-specific required checks for review artifacts and deployment/export operations.

### Cluster D: current-session guard lacks session identity fields

Findings:

- `claude-opus-4-8-adversarial-004`（WARN）

Recommended label: should-fix.

Plain explanation: The design says current-session formal records are rejected, but does not show where the current session id and target session id live in the contract / response.

Recommended action: add evidence-capture fields such as `current_session_id`, `target_session_id`, and `session_record_mode`, and fail closed when they are missing or equal for formal output.

### Cluster E: nested issue handling needs explicit contract / response fields

Findings:

- `claude-opus-4-8-adversarial-005`（WARN）

Recommended label: should-fix.

Plain explanation: Requirement 12 includes nested issue handling, but the design excerpt does not show fields for parent task, issue relation, allowed files, return condition, or nesting depth.

Recommended action: add a compact `nested_issue_state` structure and `DEVIATION` rules for unrecorded scope drift.

### Cluster F: positive / non-blocking observations

Findings:

- `gpt-5.4-primary-004`（INFO）
- `gpt-5.4-primary-005`（INFO）
- `claude-opus-4-8-adversarial-006`（INFO）
- `claude-opus-4-8-adversarial-007`（INFO）
- `claude-opus-4-8-adversarial-008`（INFO）

Recommended label: leave-as-is.

Plain explanation: These are either positive confirmations or minor review-target completeness notes. The Phase 1 / Phase 2 boundary is clear, XDI-WM-004 is directionally correct, and concrete operation ids are acceptable as an initial/extensible seed list.

## Proposed three-level labels

- must-fix: none
- should-fix: `gpt-5.4-primary-001`, `gpt-5.4-primary-002`, `gpt-5.4-primary-003`, `claude-opus-4-8-adversarial-001`, `claude-opus-4-8-adversarial-002`, `claude-opus-4-8-adversarial-003`, `claude-opus-4-8-adversarial-004`, `claude-opus-4-8-adversarial-005`
- leave-as-is: `gpt-5.4-primary-004`, `gpt-5.4-primary-005`, `claude-opus-4-8-adversarial-006`, `claude-opus-4-8-adversarial-007`, `claude-opus-4-8-adversarial-008`

## Stop condition

This is the user-visible triage gate. Do not update design, write approval.yaml, call proxy_model, update spec.json, or advance the reopen gate until the recommended triage is approved by the user or proxy_model.
