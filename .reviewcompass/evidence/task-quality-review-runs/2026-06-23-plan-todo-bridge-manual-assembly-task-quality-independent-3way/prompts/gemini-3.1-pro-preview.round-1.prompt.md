prompt_id: gemini_review
provider: gemini-api
model_id: gemini-3.1-pro-preview

# Task
Review the target document for the requested phase and criteria.

# Phase
task_quality_review

# Criteria
# Task Quality Review Criteria: Reduce manual assembly in plan to TODO bridge

## Review Task
Review whether the backlog TODO and runtime checklist for `todo-2026-06-23-plan-todo-bridge-manual-assembly` / `checklist-todo-2026-06-23-plan-todo-bridge-manual-assembly` are safe to use as the execution checklist after `task-quality-check audit` returned `OK`.

Task-quality warnings:

- `red test items appear after implementation items: PTB-RT-1, PTB-RT-2`

The review should decide whether any warning is a blocking task-quality issue, and identify missing checklist or TODO quality defects that would make execution unsafe.

## Prompt Construction Basis
- This criteria document is mechanically generated from task-quality review materials.
- The prompt follows the established three-review practice: material review, independent questions, explicit scope, sensitive-information check, and YAML result contract.
- Treat main preanalysis in the materials as a hypothesis to inspect, not as an answer to copy.

## User Review Requirements
- WARN from task-quality-check should be reviewed by API, not bypassed by local judgment.
- Review the generated review materials and judge whether the TODO/checklist may proceed.
- Do not authorize commit, push, file moves, or completion of the work.

## Review Target
The target file is `.reviewcompass/evidence/review-materials/2026-06-23-plan-todo-bridge-manual-assembly-task-quality/review-materials.yaml`.

It contains:
- The backlog TODO full text.
- The runtime checklist full text.
- The task-quality audit result.
- Main preanalysis generated from the audit.
- Review questions and decision boundaries.

## Required Checks
1. Are checklist items concrete, non-overlapping, and sized for execution? Expected output: Find missing granularity risks with item IDs and evidence.
2. Is the checklist order suitable for TDD and review-before-implementation flow? Expected output: Find ordering risks without treating warnings as automatic failure.
3. Does the checklist preserve the source TODO intent and stated scope? Expected output: Find weakened, omitted, or broadened upstream intent.
4. Do red test items cover the task quality risks before implementation work? Expected output: Find missing or under-specified red test coverage.

Also check whether the checklist can proceed as-is, should be reordered, or needs additional items before execution.

## Out Of Scope
- Do not perform the TODO work itself.
- Do not propose file moves, path deletions, or consumer reference updates unless the TODO explicitly scopes them.
- Do not judge post-write verification, commit readiness, or push readiness.
- Do not treat generated main preanalysis as authoritative.

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
.reviewcompass/evidence/review-materials/2026-06-23-plan-todo-bridge-manual-assembly-task-quality/review-materials.yaml

# Target document
schema_version: task-quality-review-materials-v1
review_target:
  backlog_id: todo-2026-06-23-plan-todo-bridge-manual-assembly
  checklist_id: checklist-todo-2026-06-23-plan-todo-bridge-manual-assembly
