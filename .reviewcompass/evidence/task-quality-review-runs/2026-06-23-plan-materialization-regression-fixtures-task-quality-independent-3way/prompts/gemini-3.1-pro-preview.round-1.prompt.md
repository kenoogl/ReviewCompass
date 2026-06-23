prompt_id: gemini_review
provider: gemini-api
model_id: gemini-3.1-pro-preview

# Task
Review the target document for the requested phase and criteria.

# Phase
task_quality_review

# Criteria
# Task Quality Review Criteria: Plan Materialization Regression Fixtures

## Review Task
Review whether the backlog TODO and runtime checklist for
`todo-2026-06-23-plan-materialization-regression-fixtures` /
`checklist-todo-2026-06-23-plan-materialization-regression-fixtures`
are safe to use as the execution checklist after `task-quality-check audit`
returned `OK` with a warning.

Task-quality warning:

- `red test items appear after implementation items: PTC-RT-1, PTC-RT-2, PTC-RT-3, PTC-RT-4`

The review should decide whether the warning is a blocking task-quality issue,
and identify any missing checklist or TODO quality defects that would make
execution unsafe.

## Prompt Construction Basis
- This criteria document is generated from task-quality review materials.
- The prompt follows the established three-review practice: material review,
  independent questions, explicit scope, sensitive-information check, and YAML
  result contract.
- Treat main preanalysis in the materials as a hypothesis to inspect, not as an
  answer to copy.

## User Review Requirements
- WARN from task-quality-check should be reviewed by API, not bypassed by local judgment.
- Review the generated review materials and judge whether the TODO/checklist may proceed.
- Do not authorize commit, push, file moves, or completion of the work.

## Review Target
The target file is
`.reviewcompass/evidence/review-materials/2026-06-23-plan-materialization-regression-fixtures/review-materials.yaml`.

It contains:
- The backlog TODO full text.
- The runtime checklist full text.
- The task-quality audit result.
- Main preanalysis generated from the audit.
- Review questions and decision boundaries.

## Required Checks
1. Are checklist items concrete, non-overlapping, and sized for execution?
   Expected output: Find missing granularity risks with item IDs and evidence.
2. Is the checklist order suitable for TDD and review-before-implementation flow?
   Expected output: Find ordering risks without treating warnings as automatic failure.
3. Does the checklist preserve the source TODO intent and stated scope?
   Expected output: Find weakened, omitted, or broadened upstream intent.
4. Do red test items cover the task quality risks before implementation work?
   Expected output: Find missing or under-specified red test coverage.
5. Does the checklist sufficiently cover the plan requirement that the guidance
   relocation plan pattern is represented as a regression case?

Also check whether the checklist can proceed as-is, should be reordered, or
needs additional items before execution.

## Out Of Scope
- Do not perform the TODO work itself.
- Do not implement tests or fixtures.
- Do not judge post-write verification, commit readiness, or push readiness.
- Do not treat generated main preanalysis as authoritative.

## Finding Policy
Return findings only for substantive task-quality risks.

Use these severities:
- `ERROR`: Execution should not proceed until fixed.
- `WARN`: Execution may proceed only after explicit acceptance or minor correction.
- `INFO`: Non-blocking observation.

If there are no substantive findings, return an empty findings list and state
that the checklist may proceed.

## Output Contract
Respond as YAML with this shape:

```yaml
findings:
  - id: TQ-001
    severity: ERROR|WARN|INFO
    summary: short summary
    evidence: specific item IDs or source text
    recommendation: concrete next action
decision:
  may_proceed: true|false
  reason: concise reason
  required_changes:
    - change, if any
```


# Output contract
Return YAML only.
The response must include the top-level key findings.
Additional top-level keys are allowed only when the criteria explicitly defines them.
Do not add wrapper keys such as review, result, metadata, or summary.
Do not wrap the YAML in Markdown code fences.
Do not write prose before or after the YAML.

Each finding must include these keys:
- severity
- target_location
- description
- rationale

Use only these severity values:
- CRITICAL
- ERROR
- WARN
- INFO

If there are no findings and the criteria does not define additional top-level keys, return exactly:

findings: []

Valid shape example:

findings:
  - severity: WARN
    target_location: "path or section"
    description: "Plain finding summary"
    rationale: "Why this matters"

# Prior findings
なし

# Target path
.reviewcompass/evidence/review-materials/2026-06-23-plan-materialization-regression-fixtures/review-materials.yaml

