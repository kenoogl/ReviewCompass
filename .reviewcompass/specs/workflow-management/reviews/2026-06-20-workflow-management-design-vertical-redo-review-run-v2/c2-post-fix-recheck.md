# C2 Post-Fix Recheck

## Scope

- Target artifact: `.reviewcompass/specs/workflow-management/design.md`
- Cluster: C2
- Source findings:
  - `2026-06-20-workflow-management-design-vertical-redo-review-run-v2-claude-sonnet-4-6-adversarial-001`
  - `2026-06-20-workflow-management-design-vertical-redo-review-run-v2-claude-sonnet-4-6-adversarial-002`
- Recheck date: 2026-06-20

## Issue Summary

C2 said the design did not individually map all 19 `required_action` values to operation contract fields. It also said `run_maintenance` and `run_workflow_stage` were described as compound operations without concrete branch conditions, internal steps, max effect, or approval aggregation rules.

## Applied Design Response

`design.md` Requirement 13 now includes:

- A 19-row operation contract baseline table for every `required_action`.
- Per-action baseline fields:
  - `effect_kind`
  - `approval_required`
  - `phase_boundary`
  - `sequence.mode`
  - `actor.kind`
  - whether the operation is branchy
- A rule that the table is the minimum boundary and `stages/operation-contracts.yaml` must not weaken it.
- A rule that branchy operations must not be decided from representative values alone.
- Concrete initial branch tables for:
  - `run_maintenance`
  - `run_workflow_stage`
- Approval aggregation rules for the compound operations.
- A human-only override rule for commit, push, `spec.json` update, phase / gate completion, reopen finalize, and approval-required irreversible operation execution.

## Verification

The following local checks were run:

```text
.venv/bin/python3 - <<'PY'
from pathlib import Path
text = Path('.reviewcompass/specs/workflow-management/design.md').read_text(encoding='utf-8')
actions = [
  'repair_workflow_state',
  'run_post_write_verification',
  'wait_for_human_decision',
  'record_human_decision',
  'run_maintenance',
  'advance_reopen_after_commit_stop_point',
  'commit_stop_point',
  'draft_reopen_plan_candidates',
  'apply_approved_reopen_plan',
  'advance_reopen_after_approval_stop_point',
  'repair_canonical_documents',
  'run_reopen_drafting',
  'run_reopen_pending_gate',
  'collect_required_decisions',
  'finalize_reopen',
  'draft_reopen_classification',
  'run_reopen_start',
  'run_workflow_stage',
  'completed',
]
section = text.split('19語彙の operation contract 基線は次とする。', 1)[1].split('単純操作で承認を必須とする action', 1)[0]
missing = [a for a in actions if f'| `{a}` |' not in section]
print('missing=', missing)
print('count=', sum(1 for a in actions if f'| `{a}` |' in section))
for needle in ['maintenance_kind=read_only_diagnostic', 'maintenance_kind=workflow_state_repair', 'stage=triad-review', 'phase_transition=true', 'approval aggregation']:
  print(needle, needle in section)
PY

.venv/bin/python3 -m pytest tools/api_providers/tests -q
```

Outcome:

- Missing required_action entries: none.
- Required action count in the new baseline section: 19.
- Compound-operation branch evidence found:
  - `maintenance_kind=read_only_diagnostic`
  - `maintenance_kind=workflow_state_repair`
  - `stage=triad-review`
  - `phase_transition=true`
  - `approval aggregation`
- `tools/api_providers/tests`: 152 passed.

## Result

C2 is addressed by the current `design.md` edits.

## Remaining Limits

This recheck addresses C2 only. It does not decide C3-C7, does not authorize `spec.json` mutation, does not complete the design gate, and does not authorize commit, push, phase transition, or reopen finalization.
