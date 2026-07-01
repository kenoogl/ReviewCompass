prompt_id: anthropic_review
provider: anthropic-api
model_id: claude-sonnet-4-6

# Task
Review the target document for the requested phase and criteria.

# Phase
post_write_verification

# Criteria
backlog_candidate_routing_reopen_classification_post_write

# Output contract
Return YAML only.
The response must include the top-level key findings.
Additional top-level keys are allowed only when the criteria explicitly defines them.
Do not use review: as a wrapper.
Do not use result:, metadata:, or summary: as wrappers.
Do not wrap the YAML in Markdown code fences.
Do not include ```yaml or any other fence marker.
Do not write explanatory prose before or after the YAML.

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
.reviewcompass/evidence/review-runs/2026-07-01-backlog-candidate-routing-postwrite-r2/review-target.md

# Target document
# Post-write Review Target

criteria_id: backlog_candidate_routing_reopen_classification_post_write
phase: post_write_verification
generated_at: 2026-07-01T03:10:35.001826+00:00

## Change Summary

post-write 所見を受け、候補1の reopen 分類記録で第1過程停止点と現在の第2過程停止点を分け、spec.json の差し戻し範囲と indirect check の確認タイミングを明確化した。

## Review Question

修正後の分類記録が利用者の合意、対象 plan、spec.json 差し戻し、reopen 手続き記録と矛盾せず、重要な欠落や過剰主張がないかを確認してください。

## Target Files

- docs/reviews/reopen-classification-2026-07-01-wm-backlog-candidate-routing.md sha256=acd998e3d0f7304fdc15baa484319887c5bf1b4548bce054baaf67dcebcd4b0f

## Source Materials

### .reviewcompass/backlog/plans/plan-2026-07-01-backlog-entry-lane-routing.yaml

content_mode: full_text
content_sha256: c2c5d07acbfa086a7fa31e6c58521bd5d830cc3578edff5bb12deeac239c559a

```text
schema_version: reviewcompass-backlog-item-v1
id: plan-2026-07-01-backlog-entry-lane-routing
kind: plan
title: Define backlog candidate routing and resilient plan format discipline
status: candidate
plan_level: executable
materialization_required: true
source_unit_id: main-completed
created_at: '2026-07-01T00:00:00+09:00'
index_path: .reviewcompass/backlog/index.yaml
supersedes:
  - .reviewcompass/backlog/plans/plan-2026-07-01-backlog-text-format-resilience.yaml
provenance:
  created_by: llm
  source_ref: conversation:user:採用
  reason: >
    The discussion clarified that backlog is not a work lane or entry point. It
    is a candidate holding area. User-visible work lanes for this discipline are
    SDD workflow, reopen, and maintenance. TODO should not be used as the
    backlog materialization step; maintenance candidates that are small and
    local go directly to checklist, while other candidates are routed to SDD
    workflow or reopen. The older text-format resilience plan is absorbed here
    because plan/checklist format safety must be handled together with backlog
    routing.
summary: >
  Establish a backlog candidate routing discipline and resilient record format:
  backlog holds candidates only, candidates are routed to SDD workflow, reopen,
  or maintenance, TODO is not used as the backlog materialization step, and only
  maintenance work that is small, local, and checklist-ready may proceed
  directly. This plan also absorbs the text-format resilience work so natural
  language fields do not break machine-readable backlog records.
lane_model:
  work_lanes:
    - id: sdd_workflow
      title: SDD workflow
      meaning: >
        The normal requirements, design, tasking, review, and implementation
        workflow. Candidates that need new design, work breakdown, or a new
        product/workflow decision are routed here unless they are clearly reopen
        work.
    - id: reopen
      title: Reopen
      meaning: >
        The lane for reopening completed artifacts, decisions, plans,
        checklists, or implementation outcomes when prior completed work may
        need reconsideration. The exact boundary between SDD workflow and reopen
        requires additional design in this plan.
    - id: maintenance
      title: Maintenance
      meaning: >
        The lane for small, local workflow upkeep that does not change existing
        product intent, completed decisions, or broad process structure. A
        maintenance candidate may proceed directly to checklist when evidence
        can be recorded clearly.
  candidate_holding_area:
    id: backlog
    title: Backlog
    meaning: >
      Backlog is not a work lane and not an execution entry point. It is a place
      to hold candidates until they are routed to SDD workflow, reopen,
      maintenance, deferred, or record-only status.
  procedures_not_work_lanes:
    - id: operation_entry
      title: Operation entry
      meaning: >
        Short user operations such as commit, push, and autonomous execution
        triggers choose an action for the current state, but do not define a
        work lane by themselves.
    - id: verification_post_write
      title: Verification and post-write procedures
      meaning: >
        Checks that arise inside a work lane after changes are made. They do not
        replace SDD workflow, reopen, or maintenance.
    - id: session_handoff
      title: Session and handoff procedures
      meaning: >
        System-level continuity operations such as session records and handoff
        notes. They are not user-visible product work lanes.
routing_model:
  candidate_routes:
    - id: maintenance
      use_when: >
        The candidate is small, local, does not need design or splitting, does
        not alter prior completed decisions, and can be expressed directly as a
        checklist with evidence.
      materialization: checklist
      direct_execution_allowed: true
    - id: sdd_workflow
      use_when: >
        The candidate needs design, work breakdown, new requirements,
        implementation planning, or user/product judgment that is not simply
        reopening a completed artifact. The exact boundary with reopen is part
        of this plan's investigation.
      materialization: sdd_artifacts
      direct_execution_allowed: false
    - id: reopen
      use_when: >
        The candidate may change, invalidate, or reinterpret completed
        artifacts, decisions, checklists, or implementation outcomes. The exact
        boundary with SDD workflow is part of this plan's investigation.
      materialization: reopen_artifacts
      direct_execution_allowed: false
    - id: deferred
      use_when: >
        The candidate is valid but should not be routed yet.
      materialization: none
      direct_execution_allowed: false
    - id: record_only
      use_when: >
        The candidate is useful as a note but does not currently request work.
      materialization: none
      direct_execution_allowed: false
  todo_policy:
    summary: >
      TODO is not used as the backlog materialization step for this discipline.
      Maintenance candidates go directly to checklist. Candidates that cannot be
      expressed directly as maintenance checklist work are routed to SDD workflow
      or reopen instead of being parked in TODO.
format_resilience_model:
  source_absorbed: plan-2026-07-01-backlog-text-format-resilience
  principles:
    - >
      Separate machine-readable metadata from natural-language narrative fields.
    - >
      Use block scalars for long natural-language text, Markdown-like content,
      bullets, colons, and backticks.
    - >
      Run YAML parse and minimal schema checks immediately after creating or
      updating backlog plans, checklists, and index records.
    - >
      Prefer generated or structured update paths over LLM-authored raw YAML
      when a safer tool exists.
current_problem:
  - >
    Backlog has been treated like an executable entry lane, which allows
    candidates to bypass SDD workflow or reopen judgment.
  - >
    The previous plan-to-TODO-to-checklist path creates an extra object that is
    not needed for small maintenance work and can make backlog execution feel
    safer than it is.
  - >
    The boundary between SDD workflow and reopen is not yet precise enough for
    reliable machine routing.
  - >
    Existing implementation may still contain functions, workflow rules, and
    machine processing that assume backlog-to-TODO materialization or backlog as
    an execution lane.
  - >
    Existing backlog TODO files may contain candidates that do not have
    corresponding plan records. Since TODO is no longer the backlog
    materialization step, TODO-only candidates need to be returned to plan
    records, while content already represented in plans needs no duplicate work.
  - >
    Natural-language backlog records can break YAML syntax when long text,
    Markdown notation, colons, or backticks are embedded directly in plain
    scalars.
decisions:
  - id: BELR-D1
    summary: >
      Treat the work lanes for this discipline as SDD workflow, reopen, and
      maintenance.
  - id: BELR-D2
    summary: >
      Treat backlog as a candidate holding area, not a work lane and not an
      execution entry point.
  - id: BELR-D3
    summary: >
      Do not use TODO as the backlog materialization step. Maintenance
      candidates that qualify go directly to checklist; other candidates are
      routed to SDD workflow or reopen.
  - id: BELR-D4
    summary: >
      Direct implementation is allowed only for maintenance candidates that are
      small, local, and checklist-ready.
  - id: BELR-D5
    summary: >
      Treat SDD workflow versus reopen classification as a design target of this
      plan, not as already finalized.
  - id: BELR-D6
    summary: >
      Absorb the text-format resilience plan into this plan and remove the old
      standalone candidate after its requirements are represented here.
  - id: BELR-D7
    summary: >
      Migrate existing TODO-only backlog candidates back to plan records. If the
      same content already exists in a plan, no additional work is required for
      that TODO.
implementation_plan:
  - id: BELR-1
    title: Document backlog as candidate holding area
    goal: >
      Update guidance so backlog is described as a candidate holding area, while
      SDD workflow, reopen, and maintenance are the work lanes.
    deliverables:
      - >
        Guidance names SDD workflow, reopen, and maintenance as the lanes.
      - >
        Guidance states that backlog is not a lane and not an execution entry
        point.
      - >
        Guidance states that operation, verification/post-write, and
        session/handoff are procedures, not lanes.
  - id: BELR-2
    title: Design SDD workflow versus reopen classification
    goal: >
      Investigate and define how candidates that are not maintenance should be
      routed between SDD workflow and reopen.
    deliverables:
      - >
        Classification criteria cover new design, work breakdown, user
        judgment, completed-artifact reopening, and prior-decision impact.
      - >
        Ambiguous cases are documented with expected routing.
      - >
        Machine-readable route values are defined without treating backlog as a
        route to execution.
  - id: BELR-3
    title: Remove TODO from backlog materialization
    goal: >
      Replace backlog-to-TODO assumptions with backlog-candidate routing and
      maintenance-to-checklist materialization.
    deliverables:
      - >
        Operational guidance states that maintenance candidates go directly to
        checklist when they qualify.
      - >
        Guidance states that candidates requiring design, splitting, or user
        judgment route to SDD workflow or reopen.
      - >
        Any remaining TODO dependency is either removed or explicitly justified
        outside this backlog routing discipline.
  - id: BELR-4
    title: Investigate existing implementation impact
    goal: >
      Find and revise implemented functions, workflow rules, and machine
      processing that still assume backlog is an entry lane or TODO is required.
    deliverables:
      - >
        Inventory functions that create, inspect, or enforce plan/TODO/checklist
        materialization.
      - >
        Identify unused functions after TODO removal.
      - >
        Update next-task display, autonomous trigger handling, and commit
        preflight where they conflict with the new discipline.
  - id: BELR-5
    title: Return existing TODO-only candidates to plans
    goal: >
      Clean up the existing backlog TODO directory so TODO-only candidates are
      represented as plan records instead of remaining as standalone backlog
      work.
    deliverables:
      - >
        Inventory existing TODO files and match them against existing plans.
      - >
        Mark TODO content that is already represented in a plan as requiring no
        additional plan creation.
      - >
        Create or update plan records for TODO-only candidates that still
        represent valid backlog candidates.
      - >
        Remove or retire TODO files after their content is represented by plans
        or explicitly determined to need no work.
  - id: BELR-6
    title: Absorb resilient record format rules
    goal: >
      Fold the standalone text-format resilience work into the backlog routing
      discipline.
    deliverables:
      - >
        Natural-language fields use block scalars or structured text fields.
      - >
        Machine-readable route/materialization fields are separate from
        narrative text.
      - >
        Plan/checklist/index updates run YAML parse and minimal schema checks.
      - >
        The superseded text-format resilience plan is removed from plans and
        index after absorption.
  - id: BELR-7
    title: Verify routing and record safety
    goal: >
      Prove the new discipline with focused checks before implementation is
      considered complete.
    deliverables:
      - >
        Tests or audits cover maintenance checklist routing, SDD/reopen routing
        candidates, absence of TODO materialization, and old-text-plan removal.
      - >
        YAML parse/schema checks pass for the updated plan and backlog index.
      - >
        `next --json`, autonomous execution, and commit preflight behavior are
        checked against the revised discipline.
execution_slices:
  - phase_id: BELR-1
    title: Document backlog as candidate holding area
    status: not_materialized
    todo_id: null
    checklist_id: null
  - phase_id: BELR-2
    title: Design SDD workflow versus reopen classification
    status: not_materialized
    todo_id: null
    checklist_id: null
  - phase_id: BELR-3
    title: Remove TODO from backlog materialization
    status: not_materialized
    todo_id: null
    checklist_id: null
  - phase_id: BELR-4
    title: Investigate existing implementation impact
    status: not_materialized
    todo_id: null
    checklist_id: null
  - phase_id: BELR-5
    title: Return existing TODO-only candidates to plans
    status: not_materialized
    todo_id: null
    checklist_id: null
  - phase_id: BELR-6
    title: Absorb resilient record format rules
    status: not_materialized
    todo_id: null
    checklist_id: null
  - phase_id: BELR-7
    title: Verify routing and record safety
    status: not_materialized
    todo_id: null
    checklist_id: null
acceptance_criteria:
  - >
    Backlog is documented as a candidate holding area, not a lane or execution
    entry point.
  - >
    The work lanes are documented as SDD workflow, reopen, and maintenance.
  - >
    Maintenance is the only direct-execution path, and only after a candidate is
    small, local, and checklist-ready.
  - >
    TODO is not required or used as backlog materialization in this discipline.
  - >
    The SDD workflow versus reopen boundary is investigated and represented in
    guidance or machine-readable routing rules.
  - >
    Existing functions, operational rules, and machine processing that assume
    backlog-to-TODO materialization are identified and updated or removed.
  - >
    Existing TODO files are inventoried, and TODO-only candidates are returned
    to plan records while TODO content already represented in plans is treated
    as requiring no duplicate work.
  - >
    Natural-language backlog record fields are resilient to YAML syntax hazards.
  - >
    The superseded text-format resilience plan is removed from the backlog index
    and from the plans directory after its requirements are absorbed.