# Target document
schema_version: task-quality-review-materials-v1
review_target:
  backlog_id: todo-2026-06-23-plan-materialization-regression-fixtures
  checklist_id: checklist-todo-2026-06-23-plan-materialization-regression-fixtures
source_materials:
- id: backlog_todo
  path: .reviewcompass/backlog/todos/todo-2026-06-23-plan-materialization-regression-fixtures.yaml
  content_mode: full_text
  content: "schema_version: reviewcompass-backlog-item-v1\nid: todo-2026-06-23-plan-materialization-regression-fixtures\n\
    kind: todo\ntitle: Add plan materialization regression fixtures\nstatus: candidate\n\
    source_unit_id: main-side-conversation\ncreated_at: '2026-06-23T13:03:40.001805+00:00'\n\
    index_path: .reviewcompass/backlog/index.yaml\nprovenance:\n  created_by: llm\n\
    \  source_ref: .reviewcompass/backlog/plans/plan-2026-06-23-plan-todo-checklist-materialization.yaml#PTC-5\n\
    \  reason: Materialize the remaining PTC-5 slice so all plan slices have TODO/checklist\n\
    \    coverage.\ndecisions: []\nsource_plan_id: plan-2026-06-23-plan-todo-checklist-materialization\n\
    source_plan_path: .reviewcompass/backlog/plans/plan-2026-06-23-plan-todo-checklist-materialization.yaml\n\
    source_plan_slice:\n  phase_id: PTC-5\n  title: Tests and regression fixtures\n\
    summary: 'Add regression tests and fixtures that prove plan materialization coverage\n\
    \  remains visible when only part of a plan has been expanded into TODOs and checklists.\n\
    \n  '\ntasks:\n- id: PTC-5A\n  title: Add tests for a plan with one completed\
    \ slice and remaining unmaterialized\n    slices\n- id: PTC-5B\n  title: Add tests\
    \ that plan-todo-bridge returns next TODO candidates\n- id: PTC-5C\n  title: Add\
    \ tests that audit detects stale or missing execution_slices links\nacceptance_criteria:\n\
    - The guidance relocation plan pattern is covered as a regression case.\nred_tests:\n\
    - id: PTC-RT-1\n  title: Partial plan materialization is visible\n  expected:\
    \ 'A plan with GRC-1 completed and GRC-2..GRC-6 not_materialized reports\n   \
    \ partial coverage, not plan completion.\n\n    '\n- id: PTC-RT-2\n  title: Next\
    \ unmaterialized slice is recommended\n  expected: 'plan-todo-bridge returns GRC-2\
    \ as a next materialization candidate when\n    GRC-1 is completed.\n\n    '\n\
    - id: PTC-RT-3\n  title: Work cannot silently start from an unmaterialized slice\n\
    \  expected: 'Attempting to start implementation work for a slice without TODO/checklist\n\
    \    returns a stop reason or explicit decision requirement.\n\n    '\n- id: PTC-RT-4\n\
    \  title: Stale links are detected\n  expected: 'execution_slices entries pointing\
    \ to missing TODO/checklist/evidence\n    paths are reported by audit.\n\n   \
    \ '\nnon_goals:\n- Implement unrelated workflow changes outside the PTC-5 regression\
    \ coverage.\n- Rework the plan materialization contract already completed in PTC-1\
    \ through PTC-4.\n"
- id: runtime_checklist
  path: .reviewcompass/runtime/work-units/checklists/checklist-todo-2026-06-23-plan-materialization-regression-fixtures.yaml
  content_mode: full_text
  content: "schema_version: work-checklist-v1\nchecklist_id: checklist-todo-2026-06-23-plan-materialization-regression-fixtures\n\
    unit_id: main-side-conversation\ntitle: Add plan materialization regression fixtures\n\
    status: active\ncreated_at: '2026-06-23T13:03:44.797644+00:00'\nprovenance:\n\
    \  created_by: llm\n  source_ref: .reviewcompass/backlog/todos/todo-2026-06-23-plan-materialization-regression-fixtures.yaml\n\
    \  reason: backlog TODO から runtime checklist を機械生成する\nitems:\n- id: PTC-5A\n \
    \ title: Add tests for a plan with one completed slice and remaining unmaterialized\n\
    \    slices\n  status: pending\n  checked: false\n  child_checklist_id: null\n\
    - id: PTC-5B\n  title: Add tests that plan-todo-bridge returns next TODO candidates\n\
    \  status: pending\n  checked: false\n  child_checklist_id: null\n- id: PTC-5C\n\
    \  title: Add tests that audit detects stale or missing execution_slices links\n\
    \  status: pending\n  checked: false\n  child_checklist_id: null\n- id: PTC-RT-1\n\
    \  title: Partial plan materialization is visible\n  status: pending\n  checked:\
    \ false\n  child_checklist_id: null\n- id: PTC-RT-2\n  title: Next unmaterialized\
    \ slice is recommended\n  status: pending\n  checked: false\n  child_checklist_id:\
    \ null\n- id: PTC-RT-3\n  title: Work cannot silently start from an unmaterialized\
    \ slice\n  status: pending\n  checked: false\n  child_checklist_id: null\n- id:\
    \ PTC-RT-4\n  title: Stale links are detected\n  status: pending\n  checked: false\n\
    \  child_checklist_id: null\nsource_backlog_item_id: todo-2026-06-23-plan-materialization-regression-fixtures\n\
    source_backlog_path: .reviewcompass/backlog/todos/todo-2026-06-23-plan-materialization-regression-fixtures.yaml\n\
    progress:\n  total: 7\n  done: 0\n  active: 0\n  pending: 7\n  blocked: 0\n  active_item_ids:\
    \ []\n  blocked_item_ids: []\n"
