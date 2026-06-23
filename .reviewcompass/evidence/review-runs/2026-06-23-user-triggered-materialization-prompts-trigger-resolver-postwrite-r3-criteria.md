# PTC-4 Trigger Resolver Post-Write Verification Criteria

phase: post_write_verification

## Review Task

Review whether the latest PTC-4 follow-up changes address the accepted behavior-path finding from the prior 3-way review:

Short user continuation requests such as `次へ`, `進める`, and `継続` must mechanically resolve to the plan-to-TODO bridge operation when there is an unmaterialized plan slice.

This review is limited to the PTC-4 trigger resolver / operation prompt selection fix. Do not review unrelated `docs/notes` lightweight self-check policy test failures.

## Source Finding Being Addressed

Prior review run:

`.reviewcompass/evidence/review-runs/2026-06-23-user-triggered-materialization-prompts-postwrite-rerun/`

Same-root accepted finding:

- There was no mechanical trigger resolver mapping short continuation requests (`次へ`, `進める`, `継続`) to `user_initiated_plan_to_todo_bridge`.
- Routing was operator-mediated and only documented inside the effective prompt.
- Regression tests mainly checked prompt text rather than operation prompt selection behavior.
- `DEFAULT_DISCIPLINE_MAP` fallback did not include the new materialization plan source ref.

## Changed Target Files

Review these target files as model-readable materials:

- `tools/check-workflow-action.py`
- `tests/tools/test_check_workflow_action.py`
- `.reviewcompass/guidance/WORKFLOW_DISCIPLINE_MAP.yaml`
- `.reviewcompass/guidance/effective-prompts/user-initiated-plan-to-todo-bridge.prompt.md`
- `.reviewcompass/guidance/effective-prompts/user-initiated-backlog-todo-execution.prompt.md`
- `tests/tools/test_effective_prompt_contract.py`
- `.reviewcompass/guidance/API_REVIEW_PROMPT_QUALITY.md`
- `.reviewcompass/guidance/discipline_llm_as_judge_prompting.md`
- `.reviewcompass/backlog/plans/plan-2026-06-23-plan-todo-checklist-materialization.yaml`
- `.reviewcompass/backlog/todos/todo-2026-06-23-user-triggered-materialization-prompts.yaml`

## Required Checks

### Check 1: Mechanical Trigger Resolver Exists

Verify that `operation-prompt --trigger-text <text>` can resolve short continuation requests to an operation without the caller manually passing `user_initiated_plan_to_todo_bridge`.

Report a finding if the new behavior is still operator-mediated.

### Check 2: Correct Routing Condition

Verify that `次へ`, `進める`, and `継続` route to `user_initiated_plan_to_todo_bridge` only when an unmaterialized plan slice is found.

Report a finding if routing ignores materialization state, silently proceeds without a plan, or chooses a direct implementation operation.

### Check 3: Auditable Output

Verify that the JSON output includes enough `trigger_resolution` evidence to explain why the operation was selected, including trigger kind, reason, and candidate plan IDs.

Report a finding if the output is not auditable.

### Check 4: Regression Tests

Verify that tests execute the operation prompt command path and assert the resolved operation, not only prompt text snippets.

Report a finding if tests remain text-only for the core trigger routing claim.

### Check 5: Fallback Discipline Map

Verify that `DEFAULT_DISCIPLINE_MAP` fallback includes the materialization plan source refs for both `user_initiated_plan_to_todo_bridge` and `user_initiated_backlog_todo_execution`.

Report a finding if the fallback can still silently omit the new source materials when the YAML map is unavailable.

### Check 6: Scope Control

Do not treat unrelated broad test failures around `docs/notes` lightweight self-check vs strict post-write verification as part of this fix unless the trigger resolver change directly caused them.

## Finding Policy

Return findings for any unresolved part of the accepted routing / fallback / test coverage cluster.

If the accepted finding is fixed, return no findings.

Strict output contract:

- Output YAML only.
- The top-level YAML must include `findings`.
- If there are no findings, output exactly:

```yaml
findings: []
```

- Do not append free-form rationale outside YAML.
- If rationale is needed for a finding, put it inside that finding's `rationale` field.

Use severity:

- ERROR: short continuation requests can still bypass the bridge mechanically.
- WARN: routing exists but is weakly scoped, weakly tested, or poorly auditable.
- INFO: clarity or maintainability improvements.

## Out of Scope

- Do not review the unrelated `docs/notes` lightweight self-check policy mismatch.
- Do not approve commit or push.
- Do not require triage decisions or approval records as part of this review.
