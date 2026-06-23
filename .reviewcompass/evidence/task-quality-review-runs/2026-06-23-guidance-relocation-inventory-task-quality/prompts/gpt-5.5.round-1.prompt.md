prompt_id: openai_review
provider: openai-api
model_id: gpt-5.5

# Task
Review the target document for the requested phase and criteria.

# Phase
task_quality_review

# Criteria
# Task Quality Review Criteria: Guidance Relocation Inventory

## Review Task
Review whether the backlog TODO and runtime checklist for `todo-2026-06-23-guidance-relocation-inventory` are safe to use as the execution checklist after `task-quality-check audit` returned `OK` with a WARN:

- `red test items appear after implementation items: GRC-RT-1`

The review should decide whether this warning is a blocking task-quality issue, and identify any missing checklist or TODO quality defects that would make execution unsafe.

## User Review Requirements
- WARN from task-quality-check should be reviewed by API, not bypassed by local judgment.
- Review the generated review materials and judge whether the TODO/checklist may proceed.
- Do not authorize commit, push, file moves, or completion of the work.

## Review Target
The target file is `.reviewcompass/evidence/review-materials/2026-06-23-guidance-relocation-inventory-task-quality/review-materials.yaml`.

It contains:
- The backlog TODO full text.
- The runtime checklist full text.
- The task-quality audit result.
- Main preanalysis generated from the audit.
- Review questions and decision boundaries.

## Required Checks
1. Determine whether the WARN about `GRC-RT-1` appearing after implementation items is a blocking issue for this specific inventory-only TODO.
2. Check whether the checklist preserves the source plan slice `GRC-1` and does not broaden scope into file moves, deletion, or consumer reference updates.
3. Check whether each checklist item is concrete enough to execute and verify.
4. Check whether the red-test / acceptance item is sufficient for an inventory/classification-only task.
5. Check whether the checklist can proceed as-is, should be reordered, or needs additional items before execution.

## Out Of Scope
- Do not classify the actual `docs/operations` or `docs/disciplines` files.
- Do not propose file moves, path deletions, or consumer reference updates.
- Do not judge post-write verification, commit readiness, or push readiness.
- Do not treat the generated main preanalysis as authoritative; use it only as a hypothesis.

## Finding Policy
Return findings only for substantive task-quality risks.

Use these severities:
- `ERROR`: Execution should not proceed until fixed.
- `WARN`: Execution may proceed only after explicit acceptance or minor correction.
- `INFO`: Non-blocking observation.

If there are no substantive findings, return an empty findings list and state that the checklist may proceed.

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
.reviewcompass/evidence/review-materials/2026-06-23-guidance-relocation-inventory-task-quality/review-materials.yaml

# Target document
schema_version: task-quality-review-materials-v1
review_target:
  backlog_id: todo-2026-06-23-guidance-relocation-inventory
  checklist_id: checklist-todo-2026-06-23-guidance-relocation-inventory
