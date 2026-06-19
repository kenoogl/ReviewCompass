# proxy_model Triage Decision Prompt

You are the proxy_model for a ReviewCompass requirements triad-review.

Decide the final triage label for each finding below. The review target is only:

- `.reviewcompass/specs/workflow-management/requirements.md`
- Requirement 13 through Requirement 16
- upstream intent transfer into requirements, not design/tasks correctness

Use the upstream-intent criterion:

- `must-fix`: the finding identifies an omission, weakening, unsupported addition, or responsibility-boundary drift that must be corrected before the requirements triad-review can complete.
- `should-fix`: the finding identifies ambiguity or traceability weakness that should be corrected, but the requirement can still proceed if the fix is tracked.
- `leave-as-is`: the finding is not supported by the requirements text or upstream-intent scope, is already covered, or asks for design-level detail that should not be forced into requirements.

Return only YAML with this shape:

```yaml
proxy_model_id: gpt-5.5
decision_prompt_path: proxy-decision-prompt.md
raw_response_path: proxy-decision-raw.yaml
decisions:
  - finding_id: <exact finding id>
    final_label: must-fix | should-fix | leave-as-is
    rationale: <short but specific reason>
    rejected_options:
      must-fix: <why rejected, if final_label is not must-fix>
      should-fix: <why rejected, if final_label is not should-fix>
      leave-as-is: <why rejected, if final_label is not leave-as-is>
```

For every finding whose original severity is ERROR, or whose final label is `must-fix`, include `rejected_options` for the unselected important alternatives so that the approval record can be audited.

## Requirement Excerpts

### Requirement 13

AC3 says the 19-vocabulary table must cover all 19 `required_action` terms and not blur conditional actions with representative values.

AC4 says the table must machine-readably hold, at minimum, `required_action`, `effect_kind`, `approval_required`, `phase_boundary`, `sequence`, executor, branch-condition existence, and referenced preconditions / postconditions for each `required_action`.

AC5 says approval-gated simple operations include at minimum `commit_stop_point`, `apply_approved_reopen_plan`, `run_reopen_start`, `advance_reopen_after_commit_stop_point`, `advance_reopen_after_approval_stop_point`, `finalize_reopen`, and `repair_workflow_state`; these are treated as `approval_required: true` and require explicit human decision records before execution. It also says this list does not deny complex-operation branch conditions, `run_maintenance` follows maintenance YAML or internal-operation approvals, and `run_workflow_stage` follows stage kind.

AC6 says `record_human_decision` is not an approval target, but a decision-recording operation; its completion alone must not satisfy approval for an `approval_required: true` operation.

AC7 says `run_reopen_pending_gate` branches by active gate kind: `triad-review` and `review-wave` are `external_call`, `alignment` is `write`, `approval` is `state_mutation`, and drafting is separated as `run_reopen_drafting`.

AC8 says `run_maintenance` and `run_workflow_stage` are complex operations whose `effect_kind` and `approval_required` vary by internal operation or stage kind. Until design finalizes representation, a complex operation has branch conditions, internal steps, each step's `effect_kind`, maximum side effect, and approval aggregation rule.

AC11 says operation contract and operation registry / preflight have a single machine-readable source-of-truth boundary; registry / preflight refer to or read from that source and do not execute, update, or consume approvals.

AC12 says missing, stale, digest/version drift, or duplicate source fields between operation contract and registry / preflight must be mechanically detected and fail closed.

### Requirement 14

AC5 says `staged_file_set` / digest are captured and checked at push, before pop, and before commit / push. Out-of-scope staged changes, unexpected digest changes, unapproved parent-child staged-file overlap, and pop digest/set mismatches are WARN or higher in Phase 3 and `DEVIATION` or `repair_workflow_state` in Phase 5.

AC7 says side-track max depth defaults to 2; exceeding depth warns in Phase 3 and blocks in Phase 5. Depth excess or scope drift becomes `repair_workflow_state` or an equivalent stopped state.

AC8 says workflow-state snapshot is emitted as `.reviewcompass/runtime/workflow-state-snapshot.yaml`, as a byproduct of `next --json`, and does not replace the `next --json` output contract.

AC10 says stale, manually updated, or uncorrelatable snapshots are not trusted. Canonical state is always `next --json` and state refs; the snapshot is visualization/audit support.

AC11 says proxy_model can substitute for some decisions but cannot replace human-only decisions such as commit, push, spec.json update, phase approval, reopen finalize, or approval-required irreversible operations.

AC12 says side-track stack, approval gate record, and workflow-state snapshot must distinguish storage, read-only operations, and mutating operations; push/pop/consume/invalidate/save and current/snapshot/inspect must not be blurred.

### Requirement 15

AC3 says mechanical tasks are not embedded in effective prompts as procedure; operation contract, preflight, runner, and guard own them. Effective prompts represent checked preconditions and the LLM language task.

