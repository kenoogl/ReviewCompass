# raw review triage summary r2

run_id: 2026-06-16-workflow-management-requirements-operation-registry-preflight-review-run-r2
variant: implementation_review_independent_3way_codex_operator
phase: requirements
gate: stages/requirements.yaml#triad-review

## Role assignments

| role | path | provider | model | parse | findings |
| --- | --- | --- | --- | --- | ---: |
| primary | api | openai-api | gpt-5.4 | parsed | 5 |
| adversarial | api | anthropic-api | claude-opus-4-8 | parsed | 5 |
| judgment | api | gemini-api | gemini-3.1-pro-preview | parsed | 2 |

## Severity summary

- ERROR: 1
- WARN: 8
- INFO: 3

## Same-root clusters and recommended triage

### Cluster A: `next --json` state uniqueness is still underspecified

Findings:

- `gemini-3.1-pro-preview-judgment-001`（ERROR）
- `claude-opus-4-8-adversarial-001`（WARN）
- `gpt-5.4-primary-002`（WARN）

Recommended label: must-fix.

Plain explanation: Acceptance Criterion 13 was added to ensure `next` uniquely determines the active workflow state, but reviewers found it still needs to be explicit about the full machine-readable field set and the preflight output that verifies it.

Recommended action: strengthen AC13 so it explicitly requires current mainline, required action, phase, stage, reopen scope, impact review scope, direct features, indirect features, flag policy, next pending gate, and consistency checks against `feature_impact_decisions`, `spec.json`, and `pending_gates`.

### Cluster B: Requirement 2 / Requirement 12 ownership boundary for `next`

Findings:

- `claude-opus-4-8-adversarial-002`（WARN）

Recommended label: should-fix.

Plain explanation: Requirement 2 already owns `next --json`; Requirement 12 should not create a competing source of truth. It should state that it extends Requirement 2's `next` output for operation preflight / reopen uniqueness.

Recommended action: clarify that AC13 amends or constrains Requirement 2 rather than duplicating it.

### Cluster C: reopen scope and impact review scope separation is not yet acceptance-level

Findings:

- `claude-opus-4-8-adversarial-003`（WARN）

Recommended label: should-fix.

Plain explanation: The review target and reopen record now separate reopen scope from impact review scope, but Requirement 12 acceptance text should also require that separation so flag false/true behavior is traceable.

Recommended action: expand AC11 or AC13 to require explicit `reopen_scope`, `impact_review_scope`, direct/indirect feature sets, and flag policy.

### Cluster D: review artifacts, bundle, manifest, approval, and drift checks

Findings:

- `gemini-3.1-pro-preview-judgment-002`（WARN）
- `gpt-5.4-primary-004`（WARN）

Recommended label: should-fix.

Plain explanation: AC6 covers many review artifacts but does not explicitly name bundle, review target / manifest alignment, criteria / document-type alignment, overwrite prevention, and drift checks across already-existing artifacts.

Recommended action: expand AC6 to include bundle and cross-artifact consistency / overwrite / drift checks.

### Cluster E: operation registry should link operation to workflow phase / stage / gate

Findings:

- `gpt-5.4-primary-001`（WARN）

Recommended label: should-fix.

Plain explanation: To prevent wrong-stage or wrong-entrypoint execution, each operation contract should know which workflow phase, stage, or gate it belongs to.

Recommended action: expand AC1 to require phase/stage/gate linkage when an operation is workflow-bound.

### Cluster F: approval-chain integrity should not be framed only as worktree conflict

Findings:

- `gpt-5.4-primary-003`（WARN）

Recommended label: should-fix.

Plain explanation: Approval records can be stale or inconsistent even when the worktree is clean.

Recommended action: expand AC7 or AC5 to require approval-chain integrity checks for missing, stale, inconsistent, or already-consumed approval records.

### Cluster G: fail-closed wording for nested issue, serial-only, and current-session cases

Findings:

- `claude-opus-4-8-adversarial-004`（INFO）
- `claude-opus-4-8-adversarial-005`（INFO）

Recommended label: should-fix.

Plain explanation: These are INFO findings, but they point to small wording improvements that make the criteria testable.

Recommended action: tie nested issue scope drift, serial-only violation, and current-session formal record creation to the common `DEVIATION` / fail-closed vocabulary in AC3.

### Cluster H: positive note

Findings:

- `gpt-5.4-primary-005`（INFO）

Recommended label: leave-as-is.

Plain explanation: The review target correctly preserves reopen scoping and superseded approval context. No requirements change is needed.

## Proposed three-level labels

- must-fix: `gemini-3.1-pro-preview-judgment-001`, `claude-opus-4-8-adversarial-001`, `gpt-5.4-primary-002`
- should-fix: `gpt-5.4-primary-001`, `gpt-5.4-primary-003`, `gpt-5.4-primary-004`, `claude-opus-4-8-adversarial-002`, `claude-opus-4-8-adversarial-003`, `claude-opus-4-8-adversarial-004`, `claude-opus-4-8-adversarial-005`, `gemini-3.1-pro-preview-judgment-002`
- leave-as-is: `gpt-5.4-primary-005`

## Stop condition

This is the user-visible triage gate. Do not update requirements, write approval.yaml, call proxy_model, update spec.json, or advance the reopen gate until the recommended triage is approved by the user or proxy_model.
