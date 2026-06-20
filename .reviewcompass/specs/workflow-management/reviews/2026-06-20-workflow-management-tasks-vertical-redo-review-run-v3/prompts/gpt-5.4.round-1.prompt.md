prompt_id: openai_review
provider: openai-api
model_id: gpt-5.4

# Task
Review the target document for the requested phase and criteria.

# Phase
triad-review

# Criteria
# Tasks Triad Review Target

criteria_id: workflow_management_tasks_vertical_intent_review_req_13_16_v3
phase: tasks
gate: stages/tasks.yaml#triad-review
run_id: 2026-06-20-workflow-management-tasks-vertical-redo-review-run-v3

## Scope Rule

Do not use full `requirements.md` or full `design.md` as review targets.

Use the verbatim source excerpt files listed below. They are original excerpts from the approved source documents, not LLM-authored restatements.

## Review Purpose

Review whether `workflow-management/tasks.md` correctly translates Requirement 13 through Requirement 16, through the approved design decisions, into implementation-ready tasks T-016 through T-019.

This is a vertical intent transfer review:

`requirements verbatim excerpts -> design verbatim excerpts -> tasks.md`

The review target is `tasks.md`. The requirements/design excerpt files are source materials for intent transfer only. `spec.json` and the reopen state file are source materials for workflow state consistency only.

## Target Files For Execution

Pass these as `--target` files:

- `.reviewcompass/specs/workflow-management/tasks.md`
- `.reviewcompass/specs/workflow-management/reviews/2026-06-20-workflow-management-tasks-vertical-redo-review-run-v3/source-excerpts/requirements-req13-16.verbatim.md`
- `.reviewcompass/specs/workflow-management/reviews/2026-06-20-workflow-management-tasks-vertical-redo-review-run-v3/source-excerpts/design-req13-16.verbatim.md`
- `.reviewcompass/specs/workflow-management/spec.json`
- `stages/in-progress/reopen-procedure-2026-06-19.yaml`

Do not pass full `.reviewcompass/specs/workflow-management/requirements.md`.
Do not pass full `.reviewcompass/specs/workflow-management/design.md`.

## Source Material Contract

- `requirements-req13-16.verbatim.md` is the original text of `requirements.md` lines 217-297.
- `design-req13-16.verbatim.md` is the original text of `design.md` lines 1563-2087.
- These files must be treated as source materials, not review targets.
- Do not evaluate whether the requirements or design text should be changed unless `tasks.md` exposes a contradiction that cannot be resolved at the tasks level.
- Do not infer missing upstream intent from memory, previous conversations, or LLM-authored restatements.

## Source Field Index

This section is an index into the verbatim excerpt files, not a restatement of their content.

purpose:
- Read the Objective paragraphs in `requirements-req13-16.verbatim.md`.
- Read the opening paragraphs of each Requirement 13-16 design model in `design-req13-16.verbatim.md`.

responsibility_boundaries:
- Read the source-of-truth, read-only / mutating, approval, side-track, prompt, phase, and proxy boundary statements in the verbatim excerpt files.

acceptance_criteria:
- Read the numbered acceptance criteria in `requirements-req13-16.verbatim.md`.
- Read the schema, table, baseline, and phase-plan requirements in `design-req13-16.verbatim.md`.

forbidden_actions:
- Treat prohibitions in the verbatim excerpt files as binding when judging `tasks.md`.
- Do not infer additional prohibitions from memory or prior conversation.

unresolved_or_design_deferred_items:
- Treat implementation-phase schema, contract, checker, and CLI work that the verbatim excerpts leave to tasks / implementation as deferred source material.

intended_target_phase_transfer:
- Judge only whether `tasks.md` carries the verbatim excerpt requirements and design decisions into T-016 through T-019 at implementation-ready task granularity.

## Required Checks

1. Check whether T-016 transfers Requirement 13 and the approved design excerpt into implementation-ready task work, including operation contract / registry boundaries, all 19 `required_action` mappings, branch/internal step semantics, approval aggregation, side effects, preconditions / postconditions, and read-only preflight boundaries.
2. Check whether T-017 transfers Requirement 14 and the approved design excerpt into implementation-ready task work, including approval gate record schema, human-only / proxy-allowed / advisory boundaries, digest binding, side track stack LIFO / return rules, snapshot drift detection, and read-only vs mutating operation separation.
3. Check whether T-018 transfers Requirement 15 and the approved design excerpt into implementation-ready task work, including structured effective prompt manifest, language task I/O, source digest coverage, prompt audit, machine-task leakage checks, rounds recording, migration compatibility, and Phase 6 judge-audit limits.
4. Check whether T-019 transfers Requirement 16 and the approved design excerpt into implementation-ready task work, including Phase 0-6 order, entry / exit criteria, forbidden operations, active reopen scope vs impact review scope, proxy triage decision completeness, human-required predicate precedence, and review-wave consumer impact blocking.
5. Check whether T-016 through T-019 each have task-level implementation detail: owned files, prerequisite tasks, first failing tests, implementation order, completion conditions, verification commands, forbidden actions, and stop conditions.
6. Check whether tasks.md has stale counts, stale traceability rows, missing Requirement 13-16 coverage, inconsistent task IDs, or contradictory completion criteria.
7. Check whether tasks.md contradicts existing T-014 registry / preflight responsibilities, existing T-015 schema work, or the approved design excerpt by moving the wrong source of truth into the wrong task.
8. Check whether `spec.json` and `stages/in-progress/reopen-procedure-2026-06-19.yaml` show the correct state: requirements and design complete, tasks drafting complete, tasks triad-review / review-wave / alignment / approval incomplete, implementation incomplete, and recheck still pending for tasks / implementation.

## Out Of Scope

- Do not review full requirements.md.
- Do not review full design.md.
- Do not request implementation code changes in this tasks triad-review.
- Do not judge downstream implementation correctness.
- Do not require other features to be edited during this gate; cross-feature consumer impact belongs to tasks review-wave.
- Do not reopen requirements or design unless tasks.md exposes a real contradiction that cannot be fixed at tasks level.
- Do not judge unrelated wording outside Requirement 13 through Requirement 16 unless it directly breaks these tasks.

## Finding Policy

- Report `must-fix` for missing task coverage of approved upstream excerpts or approved design excerpts, broken requirement-to-design-to-task traceability, stale workflow state that falsely claims an uncompleted gate, source-of-truth inversions that would make implementation unsafe, human/proxy boundary violations, or tasks that bypass required commit / approval / review boundaries.
- Report `should-fix` for ambiguity likely to cause repeated manual judgment, weak TDD completion criteria, unclear file ownership, weak phase ordering, or traceability that exists but is too coarse for implementation.
- Report `leave-as-is` or no finding when tasks are traceable, internally consistent, implementation-ready, and correctly scoped for a tasks drafting artifact.

## Output Requirements

Return findings as structured YAML-compatible content with these fields for each finding:

- `severity`: `ERROR`, `WARN`, or `INFO`
- `target_location`: file path and section
- `description`: plain-language problem statement
- `rationale`: why the issue matters for requirements excerpt -> design excerpt -> tasks transfer
- `recommendation`: the smallest scoped correction

If there are no substantive findings, return an explicit no-findings result and briefly state which checks passed.


# Output contract
Return YAML only.
The top-level key must be exactly findings.
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

If there are no findings, return exactly:

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
.reviewcompass/specs/workflow-management/tasks.md
.reviewcompass/specs/workflow-management/reviews/2026-06-20-workflow-management-tasks-vertical-redo-review-run-v3/source-excerpts/requirements-req13-16.verbatim.md
.reviewcompass/specs/workflow-management/reviews/2026-06-20-workflow-management-tasks-vertical-redo-review-run-v3/source-excerpts/design-req13-16.verbatim.md
.reviewcompass/specs/workflow-management/spec.json
stages/in-progress/reopen-procedure-2026-06-19.yaml

# Target document
## .reviewcompass/specs/workflow-management/tasks.md

---
spec: workflow-management
phase: tasks
stage: drafting
author:
  identity: claude-opus-4-7
  role: drafter
created_at: 2026-05-28
updated_at: 2026-06-19
language: ja
---

# Tasks Document：workflow-management

## 概要（Overview）

本文書は `workflow-management`（所定手続きの定義と機械強制を担う機能）の実装タスクを列挙する。本機能は、所定手続きの段集合定義、軽量版検査スクリプト、起草者と判定者の分離機械検査、不可逆操作の直前ゲート、reopen 機械強制、session 跨ぎ状態管理、多層防御の第 1 層位置付け、機能依存マップの一元化、既存システムへの後追い intent 追加時の下流再展開、operation contract 語彙、承認ゲート／side track stack／workflow-state snapshot、構造化有効プロンプト、proxy_model triage decision 機械処理化を担う。計画書 §5.4「軽量化方針」に従い、思想は継承、実装は 1／10 を目標として再設計する。

タスクは設計文書（design.md）の所有モデル単位でまとめ、各タスクは「起草・実装・テスト・コミット」まで一気通貫で完結できる粒度とする。タスクの依存順は design.md §全体構造（リポジトリ内配置の 3 層構造）と各 Requirement 対応モデル節に従う。

## タスク粒度と方針（Granularity and Policy）

- **粒度**：1 タスク ＝ 1 つの所有モデル領域。design.md の節と必ずしも 1 対 1 でなく、密接に関連する節は同じタスクにまとめる。tasks.md は implementation drafting へ直接入れる粒度で書く。各タスクには、実装対象ファイル、最初に書く失敗テスト、実装順序、完了条件、検証コマンド、禁止事項、停止条件を含める
- **一気通貫**：1 タスクは「起草・実装・テスト・コミット」まで止めず連続で進められる単位
- **依存順**：前提タスクが完了してから後続タスクに進む
- **自律進行**：実装段で per-task 承認は取らず、コミット・プッシュ・spec.json 更新・フェーズ移行のみ明示承認（規律 [[implementation-autonomy]] 準拠）
- **テスト要件**：成果物は静的検証（YAML スキーマ整合、述語値域、必須節充足、front-matter 異名）と動的検証（fail-closed の遮断、reopen 連鎖の actor=human 停止、後追い intent の下流再展開、drafting-before-review 防止）で機械的に判定可能とする
- **contract consumer 原則**：foundation が所有する語彙正本を再定義せず参照のみで使用。本機能が実際に参照するのは `review_mode`（レビューモード語彙、front-matter 検査 T-005 で使用）であり、所見系（`counter_status`／`severity`／`final_label`／`confidence_label`）・状態軸系（`run_status`／`validator_status`／`human_signoff_status`／`evidence_class`）は本機能の責務外で参照しない（A-003 対処 2026-05-28）。本機能所有の正本（`completion_predicate` 述語集合 7 値 ／ `verdict` 3 値 OK／WARN／DEVIATION ／ 手戻り種別記号 5 値 N／R／D／A／I ／ 依存種別 2 値 `hard`／`review`）は本機能で確定
- **fail-closed の徹底**：結論不能（YAML パースエラー、必須フィールド欠落、未知の値）の場合は合格判定を出さず必ず fail を返す（判断 3 全面採用）
- **implementation-drafting.md 非採用**：implementation-drafting.md は正本成果物として採用しない。implementation drafting は、tasks.md に従って実際のテストと実装コードを生成する段である。実装前の手順整理が必要な場合も、正本は tasks.md のタスク記述粒度で担保し、別の implementation plan 文書を完了条件にしない

`workflow-management` 全体で 19 タスク（T-012 は 2026-06-14 reopen R-0、T-013 は 2026-06-15 reopen R-0 decision-source-lint、T-014 は 2026-06-16 reopen R-0 operation registry / preflight、T-015 は 2026-06-18 reopen R-0 phase1-schema-definitions、T-016〜T-019 は 2026-06-19 reopen R-0 integrated design Requirement 13〜16 で追加）。2026-06-15 reopen R-0 commit-approval-nonce と 2026-06-16 reopen R-0 commit-execution-delegation-formal-cli は新タスクを増やさず、既存の commit 直前ゲート領域である T-004／T-006／T-011 へ展開する。

2026-06-16 reopen R-0 の design triad-review で利用者が選択した案A（commit 実行代行承認を別ファイル化する案）は、保存先と検証対象を分離する設計変更であり、所有領域は既存の commit gate 領域に収まる。したがって T-004 が CLI 入口、T-006 が runtime record と gate 判定、T-011 が統合・回帰テストを担う。

## タスク一覧（Task List）

### T-001：成果物配置の準備

- **対応設計節**：design.md §全体構造、§段集合の静的列挙モデル §1
- **対応要件**：Requirement 1 受入 1（段集合の静的列挙）、Requirement 6 受入 1（進行中状態ファイル配置）
- **責務**：リポジトリ内に `stages/` ディレクトリと配下の 9 ファイル骨格、`stages/in-progress/` と `stages/completed/` の 2 サブディレクトリ、検査スクリプト配置先 `tools/`、ログ書き出し先 `docs/logs/`、reopen 種別判定根拠ファイル配置先 `docs/reviews/`、種別判定根拠ファイル雛形配置先 `templates/review/` を新設し、各ディレクトリに配置目的を記す README を置く。`stages/in-progress/.gitkeep` と `stages/completed/.gitkeep` で空ディレクトリを Git 追跡可能にする（foundation T-001 ／ runtime T-001 ／ evaluation T-001 ／ analysis T-001 の方針継承）
- **前提タスク**：なし（起点）
- **成果物**：
  - `stages/README.md`
  - `stages/in-progress/.gitkeep`
  - `stages/in-progress/README.md`
  - `stages/completed/.gitkeep`
  - `stages/completed/README.md`
  - `docs/logs/README.md`（`workflow-precheck.log` の所在説明、初版は空ログ。ログの現行書き出し先は `.reviewcompass/runtime/logs/`、2026-06-12 配置規約 PLC-DEC-004〜005 反映。既存配置は凍結保全）
  - `docs/reviews/README.md`（`reopen-classification-<日付>.md` の所在説明）
  - `templates/review/reopen_classification_template.md`（reopen 種別判定根拠ファイルの雛形＝空の骨格を配置。内容の確定は T-007 が担い、本ファイルの成果物所有は T-001 単独、A-010 対処 案 2 2026-05-28）
  - `docs/operations/WORKFLOW_MANAGEMENT.md`（アプリ側規約節を追記、計画書 §5.4〜§5.8 由来）
  - `tools/README.md`（検査スクリプト配置先 `tools/` の説明、実体 `.py` は T-004 で配置。`tests/` との対称化、F-017 対処 2026-05-28）
  - `tests/workflow-management/.gitkeep`
- **完了条件**：
  1. `stages/` 配下のディレクトリ構造（直下 9 ファイル骨格 ＋ `in-progress/` ＋ `completed/`）と各 README が存在し、`docs/operations/WORKFLOW_MANAGEMENT.md` に配置規約が記述されている。`tools/` ディレクトリに README が存在し Git 追跡可能である（F-017 対処 2026-05-28）
  2. `templates/review/reopen_classification_template.md` が design.md §reopen 機械強制モデル §4 の最低限の構造（front-matter ＋分類根拠節）を満たす
  3. `tests/workflow-management/.gitkeep` が Git に追跡可能な状態である
- **テスト要件**：ディレクトリ存在検査、README 存在検査、`reopen_classification_template.md` 必須節検査、`.gitkeep` 存在検査

### T-002：機能依存マップ（feature-dependency.yaml）

- **対応設計節**：design.md §機能依存マップモデル §1〜§6、§主要な設計判断 判断 6
- **対応要件**：Requirement 8 受入 1〜5
- **責務**：`stages/feature-dependency.yaml` を作成、7 機能（foundation／runtime／evaluation／analysis／workflow-management／self-improvement／conformance-evaluation）の `features.<機能>.depends_on` と `feature_order`（機能間処理順。旧称 phase_order、requirements.md Requirement 8 受入 2 の由来注記参照）を一元保管。`depends_on` の 2 形式（単純リスト構造 ／ 連想配列構造）を許容し、`conformance-evaluation` のみ連想配列構造（`hard` ／ `review` 併記）。`feature_order` は 7 機能を依存マップ順で列挙。本機能が単独所有・他機能は再定義せず参照のみ、を運用文書に明示
- **前提タスク**：T-001
- **成果物**：
  - `stages/feature-dependency.yaml`（features ＋ feature_order）
  - パース仕様の正本：`tools/check-workflow-action.py` の解決・整合検査の実装（`resolve_feature_order`・`validate_feature_order_consistency`・`depends_on` 解釈）とそのテスト（単純リスト構造 ／ 連想配列構造の許容、値域 `hard` ／ `review` の 2 値、それ以外は結論不能）。独立した JSON Schema ファイルは作成しない（MLE-DEC-002、2026-06-12 利用者決定。当初計画の `stages/feature-dependency.schema.json` を実装検査で代替）
  - `docs/operations/WORKFLOW_MANAGEMENT.md` の §機能依存マップ節（所有者明示、改廃ルール）
- **完了条件**：
  1. `feature-dependency.yaml` の `features` に 7 機能すべてが列挙、`feature_order` が 7 機能を依存マップ順で列挙
  2. `conformance-evaluation` の `depends_on` が連想配列構造で `foundation: hard ／ runtime: review ／ evaluation: review ／ workflow-management: review` を保持
  3. `hard` ／ `review` 以外の値が結論不能になることが、検査ツールの実装とテストで機械検証される（MLE-DEC-002）
  4. 単純リスト構造と連想配列構造の両方が検査ツールでパース可能であることが機械検証される
- **テスト要件**：パース仕様の実装検査テスト、7 機能列挙テスト、依存マップ順テスト、連想配列構造の値域テスト（`hard` ／ `review` ／ 不正値 `weak` ／ 空文字 ／ null の 5 ケース）、依存循環検出テスト

### T-003：段集合 YAML 8 ファイル（9 ファイル体制のうち feature-dependency.yaml を除く）

- **対応設計節**：design.md §段集合の静的列挙モデル §1〜§4、§テンプレート変数の展開規則
- **対応要件**：Requirement 1 受入 1〜5、Requirement 5 受入 1〜5（reopen-procedure.yaml の構造）
- **責務**：`stages/` 配下に 8 ファイル（`intent.yaml` ／ `feature-partitioning.yaml` ／ `requirements.yaml` ／ `design.yaml` ／ `tasks.yaml` ／ `implementation.yaml` ／ `reopen-procedure.yaml` ／ `cross-spec-alignment.yaml`）を作成。各 YAML は段集合（段名・`actor`・`artifact_paths`・`required_sections`・`completion_predicate`）を静的列挙、機能横断段は `feature_order: feature-dependency.yaml#feature_order` を参照。テンプレート変数（`{feature}` ／ `{phase}` ／ `{日付}`）の展開規則は設計書 §テンプレート変数の展開規則に従う。`reopen-procedure.yaml` に `trigger_map` を持たせ（第3過程で参照）、種別記号 N／R／D／A／I × 深さの二次元表記から再実施対象を機械的に決定。`cross-spec-alignment.yaml` は段集合本体を後続フェーズで確定する旨を YAML コメントに明記、枠のみ確保
- **前提タスク**：T-001、T-002（`feature_order` 参照先）
- **成果物**：
  - `stages/intent.yaml`（drafting／review／approval の 3 段、actor=human／llm／human）
  - `stages/feature-partitioning.yaml`（candidate-proposal／approval の 2 段、actor=llm／human）
  - `stages/requirements.yaml`（drafting／triad-review／review-wave／alignment／approval の 5 段、機能横断段 3 段は `feature_order` 参照）
  - `stages/design.yaml`（同 5 段）
  - `stages/tasks.yaml`（同 5 段）
  - `stages/implementation.yaml`（同 5 段）
  - `stages/reopen-procedure.yaml`（4 過程構成、`trigger_map` ＋ `actor_resolution: per_target_stage` を第3過程で参照）
  - `stages/cross-spec-alignment.yaml`（枠のみ、段集合は後続フェーズで確定）
  - `stages/stage_schema.json`（段集合 YAML 共通スキーマ：段名・actor・artifact_paths・required_sections・completion_predicate・feature_order・front_matter_required）
- **完了条件**：
  1. 8 ファイルすべてが配置、各 YAML が `stage_schema.json` で構造検証を通る。`stage_schema.json` は `completion_predicate` を 7 値（design §軽量版検査スクリプトモデル §3 確定）に、`actor` を 3 値（`human` ／ `llm` ／ `proxy_model`、design §段集合 §1／§3 確定）に enum で値域制限し、いずれも未知の値が DEVIATION（fail-closed）になることが機械検証される（F-015／A-004 対処 2026-05-28）
  2. 機能横断段（review-wave／alignment／approval）が `feature_order: feature-dependency.yaml#feature_order` を参照、機能単位段（drafting／triad-review）は `feature_order` を持たない
  3. `reopen-procedure.yaml` の `trigger_map` が手戻り種別 N-0 ／ R-0〜1 ／ D-0〜2 ／ A-0〜3 ／ I-0〜4 の全 15 種について再実施対象段リストを保持
  4. `trigger_map` 各エントリの参照先段（`<YAML ファイル>#<段名>` 形式）が、`actor_resolution: per_target_stage` により段定義から動的解決可能であることが機械検証される
  5. テンプレート変数 `{feature}` ／ `{phase}` ／ `{日付}` の展開元と解決規則が `stage_schema.json` の構造化フィールド（各変数の展開元を列挙する `template_vars` 等）に格納され、フィールドの存在が機械検証される（自由記述コメントの grep ではなく構造化、F-010 対処 案 2 2026-05-28）
- **テスト要件**：8 ファイルすべての構造検証、`feature_order` 参照解決テスト、`trigger_map` 全 15 種テスト、テンプレート変数展開テスト（3 種それぞれ）、`cross-spec-alignment.yaml` の枠のみ確保テスト、`completion_predicate` 値域 7 値テスト（7 値 OK ＋ 未知値 DEVIATION）、`actor` 値域 3 値テスト（human ／ llm ／ proxy_model OK ＋ 未知値 DEVIATION、F-015／A-004 対処 2026-05-28）

### T-004：軽量版検査スクリプト本体（補助層 C 段階 2）

