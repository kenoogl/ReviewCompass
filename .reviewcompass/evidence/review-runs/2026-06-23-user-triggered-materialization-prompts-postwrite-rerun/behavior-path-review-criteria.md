# PTC-4 Behavior-Path Post-Write Verification Criteria

phase: post_write_verification

## Review Task

Review whether the PTC-4 changes actually make short user continuation requests follow the plan-to-TODO/checklist materialization path before implementation work starts.

This is a behavior-path claim review, not only a documentation consistency review.

## User Review Requirements

The user challenged the prior post-write review because `findings: []` looked implausible. The prompt had been created too narrowly: it checked updated guidance/effective prompts and the discipline map, but did not include enough trigger, operation, preflight, runner, or test materials to verify whether the intended behavior path is enforced.

This rerun must check the actual path from short user requests such as `次へ`, `進める`, and `継続` through operation prompt selection, plan materialization review, TODO/checklist generation, coverage audit, and task-quality audit.

## Main Preanalysis

The claim under review is:

1. Short continuation requests must not bypass the plan-to-TODO bridge when the next work is derived from a plan.
2. The operator-facing effective prompts must require `work-backlog plan-todo-bridge --plan-id <plan-id> --json` before creating a TODO from a plan.
3. The prompts must require runtime checklist creation and coverage/quality audits before marking a checklist item active or starting implementation.
4. The discipline map must connect the relevant user-initiated operations to the canonical effective prompts and source materials.
5. The tests must fix enough of this behavior so future edits cannot silently remove the materialization review / quality gates.

Important limitation to verify:

- If the repository has no machine trigger resolver that maps raw short utterances (`次へ`, `進める`, `継続`) directly to `user_initiated_plan_to_todo_bridge`, that is a finding. Guidance text alone does not prove the short request path is mechanically enforced.
- If the behavior is currently operator-mediated rather than fully mechanical, the review should say so plainly and classify the gap.

## Review Target Bundle

The target files supplied to the review runner include both changed artifacts and execution-path materials. Treat all supplied files as model-readable materials.

Changed artifacts:

- `.reviewcompass/guidance/WORKFLOW_DISCIPLINE_MAP.yaml`
- `.reviewcompass/guidance/effective-prompts/user-initiated-plan-to-todo-bridge.prompt.md`
- `.reviewcompass/guidance/effective-prompts/user-initiated-backlog-todo-execution.prompt.md`
- `tests/tools/test_effective_prompt_contract.py`
- `.reviewcompass/backlog/plans/plan-2026-06-23-plan-todo-checklist-materialization.yaml`
- `.reviewcompass/backlog/todos/todo-2026-06-23-user-triggered-materialization-prompts.yaml`

Execution-path source materials:

- `tools/check-workflow-action.py`
- `tools/check_workflow_action/operation_preflight.py`
- `tools/check_workflow_action/work_backlog.py`
- `tools/check_workflow_action/task_quality_check.py`
- `tests/tools/test_check_workflow_action.py`
- `tests/tools/test_work_backlog_cli.py`
- `tests/tools/test_task_quality_check_cli.py`

Prompt-design method used for this rerun:

- `.reviewcompass/guidance/API_REVIEW_PROMPT_QUALITY.md`
- `.reviewcompass/guidance/discipline_llm_as_judge_prompting.md`

## Required Checks

### Check 1: Short Request to Operation Path

Determine whether the supplied implementation and tests show a mechanical path from short continuation requests (`次へ`, `進める`, `継続`) to the relevant operation prompt, especially `user_initiated_plan_to_todo_bridge` when a plan has unmaterialized work.

Report a finding if this is only documented for the operator but not enforced or tested by a trigger resolver / operation preflight / command path.

### Check 2: Plan Materialization Review Before TODO Creation

Determine whether the canonical plan-to-TODO bridge prompt requires `work-backlog plan-todo-bridge --plan-id <plan-id> --json` before `work-backlog add-todo`, and whether it requires reading `materialization.summary`, `materialization.slices`, and `materialization.next_candidates`.

Report a finding if the order is ambiguous, optional, or not test-protected.

### Check 3: TODO/Checklist Coverage and Quality Before Implementation

Determine whether the canonical prompts require `work-backlog start-checklist`, `work-backlog audit-checklist-coverage`, and `task-quality-check audit` before marking a checklist item active or starting implementation work.

Report a finding if active implementation can start before coverage/quality is OK, or if WARN/high-risk handling can bypass review materials.

### Check 4: Discipline Map Wiring

Determine whether `.reviewcompass/guidance/WORKFLOW_DISCIPLINE_MAP.yaml` wires the relevant operation prompt IDs to the canonical effective prompts and the plan materialization source materials.

Report a finding if the map omits necessary source references or if defaults in `tools/check-workflow-action.py` diverge from the canonical map in a way that could affect operation prompt generation.

### Check 5: Regression Tests

Determine whether the tests verify the behavior-path claims, not merely the presence of words in documents.

Report a finding if tests only assert text snippets while leaving the operation routing / preflight / command output path untested.

### Check 6: Prompt-Design Compliance

Determine whether this rerun criteria and target bundle follow the revised prompt-design method:

- main preanalysis before prompt
- behavior-path materials included
- claim-by-claim required checks
- no reliance on unexplained single-model `findings: []`

Report a finding if the prompt remains too confirmatory, under-scoped, or unable to produce auditable rationale.

## Finding Policy

Return findings for any gap that could let an operator or tool path bypass plan materialization review, TODO/checklist creation, coverage audit, task-quality audit, or WARN/high-risk review-material preparation.

Return findings for insufficient evidence even if the guidance text says the right thing.

If a claim passes, include a brief pass rationale in the response summary or rationale fields. Do not return bare `findings: []` with no explanation.

Use severity:

- ERROR: behavior can bypass a required gate or no mechanical/test evidence exists for a core claim.
- WARN: behavior is mostly guided but weakly tested, under-specified, or operator-mediated.
- INFO: clarity or auditability improvement that does not change gate behavior.

## Out of Scope

- Do not review unrelated workflow-management features.
- Do not propose broad architecture rewrites unless needed to address a concrete finding.
- Do not approve commit or push.