non_goals:
  - >
    Do not replace or duplicate SDD review stages.
  - >
    Do not treat operation triggers, post-write verification, or session handoff
    as work lanes.
  - >
    Do not preserve TODO as a required backlog materialization object.
  - >
    Do not complete a bulk migration of every historical backlog item in this
    plan unless a later slice explicitly scopes that work.
```

### .reviewcompass/specs/workflow-management/requirements.md

content_mode: full_text
content_sha256: 1de563a12fd422083ad09e78eee6b46641484c5a78efa2cfbd8c40008ed8fe3d

```text
# Requirements Document：workflow-management

## Introduction

`workflow-management` は ReviewCompass における所定手続きの定義と機械強制を担う機能である。先行プロジェクトでは `implementation-governance` と呼ばれ、節ハッシュ・独立再導出パーサ・通過マーカーの後続確認・supersedes リンク等を含む大規模機構として組み上がっていたが、ReviewCompass では計画書 §5.4「軽量化方針」に従い、**思想は継承、実装は 1／10** を目標として再設計する。

計画書 §5.15.6 により機能名を `implementation-governance` → `workflow-management` に改称、§5.4〜§5.8 で軽量化方針・段階層構造・reopen 機械強制・session 跨ぎ状態管理・多層防御の位置付けを確定済み。本仕様はこれらの確定事項を要件として整理する。

## Boundary Context

- **In scope（範囲内）**
  - 所定手続き（intent／feature-partitioning／requirements／design／tasks／implementation／reopen／cross-spec-alignment）の段集合定義
  - 段集合の YAML 静的列挙（リポジトリ内 `stages/<process_id>.yaml`）
  - 軽量版検査スクリプト（証跡ファイル存在 ＋ 必須節充足の判定）
  - 不可逆操作の直前ゲート（spec.json 承認／コミット／プッシュ／フェーズ移行）
  - reopen 手続きの機械強制（手戻り種別の二次元表記、`trigger_map` による連鎖再実施）
  - session 跨ぎ状態管理（`stages/in-progress/`）
  - 多層防御の第 1 層位置付け（フェーズ 4 以降の第 2〜5 層の宿題化）
  - 起草者と判定者の分離（レビュー記録の front-matter `author`／`reviewer` 異名必須）

- **Out of scope（範囲外）**
  - 各機能の業務ロジック修正
  - `runtime`／`evaluation`／`self-improvement`／`analysis`／`conformance-evaluation` の具体的挙動変更
  - PR 運用や外部 CI の詳細
  - 人間レビュアー割り当て方針
  - 節ハッシュ・supersedes リンク・grandfathering 機構（§5.4 で削除確定）
  - 独立再導出パーサ（§5.4 で削除確定）
  - 通過マーカーの後続確認（§5.4 で削除確定、二次防御は多層防御の宿題）

- **隣接仕様の期待**
  - `foundation`／`runtime`／`evaluation`／`analysis`／`self-improvement`／`conformance-evaluation` は本仕様の完了規則に従う
  - `foundation` が所有する語彙正本を再定義せず参照する。本機能が実際に参照するのは、レビュー記録の冒頭メタデータ検査（Requirement 3）で用いる `review_mode`（レビューモード語彙、`foundation` Requirement 6 受入 6 所有）であり、所見系（`counter_status`／`severity`／`final_label`／`confidence_label`）・状態軸系（`run_status`／`validator_status`／`human_signoff_status`／`evidence_class`）は本機能の責務外で参照しない（`foundation` design.md が `severity` 等の再定義禁止対象から本機能を明示的に除外していることと整合。A-003 対処 2026-05-28）
  - `evaluation` から本仕様の所定手続き実行結果に対する評価要求を受ける
  - `self-improvement` からの規律変更提案（5 種類：new_discipline／update／status_change／archive／consolidation、`self-improvement` Requirement 3 由来）を所定手続き（drafting → review → approval）の入力として受け取り、承認後に規律ファイル（`docs/disciplines/discipline_*.md`、active 必読 12 件は 2026-05-25 セッション 26 で memory から軽量手続きで移管済み）の実体変更を本機能が実施する。本機能は規律変更を不可逆操作（Requirement 4 受入 1）の対象として扱い、`self-improvement` が直接ファイル書き換えを行うことはない（案 2、2026-05-23 利用者承認、A-007 由来）。memory 側の `feedback_*.md` 索引（Claude Code auto memory 機構の領域）は本機能の管理対象外で、本体は repo の `docs/disciplines/` を参照する設計

## Requirements

### Requirement 1：所定手続きの段集合の静的列挙

**目的（Objective）**：保守担当者と実装者が、所定手続きの段集合を機械可読な形で参照でき、各段の完了条件を再現可能に検査できるようにする。

#### 受入基準（Acceptance Criteria）

1. 本機能はリポジトリ内 `stages/` ディレクトリに、所定手続きごとの段集合を YAML として静的に列挙する。Markdown 節からの動的解析を行わない。
2. 本機能は計画書 §5.5 で確定した 9 ファイル体制（`intent.yaml`／`feature-partitioning.yaml`／`feature-dependency.yaml`／`requirements.yaml`／`design.yaml`／`tasks.yaml`／`implementation.yaml`／`reopen-procedure.yaml`／`cross-spec-alignment.yaml`）を支える。
3. 各 YAML 段は最低限、段名、`actor`（`human` または `llm`）、期待する証跡ファイルのパスパターン、必須節名のリスト、完了判定方式を含む。
4. 機能横断段の場合、`feature_order` フィールドで `feature-dependency.yaml#feature_order` を参照する（旧称 `phase_order`。Requirement 8 受入 2 の由来注記を参照）。
5. 段集合の変更は YAML ファイル 1 箇所の修正で完結し、Markdown 文書側との整合は人手で取る前提とする（§5.4 受け入れリスク）。
6. **機能横断段（review-wave）の作業内容（2026-05-27 セッション 34 追記、2026-05-28 セッション 35 で 2 回方式に訂正、軽量手続き）**：本機能が管理する所定手続きの中で、機能横断段（review-wave）の作業内容は計画書 §5.5（機能横断段の作業内容）／ §5.9.6（N モデル比較実験の実施タイミング）と整合する。具体的には、機能横断段は「機能横断波及所見の集約・対処」に加え、「**7 モデル比較実験の 2 回目（同根問題評価）と同根問題集約**」（(ニ) (Q2)、2026-05-27 セッション 34 確定 ／ 2 回方式への訂正、2026-05-28 セッション 35 確定）を作業内容として含む。7 モデル比較実験は **2 回方式** で実施し、1 回目は機能ごとの triad-review 段で機能内 must-fix／should-fix を評価して機能内対処を完了させ、2 回目（本機能横断段）は機能横断波及所見と同根所見を評価する。本受入基準は計画書 §5.23.13 軽量手続き許容の範囲内で追加。利用者明示承認の出典：「計画書や仕様・設計にも反映」「提案通り」（2026-05-27 セッション 34）／「機能内対処は triad-review 段で実施しないと、他のフィーチャーの処理に影響する可能性がある。一方、同根問題は機能横断段で処理するべきである。つまり、2 回に分けて 7 モデルの must-fix+should-fix の対応が必要」「案 イ」「案 ア」（2 回方式への訂正、2026-05-28 セッション 35）。

### Requirement 2：軽量版検査スクリプトの提供

**目的**：保守担当者が、所定手続きの段完了を機械検査できるようにする。検査は主張ではなく証拠に基づき、結論不能なら遮断する。

#### 受入基準

1. 本機能はリポジトリ内検査スクリプト（Python 実装）を提供する。
2. 本検査スクリプトは段ごとの完了判定を次のみで実施する：YAML に列挙された証跡ファイルがすべて存在し、必須節名がすべて含まれること。
3. 本検査スクリプトは中身の妥当性（記述内容の品質）を判定しない。第 1 層の限界（§5.8）として明示する。
4. 本検査スクリプトは結論不能（証跡ファイルが解析不能、YAML が壊れている等）の場合、合格判定を出さず fail を返す。
5. 本検査スクリプトは `stages/in-progress/` に何かファイルがあれば「未完了の手続きあり」の警告を出す（§5.7）。
6. 本検査スクリプトは next サブコマンドを標準のワークフロー遷移入口として提供し、`workflow_state`、`stages/in-progress/`、post-write-verification pending、reopen pending、上流成果物が下流成果物より新しい状態から次に実行すべき作業を機械的に返す。完了済み workflow であっても、intent が feature-partitioning より新しい場合は機能分割確認、requirements が design より新しい場合は design 再確認、tasks が implementation 成果物より新しい場合は implementation 再確認のように、上流から下流への再展開を next action として返す。
7. 本検査スクリプトは post-write target detection と manifest verification を workflow-management の実装契約として扱う。post-write-verification 対象の未コミット変更がある場合、通常 workflow へ進ませず、completed manifest の `target_files`、`target_sha256`、`required_verifiers`、`verifications[]`、`unresolved_substantive_findings` に基づいて完了可否を判定する。
8. 本機能は `docs/operations/WORKFLOW_DISCIPLINE_MAP.yaml` を、判定点ごとに読み込む規律文書と入力資料の機械可読マップとして所有する。`next` はこのマップを読み、`next_action.required_disciplines` と `next_action.required_inputs` を返す。判定点ごとの `effective prompt` は、このマップが示す元資料を束ねて生成・記録する。`next` は生成した prompt の `effective_prompt_path`、`effective_prompt_sha256`、`effective_prompt_loaded` を `next_action.effective_prompt` に含める。元資料をすべて読めない場合は `effective_prompt_loaded: false` とし、fail-closed で通常作業へ進ませない。review-run 実行時は `rounds.yaml` に `effective_prompt_path` と `effective_prompt_sha256` を記録する。
9. 本検査スクリプトの `next --json` は、状態要約ではなく現在実行してよい唯一の action selector として振る舞う。`next_action.required_action` は常に 1 つだけを返し、post-write verification、maintenance、reopen blocker、reopen commit stop point、workflow state repair のような active workflow unit を持たない action では `feature`、`phase`、`stage`、`active_gate` を null にする。reopen 第3過程または通常 workflow の gate 実行だけが active workflow unit を持ち、その場合のみ `active_gate`、`feature`、`phase`、`stage` を非 null にする。`pending_gates`、`future_gates`、reopen scope、impact review scope は予定または補助情報であり、`active_gate` と混同してはならない。
10. 本機能は `required_action` の19語彙（D-003 §6 の19段階優先順位に対応）を `.reviewcompass/schema/required_action.schema.json` として JSON Schema 形式で定義する。語彙は D-003 §6 の優先順位順に列挙し、`repair_workflow_state`〜`completed` の19値を `enum` として持つ。語彙の追加・変更はこのスキーマファイルの修正で完結し、実装コード側の列挙はこのファイルを正本とする。
11. 本機能は `next --json` の目標応答スキーマを `.reviewcompass/schema/next_action_response.schema.json` として JSON Schema 形式で定義する。本スキーマは受入9が定める振る舞い契約（唯一アクション選択・進行中作業単位の有無による null/非 null の切り替え）をスキーマとして表現する。（1）最上位の必須フィールドは `verdict`（文字列）・`exit_code`（整数）・`next_action`（オブジェクト）・`reasons`（配列）・`current_state`（オブジェクト）の5つとし、`verdict` は最上位だけに置き `next_action` 内には含めない。（2）`next_action` の最低限の必須フィールドは `kind`（文字列・`required_action` の分類子、値域は受入 12 で確定）・`required_action`（受入10のスキーマを参照）・`active_gate`（文字列または null）・`feature`（文字列または null）・`phase`（文字列または null）・`stage`（文字列または null）・`required_feature_scope`（配列）・`blocked_by`（オブジェクトまたは null）・`future_gates`（配列）・`state_refs`（オブジェクト）の10フィールドとする。これに加え、`repair_reasons`（配列）は `repair_workflow_state` 時に必須となる条件付きフィールド（非空配列・最低1要素）とし、`action_parameters`（オブジェクト）は `run_maintenance` のみを対象とする必須の条件付きフィールドとして定義する。6フィールド（`maintenance_action`・`allowed_scope`・`allowed_files`・`completion_conditions`・`active_stack_frame_id`・`parent_frame_id`）はすべて required とし、追加フィールドの許可・禁止は design で確定する。（3）`feature` はリスト型を許容せず、取り得る値は「単一フィーチャー名」・`"all_features"`（review-wave のような真に横断的な実行単位の場合のみ）・null（進行中の作業単位がない場合）の3種類に限る。複数フィーチャーが影響範囲に入る場合は `required_feature_scope` または `future_gates` に置く。（4）受入9の null/非 null 規則をスキーマで表現する。進行中の作業単位（active workflow unit）がない場合、`feature`・`phase`・`stage`・`active_gate` はすべて null とする。作業単位がある（reopen 第3過程または通常 workflow の gate 実行時）場合のみ、これらのフィールドは非 null とする。（5）後方互換のため `pending_gates`・`next_pending_gate` はオプションフィールドとして定義し、このスキーマの正本フィールドは `future_gates`・`active_gate` とする。これらの後方互換フィールドが存在する場合は対応する正本フィールドと一致させること（`next --json` の実装側の不変条件として要求する。JSON Schema での表現は design で確定する）。新規のコンシューマは正本フィールドのみを参照してよい。（6）`required_action` の値ごとにフィールドの値制約（相互排他）がある。以下は D-003 §4.2 で確定している制約であり、スキーマはこれらを機械的に検証できる構造で表現する（スキーマ上の表現方法は design で確定）。① `commit_stop_point` の時：`active_gate=null`・`phase=null`・`stage=null`・`blocked_by.type="commit_stop_point"`。② `run_reopen_pending_gate` の時：`active_gate` 非 null・`phase`/`stage` は `active_gate` と一致・`blocked_by=null`。③ `run_reopen_drafting` の時：`active_gate` は `stages/<phase>.yaml#drafting` 形式・`phase`/`stage` はその drafting 単位と一致。④ `repair_workflow_state` の時：`active_gate=null`・`phase=null`・`stage=null`・`repair_reasons` に修復理由を含める。⑤ `wait_for_human_decision` の時：`blocked_by.type` で停止理由を区別。⑥ `run_maintenance` の時：`action_parameters` に `maintenance_action`・`allowed_scope`・`allowed_files`・`completion_conditions`・`active_stack_frame_id`・`parent_frame_id` を含める。上記①〜⑥の制約は D-003 §4.2 で確定している制約の全てであり、これ以外の `required_action` 種別には確定した追加フィールド制約はない（universal 必須フィールドのみが適用される）。
12. 本機能は `commit_candidate`、`commit_mixing_risk`、`commit_unit_stale` の3種類の判定を `next --json` の `kind` から除外し、`commit-preflight` サブコマンドの出力にのみ含める。これらの判定は「作業の現在地カテゴリ」ではなく「コミット操作の前確認」であり、`next --json` の `kind` は作業の現在地のみを示す7種類（`completed` / `in_progress` / `blocking_in_progress` / `verification_pending` / `reopen_in_progress` / `feature_definition_required` / `unknown`）に限定する。設計の詳細は `docs/notes/2026-06-26-next-json-kind-redesign.md` を正本とする。（2026-06-26 reopen R-0 next-json-kind-redesign、根拠：`docs/reviews/reopen-classification-2026-06-26-wm-next-json-kind-redesign.md`）
13. 本機能は、通常 workflow が完了状態のときに backlog 候補を次作業候補として表示できるが、backlog 自体を work lane または execution entry point として扱わない。work lane は SDD workflow、reopen、maintenance とし、backlog は候補置き場に限定する。候補を実行へ進める前に、maintenance 直行可能か、reopen として開き直すべきか、SDD workflow へ送るべきかを分類する。maintenance は小さく局所的で、既存判断を変えず、checklist に直接落とせる場合だけ直接実行可能とする。TODO は backlog materialization の標準中間物として使わず、maintenance 候補は checklist へ直行し、それ以外は SDD workflow または reopen へ送る。既存 TODO ファイルは棚卸しし、既存 plan に内容があるものは重複作業不要、TODO-only の候補は plan record に戻す。`next --json`、自律実行トリガー、commit preflight、既存 helper は、この routing discipline と矛盾してはならない。設計の詳細は `plan-2026-07-01-backlog-entry-lane-routing` と本 reopen の design/tasks 段で確定する。（2026-07-01 reopen R-0 backlog-candidate-routing、根拠：`docs/reviews/reopen-classification-2026-07-01-wm-backlog-candidate-routing.md`）