- **対応設計節**：design.md §軽量版検査スクリプトモデル §1〜§4、§主要な設計判断 判断 2 ／ 判断 3 ／ 判断 8
- **対応要件**：Requirement 2 受入 1〜5、Requirement 4 受入 2 ／ 3 ／ 6 ／ 7 ／ 8（fail-closed、独立走行、commit approval nonce challenge、LLM 非依存判定、commit execution delegation formal CLI）、Requirement 8 受入 6〜8（feature 一覧解決・整合検査・立ち上げ案内）、Requirement 9 受入 2 ／ 5（drafting-before-review と下流再展開判定）
- **責務**：`tools/check-workflow-action.py` を Python で実装。3 サブコマンド（`spec-set <feature> <phase> <stage> <new_value> [--rationale "..."]` ／ `commit --rationale "..."` ／ `push --rationale "..."`）と next サブコマンド、`--json` 出力オプションを提供。next サブコマンドは標準のワークフロー遷移入口として `workflow_state`、`stages/in-progress/`、reopen pending、post-write-verification pending、上流成果物が下流成果物より新しい状態を読み、次作業を返す。完了済み workflow でも、intent → feature-partitioning、feature-partitioning → requirements、requirements → design、design → tasks、tasks → implementation の順で上流更新後の再展開漏れを `upstream_recheck` として返す。`docs/operations/WORKFLOW_DISCIPLINE_MAP.yaml` を読み、判定点ごとの `required_disciplines` と `required_inputs` を `next_action` に含める。このマップは判定点ごとの `effective prompt` 生成に使う元資料の正本である。`next` は判定点ごとの元資料を 1 本の prompt に束ね、`.reviewcompass/runtime/effective-prompts/` に保存し（旧 `.reviewcompass/effective-prompts/` からの変更は 2026-06-12 配置規約 PLC-DEC-004・009〜011 反映、旧パス読み取り互換は P3 まで維持）、`next_action.effective_prompt` の `effective_prompt_path`、`effective_prompt_sha256`、`effective_prompt_loaded` として返す。元資料を読めない場合は `effective_prompt_loaded: false` とし、`DEVIATION` で fail-closed する。`tools/api_providers/run_role.py` と `tools/api_providers/run_review.py` は review-run の `rounds.yaml` に `effective_prompt_path` と `effective_prompt_sha256` を記録する。後追い intent を既存システムへ適用する reopen では、pending_gates が triad-review を指していても、対応 phase の `drafting_completed_gates` または `completed_gates` に `stages/<phase>.yaml#drafting` がなければ、next は triad-review ではなく `run_reopen_drafting` を返す。verdict 3 値（OK／WARN／DEVIATION）と exit code（0 ／ 1 ／ 2）の対応。`completion_predicate` 述語集合 7 値（`artifact_exists` ／ `artifact_exists_and_sections_present` ／ `artifact_exists_and_sections_present_and_author_reviewer_distinct` ／ `all_features_drafting_and_triad_review_completed` ／ `cross_spec_alignment_passed` ／ `explicit_human_approval_recorded` ／ `depends_on_resolves_correctly`）の判定ロジックを符号化。post-write target detection と manifest verification を実装契約として扱い、completed manifest の `target_files`、`target_sha256`、`required_verifiers`、`verifications[]`、`unresolved_substantive_findings` を検査する。feature 一覧と機能順は `feature-dependency.yaml` の `feature_order` キーから解決する（ツール実行時のカレントディレクトリ基準で `.reviewcompass/feature-dependency.yaml` → `stages/feature-dependency.yaml` → `feature-dependency.yaml` の順、最初に存在した 1 ファイルのみ、遡上探索なし。`resolve_feature_order`。design §機能依存マップモデル §7、2026-06-12 反映）。ファイル不在・`feature_order` 未定義は `next_action.kind: feature_definition_required`（verdict OK、exit 0）で intent／feature-partitioning の実施を案内し、探索で選ばれた 1 ファイルが読めない場合（パース不能・空・最上位が連想配列でない場合を含む。値の整合検査より先に判定）と `feature_order` と `depends_on` の整合違反（依存先行違反・循環、`validate_feature_order_consistency`）は `next_action.kind: unknown`・`reasons` 列挙・DEVIATION（exit 2）で遮断する（パース不能は破損ファイルのパスと内容確認を促す理由、空の場合は `feature_order` の記録を促す理由を含める）。fail-closed の既定（YAML パースエラー（段集合・feature-dependency とも） ／ 証跡欠落 ／ 必須フィールド欠落 ／ `feature_order` 整合違反で遮断。feature-dependency.yaml の不在・未定義のみ立ち上げ案内として OK）を全面採用（パース不能の遮断分離は MLE-DEC-005 により本契約へ反映、FUP-2026-06-12-001 解消、2026-06-12）。`.reviewcompass/runtime/logs/workflow-precheck.log` への追記（旧 `docs/logs/workflow-precheck.log` からの変更は同配置規約反映。commit 承認記録も同様に `.reviewcompass/runtime/approvals/commit-approval.json` へ〔旧 `.reviewcompass/approvals/commit-approval.json`〕）、出力形式は `[VERDICT]` ／ `[ACTION]` ／ `[REASON]` ／ `[CURRENT STATE]` の 4 ブロック大括弧付きラベル形式。**凍結期（P3 まで）の責務（2026-06-12 配置規約反映、正本は design §実行時生成物の凍結期（P3 まで）の扱い）**：実行時生成物 3 パス（検査ログ・effective prompt・commit 承認記録）の書き込みは常に新配置とし、旧配置（`docs/logs/workflow-precheck.log`・`.reviewcompass/effective-prompts/`・`.reviewcompass/approvals/commit-approval.json`）への新規書き込みを行わない（凍結契約。効力発生は P1 実装反映コミット＝書き込み先切替と同時。互換の終了は P3 の専用 reopen における設計改訂として扱い、暗黙の終了はない）。読み取りは新配置優先・旧配置フォールバック（**新→旧の順**、3 パスとも P3 まで）。新旧いずれにも記録がない場合は各ツールの既存挙動（検査ログの初回新規作成、effective prompt 元資料欠落の DEVIATION fail-closed、commit 承認記録不在のガード遮断）に従い、本配置変更はそれらの挙動を変えない
- **next unique action selector 補足責務**：`next --json` は状態投影ではなく唯一 action selector として `required_action`、`active_gate`、`blocked_by`、`action_parameters` を返す。maintenance は `required_action=run_maintenance` に固定し、個別 action 名は `maintenance_action` へ分離する。reopen では `current_blocker` を `wait_for_human_decision`、`commit_stop_point: true` を `commit_stop_point` として pending gate より優先し、第3過程で停止点がない場合だけ `run_reopen_drafting` / `run_reopen_pending_gate` を active gate とする。
- **commit 承認 nonce 補足責務**：`tools/check-workflow-action.py` に `commit-approval prepare --json`、`commit-approval record --nonce <nonce> --source-text-stdin --json`、`commit-approval record --nonce <nonce> --no-source-text --json`、`commit-approval invalidate --json` を追加する。承認本文を argv で受け取る経路は提供しない。`--json` 指定時の正常系出力は機械可読 JSON に限定し、happy path で自由文を混在させない。これらのサブコマンドは T-006 の `commit_approval.py` を呼び、challenge／承認レコードの生成・検証・invalidate・consume を行う。承認本文を保存する場合は `tools.session_record_extractor.redact.redact_text` と `find_residual_secrets` を通し、保存不能時は T-006 の `source_omission_reason` enum に従う。
- **commit 実行代行承認補足責務**：`tools/check-workflow-action.py` に `commit-approval delegate-execution --nonce <nonce> --source-text-stdin --json` を追加する。承認文を argv で受け取る経路は提供しない。`--json` 指定時の正常系出力は機械可読 JSON に限定し、happy path で自由文を混在させない。このサブコマンドは T-006 の `commit_approval.py` を呼び、同じ nonce の challenge と staged 内容承認 record が有効で、現在の index と target digest が一致する場合だけ `.reviewcompass/runtime/approvals/commit-execution-delegation.json` を作成する。承認文は UTF-8 stdin、末尾 POSIX LF 1 個のみ許容、CR／CRLF／内部改行／NUL／空白のみ／256 bytes 超過を fail-closed とし、許可文言の完全一致を T-006 の正規化規則に委譲する。
- **配布可能 commit UX 補足責務**：`tools/guarded-git-commit.py` に `--approval-nonce <nonce>` と `--approval-source-text-line-stdin` を追加する。この wrapper は stdin から承認文を 1 行だけ読み、EOF を待たずに staged 内容承認 record と commit 実行代行 delegation record を順序作成してから commit 直前ゲートを実行する。低レベル `record`／`delegate-execution` はデバッグ・検査用に残すが、第三者向け通常手順には露出させない。`commit-approval prepare` は古い壊れた runtime approval / delegation record を invalidated へ寄せ、新しい challenge 準備の邪魔にしない。commit 直前ゲート通過後、`git commit` 呼び出し直前に `index.lock` の排他作成可否を preflight し、permission / sandbox 系の作成失敗を `sandbox_git_write_denied`、`required_action=rerun_commit_with_escalation` として表示して停止する。この停止では `git commit` を呼ばず、approval / challenge / delegation を consumed または invalidated にしない。`git commit` 実行後に `.git/index.lock` / permission 系エラーが返った場合も同じ分類表示を行い、承認保持・staged 内容不変なら再承認不要・sandbox 外 guarded commit 再実行が必要、の 3 点に絞って利用者へ示す。
- **前提タスク**：T-001、T-002、T-003
- **成果物**：
  - `tools/check-workflow-action.py`（argparse 定義 ＋ 3 サブコマンド ＋ `--json` ＋ ログ追記）
  - `tools/check_workflow_action/predicates.py`（`completion_predicate` 述語集合 7 値の判定ロジック）
  - `tools/check_workflow_action/yaml_loader.py`（YAML 読み込み ＋ パースエラー fail-closed）
  - `tools/check_workflow_action/output_formatter.py`（4 ブロック大括弧付きラベル形式 ／ JSON 形式）
  - `docs/operations/WORKFLOW_DISCIPLINE_MAP.yaml`（判定点ごとの `required_disciplines`、`required_inputs`、effective prompt 元資料マップ）
  - `docs/operations/WORKFLOW_PRECHECK.md`（ワークフロー事前検査の運用契約）
  - `docs/operations/WORKFLOW_PRECHECK_DETAILS.md`（サブコマンド引数 ／ 出力形式 ／ ログの詳細仕様）
- **完了条件**：
  1. 3 サブコマンドと `next` サブコマンドが exit code 0 ／ 1 ／ 2 を正しく返す
  2. 述語 7 値すべてが正常系で OK、異常系（証跡欠落 ／ 必須節欠落 ／ 異名不成立 等）で DEVIATION を返す
  3. YAML パースエラー時に DEVIATION（exit 2）を返す（fail-closed）
  4. `--rationale` が `commit` ／ `push` で必須引数として強制される（省略時はエラー）。`spec-set` の `--rationale`（任意）を省略した場合もログ記録が正しく行われる（F-013 対処 2026-05-28）
  5. ログ追記が `.reviewcompass/runtime/logs/workflow-precheck.log` に発生し、4 ブロックラベル形式と JSON 形式の両方が正しく出力される。実行時生成物 3 パス（検査ログ・effective prompt・commit 承認記録）それぞれについて、(1) 新配置への書き込み、(2) 旧配置への新規書き込みが発生しないこと、(3) 旧パスにしか記録がない場合の新→旧フォールバック読み取り、(4) 新旧両方に記録がある競合時に新配置が採用されること（design 契約「新→旧の順」の直接検証）、(5) 凍結済み旧成果物の不変性（P1 実装反映コミット以降に旧既存ファイルが変更・削除されていないこと）、の凍結期挙動が機械検証される（2026-06-12 配置規約反映、観点 4・5 は triad-review round-3 所見の適用）
  6. `explicit_human_approval_recorded` 述語は `actor=proxy_model` の場合 `reviewcompass.yaml#human_proxy.proxy_allowed` を参照して代行可否を機械判定する（条件を満たさなければ DEVIATION）。`depends_on_resolves_correctly` 述語は値域チェック（依存先の解決可能性）のみを担い、依存先の変更検知と recheck 更新発火は別機構（フェーズ 2 宿題、DVT-W007）であることを境界テストで明示する（A-004／A-006 対処 2026-05-28）
  7. review-run の proxy_model 判断代行ゲートは、`approval-proxy-<日付>.yaml`、`proxy-decisions/<finding-id>.decision.yaml`、decision prompt、元 review raw、raw response、候補案、採用案、判断理由、最終ラベルを検査し、欠落または triage との不一致があれば DEVIATION にする。proxy_model 代行は実装方針判断に限定し、コミット・プッシュ・spec.json 更新・フェーズ移行には使わない
  8. post-write-verification pending の検出、completed manifest の sha 一致、verifier ごとの全対象 coverage、未解決本質的指摘 0 件が機械検証される
  9. triad-review が pending でも drafting が未完了なら、next が `run_reopen_drafting` を返し、review を先に実施しない
  10. `WORKFLOW_DISCIPLINE_MAP.yaml` から判定点ごとの `required_disciplines` と `required_inputs` を返せる
  11. `next` は `effective_prompt_path`、`effective_prompt_sha256`、`effective_prompt_loaded` を返し、元資料欠落時は `DEVIATION` で fail-closed する
  12. review-run は `rounds.yaml` に `effective_prompt_path` と `effective_prompt_sha256` を記録できる
- **テスト要件**：3 サブコマンド × 各 verdict 3 値 = 9 ケース、`next` サブコマンドの通常 workflow／reopen pending／post-write-verification pending／upstream_recheck ケース、述語 7 値の正常系 ／ 異常系テスト、YAML パースエラーの fail-closed テスト、`--rationale` 必須化テスト（commit／push）＋ `spec-set` 省略時ログ記録テスト（F-013）、ログ追記テスト、4 ブロックラベル形式 ／ JSON 出力テスト、`explicit_human_approval_recorded` の proxy_model 代行可否テスト（proxy_allowed 満たす／満たさないの 2 ケース、A-004）、`depends_on_resolves_correctly` の境界テスト（値域チェックのみで変更検知しないことの確認、A-006）、post-write target detection と manifest verification の正常系／sha 不一致／coverage 不足／未解決本質的指摘ありテスト、proxy_model 判断代行ゲートの正常系／raw 欠落／候補案欠落／採用案欠落／判断理由欠落／triage 不一致の fail-closed テスト、intent 更新後に feature-partitioning 確認を返すテスト、requirements 更新後に design 再確認を返すテスト、tasks 更新後に implementation 再確認を返すテスト、triad-review pending かつ drafting 未完了なら `run_reopen_drafting` を返すテスト、reopen `commit_stop_point: true` が pending gate より優先されるテスト、reopen blocker が `wait_for_human_decision` と `blocked_by` を返すテスト、maintenance が `required_action=run_maintenance` と `maintenance_action` を分離するテスト、active gate がある時だけ `active_gate` / `phase` / `stage` が非 null になるテスト、`WORKFLOW_DISCIPLINE_MAP.yaml` の `required_disciplines`／`required_inputs` 反映テスト、`effective_prompt_path`／`effective_prompt_sha256`／`effective_prompt_loaded` の JSON 出力テスト、effective prompt 元資料欠落時の fail-closed テスト、`rounds.yaml` への effective prompt 記録テスト、**凍結期挙動テスト（実行時生成物 3 パス × 5 観点＝計 15 観点：新配置への書き込み／旧配置への新規書き込みが発生しないこと／旧パスにしか記録がない場合の新→旧フォールバック読み取り／新旧両方に記録がある競合時に新配置が採用されること〔新旧に異なる内容を置き、新配置の内容が採用されることを 3 パスそれぞれで検証。design 契約「新→旧の順」の直接検証〕／凍結済み旧成果物の不変性〔P1 実装反映コミット以降に旧 3 パスの既存ファイルが変更・削除されていないことを git 追跡履歴で検出。conformance-evaluation の凍結違反検出と同一判定規則〕。境界条件として、観点 2 が凍結の効力発生時点〔P1 実装反映コミット以後の旧書き込み不在〕の検証を兼ねること、観点 3 のフォールバックが設定・条件分岐等で暗黙に無効化されないことを検証対象に含める。2026-06-12 配置規約反映、観点 4・5 は triad-review round-3 所見の適用、TDD 先行）**、feature_order 外出し・探索順・立ち上げ案内（feature_definition_required）・整合検査・対象アプリ独自 feature 構成での next 動作テスト（2026-06-12 反映、cde1f5c で実装済み）、feature-dependency.yaml パース不能・空・非連想配列の遮断テスト（`next_action.kind: unknown`・verdict DEVIATION・exit 2 を検証し、`reasons` に対象ファイルパスと、パース不能・非連想配列では内容確認を促す文言、空では `feature_order` の記録を促す文言が含まれることを検証）と、不在・未定義の案内維持テスト（`next_action.kind: feature_definition_required`・verdict OK・exit 0 を検証）（MLE-DEC-005、仕様確定後に TDD で実装。検証粒度の明記は triad-review 同根所見対処）

### T-005：起草者と判定者の分離 機械検査

- **対応設計節**：design.md §起草者と判定者の分離モデル §1〜§3
- **対応要件**：Requirement 3 受入 1〜4
- **責務**：レビュー記録の front-matter 検査機能を `tools/check_workflow_action/front_matter_checker.py` として実装、`completion_predicate=artifact_exists_and_sections_present_and_author_reviewer_distinct` から呼び出される。判定 3 点：(1) `author.identity` ／ `reviewer.identity` フィールドの存在、(2) `author.identity` ≠ `reviewer.identity`（文字列比較）、(3) `reviewer.separation_from_author=true`。`mode: subagent_mediated` の場合の `role` フィールド複合役（`drafter_and_primary_reviewer` 等）を許容する暫定特例を符号化。別モデル ／ 別 session の機械判定は範囲外（第 3 層利用者監査に委ねる、Req 3 受入 4）であることを運用文書に明示
- **前提タスク**：T-004
- **成果物**：
  - `tools/check_workflow_action/front_matter_checker.py`（3 点判定ロジック）
  - `tools/check_workflow_action/front_matter_schema.json`（必須フィールド：type ／ target ／ target_commit ／ target_content_hash ／ date ／ mode ／ author ／ reviewer、author/reviewer の必須サブフィールド：identity ／ model ／ role、reviewer.separation_from_author=true 必須）
  - `docs/operations/WORKFLOW_PRECHECK_DETAILS.md`（関連する判定詳細を必要に応じて更新）
- **完了条件**：
  1. 3 点判定が機械検証で確実に発火する（異名のみ／同名／separation_from_author=false の 3 ケース）
  2. `subagent_mediated` の複合役（`drafter_and_primary_reviewer`）が許容される
  3. 既存レビュー記録 7 件以上（各機能の requirements ／ design ／ tasks）への本検査の遡及適用は、grandfathering（遡及検査の免除）判断（DVT-W002、利用者承認事項）が確定するまで検査対象から除外する（未確定のまま走らせて既存記録が DEVIATION を返し本機能のゲートが自己ロックするのを回避）。本完了条件としては「DVT-W002 のエントリが DVT 表に存在すること」を grep で機械検証する（実装作業と人手判断を分離、F-009／A-007 対処 2026-05-28）
- **テスト要件**：3 点判定テスト（異名 ／ 同名 ／ separation_from_author=false の 3 ケース）、`mode` の各値（foundation 正本が定める）の複合役許容テスト（複合役の許容は `subagent_mediated` 特例のみ、他の値は不許容）、必須フィールド欠落テスト、fail-closed テスト

### T-006：不可逆操作の直前ゲート機構

- **対応設計節**：design.md §不可逆操作の直前ゲートモデル §1〜§4、§主要な設計判断 判断 4
- **対応要件**：Requirement 4 受入 1〜8
- **責務**：4 種類の不可逆操作（`spec.json` の `approval` 段書き込み ／ `git commit` ／ `git push` ／ フェーズ移行）の直前ゲート判定ロジックを `tools/check_workflow_action/gate_predicates.py` として実装、T-004 のサブコマンドから呼ばれる。ゲート発火条件：(1) Requirement 2 検査スクリプトが pass を返す、(2) `stages/in-progress/` が空。毎回独立走行（session 開始時のキャッシュを使わない、状態変化を直前で再検出）。fail-closed の既定（検査結論不能で必ず遮断）。`git commit` では commit 承認 challenge と承認レコードを読み、nonce 一致、UTC ISO-8601 の `created_at`／`expires_at`、TTL 10 分、`now_utc` 注入可能な時刻判定、clock rollback fail-closed、未期限切れ、未消費、staged ファイル集合一致、staged 内容一致、approval と challenge の全体 target digest 一致、実際に commit される exact index との一致を検査する。承認レコード単体の `target_sha256` 検査は互換入力として維持するが、nonce challenge がある場合は challenge と承認レコードの両方を必須とする。canonical target digest は `commit-approval-v1` の固定形式で計算し、path 順非依存、削除 staged、git index mode、staged object id を覆う。challenge／承認レコードが JSON として読めない、object でない、必須フィールド欠落、型不正、path 重複、不正 path、未知 path、file set 不一致などの場合は、部分推測せず fail-closed とする。schema に `llm`、`provider`、`model`、`model_id`、`proxy_model_id` を受け入れず、承認レコードは `attestation_type=staged_content_nonce_binding` と `guarantee_scope=staged_content_binding_not_ui_utterance_proof` を必須とする。承認本文は stdin または no-store mode のみで扱い、保存する場合は `tools.session_record_extractor.redact.redact_text` と `find_residual_secrets` を通す。`source_omission_reason` は `source_not_provided`、`unsafe_source_omitted`、`redaction_failed`、`residual_secret_detected` の 4 値に限定する。`--execution-actor llm` の commit gate では、challenge と staged 内容承認 record に加えて `.reviewcompass/runtime/approvals/commit-execution-delegation.json` を必須とし、strict schema、`approved_action=commit_execution_delegation`、`delegated_action=commit`、`delegated_to=llm`、`approved_by=user`、nonce／target digest／staged file set digest／staged 内容承認 digest／expiry 一致、未期限切れ、未消費、未 invalidated、禁止 LLM/provider/model 系 field 不在、許可文言完全一致、`attestation_type=commit_execution_delegation_nonce_binding`、`guarantee_scope=stdin_text_instruction_bound_to_commit_approval_not_ui_utterance_proof` を検査する。`--execution-actor human` では execution delegation を不要とする。delegation record の作成は保存直前再検証と atomic write を必須にし、既存未期限切れ delegation、形式不正、unknown field、外部変更、保存直前の期限切れは fail-closed とする。`commit-approval invalidate --json` は challenge／staged 内容承認 record／delegation record を一括 invalidated にする。validation failure は security failure として challenge／承認レコード／delegation record を invalidated にし、commit 成功後は consumed にする。consume 永続化失敗後は later gate で再利用を拒否する。通常の git execution failure は index と approval 状態が validation 時と同一の場合だけ再試行可能とする。フェーズ移行検査は `feature-dependency.yaml#feature_order` の全機能で approval=true を要求。最小集合方針の徹底（中間段の遷移には機械ゲートを置かない）
- **前提タスク**：T-002、T-003、T-004
- **成果物**：
  - `tools/check_workflow_action/gate_predicates.py`（4 種類のゲート判定）
  - `tools/check_workflow_action/commit_approval.py`（nonce challenge、承認レコード、canonical digest、redaction、validation、invalidate／consume）
  - `tools/check_workflow_action/state_resolver.py`（spec.json ／ in-progress ／ pending 所見の状態解決、毎回独立走行）
- **完了条件**：
  1. 4 種類のゲートそれぞれが正常系で OK、異常系（前段未完了 ／ in-progress あり ／ 未消化所見あり ／ 全機能 approval 未完了）で DEVIATION を返す
  2. session 開始時のキャッシュを使わず、毎回 spec.json と `stages/in-progress/` を読み直すことが機械検証される
  3. 最小集合方針（中間段の遷移には機械ゲートが発火しない）が機械検証される
  4. commit 承認レコードの `target_sha256` 欠落、形式不正、staged 内容との不一致が DEVIATION になる
  5. nonce challenge の prepare／record／invalidate／commit validation／consume が機械検証され、欠落・形式不正・期限切れ・消費済み・staged 内容不一致・approval/challenge target digest 不一致・exact index 不一致・clock rollback が DEVIATION になる
  6. 承認 schema に `llm`、`provider`、`model`、`model_id`、`proxy_model_id` が混入した場合は形式不正で DEVIATION になる
  7. `attestation_type=staged_content_nonce_binding`、`guarantee_scope=staged_content_binding_not_ui_utterance_proof` が機械検証される
  8. 承認本文の stdin 入力、no-store mode、4096 bytes 上限、redaction 失敗時の source omission が機械検証される
  9. LLM commit 実行代行承認は staged 内容承認と別 record として `.reviewcompass/runtime/approvals/commit-execution-delegation.json` に保存され、`commit-approval.json` は staged 内容承認のみを保持することが機械検証される
  10. delegation record の全必須 field（`approved_action`、`delegated_action`、`delegated_to`、`approved_by`、`nonce`、`target_digest`、`staged_file_set_digest`、`staged_content_approval_digest`、`challenge_path`、`approval_record_path`、`created_at`、`expires_at`、`explicit_instruction`、`instruction_sha256`、`attestation_type`、`guarantee_scope`、`consumed`、`invalidated`）の生成・検証・欠落時 fail-closed が機械検証される
  11. delegation record の strict schema、禁止 LLM/provider/model 系 field、staged 内容 binding、stdin 正規化、許可文言完全一致、secret redaction、保存直前再検証、atomic write、invalidate／consume／再利用拒否が機械検証される
  12. `--execution-actor llm` では challenge／staged 内容承認 record／delegation record／現在 index を commit gate 直前に再検証し、`--execution-actor human` では delegation を不要とすることが機械検証される
  13. precheck OK 後に `git commit` 本体が commit 未作成のまま失敗した場合、approval／challenge／delegation を consumed または invalidated にせず、同じ staged exact index と nonce の wrapper 再実行で既存 active transaction を再利用できることが機械検証される
  14. `guarded-git-commit.py` が `git commit` 呼び出し直前に `index.lock` 作成可否を preflight し、permission / sandbox 系の作成失敗では `git commit` を呼ばず、approval／challenge／delegation を consumed または invalidated にせず、`sandbox_git_write_denied` と `required_action=rerun_commit_with_escalation` を表示することが機械検証される
  15. `git commit` 実行後に `.git/index.lock` / permission 系エラーが返った場合も、approval／challenge／delegation を consumed または invalidated にせず、同じ `sandbox_git_write_denied` 分類表示を行うことが機械検証される
- **テスト要件**：4 種類ゲート × 正常系 ／ 異常系 = 8 ケース、独立走行テスト（同 session 内で状態変化させて再検査が異なる結果を返す）、最小集合テスト（drafting ／ triad-review の遷移ではゲート発火しない）、commit 承認レコードの `target_sha256` 正常系／欠落／不一致テスト、nonce challenge 正常系（prepare→record→commit validation→consume）、期限切れ、UTC ISO-8601 不正、TTL 10 分以外、`now_utc` 注入、clock rollback、未消費 challenge あり prepare、明示 invalidate、canonical digest `commit-approval-v1`、canonical digest のパス順非依存、削除 staged、approval/challenge target digest 不一致、exact index 不一致、malformed challenge／approval record の no partial inference、schema 禁止フィールド混入、`attestation_type`／`guarantee_scope` 欠落・不正、stdin source text、no-store mode、UTF-8 不正、4096 bytes 超過、`source_not_provided`、`unsafe_source_omitted`、`redaction_failed`、`residual_secret_detected` の 4 値、`redact_text` 呼び出し、`find_residual_secrets` 呼び出し、residual secret 検出、validation failure 後の再利用拒否、consume 永続化失敗後の再利用拒否、git execution failure 後の条件付き retry、`commit-approval * --json` の parseable JSON 出力テスト、`delegate-execution` 正常系（prepare→record→delegate-execution→commit validation→consume）、staged 内容承認前の delegation 拒否、既存未期限切れ delegation 拒否、delegation record の全必須 field の生成／欠落／型不正、delegation の nonce／target digest／staged file set digest／staged 内容承認 digest／challenge path／approval record path／expiry／instruction hash 不一致、malformed delegation record、unknown field、禁止 LLM/provider/model 系 field、`attestation_type=commit_execution_delegation_nonce_binding`、`guarantee_scope=stdin_text_instruction_bound_to_commit_approval_not_ui_utterance_proof`、両 field の欠落・不正、末尾 POSIX LF 1 個だけ許容、CR／CRLF／内部改行／2 個以上の末尾 LF／NUL／空／空白のみ／256 bytes 超過／全角 Latin 拒否、ASCII 英字のみ小文字化、末尾日本語句点 1 個だけ除去、許可文言 `コミット`／`コミットして`／`コミットを実行`／`承認`／`commit`／`commitして` の完全一致、secret redaction failure／residual secret 検出時の delegation 作成拒否、保存直前再検証、atomic write 失敗、保存直前 expiry race、`--execution-actor llm` で challenge／staged 内容承認 record／delegation record／現在 index の全再検証と delegation 必須、`--execution-actor human` で delegation 不要、invalidate が challenge／staged 内容承認 record／delegation record を一括 invalidated にすること、`guarded-git-commit.py --approval-nonce --approval-source-text-line-stdin` が承認 1 行で record／delegate-execution／commit／consume まで完了すること、同 wrapper が precheck OK 後の git execution failure で commit 未作成の場合に record を消費・無効化せず、同一 nonce 再実行で既存 approval／delegation を再利用すること、`index.lock` preflight 失敗時に commit を呼ばず承認を保持して `sandbox_git_write_denied` / `required_action=rerun_commit_with_escalation` を表示すること、`git commit` 実行後の `.git/index.lock` / permission 系失敗も同じ分類で表示し承認を保持すること、壊れた古い delegation が `prepare` 後の新規承認フローを妨げないこと

### T-007：reopen 機械強制

