# Post-write review target: API triage approval gate

## Scope

This review covers the current uncommitted changes that add mechanical enforcement for API-mediated review-run handling.

Changed files in scope:

- `tools/api_providers/review_triage.py`
- `tools/api_providers/tests/test_review_triage.py`
- `tools/check-workflow-action.py`
- `tests/tools/test_check_workflow_action.py`
- `docs/operations/WORKFLOW_NAVIGATION.md`
- `docs/operations/WORKFLOW_PRECHECK.md`
- `docs/disciplines/discipline_must_fix_discussion_obligation.md`
- `TODO_NEXT_SESSION.md`

Prior post-write artifacts already present in the worktree are also part of the target set because they are uncommitted post-write-verification records:

- `.reviewcompass/post-write-verification/post-write-2026-06-03-018.yaml`
- `docs/notes/review-runs/postwrite-commit-audit-guard-2026-06-03-r1/`

## Intended behavior

1. API-mediated review results must be summarized for the user before important findings are acted on.
2. Findings with severity `CRITICAL` / `ERROR`, or a final triage label of `must-fix`, require a user approval record before `review_triage.py decide` can mutate `triage.yaml`.
   This check applies on every `decide` call. A previously decided item is not treated as locked by this helper, but re-labeling it to `must-fix` still requires approval. A `CRITICAL` / `ERROR` item also requires approval even when the requested final label is `should-fix` or `leave-as-is`.
3. A review-run containing important decided findings requires a user approval record before `manifest-template` or `write-manifest` can produce a completed post-write manifest.
4. The approval record must show:
   - `approved_by: user`
   - matching `review_run_id`
   - `summary_presented_to_user: true`
   - `triage_presented_to_user: true`
   - `approved_finding_ids` covering the important findings
   - optional `approved_final_labels` matching requested labels when present
5. `check-workflow-action.py next` should treat forbidden-file checks as applying only while post-write-verification is pending. If a completed manifest already covers the current post-write target files and sha256 values, `next` should return to the normal workflow instead of reporting `post_write_policy_violation`.

## Key implementation notes

`tools/api_providers/review_triage.py` adds:

- `IMPORTANT_SEVERITIES = ("CRITICAL", "ERROR")`
- `_is_important_item(item, final_label=None)`
- `_load_approval_record(path)`
- `_approval_errors(...)`
- `_require_review_run_approval(...)`
- `--approval-record` for `decide`, `manifest-template`, and `write-manifest`

`decide_item(...)` now checks `_is_important_item(item, final_label)` before mutating the item. If important, it calls `_require_review_run_approval(...)` with `TRIAGE_DECIDE_APPROVAL_ACTIONS`.

The importance check is an OR condition: existing item severity in `CRITICAL` / `ERROR`, or the requested final label `must-fix`, is sufficient to require approval. This prevents a high-severity finding from bypassing the gate by choosing a non-`must-fix` label.

`assert_manifest_ready(...)` still blocks if `human_required` items remain. It now also collects decided important items and requires approval with `MANIFEST_APPROVAL_ACTIONS` before manifest output is allowed.

`tools/check-workflow-action.py` changes `cmd_next` ordering:

- First compute `manifest_state = evaluate_post_write_manifest_state(cwd, verification_targets)`.
- If `manifest_state == "completed"`, return to maintenance or normal workflow.
- Otherwise, check `list_forbidden_post_write_pending_changes(...)` and report `post_write_policy_violation` if needed.
- Then handle `human_required` or ordinary `post_write_verification`.

## Tests added or updated

`tools/api_providers/tests/test_review_triage.py`:

- Adds approval-record fixture.
- Confirms `decide` blocks important findings without approval.
- Confirms manifest output blocks important decided findings without approval.
- Updates existing important-finding success paths to pass `--approval-record`.

`tests/tools/test_check_workflow_action.py`:

- Adds commit precheck coverage for post-write targets requiring completed manifests.
- Adds `audit-commit` coverage.
- Adds `next` coverage that completed manifest should prevent a stale `post_write_policy_violation`.

Executed locally:

- `.venv/bin/python3 -m pytest tools/api_providers/tests/test_review_triage.py -q`
- `.venv/bin/python3 -m unittest tests.tools.test_check_workflow_action.CommitExitCodeTests tests.tools.test_check_workflow_action.AuditCommitTests -v`
- `.venv/bin/python3 -m unittest tests.tools.test_check_workflow_action.NextNavigationTests.test_next_does_not_report_policy_violation_after_manifest_completion tests.tools.test_check_workflow_action.NextNavigationTests.test_next_deviation_when_new_runner_created_during_post_write_verification tests.tools.test_check_workflow_action.NextNavigationTests.test_next_deviation_when_template_changes_during_post_write_verification tests.tools.test_check_workflow_action.NextNavigationTests.test_next_deviation_when_discipline_change_is_mixed_with_other_post_write_target -v`
- `.venv/bin/python3 -m pytest -q`

Latest full-suite result before this review target was added: `512 passed`.

## Review criteria

Please review whether:

1. The approval gate actually prevents an agent from acting on important API review findings before user-facing summary and triage approval are recorded.
2. The approval record fields are sufficient to machine-check the rule without making the workflow unworkable.
3. The `cmd_next` ordering change correctly distinguishes "pending post-write verification" from "completed manifest already covers current targets."
4. The tests cover the failure modes that caused the workflow violation.
5. The documentation and TODO memo describe the enforceable rule plainly enough for future sessions.

Return findings in the configured structured review format. Use `CRITICAL` or `ERROR` only for issues that should block manifest completion or require user approval before fixing.