### Requirement 3：起草者と判定者の分離

**目的**：保守担当者が、自己承認による所定手続きの空洞化を防ぐ。レビュー記録の冒頭メタデータで起草者と判定者の異名を必須化する。

#### 受入基準

1. 本機能はレビュー記録の front-matter に `author`（起草者）と `reviewer`（最終判定者）のフィールドを必須化する。
2. 本機能は `author.identity` と `reviewer.identity` の同一を許容しない（§5.4 の自己承認禁止）。
3. 本機能はサブエージェント方式（`mode: subagent_mediated`、計画書 §5.23.12）でメインセッションが主役を担う場合、判定役を必ず別エンティティ（別モデル、別 session）で実施することを要求する。
4. 本機能は機械検査時に front-matter の必須フィールド存在と異名条件を判定する（別モデル・別 session の機械判定は第 1 層検査対象外。利用者監査の第 3 層に委ねる、Requirement 7 受入 2 由来）。
5. 本機能は review-run 後の proxy_model 判断代行を、メインセッション LLM のトリアージ下書き、proxy_model の採用案・判断理由・最終ラベル決定、機械ガードによる proxy decision 充足確認、メインセッション LLM の TDD 実装、利用者による不可逆操作承認、の分担として扱う。proxy_model は重要件の判断を代行できるが、コミット・プッシュ・spec.json 更新・フェーズ移行は代行しない。

### Requirement 4：不可逆操作の直前ゲート

**目的**：保守担当者が、所定手続きの空洞化を構造的に防ぐ。機械ゲートを不可逆操作の直前に集中する。

#### 受入基準

1. 本機能は次の不可逆操作の直前を機械ゲートの対象とする：`spec.json` の `approve` 書き込み、コミット、プッシュ、フェーズ移行。
2. 本機能はゲート発火条件として、Requirement 2 の検査スクリプトが pass を返すこと、および `stages/in-progress/` に未完了手続きがないことを要求する。直前ゲートは毎回独立して走行する（session 開始時の検査結果（Requirement 6 受入 3）をキャッシュせず、session 開始後の状態変化を直前で再検出する）。
3. 本機能は検査が結論不能な場合、ゲートを通さない（fail-closed の既定）。
4. 本機能は機械ゲートを最小集合に絞り、不可逆操作以外には機械検査を強制しない（§5.4 の「最小集合」方針）。
5. 本機能はコミット直前ゲートで commit 承認レコードを要求する。承認レコードは `approved_action=commit`、`approved_by=user`、未消費状態、staged ファイルの被覆に加え、staged 内容と一致する `target_sha256` を対象ファイルごとに保持しなければならない。`target_sha256` が欠落、形式不正、または staged 内容と不一致の場合は fail-closed で遮断する。
6. 本機能は LLM 介在の commit 承認を、staged ファイル集合と staged 内容に束縛した nonce challenge 経由で記録する。commit 承認用 challenge は、staged ファイル一覧、ファイル別 `target_sha256`、全体 target digest、nonce、有効期限、消費状態を保持する。commit 承認レコードの作成時と commit 直前ゲートは、nonce 一致、challenge の未期限切れ、未消費、staged ファイル集合と staged 内容の一致、approval record と challenge の target digest 一致を検査し、欠落・形式不正・期限切れ・不一致・消費済みの場合は fail-closed で遮断する。
7. 本機能は commit 承認 nonce の判定を、操縦する LLM、provider、model に依存させない。nonce 生成、challenge 保存、approval record 作成、commit gate 判定、consume は staged ファイル集合・staged blob hash・target digest・nonce・expiry・consumed 状態だけを入力にし、model 名や provider 名を判定条件に含めない。LLM ごとの差異は利用者への説明文やプロンプト表現に限定する。本方式は利用者が UI 上で nonce を発話したことの暗号的証明ではなく、承認を staged 内容に束縛して古い承認・別対象の承認・対象差し替え後の commit を防ぐ範囲を保証する。
8. 本機能は LLM が `git commit` 実行を代行する場合、staged 内容承認とは別に、LLM への commit 実行代行承認を正式 CLI で記録できなければならない。正式 CLI は承認文を標準入力からのみ受け取り、argv には載せず、commit approval record と同居または参照可能な機械可読 delegation record を書き込む。実行代行承認は、同じ nonce challenge、target digest、staged ファイル集合、有効期限に束縛し、runtime JSON の手編集を正規経路として扱わない。delegation record は、同じ nonce に対する有効・未期限切れ・未消費の staged 内容承認 challenge と staged 内容承認 record が存在する場合だけ作成でき、staged 内容承認より前、challenge 不在、期限切れ、消費済み、target digest 不一致、または未期限切れ delegation record が既に存在する場合は fail-closed にする。ただし、同じ nonce・同じ staged exact index・同じ承認文に対する有効な staged 内容承認 record と delegation record が既に揃っている場合、配布可能 wrapper の再実行は既存 transaction を再利用し、approval record を書き直して delegation の digest を壊してはならない。承認文は commit 実行を明示する短い UTF-8 text に限定し、UTF-8 として解析不能、空、空白のみ、設計で定める byte 上限超過、または non-text/binary input の場合は fail-closed にする。承認文を保存する場合は秘匿性のある文字列を redaction し、redaction 失敗または redaction 後の残留 secret 検出時は delegation record を作成せず fail-closed にする。承認文言は `コミット`、`コミットして`、`コミットを実行`、`承認`、`commit`、`commitして` のような commit 実行代行を明示する短い文言に限定し、`次のコミットまで`、`コミット点まで`、`コミット準備`、`自律実行`、`進めて`、`続けて`、`OK` のような準備・継続・一般応答を表す文言では fail-closed にする。配布可能な通常 UX では、1 回目の「コミット」で nonce / target digest / staged 対象を提示し、2 回目の「承認」1 行を `guarded-git-commit.py` が読み、staged 内容承認 record と実行代行 delegation record を内部で連続作成してから commit 直前ゲートを通す。低レベルの `prepare`、`record`、`delegate-execution` はデバッグ・検査用に残してよいが、第三者向け操作手順に露出させない。commit 直前 gate 通過後に `git commit` 本体が lock、sandbox、hook、署名などの実行失敗で commit を作成できなかった場合、staged exact index と approval / challenge / delegation が同一で未期限切れなら、approval / challenge / delegation を consumed または invalidated にせず同じ transaction で再試行可能にする。

### Requirement 5：reopen 手続きの機械強制

**目的**：保守担当者が、reopen 手続き（やり直し）の連鎖再実施を機械的に決定できるようにする。手戻り種別から再実施対象を自動決定する。

#### 受入基準

1. 本機能は手戻り種別を「起点フェーズ記号 N／R／D／A／I ＋ 深さ」の二次元表記で表す（計画書 §5.6）。N＝intent、R＝requirements、D＝design、A＝tasks、I＝implementation。深さの範囲は起点ごとに非対称：N 起点は深さ 0 のみ（intent より上流が存在しないため）、R 起点は 0〜1、D 起点は 0〜2、A 起点は 0〜3、I 起点は 0〜4。
2. 本機能は `stages/reopen-procedure.yaml` の第 7 段に `trigger_map` を持たせ、種別から再実施対象を機械的に決定する。
3. 本機能は actor=human の段（intent.yaml#approval、feature-partitioning.yaml#approval 等）に進行が到達した時点で作業を停止し、in-progress ファイルに「人間承認待ち」を記録して待機する。
4. 本機能は人間承認なしに次の段への進行を許さない（fail-closed）。
5. 本機能は種別判定の根拠を `docs/reviews/reopen-classification-<日付>.md` として保存し、第 7 段はその判定ファイルを読み込んで連鎖再実施対象を決定する。
6. 本機能は reopen 進行中 state を `next --json` へ投影する前に、blocker、commit stop point、reopen step、pending gate の優先順位を機械的に解決する。`current_blocker` がある場合は gate 実行ではなく `wait_for_human_decision`、`commit_stop_point: true` がある場合は pending gate が残っていても `commit_stop_point` を唯一 action とする。第3過程の pending gate は、これらの停止点がない場合だけ `run_reopen_drafting` または `run_reopen_pending_gate` として active gate になる。

### Requirement 6：session 跨ぎ状態管理

**目的**：複数段にまたがる手続きの途中で session が切れる場合、進行中状態を明示し、次セッションが優先処理できるようにする。

#### 受入基準

1. 本機能は現在進行中の手続きを `stages/in-progress/<process_id>-<日付>.yaml` で表す。
2. 進行中ファイルは最低限、`process_id`、`started_at`、`trigger`、`completed_steps`、`next_step`、`pending_gates` を含む。
3. 本機能は session 開始時の標準フローとして次を要求する：TODO_NEXT_SESSION.md と git log で全体到達点把握、`stages/*.yaml` 全件検査、`stages/in-progress/` の有無確認、進行中手続きの優先完了、次作業の決定。
4. 本機能は手続き完了時、進行中ファイルを `stages/completed/` に移動するか削除する。
5. 本機能は `stages/in-progress/` に何かある状態での不可逆操作実行を遮断する（fail-closed、Requirement 4 と整合）。
6. 本機能は原則として毎 session、特に重要な判断・承認・レビュー結果・修正経緯が発生した session について、`docs/sessions/session-<N>-<YYYY-MM-DD>.md` にセッション記録を残す運用を要求する。`<N>` は既存の最大セッション番号 + 1 とし、メインセッション LLM が草案作成責任を持つ。`TODO_NEXT_SESSION.md` は入口メモ、`docs/sessions/` は経緯記録の保存先として役割を分離する。
7. 本機能は、通常の `next_action` と異なる side track、または `next` 判定自体の欠陥修復に着手する場合、ファイル編集前に `process_id: maintenance` の進行中ファイルを作成することを要求する。maintenance 進行中ファイルは `trigger`、`mainline_blocked_by`、`allowed_scope`、`allowed_files`、`completion_conditions` を保持する。

### Requirement 7：多層防御の位置付け

**目的**：保守担当者が、本機能（軽量版 YAML 検査機構）が多層防御の第 1 層であることを理解し、過剰な期待をしないようにする。100% の規律遵守は原理的に不可能であり、複数層を重ねて実効遵守率を引き上げる方針。

#### 受入基準

1. 本機能は自身を多層防御の第 1 層として位置付け、第 1 層が解決しない失敗モード（中身の空疎、検査スクリプトの呼び出し依存、in-progress ファイルの自己申告性、文脈圧力下での規律低下、§5.8 由来）を明文化する。
2. 本機能は第 2〜5 層（git フックによる外部強制、フェーズ境目の利用者監査、定期事後監査、処理表面積の抑制方針）をフェーズ 4 以降の宿題として参照する。
3. 本機能は第 5 層（処理表面積の抑制方針）の運用ルール「新規規律を追加するときは既存規律 1 つ以上を統廃合する」を本機能の運用ルールに反映する（フェーズ 4 までは利用者の意識に依拠、機械強制は第 5 層導入時に検討）。
4. 本機能は第 1 層の限界を運用文書に明示し、利用者の期待値を整える。
5. 本機能は自律・並列実行を行う場合の安全契約として、自律 plan と履歴 ledger を検査対象に含める。自律 plan は run ID、依存順、recheck 対象、許可パス、期待テストを明示し、履歴 ledger は実行結果、統合判断、検証コマンド、未解決 blocker を追跡する。未記録依存や上流 recheck の下流反映が必要になった場合は、統合判断に戻るまで当該作業を進めない。

