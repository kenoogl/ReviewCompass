# Integrated post-fix review

## Scope

- Review run: `2026-06-20-workflow-management-design-vertical-redo-review-run-v2`
- Target artifact: `.reviewcompass/specs/workflow-management/design.md`
- Original target SHA in `target-manifest.yaml`: `cc668ad714baf00bb6edd5e108cd6e1b3a9a673dac88e0cfe947e58fa8643ef8`
- Current target SHA after post-fix edits: `b20a4125d5c7635ca86c59aff786c65a62dae2efff53879070ac7e5b41d0bf75`
- Review date: 2026-06-20

This review is a local integrated post-fix review by the main LLM. It did not run a new proxy_model or external API review. It checks whether the accumulated post-fix edits still satisfy the original review intent and whether the updated design has introduced local contract inconsistencies.

## Inputs

- `target-manifest.yaml`
- `review_summary.md`
- `triage.yaml`
- `post-fix-coverage-inventory.md`
- All local `*post-fix*.md` recheck artifacts in this review-run directory
- Current `.reviewcompass/specs/workflow-management/design.md`

## Findings

### ERROR: `approval_required` is typed as boolean but branch step tables contain policy prose

The operation contract field list defines `approval_required: boolean` at `.reviewcompass/specs/workflow-management/design.md:1590`. However, the branch and step tables added for `run_maintenance` and `run_workflow_stage` put prose values such as `外部送信承認 contract に従う` in the same column at `.reviewcompass/specs/workflow-management/design.md:1684`, `.reviewcompass/specs/workflow-management/design.md:1703`, `.reviewcompass/specs/workflow-management/design.md:1711`, `.reviewcompass/specs/workflow-management/design.md:1712`, `.reviewcompass/specs/workflow-management/design.md:1713`, `.reviewcompass/specs/workflow-management/design.md:1727`, `.reviewcompass/specs/workflow-management/design.md:1730`, and `.reviewcompass/specs/workflow-management/design.md:1732`.

This weakens the contract from a machine-checkable boolean into an implementation-time interpretation. It also reintroduces the risk that external-send approval and phase/gate approval are mixed through prose rather than represented as separate fields or referenced contract IDs.

Required follow-up:

- Keep `approval_required` strictly boolean in all branch and step baseline tables.
- Add a separate field such as `approval_contract_ref`, `external_send_approval_ref`, or equivalent, when a step must bind to the external-send approval contract.
- State the aggregation rule over the boolean field and the referenced approval contract explicitly.

### WARN: branch step baseline requires `source_ref` but the tables do not provide it

The design states that each `internal_steps[]` element must have `step_id`, `effect_kind`, `approval_required`, `phase_boundary`, and `source_ref` at `.reviewcompass/specs/workflow-management/design.md:1674`. The branch step baseline tables at `.reviewcompass/specs/workflow-management/design.md:1690` and `.reviewcompass/specs/workflow-management/design.md:1721` contain `step_id`, `effect_kind`, `approval_required`, and `phase_boundary`, but omit `source_ref`.

The text says the human-facing tables are expanded into operation contract structure, so this is not necessarily a runtime defect by itself. However, because `source_ref` is mandatory and is intended to prevent invented implementation authority, omitting it from the baseline leaves the source binding to downstream task judgment.

Required follow-up:

- Add a `source_ref` column to the branch step baseline tables, or
- State a deterministic inheritance rule that derives each step `source_ref` from the branch row and the current design section without task-level invention.

## Non-findings and status

- The local coverage inventory confirms all 15 triage findings have at least one post-fix recheck artifact: 15 covered, 0 missing.
- The previous `tools/api_providers/tests` verification remained green at `152 passed` during the individual post-fix rechecks.
- The original `target-manifest.yaml` is expected to be stale after post-fix edits. Any new external review or gate-completion judgment should use the current target SHA above or a refreshed manifest.
- `triage.yaml` still represents the review-run as not finalized. This integrated review does not mark findings adopted, rejected, or complete, and does not authorize commit, push, `spec.json` mutation, phase transition, or reopen finalization.

## Recommendation

Do not treat the design post-fix work as complete yet. First fix the two Req 13 table/contract consistency issues above, then run a narrow local recheck against the corrected lines. After that, the run can proceed to the next review-wave or human decision gate with a current target manifest.