source_materials:
- id: backlog_todo
  path: .reviewcompass/backlog/todos/todo-2026-06-23-guidance-relocation-inventory.yaml
  content_mode: full_text
  content: "schema_version: reviewcompass-backlog-item-v1\nid: todo-2026-06-23-guidance-relocation-inventory\n\
    kind: todo\ntitle: Create guidance relocation inventory and classification table\n\
    status: candidate\nsource_unit_id: main-completed\ncreated_at: '2026-06-23T09:12:49.197484+00:00'\n\
    index_path: .reviewcompass/backlog/index.yaml\nprovenance:\n  created_by: llm\n\
    \  source_ref: .reviewcompass/backlog/plans/plan-2026-06-23-guidance-relocation-and-docs-classification.yaml\n\
    \  reason: plan GRC-1 をファイル移動なしの inventory / classification 作業として実行対象化する\ndecisions:\
    \ []\nsource_plan_id: plan-2026-06-23-guidance-relocation-and-docs-classification\n\
    source_plan_path: .reviewcompass/backlog/plans/plan-2026-06-23-guidance-relocation-and-docs-classification.yaml\n\
    source_plan_slice:\n  phase_id: GRC-1\n  title: Inventory and classification only\n\
    summary: 'Create an inventory and first-pass classification table for the remaining\n\
    \  docs/operations and docs/disciplines files. Do not move files in this TODO.\n\
    \n  '\nimplementation_plan:\n  phases:\n  - id: GRC-1\n    title: Inventory and\
    \ classification only\n    tasks:\n    - id: GRC-1A\n      title: List all remaining\
    \ docs/operations and docs/disciplines files\n    - id: GRC-1B\n      title: Classify\
    \ each file using the plan classification axes\n    - id: GRC-1C\n      title:\
    \ Record current readers and proposed destination for each file\n    - id: GRC-1D\n\
    \      title: Mark move, keep, and decision-required candidates without moving\
    \ files\nacceptance_criteria:\n- 移動対象、残置対象、判断保留対象が表で確認できる。\n- この段階ではファイル移動をしない。\n\
    non_goals:\n- docs/operations / docs/disciplines のファイル移動。\n- 旧 path 削除。\n- consumer\
    \ reference 更新。\nred_tests:\n- id: GRC-RT-1\n  title: Inventory table exists before\
    \ any move\n  expected: classification table が存在し、対象ファイルごとに classification / current\
    \ readers /\n    proposed destination を持つ\n"
- id: runtime_checklist
  path: .reviewcompass/runtime/work-units/checklists/checklist-todo-2026-06-23-guidance-relocation-inventory.yaml
  content_mode: full_text
  content: "schema_version: work-checklist-v1\nchecklist_id: checklist-todo-2026-06-23-guidance-relocation-inventory\n\
    unit_id: maintenance-2026-06-23-guidance-relocation-inventory\ntitle: Create guidance\
    \ relocation inventory and classification table\nstatus: active\ncreated_at: '2026-06-23T09:12:56.291657+00:00'\n\
    provenance:\n  created_by: llm\n  source_ref: .reviewcompass/backlog/todos/todo-2026-06-23-guidance-relocation-inventory.yaml\n\
    \  reason: backlog TODO から runtime checklist を機械生成する\nitems:\n- id: GRC-1A\n \
    \ title: List all remaining docs/operations and docs/disciplines files\n  status:\
    \ pending\n  checked: false\n  child_checklist_id: null\n- id: GRC-1B\n  title:\
    \ Classify each file using the plan classification axes\n  status: pending\n \
    \ checked: false\n  child_checklist_id: null\n- id: GRC-1C\n  title: Record current\
    \ readers and proposed destination for each file\n  status: pending\n  checked:\
    \ false\n  child_checklist_id: null\n- id: GRC-1D\n  title: Mark move, keep, and\
    \ decision-required candidates without moving files\n  status: pending\n  checked:\
    \ false\n  child_checklist_id: null\n- id: GRC-RT-1\n  title: Inventory table\
    \ exists before any move\n  status: pending\n  checked: false\n  child_checklist_id:\
    \ null\nsource_backlog_item_id: todo-2026-06-23-guidance-relocation-inventory\n\
    source_backlog_path: .reviewcompass/backlog/todos/todo-2026-06-23-guidance-relocation-inventory.yaml\n\
    progress:\n  total: 5\n  done: 0\n  active: 0\n  pending: 5\n  blocked: 0\n  active_item_ids:\
    \ []\n  blocked_item_ids: []\n"