### Requirement 8：機能依存マップの一元化

**目的**：保守担当者が、機能間の処理順と依存関係を 1 箇所で管理できるようにする。各フェーズの YAML がこのマップを参照することで、機能の追加・削除や依存関係の変更が 1 箇所のみの修正で完結する。

#### 受入基準

1. 本機能は `feature-dependency.yaml` を機能間処理順と依存関係の一元保管先とする。開発リポジトリでは `stages/feature-dependency.yaml` に置く。対象アプリでは feature-partitioning の承認結果を `.reviewcompass/feature-dependency.yaml` として実体化する（設計記録 `docs/notes/2026-06-10-deployment-multi-llm-entry-design.md` §3.5 由来、2026-06-12 反映）。
2. 本ファイルは最低限、`features`（機能ごとの `depends_on` 列挙）と `feature_order`（機能間処理順）を含む。`depends_on` の値は単純なリスト構造（例：`[foundation, runtime]`）、または依存種別（`hard`／`review`）を持つ連想配列構造（例：`foundation: hard, runtime: review`）の両方を許容する。後者は `conformance-evaluation` のように依存性の強度を区別する機能で使う（計画書 §5.5 行 368〜373 由来）。**由来注記**：旧称 `phase_order`（計画書 §5.5 および `stages/feature-partitioning/2026-05-24-proposal.md` の表記）は `feature_order` と同一物である。過去記録（レビュー記録・分割提案書・計画書）は書き換えず、本注記で読み解く（語彙調停 案 A、MLE-DEC-001、2026-06-12 利用者決定）。
3. 各フェーズの YAML（`requirements.yaml`／`design.yaml`／`tasks.yaml`／`implementation.yaml`）の草案段とレビュー波段は `feature_order: <feature-dependency.yaml#feature_order>` の参照を持つ。
4. 機能の追加・削除や依存関係の変更は本ファイル 1 箇所の修正で完結する（計画書 §5.5 選択肢 X：独立 YAML 参照方式）。
5. 機能間依存マップの所有者は本機能であり、`runtime`／`evaluation` 等の他機能は再定義せず参照のみとする。
6. 検査ツール（Requirement 2）は feature 一覧と機能順を `feature-dependency.yaml` の `feature_order` キーから解決する。探索はツール実行時のカレントディレクトリを基準に、相対パス `.reviewcompass/feature-dependency.yaml` → `stages/feature-dependency.yaml` → `feature-dependency.yaml` の順で行い、最初に存在したファイル 1 つだけを読む。親ディレクトリへの遡上探索は行わない。直下の `feature-dependency.yaml` は標準 2 配置（受入 1：対象アプリ＝`.reviewcompass/`、開発リポジトリ＝`stages/`）のいずれにも該当しない配置への後方互換の受け皿であり、標準配置としては使わない。「一元保管先」（受入 1）とは、この探索で選ばれる実行文脈ごとの単一ファイルを指し、同一実行で複数ファイルを併読しない。ソース直書きの既定機能順（`tools/check-workflow-action.py` 内の既定定数）は `next` 判定では解決結果で上書きされる（2026-06-12 反映、MLE-C-001。探索基準の精密化は triad-review クラスタ A・F1・F2 対処）。
7. 検査ツールは `feature_order` が `depends_on` と矛盾しない順序であること（依存される機能［依存先］を、依存する機能［依存元］より先に置くこと。例：runtime が foundation に依存する場合、foundation を runtime より先に置く）、および循環依存がないことを機械検査する。違反時、`next` は `next_action.kind: unknown` を返し、違反内容を出力の `reasons` 配列に理由として列挙し、verdict は DEVIATION（exit code 2、fail-closed）とする（2026-06-12 反映、MLE-C-003。出力形式の明記は triad-review クラスタ B・D・F3 対処）。
8. feature 一覧が解決できない場合のうち、`feature-dependency.yaml` がどの探索先にも存在しない、または `feature_order` キーが未定義の場合、検査ツールはエラーではなく `next_action.kind: feature_definition_required`（verdict OK、exit code 0）を返し、intent／feature-partitioning の実施と、承認された分割結果（依存の根拠と順序の導出を含む）の `feature-dependency.yaml` への記録を案内する（2026-06-12 反映、MLE-C-002）。
9. 受入 6 の探索で選ばれた（最初に存在した）1 ファイルが、YAML として読めない（パース不能）、空（内容なし）、または最上位が連想配列でない場合は、未定義と区別して遮断する。これらはファイルそのものの破損・構造異常であり、読み込み後の値の整合検査（受入 7）とは別であって、判定は受入 9 を受入 7 より先に行う。`next` は `next_action.kind: unknown`（既存の判定種別。受入 7 の整合違反と同じ kind で、WORKFLOW_DISCIPLINE_MAP.yaml に登録済み）を返し、破損ファイルのパスと内容確認を促す理由（空の場合は `feature_order` の記録を促す理由）を `reasons` 配列に列挙し、verdict は DEVIATION（exit code 2、fail-closed）とする。破損を立ち上げ案内で覆い隠さない（2026-06-12 反映、MLE-DEC-005。同日の triad-review F4 では現挙動の明文化（案 a）をいったん採ったが、利用者決定により遮断へ改めた。FUP-2026-06-12-001 の解消。境界の精密化は同日 triad-review 対処）。

### Requirement 9：既存システムへの後追い intent 追加時の下流再展開

**目的**：保守担当者が、既に requirements／design／tasks／implementation が存在するシステムへ intent を後から追加した場合でも、仕様駆動開発の順序を崩さず、既存設計との衝突確認を含めて下流工程へ進められるようにする。

#### 受入基準

1. 本機能は、既存システムで intent が追加または修正された場合、機能分割で受け皿 feature を判定し、受け皿がある feature は reopen 対象、受け皿がない場合は新 feature 候補として扱う。
2. 本機能は、既存 requirements に似た記述があることだけを理由に処理を終了しない。該当 feature を reopen し、requirements／design／tasks／implementation の各段で、修正不要か修正必要かを判定して記録する。
3. 本機能は、下流工程の各段で既存仕様との衝突確認を要求する。新しい要件や設計が既存設計、既存タスク、既存実装と矛盾する可能性がある場合は、衝突候補として記録し、reopen record の `current_blocker` に人間承認待ちを設定するか、該当 phase の approval gate で停止する。停止解除には、判定対象 gate、feature scope、判断、理由、証跡、判定者を `downstream_impact_decisions` に記録することを必要とする。
4. 本機能は、コード由来の仕様差分抽出を `conformance-evaluation` の評価記録として受け取り、正式な requirements／design／tasks／implementation 更新は本機能の reopen 手続きで進める。受け取り対象の評価記録は、最低限 `feature`、`phase`、`classification`、`code_refs`、`existing_spec_refs`、`reasoning_summary`、`needs_human_decision` を持つ候補一覧を含む。
5. 本機能は、後追い intent 追加が既存 implementation まで影響する可能性を持つ場合、`impacted_downstream_phases` に requirements、design、tasks、implementation を含める。各段で `existing_sufficient` と判定する場合も、その判定対象 gate、feature scope、理由、証跡、判定者を `downstream_impact_decisions` に残す。
6. 本機能は、ReviewCompass 自身を試行対象にした場合も、通常の所定手続きとして扱う。試行中にワークフロー手続きの不足が見つかった場合は、本線作業と side track を区別し、必要なら `stages/in-progress/maintenance-*.yaml` を作成する。maintenance 進行中ファイルは、本線の `mainline_blocked_by`、許可範囲、許可ファイル、完了条件を持ち、完了時は `stages/completed/maintenance-*.yaml` に移す。

### Requirement 10：review-wave 横断確認の要約コマンド

**目的（Objective）**：保守担当者が、review-wave（機能横断段）の横断確認で用いる指標を、手動集計ではなく機械的に生成・再現できるようにする。集計漏れや報告の揺れを防ぐ。本要件は Requirement 1 が定める「段集合 YAML による静的列挙」と Requirement 2 の検査スクリプトを土台に、横断確認の指標化を機能内の静的検査として位置づける（新しい意図を要さない。2026-06-14 reopen R-0、利用者決定）。

#### 受入基準（Acceptance Criteria）

1. 本機能は、review-wave の横断確認指標を機械生成する要約コマンド（Requirement 2 の検査スクリプトのサブコマンド、または同等の helper）を提供する。読み取り元は次とし、手動集計に依存しない：各 feature の spec.json の `workflow_state` と `recheck`、`stages/in-progress/`、機能依存マップ（Requirement 8 の `feature_order`）、各 review-run の `triage.yaml`（triage 件数の算出元）、機能横断持ち越し所見記録（carry-forward register、`learning/workflow/carry-forward-register/`）。各指標の厳密な算出定義（フィールド対応・集計規則）の詳細は design で確定する。
2. 本コマンドの出力項目は最低限、次を含む：feature coverage（機能ごとの段到達状況）、各機能の phase／stage 状態、triage の未解決（unresolved）件数・draft 件数・human_required 件数、recheck 状態（`upstream_change_pending` と `impacted_downstream_phases`）、依存状況（`feature_order` と未充足依存）、carry-forward（機能横断持ち越し所見）の未消化件数。
3. 本コマンドは出力形式として Markdown と JSON の両方を提供し、両者は情報同等とする。JSON は機械処理用に安定したスキーマ（キー構造・型）を持ち、その確定は design で行う。Markdown は人が読む横断確認用とする。
4. 本コマンドは結論不能（必要な記録が解析不能・欠落。解析不能の範囲は Requirement 2 受入 4 に従う）の場合、合格や完了を主張しない。機械可読な失敗シグナルとして**非ゼロ終了コード**を返し、JSON 出力に不能を示す機械可読な `status` を含め、Markdown でも完了と誤読されない明示をする。部分集計値を完了として扱わない（第 1 層の限界・fail-closed と整合、Requirement 2 受入 4・Requirement 7）。
5. 本コマンドは集計（読み取り）に徹し、`spec.json`・フェーズ状態・トリアージ判断を書き換えない（Requirement 3 受入 5 の proxy_model 非代行範囲、および Requirement 4 受入 1 の不可逆操作と整合）。書き出しは自身の要約出力に限り、保存先は `.reviewcompass/specs/_cross_feature/reviews/` とする（保存はオプションで既定は標準出力。自身の要約出力の書き出しは状態変更に当たらない）。

由来：D-001（review-wave summary command）。要件正本は `docs/notes/2026-06-04-implementation-review-wave-improvements.md` と `docs/notes/2026-06-05-future-development-candidates.md`。分類は 2026-06-14 reopen R-0（`docs/reviews/reopen-classification-2026-06-14-wm-review-wave-summary-command.md`）。実装は仕様確定後に TDD で行う正順の手続きとする。

### Requirement 11：重要決定の出典検査（裁定負荷対策）

**目的（Objective）**：保守担当者が、重要決定（不可逆操作・規律変更・仕様／計画変更に限定）の確定について、出典の有無・束ね・逐語一致・内容性を機械検査できるようにし、一括承認のなかに重要な件が埋もれて正しく裁定されないまま確定する誤り（裁定負荷）を防ぐ。本要件は新しい規律を導入するのではなく、既存規律 `discipline_approval_operation`（確定記述に出典必須・出典なし禁止・機械検査は承認の代替でない）と `discipline_plain_explanation_each_step`（重要承認は 1 件ずつ）を機械強制するものであり、Requirement 1 が定める静的検査と Requirement 4 が定める不可逆操作の直前ゲートの範囲に位置づける（新しい意図を要さない。2026-06-15 reopen R-0、利用者決定）。

#### 受入基準（Acceptance Criteria）