audit_result:
  verdict: OK
  reasons: []
  warnings:
  - 'red test items appear after implementation items: PTC-RT-1, PTC-RT-2, PTC-RT-3,
    PTC-RT-4'
  quality:
    expected_count: 7
    actual_count: 7
    missing_item_ids: []
    missing_red_test_item_ids: []
    extra_item_ids: []
    duplicate_item_ids: []
    empty_title_item_ids: []
    ordering_warning_item_ids:
    - PTC-RT-1
    - PTC-RT-2
    - PTC-RT-3
    - PTC-RT-4
    source_backlog_item_id: todo-2026-06-23-plan-materialization-regression-fixtures
    source_backlog_path: .reviewcompass/backlog/todos/todo-2026-06-23-plan-materialization-regression-fixtures.yaml
  item:
    schema_version: reviewcompass-backlog-item-v1
    id: todo-2026-06-23-plan-materialization-regression-fixtures
    kind: todo
    title: Add plan materialization regression fixtures
    status: candidate
    source_unit_id: main-side-conversation
    created_at: '2026-06-23T13:03:40.001805+00:00'
    index_path: .reviewcompass/backlog/index.yaml
    provenance:
      created_by: llm
      source_ref: .reviewcompass/backlog/plans/plan-2026-06-23-plan-todo-checklist-materialization.yaml#PTC-5
      reason: Materialize the remaining PTC-5 slice so all plan slices have TODO/checklist
        coverage.
    decisions: []
    source_plan_id: plan-2026-06-23-plan-todo-checklist-materialization
    source_plan_path: .reviewcompass/backlog/plans/plan-2026-06-23-plan-todo-checklist-materialization.yaml
    source_plan_slice:
      phase_id: PTC-5
      title: Tests and regression fixtures
    summary: 'Add regression tests and fixtures that prove plan materialization coverage
      remains visible when only part of a plan has been expanded into TODOs and checklists.

      '
    tasks:
    - id: PTC-5A
      title: Add tests for a plan with one completed slice and remaining unmaterialized
        slices
    - id: PTC-5B
      title: Add tests that plan-todo-bridge returns next TODO candidates
    - id: PTC-5C
      title: Add tests that audit detects stale or missing execution_slices links
    acceptance_criteria:
    - The guidance relocation plan pattern is covered as a regression case.
    red_tests:
    - id: PTC-RT-1
      title: Partial plan materialization is visible
      expected: 'A plan with GRC-1 completed and GRC-2..GRC-6 not_materialized reports
        partial coverage, not plan completion.

        '
    - id: PTC-RT-2
      title: Next unmaterialized slice is recommended
      expected: 'plan-todo-bridge returns GRC-2 as a next materialization candidate
        when GRC-1 is completed.

        '
    - id: PTC-RT-3
      title: Work cannot silently start from an unmaterialized slice
      expected: 'Attempting to start implementation work for a slice without TODO/checklist
        returns a stop reason or explicit decision requirement.

        '
    - id: PTC-RT-4
      title: Stale links are detected
      expected: 'execution_slices entries pointing to missing TODO/checklist/evidence
        paths are reported by audit.

        '
    non_goals:
    - Implement unrelated workflow changes outside the PTC-5 regression coverage.
    - Rework the plan materialization contract already completed in PTC-1 through
      PTC-4.
  checklist:
    schema_version: work-checklist-v1
    checklist_id: checklist-todo-2026-06-23-plan-materialization-regression-fixtures
    unit_id: main-side-conversation
    title: Add plan materialization regression fixtures
    status: active
    created_at: '2026-06-23T13:03:44.797644+00:00'
    provenance:
      created_by: llm
      source_ref: .reviewcompass/backlog/todos/todo-2026-06-23-plan-materialization-regression-fixtures.yaml
      reason: backlog TODO から runtime checklist を機械生成する
    items:
    - id: PTC-5A
      title: Add tests for a plan with one completed slice and remaining unmaterialized
        slices
      status: pending
      checked: false
      child_checklist_id: null
    - id: PTC-5B
      title: Add tests that plan-todo-bridge returns next TODO candidates
      status: pending
      checked: false
      child_checklist_id: null
    - id: PTC-5C
      title: Add tests that audit detects stale or missing execution_slices links
      status: pending
      checked: false
      child_checklist_id: null
    - id: PTC-RT-1
      title: Partial plan materialization is visible
      status: pending
      checked: false
      child_checklist_id: null
    - id: PTC-RT-2
      title: Next unmaterialized slice is recommended
      status: pending
      checked: false
      child_checklist_id: null
    - id: PTC-RT-3
      title: Work cannot silently start from an unmaterialized slice
      status: pending
      checked: false
      child_checklist_id: null
    - id: PTC-RT-4
      title: Stale links are detected
      status: pending
      checked: false
      child_checklist_id: null
    source_backlog_item_id: todo-2026-06-23-plan-materialization-regression-fixtures
    source_backlog_path: .reviewcompass/backlog/todos/todo-2026-06-23-plan-materialization-regression-fixtures.yaml
    progress:
      total: 7
      done: 0
      active: 0
      pending: 7
      blocked: 0
      active_item_ids: []
      blocked_item_ids: []
  path: .reviewcompass/runtime/work-units/checklists/checklist-todo-2026-06-23-plan-materialization-regression-fixtures.yaml