- **対応設計節**：design.md §reopen 機械強制モデル §1〜§4、§主要な設計判断 判断 5
- **対応要件**：Requirement 5 受入 1〜5、Requirement 9 受入 1〜4
- **責務**：reopen 手続きの 4 過程構成を T-003 の `stages/reopen-procedure.yaml` で静的列挙、第3過程の `trigger_map` 解決ロジックを `tools/check_workflow_action/reopen_resolver.py` として実装。手戻り種別の二次元表記（N／R／D／A／I × 深さ）から再実施対象段リストを取得、各段の `actor` を当該段定義から動的解決（`actor_resolution: per_target_stage`）。`actor=human` 段に到達した時点で作業を停止し、`stages/in-progress/reopen-procedure-<日付>.yaml` に「人間承認待ち」を記録して待機。種別判定根拠ファイル（`docs/reviews/reopen-classification-<日付>.md`）の保存・読み込み機構を実装。後追い intent の downstream impact では、conformance-evaluation から受け取った候補を直接の実行命令にせず、既存 feature の受け皿ありなら `reopen_existing_feature`、受け皿なしなら `new_feature_required`、根拠不足なら `human_decision_required` として分類する。CE から渡される `downstream_impact_candidate` や `implementation_change_candidate` が tasks phase を指す場合も、候補 ID、対象 feature、対象 phase、根拠参照を読み、T-007 が受け皿判定を行って `pending_gates` に反映する。`reopen_existing_feature` は既存 feature の該当 phase を reopen し、`new_feature_required` は feature-partitioning へ戻し、`human_decision_required` は blocker として停止する。fail-closed の既定（人間承認なしに次段への進行を許さない）
- **前提タスク**：T-003、T-004、T-005、T-006（T-005 を追加：reopen 解決器が triad-review 段の述語 `artifact_exists_and_sections_present_and_author_reviewer_distinct` 経由で `front_matter_checker` を呼ぶため、T-005 完了前の着手を防ぐ。F-006 対処 2026-05-28）
- **成果物**：
  - `tools/check_workflow_action/reopen_resolver.py`（`trigger_map` 解決 ＋ `actor` 動的解決 ＋ actor=human 自動停止）
  - `tools/check_workflow_action/classification_loader.py`（種別判定根拠ファイルの読み込み）
  - （`templates/review/reopen_classification_template.md` の成果物所有は T-001 単独。本タスクは内容確定のみで成果物に再列挙しない、A-010 対処 案 2 2026-05-28）
- **完了条件**：
  1. 全 15 種の手戻り種別（N-0 ／ R-0〜1 ／ D-0〜2 ／ A-0〜3 ／ I-0〜4）に対する `trigger_map` 解決が機械検証される
  2. `actor=human` 段で自動停止し、`stages/in-progress/reopen-procedure-<日付>.yaml` に `current_blocker` フィールドが書き込まれる
  3. 種別判定根拠ファイル不在の場合は結論不能（DEVIATION）で遮断
  4. 人間承認なしに次段への進行が機械的に許可されない（fail-closed）
  5. T-001 が配置した `reopen_classification_template.md` の内容（front-matter ＋ 分類根拠節）が確定している（成果物所有は T-001、本タスクは内容確定のみ、A-010 対処 案 2 2026-05-28）
  6. 後追い intent の受け皿判定が `reopen_existing_feature` ／ `new_feature_required` ／ `human_decision_required` の 3 値で記録される
  7. CE から渡された tasks phase の `downstream_impact_candidate` を、直接実装せず reopen pending gate へ変換できる
- **テスト要件**：15 種類の `trigger_map` 解決テスト、`actor=human` 自動停止テスト、種別判定根拠ファイル欠落の fail-closed テスト、人間承認なし進行禁止テスト、後追い intent の受け皿判定 3 値の分岐テスト、CE 由来 tasks phase 候補の reopen pending gate 変換テスト

### T-008：session 跨ぎ状態管理

- **対応設計節**：design.md §session 跨ぎ状態管理モデル §1〜§5
- **対応要件**：Requirement 6 受入 1〜7、Requirement 9 受入 3 ／ 5 ／ 6
- **責務**：進行中状態ファイル（`stages/in-progress/<process_id>-<日付>.yaml`）の発行 ／ 読み込み ／ 完了時移動（`stages/completed/` への移動）の機構を `tools/check_workflow_action/in_progress_manager.py` として実装。最低限のフィールド 6 件（`process_id` ／ `started_at` ／ `trigger` ／ `completed_steps` ／ `next_step` ／ `pending_gates`）を必須化、任意フィールド（`classification_basis` ／ `current_blocker` ／ `escalation_status`）を許容。後追い intent の reopen では `completed_gates`、`drafting_completed_gates`、`downstream_impact_decisions` を保持できる。`downstream_impact_decisions` は `gate`、`feature_scope`、`decision`、`rationale`、`evidence`、`decision_actor`、`decision_source` を最低フィールドとする。これらの進行中状態フィールドは workflow-management が所有する `stages/in-progress.schema.json` を正本とし、foundation の共有スキーマへ昇格するまでは foundation tasks.md に追加タスクを作らない。通常の `next_action` と異なる side track、または `next` 判定自体の欠陥修復に入る場合は、`process_id: maintenance` と `mainline_blocked_by`、`allowed_scope`、`allowed_files`、`completion_conditions` を持つ進行中ファイルを先に作成する。session 開始時の標準フロー 7 ステップ（TODO 確認 ／ 直近 session 記録確認 ／ git log ／ 検査スクリプト全件 ／ in-progress 有無 ／ 進行中優先 ／ 次作業決定）と、session record 作成手順（重要な判断・承認・レビュー結果・修正経緯を `docs/sessions/session-<N>-<YYYY-MM-DD>.md` に残す）を運用文書に明示、`tools/check-workflow-action.py session-start` サブコマンドとして実装可能か別途判断（任意拡張）。fail-closed：`stages/in-progress/` に何かファイルがある状態での不可逆操作実行を遮断（T-006 と整合）。reopen 固有フィールド（`current_blocker` 等）の意味解釈は T-007 の責務とし、T-008 は進行中ファイルの一般管理（発行 ／ 読み込み ／ 移動 ／ 遮断）に徹して reopen 連動を内包しない（前提タスクに T-007 を加えず独立性を保つ、F-007 対処 案 2 2026-05-28）
- **前提タスク**：T-001、T-004、T-006
- **成果物**：
  - `tools/check_workflow_action/in_progress_manager.py`（発行 ／ 読み込み ／ 完了時移動）
  - `stages/in-progress.schema.json`（必須 6 フィールド ＋ 任意フィールド。命名をディレクトリ名 `in-progress/` に合わせハイフン統一、design 配置ツリーにも追記、F-018 対処 案 1 2026-05-28）
  - `docs/operations/WORKFLOW_PRECHECK.md`（段階 1・段階 3 との接続）
  - `docs/operations/SESSION_WORKFLOW_GUIDE.md` §セッション記録の作成規律
- **完了条件**：
  1. `in-progress.schema.json` が JSON Schema として meta-schema 検証を通る、必須 6 フィールドが確定（F-018 対処 命名統一）
  2. 進行中状態ファイルの発行 ／ 読み込み ／ 完了時移動が機械検証される
  3. `stages/in-progress/` に何かある状態での不可逆操作実行が遮断される（T-006 連動）
  4. 進行中状態ファイル自体の更新（次ステップ進行 ／ 人間承認の記録）は遮断対象外であることが機械検証される
  5. `SESSION_WORKFLOW_GUIDE.md` と workflow-management 仕様が session record 作成手順を持つことが機械検証される
  6. maintenance 進行中ファイルが `mainline_blocked_by`、`allowed_scope`、`allowed_files`、`completion_conditions` を保持できる
  7. `completed_gates`、`drafting_completed_gates`、`downstream_impact_decisions` の最低フィールドを保持できる
- **テスト要件**：スキーマ検証、必須 6 フィールド検査、発行 ／ 読み込み ／ 移動の 3 機能テスト、in-progress あり状態での不可逆操作遮断テスト、自己更新の許容テスト、maintenance side track の読み込みテスト、複数 in-progress 並存テスト（複数 reopen-procedure-*.yaml が正常系として並ぶ場合の優先完了対象と解決順。design §テスト戦略 境界条件 L840、reopen やり直し時の証跡保全 L505 由来、A-008 対処 案 1 2026-05-28）、`downstream_impact_decisions` の gate coverage テスト、`drafting_completed_gates` による再開位置判定テスト

### T-009：多層防御の位置付けと運用文書

- **対応設計節**：design.md §多層防御の位置付けモデル §1〜§5、§主要な設計判断（全般）
- **対応要件**：Requirement 7 受入 1〜4
- **責務**：ワークフロー事前検査の呼び出し責務、対象操作、判定結果の扱いを `docs/operations/WORKFLOW_PRECHECK.md` に置き、サブコマンド引数、判定条件、出力形式、ログ、テスト観点の詳細を `docs/operations/WORKFLOW_PRECHECK_DETAILS.md` に置く。自律・並列実行の安全契約として自律 plan と履歴 ledger を運用文書に明示し、依存順、recheck 対象、許可パス、期待テスト、統合判断、未解決 blocker を追跡できるようにする。本タスクは実装ではなく運用文書の整備が主、機械検査の対象ではない。
- **前提タスク**：T-004、T-005、T-006、T-007、T-008
- **成果物**：
  - `docs/operations/WORKFLOW_PRECHECK.md`（ワークフロー事前検査の運用契約）
  - `docs/operations/WORKFLOW_PRECHECK_DETAILS.md`（ワークフロー事前検査の詳細仕様）
  - `docs/operations/WORKFLOW_MANAGEMENT.md` の §多層防御位置付け節
- **完了条件**：
  1. 運用契約と詳細仕様の分離が明示される
  2. 自律 plan と履歴 ledger の必須目的が運用文書に明示される
- **テスト要件**：本タスクの「実装ではなく運用文書の整備が主、機械検査の対象ではない」位置づけ（責務記述）と整合させ、文書内容の grep キーワード検査は完了条件・テスト要件から外す

### T-010：規律変更の所定手続き経由実体変更（A-007 案 2、A-012 連動）

- **対応設計節**：design.md §責務境界の明確化、§主要な設計判断 判断 7
- **対応要件**：Requirement 4 受入 1（規律変更は不可逆操作）、Boundary Context 隣接期待（self-improvement との接合面）
- **責務**：`learning/workflow/approved-updates/` ディレクトリを新設、`self-improvement` から承認済み提案 YAML が `git mv` で配置される入力経路を確立。本機能の所定手続き（drafting → review → approval）を経て規律ファイル（`docs/disciplines/discipline_*.md`）の実体変更を実施。完了時に `approved-updates/<日付>-<id>.yaml` に `materialized_at`（ISO 8601 完了時点）と `materialization_commit_hash`（規律変更コミットのハッシュ）を追記。`self-improvement` design §13.5 と本機能 判断 7 の相互参照、時系列契約（`approved` ＝ self-improvement 承認時点 ／ `materialized_at` ＝ 本機能完了時点）の符号化。ロールバック責務は `self-improvement` 側、本機能は受動的に状態通知を受ける
- **前提タスク**：T-003（段集合 YAML 群の配置）、T-004。**規律変更段集合の方針（F-008 対処 案 1 2026-05-28）**：規律変更専用の段集合は機能横断整合用 `cross-spec-alignment.yaml` への相乗り（責務混在）を避け、独立ファイル `stages/discipline-update.yaml` とする方針に一意化。ただし段集合本体（`drafting → review → approval` の 3 段か `triad-review` を含むか）は未確定のため **DVT-W003 として後続セッションに延期**し、本ファイルは T-003 の成果物には含めず DVT-W003 解除時に静的列挙する（tasks 段 2 軸整合性監査 #5 で「T-003 が枠を新設」との誤記述を訂正、2026-05-29）
- **成果物**：
  - `learning/workflow/approved-updates/.gitkeep`
  - `learning/workflow/approved-updates/README.md`（入力経路の説明、`git mv` 配置の規約）
  - （入力 YAML のスキーマは本機能で独自定義しない。self-improvement design §8.4 の正本スキーマを唯一の定義元として参照し、項目名は §8.4（`target_discipline_path` ／ `status` ／ `materialized_at` ／ `materialization_commit_hash` 等）に従う。受け手側の検証は §8.4 由来の共有フィクスチャで行う。**A-019 対処（案1、2026-05-29 セッション40）**：独自 `approved_update.schema.json` の新設と独自項目名 `approved_at` ／ `target_discipline` を廃止し、二重管理を解消）
  - `tools/check_workflow_action/discipline_update_processor.py`（規律変更の所定手続き実施 ＋ 完了通知の追記）
  - （`learning/workflow/approved-updates/` の配置は本機能 design 配置ツリー外だが、self-improvement design §13.5 に正本記述があり機能横断では整合済み。tasks.md 側は出典注記で吸収し design 遡及はしない、F-020 対処 案 1 2026-05-28）
- **完了条件**：
  1. `approved-updates/` ディレクトリが配置され、入力 YAML が self-improvement §8.4 正本スキーマに適合することを検証する（本機能は独自スキーマを定義しない、A-019 対処 案1）
  2. `self-improvement` から `git mv` で配置された YAML を本機能が読み、所定手続きを経て規律ファイル実体変更を完了
  3. 完了時に `materialized_at` ／ `materialization_commit_hash` が追記される
  4. `self-improvement` design §13.5 との時系列契約の整合が機械検証される（DVT-W003）。さらに **§13.5 の変更が機能依存マップ（feature-dependency.yaml）に記録されたとき、DVT-W003 を自動的に open（未解決）へ差し戻し、事前検査スクリプトが再評価完了を確認するまで本タスクを完了扱いにしない**（依存マップ駆動の追従強制、本機能の自己適用、F-016 対処 案 3 2026-05-28）。**【実装時の調停】** A-006 で「`depends_on_resolves_correctly` の汎用的な変更検知はフェーズ 2 の宿題（DVT-W007）」と確定したため、本条件では §13.5（self-improvement 接合面）の変更検知のみを先行実装し、機能依存マップ全般の汎用変更検知はフェーズ 2 に据え置く
- **テスト要件**：スキーマ検証、所定手続きの 3 段（drafting → review → approval）が走るテスト、完了通知の追記テスト、時系列契約の整合テスト、self-improvement の `git mv` 外部依存をモック／スタブ化した consumer 側統合テスト（`approved-updates/` への YAML 配置を擬似再現、実 git mv は呼ばない。擬似 YAML は self-improvement §8.4 正本スキーマ準拠の共有フィクスチャとする（A-019 解消＝案1 採用 2026-05-29 により §8.4 を唯一の定義元として参照）。producer/consumer 境界の契約確認は T-011 に集約、F-012 対処 別案 2026-05-28）

### T-011：テスト戦略全体の整備

- **対応設計節**：design.md §テスト戦略 §1〜§5、§完成判定基準
- **対応要件**：本機能全要件の機械的合否判定、foundation 語彙正本（本機能が参照する `review_mode`）の参照のみ使用の機械検証、要件追跡表の双方向整合、DVT 解除確認、Requirement 9 の統合検証
- **責務**：design.md §テスト戦略で定義された 4 検証類（単体テスト ／ 統合テスト ／ 異常系 fixture ／ 境界条件）をすべて Python テストとして整備。pytest で一括実行可能。foundation 語彙正本（本機能が参照する `review_mode`）の参照のみ使用の機械検証、および所見系・状態軸系語彙を参照していないことの機械検証、本機能所有正本（`completion_predicate` 述語 7 値 ／ `verdict` 3 値 ／ 手戻り種別記号 5 値 ／ 依存種別 2 値）が T-002 ／ T-003 ／ T-004 ／ T-007 の成果物で正本確定されていることの機械検証。要件追跡表と各タスク本文の対応要件欄の双方向整合チェック（foundation T-010 ／ runtime T-011 ／ evaluation T-011 ／ analysis T-011 の方針継承）。Requirement 4 受入 8 については、T-004 の `delegate-execution` CLI、T-006 の delegation record 生成・validation・`--execution-actor llm` gate、staged 内容承認との分離、LLM/provider/model 非依存、secret handling、invalidate／consume の一連の統合・回帰テストを T-011 が覆う。XDI-WM-002 として、後追い intent の下流再展開、conformance-evaluation 候補の受け取り、drafting-before-review 防止、side track 分離、`downstream_impact_decisions` の証跡保持を統合検証する。**遅延確認事項テーブル（DVT）内の未解除項目がない、または延期理由が明記されている**ことを完了条件にゲート化（evaluation T-011 ／ analysis T-011 の方針継承）
- **前提タスク**：T-001 ／ T-002 ／ T-003 ／ T-004 ／ T-005 ／ T-006 ／ T-007 ／ T-008 ／ T-009 ／ T-010
- **成果物**：`tests/workflow-management/` 配下のテストファイル群（`test_feature_dependency.py` ／ `test_stages_yaml.py` ／ `test_check_workflow_action.py` ／ `test_front_matter.py` ／ `test_gate_predicates.py` ／ `test_reopen.py` ／ `test_in_progress.py` ／ `test_discipline_update.py` ／ `test_operations_docs.py` ／ `test_traceability.py` の 10 ファイル相当）
- **完了条件**：すべての pytest が pass、4 検証類を網羅、foundation 語彙正本（本機能が参照する `review_mode`）の参照のみ使用が機械検証される（所見系・状態軸系の不参照を含む）、workflow-management 所有正本（`completion_predicate` 述語 7 値 ／ `verdict` 3 値 ／ 手戻り種別記号 5 値 ／ 依存種別 2 値）が正本確定されている、要件追跡表の双方向整合が機械チェックされる、DVT 内の未解除項目がない（または延期理由が明記されている）
- **テスト要件**：すべての pytest が pass、回帰なし、要件追跡表の双方向整合チェック、DVT ゲート化、self-improvement との接合面の producer/consumer 境界の契約確認（T-010 の consumer 側統合テストと対をなす境界テスト、`git mv` 経由の `approved-updates/` 取り込みの整合確認を集約、F-012 対処 別案 2026-05-28）、Requirement 4 受入 8 の一気通貫統合テスト（prepare→record→delegate-execution→`--execution-actor llm` commit gate→consume、human actor 免除、staged 内容承認と execution delegation の分離、LLM/provider/model 非依存、secret handling、invalidate／再利用拒否）、XDI-WM-002 の後追い intent 下流再展開テスト、CE 候補受け取りテスト、drafting-before-review 防止テスト、side track 分離テスト、`downstream_impact_decisions` 証跡保持テスト

### T-012：review-wave 横断確認の要約コマンド（Req 10、reopen R-0 2026-06-14）

- **対応設計節**：design.md §review-wave 要約コマンドモデル §1〜§6
- **対応要件**：Requirement 10 受入 1〜5
- **責務**：`tools/check-workflow-action.py` に `review-wave-summary` サブコマンドを追加（`next`／`spec-set`／`commit` と同じ CLI 体系）。design §2 の読み取り元（各 feature の spec.json の `workflow_state`・`recheck`、`stages/in-progress/`、feature-dependency.yaml の `feature_order`、review-run の `triage.yaml` 群〔`evidence/review-runs/` 優先・旧 `_cross_feature/reviews/` 互換、`run_id` 単位で重複排除〕、carry-forward register）から design §2 の算出定義で指標を集計する。出力は Markdown（既定）と JSON（`--json`、design §3 の安定スキーマ）で情報同等。fail-closed（design §4：必須記録〔spec.json・feature-dependency.yaml〕の欠落・解析不能、および任意記録の解析不能で `status: insufficient`＋非ゼロ終了コード 2。任意記録〔triage.yaml 群・carry-forward register〕の非在は 0 件として `ok`）。読み取りに徹し spec.json・triage・phase を書き換えない。保存は `--out`／`--save` で自身の要約出力のみ（design §5）。既存関数（`load_all_feature_specs`・`feature_order` 解決・`collect_recheck_items`・`review_triage` 集計）を再利用し二重定義を避ける。
- **前提タスク**：T-002（feature-dependency）、T-003（段集合 YAML）、T-004（検査スクリプト本体）
- **成果物**：`tools/check-workflow-action.py` の `review-wave-summary` サブコマンド（必要に応じ `tools/check_workflow_action/` 配下の helper モジュール）、`tests/tools/`（または `tests/workflow-management/`）のテストファイル
- **完了条件**：design §1〜§6 を満たす。Markdown と JSON が情報同等で JSON が安定スキーマ（キー名・型固定）。必須記録の欠落・解析不能で `status: insufficient`＋終了コード 2、任意記録の非在は `ok`（0 件）。spec.json・triage・phase を書き換えない。TDD（赤→緑→全テスト通過、回帰なし）。
- **テスト要件（TDD：先に失敗テストを書く）**：(1) 各指標の集計（feature coverage・phase/stage 状態・triage の unresolved/draft/human_required・recheck・依存状況・carry-forward 未消化）、(2) JSON 安定スキーマの**キー名・型を固定値として表明検証**（design §3 のトップレベル・ネスト構造と一致）と `status` 判定基準、(3) Markdown と JSON の情報同等、(4) fail-closed：必須記録（spec.json・feature-dependency.yaml）の**欠落**と**解析不能（パースエラー・非連想配列）**で `status: insufficient`＋**exit 2**、任意記録（triage.yaml 群・carry-forward register・stages/in-progress/）の**非在は `ok`・0 件**だが**存在して解析不能なら `status: insufficient`＋exit 2**、(5) 読み取り専用（実行後に spec.json・triage が不変）、(6) draft は run 単位・unresolved/human_required は item 単位の集計軸の区別、(7) **`--out`／`--save` の保存正常系**（指定パス／既定保存先 `_cross_feature/reviews/` へ自身の要約出力が書かれ、spec.json・triage・phase は不変）。全 pytest が pass、回帰なし。

### T-013：重要決定の出典検査（decision-source-lint サブコマンド、Req 11、reopen R-0 2026-06-15）

- **対応設計節**：design.md §Req 11 設計モデル §1〜§6
- **対応要件**：Requirement 11 受入 1〜7
- **責務**：`tools/check-workflow-action.py` に `decision-source-lint` サブコマンドを追加し、`.reviewcompass/decisions/` 直下の重要決定記録 YAML を逐語照合・束ね検出・内容性検査する。①`stages/decision-source-lint-config.yaml` の生成（内容なし語リスト初期値 11 件）。②決定記録スキーマの機械検査（必須フィールド・category 3 値 enum・multiplicity 制約・verification_status 3 値 enum）。③逐語照合：source.locator のパス部分に対応する転写ファイル全文に対して NFC 正規化・連続空白→単一スペース・前後除去の正規化を両辺に適用し `source.excerpt` が含まれるかを検索（ターン番号は絞り込みに使わない）。④束ね例外の 3 条件確認（承認レコードが存在し・当該 decision_id が covered_decision_ids に含まれ・multiplicity が single）。⑤内容なし語リスト判定（句読点除去→スペース区切りトークン化→全トークンがリスト一致で fail-closed）。⑥commit 直前ゲートへの統合（`cmd_commit` から `decision-source-lint --all` を呼び出し、pending=WARN・unverifiable=DEVIATION・multiplicity:bundled かつ承認なし=DEVIATION）。⑦`--verify-pending` フラグ（verification_status: pending の決定を再照合し合格なら verified に更新・verified_at に現在日時を記録。書き換えるのは verification_status・verified_at の 2 フィールドのみ。照合不合格時はファイル不変・差分表示・非ゼロ終了）。
- **前提タスク**：T-001（配置）、T-004（検査スクリプト本体）
- **成果物**：`tools/check-workflow-action.py` の `decision-source-lint` サブコマンド、`stages/decision-source-lint-config.yaml`（初期内容なし語リスト）、`tests/tools/` のテストファイル
- **完了条件**：design §1〜§6 を満たす。TDD（赤→緑→全テスト通過、回帰なし）。commit 直前ゲートへの統合済み（`pending=WARN`・`unverifiable=DEVIATION`）。`--all` が `bundle-exceptions/` サブディレクトリを除外する。`--verify-pending` が `verification_status`・`verified_at` の 2 フィールドのみを更新し他フィールドを書き換えない。design §6 の実装委譲 4 事項（`--verify-pending` 安全性保証・`bundle_exception_id` 採番規則・逐語不一致時の差分表示形式・既存関数との統合方法）が implementation で確定されていること。
- **テスト要件（TDD：先に失敗テストを書く）**：(1) 必須フィールドと category 3 値 enum の検査（欠落・不正値・空文字列・非文字列型で DEVIATION）、(2) multiplicity: bundled → fail-closed（承認レコードなし）、束ね例外 3 条件の**部分満足も fail-closed**（承認レコードあり＋covered_decision_ids 含むが multiplicity=bundled で DEVIATION・承認レコードなし＋multiplicity=single で DEVIATION）、全 3 条件充足（承認レコード有＋covered_decision_ids 含む＋multiplicity=single）で通過、(3) 逐語照合正常系（正規化後 excerpt が転写ファイル全文に含まれる → verified 判定）、(4) 逐語照合不合格系（転写ファイルに excerpt なし → pending 維持・差分表示・非ゼロ終了）、(5) verification_status: pending → WARN（commit 遮断しない）、verification_status: unverifiable → DEVIATION、(6) 内容なし語リスト正常系（全トークンが empty_content_words に一致 → fail-closed）と不合格系（一部不一致 → 通過）、(7) `--all` で `decisions/` 直下のみ（`bundle-exceptions/` YAML は検査対象外）、(8) `--verify-pending` 正常系（pending → verified・verified_at 記録・他フィールド不変）、(9) `--verify-pending` 不合格系（ファイル内容不変・差分表示・非ゼロ終了）、(10) commit ゲート統合（`python3 check-workflow-action.py commit` の end-to-end テストで decision-source-lint の DEVIATION/WARN 判定が commit 結果に反映されること）、(11) 設定ファイル `stages/decision-source-lint-config.yaml` の読み取り（リストの内容が正しく反映される）。全 pytest が pass、回帰なし。

### T-014：operation registry / read-only preflight（Req 12、reopen R-0 2026-06-16）