1. 本機能は、機械検査を可能にする構造化した重要決定の記録形式を定める。記録は最低限、決定 ID、重要種別（不可逆操作／規律変更／仕様・計画変更のいずれか）、決定文言、出典（出典の引用、セッション ID、出典発言を一意に特定するロケータ〔会話転写内の位置情報〕、当該出典が単一決定に対応するか複数決定で共有されるかの区分）を持つ。重要種別は不可逆操作・規律変更・仕様／計画変更に限定し、各種別の境界は既存の Requirement 4（不可逆操作の直前ゲート対象）を基準に判定する。仕様／計画変更は spec.json・requirements／design／tasks・計画文書の確定的変更を指し、軽微なタスク状態更新（段フラグの true/false 更新、進行中ファイルへの作業ログ追記など、新たな確定的決定を伴わない状態反映）とは区別する（境界の細目は design で確定）。本記録形式は going-forward の新規重要決定から適用し、過去の散文の決定台帳は遡及移行しない。記録形式の厳密なスキーマ（フィールド名・型・配置先・ロケータの表現）は design で確定する。
2. 本機能は、束ね検出を行う。複数の重要決定が同一の出典（同じ一回の承認発言）を共有している場合、それらを確定扱いにさせない（fail-closed、非ゼロ終了）。束ねの例外は原則認めず、避けられない場合も各決定が個別の出典・ロケータ・区分を持つことを確定の必要条件とする（束ね一括では確定させない）。束ね例外の適用（「避けられない場合」の判定）は機械が自動で認めず、機械は束ねを検出して fail-closed するに留め、例外適用は人の明示承認に委ねる。例外時の具体的な扱い・記録方法は design で確定するが、この「個別出典なしには確定させない」という必要条件は design で緩めない。
3. 本機能は、逐語照合を行う。各重要決定の出典の引用が、repo に取り込み済みの会話転写（層 1、`.reviewcompass/evidence/sessions/`）に逐語で存在するかを機械照合する。逐語で存在しない（言い換え・でっち上げ）場合は fail-closed とする。出典が現在進行中（未取り込み）のセッションの発言である場合は、確定操作（不可逆操作の直前ゲート）と転写取り込みの順序依存によるデッドロックを避けるため、次のとおり扱う。(i) 当該決定を「未検証（保留）」として記録し、検証済みの確定済み重要決定として扱わない（後続の確定や承認の根拠に用いない。直前ゲートを通過させて確定済みと見なすことはしない＝fail-closed の抜け道を作らない）。(ii) 直前ゲートは未取り込み出典の即時照合合格を確定の条件として強制しないことで作業の進行（コミット等）自体はブロックしないが、当該決定の「確定」は保留のままとする。(iii) 当該セッションの転写が層 1 へ取り込まれた後に逐語照合し、合格して初めて確定とする。取り込み・照合が行われない限り当該決定は未検証のままで、タイムアウト等で確定へ昇格させない。照合の対象範囲・正規化（空白・改行等）の規則、および保留状態の管理と後追い確定の順序制御の仕組みは design で確定する。
4. 本機能は、内容性検査を行う。「OK」「承認」等の内容を持たない返事だけを、重要決定の唯一の出典として認めない。検査は機械的に検出し fail-closed とする。内容なしとみなす語の判定基準は拡張可能なリストで管理し、その確定は design で行う。リストの拡張は規律変更扱いとし人の明示承認を要する。
5. 本機能は、検査（読み取り）に徹し、`spec.json`・フェーズ状態・決定記録そのものを書き換えない（Requirement 3 受入 5 の proxy_model 非代行範囲、および Requirement 4 受入 1 の不可逆操作と整合）。ただし `--verify-pending` による `verification_status`（pending → verified）と `verified_at` フィールドの更新のみを例外とし、design で明示的に確定する（書き換えられるフィールドは `verification_status`・`verified_at` の 2 フィールドに限定し、`statement`・`source`・`category` は書き換えない）。必要な記録が解析不能・欠落で結論不能の場合、合格や完了を主張せず、非ゼロ終了と機械可読な `status` で fail-closed とする（Requirement 2 受入 4・Requirement 7 と整合）。
6. 本機能の検査範囲は、出典の存在・束ね・逐語一致・内容性という機械的に判定可能なものに限定する。決定文言が利用者の意図を正しく汲んでいるかという意味一致の最終判断は機械で行わず、人または判定役（会話転写との突き合わせ）に委ねる。本機能は意味一致を「検証可能化」する（突き合わせに必要な出典と転写を提示する）ところまでを担う。
7. 本機能は、本検査を Requirement 2 の検査スクリプトのサブコマンドとして提供することを必須とする（基線）。加えて、Requirement 4 の不可逆操作の直前ゲート（commit 直前検査）へ組み込むかどうかは、組み込みの可否・発火条件を含めて design で確定する（設計上の拡張であり必須ではない）。これにより接続点を「必須のサブコマンド提供」と「設計判断の直前ゲート組み込み」に分け、達成条件を一意にする。

由来：裁定負荷対策（利用者決定の埋没防止）。動機事例は PLC-DEC-007 の誤記録（6 論点の一括確認表＋包括「OK」により、利用者発言と食い違う決定文言が裁定されないまま台帳化された。訂正記録は `docs/notes/2026-06-12-document-placement-stage2-decisions.md` の PLC-DEC-007 2026-06-13 訂正欄）。方針は 2026-06-13 利用者決定「(b) で対応」、検査方針（束ね検出・逐語照合・内容性、重要種別限定）の確定は 2026-06-14 利用者決定。分類は 2026-06-15 reopen R-0（`docs/reviews/reopen-classification-2026-06-15-wm-decision-source-lint.md`）。実装は仕様確定後に TDD で行う正順の手続きとする。

### Requirement 12：operation registry / preflight

**目的（Objective）**：保守担当者が、review-run、post-write verification、triage、reopen、commit approval、session-record、deployment / export などの操作を、記憶・前例・短縮名ではなく、機械可読な operation contract に基づいて開始できるようにする。操作開始前に、正本コマンド、入力、成果物、順序、pending 衝突、worktree 状態、上書き policy を read-only に検査し、作ってから直す手戻りを減らす。

#### 受入基準（Acceptance Criteria）

1. 本機能は operation registry を提供し、各 operation について最低限、`operation_id`、`kind`、正本 invocation identity（entrypoint path、subcommand、option、位置引数、実行 context を含む）、必須入力、対象識別子、生成予定成果物、順序モード、worktree policy、pending conflict policy、artifact policy、参照する既存 workflow 語彙を機械可読に定義する。workflow 段に属する operation は、対応する phase、stage、gate、または `next_action.kind` を registry 上で示し、現在の workflow state と照合できるようにする。registry の pending conflict は静的な衝突 policy、preflight 結果の pending conflict は実 worktree / workflow state から観測した runtime state として分ける。初期の `kind` は `irreversible`、`review_artifact`、`workflow_state`、`evidence_capture`、`deployment_export` を基本値とし、未知の `kind` は registry 定義エラーとして扱う。
2. 本機能は read-only の operation preflight を提供する。preflight は成果物を作らず、操作可否、足りない入力、衝突している pending / dirty / staged 状態、生成予定成果物、正本コマンド、順序モード、次に必要な人間向け手順を機械可読に返す。workflow state に依存する operation では、preflight が確認した現在の本線、required action、phase、stage、reopen scope、impact review scope、direct features、indirect features、flag policy、next pending gate などの状態次元を返し、`next --json` の状態一意性と照合できるようにする。read-only preflight は review-run directory、manifest、approval record、session record、commit、deployment / export output など、対象 operation の正本成果物を作成・更新してはならない。
3. preflight の共通結果は、少なくとも `schema_version`、`operation_id`、`verdict`、`allowed_verdicts`、`sequence_mode`、`allowed_sequence_modes`、`state_refs`、`required_inputs`、`missing_inputs`、`template_available`、`target_identity`、`worktree_state`、`pending_conflicts`、`checks`、`planned_outputs`、`canonical_commands`、`next_step` を持つ。`verdict` は `OK`、`WARN`、`DEVIATION` の 3 値とし、必須入力欠落、確認済み衝突、存在しない command / option、上書き禁止違反は `DEVIATION` として扱う。`DEVIATION` は対象 operation の開始を許さない。安全性または適用可否を確認できない条件は `OK` にしてはならず、read-only advisory 段階では `WARN` 以上、runner-enabled operation では `DEVIATION` として fail-closed にする。
4. 本機能は command validation を operation preflight の一部として扱い、registry の正本 invocation identity と実 parser / parser adapter を照合して、正本 entrypoint、サブコマンド、option、required option、位置引数の存在を実行前に検査できるようにする。`reopen-status`、`next --file`、誤った script path、短縮名、未登録 alias のような推測実行は、成果物を作る前に `DEVIATION` または確認不能 `WARN` として表示する。command validation の正本は人間向け help 文字列ではなく、実 parser または parser adapter から得る。
5. 本機能は worktree / pending conflict を operation ごとに検査する。post-write pending、reopen in-progress、maintenance in-progress、staged / unstaged の混在、対象外差分の同居、commit approval 作成後の staged 変更など、操作開始前に分離が必要な状態を表示し、明示された policy なしに別作業を混ぜて進ませない。worktree が clean でも、対象 operation に必要な承認 record、delegation record、manifest、bundle、target digest が欠落、stale、不一致、消費済み、または対象外である場合は pending conflict とは別の integrity conflict として扱う。
6. 本機能は review artifact 系 operation の作成前 preflight を扱う。対象には少なくとも `post_write_review`、`review_run_create`、`triage_decide`、`document_type_preflight`、`review_criteria_preflight`、`post_write_manifest_coverage_preflight`、`approval_record_preflight`、`bundle_preflight` を含める。preflight は、review target が phase / artifact 種別に必要な一次情報を含むか、差分 bundle が空でないか、staged / unstaged のどちらを対象にすべきか、review target、manifest、bundle、criteria、document-type、approval record、既存 review-run artifact の対象集合が一致するか、approval record に対象 finding id と final label があるか、bundle / export artifact が対象全体を過不足なく覆るか、既存 artifact の上書き・stale・drift がないかを検査できる。
7. 本機能は順序依存 operation を `serial_only` として表現し、`prepare -> record -> delegate-execution -> guarded commit` のような commit approval chain を並列実行対象として扱わない。配布可能 UX では `guarded-git-commit.py --approval-nonce <nonce> --approval-source-text-line-stdin` が `record -> delegate-execution -> guarded commit` を単一操作として順序実行する。preflight は `serial_only` operation の複数 step を並列または順序外に実行しようとする状態、または承認 chain の成果物欠落、nonce / target digest / staged file set digest の不一致、stale、期限切れ、消費済み、invalidated、対象外 record を検出した場合、`DEVIATION` として対象 operation の開始を拒否する。runner を導入する前の read-only 段階でも、各段階の成果物存在、nonce、target digest、stale 状態、未消費状態を preflight 結果に示す。
8. 本機能は evidence capture 系 operation の current-session guard を扱う。session-record の formal 2 層出力入口では、現セッションを正式記録として生成しようとする操作を作成前に `DEVIATION` として拒否し、current session id を確認できない場合は正式出力を fail-closed にする。commit guard による混入防止は最後の保険として維持する。
9. 本機能は nested issue handling を operation preflight の対象に含める。作業中に別問題が見つかり、元作業の対象、検証範囲、allowed files、review target、manifest target、return condition のいずれかが広がる場合、parent task、発見 issue、親作業との関係、blocker / follow-up / side-track / dependent issue の分類、allowed files、return condition、nesting depth を記録または検査できるようにする。機械は記録漏れ、scope 増加、return condition 欠落、深度超過を検出し、明示された side-track / follow-up / blocker 記録がない scope drift は `DEVIATION` として停止する。意味判断は人または review / proxy に委ねる。
10. 本機能は deployment / export 系 operation の作成前 preflight を扱う。対象には少なくとも deployment smoke、deploy package build、runtime bundle export など、repo 外または出力ディレクトリへ成果物を書く操作を含める。preflight は、出力先の既存成果物、上書き禁止 policy、作成予定ファイル一覧、外部 app root への書き込み、既存 bundle / smoke-run / app file との衝突を成果物作成前に検査できる。
11. 本機能は全 feature impact review scope を operation preflight の入力として扱えるようにする。operation contract の直接所有が `workflow-management` にある場合でも、consumer / derivative として参照する foundation／runtime／evaluation／analysis／self-improvement／conformance-evaluation を review scope に含め、正本変更要否を gate ごとに記録できるようにする。このとき、正本を再オープンして flag を false に戻す `reopen_scope` と、正本変更要否だけを確認し flag を維持する `impact_review_scope` を区別し、direct / indirect feature sets、各 feature の flag policy、判断理由、証跡を機械可読に残す。
12. 本機能は operation registry / preflight の判定を、利用する LLM、provider、model に依存させない。判定入力は repository 状態、git index、既存 workflow state、registry 定義、parser / parser adapter、既存成果物、明示入力に限定し、model 名や provider 名を合否条件に含めない。LLM ごとの差異は説明文や prompt 表現に限定する。
13. 本機能は、Requirement 2 が所有する `next --json` の reopen 出力契約を拡張し、operation registry / preflight が `next` 状態を一意に参照できるようにする。`next` が `reopen_in_progress` を返す場合、現在の本線、次に実行すべき `required_action`、phase、stage、reopen scope、impact review scope、direct features、indirect features、flag policy、`next_pending_gate`、`next_drafting_gate`、`pending_gates`、`completed_gates`、superseded gate の有無、参照した state files を機械可読に返し、どの feature の workflow flag を false に戻し、どの feature の flag を維持するかを一意に判定できるようにする。これらの値は `feature_impact_decisions`、`spec.json`、`pending_gates`、`drafting_completed_gates`、`downstream_impact_decisions` と整合していなければならない。reopen scope と impact review scope が欠落、矛盾、または `feature_impact_decisions` / `spec.json` / `pending_gates` と整合しない場合、`next` は通常進行を許す `OK` として扱わず、`WARN` または `DEVIATION` と理由を返して停止させる。
14. Requirement 12 の preflight は `next --json` の出力を複製せず、Requirement 2 の selector 結果を参照する。preflight が扱う `state_refs.next_action` では、`required_action`、`active_gate`、`blocked_by`、`action_parameters`、`state_refs` を用いて唯一 action と補助情報を分離し、古い in-progress record、複数 frame、pending gate、maintenance action を LLM が解釈で選ぶ経路を作らない。

由来：operation registry / preflight 統合設計。動機事例は `docs/notes/2026-06-16-workflow-recovery-smell-inventory.md`、設計入口は `docs/notes/2026-06-16-operation-registry-preflight-design.md`、nested issue handling は `docs/notes/2026-06-16-nested-issue-handling-smell.md`。reopen scope / impact review scope と `next` 状態一意性の追記は、2026-06-16 セッション中の requirements approval 後の再確認で発見した証跡追跡上の欠落に基づく。分類は 2026-06-16 reopen R-0（`docs/reviews/reopen-classification-2026-06-16-wm-operation-registry-preflight.md`）。本改訂は仕様確定後に design／tasks／implementation へ連鎖し、実装は TDD で進める正順の手続きとする。

### Requirement 13：operation contract 語彙と required_action 対応

**目的（Objective）**：保守担当者が、`next --json` が選んだ唯一 action を、記憶や前例ではなく operation contract に基づいて実行できるようにする。選択層は「何をすべきか」を一意に返し、実行層は「どう実行するか」を副作用・承認・前提条件・事後条件として定義する。

#### 受入基準（Acceptance Criteria）

