# Existing-system SDD implementation triad-review target

## Purpose

This is the implementation triad-review for the reopen triggered by adding an intent after the system already had requirements, design, tasks, and implementation.

The added intent is:

> 既存のシステムに意図を後から追加した場合も、仕様駆動開発の手順に従って下流工程へ進める。

The implementation phase must verify that this intent has reached code and implementation evidence without skipping the workflow stages.

## Scope

All 7 features are in review scope:

- foundation
- runtime
- evaluation
- analysis
- workflow-management
- self-improvement
- conformance-evaluation

Direct implementation impact:

- conformance-evaluation
- workflow-management

Indirect check only:

- foundation
- runtime
- evaluation
- analysis
- self-improvement

## Requirements / Design / Tasks Basis

The upstream phases already concluded:

- conformance-evaluation owns existing-system difference extraction.
- workflow-management owns downstream reopen propagation, drafting-before-review prevention, and downstream decision records.
- Indirect features are checked for conflict, but do not receive implementation changes in this reopen chain.

Primary task anchors:

- `.reviewcompass/specs/conformance-evaluation/tasks.md` T-016
- `.reviewcompass/specs/workflow-management/tasks.md` Requirement 9 / XDI-WM-002 related implementation tasks

## Implementation Changes

### conformance-evaluation

Added:

- `tools/conformance_evaluation/post_hoc_intent_diff.py`
- `tools/conformance_evaluation/schemas/post_hoc_intent_diff.schema.json`

Updated:

- `tests/conformance-evaluation/test_conformance_evaluation.py`
- `.reviewcompass/specs/conformance-evaluation/implementation-drafting.md`

Generated trial record:

- `.reviewcompass/specs/conformance-evaluation/conformance/2026-06-09-post-hoc-intent-diff.md`

The new `PostHocIntentDiff` implementation accepts:

- added intent
- feature partitioning statement
- existing requirements/design/tasks references
- implementation code references
- run date

It emits candidate records with at least:

- `feature`
- `phase`
- `classification`
- `code_refs`
- `existing_spec_refs`
- `reasoning_summary`
- `needs_human_decision`

Allowed classifications:

- `existing_sufficient`
- `spec_update_candidate`
- `design_conflict_candidate`
- `downstream_impact_candidate`
- `implementation_change_candidate`

The workflow-management candidate is handoff-only and does not modify `tasks.md` directly. Task-level candidates are expressed as `phase: tasks` with `classification: downstream_impact_candidate`; no extra task-specific classification is introduced. `needs_human_decision` means that CE cannot finalize adoption by itself. Even when this value is false, downstream adoption still happens through workflow-management gate decisions, not by CE writing back to the reopen YAML.

T-016-specific tests:

- `test_t016_post_hoc_intent_diff_outputs_candidates_and_record`
- `test_t016_post_hoc_intent_diff_rejects_unknown_classification`
- `test_t016_post_hoc_intent_diff_schema_tracks_classification_contract`

### workflow-management

No new code was required in this implementation drafting because the required behavior already exists:

- `tools/check-workflow-action.py next --json` reads the reopen in-progress file and returns `run_reopen_drafting` before `triad-review` unless `drafting_completed_gates` or `completed_gates` contains the phase drafting gate.
- Once drafting is recorded, `next` returns `run_reopen_pending_gate` for `stages/implementation.yaml#triad-review`.
- Reopen completion checks require `downstream_impact_decisions` coverage for completed / required gates.

The relevant regression test is:

- `tests/tools/test_check_workflow_action.py::NextNavigationTests::test_next_reopen_requires_drafting_before_triad_review`

Detailed mapping:

| Requirement 9 / XDI-WM-002 element | Implementation evidence | Test evidence |
| --- | --- | --- |
| reopen state has priority | `tools/check-workflow-action.py:build_in_progress_next_action` | `test_next_reads_reopen_in_progress_next_step` |
| drafting-before-review is enforced | `tools/check-workflow-action.py:_resolve_reopen_next_gate` | `test_next_reopen_requires_drafting_before_triad_review` |
| all-feature scope comes from impact decisions | `tools/check-workflow-action.py:reopen_feature_scope_from_data` | `test_next_reopen_uses_feature_impact_decisions_as_review_scope` |
| completed gates require downstream decisions | `tools/check-workflow-action.py:validate_reopen_completion_impact_decisions` | `test_commit_blocks_completed_reopen_missing_completed_gate_decision` |
| completed reopen is allowed when decisions cover gates | `tools/check-workflow-action.py:validate_reopen_completion_impact_decisions` | `test_commit_allows_completed_reopen_with_completed_gate_decisions` |
| impacted phases require gate coverage | `tools/check-workflow-action.py:validate_reopen_completion_impact_decisions` | `test_commit_blocks_completed_reopen_when_impacted_phase_is_uncovered` |

## Indirect Feature No-change Check

| feature | implementation result | evidence basis |
| --- | --- | --- |
| foundation | no implementation change | no shared vocabulary/schema change in this reopen; previous review-wave recorded future recheck if CE/WM contract becomes shared schema |
| runtime | no implementation change | no provider, prompt execution, or raw-response persistence contract change |
| evaluation | no implementation change | T-016 output is not an evaluation metric or aggregation input in this chain |
| analysis | no implementation change | T-016 output is not yet a reportable analysis intake artifact |
| self-improvement | no implementation change | no proposal/history/rollback contract change |

## Current Mechanical State

Before implementation drafting completion, `next` returned:

- `required_action: run_reopen_drafting`
- `phase: implementation`
- `stage: drafting`
- `next_pending_gate: stages/implementation.yaml#triad-review`

After recording `stages/implementation.yaml#drafting` in `drafting_completed_gates`, `next` returns:

- `required_action: run_reopen_pending_gate`
- `phase: implementation`
- `stage: triad-review`
- `next_pending_gate: stages/implementation.yaml#triad-review`

## Tests Run

- `.venv/bin/python3 -m pytest tests/conformance-evaluation/test_conformance_evaluation.py -q`
  - 19 passed
- `.venv/bin/python3 -m pytest tests/tools/test_workflow_management_implementation_drafting.py -q`
  - 3 passed
- `.venv/bin/python3 -m unittest tests.tools.test_check_workflow_action -v`
  - 139 passed
- `.venv/bin/python3 -m unittest tests.tools.test_check_workflow_action.NextNavigationTests.test_next_reopen_requires_drafting_before_triad_review -v`
  - 1 passed
- `.venv/bin/python3 tools/check-workflow-action.py next --json`
  - returned implementation triad-review as the next gate

## Review Questions

1. Does the implementation satisfy conformance-evaluation T-016 without relying on a fixed checklist mapping?
2. Does the implementation correctly avoid direct tasks.md mutation and hand off downstream candidates to workflow-management?
3. Is workflow-management correctly covered by existing code/tests, or is new implementation needed for Requirement 9 / XDI-WM-002?
4. Are indirect features correctly treated as implementation no-change in this reopen chain?
5. Are the test cases sufficient for this implementation phase?
6. Is there any workflow violation in how drafting was performed before triad-review?

## Evidence Files

- `tools/conformance_evaluation/post_hoc_intent_diff.py`
- `tools/conformance_evaluation/schemas/post_hoc_intent_diff.schema.json`
- `tests/conformance-evaluation/test_conformance_evaluation.py`
- `.reviewcompass/specs/conformance-evaluation/conformance/2026-06-09-post-hoc-intent-diff.md`
- `.reviewcompass/specs/conformance-evaluation/implementation-drafting.md`
- `.reviewcompass/specs/workflow-management/implementation-drafting.md`
- `.reviewcompass/specs/_cross_feature/reviews/2026-06-09-existing-system-sdd-implementation-drafting.md`
- `stages/in-progress/reopen-procedure-2026-06-09-existing-system-sdd-code-drift.yaml`