- **対応設計節**：design.md §Requirement 12 設計モデル §1〜§13、§XDI-WM-004
- **対応要件**：Requirement 12 受入 1〜13
- **責務**：`stages/operation-registry.yaml` と read-only preflight を追加し、review-run、post-write verification、triage、reopen、commit approval chain、session-record、deployment / export などの操作を、記憶・前例・短縮名ではなく operation contract から開始できるようにする。Phase 1 は成果物を作らない preflight のみとし、review-run directory、manifest、approval record、session record、commit、deployment / export output を作成・更新しない。実際に artifact を作る runner は Phase 2 として分離する。
- **前提タスク**：T-002（feature-dependency）、T-003（段集合 YAML）、T-004（`next`／workflow CLI／parser 接続）、T-006（commit gate）、T-007（reopen 解決）、T-008（in-progress 管理）、T-012（review-wave summary）、T-013（decision-source-lint）。T-011 は T-014 の前提ではなく、T-014 の個別テストを後段で統合・回帰検証する集約タスクとして扱う。
- **成果物**：
  - `stages/operation-registry.yaml`（operation_id、kind、operation_family、canonical_invocation、workflow_binding、required_inputs、target_identity、planned_outputs、sequence_mode、worktree_policy、pending_conflict_policy、artifact_policy、family_required_checks、vocabulary_refs）
  - `tools/check_workflow_action/operation_registry.py`（registry 読み込み、schema 検査、operation family 必須 check 検査）
  - `tools/check_workflow_action/operation_preflight.py`（read-only preflight 判定、state_refs、conflict、planned_outputs、canonical_commands、verdict 生成）
  - `tools/check-workflow-action.py operation-preflight --operation-id <id> --json` サブコマンド
  - `tests/workflow-management/test_operation_registry.py`
  - `tests/workflow-management/test_operation_preflight_response.py`
  - `tests/workflow-management/test_operation_preflight_next_state.py`
  - `tests/workflow-management/test_operation_preflight_review_artifacts.py`
  - `tests/workflow-management/test_operation_preflight_approval_chain.py`
  - `tests/workflow-management/test_operation_preflight_session_record.py`
  - `tests/workflow-management/test_operation_preflight_nested_issue.py`
  - `tests/workflow-management/test_operation_preflight_deployment_export.py`
- **完了条件**：
  1. registry が `operation_id`、`kind`、`operation_family`、canonical invocation、workflow binding、required inputs、target identity、planned outputs、sequence mode、各 policy、family required checks、`vocabulary_refs` を機械検査できる。
  2. preflight response が `schema_version`、`operation_id`、`verdict`、`allowed_verdicts`、`sequence_mode`、`allowed_sequence_modes`、`state_refs`、`required_inputs`、`missing_inputs`、`template_available`、`target_identity`、`worktree_state`、`pending_conflicts`、`integrity_conflicts`、`checks`、`planned_outputs`、`canonical_commands`、`next_step` を返す。
  3. workflow state に依存する operation では、Requirement 2 が所有する `next --json` の active state dimensions（current mainline、required action、phase、stage、reopen scope、impact review scope、direct / indirect features、flag policy、next pending gate、next drafting gate、pending / completed / superseded gates、state files）を `state_refs.next_action` に返す。Requirement 12 は `next` 正本を複製せず、preflight が参照・照合する側として実装する。
  4. command validation は help 文字列ではなく parser / parser adapter と registry の `canonical_invocation` を照合し、存在しない entrypoint、subcommand、option、未登録 alias、誤 script path を成果物作成前に DEVIATION または確認不能 WARN として返す。
  5. worktree conflict と integrity conflict を分け、post-write pending、reopen in-progress、staged / unstaged 混在、承認 record / delegation record / manifest / bundle / target digest の欠落・stale・不一致・消費済み・対象外を検出できる。
  6. `operation_family=review_artifact` は target / manifest / bundle / criteria / document-type / approval record / existing review-run artifact の対象集合一致、approval.yaml の finding id / final_label、bundle 非空、staged / unstaged 対象選択、上書き・stale・drift を必須 check として作成前に検査できる。
  7. `serial_only` operation は `prepare -> record -> delegate-execution -> guarded commit` の内部順序、または配布可能 UX の `prepare -> guarded commit --approval-nonce --approval-source-text-line-stdin` の wrapper 順序、nonce、target digest、staged file set digest、staged content approval digest、expiry、consume、invalidated、target を検査し、並列・順序外実行を DEVIATION にする。
  8. current-session formal record guard は `session_record_mode`、`current_session_id`、`target_session_id` を返し、formal 出力で current と target が同一または不明なら DEVIATION にする。
  9. nested issue handling は parent task、discovered issue、relation、allowed files、return condition、nesting depth を検査し、記録なしの scope drift を DEVIATION にする。
  10. deployment / export preflight は planned outputs、既存成果物、上書き禁止 policy、外部 app root、既存 bundle / smoke-run / app file 衝突を作成前に返す。観測範囲は registry または明示入力で与えられた repo-relative output、許可済み external output root、target app root に限定し、未指定の外部探索はしない。観測範囲が不明な場合は OK にせず WARN 以上、runner-enabled operation では DEVIATION とする。
  11. `reopen_scope` と `impact_review_scope` を区別し、direct / indirect feature sets、flag policy、判断理由、証跡を `next --json` と整合させる。不整合は WARN または DEVIATION として通常進行を止める。
  12. 判定は LLM、provider、model 名に依存しない。registry / response schema に `llm`、`provider`、`model`、`model_id`、`proxy_model_id` を合否条件として持たせない。
  13. read-only preflight は正本 artifact を作らず、runner-enabled operation は本タスクの範囲外として明示されている。
- **operation_family 初期必須 check**：
  - `review_artifact`：target / manifest / bundle / criteria / document-type / approval record / existing artifact drift / staged-vs-unstaged target selection。
  - `workflow_cli`：parser / parser adapter invocation、workflow binding、`next --json` active state dimensions、scope consistency。
  - `commit_approval_chain`：nonce、target digest、staged file set digest、staged content approval digest、expiry、consume、invalidated、target。
  - `session_record_capture`：session_record_mode、current_session_id、target_session_id、formal output の current-session 禁止。
  - `deployment_export`：planned outputs、overwrite policy、external output root、target app root、existing bundle / smoke-run / app file。
  - `nested_issue_control`：parent task、discovered issue、relation、allowed files、return condition、nesting depth。
- **テスト要件（TDD：先に失敗テストを書く）**：(1) registry schema 正常系と必須 field 欠落・未知 kind・未知 operation_family・family_required_checks / vocabulary_refs 欠落の fail-closed、(2) parser / parser adapter との invocation 照合正常系・存在しない subcommand / option / entrypoint / alias の DEVIATION、(3) preflight response JSON のキー名・型固定、`allowed_verdicts` と `verdict` 整合、DEVIATION hard-stop の WARN downgrading 拒否、(4) `state_refs.next_action` の必須キー固定検証（current mainline、required_action、phase、stage、reopen_scope、impact_review_scope、direct / indirect features、flag policy、next_pending_gate、next_drafting_gate、pending_gates、completed_gates、superseded_gates、state_files）、(5) Requirement 2 所有の `next --json` 出力を参照し、別正本を作らないことの検証、(6) `feature_impact_decisions` / `spec.json` / `pending_gates` / `drafting_completed_gates` / `downstream_impact_decisions` 不整合の検出、(7) worktree conflict と integrity conflict の分離、(8) review artifact preflight の target / manifest / bundle / criteria / document-type / approval.yaml / existing artifact drift / staged-vs-unstaged target selection 検査、(9) serial_only approval chain の順序外・期限切れ・消費済み・invalidated・digest 不一致検査、(10) current-session formal record guard、(11) nested issue scope drift、(12) deployment / export planned output / overwrite policy / explicit external root / target app root 衝突、および未指定外部探索をしないこと、(13) read-only 不変性（preflight 実行前後で registry 以外の正本 artifact が変化しない）、(14) LLM/provider/model 系 field 非依存・禁止 field 検査。全 pytest が pass、回帰なし。

### T-015：Phase 1 最小スキーマ定義ファイルの作成（Req 2 受入 10・11、reopen R-0 2026-06-18）

- **対応設計節**：design.md §軽量版検査スクリプトモデル §5（§5.1 required_action.schema.json・§5.2 next_action_response.schema.json）
- **対応要件**：Requirement 2 受入 10・11
- **責務**：`.reviewcompass/schema/required_action.schema.json` と `.reviewcompass/schema/next_action_response.schema.json` の 2 ファイルを TDD で作成する。スキーマ形式は JSON Schema Draft 2020-12。テストファイル `tests/tools/test_phase1_schema_definitions.py` の 17 テストを通過させることで実装の正しさを担保する。スキーマの設計仕様は design.md §5 を正本とし、コード内に語彙を直書きしない。
- **前提タスク**：T-004（`check-workflow-action.py` が参照するスキーマの実体）、T-011（回帰テスト統合）
- **成果物**：
  - `.reviewcompass/schema/required_action.schema.json`（Req 2 受入 10）
  - `.reviewcompass/schema/next_action_response.schema.json`（Req 2 受入 11）
- **完了条件**：
  1. `required_action.schema.json` が design §5.1 の設計（`$schema: https://json-schema.org/draft/2020-12/schema`・`$id: urn:reviewcompass:schema:required_action`・`type: string`・`enum` 19語彙）を満たし、かつ `enum` の配列が D-003 §6 の優先順位順に並んでいること（テストは順序を確認しないため手動確認）
  2. `next_action_response.schema.json` が design §5.2 の設計を満たすこと：最上位5フィールド必須（`verdict`・`exit_code`・`next_action`・`reasons`・`current_state`）、`next_action` 10フィールド必須（`kind`・`required_action`・`active_gate`・`feature`・`phase`・`stage`・`required_feature_scope`・`blocked_by`・`future_gates`・`state_refs`）、`next_action` 内で `properties: { "verdict": false }` による verdict 禁止（手動確認）、`next_action.required_action` が `$ref: "urn:reviewcompass:schema:required_action"` を参照（手動確認、テストは $ref 値を検証しない）、`kind` が 14 値インライン enum であること（手動確認）、条件付き必須フィールドが `if/then` 構文で定義されていること：`repair_reasons`（`required_action = "repair_workflow_state"` のとき必須）・`action_parameters`（`required_action = "run_maintenance"` のとき必須）（手動確認）
  3. `python3 -m pytest tests/tools/test_phase1_schema_definitions.py -v` の 17 テストが全て pass する（exit 0）。ただし17テスト全通過は必要条件であり、完了条件1の enum 順序、完了条件2の手動確認項目（verdict 禁止・kind 14 値の具体値・$ref 具体値・条件付き必須フィールド）の充足は別途手動で確認する
- **テスト要件（TDD：テストは作成済み、失敗状態）**：テストは `tests/tools/test_phase1_schema_definitions.py` に作成済みで commit 済み（失敗状態）。実装でテストを通過させる。テストの変更は禁止。

### T-016：operation contract 語彙と required_action 対応（Req 13、reopen R-0 2026-06-19）

- **対応設計節**：design.md §Requirement 13 設計モデル、§D-003、§XDI-WM-005
- **対応要件**：Requirement 13 受入 1〜10
- **責務**：operation contract を、operation registry / preflight の補助情報ではなく、`next --json` の `required_action` と実行前検査を束ねる正本契約として定義する。`effect_kind`、`phase_boundary`、operation contract response、precondition／postcondition、side effect 宣言、commit boundary 宣言、required_action mapping を構造化し、各 `required_action` が必ず 1 つ以上の operation contract に接続されることを機械検査する。T-014 の registry / read-only preflight は参照側として残し、T-016 が operation contract 語彙・schema・対応表の所有タスクとなる。
- **上流意図継承**：Requirement 13 の目的は「`next --json` が選んだ唯一 action を、記憶や前例ではなく operation contract に基づいて実行できるようにする」ことである。design.md §Requirement 13 は、`stages/operation-contracts.yaml` を operation contract 正本、`stages/operation-registry.yaml` を registry / preflight binding 正本として確定した。T-016 はこの設計に従い、contract 側に副作用・承認要否・順序・前提・事後条件・side effects・承認要否集約規則を置き、registry 側は canonical invocation / workflow binding / policies / contract ID / digest / schema_version 参照だけを持つようにする。preflight は contract を読み取って確認する read-only confirmation であり、contract 更新、operation 実行、approval consume、workflow state 更新を行わない。
- **前提タスク**：T-004（`next --json`）、T-014（operation registry / preflight）、T-015（required_action schema）
- **実装対象ファイル**：
  - `.reviewcompass/schema/effect_kind.schema.json`
  - `.reviewcompass/schema/phase_boundary.schema.json`
  - `.reviewcompass/schema/operation_contract.schema.json`
  - `stages/operation-contracts.yaml`
  - `tools/check_workflow_action/operation_contracts.py`
  - `tools/check-workflow-action.py`（`operation-contract-check --json` サブコマンド追加）
  - `tests/workflow-management/test_operation_contract_schema.py`
  - `tests/workflow-management/test_required_action_contract_mapping.py`
  - `tests/workflow-management/test_operation_contract_cli.py`
- **最初に書く失敗テスト**：
  1. `test_required_action_contract_mapping_covers_required_action_enum`：`required_action.schema.json` の enum 全値が `stages/operation-contracts.yaml` に 1 件以上接続されていなければ失敗する。
  2. `test_operation_contract_check_reports_unmapped_required_action`：一時 fixture で `required_action` を 1 つ未接続にし、`operation-contract-check --json` が `verdict=DEVIATION` を返すことを期待して失敗させる。
  3. `test_commit_boundary_blocks_bypass_for_irreversible_actions`：`commit_stop_point`、`advance_reopen_after_commit_stop_point`、`finalize_reopen` など commit 境界必須 operation が `commit_boundary.required=true` でない場合に失敗する。
  4. `test_registry_references_contract_without_duplicating_contract_fields`：`stages/operation-registry.yaml` が contract の正本 field を複製した場合、または参照 contract ID / digest が不一致の場合に失敗する。
  5. `test_record_human_decision_does_not_satisfy_target_approval_required`：`record_human_decision` の完了だけで対象 operation の `approval_required=true` が満たされた扱いになる場合に失敗する。
  6. `test_preflight_reads_contract_without_mutating_state_or_approval`：operation preflight が contract / workflow state / approval record / side track stack / snapshot / review-run artifact を作成・更新・consume した場合に失敗する。
- **実装順序**：
  1. JSON Schema 3 件を追加し、enum 値は design.md の語彙をそのまま写す。
  2. `stages/operation-contracts.yaml` を新設し、既存 required_action enum 全値を最小契約へ接続する。
  3. `operation_contracts.py` に読み込み、schema 検証、required_action coverage、commit boundary 検査を実装する。
  4. registry / contract 境界検査を追加し、registry 側は `operation_contract` ID / digest / schema_version 参照、contract 側は副作用・承認要否・順序・前提・事後条件・side effects・承認要否集約規則を持つことを検査する。
  5. `tools/check-workflow-action.py` に read-only の `operation-contract-check --json` を追加する。
  6. T-014 の operation registry / preflight とは正本を重複させず、必要な場合は contract id と digest を参照するだけにする。
- **完了条件**：
  1. `effect_kind` と `phase_boundary` が JSON Schema Draft 2020-12 で定義され、未知値・空文字・型不一致を fail-closed にできる。
  2. operation contract が `operation_id`、`required_action`、`effect_kind`、`phase_boundary`、preconditions、postconditions、side_effects、commit_boundary、workflow_state_effect、canonical_invocation を構造化して保持する。
  3. `required_action.schema.json` の enum 全値が operation contract に接続され、未接続・重複矛盾・未知 `required_action` を DEVIATION にする。
  4. commit を強制すべき operation と強制しない operation が `commit_boundary` で区別され、停止点消費・approval consumption・phase boundary などの強制 commit 点を bypass できない。
  5. T-014 の preflight response が operation contract ID / digest / schema_version を参照でき、別正本の再定義を持たない。registry と contract の不一致、参照先欠落、digest drift、正本 field 重複は DEVIATION になる。
  6. operation preflight は read-only confirmation に閉じ、contract 更新、operation 実行、approval consume、workflow state 更新、side track stack 更新、snapshot 保存を行わないことが機械検証される。
- **検証コマンド**：
  - `.venv/bin/python3 -m pytest tests/workflow-management/test_operation_contract_schema.py tests/workflow-management/test_required_action_contract_mapping.py tests/workflow-management/test_operation_contract_cli.py -q`
  - `.venv/bin/python3 tools/check-workflow-action.py operation-contract-check --json`
  - `.venv/bin/python3 -m pytest tests/tools/test_phase1_schema_definitions.py tests/tools/test_operation_registry_preflight.py -q`
- **禁止事項**：
  - `required_action` 語彙を schema、YAML、コードへ別々に手書きして不一致を作らない。
  - T-014 の operation registry を operation contract 正本として上書きしない。
  - operation contract の副作用・承認要否・前提・事後条件を registry に複製して二重正本を作らない。
  - commit 境界必須 operation を WARN に格下げしない。
- **停止条件**：
  - `required_action.schema.json` と `stages/operation-contracts.yaml` の語彙差分が残る場合。
  - 既存 preflight と contract の責務境界が衝突し、どちらを正本にするか判断が必要な場合。

### T-017：承認ゲート・side track stack・workflow-state snapshot（Req 14、reopen R-0 2026-06-19）

- **対応設計節**：design.md §Requirement 14 設計モデル、§XDI-WM-005
- **対応要件**：Requirement 14 受入 1〜10
- **責務**：承認ゲート、side track stack、workflow-state snapshot を同一の状態防御層として追加する。承認ゲートは human / proxy_model decision の対象・根拠・有効期限・消費状態を構造化し、side track stack は本線作業、maintenance、nested issue、post-write verification などの入れ子状態を LIFO で保持する。workflow-state snapshot は `spec.json`、`stages/in-progress/`、pending gates、drafting completed gates、completed gates、worktree digest、staged file set、operation contract を同時点の証跡として記録し、状態 drift を検出する。
- **上流意図継承**：Requirement 14 の目的は、承認・側道・状態可視化を LLM の暗黙解釈ではなく機械可読状態として扱うことである。design.md §Requirement 14 は、approval gate record、side track stack、workflow-state snapshot の保存先・正本性・read-only / mutating 操作境界を確定した。T-017 は `decision_scope=human_only|proxy_allowed|advisory_only` により proxy / human decision 境界を実装し、commit、push、`spec.json` 更新、phase approval、reopen finalize、`approval_required=true` の不可逆 operation 実行許可を human-only として扱う。side track stack は `current` / `inspect` を read-only、`push` / `pop` / `repair` を mutating とし、snapshot は正本ではなく `next --json` と state refs の監査補助として扱う。
- **前提タスク**：T-006（直前ゲート）、T-008（in-progress 管理）、T-014（preflight）、T-016（operation contract）
- **実装対象ファイル**：
  - `.reviewcompass/schema/approval_gate.schema.json`
  - `.reviewcompass/schema/side_track_stack.schema.json`
  - `.reviewcompass/schema/workflow_state_snapshot.schema.json`
  - `tools/check_workflow_action/approval_gate.py`
  - `tools/check_workflow_action/side_track_stack.py`
  - `tools/check_workflow_action/workflow_state_snapshot.py`
  - `tools/check-workflow-action.py`（`workflow-snapshot --json`、`side-track-stack --json` を追加）
  - `tests/workflow-management/test_approval_gate.py`
  - `tests/workflow-management/test_side_track_stack.py`
  - `tests/workflow-management/test_workflow_state_snapshot.py`
  - `tests/workflow-management/test_workflow_snapshot_cli.py`
- **最初に書く失敗テスト**：
  1. `test_workflow_snapshot_includes_reopen_and_worktree_digests`：snapshot に `spec.json.workflow_state`、`recheck`、in-progress sha、pending gates、staged file set digest、worktree dirty path digest が欠けると失敗する。
  2. `test_snapshot_drift_reports_pending_gate_change`：snapshot 後に pending gate を変えた fixture で drift reason が返らなければ失敗する。
  3. `test_side_track_stack_rejects_non_lifo_pop`：LIFO でない pop を `DEVIATION` にしなければ失敗する。
  4. `test_side_track_push_pop_are_mutating_but_current_is_read_only`：`side-track-stack current --json` が正本を書き換えず、push / pop だけが stack state を変更することを期待して失敗させる。
  5. `test_snapshot_is_not_trusted_without_matching_next_action_digest`：snapshot が古い、手動更新された、または `next --json` digest と一致しない場合に通常進行の根拠にできないことを期待して失敗させる。
  6. `test_approval_record_non_approved_decisions_block_irreversible_operation`：rejected / deferred / changes_requested が対象不可逆操作を許可しないことを期待して失敗させる。
  7. `test_proxy_model_cannot_approve_human_only_decision_scope`：`decision_scope=human_only` かつ `decided_by=proxy_model` の approval gate record が不可逆操作を許可しないことを期待して失敗させる。
  8. `test_side_track_pop_unresolved_return_to_routes_to_repair`：pop 後に `return_to` が解決不能、または staged file set が本線復帰条件を満たさない場合に通常作業へ戻らず repair 停止になることを期待して失敗させる。
- **実装順序**：
  1. approval gate / side track stack / snapshot の schema を追加する。
  2. snapshot の読み取り専用 builder を実装し、path と sha256 は repo-relative で安定化する。
  3. drift 検査を `workflow_state`、`recheck`、in-progress sha、pending gate、operation contract digest、staged / dirty digest の順で実装する。
  4. side track stack の `current` を read-only、`push` / `pop` を mutating operation として分け、LIFO、許可ファイル境界、return_to、staged digest を検査する。
  5. approval gate record の decision 4 値、`decision_scope` 3 値、human-only 初期集合、next 分岐を実装し、approved 以外または proxy_model による human-only approval は不可逆操作を許可しない。
  6. side track pop 後の `return_to` 解決、staged file set の本線復帰条件、親子 frame overlap 許可境界を検査する。
  7. CLI は read-only 系と mutating 系を operation contract で分ける。`workflow-snapshot --json` と `side-track-stack current --json` は成果物を書かず、保存が必要な段は別 contract に委ねる。
- **完了条件**：
  1. 承認ゲートは対象 operation、承認 actor、source evidence、target digest、expiry、consume / invalidate 状態を保持し、欠落・期限切れ・対象不一致を fail-closed にする。
  2. proxy_model decision は人間承認を置換しない対象と、代行可能な判断対象を schema / gate で区別する。
  3. side track stack は push / pop / current の 3 操作を持ち、親 task、許可ファイル、戻り条件、nesting depth、関連 operation を検査する。
  4. side track 完了後に本線へ戻る条件が未充足なら通常進行を返さず、必要 action を `next --json` に反映する。
  5. workflow-state snapshot は正本状態と worktree / staged 対象を同時点で固定し、snapshot と現状態の drift を WARN または DEVIATION として検出する。snapshot payload は最低限、`spec.json.workflow_state`、`spec.json.reopened`、`spec.json.recheck`、`stages/in-progress/` の対象ファイル path / sha256、`pending_gates`、`drafting_completed_gates`、`completed_gates`、`downstream_impact_decisions`、参照した operation contract id / sha256、staged file set digest、worktree dirty path digest を保持する。
  6. snapshot は commit / phase transition / approval consumption など T-016 の commit boundary と接続する。
  7. snapshot drift 判定は、`pending_gates`、`drafting_completed_gates`、`completed_gates`、operation contract digest、staged file set digest、worktree dirty path digest のいずれかが snapshot 時点と異なる場合を個別理由として返す。
  8. snapshot は正本ではなく、古い snapshot、手動更新 snapshot、`next --json` digest と一致しない snapshot は操作許可の根拠にしない。
  9. side track stack の保存先、read-only 操作、mutating 操作、return_to 解決、commit / push 直前の digest 照合がそれぞれ機械検査される。
  10. `decision_scope=human_only` の承認は proxy_model decision で通過できず、human-only 初期集合が機械検査される。
  11. side track pop 後に `return_to` が解決できない、または staged file set が本線復帰条件を満たさない場合、通常作業へ戻さず `repair_workflow_state` または同等の停止状態を返す。
- **検証コマンド**：
  - `.venv/bin/python3 -m pytest tests/workflow-management/test_approval_gate.py tests/workflow-management/test_side_track_stack.py tests/workflow-management/test_workflow_state_snapshot.py tests/workflow-management/test_workflow_snapshot_cli.py -q`
  - `.venv/bin/python3 tools/check-workflow-action.py workflow-snapshot --json`
  - `.venv/bin/python3 -m pytest tests/tools/test_check_workflow_action.py -k \"reopen or maintenance or commit_stop_point\" -q`
- **禁止事項**：
  - snapshot 作成コマンドで正本ファイルや approval record を書き換えない。
  - proxy_model decision を commit / push / spec.json 更新の人間承認として扱わない。
  - proxy_model decision を `decision_scope=human_only` の承認として扱わない。
  - side track stack の current だけを見て親 task / 戻り条件を省略しない。
  - read-only CLI と mutating CLI を同じ operation として曖昧に扱わない。
- **停止条件**：
  - snapshot digest が実行ごとに不安定で、同じ状態から同じ値を再現できない場合。
  - proxy_model 代行可否の境界が既存承認規律と衝突する場合。
  - stack state の保存先または mutation boundary を design.md の意図と一致させられない場合。

### T-018：構造化有効プロンプトと prompt audit（Req 15、reopen R-0 2026-06-19）