audit_result:
  verdict: OK
  reasons: []
  warnings:
  - 'red test items appear after implementation items: GRC-RT-1'
  quality:
    expected_count: 5
    actual_count: 5
    missing_item_ids: []
    missing_red_test_item_ids: []
    extra_item_ids: []
    duplicate_item_ids: []
    empty_title_item_ids: []
    ordering_warning_item_ids:
    - GRC-RT-1
    source_backlog_item_id: todo-2026-06-23-guidance-relocation-inventory
    source_backlog_path: .reviewcompass/backlog/todos/todo-2026-06-23-guidance-relocation-inventory.yaml
  item:
    schema_version: reviewcompass-backlog-item-v1
    id: todo-2026-06-23-guidance-relocation-inventory
    kind: todo
    title: Create guidance relocation inventory and classification table
    status: candidate
    source_unit_id: main-completed
    created_at: '2026-06-23T09:12:49.197484+00:00'
    index_path: .reviewcompass/backlog/index.yaml
    provenance:
      created_by: llm
      source_ref: .reviewcompass/backlog/plans/plan-2026-06-23-guidance-relocation-and-docs-classification.yaml
      reason: plan GRC-1 をファイル移動なしの inventory / classification 作業として実行対象化する
    decisions: []
    source_plan_id: plan-2026-06-23-guidance-relocation-and-docs-classification
    source_plan_path: .reviewcompass/backlog/plans/plan-2026-06-23-guidance-relocation-and-docs-classification.yaml
    source_plan_slice:
      phase_id: GRC-1
      title: Inventory and classification only
    summary: 'Create an inventory and first-pass classification table for the remaining
      docs/operations and docs/disciplines files. Do not move files in this TODO.

      '
    implementation_plan:
      phases:
      - id: GRC-1
        title: Inventory and classification only
        tasks:
        - id: GRC-1A
          title: List all remaining docs/operations and docs/disciplines files
        - id: GRC-1B
          title: Classify each file using the plan classification axes
        - id: GRC-1C
          title: Record current readers and proposed destination for each file
        - id: GRC-1D
          title: Mark move, keep, and decision-required candidates without moving
            files
    acceptance_criteria:
    - 移動対象、残置対象、判断保留対象が表で確認できる。
    - この段階ではファイル移動をしない。
    non_goals:
    - docs/operations / docs/disciplines のファイル移動。
    - 旧 path 削除。
    - consumer reference 更新。
    red_tests:
    - id: GRC-RT-1
      title: Inventory table exists before any move
      expected: classification table が存在し、対象ファイルごとに classification / current readers
        / proposed destination を持つ
  checklist:
    schema_version: work-checklist-v1
    checklist_id: checklist-todo-2026-06-23-guidance-relocation-inventory
    unit_id: maintenance-2026-06-23-guidance-relocation-inventory
    title: Create guidance relocation inventory and classification table
    status: active
    created_at: '2026-06-23T09:12:56.291657+00:00'
    provenance:
      created_by: llm
      source_ref: .reviewcompass/backlog/todos/todo-2026-06-23-guidance-relocation-inventory.yaml
      reason: backlog TODO から runtime checklist を機械生成する
    items:
    - id: GRC-1A
      title: List all remaining docs/operations and docs/disciplines files
      status: pending
      checked: false
      child_checklist_id: null
    - id: GRC-1B
      title: Classify each file using the plan classification axes
      status: pending
      checked: false
      child_checklist_id: null
    - id: GRC-1C
      title: Record current readers and proposed destination for each file
      status: pending
      checked: false
      child_checklist_id: null
    - id: GRC-1D
      title: Mark move, keep, and decision-required candidates without moving files
      status: pending
      checked: false
      child_checklist_id: null
    - id: GRC-RT-1
      title: Inventory table exists before any move
      status: pending
      checked: false
      child_checklist_id: null
    source_backlog_item_id: todo-2026-06-23-guidance-relocation-inventory
    source_backlog_path: .reviewcompass/backlog/todos/todo-2026-06-23-guidance-relocation-inventory.yaml
    progress:
      total: 5
      done: 0
      active: 0
      pending: 5
      blocked: 0
      active_item_ids: []
      blocked_item_ids: []
  path: .reviewcompass/runtime/work-units/checklists/checklist-todo-2026-06-23-guidance-relocation-inventory.yaml
main_preanalysis:
  role: main_llm_preanalysis
  status: mechanically_seeded
  data_sources:
  - backlog:todo-2026-06-23-guidance-relocation-inventory
  - checklist:checklist-todo-2026-06-23-guidance-relocation-inventory
  - task-quality-check audit result
  observations:
  - Checklist covers 5 actual items for 5 backlog-derived items.
  - 'Ordering warnings: GRC-RT-1'
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
    prompt_materials: .reviewcompass/evidence/review-materials/2026-06-23-guidance-relocation-inventory-task-quality/review-materials.yaml
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

