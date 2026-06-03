# Post-write verification target: proxy review and parallel implementation workflow

## Scope

This post-write verification covers the 2026-06-04 update that canonicalized and partially mechanized the workflow for:

1. review-run post-processing by the main session LLM,
2. proxy_model decision delegation for important findings,
3. parallel implementation using sub-implementation LLMs,
4. subthread / separated worktree output handling,
5. proxy approval machine checks in `tools/api_providers/review_triage.py`.

## Files changed in this scope

- `docs/operations/SESSION_WORKFLOW_GUIDE.md`
- `docs/operations/WORKFLOW_NAVIGATION.md`
- `TODO_NEXT_SESSION.md`
- `.reviewcompass/specs/workflow-management/requirements.md`
- `.reviewcompass/specs/workflow-management/design.md`
- `.reviewcompass/specs/workflow-management/tasks.md`
- `docs/notes/2026-06-04-proxy-review-parallel-implementation-plan.md`
- `tests/tools/test_session_record_contract.py`
- `tools/api_providers/review_triage.py`
- `tools/api_providers/tests/test_review_triage.py`

## Canonical workflow added

The canonical flow is:

1. The main session LLM reads all review raw responses, builds model summaries, clusters same-root findings, and drafts triage labels: `must-fix`, `should-fix`, `leave-as-is`.
2. For important findings, the main session LLM prepares plain-language issue explanations, multiple options, option tradeoffs, downstream impact, and a recommended option.
3. A `proxy_model` decides the selected option, rationale, rejected-option reasons, and final label. The proxy model does not implement changes.
4. Machine guards verify that proxy decisions are complete before fixes are applied.
5. The main session LLM implements only accepted fixes using TDD.
6. Commit, push, spec.json updates, phase transitions, discipline changes, and major policy changes remain human-approved irreversible operations.

## Parallel implementation policy added

Parallel implementation is allowed only after findings have been classified into safe units.

- Proxy decision requests may be parallelized by same-root finding cluster.
- Implementation work may be parallelized only when units do not update the same files or share mutable output contracts.
- Shared schemas, shared builders, same manifest files, same traceability outputs, and same target files are serial.
- Sub-implementation LLMs are handled as separate threads with separated worktrees by default.
- Same-repo parallel implementation is prohibited except for read-only investigation or very small non-conflicting checks.

Subthread outputs are classified as:

- `implementation_diff`: source, test, schema, fixture, or minimal docs changes eligible for mainline integration.
- `verification_summary`: red/green tests, commands, skipped test reasons.
- `decision_basis`: blockers, failed assumptions, new judgment questions, adoption-relevant failure logs.
- `work_noise`: temporary notes, intermediate logs, failed patch attempts, local scratch records. These are not imported into the mainline repo.

## Machine guard added

`tools/api_providers/review_triage.py` now accepts `approved_by: proxy_model` in approval records in addition to `approved_by: user`.

For proxy approval, it requires:

- `proxy_model_id`
- `proxy_decisions`
- decision file per required finding
- decision file fields:
  - `finding_id`
  - `approved_by: proxy_model`
  - `proxy_model_id`
  - `selected_option`
  - `final_label`
  - `rationale`
  - `rejected_options`
  - `raw_response_path`
- existing raw response file
- consistency between `approved_final_labels` and each decision file `final_label`

The guard remains fail-closed. Missing proxy decision files, missing raw responses, missing required fields, and label mismatches must block apply-fixes readiness.

## Tests added or updated

`tests/tools/test_session_record_contract.py` now checks that the canonical documents define:

- proxy_model review-run decision workflow,
- role split between main LLM, proxy_model, machine guard, implementation, and human,
- parallelizable units,
- separate thread + separated worktree policy,
- output classes and work-noise exclusion.

`tools/api_providers/tests/test_review_triage.py` now checks:

- unresolved `human_required` blocks apply-fixes readiness,
- fix labels require approval,
- user approval still passes,
- proxy_model approval passes when decision and raw evidence exist,
- proxy_model approval fails when raw response evidence is missing.

## Verification commands already run

```text
.venv/bin/python3 -m pytest tools/api_providers/tests -q
112 passed

.venv/bin/python3 -m pytest tests/tools/test_session_record_contract.py -q
8 passed
```

## Known workflow state

`tools/check-workflow-action.py next --json` currently returns `post_write_policy_violation` because post-write verification is pending and tool files were changed after the canonical docs were updated. This review run is intended to resolve that pending verification path, not to mark the normal implementation workflow complete.

## Review request

Please review whether the canonicalized workflow and proxy approval machine guard are sufficient and internally consistent.

Focus especially on:

1. Whether the role split is clear enough to prevent the main session LLM from silently deciding important fixes.
2. Whether proxy_model approval has enough evidence to be auditable.
3. Whether sub-implementation LLMs and separated worktrees are constrained enough to avoid noisy or unsafe integration.
4. Whether work-noise exclusion could accidentally discard needed evidence.
5. Whether the implementation still preserves the user-only boundary for irreversible operations.

Return findings as structured YAML if possible. If strict YAML is difficult, return raw findings with stable IDs, severity, target location, description, rationale, and recommendation.