source_materials:
- id: backlog_todo
  path: .reviewcompass/backlog/todos/todo-2026-06-23-plan-todo-bridge-manual-assembly.yaml
  content_mode: full_text
  content: "schema_version: reviewcompass-backlog-item-v1\nid: todo-2026-06-23-plan-todo-bridge-manual-assembly\n\
    kind: todo\ntitle: Reduce manual assembly in plan to TODO bridge\nstatus: candidate\n\
    source_unit_id: maintenance-2026-06-23-guidance-relocation-inventory\ncreated_at:\
    \ '2026-06-23T09:26:45.388681+00:00'\nindex_path: .reviewcompass/backlog/index.yaml\n\
    provenance:\n  created_by: llm\n  source_ref: conversation:user:LM手組み箇所を整理して、実作業前の改善対象にする\n\
    \  reason: guidance relocation inventory 実作業前に、plan-todo-bridge から TODO/checklist/review\n\
    \    へ進む流れの LLM 手組み箇所を改善対象化する\ndecisions: []\nsummary: 'plan-todo-bridge から TODO\
    \ / checklist / task-quality review へ進む流れで、\n\n  LLM が手で組み立てている箇所を改善対象として明示する。\n\
    \n  実作業に入る前に、どこまでを機械化し、どこを明示ゲートとして残すかを整理する。\n\n  '\nproblem_statement:\n- plan-todo-bridge\
    \ は plan と TODO の接続有無を確認できるが、plan slice から TODO body を生成する処理はまだ機械化されていない。\n- TODO\
    \ body の task 分解、red test、acceptance criteria 反映が LLM 手組みに残っている。\n- task-quality\
    \ review criteria の作成が LLM 手組みに残っている。\n- task-quality review の variant 選択が operation\
    \ default または明示ゲートとして固定されていない。\n- API review 後の checklist / TODO 反映が、所見ごとの機械的な\
    \ patch plan ではなく LLM 判断に寄っている。\nobserved_manual_steps:\n- id: PTB-MANUAL-1\n\
    \  title: Select source plan and slice for execution\n  current_state: LLM が TODO_NEXT_SESSION\
    \ と plan 一覧から対象 plan / phase を選んでいる。\n  desired_state: 候補選択理由を機械可読に記録し、複数候補時は停止または利用者確認にする。\n\
    - id: PTB-MANUAL-2\n  title: Assemble TODO body from plan slice\n  current_state:\
    \ LLM が body-file YAML を作成し、task split / red_tests / non_goals を手で組んでいる。\n  desired_state:\
    \ plan slice から TODO body draft を生成する CLI、または差分確認ゲートを用意する。\n- id: PTB-MANUAL-3\n\
    \  title: Build task-quality API review criteria\n  current_state: LLM が review-criteria.md\
    \ を手で作成している。\n  desired_state: task-quality review materials から criteria draft\
    \ を生成し、path-only /\n    複数判断詰め込み / main preanalysis 省略を検査する。\n- id: PTB-MANUAL-4\n\
    \  title: Select task-quality API review variant\n  current_state: LLM が run_review\
    \ の variant を選んでいる。\n  desired_state: config/api-settings.yaml の operation_defaults\
    \ か、明示停止ゲートで variant\n    と role assignment を確定する。\n- id: PTB-MANUAL-5\n  title:\
    \ Apply review findings back to TODO and checklist\n  current_state: LLM が所見を読んで\
    \ TODO / runtime checklist を直接編集している。\n  desired_state: triage 決定、patch 対象、反映済み監査を対応づける記録を残す。\n\
    implementation_plan:\n  phases:\n  - id: PTB-1\n    title: Manual assembly inventory\
    \ and boundary contract\n    tasks:\n    - id: PTB-1A\n      title: Record every\
    \ manual step in plan-to-TODO-to-review flow\n    - id: PTB-1B\n      title: Classify\
    \ each step as mechanize, explicit gate, or acceptable LLM judgment\n    - id:\
    \ PTB-1C\n      title: Define required evidence for each remaining LLM judgment\n\
    \  - id: PTB-2\n    title: Mechanization hooks\n    tasks:\n    - id: PTB-2A\n\
    \      title: Add or plan a CLI path for plan slice to TODO body draft generation\n\
    \    - id: PTB-2B\n      title: Add or plan task-quality criteria draft generation\n\
    \    - id: PTB-2C\n      title: Add or plan task-quality review variant default\
    \ resolution\n  - id: PTB-3\n    title: Pre-work gate\n    tasks:\n    - id: PTB-3A\n\
    \      title: Ensure guidance relocation inventory work does not begin until this\
    \ boundary\n        is accepted or deferred\nacceptance_criteria:\n- LLM 手組み箇所が一覧化され、各項目に\
    \ mechanize / explicit-gate / acceptable-llm-judgment の分類がある。\n- plan slice から\
    \ TODO body を作る箇所について、機械化するか明示確認ゲートにするかが決まっている。\n- task-quality review criteria\
    \ と variant 選択について、機械化するか明示確認ゲートにするかが決まっている。\n- inventory 実作業を開始する前に、この TODO を先に実行するか\
    \ defer するかを判断できる。\nred_tests:\n- id: PTB-RT-1\n  title: Manual TODO body assembly\
    \ is visible before execution\n  expected: plan-todo-bridge 由来の TODO 作成前に、TODO\
    \ body draft が機械生成か LLM 手組みかを証跡として確認できる。\n- id: PTB-RT-2\n  title: Task-quality\
    \ review setup does not rely on hidden variant choice\n  expected: task-quality\
    \ review 実行前に variant と role assignment が operation default\n    または明示ゲートで確認できる。\n\
    non_goals:\n- guidance relocation inventory table の作成。\n- docs/operations / docs/disciplines\
    \ のファイル移動。\n- すべての自然言語判断の完全自動化。\n"
