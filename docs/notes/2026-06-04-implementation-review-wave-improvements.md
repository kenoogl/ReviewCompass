# Implementation Review-Wave Improvements

## Context

Implementation review-wave found useful blockers before approval:

- `workflow-management` triage had `triage_status: decided` while 11 individual items still had `decision_status: draft`.
- `evaluation` implementation review evidence existed under `docs/notes/review-runs/`, but the feature namespace did not point to it.
- `foundation` recheck remained pending even after downstream implementation review evidence had been collected.

## Improvements

| Improvement | Purpose | Status |
| --- | --- | --- |
| Treat draft triage items as unresolved | Prevent `triage_status: decided` while item-level decisions are still draft. | implemented in `tools/api_providers/review_triage.py` |
| Require feature-local pointers for API review-run evidence | Make review-wave evidence collection follow `.reviewcompass/specs/<feature>/reviews/` even when raw runs live under `docs/notes/review-runs/`. | applied for evaluation; future generalization pending |
| Define recheck clearing evidence | Avoid leaving stale recheck flags, and avoid clearing them without downstream evidence. | applied for foundation; canonical rule pending |
| Generate review-wave summary metrics | Stabilize reporting of feature coverage, triage completeness, recheck state, and carry-forward count. | pending |

## Implemented Change

`review_triage.py` now treats any item whose `decision_status` is not `decided` as unresolved triage.

Effects:

- `list-pending` includes `draft` items as pending, not only `human_required` items.
- `decide` keeps top-level `triage_status: draft` while any item remains draft.
- `model-result-summary.yaml` keeps affected model rows at `triage_pending` while any item remains draft.
- manifest generation and apply-fixes readiness fail closed while unresolved triage remains.

Regression tests:

- `test_decide_keeps_triage_draft_when_other_draft_item_remains`
- `test_list_pending_includes_draft_items`

## Follow-Up Candidates

- Add a review-wave summary command that emits feature coverage, triage completeness, recheck state, dependency status, and carry-forward count.
- Add a canonical rule for when recheck can be cleared after downstream review evidence is collected.
- Add a feature-local pointer requirement for API review-run bundles used as phase evidence.