- **対応設計節**：design.md §Requirement 15 設計モデル、§XDI-WM-005
- **対応要件**：Requirement 15 受入 1〜7
- **責務**：`effective prompt` を単なる連結テキストではなく、language task I/O、入力 artifact、制約、禁止事項、出力 schema、completion routing、監査 anchor を持つ構造化成果物として生成・検査する。LLM に実行させる作業と機械が検査する作業を分け、prompt 内の on_completion 指示が workflow state を暗黙に変更しないようにする。prompt audit は、元資料 digest、schema coverage、禁止指示、機械実行タスク混入、出力 schema 不整合を検出する。
- **前提タスク**：T-004（effective prompt 生成）、T-014（operation preflight）、T-016（operation contract）、T-017（snapshot）
- **実装対象ファイル**：
  - `.reviewcompass/schema/language_task_io.schema.json`
  - `.reviewcompass/schema/effective_prompt_manifest.schema.json`
  - `tools/check_workflow_action/effective_prompt_builder.py`
  - `tools/check_workflow_action/prompt_audit.py`
  - `tools/check-workflow-action.py`（`prompt-audit --prompt-manifest <path> --json` を追加）
  - `tests/workflow-management/test_language_task_io_schema.py`
  - `tests/workflow-management/test_effective_prompt_manifest.py`
  - `tests/workflow-management/test_prompt_audit.py`
  - `tests/workflow-management/test_prompt_manifest_rounds_recording.py`
- **最初に書く失敗テスト**：
  1. `test_effective_prompt_manifest_covers_source_digests`：manifest の source artifact に path と sha256 がない場合に失敗する。
  2. `test_prompt_audit_rejects_direct_state_mutation_instruction`：prompt の completion routing に spec.json 直接変更や commit 実行指示が含まれると `DEVIATION` を期待して失敗する。
  3. `test_rounds_records_prompt_manifest_without_removing_text_prompt_fields`：review-run の `rounds.yaml` が manifest path / sha256 を追加しつつ既存 text field を保持しなければ失敗する。
  4. `test_prompt_audit_rejects_machine_execution_steps_beyond_state_mutation`：review-run artifact 作成、approval consume、side-track mutation、operation execution などの機械実行手順が prompt の language_task に残ると `DEVIATION` になることを期待して失敗させる。
- **実装順序**：
  1. language task I/O と effective prompt manifest の schema を追加する。
  2. 既存 effective prompt 生成は壊さず、manifest builder を横に追加する。
  3. prompt audit で source digest、禁止 action、output schema、operation contract 参照、機械実行タスク混入を検査する。
  4. `run_role.py` / `run_review.py` の rounds 記録へ manifest path / sha256 を追加する。既存 `effective_prompt_path` / `effective_prompt_sha256` は P1 互換として残す。
  5. `prompt-audit` CLI を read-only として追加し、manifest 欠落時と text-only 互換時の WARN / DEVIATION を固定する。
- **完了条件**：
  1. effective prompt manifest が source artifacts、sha256、required disciplines、operation contract、expected output schema、completion routing を構造化して保持する。
  2. language task I/O schema が input role、allowed action、forbidden action、output contract、evidence anchors を定義し、未知 field / 欠落を fail-closed にする。
  3. prompt に含まれる on_completion / next step 指示は `next --json` または operation contract への参照に限定され、spec.json・phase・commit の直接変更指示を禁止する。
  4. prompt audit が元資料 digest 不一致、必須 source 欠落、機械実行タスク混入、出力 schema 欠落、禁止事項違反を DEVIATION にする。機械実行タスク混入には、commit / push / spec.json 更新 / phase 移行だけでなく、review-run artifact 作成、approval consume、side-track mutation、operation execution を含める。
  5. review-run / role-run の `rounds.yaml` は prompt manifest path と sha256 を、既存 T-004 の `effective_prompt_path` / `effective_prompt_sha256` を置換せず拡張 field として記録する。移行中は既存 text-only effective prompt field と structured manifest field の併存を許可し、manifest field がある場合は manifest sha256 と source digest coverage を正本検査対象にする。manifest field がなく text-only field のみの場合は P1 互換として WARN、manifest field があるが text-only field と対象 decision point が不一致の場合は DEVIATION、どちらの field もない場合は DEVIATION とする。
- **検証コマンド**：
  - `.venv/bin/python3 -m pytest tests/workflow-management/test_language_task_io_schema.py tests/workflow-management/test_effective_prompt_manifest.py tests/workflow-management/test_prompt_audit.py tests/workflow-management/test_prompt_manifest_rounds_recording.py -q`
  - `.venv/bin/python3 tools/check-workflow-action.py prompt-audit --prompt-manifest <fixture-or-generated-manifest> --json`
  - `.venv/bin/python3 -m pytest tests/tools/test_effective_prompt_contract.py tools/api_providers/tests/test_run_review.py -q`
- **禁止事項**：
  - 既存 text-only effective prompt path を同時削除しない。
  - prompt の on_completion に spec.json 更新、commit、push、phase 移行を直接書かない。
  - prompt audit の WARN / DEVIATION を provider や model 名に依存させない。
- **停止条件**：
  - manifest と既存 effective prompt の decision point を一意に対応付けられない場合。
  - `rounds.yaml` の既存互換フィールド削除が必要になった場合。

### T-019：段階的実装計画 Phase 0〜6 と proxy_model triage decision 機械処理化（Req 16、reopen R-0 2026-06-19）

- **対応設計節**：design.md §Requirement 16 設計モデル、§XDI-WM-005
- **対応要件**：Requirement 16 受入 1〜12
- **責務**：Requirement 13〜15 の実装を Phase 0〜6 に分け、各 phase の開始条件・完了条件・禁止事項・成果物・回帰範囲を機械的に確認できるようにする。proxy_model triage decision は review-run の raw response、triage 候補、decision prompt、decision output、採用理由、最終反映先を束ね、human decision と proxy_model decision の境界を operation contract / approval gate / prompt audit に接続する。review-wave への影響は consumer impact として追跡し、未反映のまま完了できないようにする。
- **上流意図継承**：Requirement 16 の目的は、選択層と実行層の機械化を一度に混ぜず、既存挙動を壊さない順序で TDD 実装できるようにすることである。design.md §Requirement 16 は Phase 0〜6 の順序、active reopen scope と impact review scope の分離、proxy_model triage decision の証跡処理、human-required predicate の優先順位を定義している。実装では phase plan の entry / exit criteria と forbidden operations を正本化し、human-required decision は triage item、approval gate record、operation contract の `approval_required`、review-wave impact evidence、downstream impact decisions / scope 整合から machine-readable に導出する。`decision_scope=human_only`、未解決 approval gate、`approval_required=true`、未解決 review-wave impact evidence は proxy decision より常に優先する。`spec.json.reopened` は履歴であり active scope ではない。
- **前提タスク**：T-012（review-wave summary）、T-014（operation preflight）、T-016（operation contract）、T-017（approval / snapshot）、T-018（structured prompt）
- **実装対象ファイル**：
  - `stages/workflow-management-implementation-phases.yaml`
  - `.reviewcompass/schema/implementation_phase.schema.json`
  - `.reviewcompass/schema/proxy_triage_decision.schema.json`
  - `tools/check_workflow_action/implementation_phases.py`
  - `tools/check_workflow_action/proxy_triage_decisions.py`
  - `tools/check-workflow-action.py`（`implementation-phase-check --feature workflow-management --json`、`proxy-triage-decision-check --run <path> --json` を追加）
  - `tests/workflow-management/test_implementation_phase_plan.py`
  - `tests/workflow-management/test_proxy_triage_decision_machine.py`
  - `tests/workflow-management/test_review_wave_consumer_impact.py`
  - `tests/workflow-management/test_implementation_phase_cli.py`
- **最初に書く失敗テスト**：
  1. `test_implementation_phase_plan_covers_phase_0_to_6`：Phase 0〜6 の欠落、順序違反、entry / exit criteria 欠落で失敗する。
  2. `test_proxy_triage_decision_requires_raw_prompt_candidate_selected_reason_target`：proxy decision の raw、prompt、候補、採用、理由、反映先のいずれかが欠けると失敗する。
  3. `test_reopened_history_flag_is_not_active_scope`：`spec.json.reopened` だけを根拠に active reopen scope と判定すると失敗する。
  4. `test_human_required_decision_blocks_proxy_application`：triage item / approval gate / operation contract / review-wave impact evidence のいずれかが human-required を示す場合に、proxy decision apply が失敗する。
  5. `test_phase_checker_uses_entry_exit_and_forbidden_operations`：phase plan が entry criteria 未充足、exit criteria 未充足、または forbidden operation 実行済みの場合に DEVIATION を返すことを期待して失敗させる。
  6. `test_human_required_priority_overrides_proxy_approved_leave_as_is`：`decision_scope=human_only`、未解決 approval gate、`approval_required=true`、未解決 review-wave impact evidence がある場合、triage の `leave-as-is` や `proxy_approved` があっても proxy apply が失敗する。
  7. `test_proxy_triage_requires_complete_finding_cluster_coverage`：finding / cluster coverage が不足・過剰・競合する場合に proxy decision 展開が DEVIATION になる。
- **実装順序**：
  1. implementation phase plan schema と `stages/workflow-management-implementation-phases.yaml` を追加する。
  2. phase check を read-only で実装し、Phase 0〜6 coverage、順序、entry / exit criteria、禁止 operation を検査する。
  3. human-required predicate を、triage item、approval gate record の `decision_scope` / decision / decided_by、operation contract の `approval_required` / `phase_boundary`、review-wave impact evidence、downstream impact decisions / scope 整合から機械的に導出する。
  4. human-required の優先順位を実装し、human-only / 未解決 approval / `approval_required=true` / 未解決 review-wave impact evidence を proxy apply より優先する。
  5. proxy triage decision schema と検査器を追加し、provider / model 名ではなく証跡 completeness、対象一致、coverage、human-required predicate で判定する。
  6. review-wave consumer impact 検査を、review-wave summary、carry-forward register、downstream impact decisions、spec recheck から組み立てる。
  7. CLI 2 件を追加し、既存 review triage の生成物を壊さず検査だけを行う。
- **完了条件**：
  1. Phase 0〜6 が schema 化され、各 phase の entry criteria、exit criteria、allowed operations、forbidden operations、required tests、commit boundary を検査できる。
  2. Phase の順序違反、未完了 exit criteria、禁止 operation 実行、必要 snapshot 欠落を DEVIATION にする。
  3. proxy_model triage decision が raw response、triage item、decision prompt、candidate decisions、selected decision、reasoning summary、final application target を構造化して保持する。
  4. proxy_model decision は LLM/provider/model 名ではなく、証跡 completeness、対象一致、decision schema、approval gate 可否で判定する。
  5. human 承認が必要な decision を proxy_model decision で通過させない。human-required は triage item、approval gate record の `decision_scope` / decision / decided_by、operation contract の `approval_required` / `phase_boundary`、review-wave impact evidence、downstream impact decisions / scope 整合から導出され、判定元が欠ける場合は DEVIATION にする。
  6. review-wave summary / carry-forward register / downstream impact decisions への consumer impact が未反映なら完了判定を出さない。必須入力は `review-wave-summary` JSON / Markdown 出力、`learning/workflow/carry-forward-register/reviewcompass-import.yaml`、reopen in-progress / completed YAML の `downstream_impact_decisions`、`spec.json.recheck.impacted_downstream_phases`、`spec.json.reopened` とする。
  7. T-019 は `spec.json.reopened` を履歴フラグとして扱い、active reopen scope と同一視しない。active reopen scope は reopen in-progress / completed YAML の `pending_gates`、`completed_gates`、`drafting_completed_gates`、`feature_impact_decisions`、`downstream_impact_decisions` から解決し、impact review scope は review-wave summary と downstream impact decisions から解決する。両 scope が混同・欠落・矛盾した場合は DEVIATION とする。
  8. `decision_scope=human_only`、未解決 approval gate、`approval_required=true` の対象 operation、未解決 review-wave impact evidence は proxy_model の判断より常に優先し、triage 上の `leave-as-is` や `proxy_approved` で打ち消されない。
- **検証コマンド**：
  - `.venv/bin/python3 -m pytest tests/workflow-management/test_implementation_phase_plan.py tests/workflow-management/test_proxy_triage_decision_machine.py tests/workflow-management/test_review_wave_consumer_impact.py tests/workflow-management/test_implementation_phase_cli.py -q`
  - `.venv/bin/python3 tools/check-workflow-action.py implementation-phase-check --feature workflow-management --json`
  - `.venv/bin/python3 tools/check-workflow-action.py proxy-triage-decision-check --run <fixture-or-review-run> --json`
- **禁止事項**：
  - `spec.json.reopened` を active reopen scope として扱わない。
  - proxy_model decision を human-required decision の承認として通過させない。
  - review-wave consumer impact を carry-forward register なしで完了扱いにしない。
- **停止条件**：
  - Phase 0〜6 の順序や境界が design.md と一致しない場合。
  - proxy decision 証跡の既存形式が複数あり、単一 schema へ写像できない場合。

## 要件追跡（Requirements Traceability）

| 要件 | 対応タスク |
|------|-----------|
| Requirement 1 受入 1：YAML 静的列挙、Markdown 動的解析しない | T-003 |
| Requirement 1 受入 2：9 ファイル体制 | T-001（配置）＋ T-002（feature-dependency）＋ T-003（8 ファイル） |
| Requirement 1 受入 3：段名／actor／証跡パス／必須節／完了判定 | T-003 |
| Requirement 1 受入 4：feature_order 参照 | T-002（参照先）＋ T-003（参照側） |
| Requirement 1 受入 5：YAML 1 箇所修正、Markdown 整合は人手 | T-003 |
| Requirement 1 受入 6：機能横断段 review-wave の作業内容（7 モデル評価 2 回方式） | T-003（`cross-spec-alignment.yaml` 枠）＋ T-009（運用文書）※ 段集合本体は DVT-W004 で延期、cross-spec-alignment.yaml 確定後に符号化（F-001 対処 2026-05-28） |
| Requirement 2 受入 1：Python 実装 | T-004 |
| Requirement 2 受入 2：証跡＋必須節のみ判定 | T-004 |
| Requirement 2 受入 3：中身の妥当性判定しない | T-004（判定範囲）＋ T-009（運用文書での明示） |
| Requirement 2 受入 4：結論不能は fail（fail-closed） | T-004（パースエラー）＋ T-006（ゲート） |
| Requirement 2 受入 5：in-progress 警告 | T-004（警告出力）＋ T-008（in-progress 管理） |
| Requirement 2 受入 10：required_action 語彙スキーマ定義 | T-015 |
| Requirement 2 受入 11：next_action_response 応答スキーマ定義 | T-015 |
| Requirement 3 受入 1：author／reviewer 必須 | T-005 |
| Requirement 3 受入 2：identity 同一を許容しない | T-005 |
| Requirement 3 受入 3：subagent_mediated の判定役は別エンティティ | T-005（複合役許容） |
| Requirement 3 受入 4：front-matter 検査、別モデル／別 session は第 1 層対象外 | T-005（検査範囲）＋ T-009（運用文書での明示） |
| Requirement 4 受入 1：4 種類の不可逆操作 | T-006 |
| Requirement 4 受入 2：pass ＋ in-progress 空、毎回独立走行 | T-006（独立走行）＋ T-008（in-progress 連動） |
| Requirement 4 受入 3：fail-closed | T-004 ／ T-006 ／ T-007 ／ T-008（全体方針） |
| Requirement 4 受入 4：最小集合方針 | T-006 |
| Requirement 4 受入 5：commit 承認レコード・staged `target_sha256` | T-006（互換入力検査）＋ T-011（回帰テスト） |
| Requirement 4 受入 6：nonce challenge・target digest・consume | T-004（commit-approval サブコマンドと `--json` 契約）＋ T-006（prepare／record／validation／invalidate／consume／consume 永続化失敗）＋ T-011（統合テスト） |
| Requirement 4 受入 7：LLM 非依存・保証範囲 | T-006（schema 禁止フィールド、判定入力限定、`attestation_type`、`guarantee_scope`）＋ T-011（統合テスト） |
| Requirement 4 受入 8：LLM commit 実行代行承認の正式 CLI | T-004（`commit-approval delegate-execution --source-text-stdin --json`）＋ T-006（delegation record 生成／validation／invalidate／consume／`--execution-actor llm` gate）＋ T-011（統合テスト） |
| Requirement 5 受入 1：手戻り種別の二次元表記 | T-003（reopen-procedure.yaml）＋ T-007（解決ロジック） |
| Requirement 5 受入 2：trigger_map | T-003（trigger_map 列挙）＋ T-007（解決） |
| Requirement 5 受入 3：actor=human で停止 | T-007 |
| Requirement 5 受入 4：人間承認なしに進まない | T-007 |
| Requirement 5 受入 5：種別判定根拠の保存 | T-001（雛形配置）＋ T-007（読み込み機構） |
| Requirement 6 受入 1：in-progress ファイル配置 | T-001（配置）＋ T-008（管理機構） |
| Requirement 6 受入 2：必須フィールド | T-008 |
| Requirement 6 受入 3：session 開始時の標準フロー | T-008（実装）＋ T-009（運用文書） |
| Requirement 6 受入 4：完了時の移動 | T-008 |
| Requirement 6 受入 5：in-progress ある状態での遮断 | T-006 ／ T-008 連動 |
| Requirement 7 受入 1：第 1 層の限界の明文化 | T-009 |
| Requirement 7 受入 2：第 2〜5 層を宿題として参照 | T-009 |
| Requirement 7 受入 3：第 5 層運用ルールの反映 | T-009 |
| Requirement 7 受入 4：第 1 層の限界の運用文書への明示 | T-009 |
| Requirement 8 受入 1：feature-dependency.yaml が一元保管先 | T-002 |
| Requirement 8 受入 2：features ＋ feature_order、2 形式の depends_on | T-002 |
| Requirement 8 受入 3：feature_order 参照 | T-003 |
| Requirement 8 受入 4：1 箇所修正で完結 | T-002（運用文書）※ T-009 は本受入に直接寄与しないため追跡先から除外（F-003 対処 2026-05-28） |
| Requirement 8 受入 5：所有者は本機能、他機能は参照のみ | T-002（運用文書） |
| Requirement 9 受入 1：後追い intent を既存システムへ適用する reopen 分類 | T-007 |
| Requirement 9 受入 2：受け皿あり／なし／人間判断の分岐 | T-004 ＋ T-007 |
| Requirement 9 受入 3：downstream impact decision の証跡保持 | T-007 ＋ T-008 |
| Requirement 9 受入 4：conformance-evaluation 候補を実行命令にしない | T-007 ＋ T-008 |
| Requirement 9 受入 5：drafting-before-review の機械強制 | T-004 ＋ T-008 |
| Requirement 9 受入 6：side track と本線 reopen の分離 | T-008 ＋ T-009 |
| Requirement 10 受入 1：要約サブコマンド・読み取り元 | T-012（T-002／T-003／T-004 を前提） |
| Requirement 10 受入 2：出力項目 | T-012 |
| Requirement 10 受入 3：Markdown／JSON 両方・安定スキーマ・情報同等 | T-012 |
| Requirement 10 受入 4：結論不能は fail-closed・機械可読シグナル | T-012（T-004 の fail-closed と整合） |
| Requirement 10 受入 5：読み取り専用・自身の出力のみ保存 | T-012 |
| Requirement 11 受入 1：決定記録スキーマ・category 種別判定基準・going-forward 適用 | T-013 |
| Requirement 11 受入 2：multiplicity:bundled の fail-closed・束ね例外 3 条件 | T-013 |
| Requirement 11 受入 3：逐語照合・正規化規則・保留管理・照合不合格時 pending 維持 | T-013 |
| Requirement 11 受入 4：内容なし語リスト・判定ロジック・設定ファイル配置 | T-013 |
| Requirement 11 受入 5：サブコマンド呼び出し形式・--all（bundle-exceptions/ 除外）・読み取り専用例外（--verify-pending） | T-013 |
| Requirement 11 受入 6：lint が内部エラー時に unverifiable 判定・人が設定するのは口頭合意等の場合のみ | T-013 |
| Requirement 11 受入 7：commit 直前ゲート組み込み（pending=WARN・unverifiable=DEVIATION） | T-013 |
| Requirement 12 受入 1：operation registry | T-014 |
| Requirement 12 受入 2：read-only preflight | T-014 |
| Requirement 12 受入 3：共通 response・verdict・fail-closed | T-014 |
| Requirement 12 受入 4：command validation と parser / parser adapter 照合 | T-014（T-004 の parser 接続を前提） |
| Requirement 12 受入 5：worktree / pending / integrity conflict 分離 | T-014（T-006／T-008 と連動） |
| Requirement 12 受入 6：review artifact / bundle / approval 作成前検査 | T-014（T-012／T-013 と連動） |
| Requirement 12 受入 7：serial_only approval chain | T-014（T-004／T-006／T-011 と連動） |
| Requirement 12 受入 8：current-session formal record guard | T-014（T-008 と連動） |
| Requirement 12 受入 9：nested issue handling | T-014（T-008 と連動） |
| Requirement 12 受入 10：deployment / export preflight | T-014 |
| Requirement 12 受入 11：reopen scope / impact review scope 分離 | T-014（T-007／T-008 と連動） |
| Requirement 12 受入 12：LLM / provider / model 非依存 | T-014（T-006 の非依存契約と整合） |
| Requirement 12 受入 13：`next --json` 状態一意性 | T-014（T-004 の `next` 契約を拡張） |
| Requirement 13 受入 1〜2：operation contract 語彙・schema | T-016 |
| Requirement 13 受入 3〜4：required_action と operation contract の対応 | T-016（T-015 と連動） |
| Requirement 13 受入 5〜7：precondition / postcondition / side effect / phase boundary | T-016（T-014 と連動） |
| Requirement 13 受入 8〜10：commit boundary 強制・bypass 防止・LLM 非依存 | T-016（T-006／T-014 と連動） |
| Requirement 13 受入 11〜12：registry / contract 単一正本境界、drift / 重複検出、preflight read-only 境界 | T-016（T-014 と連動） |
| Requirement 14 受入 1〜3：承認ゲート、proxy_model / human decision 境界、decision 消費状態 | T-017（T-006／T-016 と連動） |
| Requirement 14 受入 4〜7：side track stack、push / pop / current、本線復帰条件、許可ファイル・nesting depth | T-017（T-008／T-014 と連動） |
| Requirement 14 受入 8〜10：workflow-state snapshot、staged file set / worktree digest、pending / completed gates drift 検出 | T-017（T-016 と連動） |
| Requirement 14 受入 11〜12：proxy / human decision_scope、read-only / mutating 操作境界 | T-017（T-006／T-016 と連動） |
| Requirement 15 受入 1〜2：language task I/O と effective prompt manifest | T-018 |
| Requirement 15 受入 3〜5：prompt audit、on_completion 制御、機械実行タスク混入防止 | T-018（T-004／T-016 と連動） |
| Requirement 15 受入 6〜7：review-run 記録、structured prompt manifest、T-004 rounds.yaml field 互換、text-only 移行境界 | T-018（T-014／T-017 と連動） |
| Requirement 16 受入 1〜4：Phase 0〜6 実装計画と phase gate | T-019（T-016〜T-018 と連動） |
| Requirement 16 受入 5〜9：proxy_model triage decision の機械処理化 | T-019（T-017／T-018 と連動） |
| Requirement 16 受入 10〜12：review-wave consumer impact blocking、carry-forward / downstream impact evidence、active reopen scope / impact review scope 分離 | T-019（T-012／T-016〜T-018 と連動） |
| Requirement 16 受入 13〜14：human-required predicate、proxy decision 優先順位、競合解決 | T-019（T-017／T-018 と連動） |
| Boundary Context 隣接期待（self-improvement との接合面、A-007 案 2／A-012） | T-010 |

## テスト戦略の継承（Test Strategy Inheritance）

design.md §テスト戦略の 4 検証類を T-011 にまとめて継承する。各検証類の対応タスクは次のとおり：

- 単体テスト → T-002 ／ T-003 ／ T-004 ／ T-005 ／ T-008 ／ T-014 ／ T-015 ／ T-016 ／ T-017 ／ T-018 ／ T-019 個別 ＋ T-011 統合
- 統合テスト → T-006 ／ T-007 ／ T-010 ／ T-014 ／ T-016 ／ T-017 ／ T-018 ／ T-019 個別 ＋ T-011 統合
- 異常系 fixture → 各タスクで fail-closed テスト ＋ T-011 統合
- 境界条件 → T-002（依存マップ境界）／ T-003（テンプレート変数境界）／ T-008（複数 in-progress 並存）／ T-016（commit boundary）／ T-017（side track / snapshot drift）／ T-018（prompt / machine task 境界）／ T-019（proxy_model / human decision 境界）＋ T-011 統合

## 完成判定基準（Completion Criteria）

本タスク文書は次を満たすときに完了とみなす：

- T-001〜T-019 のすべてが起草・実装・テスト・コミット完了
- tasks.md の各タスクが、実装対象ファイル、最初に書く失敗テスト、実装順序、完了条件、検証コマンド、禁止事項、停止条件を持ち、implementation-drafting.md なしで実装に着手できる粒度である
- design.md §完成判定基準の 7 項目すべてが T-011 の統合テストで pass
- foundation が所有する語彙正本のうち本機能が参照する `review_mode` を再定義せず参照のみで使用し、所見系（`counter_status`／`severity`／`final_label`／`confidence_label`）・状態軸系（`run_status`／`validator_status`／`human_signoff_status`／`evidence_class`）を参照していないことが、機械検証で確認できる（A-003 対処 2026-05-28）
- workflow-management 所有の正本（`completion_predicate` 述語集合 7 値 ／ `verdict` 3 値 OK／WARN／DEVIATION ／ 手戻り種別記号 5 値 N／R／D／A／I ／ 依存種別 2 値 `hard`／`review`）が T-002 ／ T-003 ／ T-004 ／ T-007 の成果物で正本として確定されている
- 各タスクの成果物配置が design.md §全体構造 と一致
- 各タスクの依存順が守られている（前提タスクなしで後続タスクを開始しない）
- 遅延確認事項テーブル（DVT）内の未解除項目がない（または延期理由が明記されている）

## 変更意図（Change Intent）

本タスク文書は workflow-management 機能を「思想は継承、実装は 1／10」（計画書 §5.4 軽量化方針）の精神で実装するため、次を採用する：

