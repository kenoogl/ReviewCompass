# Integrated post-fix recheck

## Scope

- Review run: `2026-06-20-workflow-management-design-vertical-redo-review-run-v2`
- Rechecked artifact: `.reviewcompass/specs/workflow-management/design.md`
- Prior integrated review: `integrated-post-fix-review.md`
- Current target SHA after this fix: `ac6bd42e57b507a615af3ed6a40f3c031f56fe75f27e7f1fcc12ddcb4dc46558`
- Recheck date: 2026-06-20

## Findings rechecked

### `approval_required` boolean / approval contract prose split

Status: resolved locally.

Changes:

- Added `approval_contract_refs` to the operation contract logical structure.
- Stated that `approval_required` only accepts boolean values.
- Required external-send, human-only, and operation-specific approval links to be represented by `approval_contract_refs` or branch / step `approval_contract_ref`.
- Removed policy prose from the `approval_required` cells in the `run_maintenance` and `run_workflow_stage` branch step tables.
- Set external API execution steps to `approval_required=true` with `approval_contract_ref=external_send_approval`.
- Kept non-approval steps at `approval_required=false` with `approval_contract_ref=none`.

Verification:

- Search for the previous prose values in the current design returned no matches:
  - `外部送信承認 contract に従う`
  - `外部 API を使う step は外部送信承認 contract に従う`

### branch step `source_ref` coverage

Status: resolved locally.

Changes:

- Added `approval_contract_ref` and `source_ref` to the required branch internal step structure.
- Added `source_ref` columns to both branch step baseline tables.
- Assigned deterministic source refs for each listed step using the pattern:
  - `design.md#req13-run-maintenance-step-<step_id>`
  - `design.md#req13-run-workflow-stage-step-<step_id>`

Verification:

- The `run_maintenance` branch step table now has columns:
  - `branch condition`
  - `step_id`
  - `effect_kind`
  - `approval_required`
  - `approval_contract_ref`
  - `phase_boundary`
  - `source_ref`
- The `run_workflow_stage` branch step table now has the same columns.

## Remaining limits

This recheck is local and narrow. It does not run a new external triad-review, does not mark `triage.yaml` final, and does not authorize commit, push, `spec.json` mutation, phase transition, or reopen finalization.

The current post-fix target set is recorded in `post-fix-target-manifest.yaml`. The original `target-manifest.yaml` remains the immutable input record for the first triad-review run.