- id: runtime_checklist
  path: .reviewcompass/runtime/work-units/checklists/checklist-todo-2026-06-23-plan-todo-bridge-manual-assembly.yaml
  content_mode: full_text
  content: "schema_version: work-checklist-v1\nchecklist_id: checklist-todo-2026-06-23-plan-todo-bridge-manual-assembly\n\
    unit_id: maintenance-2026-06-23-plan-todo-bridge-manual-assembly\ntitle: Reduce\
    \ manual assembly in plan to TODO bridge\nstatus: active\ncreated_at: '2026-06-23T09:26:50.767099+00:00'\n\
    provenance:\n  created_by: llm\n  source_ref: .reviewcompass/backlog/todos/todo-2026-06-23-plan-todo-bridge-manual-assembly.yaml\n\
    \  reason: backlog TODO から runtime checklist を機械生成する\nitems:\n- id: PTB-1A\n \
    \ title: Record every manual step in plan-to-TODO-to-review flow\n  status: pending\n\
    \  checked: false\n  child_checklist_id: null\n- id: PTB-1B\n  title: Classify\
    \ each step as mechanize, explicit gate, or acceptable LLM judgment\n  status:\
    \ pending\n  checked: false\n  child_checklist_id: null\n- id: PTB-1C\n  title:\
    \ Define required evidence for each remaining LLM judgment\n  status: pending\n\
    \  checked: false\n  child_checklist_id: null\n- id: PTB-2A\n  title: Add or plan\
    \ a CLI path for plan slice to TODO body draft generation\n  status: pending\n\
    \  checked: false\n  child_checklist_id: null\n- id: PTB-2B\n  title: Add or plan\
    \ task-quality criteria draft generation\n  status: pending\n  checked: false\n\
    \  child_checklist_id: null\n- id: PTB-2C\n  title: Add or plan task-quality review\
    \ variant default resolution\n  status: pending\n  checked: false\n  child_checklist_id:\
    \ null\n- id: PTB-3A\n  title: Ensure guidance relocation inventory work does\
    \ not begin until this boundary\n    is accepted or deferred\n  status: pending\n\
    \  checked: false\n  child_checklist_id: null\n- id: PTB-RT-1\n  title: Manual\
    \ TODO body assembly is visible before execution\n  status: pending\n  checked:\
    \ false\n  child_checklist_id: null\n- id: PTB-RT-2\n  title: Task-quality review\
    \ setup does not rely on hidden variant choice\n  status: pending\n  checked:\
    \ false\n  child_checklist_id: null\nsource_backlog_item_id: todo-2026-06-23-plan-todo-bridge-manual-assembly\n\
    source_backlog_path: .reviewcompass/backlog/todos/todo-2026-06-23-plan-todo-bridge-manual-assembly.yaml\n\
    progress:\n  total: 9\n  done: 0\n  active: 0\n  pending: 9\n  blocked: 0\n  active_item_ids:\
    \ []\n  blocked_item_ids: []\n"