- **一気通貫粒度**：1 タスク ＝ 1 つの所有モデル領域。foundation T-001〜T-010 ／ runtime T-001〜T-011 ／ evaluation T-001〜T-011 ／ analysis T-001〜T-011 の粒度方針を継承
- **所有モデル単位の分離**：design.md の所有モデル（段集合 ／ 検査スクリプト ／ 起草者判定者分離 ／ 直前ゲート ／ reopen 機械強制 ／ session 跨ぎ ／ 多層防御 ／ 機能依存マップ ／ review-wave 要約 ／ 重要決定の出典検査 ／ operation registry / preflight）に各タスクを対応付け
- **依存順の明示**：T-001（配置）→ T-002（依存マップ）→ T-003（段集合 YAML）→ T-004（検査スクリプト本体）→ T-005〜T-008（各機械検査）→ T-009（運用文書）→ T-010（規律変更接合面）→ T-011（統合テスト）の流れを固定
- **fail-closed の全面採用**：判断 3 を全タスクで徹底、結論不能（YAML パースエラー ／ 証跡欠落 ／ 必須フィールド欠落 ／ 未知の値）は必ず DEVIATION で遮断
- **最小集合方針**：判断 4 を T-006 で徹底、中間段の遷移には機械ゲートを置かない
- **contract consumer 原則の徹底**：foundation が所有する語彙正本を再定義せず参照のみで使用（本機能が参照するのは `review_mode` のみ。所見系・状態軸系は責務外で不参照、A-003 対処 2026-05-28）、本機能所有の正本（`completion_predicate` 述語 7 値 ／ `verdict` 3 値 ／ 手戻り種別記号 5 値 ／ 依存種別 2 値）は本機能で確定
- **2026-06-08 の design 再確認への対応**：intent の「レビュー収集処理を事前設定の写像にしない」意図は、T-004 の `next` による上流更新再展開、T-006 の不可逆操作直前ゲート、T-008 の session 跨ぎ状態管理、T-002 の機能依存マップ一元化で受けられるため、タスク追加は不要と確認
- **2026-06-08 の reopen 判定修正**：完了済み workflow で上流正本が後続成果物より新しい場合、T-004 の `next` は `reopen_classification_required` を返し、単なる再確認ではなく reopen 分類と `reopen-start` へ進ませる。テストは intent → feature-partitioning、requirements → design、tasks → implementation の代表経路を覆う。
- **2026-06-09 の後追い intent 追加への対応**：既存システムに intent を後から追加した場合、conformance-evaluation から受け取る差分候補を実行命令にせず、T-007 で既存 feature reopen／新規 feature 必要／人間判断必要に分類する。T-004 は drafting-before-review を機械強制し、T-008 は `downstream_impact_decisions` と `drafting_completed_gates` を保持する。正式な requirements／design／tasks／implementation 更新は reopen 手続きで行う。
- **テスト戦略の継承**：design.md §テスト戦略の 4 検証類を T-011 で網羅
- **要件追跡表の双方向整合チェックを T-011 に組み込み**：foundation T-010 ／ runtime T-011 ／ evaluation T-011 ／ analysis T-011 の方針を踏襲
- **遅延確認事項テーブル（DVT）の活用**：未確定上流仕様（段階 3 Claude Code フック ／ 既存レビュー記録の遡及検査 grandfathering ／ 規律変更の所定手続きの段集合 ／ cross-spec-alignment.yaml の段集合）を DVT で集約管理、T-011 完了条件で未解除項目がないことをゲート化（evaluation T-011 ／ analysis T-011 の方針継承）
- **自律進行**：実装段で per-task 承認は取らず、コミット・プッシュ・spec.json 更新・フェーズ移行のみ明示承認（規律 [[implementation-autonomy]] 準拠）
- **計画書 §5.4 軽量化方針との整合**：節ハッシュ・supersedes リンク・通過マーカー後続確認・独立再導出パーサ・実行台帳の機構全体は導入せず、`required_sections` 配列と `completion_predicate` 述語集合、構造化参照、機械検証可能な fail-closed 判定のみで mandatory ／ deferred を符号化
- **2026-06-15 reopen R-0（decision-source-lint）Req 11 への対応**：重要決定の出典検査・束ね検出・逐語照合・内容性検査と構造化決定記録の新設を T-013 として追加。decision-source-lint サブコマンドを commit 直前ゲートに統合し、pending=WARN・unverifiable=DEVIATION で fail-closed を保証する。
- **2026-06-15 reopen R-0（commit-approval-nonce）Req 4 受入 6〜7 への対応**：LLM 介在の commit 承認を staged 内容に束縛する nonce challenge は既存の不可逆操作直前ゲート強化であるため新タスク化せず、T-004 に commit-approval サブコマンド、T-006 に validation／consume／redaction／LLM 非依存 schema、T-011 に統合テストとして展開する。
- **2026-06-16 reopen R-0（commit-execution-delegation-formal-cli）Req 4 受入 8 への対応**：LLM の commit 実行代行承認は staged 内容承認とは別責務だが、既存の commit 直前ゲート領域で受けられるため新タスク化しない。T-004 に `commit-approval delegate-execution` サブコマンド、T-006 に `.reviewcompass/runtime/approvals/commit-execution-delegation.json` の生成／validation／invalidate／consume／`--execution-actor llm` gate、T-011 に統合テストとして展開する。
- **Req 4 受入 8 と T-013 の責務分離**：T-013 は重要決定の出典検査・束ね検出・逐語照合を担う。Req 4 受入 8 は runtime の commit execution delegation record と commit gate validation を担う。両者はいずれも commit 前の防御に関係するが、T-013 は判断出典の lint、T-004／T-006／T-011 は実行代行承認の CLI・record・gate・統合テストを担当し、互いの責務を置き換えない。
- **2026-06-16 reopen R-0（operation-registry-preflight-unified-design）Req 12 への対応**：推測コマンド、誤 entrypoint、review artifact drift、approval record gap、staged / unstaged 対象誤り、current-session formal record 作成、nested issue scope drift を個別対処ではなく、operation registry / read-only preflight として T-014 に集約する。Phase 1 は作成前に止める read-only 検査に限定し、runner-enabled operation は後段に分離する。
- **2026-06-19 reopen R-0（integrated design）Req 13〜16 への対応**：operation contract 語彙と required_action 対応を T-016、承認ゲート・side track stack・workflow-state snapshot を T-017、構造化有効プロンプトと prompt audit を T-018、Phase 0〜6 実装計画と proxy_model triage decision 機械処理化を T-019 として追加する。T-014 の operation registry / preflight は参照側、T-016〜T-019 は新規正本・状態防御・prompt 防御・実装段階防御の所有タスクとして分離する。

---

## 遅延確認事項テーブル（Deferred Verification Table、DVT）

本テーブルは tasks 段で参照される未確定上流仕様または将来確定予定の事項を集約管理する。evaluation T-011 ／ analysis T-011 の DVT 同型運用。

| ID | 関連タスク | 遅延内容 | 解除トリガー | 状態 |
|---|---|---|---|---|
| DVT-W001 | T-004 ／ T-006 | 段階 3 Claude Code フックとの結合方式（design.md §先送り論点 5）。検査スクリプトを `pre-commit` ／ `pre-push` フックから呼ぶ経路、および Claude Code の PreToolUse フックから呼ぶ経路の具体配線はフェーズ 2 以降の宿題 | フェーズ 2 で段階 3 フック実装着手時に T-004 ／ T-006 完了条件と整合を再確認 | 未解除（フェーズ 2 以降まで延期） |
| DVT-W002 | T-005 | 既存レビュー記録の遡及検査（design.md §先送り論点 4）。Req 3 の front-matter 必須化を既存 7 件（requirements の各機能）に遡及適用するか、grandfathering（移行期免除）で扱うかが未確定 | フェーズ 2 で検査スクリプト導入時に grandfathering 判断を確定、または利用者明示承認で遡及適用範囲を確定 | 未解除 |
| DVT-W003 | T-010 | 規律変更の所定手続きの段集合（design.md §先送り論点 6）。規律変更を `drafting → review → approval` の 3 段で扱うか、`triad-review` を含めるかが未確定。A-007 案 2 対応の細部 | 後続セッションで規律変更の段集合を確定、`stages/discipline-update.yaml` 等として静的列挙 | 未解除 |
| DVT-W004 | T-003 | `cross-spec-alignment.yaml` の段集合（design.md §先送り論点 7）。機能横断整合手続きの段集合本体が未確定、本タスクでは枠のみ確保 | フェーズ 2 以降で機能横断整合手続きの実体設計時に段集合を確定 | 未解除（フェーズ 2 以降まで延期） |
| DVT-W005 | T-010 | 規律変更の所定手続き実装と参照層 5 件（memory 配下の現行規律本体）の memory→repo 移管要否（design.md §先送り論点 8）。参照層が repo 未移管なら本機能の機械検査が効かない構造問題 | 参照層の移管方針を利用者明示承認で確定、またはフェーズ 2 で対象範囲を確定 | 未解除（A-005 対処で登録 2026-05-28） |
| DVT-W006 | T-009 ／ T-010 | 運営ガイド等の現行規律本体の改廃手続きを本機能の規律変更手続きの対象に含めるか（design.md §先送り論点 9） | フェーズ 2 以降で対象範囲を確定 | 未解除（A-005 対処で登録 2026-05-28） |
| DVT-W007 | T-004 ／ T-010 | `depends_on_resolves_correctly` の汎用的な変更検知と recheck 更新発火（design.md §機能依存マップ §6、フェーズ 2 宿題）。**ただし F-016 案 3 により §13.5（self-improvement 接合面）の変更検知のみ T-010 で先行実装**、機能依存マップ全般の汎用変更検知は本 DVT で据え置き | フェーズ 2 で変更検知機構の実装着手時に T-004／T-010 完了条件と整合を再確認 | 未解除（A-006／F-016 調停で登録 2026-05-28、フェーズ 2 以降まで延期） |

**運用ルール**：

- 本テーブルの「未解除」項目があるとき、関連タスクは完了判定可能だが、解除トリガー発火時に再評価が必須
- T-011 完了条件は本テーブル内の未解除項目がない（または延期理由が明記されている）ことをゲート化
- 新規の遅延項目が発生した場合は本テーブルに追記、解除時に「状態」を「解除済（日付、解除根拠）」に更新

---

## 機能横断段への持ち越し事項

本機能の triad-review 段で発見された機能横断波及所見は、carry-forward register 正本 `learning/workflow/carry-forward-register/reviewcompass-import.yaml` に追記し、tasks の機能横断段（review-wave）で消化する。7 モデル評価 2 回目と同根問題集約は本機能では実施せず、機能横断段で一括実施する（(Q2) ／ (ニ) 採用、2 回方式に訂正、計画書 §5.5 ／ §5.9.6 反映済み）。

## 実装由来契約の波及トレース

- `XDI-WM-001`：T-003／T-006／T-009／T-011 の実装・検証範囲で post-write verification、commit approval、audit trail、autonomous ledger の回帰を保持する。commit approval は nonce challenge、canonical target digest、redaction、invalidate／consume、LLM 非依存 schema、commit execution delegation の別 record 化と `--execution-actor llm` gate を含み、判定が LLM／provider／model 名に依存しないことを invariant とする。詳細な設計採用は design.md §実装由来契約の採用を正本とし、本 tasks.md はタスク層から追跡可能であることを示す。
- `XDI-WM-002`：T-004／T-007／T-008／T-011 の実装・検証範囲で、後追い intent の下流再展開、CE 候補の受け取り、drafting-before-review の強制、`downstream_impact_decisions` の証跡保持、side track と本線 reopen の分離を保持する。詳細な設計採用は design.md §既存システム後追い intent モデルと §実装由来契約の採用を正本とし、本 tasks.md はタスク層から追跡可能であることを示す。
- `XDI-WM-004`：T-014 の実装・検証範囲で、operation registry / preflight、正本 invocation、parser / parser adapter 照合、worktree / pending / integrity conflict、review artifact / bundle / approval 作成前検査、serial_only approval chain、current-session formal record guard、nested issue handling、deployment / export preflight、reopen scope / impact review scope、`next --json` 状態一意性、LLM／provider／model 非依存を保持する。詳細な設計採用は design.md §XDI-WM-004 と §Requirement 12 設計モデルを正本とし、本 tasks.md はタスク層から追跡可能であることを示す。
- `XDI-WM-005`：T-016／T-017／T-018／T-019 の実装・検証範囲で、operation contract 語彙、required_action 対応、commit boundary 強制、承認ゲート、side track stack、workflow-state snapshot、構造化有効プロンプト、prompt audit、Phase 0〜6 実装計画、proxy_model triage decision の機械処理化、review-wave consumer impact の完了遮断を保持する。詳細な設計採用は design.md §XDI-WM-005 と §Requirement 13〜16 設計モデルを正本とし、本 tasks.md はタスク層から追跡可能であることを示す。


## .reviewcompass/specs/workflow-management/reviews/2026-06-20-workflow-management-tasks-vertical-redo-review-run-v3/source-excerpts/requirements-req13-16.verbatim.md

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



## .reviewcompass/specs/workflow-management/reviews/2026-06-20-workflow-management-tasks-vertical-redo-review-run-v3/source-excerpts/design-req13-16.verbatim.md

## Requirement 13 設計モデル：operation contract 語彙と required_action 対応（Req 13）

Requirement 13 は、`next --json` の選択層が返す唯一 action を、実行層の operation contract へ接続する。Requirement 12 の operation registry / preflight は「操作開始前の read-only 確認」を担い、本節の operation contract は「操作の副作用・承認要否・順序・前提・事後条件」を定義する。

### 1. 共通語彙 schema（Req 13 受入 1〜2）

Phase 1 で追加する schema は次の 5 ファイルである。いずれも JSON Schema Draft 2020-12 を使い、既存実行挙動を変更しない。

| ファイル | 責務 |
|---|---|
| `.reviewcompass/schema/effect_kind.schema.json` | `read`、`write`、`state_mutation`、`external_call` の 4 値を定義する |
| `.reviewcompass/schema/phase_boundary.schema.json` | `none`、`within_phase`、`phase_transition`、`reopen_boundary`、`commit_boundary`、`push_boundary`、`external_boundary` を定義する |
| `.reviewcompass/schema/operation_contract.schema.json` | operation contract の共通構造を定義する |
| `.reviewcompass/schema/workflow_state_snapshot.schema.json` | Requirement 14 の snapshot 構造を定義する |
| `.reviewcompass/schema/language_task_io.schema.json` | Requirement 15 の `language_task` 入出力構造を定義する |

`effect_kind` は副作用の種類だけを表す。承認要否は `approval_required` として独立させ、`read` でも承認が必要な操作、`state_mutation` でも承認不要な判断記録操作を表現できるようにする。

### 2. operation contract schema（Req 13 受入 3〜4、10）

`operation_contract.schema.json` の論理構造は次を最低限とする。

```yaml
schema_version: string
operation_id: string
required_action: string
effect_kind: read | write | state_mutation | external_call
approval_required: boolean
approval_contract_refs: [string]
phase_boundary: none | within_phase | phase_transition | reopen_boundary | commit_boundary | push_boundary | external_boundary
sequence:
  mode: parallel_ok | serial_only
  internal_steps: [object]
actor:
  kind: human | llm | proxy_model | tool | mixed
  source: string
branching:
  has_branches: boolean
  branches: [object]
max_effect_kind: read | write | state_mutation | external_call
preconditions: [object]
postconditions: [object]
state_refs: [string]
registry_refs: [string]
```

`approval_required` は boolean のみを許容する。外部送信承認、human-only gate、または対象 operation 固有の承認 contract への接続は `approval_contract_refs` または branch / internal step の `approval_contract_ref` に分離し、`approval_required` 欄に方針文を入れてはならない。`preconditions` と `postconditions` は `id`、`description`、`check_kind`、`machine_checkable`、`source_ref`、`failure_verdict` を持つ。`machine_checkable=false` の条件を `OK` の根拠にしてはならない。read-only advisory 段階では確認不能を `WARN` 以上、runner-enabled operation では `DEVIATION` として扱う。

### 3. required_action 19語彙の対応表（Req 13 受入 3〜5、7〜8）

19語彙の正本は `.reviewcompass/schema/required_action.schema.json` である。operation contract の物理正本は `stages/operation-contracts.yaml` とし、`stages/operation-registry.yaml` は operation registry / preflight binding の正本として各 `required_action` から `operation_contract` ID と contract digest / schema_version を参照する。

`stages/operation-contracts.yaml` は、最低限 `required_action`、`effect_kind`、`approval_required`、`approval_contract_refs`、`phase_boundary`、`sequence`、実行主体、分岐条件、preconditions / postconditions、side effects、承認要否の集約規則、branch / internal step semantics、max effect、出力・副作用 contract field を持つ。`stages/operation-registry.yaml` は operation id、canonical invocation、workflow binding、required inputs、target identity、sequence mode、worktree / pending / artifact policy、planned outputs の参照・投影・binding hint、contract ID、contract digest、schema_version を持ち、contract field を再定義しない。registry / preflight は contract と state evidence を読み取って確認するだけで、contract 更新、operation 実行、approval consume、workflow state 作成、review-run artifact 作成、artifact mutation、action 独自選択を行わない。

registry / contract の整合検査は次を fail-closed にする。

- registry が参照する contract ID が存在しない
- registry が保持する contract digest または schema_version が contract 正本と一致しない
- registry が `effect_kind`、`approval_required`、`approval_contract_refs`、`phase_boundary`、preconditions / postconditions、side effects、承認要否の集約規則、branch / internal step semantics、max effect、出力・副作用 contract field を複製して二重正本化している
- contract が required_action schema に存在しない語彙を参照している
- required_action schema の語彙が contract に接続されていない

19語彙の operation contract 基線は次とする。各 contract はこの表を最小境界とし、詳細 preconditions / postconditions は `stages/operation-contracts.yaml` でこの基線から弱めずに具体化する。

| required_action | effect_kind | approval_required | phase_boundary | sequence.mode | actor.kind | 分岐 |
|---|---|---:|---|---|---|---|
| `repair_workflow_state` | `state_mutation` | true | `within_phase` | `serial_only` | `tool` | なし |
| `run_post_write_verification` | `external_call` | false | `within_phase` | `serial_only` | `mixed` | なし |
| `wait_for_human_decision` | `read` | false | `none` | `serial_only` | `human` | なし |
| `record_human_decision` | `state_mutation` | false | `within_phase` | `serial_only` | `tool` | なし |
| `run_maintenance` | `state_mutation` | true | `within_phase` | `serial_only` | `mixed` | あり |
| `advance_reopen_after_commit_stop_point` | `state_mutation` | true | `reopen_boundary` | `serial_only` | `tool` | なし |
| `commit_stop_point` | `state_mutation` | true | `commit_boundary` | `serial_only` | `human` | なし |
| `draft_reopen_plan_candidates` | `write` | false | `within_phase` | `serial_only` | `llm` | なし |
| `apply_approved_reopen_plan` | `state_mutation` | true | `reopen_boundary` | `serial_only` | `tool` | なし |
| `advance_reopen_after_approval_stop_point` | `state_mutation` | true | `reopen_boundary` | `serial_only` | `tool` | なし |
| `repair_canonical_documents` | `write` | false | `within_phase` | `serial_only` | `mixed` | なし |
| `run_reopen_drafting` | `write` | false | `within_phase` | `serial_only` | `llm` | なし |
| `run_reopen_pending_gate` | `external_call` | false | `within_phase` | `serial_only` | `mixed` | あり |
| `collect_required_decisions` | `read` | false | `none` | `serial_only` | `tool` | なし |
| `finalize_reopen` | `state_mutation` | true | `reopen_boundary` | `serial_only` | `tool` | なし |
| `draft_reopen_classification` | `write` | false | `within_phase` | `serial_only` | `llm` | なし |
| `run_reopen_start` | `state_mutation` | true | `reopen_boundary` | `serial_only` | `tool` | なし |
| `run_workflow_stage` | `state_mutation` | true | `phase_transition` | `serial_only` | `mixed` | あり |
| `completed` | `read` | false | `none` | `parallel_ok` | `tool` | なし |

各 `required_action` の preconditions / postconditions 基線は次とする。`stages/operation-contracts.yaml` はこの基線を弱めず、各 `id` を machine-checkable な check と `source_ref` に展開する。

| required_action | precondition baseline IDs | postcondition baseline IDs |
|---|---|---|
| `repair_workflow_state` | `state_evidence_present`, `repair_plan_bound`, `human_only_repair_authorized` | `state_consistency_restored`, `repair_evidence_saved` |
| `run_post_write_verification` | `changed_targets_detected`, `verification_manifest_bound` | `verification_artifact_saved`, `unresolved_findings_recorded` |
| `wait_for_human_decision` | `pending_human_gate_present`, `target_operation_bound` | `no_state_mutation`, `blocked_state_reported` |
| `record_human_decision` | `pending_gate_present`, `decision_scope_derived`, `binding_digest_matches` | `decision_record_saved`, `target_operation_not_auto_approved` |
| `run_maintenance` | `side_track_frame_present`, `allowed_scope_bound`, `branch_condition_resolved` | `maintenance_evidence_saved`, `return_condition_preserved` |
| `advance_reopen_after_commit_stop_point` | `commit_stop_point_committed`, `worktree_clean`, `reopen_state_bound` | `commit_stop_point_cleared`, `reopen_gate_selector_reenabled` |
| `commit_stop_point` | `staged_content_bound`, `commit_approval_valid`, `post_write_verification_clear` | `commit_created`, `approval_consumed`, `reopen_state_preserved` |
| `draft_reopen_plan_candidates` | `classification_basis_present`, `reopen_scope_bound` | `candidate_plan_saved`, `human_decision_required` |
| `apply_approved_reopen_plan` | `approved_plan_record_present`, `plan_digest_matches`, `human_only_approval_valid` | `reopen_in_progress_record_created`, `active_scope_initialized` |
| `advance_reopen_after_approval_stop_point` | `human_approval_record_valid`, `pending_gate_bound` | `approval_stop_point_cleared`, `next_reopen_step_selected` |
| `repair_canonical_documents` | `target_documents_bound`, `allowed_scope_bound`, `repair_basis_present` | `canonical_documents_updated`, `post_write_verification_required` |
| `run_reopen_drafting` | `active_reopen_scope_present`, `drafting_gate_selected` | `draft_artifact_updated`, `drafting_completed_gate_recorded` |
| `run_reopen_pending_gate` | `active_gate_resolved`, `gate_contract_bound`, `required_evidence_present` | `gate_evidence_saved`, `downstream_impact_recorded_if_needed` |
| `collect_required_decisions` | `open_decision_sources_present`, `decision_records_discoverable` | `required_decision_list_reported`, `no_state_mutation` |
| `finalize_reopen` | `pending_gates_empty`, `active_scope_covered`, `human_only_finalize_approval_valid` | `reopen_record_completed`, `active_scope_closed` |
| `draft_reopen_classification` | `upstream_change_evidence_present`, `affected_feature_scope_known` | `classification_basis_saved`, `reopen_start_decision_required` |
| `run_reopen_start` | `classification_approved`, `target_scope_bound`, `human_only_start_approval_valid` | `reopen_in_progress_record_created`, `spec_flags_updated` |
| `run_workflow_stage` | `stage_contract_bound`, `branch_condition_resolved`, `required_artifacts_available` | `stage_evidence_saved`, `completion_predicate_rechecked` |
| `completed` | `no_pending_required_action`, `workflow_state_consistent` | `completed_report_returned`, `no_state_mutation` |

`run_maintenance`、`run_reopen_pending_gate`、`run_workflow_stage` は branchy operation であり、代表値だけで実行可否を判断してはならない。これらの contract は `effect_kind` に最大副作用、`max_effect_kind` に同じ値またはより強い値を持ち、`branching.branches[]` で各 branch の条件、内部 step、step ごとの `effect_kind`、承認要否、phase boundary を列挙する。

`branching.branches[]` の最低構造は、`branch_id`、`condition`、`internal_steps[]`、`max_effect_kind`、`approval_aggregation`、`human_only_override_applies`、`precondition_ids[]`、`postcondition_ids[]` を持つ。`internal_steps[]` の各要素は、最低限 `step_id`、`effect_kind`、`approval_required`、`approval_contract_ref`、`phase_boundary`、`source_ref` を持つ。`approval_contract_ref` は `none` または `stages/operation-contracts.yaml` 内の承認 contract ID とする。branch 表の「internal steps」は人向け略記であり、operation contract ではこの step 構造へ展開する。

`run_maintenance` の初期 branch は次とする。

| branch condition | internal steps | branch max_effect_kind | approval aggregation | approval contract refs | 補足 |
|---|---|---|---|---|---|
| `maintenance_kind=read_only_diagnostic` | 対象資料読取、diagnostic artifact 生成なし、結果表示 | `read` | `all_false` | `none` | 正本 artifact を作らない |
| `maintenance_kind=working_note_or_decision_basis` | working note / decision basis 作成、対象 digest 記録 | `write` | `any(child.approval_required)` | `none` | 正本変更ではなく判断根拠保存 |
| `maintenance_kind=canonical_document_repair` | 対象正本文書読取、利用者または proxy 判断の照合、正本文書更新、post-write verification | `write` | `any(child.approval_required)` | `none` | source-of-truth 文書修正は対象 contract を別途参照する |
| `maintenance_kind=workflow_state_repair` | state evidence 読取、repair plan 照合、workflow state 更新、整合検査 | `state_mutation` | `true` | `repair_workflow_state` | `repair_workflow_state` contract を参照する |
| `maintenance_kind=external_review_or_audit` | prompt 生成、外部 provider 実行、raw / parsed / metadata 保存 | `external_call` | `any(child.approval_required)` | `external_send_approval` | provider/model は合否条件ではなく実行証跡 |

`run_maintenance` の approval aggregation は `any(child.approval_required)` とする。ただし、子 step が `human_only` decision scope、commit / push / `spec.json` update、phase / gate completion、reopen finalize、approval_required irreversible operation execution を含む場合、proxy_model は承認主体になれない。

`run_maintenance` の branch 内 step 基線は次とする。