1. 本機能は operation contract の共通語彙として、最低限 `effect_kind`、`approval_required`、`phase_boundary`、`sequence`、`preconditions`、`postconditions` を定義する。`effect_kind` は `read`、`write`、`state_mutation`、`external_call` の4値を基線とし、`approval_required` は `effect_kind` とは独立した真偽値として扱う。
2. 本機能は Phase 1 のスキーマ定義として、operation contract schema、`effect_kind` schema、`phase_boundary` schema、状態スナップショット schema、言語タスク共通入出力 schema を `.reviewcompass/schema/` 配下に定義する。既存実行挙動はこの段階では変更しない。
3. 本機能は D-003 §6 の19段階優先順位に対応する `required_action` それぞれについて、operation contract 上の `effect_kind`、実行主体、`approval_required` の対応を registry または同等の機械可読定義で表す。対応表は19語彙すべてを対象とし、`run_maintenance`、`run_reopen_pending_gate`、`run_workflow_stage` のような条件分岐を持つ action を代表値だけで曖昧化しない。`required_action` 語彙そのものの正本は Requirement 2 受入 10 の JSON Schema とする。
4. 19語彙対応表は各 `required_action` について、最低限 `required_action`、`effect_kind`、`approval_required`、`phase_boundary`、`sequence`、実行主体、分岐条件の有無、参照する preconditions / postconditions を機械可読に持つ。複合操作または条件分岐を持つ語彙は、対応表上で「未確定」や代表値だけにせず、分岐ごとの条件と最大副作用を明示する。
5. 承認ゲートを必須とする単純操作は、最低限 `commit_stop_point`、`apply_approved_reopen_plan`、`run_reopen_start`、`advance_reopen_after_commit_stop_point`、`advance_reopen_after_approval_stop_point`、`finalize_reopen`、`repair_workflow_state` を含む。これらは `approval_required: true` として扱い、実行前に明示的な人間判断記録を必要とする。ただし、この人間判断記録は受入 6 および Requirement 14 受入 1〜3 の承認ゲート全体の一部であり、`record_human_decision` の完了だけを対象 operation の承認成立として扱ってはならない。この列挙は複合操作の分岐条件を否定しない。`run_maintenance` は maintenance YAML または内部操作の承認要求に従い、`run_workflow_stage` は stage 種別に従う。
6. `record_human_decision` は承認対象操作ではなく、承認ゲートを構成する判断記録操作として扱う。`effect_kind` は判断記録を書き込む場合は `state_mutation` とし、`approval_required` は常に `false` とする。`record_human_decision` の完了だけでは、対象 operation の `approval_required: true` を満たしたことにしてはならない。
7. `run_reopen_pending_gate` は active gate 種別に応じて operation contract を分岐する。`triad-review` と `review-wave` は外部レビュー実行を伴う `external_call`、`alignment` は LLM が整合確認材料を生成する `write`、`approval` は承認要求を構造化する `state_mutation` として扱う。drafting は `run_reopen_drafting` として分離する。
8. `run_maintenance` と `run_workflow_stage` は、内部で実行する操作または stage 種別によって `effect_kind` と `approval_required` が変わる複合操作として扱う。複合操作を単一代表値、list 型、内部ステップ分解のいずれで表すかは design で確定するが、LLM が都度推測する形にはしない。design で確定するまでの最小規則として、複合操作は分岐条件、内部 step、各 step の `effect_kind`、最大副作用、承認要否の集約規則を持つものとして扱う。
9. 複合操作の schema 表現は Phase 1 の未確定事項として扱う。候補は、最大副作用の `effect_kind` を代表値として注記する、`effect_kind` を list 型にする、複合操作を単一 enum の内部ステップへ分解する、の3案を最低限保持する。どの案を design で採用する場合でも、受入 8 の分岐条件、内部 step、各 step の `effect_kind`、最大副作用、承認要否の集約規則という最小制約を失わせてはならない。また、`record_human_decision` が記録する判断と承認対象の `required_action` を、セッション識別子、タイムスタンプ、操作 ID、または同等の識別子で結びつける方法を design で確定する。
10. 本機能は operation contract の実行前に preconditions を、実行後に postconditions を機械確認できるようにする。確認不能な条件を `OK` として扱わず、read-only advisory 段階では `WARN` 以上、runner-enabled operation では `DEVIATION` として fail-closed にする。
11. operation contract と operation registry / preflight の間には、単一の機械可読正本境界を置く。物理表現は design で確定するが、`effect_kind`、`approval_required`、`phase_boundary`、`sequence`、preconditions、postconditions、side effects、承認要否の集約規則を、registry と contract の複数箇所で別々に再定義してはならない。registry / preflight は正本 contract を参照または同一正本内で読み取り、実行・更新・承認消費を行わない read-only confirmation として扱う。
12. operation contract 正本と registry / preflight の参照関係は、欠落、stale、digest / version drift、または正本 field の重複を機械検出できなければならない。検出時は read-only advisory 段階では `WARN` 以上、runner-enabled operation では `DEVIATION` として fail-closed にする。

由来：`docs/notes/2026-06-18-integrated-design-selection-execution-layers.md` §3、`docs/notes/working/2026-06-18-mechanized-workflow-execution-design.md` §3・§10 Phase 1。2026-06-18 セッション 77e272a2 の統合設計メモ要件追記未完了分を、AC10・AC11 だけでなく operation contract 全体へ戻す。

### Requirement 14：承認ゲート、側道スタック、状態スナップショット

**目的（Objective）**：保守担当者が、不可逆操作の承認、予期しない側道作業、現在状態の可視化を、LLM の暗黙解釈ではなく機械可読な状態として扱えるようにする。

#### 受入基準（Acceptance Criteria）

1. 本機能は承認ゲートを、`wait_for_human_decision` と `record_human_decision` のペア、およびその後の `next --json` による分岐として扱う。`record_human_decision` が完了した事実は、対象操作が承認された事実と同一視しない。
2. 承認ゲートは、承認、拒否、保留、修正要求を区別して記録できなければならない。記録された判断の内容を読み、対象の不可逆操作へ進むか、停止を維持するか、再起草へ戻すかを決めるのは `next --json` の責務とする。
3. 承認、拒否、保留、修正要求の各判断は、対象 operation ID、対象 `required_action`、対象 artifact または staged file set digest、判断者、判断時刻、出典を持つ。`next --json` は、承認以外の判断が記録されている場合に対象の不可逆操作を許可してはならず、拒否は停止、保留は待機、修正要求は再起草または repair に分岐させる。
4. 本機能は side track をスタックとして扱う。各 frame は最低限、`frame_id`、`kind`、`parent_frame_id`、`pushed_by`、`allowed_scope`、`allowed_files`、`completion_conditions`、`return_to`、`title`、`spawned_from`、`staged_file_digest`、`staged_file_set` を持つ。
5. `staged_file_set` と `staged_file_digest` は side track push 時点、pop 直前、commit / push 直前に採取・照合できなければならない。frame の `allowed_files` 外の staged 変更、push 時点からの予期しない digest 変化、親子 frame 間で明示許可されていない staged file set の重なり、pop 時の digest / set 不一致は、Phase 3 では WARN 以上、Phase 5 では `DEVIATION` または `repair_workflow_state` として扱う。
6. side track は top frame だけを閉じられる。`side-track-pop` 後は `next --json` が直下の frame または本線作業を自動的に再開する。LLM が復帰先を会話文脈から選ばない。pop 後に git index が side track 開始前の本線状態へ戻っていない場合、または side track 内の commit / push 後に index の変化を説明する記録がない場合、通常作業へ戻してはならない。
7. side track の `max_depth` は既定 2 とし、Phase 3 では超過を警告、Phase 5 ではブロック対象とする。深度超過または scope drift は `repair_workflow_state` または同等の停止状態として扱う。
8. 本機能は `.reviewcompass/runtime/workflow-state-snapshot.yaml` を現在状態のスナップショットとして出力できるようにする。スナップショットは `next --json` の副産物であり、`next --json` 自体の出力契約を置き換えない。
9. 状態スナップショットは最低限、`schema_version`、`generated_by`、`generated_at`、`current_work`、`active_side_tracks`、`git_tree_summary`、`post_write_manifest_summary`、`workflow_state_summary` を持つ。`current_work` は `required_action`、人間可読 `title`、`outer_node`、`inner_node`、`active_gate` を含む。
10. スナップショットが古い、手動更新された、または `next --json` の実行結果と照合できない場合は信頼しない。正本は常に `next --json` と state refs であり、スナップショットは可視化・監査補助である。
11. 承認ゲートは proxy_model が代行できる判断と、人間だけが承認できる判断を機械可読に区別する。少なくとも commit、push、spec.json 更新、phase approval、reopen finalize、approval_required な不可逆操作の実行許可は human-only decision として扱い、proxy_model decision だけで通過させてはならない。proxy_model は所見 triage や補助判断を代行できるが、human-only decision の承認主体を置換しない。proxy_model の適用可否と human-required predicate の優先順位は Requirement 16 受入 13〜14 と整合させる。
12. side track stack、approval gate record、workflow-state snapshot は保存先、read-only 操作、mutating 操作を区別できなければならない。状態を書き換える push / pop / consume / invalidate / save 系操作と、状態を読む current / snapshot / inspect 系操作を同一 operation として曖昧化してはならない。

由来：`docs/notes/2026-06-18-integrated-design-selection-execution-layers.md` §5.1〜§5.3、`docs/notes/working/2026-06-18-mechanized-workflow-execution-design.md` §3.3・§8・§10 Phase 1。

### Requirement 15：構造化有効プロンプトと監査

**目的（Objective）**：保守担当者が、有効プロンプトを長い説明文ではなく、LLM が担当する言語タスクの仕様書として扱えるようにする。機械タスクは operation contract とツールが担い、有効プロンプトには言語タスクの入力・出力・制約・事後条件を明示する。

#### 受入基準（Acceptance Criteria）

1. 本機能は有効プロンプトの構造として、最低限 `decision_point`、`preconditions_checked`、`language_task`、`postconditions`、`on_completion` を定義する。
2. `language_task` は最低限、`document_kind`、`input`、`output_format`、`constraints` を持つ。LLM が生成または判断する対象、参照すべき入力、出力形式、禁止事項を判定点ごとに明示する。
3. 機械タスクは有効プロンプトに実行手順として埋め込まず、operation contract、preflight、runner、guard の責務として扱う。有効プロンプトは、機械が実行済みまたは確認済みの preconditions と、LLM が行う言語タスクだけを表す。
4. 本機能は Phase 4 で、`docs/operations/WORKFLOW_DISCIPLINE_MAP.yaml` または後継 registry から、全判定点について構造化有効プロンプトを生成できるようにする。既存の `next_action.effective_prompt.effective_prompt_path` との互換は維持する。
5. 本機能は有効プロンプトの第1層機械検査を提供する。検査は、参照先ファイルの実在、アンカーの実在、必須構造節の存在、長さの上下限、DISCIPLINE_MAP 未登録 action kind、review target manifest と review-run target の一致を確認する。加えて、`language_task.output_format` と `postconditions` の対応、`preconditions_checked` が機械確認済み条件だけを参照していること、`on_completion` が operation contract の postconditions / 次 action と矛盾しないことを検査する。側道スタックまたは operation preflight が持つ staged file set とのコミット混線検査は Requirement 12・14 の責務として扱い、有効プロンプト監査から参照可能にする。
6. 本機能は Phase 6 で、構造化有効プロンプトと `WORKFLOW_NAVIGATION.md` の該当節を入力に、LLM 裁判官による意味的監査を行えるようにする。監査は不足や gap を構造化出力で返す補助であり、意味的な最終承認を自動化しない。監査観点は、前提条件が機械確認可能な条件を網羅しているか、言語タスクの入出力形式が明確か、事後条件が出力妥当性を確認できるか、機械タスクに移すべき処理が有効プロンプトへ残っていないかを含む。
7. LLM 裁判官の出力は schema に適合する JSON または同等の構造化形式とし、既知の gap を検出できることをテストで確認する。既知の gap には、必須構造節の欠落だけでなく、機械タスクの有効プロンプト内残留、preconditions の網羅不足、postconditions の確認不能性を含める。Phase 6 は Phase 5 までの機械的強制が完了した後の任意・後回し可能な段階とする。

由来：`docs/notes/working/2026-06-18-mechanized-workflow-execution-design.md` §4・§5・§10 Phase 4・Phase 6、`docs/notes/2026-06-18-integrated-design-selection-execution-layers.md` §4.2。

### Requirement 16：段階的実装計画 Phase 0〜6

**目的（Objective）**：保守担当者が、選択層と実行層の機械化を一度に混ぜず、既存挙動を壊さない順序で TDD 実装できるようにする。

#### 受入基準（Acceptance Criteria）

