# Req14 approval gate implementation review integrated triage summary

## Run status

- review_run_dir: `.reviewcompass/specs/workflow-management/reviews/2026-06-20-workflow-management-implementation-req14-approval-gate-review-run`
- variant: `implementation_review_independent_3way`
- primary: `claude-sonnet-4-6`
- adversarial: `gpt-5.5`
- judgment: `gemini-3.1-pro-preview`
- initial judgment response: parse failed
- judgment retry: parsed successfully as `round-1-judgment-retry`

## Model result summary

- `claude-sonnet-4-6`: parsed, 6 findings (`ERROR`: 2, `WARN`: 3, `INFO`: 1)
- `gpt-5.5`: parsed, 6 findings (`CRITICAL`: 2, `ERROR`: 3, `WARN`: 1)
- `gemini-3.1-pro-preview`: retry parsed, 4 findings (`CRITICAL`: 2, `ERROR`: 2)

## Same-root clusters

### Cluster A: non-human actors can satisfy human-only approval

Proposed label: `must-fix`

Models:

- `gpt-5.5`: `CRITICAL`
- `gemini-3.1-pro-preview`: `CRITICAL`
- `claude-sonnet-4-6`: `ERROR` / `INFO` coverage variant

Summary:

`allows_target_operation` rejects `decided_by=proxy_model` for `decision_scope=human_only`, but does not reject other non-human actors such as `llm`. The schema permits `llm`, and implementation validation does not enforce a human-only allowlist.

Why this matters:

This directly weakens the Req14 human-only boundary for commit, push, spec.json update, phase approval, reopen finalize, and approval-required irreversible operations.

### Cluster B: current digest / binding checks are not enforced on the authorization path

Proposed label: `must-fix`

Models:

- `gpt-5.5`: `CRITICAL`
- `claude-sonnet-4-6`: related `WARN` on source digest validation

Summary:

`validate_approval_gate_record` can compare current digests only when current digest values are passed, but `allows_target_operation` has no current digest inputs and calls validation without them. The schema also does not enforce `binding_kind`-specific digest requirements.

Why this matters:

An approved record with stale or missing digest binding can still allow an irreversible operation, contradicting the required approval decision binding and stale-digest blocking behavior.

### Cluster C: approval gate is not integrated into CLI / next --json flow

Proposed label: `must-fix`

Models:

- `gemini-3.1-pro-preview`: `CRITICAL`
- `gpt-5.5`: `ERROR`

Summary:

The implementation adds approval gate schema and helper logic, but `tools/check-workflow-action.py` does not register approval-gate commands or integrate approval gate evaluation into `next --json` / irreversible-operation flow.

Why this matters:

Req14 requires `record_human_decision` to record a decision and `next --json` to decide whether the target operation may proceed. Without CLI / next integration, the approval boundary is not enforced at the workflow entry point.

### Cluster D: actor and source metadata are only presence-checked

Proposed label: `must-fix`

Models:

- `gpt-5.5`: `ERROR`
- `gemini-3.1-pro-preview`: `ERROR`
- `claude-sonnet-4-6`: `ERROR` / `WARN`

Summary:

`decided_by`, `source_ref`, and `source_digest` are required fields, but implementation validation does not reject invalid actor values, empty source strings, malformed digests, or wrong actor/source records.

Why this matters:

Req14 requires approval records to be bound to actor and source metadata. Presence-only validation is insufficient for wrong actor/source blocking.

### Cluster E: human-only required action mapping is incomplete

Proposed label: `must-fix` if confirmed against operation identifiers, otherwise `should-fix`

Models:

- `gemini-3.1-pro-preview`: `ERROR`
- `claude-sonnet-4-6`: `WARN`

Summary:

`HUMAN_ONLY_REQUIRED_ACTIONS` may omit required human-only operations such as push, spec.json update, and phase approval. The implementation contains `commit_stop_point` and `finalize_reopen`, but the mapping to actual operation identifiers needs confirmation.

Why this matters:

If real operation contracts use identifiers not listed in the human-only set, they can fall through to `proxy_allowed` or `advisory_only`.

### Cluster F: consumed / replay behavior is unclear

Proposed label: `human-required`

Models:

- `claude-sonnet-4-6`: `ERROR`

Summary:

The implementation blocks records where `consumed is True`, but does not itself mark a record as consumed after use. It is unclear whether single-use consumption is enforced elsewhere or deferred to a future write path.

Why this matters:

If approval records can be replayed, approval binding can be weakened. This needs a design/implementation boundary decision before labeling as must-fix.

### Cluster G: focused tests do not cover all required boundaries

Proposed label: `should-fix`, with parts promoted to `must-fix` when tied to fixed bugs

Models:

- `gpt-5.5`: `WARN`
- `gemini-3.1-pro-preview`: `ERROR`
- `claude-sonnet-4-6`: `WARN` / `INFO`

Summary:

Tests cover several approval gate paths but miss important cases: `decided_by=llm`, wrong/empty source metadata, allowed positive human record, stale digest through the authorization path, and additional `binding_kind=none` reject paths.

Why this matters:

The tests did not catch the human-only bypass and binding/source validation gaps reported by the models.

## Proposed handling

- Treat clusters A, B, C, and D as `must-fix`.
- Treat cluster E as `must-fix` after confirming real operation identifiers; otherwise keep it as `should-fix` with a targeted mapping test.
- Treat cluster F as `human-required` until the design responsibility for marking `consumed` is confirmed.
- Treat cluster G as `should-fix`, except tests directly covering A-D should be part of those `must-fix` fixes.

## Implementation follow-up status

### Fixed in local working tree

- Cluster A: added regression coverage and implementation guard so `decided_by=llm` cannot satisfy `decision_scope=human_only`.
- Cluster B: added authorization-path current digest parameters and fail-closed behavior when required current digest evidence is missing or mismatched.
- Cluster C partial: `explicit_human_approval_recorded` now validates `approval-gate-v1` records instead of treating their mere file presence as sufficient. Legacy non-approval-gate approval files remain presence-based for compatibility.
- Cluster C partial: added `record-human-decision` as the first CLI entry point for `record_human_decision`. It writes an `approval-gate-v1` record under `.reviewcompass/runtime/approvals/`, binds the record path back to the reopen `current_blocker`, rejects non-human actors for `human_only`, and exposes the approval record reference through `next --json` `blocked_by`.
- Cluster C partial: `next --json` now evaluates `current_blocker.status=decision_recorded` approval records for reopen approval gates. When the record is approved, human-only, bound to a real operation contract, and its `target_artifact_digest` matches the current target artifact digest, `next --json` can return the pending approval gate as `run_reopen_pending_gate`. Stale target artifact digest keeps the workflow blocked.
- Cluster C partial: non-approved approval decisions are now distinguished. `rejected` and `deferred` remain blocked with explicit decision metadata in `blocked_by`, while `changes_requested` routes to either the same phase drafting gate (`next_action_expectation=redraft`) or workflow repair (`next_action_expectation=repair`).
- Cluster D: added actor/source validation for invalid `decided_by`, empty source fields, malformed `source_digest`, and schema-level binding-kind digest requirements.
- Cluster G partial: added focused tests for A/B/C partial/D regressions.

Validation performed:

- `.venv/bin/python3 -m pytest tests/workflow-management/test_approval_gate.py -q` -> 13 passed.
- `.venv/bin/python3 -m pytest tests/workflow-management/test_approval_gate.py tests/workflow-management/test_operation_contract_schema.py tests/workflow-management/test_required_action_contract_mapping.py -q` -> 23 passed.
- `.venv/bin/python3 -m pytest tests/workflow-management/test_operation_contract_cli.py -q` -> 2 passed.
- `.venv/bin/python3 -m pytest tools/api_providers/tests/test_run_review.py tools/api_providers/tests/test_run_role.py tools/api_providers/tests/test_response_formatter.py -q` -> 51 passed.
- `.venv/bin/python3 -m pytest tools/api_providers/tests -q` -> 173 passed.
- `.venv/bin/python3 -m pytest tests/tools/test_check_workflow_action.py::SpecSetExitCodeTests::test_spec_set_blocks_approval_gate_record_when_human_only_actor_is_llm tests/tools/test_check_workflow_action.py::SpecSetExitCodeTests::test_spec_set_allows_valid_approval_gate_human_record -q` -> 2 passed.
- `.venv/bin/python3 -m pytest tests/tools/test_check_workflow_action.py -k "spec_set or human_approval or approval_gate" -q` -> 22 passed, 215 deselected.
- `.venv/bin/python3 -m pytest tests/workflow-management/test_operation_contract_cli.py tests/workflow-management/test_operation_contract_schema.py tests/workflow-management/test_required_action_contract_mapping.py -q` -> 12 passed.
- `.venv/bin/python3 -m pytest tests/tools/test_check_workflow_action.py::ReopenSetBlockerTests tests/tools/test_check_workflow_action.py::RecordHumanDecisionTests -q` -> 7 passed.
- `.venv/bin/python3 -m pytest tests/tools/test_check_workflow_action.py -k "approval_gate or human_approval or record_human_decision or reopen_set_blocker" -q` -> 10 passed, 229 deselected.
- `.venv/bin/python3 -m pytest tests/tools/test_check_workflow_action.py::ReopenSetBlockerTests tests/tools/test_check_workflow_action.py::RecordHumanDecisionTests -q` -> 9 passed.
- `.venv/bin/python3 -m pytest tests/workflow-management/test_approval_gate.py tests/tools/test_check_workflow_action.py -k "approval_gate or human_approval or record_human_decision or reopen_set_blocker" -q` -> 24 passed, 230 deselected.
- `.venv/bin/python3 -m pytest tests/tools/test_check_workflow_action.py::RecordHumanDecisionTests -q` -> 6 passed.
- `.venv/bin/python3 -m pytest tests/workflow-management/test_approval_gate.py tests/tools/test_check_workflow_action.py -k "approval_gate or human_approval or record_human_decision or reopen_set_blocker" -q` -> 24 passed, 232 deselected.
- `.venv/bin/python3 -m pytest tests/tools/test_check_workflow_action.py::RecordHumanDecisionTests -q` -> 7 passed.
- `.venv/bin/python3 -m pytest tests/workflow-management/test_approval_gate.py tests/tools/test_check_workflow_action.py -k "approval_gate or human_approval or record_human_decision or reopen_set_blocker" -q` -> 24 passed, 233 deselected.

### Still open

- Cluster C remains partially open. The CLI now records an approval decision and `next --json` can evaluate approved reopen approval records against operation contract and current target artifact digest. Non-approved decisions are mapped for `rejected`, `deferred`, `changes_requested + redraft`, and `changes_requested + repair`. Remaining work: `staged_file_set_digest` / `both` current digest evidence and record consume after use.
- Cluster E remains open until actual operation identifiers for push, spec.json update, and phase approval are confirmed against the operation registry.
- Cluster F remains human-required until the responsibility for marking approval records as consumed is confirmed.

Related validation caveat:

- Running `.venv/bin/python3 -m pytest tests/workflow-management/test_operation_contract_cli.py tests/tools/test_check_workflow_action.py -q` produced 236 passed and 1 failure in `PostWriteReviewRunEndToEndTests.test_next_accepts_manifest_generated_from_review_triage_helper`. The failure is in `review_triage.py` post-write manifest readiness and is not caused by the approval gate changes.

## Notes

- The first Gemini response was not parser-compatible but contained substantively similar findings. The retry produced parser-compatible findings and is the judgment result used here.
- `triage.yaml` was generated before the judgment retry, so it does not fully represent the retry findings. This integrated summary should be used together with the parsed retry file.
- The attempted `--default-variant-for implementation_review` failed because `operation_defaults.implementation_review` is not registered. The actual run used explicit variant `implementation_review_independent_3way`.