| branch condition | step_id | effect_kind | approval_required | approval_contract_ref | phase_boundary | source_ref |
|---|---|---|---:|---|---|---|
| `maintenance_kind=read_only_diagnostic` | `read_target_materials` | `read` | false | `none` | `none` | `design.md#req13-run-maintenance-step-read_target_materials` |
| `maintenance_kind=read_only_diagnostic` | `present_diagnostic_result` | `read` | false | `none` | `none` | `design.md#req13-run-maintenance-step-present_diagnostic_result` |
| `maintenance_kind=working_note_or_decision_basis` | `read_decision_basis_sources` | `read` | false | `none` | `none` | `design.md#req13-run-maintenance-step-read_decision_basis_sources` |
| `maintenance_kind=working_note_or_decision_basis` | `write_working_note` | `write` | false | `none` | `within_phase` | `design.md#req13-run-maintenance-step-write_working_note` |
| `maintenance_kind=canonical_document_repair` | `read_canonical_targets` | `read` | false | `none` | `none` | `design.md#req13-run-maintenance-step-read_canonical_targets` |
| `maintenance_kind=canonical_document_repair` | `apply_canonical_repair` | `write` | false | `none` | `within_phase` | `design.md#req13-run-maintenance-step-apply_canonical_repair` |
| `maintenance_kind=canonical_document_repair` | `require_post_write_verification` | `external_call` | false | `none` | `within_phase` | `design.md#req13-run-maintenance-step-require_post_write_verification` |
| `maintenance_kind=workflow_state_repair` | `read_state_evidence` | `read` | false | `none` | `none` | `design.md#req13-run-maintenance-step-read_state_evidence` |
| `maintenance_kind=workflow_state_repair` | `apply_state_repair` | `state_mutation` | true | `repair_workflow_state` | `within_phase` | `design.md#req13-run-maintenance-step-apply_state_repair` |
| `maintenance_kind=workflow_state_repair` | `validate_state_consistency` | `read` | false | `none` | `none` | `design.md#req13-run-maintenance-step-validate_state_consistency` |
| `maintenance_kind=external_review_or_audit` | `build_external_prompt` | `write` | false | `none` | `within_phase` | `design.md#req13-run-maintenance-step-build_external_prompt` |
| `maintenance_kind=external_review_or_audit` | `execute_external_review` | `external_call` | true | `external_send_approval` | `external_boundary` | `design.md#req13-run-maintenance-step-execute_external_review` |
| `maintenance_kind=external_review_or_audit` | `save_review_artifacts` | `write` | false | `none` | `within_phase` | `design.md#req13-run-maintenance-step-save_review_artifacts` |

`run_workflow_stage` の初期 branch は次とする。

| branch condition | internal steps | branch max_effect_kind | approval aggregation | approval contract refs | 補足 |
|---|---|---|---|---|---|
| `phase=drafting` | source materials 読取、draft artifact 更新、target digest 記録 | `write` | `all_false` | `none` | phase 内の草案更新 |
| `stage=triad-review` | review prompt / target / manifest 作成、API/CLI review 実行、raw / parsed / triage artifact 保存 | `external_call` | `any(child.approval_required)` | `external_send_approval` | レビュー実行であり gate 完了ではない |
| `stage=review-wave` | cross-feature source 読取、wave summary / impact decision artifact 保存 | `external_call` | `any(child.approval_required)` | `external_send_approval` | reopen scope と impact scope を混同しない |
| `stage=alignment` | alignment prompt 実行、alignment artifact 保存 | `external_call` | `any(child.approval_required)` | `external_send_approval` | approval ではない |
| `stage=approval` | approval request 表示、人間判断待機、承認記録保存、phase / gate 遷移前検査 | `state_mutation` | `true` | `human_only_phase_gate_approval` | phase / gate completion は human-only |
| `phase_transition=true` | completed gate / next phase state 更新、snapshot 更新、post-transition validation | `state_mutation` | `true` | `human_only_phase_gate_approval` | `phase_boundary=phase_transition` |

`run_workflow_stage` の approval aggregation は、branch 内に human-only decision scope または approval_required operation が含まれる場合 true とし、外部 API review の実行承認と phase / gate 完了承認を別 contract として分離する。

`run_workflow_stage` の branch 内 step 基線は次とする。

| branch condition | step_id | effect_kind | approval_required | approval_contract_ref | phase_boundary | source_ref |
|---|---|---|---:|---|---|---|
| `phase=drafting` | `read_source_materials` | `read` | false | `none` | `none` | `design.md#req13-run-workflow-stage-step-read_source_materials` |
| `phase=drafting` | `write_draft_artifact` | `write` | false | `none` | `within_phase` | `design.md#req13-run-workflow-stage-step-write_draft_artifact` |
| `phase=drafting` | `record_target_digest` | `write` | false | `none` | `within_phase` | `design.md#req13-run-workflow-stage-step-record_target_digest` |
| `stage=triad-review` | `build_review_prompt_manifest` | `write` | false | `none` | `within_phase` | `design.md#req13-run-workflow-stage-step-build_review_prompt_manifest` |
| `stage=triad-review` | `execute_review_run` | `external_call` | true | `external_send_approval` | `external_boundary` | `design.md#req13-run-workflow-stage-step-execute_review_run` |
| `stage=triad-review` | `save_raw_parsed_triage` | `write` | false | `none` | `within_phase` | `design.md#req13-run-workflow-stage-step-save_raw_parsed_triage` |
| `stage=review-wave` | `read_cross_feature_sources` | `read` | false | `none` | `none` | `design.md#req13-run-workflow-stage-step-read_cross_feature_sources` |
| `stage=review-wave` | `execute_or_collect_wave_review` | `external_call` | true | `external_send_approval` | `external_boundary` | `design.md#req13-run-workflow-stage-step-execute_or_collect_wave_review` |
| `stage=review-wave` | `save_impact_decisions` | `write` | false | `none` | `within_phase` | `design.md#req13-run-workflow-stage-step-save_impact_decisions` |
| `stage=alignment` | `execute_alignment_check` | `external_call` | true | `external_send_approval` | `external_boundary` | `design.md#req13-run-workflow-stage-step-execute_alignment_check` |
| `stage=alignment` | `save_alignment_artifact` | `write` | false | `none` | `within_phase` | `design.md#req13-run-workflow-stage-step-save_alignment_artifact` |
| `stage=approval` | `present_approval_request` | `read` | false | `none` | `none` | `design.md#req13-run-workflow-stage-step-present_approval_request` |
| `stage=approval` | `record_human_approval_decision` | `state_mutation` | true | `human_only_phase_gate_approval` | `within_phase` | `design.md#req13-run-workflow-stage-step-record_human_approval_decision` |
| `stage=approval` | `validate_phase_gate_transition` | `read` | false | `none` | `none` | `design.md#req13-run-workflow-stage-step-validate_phase_gate_transition` |
| `phase_transition=true` | `update_completed_gate_state` | `state_mutation` | true | `human_only_phase_gate_approval` | `phase_transition` | `design.md#req13-run-workflow-stage-step-update_completed_gate_state` |
| `phase_transition=true` | `save_snapshot` | `write` | false | `none` | `within_phase` | `design.md#req13-run-workflow-stage-step-save_snapshot` |
| `phase_transition=true` | `validate_post_transition_state` | `read` | false | `none` | `none` | `design.md#req13-run-workflow-stage-step-validate_post_transition_state` |

単純操作で承認を必須とする action は次を基線とする。

- `commit_stop_point`
- `apply_approved_reopen_plan`
- `run_reopen_start`
- `advance_reopen_after_commit_stop_point`
- `advance_reopen_after_approval_stop_point`
- `finalize_reopen`
- `repair_workflow_state`

`run_reopen_pending_gate` は active gate で分岐する。

| active gate | effect_kind | approval_required | 補足 |
|---|---|---|---|
| `triad-review` | `external_call` | false | review-run と proxy decision の承認境界は別 contract で扱う |
| `review-wave` | `external_call` | false | 横断 impact check の証跡生成を含む |
| `alignment` | `write` | false | LLM が整合確認 artifact を生成する |
| `approval` | `state_mutation` | true | 承認要求を構造化し、人間判断待ちへ渡す。proxy_model は human-only approval を代行しない |

`run_reopen_drafting` は drafting 正本の更新であり、`run_reopen_pending_gate` とは分離する。`run_maintenance` と `run_workflow_stage` は複合操作として扱い、内部 operation または stage 種別により `effect_kind` と `approval_required` が変わる。代表値だけで確定せず、`branching.branches[]` に分岐条件、内部 step、各 step の `effect_kind`、最大副作用、承認要否の集約規則を持たせる。

### 4. 複合操作の schema 表現（Req 13 受入 8〜9）

複合 operation は `effect_kind` を単一 enum のまま保持し、`max_effect_kind` に最大副作用を置く。複数副作用の詳細は `sequence.internal_steps[]` と `branching.branches[]` に展開する。これにより、既存の単一値 schema を保ちながら、`run_maintenance` や `run_workflow_stage` の内部差異を LLM の推測に戻さない。

`record_human_decision` は承認対象 operation ではなく、判断記録 operation とする。`effect_kind=state_mutation`、`approval_required=false`、`phase_boundary=within_phase` とし、記録対象は `target_operation_id`、`target_required_action`、`target_artifact_digest` または `staged_file_set_digest` で束縛する。`record_human_decision` の完了だけでは、対象 operation の `approval_required=true` を満たさない。承認として対象 operation を進められるかどうかは、Requirement 14 §1 の approval gate record にある `decision_scope`、`binding_kind`、digest 束縛、および対象 operation contract から導出した human-only / proxy-allowed 判定で決まる。

### 5. registry / preflight の read-only 境界（Req 13 受入 11〜12）

operation preflight は `stages/operation-registry.yaml` を入口にし、参照先 `stages/operation-contracts.yaml` の preconditions / postconditions / side effects / approval_required を読み取る。preflight の責務は「開始前に確認すること」であり、contract 正本、workflow state、approval record、side track stack、snapshot、review-run artifact を作成・更新しない。

read-only diagnostic 表示では、contract 参照欠落、digest drift、schema_version mismatch、確認不能 precondition、正本 field 重複、未接続 `required_action` mapping を `WARN` 以上にしてよい。ただし、その状態を operation が安全に束縛済みまたは実行可能である根拠にしてはならない。runner-enabled operation では同じ状態を `DEVIATION` とし、operation 実行を開始しない。

## Requirement 14 設計モデル：承認ゲート、側道スタック、状態スナップショット（Req 14）

Requirement 14 は、判断記録、側道作業、現在状態の可視化を、会話文脈ではなく機械可読状態として扱う。

### 1. 承認ゲート record（Req 14 受入 1〜3）

承認ゲートは `wait_for_human_decision` と `record_human_decision` のペアとして扱う。判断 record の最低構造は次とする。

```yaml
schema_version: string
decision_id: string
decision: approved | rejected | deferred | changes_requested
decision_scope: human_only | proxy_allowed | advisory_only
target_operation_id: string
target_required_action: string
target_artifact: string | null
target_artifact_digest: string | null  # binding_kind=artifact_digest / both では必須
staged_file_set_digest: string | null  # binding_kind=staged_file_set_digest / both では必須
binding_kind: artifact_digest | staged_file_set_digest | both | none
decided_by: user | proxy_model
decided_at: string
source_ref: string
source_digest: string
rationale: string
next_action_expectation: proceed | stay_blocked | redraft | repair
consumed: boolean
```

`approved` 以外の判断は対象不可逆操作へ進めない。`rejected` は停止維持、`deferred` は待機、`changes_requested` は再起草または repair へ分岐する。分岐を選ぶ責務は `next --json` に置き、LLM が会話上の雰囲気で選ばない。

human-only decision と proxy-allowed decision は approval gate record の `decision_scope` で区別する。`decision_scope` は最低限 `human_only`、`proxy_allowed`、`advisory_only` の 3 値とする。`decision_scope` は record 作成者が任意に選ぶ値ではなく、`target_required_action` から解決した operation contract の `approval_required`、`phase_boundary`、`effect_kind`、`actor.kind`、および human-only override set から機械的に導出する。record 内の `decision_scope` が contract から導出した値と一致しない場合は形式不正として fail-closed にする。

`binding_kind` も operation contract から導出する。正本文書・review artifact・approval artifact・proxy decision artifact を対象にする operation は `target_artifact_digest` を必須にする。commit / staged content / apply-fixes / state mutation のうち git index に束縛される operation は `staged_file_set_digest` を必須にする。両方を参照する operation は `binding_kind=both` とし、両 digest を必須にする。`binding_kind=none` は `wait_for_human_decision`、`collect_required_decisions`、`completed` のような read-only / wait-only operation に限る。`approval_required=true`、human-only override set、phase / gate completion、commit、push、`spec.json` 更新、reopen finalize の対象 record では `binding_kind=none` を禁止する。必要な digest が欠落、null、または現在の対象 digest と不一致の場合、`record_human_decision` は成功せず、`next --json` は対象 operation へ進めない。

binding 条件は次のとおりとする。record schema はこの表を条件付き必須として実装し、両 digest を独立 optional として扱ってはならない。

| binding_kind | 必須 digest | null を許す digest | 対象 operation |
|---|---|---|---|
| `artifact_digest` | `target_artifact_digest` | `staged_file_set_digest` | 正本文書、review artifact、approval artifact、proxy decision artifact を対象にする判断 |
| `staged_file_set_digest` | `staged_file_set_digest` | `target_artifact_digest` | commit / push / staged content / git index に束縛される判断 |
| `both` | `target_artifact_digest` と `staged_file_set_digest` | なし | artifact と staged 内容の両方を対象にする判断 |
| `none` | なし | `target_artifact_digest`、`staged_file_set_digest` | read-only / wait-only operation のみ。承認済み不可逆操作には使えない |

`decided_by`、`decided_at`、`source_ref`、`source_digest` は常に必須である。`source_digest` は判断根拠として提示・保存した source text または source artifact の SHA-256 hex とし、source が保存不能な場合でも omission reason を持つ source evidence artifact の digest を記録する。actor、timestamp、source、target operation、required_action、binding digest のいずれかが欠落する record は、承認 record ではなく形式不正として扱う。

`decided_by=proxy_model` かつ `decision_scope=human_only` の record は承認として扱わず、`next --json` は対象不可逆操作へ進めない。`decided_by=proxy_model` かつ `decision_scope=proxy_allowed` の record は、finding triage や修正方針判断の証跡としてのみ使える。`decision_scope=advisory_only` は補助的判断であり、対象 operation の `approval_required=true` を満たさない。

human-only decision の初期集合は次とする。

- commit
- push
- `spec.json` 更新
- phase approval
- reopen finalize
- `approval_required=true` の不可逆 operation 実行許可

human-only override set は operation contract より強い。ある operation が `approval_required=false` と書かれていても、commit、push、`spec.json` 更新、phase / gate completion、reopen finalize、または approval-required irreversible operation execution に該当する branch では `decision_scope=human_only` とする。

proxy_model は finding triage、同根 cluster の採否案、補助的な整合判断を代行できる。ただし proxy_model decision は human-only decision の承認主体を置換しない。

### 2. side track stack（Req 14 受入 4〜7）

side track は stack frame として `stages/in-progress/side-track-stack.yaml` または後継 runtime state に保持する。初期実装では既存の `process_id: maintenance` 進行中ファイルを互換入力として扱い、Phase 3 以降で stack schema へ寄せる。

frame の最低構造は次とする。

```yaml
frame_id: string
kind: maintenance | follow_up | blocker_repair | dependent_issue
parent_frame_id: string | null
pushed_by: user | llm | tool
title: string
spawned_from:
  required_action: string
  active_gate: string | null
  state_file: string | null
allowed_scope: string
allowed_files: [string]
completion_conditions: [string]
return_to:
  required_action: string
  active_gate: string | null
  state_refs: [string]
staged_file_set: [string]
staged_file_digest: string
pushed_at: string
max_depth: integer
```

push 時、pop 直前、commit / push 直前に `staged_file_set` と `staged_file_digest` を採取して照合する。top frame 以外の pop、`allowed_files` 外の staged 変更、親子 frame の未許可 overlap、push 時点からの予期しない digest 変化、pop 時の digest / set 不一致は、Phase 3 では `WARN` 以上、Phase 5 では `DEVIATION` または `repair_workflow_state` とする。`max_depth` は既定 2 で、Phase 3 は警告、Phase 5 はブロックする。

side track stack の read-only 操作は `current` / `inspect` とし、stack state を書き換えない。mutating 操作は `push` / `pop` / `repair` とし、operation contract の preconditions / postconditions を通す。`push` は新 frame を top に追加し、`pop` は top frame だけを閉じる。pop 後に `return_to` が解決できない、または staged file set が本線復帰条件を満たさない場合、`next --json` は通常作業に戻さず `repair_workflow_state` または同等の停止状態を返す。

### 3. workflow-state snapshot（Req 14 受入 8〜10）

`.reviewcompass/runtime/workflow-state-snapshot.yaml` は `next --json` の副産物であり、正本ではない。正本は常に `next --json` と state refs である。snapshot が古い、手動更新された、または直近 `next --json` と照合できない場合は信頼しない。

snapshot の最低構造は次とする。

```yaml
schema_version: string
generated_by: tools/check-workflow-action.py
generated_at: string
source_next_action_sha256: string
current_work:
  required_action: string
  title: string
  outer_node: string | null
  inner_node: string | null
  active_gate: string | null
active_side_tracks: [object]
git_tree_summary:
  clean: boolean
  staged_files: [string]
  unstaged_files: [string]
post_write_manifest_summary: object
workflow_state_summary: object
```

`current_work.outer_node` は reopen / maintenance / workflow / post-write などの外側の状態、`inner_node` は phase / stage / gate などの内側の単位を表す。UI や人向け報告は snapshot を読んでよいが、操作可否は `next --json` と operation preflight で再確認する。

### 4. read-only / mutating 操作の保存先（Req 14 受入 11〜12）

approval gate record、side track stack、workflow-state snapshot は次の保存先を基線とする。

| 対象 | 保存先 | 正本性 | read-only 操作 | mutating 操作 |
|---|---|---|---|---|
| approval gate record | `.reviewcompass/runtime/approvals/` 配下または後継 approval state | 承認判断の正本 | inspect | record / consume / invalidate |
| side track stack | `stages/in-progress/side-track-stack.yaml` または後継 runtime state | side track 状態の正本 | current / inspect | push / pop / repair |
| workflow-state snapshot | `.reviewcompass/runtime/workflow-state-snapshot.yaml` | 可視化・監査補助、正本ではない | snapshot / inspect | save snapshot のみ。操作許可は変更しない |

read-only 操作と mutating 操作を同じ operation として扱ってはならない。mutating 操作は Requirement 13 の operation contract に接続し、approval_required、preconditions、postconditions、side effects を明示する。

## Requirement 15 設計モデル：構造化有効プロンプトと監査（Req 15）

Requirement 15 は、有効プロンプトを「LLM が行う言語タスクの仕様」として構造化する。機械タスクは operation contract、preflight、runner、guard が担う。

### 1. structured effective prompt schema（Req 15 受入 1〜4）

既存の `.reviewcompass/runtime/effective-prompts/*.prompt.md` は互換出力として維持する。Phase 4 では、同じ判定点から構造化 YAML または JSON を生成し、Markdown prompt はその人向けレンダリングとして扱う。

```yaml
schema_version: string
decision_point:
  kind: string
  required_action: string
  phase: string | null
  stage: string | null
  active_gate: string | null
prompt_length:
  min_chars: integer
  max_chars: integer
  source_ref: string
  failure_verdict: WARN | DEVIATION
preconditions_checked:
  - id: string
    source: next_json | operation_preflight | schema_validation | manifest_validation
    machine_checked: true
    evidence_ref: string
language_task:
  document_kind: design | requirements | tasks | review | alignment | approval | report
  input:
    required_files: [string]
    state_refs: [string]
    source_refs: [string]
  output_format:
    kind: markdown | yaml | json
    required_sections: [string]
    schema_ref: string | null
  constraints: [string]
postconditions:
  - id: string
    check_kind: section_exists | schema_valid | target_set_matches | next_action_compatible | manual_review_required
    source_ref: string
on_completion:
  next_required_action: string | null
  allowed_followups: [string]
  forbidden_actions: [string]
```

`preconditions_checked` は機械が確認済みの条件だけを参照する。LLM がこれから確認する事項をここに置いてはならない。`language_task` は生成または判断する文章の範囲を表し、commit、push、spec.json 更新、review-run 実行などの機械操作手順を埋め込まない。

`prompt_length` は、判定点ごとの長さ上下限を構造化 prompt に写した監査用フィールドである。正本は `docs/operations/WORKFLOW_DISCIPLINE_MAP.yaml#decision_points` の各判定点に置く `prompt_length_bounds` とし、個別判定点に未設定の場合は同ファイルの `default_prompt_length_bounds` を使う。上下限は `min_chars`、`max_chars`、`failure_verdict` を持ち、`min_chars` と `max_chars` は正の整数かつ `min_chars < max_chars` でなければならない。`failure_verdict` は範囲外 prompt の第1層機械検査 verdict であり、未設定値を runner が推測してはならない。

長さ基準の設定主体は workflow-management の設計・規律マップ更新手続きであり、task 個別の review-run や prompt generator が場当たり的に決めてはならない。上下限の変更は Requirement 13〜15 の責務境界を変えるため、通常の design / tasks / implementation 連鎖で扱う。

### 2. 第1層機械検査（Req 15 受入 5）

有効プロンプト検査は次を確認する。

- 参照先ファイルとアンカーが存在する
- `decision_point`、`preconditions_checked`、`language_task`、`postconditions`、`on_completion` が存在する
- `prompt_length` が `WORKFLOW_DISCIPLINE_MAP.yaml` の `prompt_length_bounds` または `default_prompt_length_bounds` と一致し、長さがその上下限内にある。範囲外の場合は当該 bounds の `failure_verdict` を返す
- DISCIPLINE_MAP または後継 registry に未登録の action kind を使っていない
- review target manifest と review-run target が一致する
- `language_task.output_format` と `postconditions` が対応している
- `preconditions_checked` が機械確認済み条件だけを参照している
- `on_completion` が operation contract の postconditions と次 action に矛盾しない

staged file set とのコミット混線、side track depth、operation preflight の pending conflict は Requirement 12・14 の責務であり、有効プロンプト検査はその結果を参照するだけにする。

### 3. LLM judge audit（Req 15 受入 6〜7）

Phase 6 では、構造化有効プロンプト、該当する `WORKFLOW_NAVIGATION.md` 節、operation contract を入力として LLM judge audit を実行できるようにする。出力は schema 適合 JSON または同等の構造化形式とし、最低限 `gap_id`、`severity`、`prompt_ref`、`contract_ref`、`finding`、`recommended_action`、`blocks_approval` を持つ。

LLM judge audit は意味的な不足を見つける補助であり、最終承認を自動化しない。既知 gap fixture には、必須構造節欠落、機械タスクの prompt 内残留、preconditions の網羅不足、postconditions の確認不能性を含める。

## Requirement 16 設計モデル：段階的実装計画 Phase 0〜6（Req 16）

Requirement 16 は、選択層と実行層の機械化を一度に混ぜず、既存挙動を壊さない順序で実装するための計画である。

### 1. Phase anchor と順序（Req 16 受入 1〜10）

| Phase | 主対象 | 完了条件 |
|---|---|---|
| Phase 0 | D-003 選択層 | 19段階優先順位、`required_action` 唯一化、invariant 検査、mechanical workflow-state repair detection、reopen plan compiler / `reopen-recompile` 相当が TDD で通る |
| Phase 1 | 語彙・schema | `.reviewcompass/schema/` の required_action / next_action / operation contract / effect_kind / phase_boundary / snapshot / language task schema が meta-schema 検証を通る |
| Phase 2 | read-only registry | `check-workflow-action.py operation-list --json` または同等が operation contract を読み取り専用で返す |
| Phase 3 | advisory preflight | `operation-preflight <id> --json` または同等が pending conflict、side track depth、commit mixing、prompt 機械検査を `WARN` 以上で返す |
| Phase 4 | structured effective prompt | 全判定点で構造化 prompt と既存 Markdown prompt を生成し、互換 path を維持する |
| Phase 5 | mechanical blocking | Phase 3 の警告対象のうち serial_only 違反、承認欠落、side track depth 超過、commit mixing を `DEVIATION` で止める |
| Phase 6 | LLM judge audit | 構造化 prompt と運用文書を入力に gap を構造化出力する。承認自動化はしない |

Phase 0 の安定 anchor は `docs/notes/working/2026-06-16-next-json-unique-state-redesign.md` の D-003 とする。ただし Phase 0 完了条件は working note の節番号に依存させず、本設計の次の 6 失敗テストを tasks / implementation の受入単位へ写す。

1. `commit_stop_point=true` の reopen state では、`pending_gates` が残っていても `required_action=commit_stop_point`、`active_gate=null`、`phase=null`、`stage=null` を返す。
2. `current_blocker` がある reopen state では、`pending_gates` が残っていても `required_action=wait_for_human_decision`、`active_gate=null` を返す。
3. 正本変更済み phase が `canonical_update_phases` にあるのに `future_gates` / `pending_gates` が full gate を含まない場合、`verdict=DEVIATION`、`required_action=repair_workflow_state` を返す。
4. 第3過程で active gate がある場合だけ、`phase` / `stage` が非 null になる。
5. commit stop point commit 後、worktree clean で HEAD が当該 stop point を含む場合、`required_action=advance_reopen_after_commit_stop_point` を返し、同じ commit stop point を再提示しない。
6. `required_action` ごとの JSON 相互排他 schema を fixture で検証する。

mechanical workflow-state repair detection は Phase 0 の完了条件である。`next --json` は、reopen state の `active_reopen_scope` / `active_impact_review_scope`、`pending_gates`、`completed_gates`、`drafting_completed_gates`、`downstream_impact_decisions`、commit stop point、`current_blocker`、`spec.json` workflow_state の間に矛盾を検出した場合、通常 action へ進まず `required_action=repair_workflow_state` と `verdict=DEVIATION` を返す。Phase 0 は、この repair detection が少なくとも上記 6 失敗テストの 3 番と active scope 欠落・矛盾ケースで TDD 検証されるまで完了扱いにしない。

