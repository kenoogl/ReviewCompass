# Integrated post-fix recheck

## Scope

- Review run: `2026-06-20-workflow-management-tasks-vertical-redo-review-run-v3`
- Rechecked artifact: `.reviewcompass/specs/workflow-management/tasks.md`
- Current target SHA after fixes: `053858cf4abf94bd7b54bf8a45a8ca9504afef39ea8be48bd282193f95e84098`
- Recheck date: 2026-06-20

## Recheck result

Status: resolved locally for the tasks triad-review findings.

The local recheck confirms that C1-C6 were reflected in `tasks.md` and C7 was recorded as leave-as-is. This is a local post-fix recheck, not a new external API review.

## Findings rechecked

### C1: branchy operation contract and approval aggregation

Status: resolved locally.

`T-016` now requires branch and internal step contract structures for `run_maintenance`, `run_reopen_pending_gate`, and `run_workflow_stage`. It also requires approval aggregation, human-only override handling, approval contract references, phase boundaries, and registry/contract duplication checks.

### C2: approval gate record and binding rules

Status: resolved locally.

`T-017` now requires the approval gate record field set from design, derives `decision_scope` from the operation contract, defines the four `binding_kind` values, and rejects missing or mismatched digest bindings for irreversible or approval-required operations.

### C3: workflow-state snapshot

Status: resolved locally.

`T-017` now names the snapshot path, requires `source_next_action_sha256`, and carries the minimum top-level snapshot structure plus `current_work` fields.

### C4: prompt length and next-action compatibility

Status: resolved locally.

`T-018` now requires `prompt_length` bounds from `WORKFLOW_DISCIPLINE_MAP.yaml`, preserves the configured `failure_verdict`, and checks `postconditions.check_kind=next_action_compatible` against `on_completion`.

### C5: language task vocabulary and Phase 6 judge audit

Status: resolved locally.

`T-018` now uses the design vocabulary for language task I/O and adds structured Phase 6 judge audit output for known gap findings. The traceability table for Requirement 15 was also updated to match that scope.

### C6: Phase 2 operation-list and proxy triage safeguards

Status: resolved locally.

`T-019` now includes read-only `operation-list --json`, separates active reopen scope from impact review scope, records `spec.json.reopened` as historical state rather than active scope, and requires review/apply scope mismatch detection plus fixed human-required predicate order.

### C7: residual leave-as-is items

Status: recorded.

The remaining claims did not require additional task edits: the excerpt range issue was not valid as stated, the workflow-state concern was already consistent, and the traceability issue was handled through C5/C6.

## Local verification

```text
.venv/bin/python3 tools/api_providers/review_triage.py assert-apply-fixes-ready ...: apply_fixes_ready: true
fix_count 22
approved_count 22
missing []
extra []
label_mismatches []
git diff --check: passed
```

## Remaining limits

This recheck does not run a new external triad-review, does not authorize commit, push, `spec.json` mutation, phase transition, or reopen finalization.