main_preanalysis:
  role: main_llm_preanalysis
  status: mechanically_seeded
  data_sources:
  - backlog:todo-2026-06-23-plan-materialization-regression-fixtures
  - checklist:checklist-todo-2026-06-23-plan-materialization-regression-fixtures
  - task-quality-check audit result
  observations:
  - Checklist covers 7 actual items for 7 backlog-derived items.
  - 'Ordering warnings: PTC-RT-1, PTC-RT-2, PTC-RT-3, PTC-RT-4'
  reviewer_instruction: Treat this preanalysis as a hypothesis to inspect, not as
    an answer to copy.
review_questions:
- id: granularity
  question: Are checklist items concrete, non-overlapping, and sized for execution?
  expected_output: Find missing granularity risks with item IDs and evidence.
- id: ordering
  question: Is the checklist order suitable for TDD and review-before-implementation
    flow?
  expected_output: Find ordering risks without treating warnings as automatic failure.
- id: upstream_connection
  question: Does the checklist preserve the source TODO intent and stated scope?
  expected_output: Find weakened, omitted, or broadened upstream intent.
- id: red_test_sufficiency
  question: Do red test items cover the task quality risks before implementation work?
  expected_output: Find missing or under-specified red test coverage.
review_result_contract:
  roles:
  - primary
  - adversarial
  - judgment
  paths:
    prompt_materials: .reviewcompass/evidence/review-materials/2026-06-23-plan-materialization-regression-fixtures/review-materials.yaml
    review_run_dir: .reviewcompass/evidence/task-quality-review-runs/run
    prompts_dir: .reviewcompass/evidence/task-quality-review-runs/run/prompts
    raw_results_dir: .reviewcompass/evidence/task-quality-review-runs/run/raw-results
    normalized_results_dir: .reviewcompass/evidence/task-quality-review-runs/run/normalized-results
    triage_decision_path: .reviewcompass/evidence/task-quality-review-runs/run/triage-decision.yaml
    summary_path: .reviewcompass/evidence/task-quality-review-runs/run/review-summary.yaml
decision_boundary:
  mechanical_gate: audit_result.verdict must be OK
  blocking_finding_levels:
  - critical
  - major
  review_output_does_not_authorize_changes: true
  accepted_when:
  - audit_result.verdict == OK
  - no unresolved critical/major findings
  - judgment role does not request changes
sensitive_information_check:
  status: not_required_for_local_materialization
  reason: materials are generated locally before any API call

