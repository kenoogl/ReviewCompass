# C4 Post-Fix Recheck

## Scope

- Target artifact: `.reviewcompass/specs/workflow-management/design.md`
- State artifact: `stages/in-progress/reopen-procedure-2026-06-19.yaml`
- Cluster: C4
- Source finding:
  - `2026-06-20-workflow-management-design-vertical-redo-review-run-v2-claude-sonnet-4-6-adversarial-005`
- Recheck date: 2026-06-20

## Issue Summary

C4 said the design distinguished historical `spec.json.reopened` from active reopen scope, but did not define the authoritative state structure for active reopen scope. It also did not specify how `next --json` reads, initializes, or clears that active scope.

## Applied Design Response

`design.md` now states:

- Active scope is stored in `stages/in-progress/reopen-procedure-*.yaml`.
- The authoritative fields are:
  - `active_reopen_scope`
  - `active_impact_review_scope`
- `spec.json.reopened` is historical and is not active scope.
- `next --json` reads those fields and maps them to:
  - `next_action.reopen_scope`
  - `next_action.impact_review_scope`
- Missing, stale, or inconsistent active scope causes `repair_workflow_state` or `DEVIATION`, not normal progress.
- Scope is initialized in reopen step 1 from classification and trigger_map evidence.
- During chain re-execution, gate completion updates `pending_gates`, `completed_gates`, and `downstream_impact_decisions`; scope expansion / shrinkage requires a new user decision or repair workflow.
- Scope is closed only by moving the in-progress record to `stages/completed/` after pending gates are resolved and downstream impact coverage is recorded.

The current in-progress record now includes `active_reopen_scope` and `active_impact_review_scope` for the active workflow-management R-0 reopen.

## Verification

The following checks were run:

```text
rg -n 'active_reopen_scope|active_impact_review_scope|spec\.json\.reopened|active scope の正本|next_action\.reopen_scope|repair_workflow_state' .reviewcompass/specs/workflow-management/design.md stages/in-progress/reopen-procedure-2026-06-19.yaml

.venv/bin/python3 -m pytest tools/api_providers/tests -q
```

Outcome:

- `design.md` defines `active_reopen_scope` / `active_impact_review_scope` as active scope authority.
- `design.md` states that `spec.json.reopened` is historical, not active scope.
- `design.md` states that `next --json` reads the in-progress record and returns `repair_workflow_state` when scope is missing or inconsistent.
- `stages/in-progress/reopen-procedure-2026-06-19.yaml` now contains the active scope fields.
- `tools/api_providers/tests`: 152 passed.

## Result

C4 is addressed by the current edits.

## Remaining Limits

This recheck addresses C4 only. It does not decide C5-C7, does not authorize `spec.json` mutation, does not complete the design gate, and does not authorize commit, push, phase transition, or reopen finalization.