AC5 says first-layer machine checks cover file/anchor existence, required structural sections, length bounds, unregistered action kinds, target manifest consistency, output/postcondition correspondence, machine-checked preconditions only, and on-completion consistency. Commit-mixing checks against side-track stack or operation preflight staged-file sets are Requirement 12 / 14 responsibility and are referenceable from effective-prompt audit.

AC6 says Phase 6 LLM judge audit is auxiliary structured gap analysis and does not automate semantic final approval.

AC7 says LLM judge output must be schema-conforming structured output; Phase 6 is optional and after Phase 5 mechanical enforcement.

### Requirement 16

AC5-9 define Phase 2 through Phase 6 order: read-only registry, warning-only preflight, structured prompts, mechanical blocking, then LLM judge semantic audit.

AC10 says each Phase is committed only after `next --json` can return to normal work or an explicit stopped state; phase-spanning intermediate states must not be mixed into one commit.

AC11 says this reopen scope is requirements -> design -> tasks -> implementation replay; historical `spec.json.reopened` must not be equated with current active scope.

AC13 says proxy_model triage applicability depends on evidence completeness, finding/cluster coverage, approval gate record, operation contract `approval_required`, review-wave impact evidence, and human-only boundaries; any human-required evidence or missing/conflicting source blocks proxy-only passage.

AC14 says human-required predicates and conflict resolution are design-finalized; human-only boundary, unresolved approval gate, `approval_required: true` operation, and unresolved review-wave impact evidence outrank proxy_model applicability.

## Findings To Decide

### F1

- finding_id: `2026-06-19-workflow-management-requirements-vertical-redo-review-run-gpt-5.4-primary-001`
- original severity: ERROR
- location: Requirement 13 AC5
- summary: AC5 allegedly introduces unsupported addition by requiring approval for `repair_workflow_state` as a simple operation with `approval_required: true`.
- rationale: Upstream treats workflow-state repair as a fail-closed machine-detected stop/repair path, not necessarily human-approved for every repair action.

### F2

- finding_id: `2026-06-19-workflow-management-requirements-vertical-redo-review-run-gpt-5.4-primary-002`
- original severity: ERROR
- location: Requirement 14 AC8-10
- summary: Snapshot requirements allegedly omit an explicit read-only boundary and could drift into mutating state-management.
- rationale: Snapshot is byproduct/support, but text does not explicitly forbid snapshot generation/update from mutating workflow state.

### F3

- finding_id: `2026-06-19-workflow-management-requirements-vertical-redo-review-run-gpt-5.4-primary-003`
- original severity: WARN
- location: Requirement 15 AC6-7
- summary: LLM judge is auxiliary, but output is not explicitly forbidden from approving, clearing, or overriding machine gates, human-only decisions, or operation-contract postconditions.

### F4

- finding_id: `2026-06-19-workflow-management-requirements-vertical-redo-review-run-gpt-5.4-primary-004`
- original severity: WARN
- location: Requirement 16 AC5-9
- summary: Phase sequencing is mostly preserved, but dormant or partially wired later-phase enforcement behind feature flags during earlier phases is not explicitly prohibited.

### F5

- finding_id: `2026-06-19-workflow-management-requirements-vertical-redo-review-run-claude-opus-4-8-adversarial-001`
- original severity: ERROR
- location: Requirement 13 AC5 / AC7
- summary: AC3 says all 19 terms are covered, but AC5's approval-required list may leave remaining read/state terms' true/false values under-emphasized; the reviewer asks to state that the AC4 table has `approval_required` for every term and that AC5 examples do not shrink that coverage.

### F6

- finding_id: `2026-06-19-workflow-management-requirements-vertical-redo-review-run-claude-opus-4-8-adversarial-002`
- original severity: WARN
- location: Requirement 13 AC11 / AC12
- summary: Single-source-of-truth direction between operation contract and registry/preflight may be ambiguous; reviewer asks to fix operation contract as source and registry/preflight as derived/read side.

### F7

- finding_id: `2026-06-19-workflow-management-requirements-vertical-redo-review-run-claude-opus-4-8-adversarial-003`
- original severity: WARN
- location: Requirement 14 AC5 / AC7
- summary: `repair_workflow_state` versus `DEVIATION` choice is left as an `or`; reviewer asks for minimal rules or explicit deferral to design.

### F8

- finding_id: `2026-06-19-workflow-management-requirements-vertical-redo-review-run-claude-opus-4-8-adversarial-004`
- original severity: WARN
- location: Requirement 15 AC5
- summary: Effective prompt audit can reference commit-mixing checks, but it is ambiguous whether it consumes results or reimplements the checks; reviewer asks to state reference-only and no reimplementation.

### F9

- finding_id: `2026-06-19-workflow-management-requirements-vertical-redo-review-run-claude-opus-4-8-adversarial-005`
- original severity: INFO
- location: Requirement 16 AC11
- summary: Active reopen scope distinction is inherited, but priority among active-scope records is not stated in Req16; reviewer suggests a cross-reference to Requirement 12 AC13.