audit_result:
  verdict: OK
  reasons: []
  warnings:
  - 'red test items appear after implementation items: PTB-RT-1, PTB-RT-2'
  quality:
    expected_count: 9
    actual_count: 9
    missing_item_ids: []
    missing_red_test_item_ids: []
    extra_item_ids: []
    duplicate_item_ids: []
    empty_title_item_ids: []
    ordering_warning_item_ids:
    - PTB-RT-1
    - PTB-RT-2
    source_backlog_item_id: todo-2026-06-23-plan-todo-bridge-manual-assembly
    source_backlog_path: .reviewcompass/backlog/todos/todo-2026-06-23-plan-todo-bridge-manual-assembly.yaml
  item:
    schema_version: reviewcompass-backlog-item-v1
    id: todo-2026-06-23-plan-todo-bridge-manual-assembly
    kind: todo
    title: Reduce manual assembly in plan to TODO bridge
    status: candidate
    source_unit_id: maintenance-2026-06-23-guidance-relocation-inventory
    created_at: '2026-06-23T09:26:45.388681+00:00'
    index_path: .reviewcompass/backlog/index.yaml
    provenance:
      created_by: llm
      source_ref: conversation:user:LM手組み箇所を整理して、実作業前の改善対象にする
      reason: guidance relocation inventory 実作業前に、plan-todo-bridge から TODO/checklist/review
        へ進む流れの LLM 手組み箇所を改善対象化する
    decisions: []
    summary: 'plan-todo-bridge から TODO / checklist / task-quality review へ進む流れで、

      LLM が手で組み立てている箇所を改善対象として明示する。

      実作業に入る前に、どこまでを機械化し、どこを明示ゲートとして残すかを整理する。

      '
    problem_statement:
    - plan-todo-bridge は plan と TODO の接続有無を確認できるが、plan slice から TODO body を生成する処理はまだ機械化されていない。
    - TODO body の task 分解、red test、acceptance criteria 反映が LLM 手組みに残っている。
    - task-quality review criteria の作成が LLM 手組みに残っている。
    - task-quality review の variant 選択が operation default または明示ゲートとして固定されていない。
    - API review 後の checklist / TODO 反映が、所見ごとの機械的な patch plan ではなく LLM 判断に寄っている。
    observed_manual_steps:
    - id: PTB-MANUAL-1
      title: Select source plan and slice for execution
      current_state: LLM が TODO_NEXT_SESSION と plan 一覧から対象 plan / phase を選んでいる。
      desired_state: 候補選択理由を機械可読に記録し、複数候補時は停止または利用者確認にする。
    - id: PTB-MANUAL-2
      title: Assemble TODO body from plan slice
      current_state: LLM が body-file YAML を作成し、task split / red_tests / non_goals
        を手で組んでいる。
      desired_state: plan slice から TODO body draft を生成する CLI、または差分確認ゲートを用意する。
    - id: PTB-MANUAL-3
      title: Build task-quality API review criteria
      current_state: LLM が review-criteria.md を手で作成している。
      desired_state: task-quality review materials から criteria draft を生成し、path-only
        / 複数判断詰め込み / main preanalysis 省略を検査する。
    - id: PTB-MANUAL-4
      title: Select task-quality API review variant
      current_state: LLM が run_review の variant を選んでいる。
      desired_state: config/api-settings.yaml の operation_defaults か、明示停止ゲートで variant
        と role assignment を確定する。
    - id: PTB-MANUAL-5
      title: Apply review findings back to TODO and checklist
      current_state: LLM が所見を読んで TODO / runtime checklist を直接編集している。
      desired_state: triage 決定、patch 対象、反映済み監査を対応づける記録を残す。
    implementation_plan:
      phases:
      - id: PTB-1
        title: Manual assembly inventory and boundary contract
        tasks:
        - id: PTB-1A
          title: Record every manual step in plan-to-TODO-to-review flow
        - id: PTB-1B
          title: Classify each step as mechanize, explicit gate, or acceptable LLM
            judgment
        - id: PTB-1C
          title: Define required evidence for each remaining LLM judgment
      - id: PTB-2
        title: Mechanization hooks
        tasks:
        - id: PTB-2A
          title: Add or plan a CLI path for plan slice to TODO body draft generation
        - id: PTB-2B
          title: Add or plan task-quality criteria draft generation
        - id: PTB-2C
          title: Add or plan task-quality review variant default resolution
      - id: PTB-3
        title: Pre-work gate
        tasks:
        - id: PTB-3A
          title: Ensure guidance relocation inventory work does not begin until this
            boundary is accepted or deferred
    acceptance_criteria:
    - LLM 手組み箇所が一覧化され、各項目に mechanize / explicit-gate / acceptable-llm-judgment の分類がある。
    - plan slice から TODO body を作る箇所について、機械化するか明示確認ゲートにするかが決まっている。
    - task-quality review criteria と variant 選択について、機械化するか明示確認ゲートにするかが決まっている。
    - inventory 実作業を開始する前に、この TODO を先に実行するか defer するかを判断できる。
    red_tests:
    - id: PTB-RT-1
      title: Manual TODO body assembly is visible before execution
      expected: plan-todo-bridge 由来の TODO 作成前に、TODO body draft が機械生成か LLM 手組みかを証跡として確認できる。
    - id: PTB-RT-2
      title: Task-quality review setup does not rely on hidden variant choice
      expected: task-quality review 実行前に variant と role assignment が operation default
        または明示ゲートで確認できる。
    non_goals:
    - guidance relocation inventory table の作成。
    - docs/operations / docs/disciplines のファイル移動。
    - すべての自然言語判断の完全自動化。
  checklist:
    schema_version: work-checklist-v1
    checklist_id: checklist-todo-2026-06-23-plan-todo-bridge-manual-assembly
    unit_id: maintenance-2026-06-23-plan-todo-bridge-manual-assembly
    title: Reduce manual assembly in plan to TODO bridge
    status: active
    created_at: '2026-06-23T09:26:50.767099+00:00'
    provenance:
      created_by: llm
      source_ref: .reviewcompass/backlog/todos/todo-2026-06-23-plan-todo-bridge-manual-assembly.yaml
      reason: backlog TODO から runtime checklist を機械生成する
    items:
    - id: PTB-1A
      title: Record every manual step in plan-to-TODO-to-review flow
      status: pending
      checked: false
      child_checklist_id: null
    - id: PTB-1B
      title: Classify each step as mechanize, explicit gate, or acceptable LLM judgment
      status: pending
      checked: false
      child_checklist_id: null
    - id: PTB-1C
      title: Define required evidence for each remaining LLM judgment
      status: pending
      checked: false
      child_checklist_id: null
    - id: PTB-2A
      title: Add or plan a CLI path for plan slice to TODO body draft generation
      status: pending
      checked: false
      child_checklist_id: null
    - id: PTB-2B
      title: Add or plan task-quality criteria draft generation
      status: pending
      checked: false
      child_checklist_id: null
    - id: PTB-2C
      title: Add or plan task-quality review variant default resolution
      status: pending
      checked: false
      child_checklist_id: null
    - id: PTB-3A
      title: Ensure guidance relocation inventory work does not begin until this boundary
        is accepted or deferred
      status: pending
      checked: false
      child_checklist_id: null
    - id: PTB-RT-1
      title: Manual TODO body assembly is visible before execution
      status: pending
      checked: false
      child_checklist_id: null
    - id: PTB-RT-2
      title: Task-quality review setup does not rely on hidden variant choice
      status: pending
      checked: false
      child_checklist_id: null
    source_backlog_item_id: todo-2026-06-23-plan-todo-bridge-manual-assembly
    source_backlog_path: .reviewcompass/backlog/todos/todo-2026-06-23-plan-todo-bridge-manual-assembly.yaml
    progress:
      total: 9
      done: 0
      active: 0
      pending: 9
      blocked: 0
      active_item_ids: []
      blocked_item_ids: []
  path: .reviewcompass/runtime/work-units/checklists/checklist-todo-2026-06-23-plan-todo-bridge-manual-assembly.yaml
main_preanalysis:
  role: main_llm_preanalysis
  status: mechanically_seeded
  data_sources:
  - backlog:todo-2026-06-23-plan-todo-bridge-manual-assembly
  - checklist:checklist-todo-2026-06-23-plan-todo-bridge-manual-assembly
  - task-quality-check audit result
  observations:
  - Checklist covers 9 actual items for 9 backlog-derived items.
  - 'Ordering warnings: PTB-RT-1, PTB-RT-2'
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
    prompt_materials: .reviewcompass/evidence/review-materials/2026-06-23-plan-todo-bridge-manual-assembly-task-quality/review-materials.yaml
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