1. 本機能は D-003 の19段階優先順位、`required_action` 唯一化、invariant 検査、reopen plan compiler を Phase 0 として扱う。Phase 0 は選択層の実装であり、D-003 全体を仕様とする。D-003 の参照元は `docs/notes/working/2026-06-16-next-json-unique-state-redesign.md` とし、正本昇格または移動が起きた場合は stable canonical anchor を requirements または design で明示する。
2. Phase 0 の開始前提として、Phase 1 のうち Requirement 2 受入 10・11 のスキーマ定義を先に満たす。これは Phase 0 TDD 開始を可能にする最小前提であり、統合設計全体を AC10・AC11 に限定するものではない。`effect_kind`、`phase_boundary`、operation contract、状態スナップショット、言語タスク共通入出力 schema は Phase 0 と並行して定義してよい。
3. Phase 0 の完了条件は、D-003 §7.1 の6つの失敗テストが全てパスし、現在の D-003 reopen に必要な workflow state repair を機械的に検出できることである。D-003 の節番号が変わる場合は、6つの失敗テストを requirements、design、または tasks のいずれかで列挙し、節番号だけに依存しない完了条件へ移す。必要に応じて `reopen-recompile` が reopen plan の派生値を再導出し、in-progress YAML の `pending_gates` と `commit_stop_point` の整合を修復できるようにする。
4. Phase 1 は語彙・スキーマ定義を行い、実行挙動を変えない。新規スキーマは `.reviewcompass/schema/` に置き、スキーマ自体の整合性をテストで確認する。Phase 1 のうち Phase 0 開始をブロックする最小スキーマは Requirement 2 受入 10・11 であり、それ以外の operation contract 系 schema は Phase 0 と並行可能な Phase 1 作業として扱う。
5. Phase 2 は読み取り専用 registry を実装する。`check-workflow-action.py operation-list --json` または同等のコマンドが、各 operation の `canonical_commands`、`effect_kind`、`approval_required`、`sequence`、`pending_conflicts` を返せることを完了条件とする。既存の `next --json` の動作は変えない。
6. Phase 3 は `operation-preflight <id> --json` または同等の事前検査を警告のみで導入する。pending conflict、側道 depth、コミット混線、有効プロンプト第1層機械検査を検出するが、この段階では既存フローをブロックしない。
7. Phase 4 は有効プロンプトを構造化し、全判定点で新構造の prompt を生成できるようにする。構造の完全性はテストで確認する。
8. Phase 5 は Phase 3 の警告を機械的ブロックへ昇格する。`sequence: serial_only` の順序違反、コミット混線、side track depth 超過、`approval_required: true` の承認欠落をブロックする。正常パスがブロックされないことをテストで確認する。
9. Phase 6 は LLM 裁判官による意味的監査を実装する。構造化した有効プロンプトと該当運用文書を入力にし、gap を構造化出力として返す。Phase 6 は Phase 5 までの後に着手し、後回し可能とする。
10. 各 Phase の終了時には `next --json` が通常作業に戻れる状態、または明示された停止状態を返すことを確認してからコミット対象にする。Phase をまたいだ途中状態を単一コミットに混在させない。
11. 本改訂の reopen scope は workflow-management の requirements から design / tasks / implementation への連鎖再実施である。`spec.json.reopened` は過去に上流を reopen した履歴フラグとして保持し得るため、現在の active reopen scope と同一視しない。現在の scope、impact review scope、direct / indirect feature、flag policy は in-progress reopen record、classification record、`spec.json.recheck`、および review-wave / alignment の証跡で区別して記録する。
12. operation contract、構造化有効プロンプト、状態スナップショット、proxy_model triage decision の機械処理化は、workflow-management 以外の feature が consumer / derivative として参照し得る。正本 reopen の対象を workflow-management に限定する場合でも、review-wave では foundation、runtime、evaluation、analysis、self-improvement、conformance-evaluation などへの正本変更要否と consumer 契約影響を確認し、reopen scope と impact review scope を混同せず記録する。
13. proxy_model triage decision の適用可否は、provider / model 名ではなく、機械可読な evidence completeness、対象 finding / cluster coverage、approval gate record、operation contract の `approval_required`、review-wave impact evidence、human-only decision 境界に基づいて判定する。human-required を示す証跡が 1 つでも存在する場合、または必要な判定元が欠落・競合する場合、proxy_model decision だけで通過させてはならない。
14. human-required predicate の優先順位と競合解決は design で確定する。最低限、human-only decision 境界、未解決 approval gate、`approval_required: true` の対象 operation、未解決 review-wave impact evidence は proxy_model 適用より優先される。triage 上の leave-as-is や proxy approved は、これらの human-required 証跡を打ち消さない。

由来：`docs/notes/2026-06-18-integrated-design-selection-execution-layers.md` §4・§6・§7、`docs/notes/working/2026-06-18-mechanized-workflow-execution-design.md` §7・§10。2026-06-18 セッション 77e272a2 の「統合設計メモ全体を requirements に書き込む」未完了作業の中核。

## Change Intent

本仕様は先行プロジェクトの `implementation-governance` 仕様（156 行、9 要件）を、ReviewCompass の方針（計画書 §5.4〜§5.8）に基づき**思想は継承、実装は 1／10**で再設計した。素材の Req 9（実行台帳と強制機構）の大規模機構（節ハッシュ・独立再導出パーサ・通過マーカーの後続確認・supersedes リンク等）は §5.4 で削除確定。

ReviewCompass 固有の追加：

- 機能名 `implementation-governance` → `workflow-management` に改称（計画書 §5.15.6）
- 段集合の YAML 静的列挙への置き換え（Requirement 1、§5.4 由来）
- 軽量版検査スクリプト（証跡 ＋ 必須節のみ判定）（Requirement 2、§5.4 由来）
- 起草者と判定者の分離をレビュー記録の front-matter で担保（Requirement 3、§5.4 由来）
- 不可逆操作の直前ゲートを最小集合に絞る（Requirement 4、§5.4 由来）
- reopen 手続きの機械強制を `trigger_map` で（Requirement 5、§5.6 由来）
- session 跨ぎ状態管理を `stages/in-progress/` で（Requirement 6、§5.7 由来）
- 多層防御の第 1 層位置付けを明示（Requirement 7、§5.8 由来）
- 機能依存マップの一元化（Requirement 8、§5.5 由来）
- サブエージェント方式（`mode: subagent_mediated`）への対応を Requirement 3 受入 3 で明示（計画書 §5.23.12 由来）
- 2026-06-08 の feature-partitioning 再確認により、intent の「レビュー収集処理を事前設定の写像にしない」意図は新機能追加を要さず、workflow-management では Requirement 2 の `next` による上流から下流への再展開、Requirement 4 の不可逆操作直前ゲート、Requirement 6 の session 跨ぎ状態管理、および Requirement 8 の機能依存マップ一元化で受けることを確認した。
- 2026-06-08 の reopen 判定修正により、完了済み workflow で上流正本が後続成果物より新しい場合は、`next` が単なる再確認ではなく `reopen_classification_required` を返し、reopen 分類と `reopen-start` へ進ませることを Requirement 2 の判定責務に含める。
- 2026-06-09 の再確認により、後追い intent 追加を既存システムに適用する場合は、既存 requirements の有無だけで終了せず、受け皿 feature を reopen して requirements／design／tasks／implementation へ順に再展開することを Requirement 9 に明示した。
- 2026-06-09 の判定点プロンプト方針確認により、`WORKFLOW_DISCIPLINE_MAP.yaml` を判定点ごとの `required_disciplines`／`required_inputs` の正本として Requirement 2 に明示した。将来の `effective prompt` はこのマップの元資料を束ねる。
- 2026-06-12 の reopen R-0（conformance 評価 `2026-06-12-completed-followup-conformance.md` の gap 反映）により、Requirement 8 へ feature 一覧解決の外出し（受入 6：`feature_order` キーと探索順）、整合検査（受入 7）、立ち上げ案内（受入 8：`feature_definition_required`）を追加した。語彙は利用者決定（案 A、MLE-DEC-001）により実装語彙 `feature_order` へ統一し、旧称 `phase_order` は受入 2 の由来注記で読み解く。実装は先行済み（コミット cde1f5c、maintenance side track `stages/completed/maintenance-2026-06-11-feature-order-generalization.yaml`）で、本改訂は仕様の追認である。
- 2026-06-12 の reopen R-0（parse-error-failclosed、MLE-DEC-005）により、Requirement 8 受入 9 を新設し、パース不能ファイルの扱いを立ち上げ案内（OK）から遮断（DEVIATION、fail-closed）へ改めた。本改訂は実装先行ではなく、仕様確定後に TDD で実装する正順の手続きである。
- 2026-06-14 の reopen R-0（review-wave-summary-command、D-001）により、Requirement 10 を新設し、review-wave 横断確認指標の機械生成（要約コマンド）を機能内の静的検査として要件化した。分類は意図文書を改めず既存「静的検査」（Requirement 1）の範囲に含める R-0 とした（2026-06-13 記録の R-1 ラベルと併記説明文の食い違いを 2026-06-14 に利用者と確認のうえ R-0 を採用。根拠は `docs/reviews/reopen-classification-2026-06-14-wm-review-wave-summary-command.md`）。本改訂は仕様確定後に TDD で実装する正順の手続きである。
- 2026-06-15 の reopen R-0（decision-source-lint）により、Requirement 11 を新設し、重要決定の出典検査（束ね検出・逐語照合・内容性）と構造化した重要決定の記録形式を要件化した。既存規律 `discipline_approval_operation`／`discipline_plain_explanation_each_step` の機械強制であり、意図文書を改めず既存「静的検査」（Requirement 1）と「不可逆操作の直前ゲート」（Requirement 4）の範囲に含める R-0 とした（根拠は `docs/reviews/reopen-classification-2026-06-15-wm-decision-source-lint.md`）。動機事例は PLC-DEC-007 の誤記録（裁定負荷）。本改訂は仕様確定後に TDD で実装する正順の手続きである。
- 2026-06-15 の reopen R-0（commit-approval-nonce）により、Requirement 4 受入 6〜7 を追加し、LLM 介在 commit 承認を staged 内容に束縛した nonce challenge 経由で記録・検査すること、および commit 承認 nonce 判定を操縦 LLM／provider／model に依存させないことを要件化した。既存「不可逆操作の直前ゲート」の commit 承認レコード強化であり、意図文書・feature-partitioning は改めない（根拠は `docs/reviews/reopen-classification-2026-06-15-wm-commit-approval-nonce.md`）。本改訂は仕様確定後に TDD で実装する正順の手続きである。
- 2026-06-16 の reopen R-0（commit-execution-delegation-formal-cli）により、Requirement 4 受入 8 を追加し、staged content approval と LLM commit 実行代行承認を分離したまま、実行代行承認を正式 CLI で記録・検査することを要件化した。既存「不可逆操作の直前ゲート」の commit 承認レコード強化であり、runtime JSON 手編集を正規経路にしない（根拠は `docs/reviews/reopen-classification-2026-06-16-wm-commit-execution-delegation.md`）。本改訂は仕様確定後に TDD で実装する正順の手続きである。
- 2026-06-16 の reopen R-0（operation-registry-preflight-unified-design）により、Requirement 12 を新設し、review-run、post-write verification、triage、reopen、commit approval、session-record、deployment / export などの操作を operation contract と read-only preflight で扱うことを要件化した。個別 helper の追加ではなく、正本コマンド、入力、成果物、順序、pending 衝突、worktree 状態、上書き policy を操作開始前に同じ形式で検査する横断基盤として扱う（根拠は `docs/reviews/reopen-classification-2026-06-16-wm-operation-registry-preflight.md`）。requirements approval 後の再確認で、`next` から reopen scope と impact review scope が一意に読める必要があると判明したため、受入 13 を追加し、requirements 後段を再実施対象へ戻した。本改訂は仕様確定後に TDD で実装する正順の手続きである。
- 2026-06-17 の maintenance（next-json-unique-state）により、D-003 rollback 退避資料 `/private/tmp/reviewcompass-d003-rollback-20260617/files/docs/notes/2026-06-16-next-json-unique-state-redesign.md` を根拠として、Requirement 2 受入 9、Requirement 5 受入 6、Requirement 12 受入 14 を追加した。`next --json` を状態投影ではなく唯一 action selector とし、maintenance / reopen blocker / commit stop point / active gate の相互排他を要件化する。本改訂は退避後の単独 maintenance として TDD で実装する正順の手続きである。
- 2026-06-18 の reopen R-0（phase1-schema-definitions）により、Requirement 2 受入 10・11 を追加した。Phase 0（D-003 選択層 TDD 実装）の開始前提として、`required_action` 19語彙スキーマ（`.reviewcompass/schema/required_action.schema.json`）と `next --json` 応答スキーマ（`.reviewcompass/schema/next_action_response.schema.json`）の定義を要件化する。根拠は `docs/notes/2026-06-18-integrated-design-selection-execution-layers.md` §7 item 2 および `docs/notes/working/2026-06-16-next-json-unique-state-redesign.md` §4.1・§4.2。実装は仕様確定後に TDD で行う正順の手続きとする（失敗テスト `tests/tools/test_phase1_schema_definitions.py` は作成済み）。
- 2026-06-19 の統合設計メモ追記補完により、Requirement 13〜16 を追加した。2026-06-18 セッション 77e272a2 では `docs/notes/2026-06-18-integrated-design-selection-execution-layers.md` と `docs/notes/working/2026-06-18-mechanized-workflow-execution-design.md` の全体を intent／requirements へ織り込む依頼だったが、直前の「Phase 1 の最小限」議論に引かれて AC10・AC11 のみが追記された。今回、統合設計 §3〜§5、Phase 0〜6、機械化設計 §3〜§10 を要件層へ戻し、operation contract 語彙、承認ゲート、側道スタック、状態スナップショット、構造化有効プロンプト、段階的実装計画を正本要件化した。経緯は `docs/notes/working/2026-06-19-integrated-design-requirements-missing.md`。
- 2026-06-26 の reopen R-0（next-json-kind-redesign）により、Requirement 2 受入 12 を新設した。`commit_candidate` / `commit_mixing_risk` / `commit_unit_stale` の3種類の判定を `next --json` の `kind` から除外し `commit-preflight` サブコマンドへ集約すること、および `next --json` の `kind` を作業の現在地を示す7種類（`completed` / `in_progress` / `blocking_in_progress` / `verification_pending` / `reopen_in_progress` / `feature_definition_required` / `unknown`）に限定することを要件化する。これらの判定は「作業の現在地カテゴリ」ではなく「コミット操作の前確認」であるため、`next --json` の出力インターフェイスを所有する Requirement 2 の管轄とした。設計の詳細は `docs/notes/2026-06-26-next-json-kind-redesign.md` を正本とする（根拠は `docs/reviews/reopen-classification-2026-06-26-wm-next-json-kind-redesign.md`）。本改訂は仕様確定後に TDD で実装する正順の手続きである。
- 2026-07-01 の reopen R-0（backlog-candidate-routing）により、Requirement 2 受入 13 を新設した。backlog を work lane や execution entry point ではなく候補置き場に限定し、work lane を SDD workflow / reopen / maintenance として扱うこと、TODO を backlog materialization の標準中間物として使わないこと、maintenance 候補は checklist 直行、それ以外は SDD workflow または reopen へ送ること、既存 TODO-only 候補を plan record に戻すこと、`next --json`・自律実行トリガー・commit preflight・既存 helper をこの方針へ整合させることを要件化した。根拠は `docs/reviews/reopen-classification-2026-07-01-wm-backlog-candidate-routing.md` と `.reviewcompass/backlog/plans/plan-2026-07-01-backlog-entry-lane-routing.yaml`。本改訂は仕様確定後に design / tasks / implementation へ連鎖し、TDD で実装する正順の手続きである。