Phase 1 のうち `required_action.schema.json` と `next_action_response.schema.json` は Phase 0 開始をブロックする最小前提として先行済みである。他の operation contract 系 schema は Phase 0 と並行可能だが、Phase 2 へ進む前にはそろえる。

各 Phase の終了時は、`next --json` が通常作業へ戻れる状態、または明示された停止状態を返すことを確認する。Phase をまたいだ途中状態を単一 commit に混在させない。

### 2. reopen scope と impact review scope（Req 16 受入 11〜12）

本改訂の active reopen scope は `workflow-management` の requirements から design / tasks / implementation への連鎖再実施である。active scope の正本は `stages/in-progress/reopen-procedure-*.yaml` の `active_reopen_scope` と `active_impact_review_scope` である。`spec.json.reopened` は過去に上流を reopen した履歴フラグとして保持され得るため、現在の active reopen scope と同一視しない。

`active_reopen_scope` は正本を再オープンして workflow_state flag を false に戻した feature / phase / gate 範囲を持つ。`active_impact_review_scope` は、正本変更の有無を確認する consumer / derivative feature / phase / gate 範囲を持つが、当該 feature の workflow_state flag を自動で false に戻す根拠ではない。`next --json` は reopen 中にこの in-progress record を必ず読み、scope が欠落・不整合・stale の場合は `repair_workflow_state` を返す。

初期化は reopen 第1過程で行う。trigger_map と分類根拠から両 scope を生成し、利用者承認後に in-progress record へ固定する。更新は gate 完了記録と downstream impact decision の追加に限定し、scope の拡張・縮小は新しい利用者判断または `repair_workflow_state` を必要とする。終了は reopen 第4過程で行い、全 pending gate が解消し、active scope 全件が completed gate または downstream impact decision で覆われた場合だけ in-progress record を `stages/completed/` へ移す。

operation contract、構造化有効プロンプト、状態スナップショット、proxy_model triage decision の機械処理化は、他 feature が consumer / derivative として参照し得る。正本 reopen 対象を `workflow-management` に限定する場合でも、review-wave では foundation、runtime、evaluation、analysis、self-improvement、conformance-evaluation への正本変更要否と consumer 契約影響を確認し、reopen scope と impact review scope を混同せず記録する。

### 3. proxy_model triage decision の機械処理化

proxy_model triage decision は、review-run 後の重要件判断を一括化しても、finding ごとの traceability と承認 scope を失わないための operation family として扱う。対象 operation は次を初期集合とする。

- `proxy_triage_prepare_input`：raw response、parsed finding、同根 cluster、候補案を読み、proxy_model 入力 bundle を作る。
- `proxy_triage_record_cluster_decision`：cluster 単位の proxy raw response と decision を保存する。
- `proxy_triage_expand_findings`：cluster-level decision を finding-level decision へ展開する。
- `proxy_triage_validate_coverage`：triage 対象 finding ID が decision file で過不足なく覆われているか検査する。
- `proxy_triage_apply_batch`：coverage validation が通った finding-level decision だけを `triage.yaml` へ batch 適用する。

proxy_model triage decision の適用前には、human-required predicate を必ず評価する。predicate は provider / model 名を見ず、次の証跡だけを読む。

1. proxy 適用対象 finding / cluster coverage と raw / parsed / prompt 証跡
2. approval gate record の `decision_scope`、`decision`、`decided_by`、`target_operation_id`、`target_required_action`、`binding_kind`、digest 束縛
3. operation contract の `approval_required`、`phase_boundary`、`effect_kind`、`actor.kind`、human-only override set
4. review-wave impact evidence の未解決状態
5. downstream impact decisions と active reopen scope / impact review scope の整合

triage item の `decision_status`、`final_label`、`decision_actor_type` は適用対象の状態確認と二重適用防止には使ってよいが、human-required predicate の正本にはしない。human-required predicate の正本は approval gate record と operation contract、および review-wave / downstream impact evidence である。

human-required predicate は `proxy_triage_evaluate_human_required` という read-only internal check として扱う。入力は、対象 finding / cluster IDs、finding-to-operation mapping、関連 approval gate record、対象 operation contract、review-wave impact evidence、active reopen scope / impact review scope とする。出力は最低限、`verdict`、`blocks_proxy_apply`、`blocking_reasons[]`、`checked_records[]`、`checked_contracts[]`、`source_refs[]` を持つ。`blocks_proxy_apply=true` の場合、後続の `proxy_triage_apply_batch` は `DEVIATION` とし、`triage.yaml` を更新しない。

`未解決 approval gate` は、対象 finding / cluster または対象 operation に紐づく approval gate record のうち、`decision` が `approved` ではない、`consumed=false` のまま対象 operation に未反映、`decision_scope=human_only`、binding digest 不一致、または `next_action_expectation` が `proceed` 以外のものを指す。record が欠落していて、対象 operation contract が `approval_required=true`、human-only override set、phase / gate completion、commit、push、`spec.json` 更新、reopen finalize、または approval-required irreversible operation execution に該当する場合も、未解決 approval gate と同等に扱う。

`approval_required=true の対象 operation` は、finding-to-operation mapping から得た `target_operation_id` / `target_required_action` を `stages/operation-contracts.yaml` の operation contract に解決し、その contract の `approval_required=true`、または branch 内部 step の approval aggregation が true になるものを指す。mapping が欠落、複数候補で一意に解決不能、contract 参照欠落、contract digest / schema_version drift の場合は、proxy が安全に適用可能とは扱わず `blocks_proxy_apply=true` とする。

predicate の評価順序は次の固定順とする。

1. coverage と証跡存在を検査し、対象 finding / cluster、raw、parsed、prompt、proxy raw、decision file、mapping が過不足なくそろわない場合は `DEVIATION`。
2. finding-to-operation mapping から対象 operation contract を解決し、一意に解決できない場合は `DEVIATION`。
3. 対象 operation contract と human-only override set から `approval_required`、`phase_boundary`、`effect_kind`、`actor.kind`、approval aggregation を評価する。
4. 関連 approval gate record の `decision_scope`、`decision`、`decided_by`、`binding_kind`、digest、`consumed`、`next_action_expectation` を検査する。
5. review-wave impact evidence、downstream impact decisions、active reopen scope / impact review scope の未解決・矛盾を検査する。
6. 3〜5 のいずれかが human-required を示す場合は、triage item の `decision_status`、`final_label`、`decision_actor_type`、proxy decision の selected option に関係なく `blocks_proxy_apply=true` とする。

優先順位は次のとおりとする。

1. `decision_scope=human_only`、未解決 approval gate、`approval_required=true` の対象 operation、未解決 review-wave impact evidence は、proxy_model の判断より常に優先し、proxy apply を止める。
2. 必須証跡が欠落、競合、または対象 finding / cluster coverage を満たさない場合は `DEVIATION` とする。
3. triage 上の `leave-as-is`、`proxy_approved`、または proxy_model の selected decision は、1 の human-required 証跡を打ち消さない。
4. 1〜3 を通過し、かつ finding / cluster coverage が完全な場合だけ、proxy decision を finding-level decision へ展開できる。

`proxy_triage_apply_batch` の operation contract は、preconditions に次を持つ。

- `proxy_triage_validate_coverage` が成功している
- `proxy_triage_evaluate_human_required` が成功し、`blocks_proxy_apply=false` を返している
- すべての対象 finding に raw response、parsed finding、decision prompt、proxy raw response、cluster/finding mapping が存在する
- 対象 finding / cluster に紐づく approval gate record が存在する場合、その `decision_scope` は `proxy_allowed` または `advisory_only` であり、`human_only` ではない
- 対象 operation contract の `approval_required` が true、または human-only override set に該当する場合、proxy apply を停止する
- review-wave impact evidence、downstream impact decisions、active reopen scope / impact review scope に未解決または矛盾がない

これらの preconditions のいずれかが満たされない場合、`proxy_triage_apply_batch` は `DEVIATION` とし、triage.yaml を更新しない。

cluster-level decision は保存してよいが、実装修正や manifest 作成の承認単位は finding-level decision とする。`proxy_triage_expand_findings` は、cluster ID、含まれる finding IDs、採用案、棄却案理由、final label、source raw paths、decision prompt path、proxy raw path を finding ごとに複製し、各 finding decision に `cluster_decision_id` を保持する。

coverage validation は次を fail-closed にする。

- triage 対象 finding ID が decision file に存在しない
- decision file に triage 対象外 finding ID が混入している
- cluster decision の finding set と展開後 finding decisions が一致しない
- `final_label`、採用案、判断理由、source raw paths、decision prompt path、proxy raw path のいずれかが欠落している
- `review_triage_decide` approval と apply-fixes approval の scope が一致しない

approval scope は `approval_record.scope` で区別する。`review_triage_decide` は triage label の採否だけを許可し、仕様文書・実装・spec.json・workflow_state の変更は許可しない。apply-fixes は対象 finding IDs、対象ファイル、期待する変更種別を別 record として持つ。batch 適用は triage decision の一括反映に限り、修正実装を同時に行わない。



## .reviewcompass/specs/workflow-management/spec.json

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
      "alignment": true,
      "approval": true
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
      "triad-review": false,
      "review-wave": false,
      "alignment": false,
      "approval": false
    },
    "implementation": {
      "drafting": false,
      "triad-review": false,
      "review-wave": false,
      "alignment": false,
      "approval": false
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
      "tasks",
      "implementation"
    ]
  }
}


## stages/in-progress/reopen-procedure-2026-06-19.yaml

process_id: reopen-procedure
feature: workflow-management
classification: R-0
started_at: '2026-06-19T00:00:00+09:00'
trigger: Requirement 13〜16 の縦方向意図監査に基づく requirements/design/tasks 再生成
classification_basis: docs/reviews/reopen-classification-2026-06-19-wm-requirement-13-16-vertical-redo.md
completed_steps:
- R-0 判定確定・spec.json フラグ差し戻し完了（requirements/design/tasks/implementation 全段 → false、recheck.upstream_change_pending
  → true、impacted_downstream_phases → design/tasks/implementation）
- R-0 判定確定・spec.json フラグ差し戻し完了（requirements/design/tasks/implementation 全段 → false）
- Requirement 13〜16 を基点に requirements/design/tasks を縦方向意図監査の結果へ合わせて再生成
- requirements triad-review 完了（Requirement 13〜16 縦方向意図監査、API 版 gpt-5.5 proxy_model
  判定 C1〜C3 should-fix 適用、C4 leave-as-is）
- requirements review-wave 完了（Requirement 13〜16 縦方向やり直し、全 feature impact review、他
  feature 正本変更不要）
- requirements alignment 完了（Requirement 13〜16 と design/tasks 追跡、triad-review 修正反映、review-wave
  影響確認済み）
- requirements approval 完了（利用者承認済み）
- design drafting 完了（Requirement 13〜16 の設計反映確認済み、本文追加不要）
- design triad-review 完了（v2 triage 15 件 decided、post-fix coverage 15/15、統合 post-fix recheck 済み）
- design review-wave 完了（軽量横断確認、他 feature design 正本変更不要）
- design alignment 完了（Requirement 13〜16、design post-fix、review-wave、tasks T-016〜T-019 の追跡整合確認済み）
- design approval 完了（利用者承認済み）
- tasks drafting 完了（Requirement 13〜16 を T-016〜T-019 として tasks.md へ展開済み、design alignment で追跡整合確認済み）
next_step: 第3過程：tasks triad-review
step_number: 3
pending_gates:
- stages/tasks.yaml#triad-review
- stages/tasks.yaml#review-wave
- stages/tasks.yaml#alignment
- stages/tasks.yaml#approval
current_blocker: null
drafting_completed_gates:
- stages/requirements.yaml#drafting
- stages/design.yaml#drafting
- stages/tasks.yaml#drafting
active_reopen_scope:
  feature: workflow-management
  source_phase: requirements
  reopened_phases:
  - requirements
  - design
  - tasks
  - implementation
  current_phase: tasks
  start_gate: stages/requirements.yaml#drafting
  pending_gate_source: pending_gates
  completion_condition: pending_gates_empty_and_downstream_impact_decisions_cover_required_gates
  rationale: Requirement 13〜16 の縦方向意図監査に基づき、workflow-management の requirements
    から design / tasks / implementation へ連鎖再実施している active scope。
active_impact_review_scope:
  features:
  - foundation
  - runtime
  - evaluation
  - analysis
  - self-improvement
  - conformance-evaluation
  phases:
  - requirements
  - design
  - tasks
  - implementation
  decision_source: requirements review-wave と今後の downstream impact decisions
  flag_policy: impact_review_only_no_workflow_state_false
  rationale: workflow-management の operation contract / structured prompt / workflow state
    は他 feature が consumer / derivative として参照し得るため、正本変更要否を確認するが、
    active reopen scope とは分離する。
requirements_drafting_state_sync:
  synced_at: '2026-06-19T00:00:00+09:00'
  gate: stages/requirements.yaml#drafting
  rationale: reopen 中の通常 spec-set は in-progress と recheck により DEVIATION で遮断されるため、requirements
    drafting 完了を drafting_completed_gates と workflow-management spec.json の requirements.drafting=true
    に同期した。triad-review/review-wave/alignment/approval は false のまま維持する。
  evidence:
  - .reviewcompass/specs/workflow-management/requirements.md
  - .reviewcompass/specs/workflow-management/spec.json
design_drafting_state_sync:
  synced_at: '2026-06-20T00:00:00+09:00'
  gate: stages/design.yaml#drafting
  rationale: Requirement 13〜16 は design.md の Requirement 13〜16 設計モデル、追跡表、変更履歴に反映済みであり、requirements.md
    の目的・責務境界・受入条件・禁止事項が設計判断へ落ちていることを確認した。本文追加は不要のため、drafting 完了を
    drafting_completed_gates と workflow-management spec.json の design.drafting=true に同期した。triad-review/review-wave/alignment/approval
    は false のまま維持する。
  evidence:
  - .reviewcompass/specs/workflow-management/requirements.md
  - .reviewcompass/specs/workflow-management/design.md
  - .reviewcompass/specs/workflow-management/tasks.md
  - .reviewcompass/specs/workflow-management/spec.json
tasks_drafting_state_sync:
  synced_at: '2026-06-20T00:00:00+09:00'
  gate: stages/tasks.yaml#drafting
  rationale: Requirement 13〜16 は T-016〜T-019 として tasks.md に展開済みであり、design alignment
    でも requirements / design / tasks の追跡整合を確認した。tasks triad-review 以降は未完了のまま維持し、drafting
    完了のみを drafting_completed_gates と workflow-management spec.json の tasks.drafting=true に同期する。
  evidence:
  - .reviewcompass/specs/workflow-management/tasks.md
  - .reviewcompass/specs/_cross_feature/reviews/2026-06-20-design-vertical-redo-alignment.md
  - .reviewcompass/specs/workflow-management/spec.json
reopen_step_records:
- from_step: 1
  completed_step: R-0 判定確定・spec.json フラグ差し戻し完了（requirements/design/tasks/implementation
    全段 → false、recheck.upstream_change_pending → true、impacted_downstream_phases →
    design/tasks/implementation）
  rationale: 縦方向意図監査により、Requirement 13〜16 から requirements/design/tasks を再生成する必要があるため。分類根拠に従い、requirements
    を drafting から再開し、design/tasks/implementation を下流未完了へ戻す。
  evidence:
  - docs/reviews/reopen-classification-2026-06-19-wm-requirement-13-16-vertical-redo.md
  - .reviewcompass/specs/workflow-management/spec.json
- from_step: 1
  completed_step: R-0 判定確定・spec.json フラグ差し戻し完了（requirements/design/tasks/implementation
    全段 → false）
  rationale: 縦方向意図監査により Requirement 13〜16 を基点に requirements/design/tasks を再生成するため
  evidence:
  - docs/reviews/reopen-classification-2026-06-19-wm-requirement-13-16-vertical-redo.md
  - .reviewcompass/specs/workflow-management/spec.json
- from_step: 2
  completed_step: Requirement 13〜16 を基点に requirements/design/tasks を縦方向意図監査の結果へ合わせて再生成
  rationale: tasks 粒度起点 reopen の比較実験で、registry/contract 正本境界と proxy/human decision
    境界が requirements/design authority の問題として露出したため。Requirement 13〜16、design Req 13/14/16、T-016〜T-019
    を同じ縦方向意図で再生成した。
  evidence:
  - .reviewcompass/specs/workflow-management/requirements.md
  - .reviewcompass/specs/workflow-management/design.md
  - .reviewcompass/specs/workflow-management/tasks.md
  - docs/reviews/reopen-classification-2026-06-19-wm-requirement-13-16-vertical-redo.md
  - docs/notes/working/2026-06-19-vertical-intent-review-audit-experiment.md
commit_stop_point_records:
- step: 2
  kind: canonical_update_complete
  gate: null
  reason: 第2過程の正本修正完了
  head: 24062d238cc407551f13d3edcacff940dcce6b56
  evidence:
  - 24062d238cc407551f13d3edcacff940dcce6b56
- step: 3
  kind: triad_review_complete
  gate: stages/requirements.yaml#triad-review
  reason: requirements triad-review 完了時点の停止点
  head: b46952cb96d1a0f99e90da5f6cd02d433959add5
  evidence:
  - b46952cb96d1a0f99e90da5f6cd02d433959add5
- step: 3
  kind: review_wave_complete
  gate: stages/requirements.yaml#review-wave
  reason: requirements review-wave 完了時点の停止点
  head: dd19b13c23aa34377fdedfc36100b0f3c17dc357
  evidence:
  - dd19b13c23aa34377fdedfc36100b0f3c17dc357
- step: 3
  kind: alignment_complete
  gate: stages/requirements.yaml#alignment
  reason: requirements alignment 完了時点の停止点
  head: 1e9de71e78e1f8dc3fa3b066a4b94f25ea0543ce
  evidence:
  - 1e9de71e78e1f8dc3fa3b066a4b94f25ea0543ce
- step: 3
  kind: approval_complete
  gate: stages/requirements.yaml#approval
  reason: requirements approval 完了時点の停止点
  head: c09a6f9de1144a46fae98aea4a59b92384308c2b
  evidence:
  - c09a6f9de1144a46fae98aea4a59b92384308c2b
completed_gates:
- stages/requirements.yaml#triad-review
- stages/requirements.yaml#review-wave
- stages/requirements.yaml#alignment
- stages/requirements.yaml#approval
- stages/design.yaml#triad-review
- stages/design.yaml#review-wave
- stages/design.yaml#alignment
- stages/design.yaml#approval
downstream_impact_decisions:
- gate: stages/requirements.yaml#triad-review
  feature_scope: workflow-management
  decision: proxy_model_approved_after_should_fix
  rationale: requirements triad-review で Requirement 13〜16 の縦方向意図伝達を監査し、API 版 gpt-5.5
    proxy_model が C1〜C3 should-fix、C4 leave-as-is と判定した。C1〜C3 は requirements.md に反映済みで、関連テスト
    42 件が通過したため、requirements triad-review gate を完了する。
  evidence:
  - .reviewcompass/specs/workflow-management/reviews/2026-06-19-workflow-management-requirements-vertical-redo-review-run-v2/review_summary.md
  - .reviewcompass/specs/workflow-management/reviews/2026-06-19-workflow-management-requirements-vertical-redo-review-run-v2/triage.yaml
  - .reviewcompass/specs/workflow-management/reviews/2026-06-19-workflow-management-requirements-vertical-redo-review-run-v2/proxy-decision-decisions.yaml
  - .reviewcompass/specs/workflow-management/reviews/2026-06-19-workflow-management-requirements-vertical-redo-review-run-v2/proxy-approval.yaml
  - .reviewcompass/specs/workflow-management/reviews/2026-06-19-workflow-management-requirements-vertical-redo-review-run-v2/raw-review-triage-summary.md
- gate: stages/requirements.yaml#review-wave
  feature_scope: all_features
  decision: existing_sufficient
  rationale: Requirement 13〜16 縦方向やり直しの requirements review-wave として全 feature への正本変更要否を確認した。未消化
    carry-forward は 0 件で、workflow-management 以外は consumer / derivative として現行正本で受けられるため、他
    feature の requirements 正本変更は不要。
  evidence:
  - .reviewcompass/specs/_cross_feature/reviews/2026-06-20-requirements-vertical-redo-review-wave.md
  - .reviewcompass/specs/_cross_feature/reviews/2026-06-20-requirements-vertical-redo-review-wave-summary.md
  - .reviewcompass/specs/workflow-management/requirements.md
- gate: stages/requirements.yaml#alignment
  feature_scope: workflow-management
  decision: approved
  rationale: Requirement 13〜16 は requirements.md に受入基準として定義され、design.md の Requirement
    13〜16 設計モデルおよび tasks.md の T-016〜T-019 に追跡可能である。requirements triad-review の C1〜C3
    は反映済み、review-wave では他 feature 正本変更不要と確認済みのため、requirements alignment を完了とする。
  evidence:
  - .reviewcompass/specs/workflow-management/requirements.md
  - .reviewcompass/specs/workflow-management/design.md
  - .reviewcompass/specs/workflow-management/tasks.md
  - .reviewcompass/specs/workflow-management/reviews/2026-06-19-workflow-management-requirements-vertical-redo-review-run-v2/proxy-decision-decisions.yaml
  - .reviewcompass/specs/_cross_feature/reviews/2026-06-20-requirements-vertical-redo-review-wave-summary.md
- gate: stages/requirements.yaml#approval
  feature_scope: workflow-management
  decision: approved
  rationale: 利用者が requirements approval を明示承認した。Requirement 13〜16 の requirements 再生成、triad-review
    修正反映、review-wave 影響確認、alignment 完了を踏まえ、requirements phase を承認済みとする。
  evidence:
  - .reviewcompass/specs/workflow-management/requirements.md
  - .reviewcompass/specs/workflow-management/reviews/2026-06-19-workflow-management-requirements-vertical-redo-review-run-v2/proxy-decision-decisions.yaml
  - .reviewcompass/specs/_cross_feature/reviews/2026-06-20-requirements-vertical-redo-review-wave-summary.md
  - 1e9de71e78e1f8dc3fa3b066a4b94f25ea0543ce
- gate: stages/design.yaml#triad-review
  feature_scope: workflow-management
  decision: user_approved_after_post_fix
  rationale: design triad-review v2 の 15 件は利用者承認により triage finalization 済みで、13 件 must-fix、2 件 should-fix として decided
    になった。全 15 件に post-fix recheck coverage があり、統合 post-fix review で見つかった Req 13 の追加不整合も修正・再点検済みのため、design triad-review gate を完了とする。
  evidence:
  - .reviewcompass/specs/workflow-management/reviews/2026-06-20-workflow-management-design-vertical-redo-review-run-v2/triage.yaml
  - .reviewcompass/specs/workflow-management/reviews/2026-06-20-workflow-management-design-vertical-redo-review-run-v2/post-fix-coverage-inventory.md
  - .reviewcompass/specs/workflow-management/reviews/2026-06-20-workflow-management-design-vertical-redo-review-run-v2/integrated-post-fix-review.md
  - .reviewcompass/specs/workflow-management/reviews/2026-06-20-workflow-management-design-vertical-redo-review-run-v2/integrated-post-fix-recheck.md
  - .reviewcompass/specs/workflow-management/reviews/2026-06-20-workflow-management-design-vertical-redo-review-run-v2/post-fix-target-manifest.yaml
- gate: stages/design.yaml#review-wave
  feature_scope: all_features
  decision: existing_sufficient
  rationale: Requirement 13〜16 縦方向やり直しの design review-wave として軽量横断確認を実施した。未消化 carry-forward は 0 件で、workflow-management
    以外は consumer / derivative として現行正本で受けられるため、他 feature の design 正本変更は不要。
  evidence:
  - .reviewcompass/specs/_cross_feature/reviews/2026-06-20-design-vertical-redo-review-wave.md
  - .reviewcompass/specs/_cross_feature/reviews/2026-06-20-design-vertical-redo-review-wave-summary.md
  - .reviewcompass/specs/workflow-management/design.md
- gate: stages/design.yaml#alignment
  feature_scope: workflow-management
  decision: existing_sufficient
  rationale: Requirement 13〜16 は requirements.md、design.md、tasks.md の T-016〜T-019 へ追跡可能である。design triad-review
    v2 post-fix と軽量 review-wave の結果も整合しており、他 feature 正本変更不要、tasks / implementation への連鎖再実施は pending gates
    で維持されているため、design alignment を完了とする。
  evidence:
  - .reviewcompass/specs/_cross_feature/reviews/2026-06-20-design-vertical-redo-alignment.md
  - .reviewcompass/specs/workflow-management/requirements.md
  - .reviewcompass/specs/workflow-management/design.md
  - .reviewcompass/specs/workflow-management/tasks.md
  - .reviewcompass/specs/workflow-management/reviews/2026-06-20-workflow-management-design-vertical-redo-review-run-v2/post-fix-target-manifest.yaml
- gate: stages/design.yaml#approval
  feature_scope: workflow-management
  decision: approved
  rationale: 利用者が design approval を明示承認した。Requirement 13〜16 の design 展開、triad-review v2 post-fix、軽量 review-wave、
    alignment 完了を踏まえ、design phase を承認済みとする。
  evidence:
  - .reviewcompass/specs/_cross_feature/reviews/2026-06-20-design-vertical-redo-approval.md
  - .reviewcompass/specs/workflow-management/design.md
  - .reviewcompass/specs/_cross_feature/reviews/2026-06-20-design-vertical-redo-alignment.md
  - .reviewcompass/specs/_cross_feature/reviews/2026-06-20-design-vertical-redo-review-wave.md
  - .reviewcompass/specs/workflow-management/reviews/2026-06-20-workflow-management-design-vertical-redo-review-run-v2/post-fix-target-manifest.yaml
recheck_progress:
- consumed_phase: design
  consumed_at: '2026-06-20T00:00:00+09:00'
  reason: design drafting / triad-review / review-wave / alignment / approval が完了し、利用者が design approval を明示承認したため。
  remaining_impacted_downstream_phases:
  - tasks
  - implementation
  evidence:
  - .reviewcompass/specs/_cross_feature/reviews/2026-06-20-design-vertical-redo-approval.md
  - .reviewcompass/specs/workflow-management/spec.json