削減・除去：

- 旧 Req 1（implementation conformance review の必須化）：ReviewCompass の所定手続き全体に統合（要件 5 の reopen を含む）
- 旧 Req 2（レビュー成果物と所見契約）：内容は §5.9（レビュー方法、所有者は本機能と evaluation の境界に位置）に整理
- 旧 Req 3（適合性メトリクス台帳）：§5.9.5 効果測定 3 指標に統合
- 旧 Req 4（signal と handback 連携）：Requirement 5 reopen の中に統合
- 旧 Req 5（governance artifact 検証）：Requirement 2 検査スクリプトに統合
- 旧 Req 6（workflow gate 状態と機能横断整合）：Requirement 4 ＋ Requirement 8 ＋ §5.5 の `cross-spec-alignment.yaml` に分散
- 旧 Req 7（intent review と phase-review メトリクス）：§5.5 の intent 層 ＋ §5.9.5 効果測定 3 指標に統合
- 旧 Req 8（reference-free case bootstrap）：ReviewCompass の対象アプリ配置（§5.23.7）に統合、本機能から外す
- 旧 Req 9（実行台帳と強制機構）：本仕様 Requirement 1〜4 の軽量版に置き換え。大規模機構は §5.4 で削除確定

機能横断レビューで対処された所見：

- 本機能に関連する所見：A-005（feature-dependency 依存記述の連想配列構造、Requirement 8 受入 2 で対処済み、2026-05-23）、A-007（self-improvement との権限分散調停、Boundary Context 隣接期待で対処済み、案 2 採用、2026-05-23 利用者承認）
- 参考：他機能の所見（A-001／A-003／A-004 とも 2026-05-23 対処済み）の対処履歴は carry-forward register 正本 [reviewcompass-import.yaml](../../../learning/workflow/carry-forward-register/reviewcompass-import.yaml) を参照

## 実装由来契約の波及トレース

- `XDI-WM-001`：post-write verification、commit approval、audit trail、autonomous ledger は、Requirement 2／3／4／8 の外部可視要件にまたがる。詳細な設計採用は design.md §実装由来契約の採用を正本とし、本 requirements.md は要件層から追跡可能であることを示す。
- `XDI-WM-002`：既存システムへの後追い intent 追加時に、受け皿 feature の reopen、下流工程の修正要否判定、既存設計との衝突確認、conformance-evaluation 評価記録の正式手続きへの取り込み、衝突候補発見時の停止・承認・記録を行う契約は Requirement 9 の外部可視要件に含める。詳細な設計・タスク化は design／tasks 段で確定する。
- `XDI-WM-004`：operation registry / preflight は、Requirement 12 の外部可視要件に含める。既存の `next`、post-write verification、commit approval、reopen、decision-source-lint、session-record guard などの部分対応を、操作単位の contract / preflight として束ねる。詳細な設計・タスク化は design／tasks 段で確定する。
- `XDI-WM-005`：統合設計メモ由来の選択層／実行層接続は、Requirement 13〜16 の外部可視要件に含める。`required_action` と operation contract の対応、承認ゲート、側道スタック、状態スナップショット、構造化有効プロンプト、Phase 0〜6 の段階的実装順序を要件層から追跡可能にする。詳細な設計・タスク化は design／tasks 段で確定する。
```

### .reviewcompass/specs/workflow-management/spec.json

content_mode: full_text
content_sha256: 0e22edd1545ede2a3f164958b22ecf8e92322ec3b523ab1096830e41b9b92424

```text
{
  "feature_name": "workflow-management",
  "language": "ja",
  "created_at": "2026-05-24T00:00:00+09:00",
  "updated_at": "2026-06-20T00:00:00+09:00",
  "workflow_state": {
    "intent": {
      "drafting": true,
      "review": true,
      "approval": true,
      "reference": "stages/intent.yaml"
    },
    "feature-partitioning": {
      "candidate-proposal": true,
      "approval": true,
      "reference": "stages/feature-partitioning/2026-05-24-proposal.md"
    },
    "requirements": {
      "drafting": true,
      "triad-review": true,
      "review-wave": true,
      "alignment": false,
      "approval": false
    },
    "design": {
      "drafting": true,
      "triad-review": true,
      "review-wave": true,
      "alignment": true,
      "approval": true
    },
    "tasks": {
      "drafting": true,
      "triad-review": true,
      "review-wave": true,
      "alignment": true,
      "approval": true
    },
    "implementation": {
      "drafting": true,
      "triad-review": true,
      "review-wave": true,
      "alignment": true,
      "approval": true
    }
  },
  "reopened": {
    "intent": true,
    "feature-partitioning": true,
    "requirements": true,
    "design": true,
    "tasks": true,
    "implementation": true
  },
  "recheck": {
    "upstream_change_pending": true,
    "impacted_downstream_phases": [
      "design",
      "tasks",
      "implementation"
    ]
  }
}
```

### stages/in-progress/reopen-procedure-2026-07-01.yaml

content_mode: full_text
content_sha256: fff01e2948a3f85fda265fee5526d1d26c8495498357b611a77c8980b6068f35

```text
process_id: reopen-procedure
feature: workflow-management
classification: R-0
started_at: '2026-07-01T00:00:00+09:00'
trigger: 候補1 backlog candidate routing discipline を reopen として開始
classification_basis: docs/reviews/reopen-classification-2026-07-01-wm-backlog-candidate-routing.md
completed_steps:
- 第1過程：R-0 判定確定・spec.json フラグ差し戻し完了（requirements alignment/approval → false、recheck=upstream_change_pending
  → true）
- 第2過程：正本修正完了（requirements.md に backlog candidate routing 受入13を追加）
next_step: 第2過程：停止点コミット
step_number: 2
pending_gates:
- stages/requirements.yaml#alignment
- stages/requirements.yaml#approval
current_blocker: null
reopen_step_records:
- from_step: 1
  completed_step: 第1過程：R-0 判定確定・spec.json フラグ差し戻し完了（requirements alignment/approval
    → false、recheck=upstream_change_pending → true）
  rationale: docs/reviews/reopen-classification-2026-07-01-wm-backlog-candidate-routing.md
    で R-0（workflow-management）と分類。候補1は backlog/TODO/checklist 運用前提の開き直しであり requirements
    起点で扱う。
  evidence:
  - docs/reviews/reopen-classification-2026-07-01-wm-backlog-candidate-routing.md
  - .reviewcompass/specs/workflow-management/spec.json
- from_step: 2
  completed_step: 第2過程：正本修正完了（requirements.md に backlog candidate routing 受入13を追加）
  rationale: workflow-management requirements に backlog は候補置き場、work lane は SDD workflow/reopen/maintenance、TODO
    は標準中間物にしない、既存 TODO-only 候補を plan record に戻す、関連機械処理を整合させる要件を追加した。
  evidence:
  - .reviewcompass/specs/workflow-management/requirements.md
  - docs/reviews/reopen-classification-2026-07-01-wm-backlog-candidate-routing.md
commit_stop_point: true
commit_stop_point_step: 2
commit_stop_point_kind: canonical_update_complete
commit_stop_point_reason: 第2過程の正本修正完了
```


## Target File Contents

### docs/reviews/reopen-classification-2026-07-01-wm-backlog-candidate-routing.md

content_mode: full_text
content_sha256: acd998e3d0f7304fdc15baa484319887c5bf1b4548bce054baaf67dcebcd4b0f

```text
---
date: 2026-07-01
classifier: codex
classification: R-0（workflow-management）
trigger_source: 利用者指示「reopen開始」。候補1 `plan-2026-07-01-backlog-entry-lane-routing` は、backlog を entry lane と見なした既存判断、plan -> TODO -> checklist の既存導線、TODO を backlog materialization として扱う運用を開き直すもの。
feature: workflow-management
finding: backlog-candidate-routing
---

## 分類根拠

候補1は、backlog / TODO / checklist / reopen / maintenance / autonomous execution / `next --json` / commit preflight の運用前提を見直す。具体的には、backlog を作業レーンまたは実行入口として扱わず「候補置き場」とし、作業レーンを SDD workflow / reopen / maintenance として再整理する。また、TODO を backlog materialization の標準中間物として使わず、maintenance は checklist 直行、それ以外は SDD workflow または reopen に送る方針を検討する。

手戻り種別：**R-0（requirements 起点。intent・feature-partitioning へは遡らない）**。

- intent（意図）：workflow-management の意図は、ワークフロー進行、不可逆操作、状態遷移、手続き記録、機械的な事前検査を扱うことである。backlog 候補の扱いと TODO 導線の見直しは、この既存意図内の運用契約変更であり、新しい意図を導入しない。
- feature-partitioning（機能分割）：対象は workflow-management が所有する backlog 候補、操作導線、reopen/maintenance 手続き、`next --json`、commit preflight 周辺の契約であり、既存 feature 境界で受けられる。新 feature は不要。

## 事実

- 対象 plan：`.reviewcompass/backlog/plans/plan-2026-07-01-backlog-entry-lane-routing.yaml`
- 同 plan は、旧 `plan-2026-07-01-backlog-text-format-resilience.yaml` を吸収済みである。
- 同 plan は、backlog を candidate holding area、作業レーンを SDD workflow / reopen / maintenance と定義している。
- 同 plan は、TODO を backlog materialization step として使わない方針を含む。
- 同 plan は、既存 TODO-only 候補を plan record に戻す作業、既実装の TODO 前提関数・運用規律・機械処理の調査修正を含む。
- 利用者確認により、候補1は maintenance 直行ではなく、既存判断の開き直しとして reopen に送る方が自然と判断した。

## feature impact 判定

| feature | decision | impact_basis | rationale |
| --- | --- | --- | --- |
| workflow-management | reopen_existing_feature | contract_ownership | backlog 候補、TODO/checklist 導線、reopen/maintenance 手続き、`next --json`、commit preflight、自律実行トリガーの運用契約を所有する。 |
| foundation | no_reopen_existing_feature | no_implementation_impact | 共通基盤の意図・機能境界を変更しない。 |
| runtime | indirect_check_only | consumer_or_derivative_only | session/handoff は手続きとして言及されるが、runtime の契約変更は現時点で不要。design 段または review-wave/alignment で、session/handoff の正本変更が不要であることを確認する。 |
| evaluation | no_reopen_existing_feature | no_implementation_impact | 評価・レビュー評価契約に変更なし。 |
| analysis | no_reopen_existing_feature | no_implementation_impact | 分析・可視化・報告機能に変更なし。 |
| self-improvement | indirect_check_only | consumer_or_derivative_only | 自律実行の証跡・候補提示に関係し得るが、主契約は workflow-management 側で扱う。design 段または review-wave/alignment で、self-improvement 正本変更が不要であることを確認する。 |
| conformance-evaluation | indirect_check_only | consumer_or_derivative_only | 逸脱検出や照合観点で確認対象になり得るが、主契約は workflow-management 側で扱う。design 段または review-wave/alignment で、conformance-evaluation 正本変更が不要であることを確認する。 |

新 feature 判定：no_new_feature。

## 再実施対象

- **workflow-management（R-0）**：requirements に backlog 候補置き場、SDD workflow / reopen / maintenance のレーン整理、TODO 非使用、maintenance checklist 直行条件、TODO-only 候補の plan 返却、既実装影響調査の受入基準を追加または更新する。
- **design**：SDD workflow と reopen の分類規則、backlog candidate routing、TODO 廃止後の機械処理、`next --json` / autonomous trigger / commit preflight との接続を設計する。
- **tasks**：既存 TODO 棚卸し、旧 TODO 前提関数の調査、不要関数・変更すべき運用規律・機械処理の修正タスクを定義する。
- **implementation**：TDD に従い、必要なテスト・実装修正・移行処理を行う。

impacted_downstream_phases：design／tasks／implementation。

## 第1過程停止点

reopen-start により in-progress ファイルを発行し、spec.json のフラグ差し戻し（workflow-management：requirements の alignment・approval を false、recheck＝upstream_change_pending を true・impacted_downstream_phases に design／tasks／implementation を設定）を行ったうえで、第1過程停止点として差し戻し内容の利用者承認を待つ。

## 現在の停止点

利用者承認後、requirements.md に backlog candidate routing の受入基準を追加した。現在は in-progress ファイル `stages/in-progress/reopen-procedure-2026-07-01.yaml` の `next_step` が示すとおり、第2過程「正本修正完了」の停止点コミット待ちである。
```


## Scope

- Check whether the changed target files clearly state the intended contract.
- Check whether related instructions are mutually consistent across targets.
- Check whether the documented procedure is actionable before API review, triage, manifest, or commit steps continue.

## Out Of Scope

- Do not request unrelated refactors or style-only rewrites.
- Do not judge files that are not listed in Target Files.
- Do not treat missing implementation work as a document defect unless the target text claims it already exists.

## Finding Policy

- Report must-fix findings for contradictions, missing required gates, or instructions that would allow an unsafe workflow action.
- Report should-fix findings for ambiguity that could cause repeated manual judgment or unnecessary API review loops.
- Return findings: [] when the target files are internally consistent for this review question.

## Sensitive Information Check

- status: passed
- External API review must not proceed if this section reports potential secrets.

