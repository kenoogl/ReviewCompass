prompt_id: gemini_review
provider: gemini-api
model_id: gemini-3.5-flash

# Task
Review the target document for the requested phase and criteria.

# Phase
post_write_verification

# Criteria
# Post-write Review Target

criteria_id: requirements_triad_review_stop_full_post_write
phase: post_write_verification
generated_at: 2026-06-19T14:54:18.662128+00:00

## Change Summary

requirements triad-review 停止点のため、Requirement 13〜16 の proxy_model 判定反映、縦方向監査 prompt 規律、正式 proxy_model API 入口、レビュー証跡を追加した。

## Review Question

今回の requirements triad-review 停止点に含める要件本文、運用規律、review-run 証跡は、Requirement 13〜16 の縦方向意図監査と proxy_model 判定の結果を一貫して記録し、次の requirements review-wave へ進む前の停止点証跡として重大な欠落や矛盾がないか。

## Target Files

- .reviewcompass/specs/workflow-management/requirements.md sha256=e7621e6d56a3ef42085e2864a88366d670e55c304668dd21f48dde32411e13f3
- .reviewcompass/specs/workflow-management/reviews/2026-06-19-workflow-management-requirements-vertical-redo-review-run-v2/prompt-postcheck.md sha256=280a0e974db05308acfc14a293025c0b70cfa297052c9fcd45a3e5a062004743
- .reviewcompass/specs/workflow-management/reviews/2026-06-19-workflow-management-requirements-vertical-redo-review-run-v2/prompts/claude-opus-4-8.round-1.prompt.md sha256=c4d2f479e208566177fdfdd51c186117efa0d5cba62f92e4d779c5cd8a1cf4c7
- .reviewcompass/specs/workflow-management/reviews/2026-06-19-workflow-management-requirements-vertical-redo-review-run-v2/prompts/gemini-3.1-pro-preview.round-1.prompt.md sha256=b236668f227f36b1fc88a4e46a24f3c2f0ab095d0b0803e41dee0cf4fbc34bdc
- .reviewcompass/specs/workflow-management/reviews/2026-06-19-workflow-management-requirements-vertical-redo-review-run-v2/prompts/gpt-5.4.round-1.prompt.md sha256=7004ddcd1818fdf1f126cd6f47ba7b1079227b29d116330f8cc16d74cc608d60
- .reviewcompass/specs/workflow-management/reviews/2026-06-19-workflow-management-requirements-vertical-redo-review-run-v2/proxy-decision-prompt.md sha256=263f17c21e633d649b216972445ed60ec347f6f677c2ef02751a01a68d281743
- .reviewcompass/specs/workflow-management/reviews/2026-06-19-workflow-management-requirements-vertical-redo-review-run-v2/raw-review-triage-summary.md sha256=a9e65b30525fa8df7c472c59506774814d0991c480de3e73b3e444ca8f4e630d
- .reviewcompass/specs/workflow-management/reviews/2026-06-19-workflow-management-requirements-vertical-redo-review-run-v2/review-target.md sha256=b44b2d7005a4d656a5734775696ca0bda0ab0b8d7ba4c7eb0ba7efa35ebce335
- .reviewcompass/specs/workflow-management/reviews/2026-06-19-workflow-management-requirements-vertical-redo-review-run-v2/review_summary.md sha256=e57851bf9f53b1565ea1f67b0c2a7fb5254b8e9dc2aeb6560fd70dbe56b25daf
- .reviewcompass/specs/workflow-management/reviews/2026-06-19-workflow-management-requirements-vertical-redo-review-run-v2/user-visible-triage-gate.md sha256=efda14dbf8c2aec91a433da96df72bcab4f6a527b86f37fbb35d432ea14d5b8d
- .reviewcompass/specs/workflow-management/reviews/2026-06-19-workflow-management-requirements-vertical-redo-review-run/invalidation.md sha256=6858f5e815e707d02139231c4475e51069d67e2dcd93a5fac8766c8a3a451915
- .reviewcompass/specs/workflow-management/reviews/2026-06-19-workflow-management-requirements-vertical-redo-review-run/prompts/claude-opus-4-8.round-1.prompt.md sha256=900ff36a653f3257f46de9fc17a413d98298f404b9a48f3395401590da9485d3
- .reviewcompass/specs/workflow-management/reviews/2026-06-19-workflow-management-requirements-vertical-redo-review-run/prompts/gemini-3.1-pro-preview.round-1.prompt.md sha256=e56e13114db997f504b1ab0a1e63e0c99946b9aee4a951ff3697a7e8095c2141
- .reviewcompass/specs/workflow-management/reviews/2026-06-19-workflow-management-requirements-vertical-redo-review-run/prompts/gpt-5.4.round-1.prompt.md sha256=8d892a3f1c3dc4920a18da914f1d8398648c0f72ce38a98a52b2189cae9914a6
- .reviewcompass/specs/workflow-management/reviews/2026-06-19-workflow-management-requirements-vertical-redo-review-run/proxy-decision-prompt.md sha256=02e91fb09ed76fac4164a2d3b383c46e054262f00ee5db83a91a792e79491229
- .reviewcompass/specs/workflow-management/reviews/2026-06-19-workflow-management-requirements-vertical-redo-review-run/review-target.md sha256=538243effc26a3d84f3d1bffb2ac25c9544c41e1eaf57d7a5f0f9308b20938b6
- .reviewcompass/specs/workflow-management/reviews/2026-06-19-workflow-management-requirements-vertical-redo-review-run/review_summary.md sha256=04eb12c4c15c73c4e0e1a7fd26ff63decca55475e6daa3487f3b175a912eb291
- docs/operations/SESSION_WORKFLOW_GUIDE.md sha256=904b60a6184ca438060897faf448f4de3c621c7cc66b3238912c849c477c0985
- docs/operations/WORKFLOW_DISCIPLINE_MAP.yaml sha256=007304ffb73fd022aa270296d02f2af4997728d2f975e56e2d324bc195e14ba2

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
.reviewcompass/specs/workflow-management/requirements.md
.reviewcompass/specs/workflow-management/reviews/2026-06-19-workflow-management-requirements-vertical-redo-review-run-v2/prompt-postcheck.md
.reviewcompass/specs/workflow-management/reviews/2026-06-19-workflow-management-requirements-vertical-redo-review-run-v2/prompts/claude-opus-4-8.round-1.prompt.md
.reviewcompass/specs/workflow-management/reviews/2026-06-19-workflow-management-requirements-vertical-redo-review-run-v2/prompts/gemini-3.1-pro-preview.round-1.prompt.md
.reviewcompass/specs/workflow-management/reviews/2026-06-19-workflow-management-requirements-vertical-redo-review-run-v2/prompts/gpt-5.4.round-1.prompt.md
.reviewcompass/specs/workflow-management/reviews/2026-06-19-workflow-management-requirements-vertical-redo-review-run-v2/proxy-decision-prompt.md
.reviewcompass/specs/workflow-management/reviews/2026-06-19-workflow-management-requirements-vertical-redo-review-run-v2/raw-review-triage-summary.md
.reviewcompass/specs/workflow-management/reviews/2026-06-19-workflow-management-requirements-vertical-redo-review-run-v2/review-target.md
.reviewcompass/specs/workflow-management/reviews/2026-06-19-workflow-management-requirements-vertical-redo-review-run-v2/review_summary.md
.reviewcompass/specs/workflow-management/reviews/2026-06-19-workflow-management-requirements-vertical-redo-review-run-v2/user-visible-triage-gate.md
.reviewcompass/specs/workflow-management/reviews/2026-06-19-workflow-management-requirements-vertical-redo-review-run/invalidation.md
.reviewcompass/specs/workflow-management/reviews/2026-06-19-workflow-management-requirements-vertical-redo-review-run/prompts/claude-opus-4-8.round-1.prompt.md
.reviewcompass/specs/workflow-management/reviews/2026-06-19-workflow-management-requirements-vertical-redo-review-run/prompts/gemini-3.1-pro-preview.round-1.prompt.md
.reviewcompass/specs/workflow-management/reviews/2026-06-19-workflow-management-requirements-vertical-redo-review-run/prompts/gpt-5.4.round-1.prompt.md
.reviewcompass/specs/workflow-management/reviews/2026-06-19-workflow-management-requirements-vertical-redo-review-run/proxy-decision-prompt.md
.reviewcompass/specs/workflow-management/reviews/2026-06-19-workflow-management-requirements-vertical-redo-review-run/review-target.md
.reviewcompass/specs/workflow-management/reviews/2026-06-19-workflow-management-requirements-vertical-redo-review-run/review_summary.md
docs/operations/SESSION_WORKFLOW_GUIDE.md
docs/operations/WORKFLOW_DISCIPLINE_MAP.yaml

# Target document
## .reviewcompass/specs/workflow-management/requirements.md

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
11. 本機能は `next --json` の目標応答スキーマを `.reviewcompass/schema/next_action_response.schema.json` として JSON Schema 形式で定義する。本スキーマは受入9が定める振る舞い契約（唯一アクション選択・進行中作業単位の有無による null/非 null の切り替え）をスキーマとして表現する。（1）最上位の必須フィールドは `verdict`（文字列）・`exit_code`（整数）・`next_action`（オブジェクト）・`reasons`（配列）・`current_state`（オブジェクト）の5つとし、`verdict` は最上位だけに置き `next_action` 内には含めない。（2）`next_action` の最低限の必須フィールドは `kind`（文字列・`required_action` の分類子、値域は design で確定）・`required_action`（受入10のスキーマを参照）・`active_gate`（文字列または null）・`feature`（文字列または null）・`phase`（文字列または null）・`stage`（文字列または null）・`required_feature_scope`（配列）・`blocked_by`（オブジェクトまたは null）・`future_gates`（配列）・`state_refs`（オブジェクト）の10フィールドとする。これに加え、`repair_reasons`（配列）は `repair_workflow_state` 時に必須となる条件付きフィールド（非空配列・最低1要素）とし、`action_parameters`（オブジェクト）は `run_maintenance` のみを対象とする必須の条件付きフィールドとして定義する。6フィールド（`maintenance_action`・`allowed_scope`・`allowed_files`・`completion_conditions`・`active_stack_frame_id`・`parent_frame_id`）はすべて required とし、追加フィールドの許可・禁止は design で確定する。（3）`feature` はリスト型を許容せず、取り得る値は「単一フィーチャー名」・`"all_features"`（review-wave のような真に横断的な実行単位の場合のみ）・null（進行中の作業単位がない場合）の3種類に限る。複数フィーチャーが影響範囲に入る場合は `required_feature_scope` または `future_gates` に置く。（4）受入9の null/非 null 規則をスキーマで表現する。進行中の作業単位（active workflow unit）がない場合、`feature`・`phase`・`stage`・`active_gate` はすべて null とする。作業単位がある（reopen 第3過程または通常 workflow の gate 実行時）場合のみ、これらのフィールドは非 null とする。（5）後方互換のため `pending_gates`・`next_pending_gate` はオプションフィールドとして定義し、このスキーマの正本フィールドは `future_gates`・`active_gate` とする。これらの後方互換フィールドが存在する場合は対応する正本フィールドと一致させること（`next --json` の実装側の不変条件として要求する。JSON Schema での表現は design で確定する）。新規のコンシューマは正本フィールドのみを参照してよい。（6）`required_action` の値ごとにフィールドの値制約（相互排他）がある。以下は D-003 §4.2 で確定している制約であり、スキーマはこれらを機械的に検証できる構造で表現する（スキーマ上の表現方法は design で確定）。① `commit_stop_point` の時：`active_gate=null`・`phase=null`・`stage=null`・`blocked_by.type="commit_stop_point"`。② `run_reopen_pending_gate` の時：`active_gate` 非 null・`phase`/`stage` は `active_gate` と一致・`blocked_by=null`。③ `run_reopen_drafting` の時：`active_gate` は `stages/<phase>.yaml#drafting` 形式・`phase`/`stage` はその drafting 単位と一致。④ `repair_workflow_state` の時：`active_gate=null`・`phase=null`・`stage=null`・`repair_reasons` に修復理由を含める。⑤ `wait_for_human_decision` の時：`blocked_by.type` で停止理由を区別。⑥ `run_maintenance` の時：`action_parameters` に `maintenance_action`・`allowed_scope`・`allowed_files`・`completion_conditions`・`active_stack_frame_id`・`parent_frame_id` を含める。上記①〜⑥の制約は D-003 §4.2 で確定している制約の全てであり、これ以外の `required_action` 種別には確定した追加フィールド制約はない（universal 必須フィールドのみが適用される）。

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


## .reviewcompass/specs/workflow-management/reviews/2026-06-19-workflow-management-requirements-vertical-redo-review-run-v2/prompt-postcheck.md

# Prompt Post-Check

status: passed_with_notes
date: 2026-06-19
review_run_id: 2026-06-19-workflow-management-requirements-vertical-redo-review-run-v2

## Checked Artifacts

- `review-target.md`
- `prompts/gpt-5.4.round-1.prompt.md`
- `prompts/claude-opus-4-8.round-1.prompt.md`
- `prompts/gemini-3.1-pro-preview.round-1.prompt.md`

## Checks

### Materialization Contract

Result: passed.

All checked artifacts include the vertical-intent materialization fields required by `WORKFLOW_DISCIPLINE_MAP.yaml`:

- `purpose`
- `responsibility_boundaries`
- `acceptance_criteria`
- `forbidden_actions`
- `unresolved_or_design_deferred_items`
- `intended_target_phase_transfer`

The local `validate_review_prompt_preflight` check returned OK for `review-target.md` and all three generated prompt files.

### Information

Result: passed.

The prompt includes:

- upstream source paths
- a structured upstream summary rather than path-only references
- target phase artifact excerpt
- the full target document content generated by `run_review.py`
- output contract / finding policy

### Question

Result: passed.

The prompt asks whether upstream purpose, responsibility boundaries, acceptance criteria, forbidden actions, unresolved / design-deferred items, and intended target-phase transfer are inherited into Requirement 13-16 without omission, weakening, unsupported additions, or drift.

This is an open analysis question. It does not force the reviewer to choose from closed options.

### Scope

Result: passed.

The prompt limits the target artifact to `.reviewcompass/specs/workflow-management/requirements.md`, specifically Requirement 13-16 and directly related Change Intent / traceability text.

It explicitly marks these as out of scope:

- `design.md` correctness
- `tasks.md` correctness
- implementation code changes
- commit / push / spec mutation / phase approval / reopen movement

### Sensitive Information

Result: passed with notes.

Pattern scan matched explanatory words such as `API keys`, `access tokens`, `passwords`, and `secret`, but these occur in the prompt's own sensitive-information check and in requirements text about redaction behavior. No concrete API key, access token, password, personal contact information, or non-public third-party confidential data was identified.

## Conclusion

The created prompt satisfies the corrected vertical intent-transfer review discipline and the API prompt construction guideline at the mechanical post-check level.

Residual risk: the quality of the upstream structured summary remains a semantic judgment. The mechanical check confirms required fields and non-path-only materialization, but it cannot prove that the summary is exhaustive.


## .reviewcompass/specs/workflow-management/reviews/2026-06-19-workflow-management-requirements-vertical-redo-review-run-v2/prompts/claude-opus-4-8.round-1.prompt.md

prompt_id: anthropic_review
provider: anthropic-api
model_id: claude-opus-4-8

# Task
Review the target document for the requested phase and criteria.

# Phase
triad-review

# Criteria
# Requirements Vertical Intent Review Target: Workflow Management Requirement 13-16

## Review Target

Review the vertical intent transfer into `.reviewcompass/specs/workflow-management/requirements.md`, specifically Requirement 13 through Requirement 16 and their directly related Change Intent / traceability text.

The target phase artifact is `requirements.md`. The review question is not whether downstream `design.md` or `tasks.md` are correct.

## Source Materials

These source materials were read and summarized below. They are not path-only references.

- `docs/reviews/reopen-classification-2026-06-19-wm-requirement-13-16-vertical-redo.md`
- `docs/notes/2026-06-18-integrated-design-selection-execution-layers.md`
- `docs/notes/working/2026-06-18-mechanized-workflow-execution-design.md`
- `docs/notes/working/2026-06-19-integrated-design-requirements-missing.md`
- `docs/operations/SESSION_WORKFLOW_GUIDE.md#vertical-intent-transfer-review`

## Upstream Structured Summary

### purpose

The upstream purpose is to make workflow execution less dependent on LLM memory or implicit interpretation. `next --json` remains the selector that decides what should happen next; execution must be governed by machine-readable operation contracts, preflight checks, approval gates, side-track state, workflow-state snapshots, and structured language-task prompts.

For this reopen, the purpose is narrower: restore the integrated design intent that was previously under-transferred into requirements. The 2026-06-18 request was to incorporate the two integrated design notes into intent / requirements and then proceed through the workflow. The prior result only added the minimal Phase 1 schema points, so Requirement 13-16 now need to carry the larger upstream intent.

### responsibility_boundaries

- Selection layer boundary: `next --json` chooses the single current `required_action`; it is not replaced by operation contracts or workflow-state snapshots.
- Execution layer boundary: operation contracts define how an action is executed, including `effect_kind`, `approval_required`, sequence, preconditions, postconditions, pending conflicts, and fail-closed behavior.
- Registry / preflight boundary: registry and preflight are read-only consumers / confirmations of the contract. They must not become independent sources of truth, execute operations, update state, or consume approvals.
- Human decision boundary: `record_human_decision` records a decision but does not itself authorize an approval-required operation. Commit, push, spec updates, phase approval, reopen finalize, and approval-required irreversible operations remain human-only.
- LLM boundary: LLMs perform language tasks such as drafting, triage explanation, and semantic audit. Mechanical checks, guards, preflight, and approval enforcement must not be left to implicit LLM judgment.
- Snapshot boundary: workflow-state snapshots are visualization / audit support and must not replace `next --json` or state refs.

### acceptance_criteria

Upstream acceptance intent includes:

- The 19 `required_action` terms must map to operation contract information, including `effect_kind`, execution actor, and `approval_required`.
- `approval_required` is independent from `effect_kind`; some `state_mutation` operations are approval-required and some are not.
- Approval-required actions include at least `commit_stop_point`, `apply_approved_reopen_plan`, `run_reopen_start`, `advance_reopen_after_commit_stop_point`, `advance_reopen_after_approval_stop_point`, `finalize_reopen`, and `repair_workflow_state`.
- `record_human_decision` is a decision-recording operation and a component of the approval gate; its completion must not be treated as approval for the target operation.
- `run_reopen_pending_gate` branches by gate kind: `triad-review` / `review-wave` are external API review runs, `alignment` is a write language task, `approval` structures an approval request, and drafting is separated.
- Complex actions such as `run_maintenance`, `run_reopen_pending_gate`, and `run_workflow_stage` may vary by internal step or stage kind; their representation is a design decision, but LLMs must not infer it ad hoc.
- Side track frames need `allowed_scope`, `allowed_files`, `return_to`, `staged_file_digest`, and `staged_file_set`; only the top frame can be popped, and `next --json` resumes the next state.
- Side-track depth excess, scope drift, and commit mixing are initially warning-only in Phase 3 and mechanically blocked in Phase 5.
- Structured effective prompts must describe the language task, not embed mechanical execution. Machine checks belong to contracts, preflight, runners, and guards.
- LLM judge audit is auxiliary semantic analysis and must not automate final approval or override mechanical / human-only gates.
- Phase order is Phase 1 schema, Phase 0 selector implementation, then Phase 2 read-only registry, Phase 3 warning preflight, Phase 4 structured prompts, Phase 5 blocking guards, Phase 6 optional LLM judge audit.

### forbidden_actions

The upstream materials forbid or constrain:

- Treating source materials as path-only references when the review asks for vertical intent transfer.
- Letting LLMs infer operation side effects, approval requirements, return destinations, or complex-operation branches from conversation context.
- Treating `record_human_decision` completion as approval for an approval-required target operation.
- Letting proxy_model replace human-only decisions.
- Letting workflow-state snapshots become canonical state or a hidden state-mutation path.
- Reimplementing mechanical checks inside effective prompts instead of referencing machine-confirmed preconditions and contract / preflight outputs.
- Mixing phase-spanning intermediate implementation states into a single commit.
- Treating historical `spec.json.reopened` as the current active reopen scope.
- Confusing reopen scope with impact-review scope.

### unresolved_or_design_deferred_items

The upstream materials intentionally defer some details to design:

- Physical representation of complex operations: maximum side-effect representative value, list-valued `effect_kind`, or internal-step decomposition.
- The exact data structure tying `record_human_decision` to the approval target operation.
- The exact implementation path for workflow-state snapshot generation.
- The exact way D-003 scenarios become Phase 6 semantic-audit tests.
- Human-required predicate priority and conflict resolution for proxy_model applicability.
- Concrete command names / arguments for future operation runner behavior.

These deferred details should not be forced into requirements as final implementation design, but requirements should preserve enough constraints so design cannot silently choose an unsafe option.

### intended_target_phase_transfer

The intended requirements-level transfer is:

- Requirement 13 should capture operation contract vocabulary, the 19-action mapping, approval-required semantics, complex-operation constraints, single-source-of-truth boundary, read-only registry/preflight role, and fail-closed drift handling.
- Requirement 14 should capture approval gate semantics, explicit human-decision records, side-track stack safety, staged-file digest checks, workflow-state snapshots as non-canonical support, read-only versus mutating state operations, and proxy_model versus human-only boundaries.
- Requirement 15 should capture structured effective prompts as language-task specifications, machine-checkable prompt structure, separation from mechanical tasks, and LLM judge audit as non-approving auxiliary analysis.
- Requirement 16 should capture Phase 1 / Phase 0 / Phase 2-6 ordering, phase completion constraints, no cross-phase implementation mixing, active reopen scope versus historical flags, impact review scope, and proxy_model applicability predicates.

## Target Phase Artifact Excerpt

Requirement 13 currently covers operation contract vocabulary, `.reviewcompass/schema/` Phase 1 schemas, the 19 `required_action` mapping, approval-required simple actions, `record_human_decision`, `run_reopen_pending_gate`, complex operations, fail-closed pre/postconditions, and contract / registry / preflight source-of-truth boundaries.

Requirement 14 currently covers approval gates, side-track stack frames, staged file set / digest checks, side-track pop and max depth, workflow-state snapshots, proxy_model versus human-only decisions, and read-only versus mutating operation boundaries.

Requirement 15 currently covers structured effective prompt fields, `language_task`, separation from mechanical tasks, Phase 4 prompt generation, first-layer machine checks, Phase 6 LLM judge audit, and non-automation of semantic final approval.

Requirement 16 currently covers Phase 0 through Phase 6 ordering and completion, no phase-spanning intermediate state commits, active reopen scope versus historical reopened flags, impact review scope, proxy_model triage decision applicability predicates, and human-required precedence.

## Required Check

Independently analyze whether the upstream purpose, responsibility boundaries, acceptance criteria, forbidden actions, unresolved / design-deferred items, and intended target-phase transfer are inherited into Requirement 13-16 without omission, weakening, unsupported additions, or drift.

Do not assume the requirements are correct because they mention the upstream files. Judge the actual transfer.

## Out Of Scope

- Correctness of `design.md`
- Correctness or implementation-readiness of `tasks.md`
- Whether design/tasks already carry the requirements correctly
- Implementation code changes
- Commit, push, spec.json mutation, phase approval, or reopen movement

## Finding Policy

Return findings as YAML with a top-level `findings` list. Each finding must include:

- `severity`: CRITICAL, ERROR, WARN, or INFO
- `target_location`: file and section / requirement
- `description`: concrete issue
- `rationale`: why it matters
- `recommendation`: what should change

Use `ERROR` for omissions, weakened requirements, unsupported additions, or responsibility-boundary drift that make requirements unsafe to approve.
Use `WARN` for ambiguity or traceability weakness that should be fixed before downstream design/tasks review.
Use `INFO` only for non-blocking observations.

If there are no substantive findings, return `findings: []`.

## Sensitive Information Check

No API keys, access tokens, passwords, personal contact information, or non-public third-party confidential data are intentionally included in this review target.


# Output contract
Return YAML only.
The top-level key must be exactly findings.
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
.reviewcompass/specs/workflow-management/requirements.md

# Target document
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
11. 本機能は `next --json` の目標応答スキーマを `.reviewcompass/schema/next_action_response.schema.json` として JSON Schema 形式で定義する。本スキーマは受入9が定める振る舞い契約（唯一アクション選択・進行中作業単位の有無による null/非 null の切り替え）をスキーマとして表現する。（1）最上位の必須フィールドは `verdict`（文字列）・`exit_code`（整数）・`next_action`（オブジェクト）・`reasons`（配列）・`current_state`（オブジェクト）の5つとし、`verdict` は最上位だけに置き `next_action` 内には含めない。（2）`next_action` の最低限の必須フィールドは `kind`（文字列・`required_action` の分類子、値域は design で確定）・`required_action`（受入10のスキーマを参照）・`active_gate`（文字列または null）・`feature`（文字列または null）・`phase`（文字列または null）・`stage`（文字列または null）・`required_feature_scope`（配列）・`blocked_by`（オブジェクトまたは null）・`future_gates`（配列）・`state_refs`（オブジェクト）の10フィールドとする。これに加え、`repair_reasons`（配列）は `repair_workflow_state` 時に必須となる条件付きフィールド（非空配列・最低1要素）とし、`action_parameters`（オブジェクト）は `run_maintenance` のみを対象とする必須の条件付きフィールドとして定義する。6フィールド（`maintenance_action`・`allowed_scope`・`allowed_files`・`completion_conditions`・`active_stack_frame_id`・`parent_frame_id`）はすべて required とし、追加フィールドの許可・禁止は design で確定する。（3）`feature` はリスト型を許容せず、取り得る値は「単一フィーチャー名」・`"all_features"`（review-wave のような真に横断的な実行単位の場合のみ）・null（進行中の作業単位がない場合）の3種類に限る。複数フィーチャーが影響範囲に入る場合は `required_feature_scope` または `future_gates` に置く。（4）受入9の null/非 null 規則をスキーマで表現する。進行中の作業単位（active workflow unit）がない場合、`feature`・`phase`・`stage`・`active_gate` はすべて null とする。作業単位がある（reopen 第3過程または通常 workflow の gate 実行時）場合のみ、これらのフィールドは非 null とする。（5）後方互換のため `pending_gates`・`next_pending_gate` はオプションフィールドとして定義し、このスキーマの正本フィールドは `future_gates`・`active_gate` とする。これらの後方互換フィールドが存在する場合は対応する正本フィールドと一致させること（`next --json` の実装側の不変条件として要求する。JSON Schema での表現は design で確定する）。新規のコンシューマは正本フィールドのみを参照してよい。（6）`required_action` の値ごとにフィールドの値制約（相互排他）がある。以下は D-003 §4.2 で確定している制約であり、スキーマはこれらを機械的に検証できる構造で表現する（スキーマ上の表現方法は design で確定）。① `commit_stop_point` の時：`active_gate=null`・`phase=null`・`stage=null`・`blocked_by.type="commit_stop_point"`。② `run_reopen_pending_gate` の時：`active_gate` 非 null・`phase`/`stage` は `active_gate` と一致・`blocked_by=null`。③ `run_reopen_drafting` の時：`active_gate` は `stages/<phase>.yaml#drafting` 形式・`phase`/`stage` はその drafting 単位と一致。④ `repair_workflow_state` の時：`active_gate=null`・`phase=null`・`stage=null`・`repair_reasons` に修復理由を含める。⑤ `wait_for_human_decision` の時：`blocked_by.type` で停止理由を区別。⑥ `run_maintenance` の時：`action_parameters` に `maintenance_action`・`allowed_scope`・`allowed_files`・`completion_conditions`・`active_stack_frame_id`・`parent_frame_id` を含める。上記①〜⑥の制約は D-003 §4.2 で確定している制約の全てであり、これ以外の `required_action` 種別には確定した追加フィールド制約はない（universal 必須フィールドのみが適用される）。

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
5. 承認ゲートを必須とする単純操作は、最低限 `commit_stop_point`、`apply_approved_reopen_plan`、`run_reopen_start`、`advance_reopen_after_commit_stop_point`、`advance_reopen_after_approval_stop_point`、`finalize_reopen`、`repair_workflow_state` を含む。これらは `approval_required: true` として扱い、実行前に明示的な人間判断記録を必要とする。この列挙は複合操作の分岐条件を否定しない。`run_maintenance` は maintenance YAML または内部操作の承認要求に従い、`run_workflow_stage` は stage 種別に従う。
6. `record_human_decision` は承認対象操作ではなく、承認ゲートを構成する判断記録操作として扱う。`effect_kind` は判断記録を書き込む場合は `state_mutation` とし、`approval_required` は常に `false` とする。`record_human_decision` の完了だけでは、対象 operation の `approval_required: true` を満たしたことにしてはならない。
7. `run_reopen_pending_gate` は active gate 種別に応じて operation contract を分岐する。`triad-review` と `review-wave` は外部レビュー実行を伴う `external_call`、`alignment` は LLM が整合確認材料を生成する `write`、`approval` は承認要求を構造化する `state_mutation` として扱う。drafting は `run_reopen_drafting` として分離する。
8. `run_maintenance` と `run_workflow_stage` は、内部で実行する操作または stage 種別によって `effect_kind` と `approval_required` が変わる複合操作として扱う。複合操作を単一代表値、list 型、内部ステップ分解のいずれで表すかは design で確定するが、LLM が都度推測する形にはしない。design で確定するまでの最小規則として、複合操作は分岐条件、内部 step、各 step の `effect_kind`、最大副作用、承認要否の集約規則を持つものとして扱う。
9. 複合操作の schema 表現は Phase 1 の未確定事項として扱う。候補は、最大副作用の `effect_kind` を代表値として注記する、`effect_kind` を list 型にする、複合操作を単一 enum の内部ステップへ分解する、の3案を最低限保持する。また、`record_human_decision` が記録する判断と承認対象の `required_action` を、セッション識別子、タイムスタンプ、操作 ID、または同等の識別子で結びつける方法を design で確定する。
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
11. 承認ゲートは proxy_model が代行できる判断と、人間だけが承認できる判断を機械可読に区別する。少なくとも commit、push、spec.json 更新、phase approval、reopen finalize、approval_required な不可逆操作の実行許可は human-only decision として扱い、proxy_model decision だけで通過させてはならない。proxy_model は所見 triage や補助判断を代行できるが、human-only decision の承認主体を置換しない。
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



## .reviewcompass/specs/workflow-management/reviews/2026-06-19-workflow-management-requirements-vertical-redo-review-run-v2/prompts/gemini-3.1-pro-preview.round-1.prompt.md

prompt_id: gemini_review
provider: gemini-api
model_id: gemini-3.1-pro-preview

# Task
Review the target document for the requested phase and criteria.

# Phase
triad-review

# Criteria
# Requirements Vertical Intent Review Target: Workflow Management Requirement 13-16

## Review Target

Review the vertical intent transfer into `.reviewcompass/specs/workflow-management/requirements.md`, specifically Requirement 13 through Requirement 16 and their directly related Change Intent / traceability text.

The target phase artifact is `requirements.md`. The review question is not whether downstream `design.md` or `tasks.md` are correct.

## Source Materials

These source materials were read and summarized below. They are not path-only references.

- `docs/reviews/reopen-classification-2026-06-19-wm-requirement-13-16-vertical-redo.md`
- `docs/notes/2026-06-18-integrated-design-selection-execution-layers.md`
- `docs/notes/working/2026-06-18-mechanized-workflow-execution-design.md`
- `docs/notes/working/2026-06-19-integrated-design-requirements-missing.md`
- `docs/operations/SESSION_WORKFLOW_GUIDE.md#vertical-intent-transfer-review`

## Upstream Structured Summary

### purpose

The upstream purpose is to make workflow execution less dependent on LLM memory or implicit interpretation. `next --json` remains the selector that decides what should happen next; execution must be governed by machine-readable operation contracts, preflight checks, approval gates, side-track state, workflow-state snapshots, and structured language-task prompts.

For this reopen, the purpose is narrower: restore the integrated design intent that was previously under-transferred into requirements. The 2026-06-18 request was to incorporate the two integrated design notes into intent / requirements and then proceed through the workflow. The prior result only added the minimal Phase 1 schema points, so Requirement 13-16 now need to carry the larger upstream intent.

### responsibility_boundaries

- Selection layer boundary: `next --json` chooses the single current `required_action`; it is not replaced by operation contracts or workflow-state snapshots.
- Execution layer boundary: operation contracts define how an action is executed, including `effect_kind`, `approval_required`, sequence, preconditions, postconditions, pending conflicts, and fail-closed behavior.
- Registry / preflight boundary: registry and preflight are read-only consumers / confirmations of the contract. They must not become independent sources of truth, execute operations, update state, or consume approvals.
- Human decision boundary: `record_human_decision` records a decision but does not itself authorize an approval-required operation. Commit, push, spec updates, phase approval, reopen finalize, and approval-required irreversible operations remain human-only.
- LLM boundary: LLMs perform language tasks such as drafting, triage explanation, and semantic audit. Mechanical checks, guards, preflight, and approval enforcement must not be left to implicit LLM judgment.
- Snapshot boundary: workflow-state snapshots are visualization / audit support and must not replace `next --json` or state refs.

### acceptance_criteria

Upstream acceptance intent includes:

- The 19 `required_action` terms must map to operation contract information, including `effect_kind`, execution actor, and `approval_required`.
- `approval_required` is independent from `effect_kind`; some `state_mutation` operations are approval-required and some are not.
- Approval-required actions include at least `commit_stop_point`, `apply_approved_reopen_plan`, `run_reopen_start`, `advance_reopen_after_commit_stop_point`, `advance_reopen_after_approval_stop_point`, `finalize_reopen`, and `repair_workflow_state`.
- `record_human_decision` is a decision-recording operation and a component of the approval gate; its completion must not be treated as approval for the target operation.
- `run_reopen_pending_gate` branches by gate kind: `triad-review` / `review-wave` are external API review runs, `alignment` is a write language task, `approval` structures an approval request, and drafting is separated.
- Complex actions such as `run_maintenance`, `run_reopen_pending_gate`, and `run_workflow_stage` may vary by internal step or stage kind; their representation is a design decision, but LLMs must not infer it ad hoc.
- Side track frames need `allowed_scope`, `allowed_files`, `return_to`, `staged_file_digest`, and `staged_file_set`; only the top frame can be popped, and `next --json` resumes the next state.
- Side-track depth excess, scope drift, and commit mixing are initially warning-only in Phase 3 and mechanically blocked in Phase 5.
- Structured effective prompts must describe the language task, not embed mechanical execution. Machine checks belong to contracts, preflight, runners, and guards.
- LLM judge audit is auxiliary semantic analysis and must not automate final approval or override mechanical / human-only gates.
- Phase order is Phase 1 schema, Phase 0 selector implementation, then Phase 2 read-only registry, Phase 3 warning preflight, Phase 4 structured prompts, Phase 5 blocking guards, Phase 6 optional LLM judge audit.

### forbidden_actions

The upstream materials forbid or constrain:

- Treating source materials as path-only references when the review asks for vertical intent transfer.
- Letting LLMs infer operation side effects, approval requirements, return destinations, or complex-operation branches from conversation context.
- Treating `record_human_decision` completion as approval for an approval-required target operation.
- Letting proxy_model replace human-only decisions.
- Letting workflow-state snapshots become canonical state or a hidden state-mutation path.
- Reimplementing mechanical checks inside effective prompts instead of referencing machine-confirmed preconditions and contract / preflight outputs.
- Mixing phase-spanning intermediate implementation states into a single commit.
- Treating historical `spec.json.reopened` as the current active reopen scope.
- Confusing reopen scope with impact-review scope.

### unresolved_or_design_deferred_items

The upstream materials intentionally defer some details to design:

- Physical representation of complex operations: maximum side-effect representative value, list-valued `effect_kind`, or internal-step decomposition.
- The exact data structure tying `record_human_decision` to the approval target operation.
- The exact implementation path for workflow-state snapshot generation.
- The exact way D-003 scenarios become Phase 6 semantic-audit tests.
- Human-required predicate priority and conflict resolution for proxy_model applicability.
- Concrete command names / arguments for future operation runner behavior.

These deferred details should not be forced into requirements as final implementation design, but requirements should preserve enough constraints so design cannot silently choose an unsafe option.

### intended_target_phase_transfer

The intended requirements-level transfer is:

- Requirement 13 should capture operation contract vocabulary, the 19-action mapping, approval-required semantics, complex-operation constraints, single-source-of-truth boundary, read-only registry/preflight role, and fail-closed drift handling.
- Requirement 14 should capture approval gate semantics, explicit human-decision records, side-track stack safety, staged-file digest checks, workflow-state snapshots as non-canonical support, read-only versus mutating state operations, and proxy_model versus human-only boundaries.
- Requirement 15 should capture structured effective prompts as language-task specifications, machine-checkable prompt structure, separation from mechanical tasks, and LLM judge audit as non-approving auxiliary analysis.
- Requirement 16 should capture Phase 1 / Phase 0 / Phase 2-6 ordering, phase completion constraints, no cross-phase implementation mixing, active reopen scope versus historical flags, impact review scope, and proxy_model applicability predicates.

## Target Phase Artifact Excerpt

Requirement 13 currently covers operation contract vocabulary, `.reviewcompass/schema/` Phase 1 schemas, the 19 `required_action` mapping, approval-required simple actions, `record_human_decision`, `run_reopen_pending_gate`, complex operations, fail-closed pre/postconditions, and contract / registry / preflight source-of-truth boundaries.

Requirement 14 currently covers approval gates, side-track stack frames, staged file set / digest checks, side-track pop and max depth, workflow-state snapshots, proxy_model versus human-only decisions, and read-only versus mutating operation boundaries.

Requirement 15 currently covers structured effective prompt fields, `language_task`, separation from mechanical tasks, Phase 4 prompt generation, first-layer machine checks, Phase 6 LLM judge audit, and non-automation of semantic final approval.

Requirement 16 currently covers Phase 0 through Phase 6 ordering and completion, no phase-spanning intermediate state commits, active reopen scope versus historical reopened flags, impact review scope, proxy_model triage decision applicability predicates, and human-required precedence.

## Required Check

Independently analyze whether the upstream purpose, responsibility boundaries, acceptance criteria, forbidden actions, unresolved / design-deferred items, and intended target-phase transfer are inherited into Requirement 13-16 without omission, weakening, unsupported additions, or drift.

Do not assume the requirements are correct because they mention the upstream files. Judge the actual transfer.

## Out Of Scope

- Correctness of `design.md`
- Correctness or implementation-readiness of `tasks.md`
- Whether design/tasks already carry the requirements correctly
- Implementation code changes
- Commit, push, spec.json mutation, phase approval, or reopen movement

## Finding Policy

Return findings as YAML with a top-level `findings` list. Each finding must include:

- `severity`: CRITICAL, ERROR, WARN, or INFO
- `target_location`: file and section / requirement
- `description`: concrete issue
- `rationale`: why it matters
- `recommendation`: what should change

Use `ERROR` for omissions, weakened requirements, unsupported additions, or responsibility-boundary drift that make requirements unsafe to approve.
Use `WARN` for ambiguity or traceability weakness that should be fixed before downstream design/tasks review.
Use `INFO` only for non-blocking observations.

If there are no substantive findings, return `findings: []`.

## Sensitive Information Check

No API keys, access tokens, passwords, personal contact information, or non-public third-party confidential data are intentionally included in this review target.


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
.reviewcompass/specs/workflow-management/requirements.md

# Target document
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
11. 本機能は `next --json` の目標応答スキーマを `.reviewcompass/schema/next_action_response.schema.json` として JSON Schema 形式で定義する。本スキーマは受入9が定める振る舞い契約（唯一アクション選択・進行中作業単位の有無による null/非 null の切り替え）をスキーマとして表現する。（1）最上位の必須フィールドは `verdict`（文字列）・`exit_code`（整数）・`next_action`（オブジェクト）・`reasons`（配列）・`current_state`（オブジェクト）の5つとし、`verdict` は最上位だけに置き `next_action` 内には含めない。（2）`next_action` の最低限の必須フィールドは `kind`（文字列・`required_action` の分類子、値域は design で確定）・`required_action`（受入10のスキーマを参照）・`active_gate`（文字列または null）・`feature`（文字列または null）・`phase`（文字列または null）・`stage`（文字列または null）・`required_feature_scope`（配列）・`blocked_by`（オブジェクトまたは null）・`future_gates`（配列）・`state_refs`（オブジェクト）の10フィールドとする。これに加え、`repair_reasons`（配列）は `repair_workflow_state` 時に必須となる条件付きフィールド（非空配列・最低1要素）とし、`action_parameters`（オブジェクト）は `run_maintenance` のみを対象とする必須の条件付きフィールドとして定義する。6フィールド（`maintenance_action`・`allowed_scope`・`allowed_files`・`completion_conditions`・`active_stack_frame_id`・`parent_frame_id`）はすべて required とし、追加フィールドの許可・禁止は design で確定する。（3）`feature` はリスト型を許容せず、取り得る値は「単一フィーチャー名」・`"all_features"`（review-wave のような真に横断的な実行単位の場合のみ）・null（進行中の作業単位がない場合）の3種類に限る。複数フィーチャーが影響範囲に入る場合は `required_feature_scope` または `future_gates` に置く。（4）受入9の null/非 null 規則をスキーマで表現する。進行中の作業単位（active workflow unit）がない場合、`feature`・`phase`・`stage`・`active_gate` はすべて null とする。作業単位がある（reopen 第3過程または通常 workflow の gate 実行時）場合のみ、これらのフィールドは非 null とする。（5）後方互換のため `pending_gates`・`next_pending_gate` はオプションフィールドとして定義し、このスキーマの正本フィールドは `future_gates`・`active_gate` とする。これらの後方互換フィールドが存在する場合は対応する正本フィールドと一致させること（`next --json` の実装側の不変条件として要求する。JSON Schema での表現は design で確定する）。新規のコンシューマは正本フィールドのみを参照してよい。（6）`required_action` の値ごとにフィールドの値制約（相互排他）がある。以下は D-003 §4.2 で確定している制約であり、スキーマはこれらを機械的に検証できる構造で表現する（スキーマ上の表現方法は design で確定）。① `commit_stop_point` の時：`active_gate=null`・`phase=null`・`stage=null`・`blocked_by.type="commit_stop_point"`。② `run_reopen_pending_gate` の時：`active_gate` 非 null・`phase`/`stage` は `active_gate` と一致・`blocked_by=null`。③ `run_reopen_drafting` の時：`active_gate` は `stages/<phase>.yaml#drafting` 形式・`phase`/`stage` はその drafting 単位と一致。④ `repair_workflow_state` の時：`active_gate=null`・`phase=null`・`stage=null`・`repair_reasons` に修復理由を含める。⑤ `wait_for_human_decision` の時：`blocked_by.type` で停止理由を区別。⑥ `run_maintenance` の時：`action_parameters` に `maintenance_action`・`allowed_scope`・`allowed_files`・`completion_conditions`・`active_stack_frame_id`・`parent_frame_id` を含める。上記①〜⑥の制約は D-003 §4.2 で確定している制約の全てであり、これ以外の `required_action` 種別には確定した追加フィールド制約はない（universal 必須フィールドのみが適用される）。

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
5. 承認ゲートを必須とする単純操作は、最低限 `commit_stop_point`、`apply_approved_reopen_plan`、`run_reopen_start`、`advance_reopen_after_commit_stop_point`、`advance_reopen_after_approval_stop_point`、`finalize_reopen`、`repair_workflow_state` を含む。これらは `approval_required: true` として扱い、実行前に明示的な人間判断記録を必要とする。この列挙は複合操作の分岐条件を否定しない。`run_maintenance` は maintenance YAML または内部操作の承認要求に従い、`run_workflow_stage` は stage 種別に従う。
6. `record_human_decision` は承認対象操作ではなく、承認ゲートを構成する判断記録操作として扱う。`effect_kind` は判断記録を書き込む場合は `state_mutation` とし、`approval_required` は常に `false` とする。`record_human_decision` の完了だけでは、対象 operation の `approval_required: true` を満たしたことにしてはならない。
7. `run_reopen_pending_gate` は active gate 種別に応じて operation contract を分岐する。`triad-review` と `review-wave` は外部レビュー実行を伴う `external_call`、`alignment` は LLM が整合確認材料を生成する `write`、`approval` は承認要求を構造化する `state_mutation` として扱う。drafting は `run_reopen_drafting` として分離する。
8. `run_maintenance` と `run_workflow_stage` は、内部で実行する操作または stage 種別によって `effect_kind` と `approval_required` が変わる複合操作として扱う。複合操作を単一代表値、list 型、内部ステップ分解のいずれで表すかは design で確定するが、LLM が都度推測する形にはしない。design で確定するまでの最小規則として、複合操作は分岐条件、内部 step、各 step の `effect_kind`、最大副作用、承認要否の集約規則を持つものとして扱う。
9. 複合操作の schema 表現は Phase 1 の未確定事項として扱う。候補は、最大副作用の `effect_kind` を代表値として注記する、`effect_kind` を list 型にする、複合操作を単一 enum の内部ステップへ分解する、の3案を最低限保持する。また、`record_human_decision` が記録する判断と承認対象の `required_action` を、セッション識別子、タイムスタンプ、操作 ID、または同等の識別子で結びつける方法を design で確定する。
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
11. 承認ゲートは proxy_model が代行できる判断と、人間だけが承認できる判断を機械可読に区別する。少なくとも commit、push、spec.json 更新、phase approval、reopen finalize、approval_required な不可逆操作の実行許可は human-only decision として扱い、proxy_model decision だけで通過させてはならない。proxy_model は所見 triage や補助判断を代行できるが、human-only decision の承認主体を置換しない。
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



## .reviewcompass/specs/workflow-management/reviews/2026-06-19-workflow-management-requirements-vertical-redo-review-run-v2/prompts/gpt-5.4.round-1.prompt.md

prompt_id: openai_review
provider: openai-api
model_id: gpt-5.4

# Task
Review the target document for the requested phase and criteria.

# Phase
triad-review

# Criteria
# Requirements Vertical Intent Review Target: Workflow Management Requirement 13-16

## Review Target

Review the vertical intent transfer into `.reviewcompass/specs/workflow-management/requirements.md`, specifically Requirement 13 through Requirement 16 and their directly related Change Intent / traceability text.

The target phase artifact is `requirements.md`. The review question is not whether downstream `design.md` or `tasks.md` are correct.

## Source Materials

These source materials were read and summarized below. They are not path-only references.

- `docs/reviews/reopen-classification-2026-06-19-wm-requirement-13-16-vertical-redo.md`
- `docs/notes/2026-06-18-integrated-design-selection-execution-layers.md`
- `docs/notes/working/2026-06-18-mechanized-workflow-execution-design.md`
- `docs/notes/working/2026-06-19-integrated-design-requirements-missing.md`
- `docs/operations/SESSION_WORKFLOW_GUIDE.md#vertical-intent-transfer-review`

## Upstream Structured Summary

### purpose

The upstream purpose is to make workflow execution less dependent on LLM memory or implicit interpretation. `next --json` remains the selector that decides what should happen next; execution must be governed by machine-readable operation contracts, preflight checks, approval gates, side-track state, workflow-state snapshots, and structured language-task prompts.

For this reopen, the purpose is narrower: restore the integrated design intent that was previously under-transferred into requirements. The 2026-06-18 request was to incorporate the two integrated design notes into intent / requirements and then proceed through the workflow. The prior result only added the minimal Phase 1 schema points, so Requirement 13-16 now need to carry the larger upstream intent.

### responsibility_boundaries

- Selection layer boundary: `next --json` chooses the single current `required_action`; it is not replaced by operation contracts or workflow-state snapshots.
- Execution layer boundary: operation contracts define how an action is executed, including `effect_kind`, `approval_required`, sequence, preconditions, postconditions, pending conflicts, and fail-closed behavior.
- Registry / preflight boundary: registry and preflight are read-only consumers / confirmations of the contract. They must not become independent sources of truth, execute operations, update state, or consume approvals.
- Human decision boundary: `record_human_decision` records a decision but does not itself authorize an approval-required operation. Commit, push, spec updates, phase approval, reopen finalize, and approval-required irreversible operations remain human-only.
- LLM boundary: LLMs perform language tasks such as drafting, triage explanation, and semantic audit. Mechanical checks, guards, preflight, and approval enforcement must not be left to implicit LLM judgment.
- Snapshot boundary: workflow-state snapshots are visualization / audit support and must not replace `next --json` or state refs.

### acceptance_criteria

Upstream acceptance intent includes:

- The 19 `required_action` terms must map to operation contract information, including `effect_kind`, execution actor, and `approval_required`.
- `approval_required` is independent from `effect_kind`; some `state_mutation` operations are approval-required and some are not.
- Approval-required actions include at least `commit_stop_point`, `apply_approved_reopen_plan`, `run_reopen_start`, `advance_reopen_after_commit_stop_point`, `advance_reopen_after_approval_stop_point`, `finalize_reopen`, and `repair_workflow_state`.
- `record_human_decision` is a decision-recording operation and a component of the approval gate; its completion must not be treated as approval for the target operation.
- `run_reopen_pending_gate` branches by gate kind: `triad-review` / `review-wave` are external API review runs, `alignment` is a write language task, `approval` structures an approval request, and drafting is separated.
- Complex actions such as `run_maintenance`, `run_reopen_pending_gate`, and `run_workflow_stage` may vary by internal step or stage kind; their representation is a design decision, but LLMs must not infer it ad hoc.
- Side track frames need `allowed_scope`, `allowed_files`, `return_to`, `staged_file_digest`, and `staged_file_set`; only the top frame can be popped, and `next --json` resumes the next state.
- Side-track depth excess, scope drift, and commit mixing are initially warning-only in Phase 3 and mechanically blocked in Phase 5.
- Structured effective prompts must describe the language task, not embed mechanical execution. Machine checks belong to contracts, preflight, runners, and guards.
- LLM judge audit is auxiliary semantic analysis and must not automate final approval or override mechanical / human-only gates.
- Phase order is Phase 1 schema, Phase 0 selector implementation, then Phase 2 read-only registry, Phase 3 warning preflight, Phase 4 structured prompts, Phase 5 blocking guards, Phase 6 optional LLM judge audit.

### forbidden_actions

The upstream materials forbid or constrain:

- Treating source materials as path-only references when the review asks for vertical intent transfer.
- Letting LLMs infer operation side effects, approval requirements, return destinations, or complex-operation branches from conversation context.
- Treating `record_human_decision` completion as approval for an approval-required target operation.
- Letting proxy_model replace human-only decisions.
- Letting workflow-state snapshots become canonical state or a hidden state-mutation path.
- Reimplementing mechanical checks inside effective prompts instead of referencing machine-confirmed preconditions and contract / preflight outputs.
- Mixing phase-spanning intermediate implementation states into a single commit.
- Treating historical `spec.json.reopened` as the current active reopen scope.
- Confusing reopen scope with impact-review scope.

### unresolved_or_design_deferred_items

The upstream materials intentionally defer some details to design:

- Physical representation of complex operations: maximum side-effect representative value, list-valued `effect_kind`, or internal-step decomposition.
- The exact data structure tying `record_human_decision` to the approval target operation.
- The exact implementation path for workflow-state snapshot generation.
- The exact way D-003 scenarios become Phase 6 semantic-audit tests.
- Human-required predicate priority and conflict resolution for proxy_model applicability.
- Concrete command names / arguments for future operation runner behavior.

These deferred details should not be forced into requirements as final implementation design, but requirements should preserve enough constraints so design cannot silently choose an unsafe option.

### intended_target_phase_transfer

The intended requirements-level transfer is:

- Requirement 13 should capture operation contract vocabulary, the 19-action mapping, approval-required semantics, complex-operation constraints, single-source-of-truth boundary, read-only registry/preflight role, and fail-closed drift handling.
- Requirement 14 should capture approval gate semantics, explicit human-decision records, side-track stack safety, staged-file digest checks, workflow-state snapshots as non-canonical support, read-only versus mutating state operations, and proxy_model versus human-only boundaries.
- Requirement 15 should capture structured effective prompts as language-task specifications, machine-checkable prompt structure, separation from mechanical tasks, and LLM judge audit as non-approving auxiliary analysis.
- Requirement 16 should capture Phase 1 / Phase 0 / Phase 2-6 ordering, phase completion constraints, no cross-phase implementation mixing, active reopen scope versus historical flags, impact review scope, and proxy_model applicability predicates.

## Target Phase Artifact Excerpt

Requirement 13 currently covers operation contract vocabulary, `.reviewcompass/schema/` Phase 1 schemas, the 19 `required_action` mapping, approval-required simple actions, `record_human_decision`, `run_reopen_pending_gate`, complex operations, fail-closed pre/postconditions, and contract / registry / preflight source-of-truth boundaries.

Requirement 14 currently covers approval gates, side-track stack frames, staged file set / digest checks, side-track pop and max depth, workflow-state snapshots, proxy_model versus human-only decisions, and read-only versus mutating operation boundaries.

Requirement 15 currently covers structured effective prompt fields, `language_task`, separation from mechanical tasks, Phase 4 prompt generation, first-layer machine checks, Phase 6 LLM judge audit, and non-automation of semantic final approval.

Requirement 16 currently covers Phase 0 through Phase 6 ordering and completion, no phase-spanning intermediate state commits, active reopen scope versus historical reopened flags, impact review scope, proxy_model triage decision applicability predicates, and human-required precedence.

## Required Check

Independently analyze whether the upstream purpose, responsibility boundaries, acceptance criteria, forbidden actions, unresolved / design-deferred items, and intended target-phase transfer are inherited into Requirement 13-16 without omission, weakening, unsupported additions, or drift.

Do not assume the requirements are correct because they mention the upstream files. Judge the actual transfer.

## Out Of Scope

- Correctness of `design.md`
- Correctness or implementation-readiness of `tasks.md`
- Whether design/tasks already carry the requirements correctly
- Implementation code changes
- Commit, push, spec.json mutation, phase approval, or reopen movement

## Finding Policy

Return findings as YAML with a top-level `findings` list. Each finding must include:

- `severity`: CRITICAL, ERROR, WARN, or INFO
- `target_location`: file and section / requirement
- `description`: concrete issue
- `rationale`: why it matters
- `recommendation`: what should change

Use `ERROR` for omissions, weakened requirements, unsupported additions, or responsibility-boundary drift that make requirements unsafe to approve.
Use `WARN` for ambiguity or traceability weakness that should be fixed before downstream design/tasks review.
Use `INFO` only for non-blocking observations.

If there are no substantive findings, return `findings: []`.

## Sensitive Information Check

No API keys, access tokens, passwords, personal contact information, or non-public third-party confidential data are intentionally included in this review target.


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
.reviewcompass/specs/workflow-management/requirements.md

# Target document
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
11. 本機能は `next --json` の目標応答スキーマを `.reviewcompass/schema/next_action_response.schema.json` として JSON Schema 形式で定義する。本スキーマは受入9が定める振る舞い契約（唯一アクション選択・進行中作業単位の有無による null/非 null の切り替え）をスキーマとして表現する。（1）最上位の必須フィールドは `verdict`（文字列）・`exit_code`（整数）・`next_action`（オブジェクト）・`reasons`（配列）・`current_state`（オブジェクト）の5つとし、`verdict` は最上位だけに置き `next_action` 内には含めない。（2）`next_action` の最低限の必須フィールドは `kind`（文字列・`required_action` の分類子、値域は design で確定）・`required_action`（受入10のスキーマを参照）・`active_gate`（文字列または null）・`feature`（文字列または null）・`phase`（文字列または null）・`stage`（文字列または null）・`required_feature_scope`（配列）・`blocked_by`（オブジェクトまたは null）・`future_gates`（配列）・`state_refs`（オブジェクト）の10フィールドとする。これに加え、`repair_reasons`（配列）は `repair_workflow_state` 時に必須となる条件付きフィールド（非空配列・最低1要素）とし、`action_parameters`（オブジェクト）は `run_maintenance` のみを対象とする必須の条件付きフィールドとして定義する。6フィールド（`maintenance_action`・`allowed_scope`・`allowed_files`・`completion_conditions`・`active_stack_frame_id`・`parent_frame_id`）はすべて required とし、追加フィールドの許可・禁止は design で確定する。（3）`feature` はリスト型を許容せず、取り得る値は「単一フィーチャー名」・`"all_features"`（review-wave のような真に横断的な実行単位の場合のみ）・null（進行中の作業単位がない場合）の3種類に限る。複数フィーチャーが影響範囲に入る場合は `required_feature_scope` または `future_gates` に置く。（4）受入9の null/非 null 規則をスキーマで表現する。進行中の作業単位（active workflow unit）がない場合、`feature`・`phase`・`stage`・`active_gate` はすべて null とする。作業単位がある（reopen 第3過程または通常 workflow の gate 実行時）場合のみ、これらのフィールドは非 null とする。（5）後方互換のため `pending_gates`・`next_pending_gate` はオプションフィールドとして定義し、このスキーマの正本フィールドは `future_gates`・`active_gate` とする。これらの後方互換フィールドが存在する場合は対応する正本フィールドと一致させること（`next --json` の実装側の不変条件として要求する。JSON Schema での表現は design で確定する）。新規のコンシューマは正本フィールドのみを参照してよい。（6）`required_action` の値ごとにフィールドの値制約（相互排他）がある。以下は D-003 §4.2 で確定している制約であり、スキーマはこれらを機械的に検証できる構造で表現する（スキーマ上の表現方法は design で確定）。① `commit_stop_point` の時：`active_gate=null`・`phase=null`・`stage=null`・`blocked_by.type="commit_stop_point"`。② `run_reopen_pending_gate` の時：`active_gate` 非 null・`phase`/`stage` は `active_gate` と一致・`blocked_by=null`。③ `run_reopen_drafting` の時：`active_gate` は `stages/<phase>.yaml#drafting` 形式・`phase`/`stage` はその drafting 単位と一致。④ `repair_workflow_state` の時：`active_gate=null`・`phase=null`・`stage=null`・`repair_reasons` に修復理由を含める。⑤ `wait_for_human_decision` の時：`blocked_by.type` で停止理由を区別。⑥ `run_maintenance` の時：`action_parameters` に `maintenance_action`・`allowed_scope`・`allowed_files`・`completion_conditions`・`active_stack_frame_id`・`parent_frame_id` を含める。上記①〜⑥の制約は D-003 §4.2 で確定している制約の全てであり、これ以外の `required_action` 種別には確定した追加フィールド制約はない（universal 必須フィールドのみが適用される）。

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
5. 承認ゲートを必須とする単純操作は、最低限 `commit_stop_point`、`apply_approved_reopen_plan`、`run_reopen_start`、`advance_reopen_after_commit_stop_point`、`advance_reopen_after_approval_stop_point`、`finalize_reopen`、`repair_workflow_state` を含む。これらは `approval_required: true` として扱い、実行前に明示的な人間判断記録を必要とする。この列挙は複合操作の分岐条件を否定しない。`run_maintenance` は maintenance YAML または内部操作の承認要求に従い、`run_workflow_stage` は stage 種別に従う。
6. `record_human_decision` は承認対象操作ではなく、承認ゲートを構成する判断記録操作として扱う。`effect_kind` は判断記録を書き込む場合は `state_mutation` とし、`approval_required` は常に `false` とする。`record_human_decision` の完了だけでは、対象 operation の `approval_required: true` を満たしたことにしてはならない。
7. `run_reopen_pending_gate` は active gate 種別に応じて operation contract を分岐する。`triad-review` と `review-wave` は外部レビュー実行を伴う `external_call`、`alignment` は LLM が整合確認材料を生成する `write`、`approval` は承認要求を構造化する `state_mutation` として扱う。drafting は `run_reopen_drafting` として分離する。
8. `run_maintenance` と `run_workflow_stage` は、内部で実行する操作または stage 種別によって `effect_kind` と `approval_required` が変わる複合操作として扱う。複合操作を単一代表値、list 型、内部ステップ分解のいずれで表すかは design で確定するが、LLM が都度推測する形にはしない。design で確定するまでの最小規則として、複合操作は分岐条件、内部 step、各 step の `effect_kind`、最大副作用、承認要否の集約規則を持つものとして扱う。
9. 複合操作の schema 表現は Phase 1 の未確定事項として扱う。候補は、最大副作用の `effect_kind` を代表値として注記する、`effect_kind` を list 型にする、複合操作を単一 enum の内部ステップへ分解する、の3案を最低限保持する。また、`record_human_decision` が記録する判断と承認対象の `required_action` を、セッション識別子、タイムスタンプ、操作 ID、または同等の識別子で結びつける方法を design で確定する。
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
11. 承認ゲートは proxy_model が代行できる判断と、人間だけが承認できる判断を機械可読に区別する。少なくとも commit、push、spec.json 更新、phase approval、reopen finalize、approval_required な不可逆操作の実行許可は human-only decision として扱い、proxy_model decision だけで通過させてはならない。proxy_model は所見 triage や補助判断を代行できるが、human-only decision の承認主体を置換しない。
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



## .reviewcompass/specs/workflow-management/reviews/2026-06-19-workflow-management-requirements-vertical-redo-review-run-v2/proxy-decision-prompt.md

# Proxy Model Triage Decision Prompt

You are the proxy_model for a ReviewCompass requirements triad-review.

Your task is to independently judge the four findings from a corrected vertical intent-transfer review. Do not simply accept the draft triage proposal. Analyze whether each finding identifies:

- a blocking requirements problem that must be fixed before requirements triad-review can complete,
- a non-blocking requirements clarification that should be fixed before downstream design/tasks replay,
- or an observation that should be left unchanged.

You may disagree with the draft proposal. If the available labels are not a perfect fit, choose the closest workflow label and explain the mismatch in the rationale.

## Review Context

Review run: `2026-06-19-workflow-management-requirements-vertical-redo-review-run-v2`

The review target is `.reviewcompass/specs/workflow-management/requirements.md`, specifically Requirement 13 through Requirement 16 and directly related Change Intent / traceability text.

Downstream `design.md` and `tasks.md` correctness are out of scope. Implementation code, commit, push, spec mutation, phase approval, and reopen movement are out of scope.

## Upstream Intent Summary

The upstream purpose is to reduce dependence on LLM memory and implicit interpretation. `next --json` remains the selector that decides the single current action. Execution must be governed by machine-readable operation contracts, preflight checks, approval gates, side-track state, workflow-state snapshots, and structured language-task prompts.

For this reopen, Requirement 13-16 must restore upstream intent that was previously under-transferred into requirements. The prior result only added minimal Phase 1 schema points, while the upstream materials intended operation contract vocabulary, approval gates, side-track stack, workflow-state snapshot, structured effective prompts, and Phase 0-6 ordering to be requirements-visible.

Important upstream boundaries:

- `next --json` decides the current `required_action`; operation contracts do not replace it.
- operation contracts define execution details such as `effect_kind`, `approval_required`, sequence, preconditions, postconditions, pending conflicts, and fail-closed behavior.
- registry / preflight are read-only consumers or confirmations of the contract; they must not become independent sources of truth or consume approvals.
- `record_human_decision` records a decision but does not itself authorize an approval-required operation.
- proxy_model may triage findings, but cannot replace human-only decisions such as commit, push, spec updates, phase approval, reopen finalize, or approval-required irreversible operations.
- workflow-state snapshots are visualization / audit support, not canonical state.
- LLMs perform language tasks; mechanical checks, guards, preflight, and approval enforcement must not be left to implicit LLM judgment.

Important upstream acceptance intent:

- all 19 `required_action` terms must map to operation contract information, including `effect_kind`, execution actor, and `approval_required`;
- `approval_required` is independent from `effect_kind`;
- approval-required actions include at least `commit_stop_point`, `apply_approved_reopen_plan`, `run_reopen_start`, `advance_reopen_after_commit_stop_point`, `advance_reopen_after_approval_stop_point`, `finalize_reopen`, and `repair_workflow_state`;
- complex operations may vary by internal step or stage kind, but LLMs must not infer them ad hoc;
- side-track depth excess, scope drift, and commit mixing are warning-only in Phase 3 and mechanically blocked in Phase 5;
- structured effective prompts describe language tasks, while mechanical checks belong to contracts, preflight, runners, and guards;
- LLM judge audit is auxiliary and cannot automate final approval;
- phase order is Phase 1 schema, Phase 0 selector implementation, then Phase 2 read-only registry, Phase 3 warning preflight, Phase 4 structured prompts, Phase 5 blocking guards, and Phase 6 optional LLM judge audit.

Important unresolved / design-deferred items:

- representation of complex operations may be maximum side-effect representative, list-valued `effect_kind`, or internal-step decomposition;
- exact data structure tying `record_human_decision` to an approval target is design-deferred;
- human-required predicate priority and conflict resolution for proxy_model applicability are design-deferred.

Requirements should not force final design for these deferred details, but should preserve enough constraints that design cannot silently choose an unsafe option.

## Current Findings

### F1

finding_id: `2026-06-19-workflow-management-requirements-vertical-redo-review-run-v2-claude-opus-4-8-adversarial-001`

Original severity: ERROR

Target: Requirement 13 AC5

Finding summary: AC5 says approval-required operations need an explicit human decision record. Requirement 13 AC6 and Requirement 14 AC1 / AC3 state that `record_human_decision` completion is not approval, but AC5 itself does not locally cross-reference that boundary. The reviewer says this may allow a design-stage misread that `record_human_decision` existence alone satisfies approval.

Draft triage proposal: `should-fix`, because surrounding requirements already state the boundary, but a local cross-reference would reduce drift.

### F2

finding_id: `2026-06-19-workflow-management-requirements-vertical-redo-review-run-v2-claude-opus-4-8-adversarial-002`

Original severity: WARN

Target: Requirement 14 AC11

Finding summary: AC11 says proxy_model cannot replace human-only decisions, but does not cross-reference Requirement 16 AC13 / AC14 where proxy applicability predicates and priority are defined. The reviewer says the safety boundary is distributed and easier to misread downstream.

Draft triage proposal: `should-fix`.

### F3

finding_id: `2026-06-19-workflow-management-requirements-vertical-redo-review-run-v2-claude-opus-4-8-adversarial-003`

Original severity: WARN

Target: Requirement 13 AC8 / AC9 and Requirement 16 AC2 / AC4

Finding summary: AC8 defines minimum constraints for complex operations, while AC9 lists representation options. The reviewer says AC9 does not explicitly state that AC8's minimum constraints must survive whichever representation design chooses, so a representative-value design might silently lose branch conditions, maximum side effect, or approval aggregation rules.

Draft triage proposal: `should-fix`.

### F4

finding_id: `2026-06-19-workflow-management-requirements-vertical-redo-review-run-v2-claude-opus-4-8-adversarial-004`

Original severity: INFO

Target: Requirement 16 AC1 / AC3

Finding summary: This is a confirmation that Phase 1 -> Phase 0 dependency and Phase 0 completion criteria are transferred correctly. No omission was identified.

Draft triage proposal: `leave-as-is`.

## Decision Labels

Use these workflow labels:

- `must-fix`: the finding identifies a blocking requirements omission, weakening, unsupported addition, or responsibility-boundary drift that must be fixed before requirements triad-review can complete.
- `should-fix`: the finding identifies a non-blocking clarification or traceability improvement that should be fixed before downstream design/tasks replay.
- `leave-as-is`: the finding is already covered well enough, asks for design-level detail, is only a confirmation, or should not change the requirements.

## Required Output

Return only YAML with this exact top-level shape:

```yaml
proxy_model_id: gpt-5.5
decision_prompt_path: proxy-decision-prompt.md
raw_response_path: proxy-decision-response.yaml
decisions:
  - finding_id: <exact finding id>
    final_label: must-fix | should-fix | leave-as-is
    rationale: <specific reason>
    rejected_options:
      must-fix: <why not selected>
      should-fix: <why not selected>
      leave-as-is: <why not selected>
```

For every finding, include all three `rejected_options` keys except the selected label may say `selected`.

Do not include prose outside YAML.

YAML formatting rule: write every `rationale` value and every `rejected_options` value as a block scalar (`|-`). Do not put colons inside plain unquoted scalar values.

## Sensitive Information Check

No API keys, access tokens, passwords, personal contact information, or non-public third-party confidential data are intentionally included in this prompt.


## .reviewcompass/specs/workflow-management/reviews/2026-06-19-workflow-management-requirements-vertical-redo-review-run-v2/raw-review-triage-summary.md

# Raw Review Triage Summary

review_run_id: `2026-06-19-workflow-management-requirements-vertical-redo-review-run-v2`
variant: `implementation_review_independent_3way_codex_operator`
phase: requirements
gate: `stages/requirements.yaml#triad-review`
triage_status: decided_by_proxy_model
prompt_preflight: passed
decision_actor: `proxy_model`
proxy_model: `openai-api / gpt-5.5`

## Role Assignments

| role | path | provider | model | raw | parse |
|---|---|---|---|---|---|
| primary | api | openai-api | gpt-5.4 | `raw/gpt-5.4.round-1.txt` | parsed |
| adversarial | api | anthropic-api | claude-opus-4-8 | `raw/claude-opus-4-8.round-1.txt` | parsed |
| judgment | api | gemini-api | gemini-3.1-pro-preview | `raw/gemini-3.1-pro-preview.round-1.txt` | parsed |

## Model Result Summary

- `gpt-5.4`: `findings: []`
- `claude-opus-4-8`: 4 findings（ERROR 1、WARN 2、INFO 1）
- `gemini-3.1-pro-preview`: `findings: []`

## Same-Root Finding Clusters

### C1: Requirement 13 approval record wording

- source finding: `2026-06-19-workflow-management-requirements-vertical-redo-review-run-v2-claude-opus-4-8-adversarial-001`
- severity: ERROR
- target: `requirements.md` Requirement 13 AC5
- summary: AC5 says approval-required operations need an explicit human decision record, but does not locally cross-reference that `record_human_decision` completion is not itself approval.
- same-root status: single-model only. GPT and Gemini did not report the issue.
- final label: `should-fix`
- proxy_model rationale: The surrounding AC6 and Requirement 14 AC1/AC3 already state the boundary, so this is not blocking, but AC5 should add a local cross-reference to reduce downstream drift.
- applied: Requirement 13 AC5 now states that the human decision record is part of Requirement 13 AC6 / Requirement 14 AC1-AC3 approval gate handling, and that `record_human_decision` completion alone must not count as approval.

### C2: Requirement 14 / 16 proxy boundary cross-reference

- source finding: `2026-06-19-workflow-management-requirements-vertical-redo-review-run-v2-claude-opus-4-8-adversarial-002`
- severity: WARN
- target: `requirements.md` Requirement 14 AC11
- summary: Requirement 14 states proxy_model cannot replace human-only decisions, but does not cross-reference Requirement 16 AC13/AC14 where proxy applicability predicates and priority are defined.
- same-root status: single-model only. GPT and Gemini did not report the issue.
- final label: `should-fix`
- proxy_model rationale: The safety rule exists, but Requirement 14 AC11 should cross-reference Requirement 16 AC13-AC14 to preserve proxy/human-only predicate traceability.
- applied: Requirement 14 AC11 now explicitly requires proxy_model applicability and human-required priority to align with Requirement 16 AC13-AC14.

### C3: Requirement 13 complex-operation minimum rule

- source finding: `2026-06-19-workflow-management-requirements-vertical-redo-review-run-v2-claude-opus-4-8-adversarial-003`
- severity: WARN
- target: `requirements.md` Requirement 13 AC8 / AC9 and Requirement 16 AC2 / AC4
- summary: AC8 defines minimum constraints for complex operations, and AC9 lists representation options, but it does not explicitly say AC8's minimum constraints must survive whichever representation design chooses.
- same-root status: single-model only. GPT and Gemini did not report the issue.
- final label: `should-fix`
- proxy_model rationale: AC8 contains the minimum constraints, but Requirement 13 should explicitly state AC9 representation options remain constrained by AC8 to avoid unsafe design drift.
- applied: Requirement 13 AC9 now states that every representation option must preserve AC8 minimum constraints.

### C4: Phase 1 / Phase 0 ordering confirmation

- source finding: `2026-06-19-workflow-management-requirements-vertical-redo-review-run-v2-claude-opus-4-8-adversarial-004`
- severity: INFO
- target: `requirements.md` Requirement 16 AC1 / AC3
- summary: Claude confirms Phase 1 -> Phase 0 dependency and Phase 0 completion criteria are transferred correctly.
- same-root status: confirmation only.
- final label: `leave-as-is`
- proxy_model rationale: Positive confirmation of Phase 1 to Phase 0 transfer; no requirements change needed.

## Final Three-Level Triage

| cluster | finding ids | final label | reason |
|---|---|---|---|
| C1 | `...-claude-opus-4-8-adversarial-001` | should-fix | Strengthen local wording / cross-reference, but surrounding requirements already state the boundary |
| C2 | `...-claude-opus-4-8-adversarial-002` | should-fix | Add cross-reference between Requirement 14 and Requirement 16 proxy/human-only predicate rules |
| C3 | `...-claude-opus-4-8-adversarial-003` | should-fix | Preserve AC8 minimum constraints across AC9 design representation options |
| C4 | `...-claude-opus-4-8-adversarial-004` | leave-as-is | Confirmation only |

## Resolution

The user approved using API `gpt-5.5` as `proxy_model`. The proxy decision is recorded in `proxy-decision-decisions.yaml`, `proxy-decision-metadata.yaml`, `proxy-approval.yaml`, and `triage.yaml`. The `should-fix` decisions for C1-C3 have been applied to `requirements.md`; C4 was left unchanged.


## .reviewcompass/specs/workflow-management/reviews/2026-06-19-workflow-management-requirements-vertical-redo-review-run-v2/review-target.md

# Requirements Vertical Intent Review Target: Workflow Management Requirement 13-16

## Review Target

Review the vertical intent transfer into `.reviewcompass/specs/workflow-management/requirements.md`, specifically Requirement 13 through Requirement 16 and their directly related Change Intent / traceability text.

The target phase artifact is `requirements.md`. The review question is not whether downstream `design.md` or `tasks.md` are correct.

## Source Materials

These source materials were read and summarized below. They are not path-only references.

- `docs/reviews/reopen-classification-2026-06-19-wm-requirement-13-16-vertical-redo.md`
- `docs/notes/2026-06-18-integrated-design-selection-execution-layers.md`
- `docs/notes/working/2026-06-18-mechanized-workflow-execution-design.md`
- `docs/notes/working/2026-06-19-integrated-design-requirements-missing.md`
- `docs/operations/SESSION_WORKFLOW_GUIDE.md#vertical-intent-transfer-review`

## Upstream Structured Summary

### purpose

The upstream purpose is to make workflow execution less dependent on LLM memory or implicit interpretation. `next --json` remains the selector that decides what should happen next; execution must be governed by machine-readable operation contracts, preflight checks, approval gates, side-track state, workflow-state snapshots, and structured language-task prompts.

For this reopen, the purpose is narrower: restore the integrated design intent that was previously under-transferred into requirements. The 2026-06-18 request was to incorporate the two integrated design notes into intent / requirements and then proceed through the workflow. The prior result only added the minimal Phase 1 schema points, so Requirement 13-16 now need to carry the larger upstream intent.

### responsibility_boundaries

- Selection layer boundary: `next --json` chooses the single current `required_action`; it is not replaced by operation contracts or workflow-state snapshots.
- Execution layer boundary: operation contracts define how an action is executed, including `effect_kind`, `approval_required`, sequence, preconditions, postconditions, pending conflicts, and fail-closed behavior.
- Registry / preflight boundary: registry and preflight are read-only consumers / confirmations of the contract. They must not become independent sources of truth, execute operations, update state, or consume approvals.
- Human decision boundary: `record_human_decision` records a decision but does not itself authorize an approval-required operation. Commit, push, spec updates, phase approval, reopen finalize, and approval-required irreversible operations remain human-only.
- LLM boundary: LLMs perform language tasks such as drafting, triage explanation, and semantic audit. Mechanical checks, guards, preflight, and approval enforcement must not be left to implicit LLM judgment.
- Snapshot boundary: workflow-state snapshots are visualization / audit support and must not replace `next --json` or state refs.

### acceptance_criteria

Upstream acceptance intent includes:

- The 19 `required_action` terms must map to operation contract information, including `effect_kind`, execution actor, and `approval_required`.
- `approval_required` is independent from `effect_kind`; some `state_mutation` operations are approval-required and some are not.
- Approval-required actions include at least `commit_stop_point`, `apply_approved_reopen_plan`, `run_reopen_start`, `advance_reopen_after_commit_stop_point`, `advance_reopen_after_approval_stop_point`, `finalize_reopen`, and `repair_workflow_state`.
- `record_human_decision` is a decision-recording operation and a component of the approval gate; its completion must not be treated as approval for the target operation.
- `run_reopen_pending_gate` branches by gate kind: `triad-review` / `review-wave` are external API review runs, `alignment` is a write language task, `approval` structures an approval request, and drafting is separated.
- Complex actions such as `run_maintenance`, `run_reopen_pending_gate`, and `run_workflow_stage` may vary by internal step or stage kind; their representation is a design decision, but LLMs must not infer it ad hoc.
- Side track frames need `allowed_scope`, `allowed_files`, `return_to`, `staged_file_digest`, and `staged_file_set`; only the top frame can be popped, and `next --json` resumes the next state.
- Side-track depth excess, scope drift, and commit mixing are initially warning-only in Phase 3 and mechanically blocked in Phase 5.
- Structured effective prompts must describe the language task, not embed mechanical execution. Machine checks belong to contracts, preflight, runners, and guards.
- LLM judge audit is auxiliary semantic analysis and must not automate final approval or override mechanical / human-only gates.
- Phase order is Phase 1 schema, Phase 0 selector implementation, then Phase 2 read-only registry, Phase 3 warning preflight, Phase 4 structured prompts, Phase 5 blocking guards, Phase 6 optional LLM judge audit.

### forbidden_actions

The upstream materials forbid or constrain:

- Treating source materials as path-only references when the review asks for vertical intent transfer.
- Letting LLMs infer operation side effects, approval requirements, return destinations, or complex-operation branches from conversation context.
- Treating `record_human_decision` completion as approval for an approval-required target operation.
- Letting proxy_model replace human-only decisions.
- Letting workflow-state snapshots become canonical state or a hidden state-mutation path.
- Reimplementing mechanical checks inside effective prompts instead of referencing machine-confirmed preconditions and contract / preflight outputs.
- Mixing phase-spanning intermediate implementation states into a single commit.
- Treating historical `spec.json.reopened` as the current active reopen scope.
- Confusing reopen scope with impact-review scope.

### unresolved_or_design_deferred_items

The upstream materials intentionally defer some details to design:

- Physical representation of complex operations: maximum side-effect representative value, list-valued `effect_kind`, or internal-step decomposition.
- The exact data structure tying `record_human_decision` to the approval target operation.
- The exact implementation path for workflow-state snapshot generation.
- The exact way D-003 scenarios become Phase 6 semantic-audit tests.
- Human-required predicate priority and conflict resolution for proxy_model applicability.
- Concrete command names / arguments for future operation runner behavior.

These deferred details should not be forced into requirements as final implementation design, but requirements should preserve enough constraints so design cannot silently choose an unsafe option.

### intended_target_phase_transfer

The intended requirements-level transfer is:

- Requirement 13 should capture operation contract vocabulary, the 19-action mapping, approval-required semantics, complex-operation constraints, single-source-of-truth boundary, read-only registry/preflight role, and fail-closed drift handling.
- Requirement 14 should capture approval gate semantics, explicit human-decision records, side-track stack safety, staged-file digest checks, workflow-state snapshots as non-canonical support, read-only versus mutating state operations, and proxy_model versus human-only boundaries.
- Requirement 15 should capture structured effective prompts as language-task specifications, machine-checkable prompt structure, separation from mechanical tasks, and LLM judge audit as non-approving auxiliary analysis.
- Requirement 16 should capture Phase 1 / Phase 0 / Phase 2-6 ordering, phase completion constraints, no cross-phase implementation mixing, active reopen scope versus historical flags, impact review scope, and proxy_model applicability predicates.

## Target Phase Artifact Excerpt

Requirement 13 currently covers operation contract vocabulary, `.reviewcompass/schema/` Phase 1 schemas, the 19 `required_action` mapping, approval-required simple actions, `record_human_decision`, `run_reopen_pending_gate`, complex operations, fail-closed pre/postconditions, and contract / registry / preflight source-of-truth boundaries.

Requirement 14 currently covers approval gates, side-track stack frames, staged file set / digest checks, side-track pop and max depth, workflow-state snapshots, proxy_model versus human-only decisions, and read-only versus mutating operation boundaries.

Requirement 15 currently covers structured effective prompt fields, `language_task`, separation from mechanical tasks, Phase 4 prompt generation, first-layer machine checks, Phase 6 LLM judge audit, and non-automation of semantic final approval.

Requirement 16 currently covers Phase 0 through Phase 6 ordering and completion, no phase-spanning intermediate state commits, active reopen scope versus historical reopened flags, impact review scope, proxy_model triage decision applicability predicates, and human-required precedence.

## Required Check

Independently analyze whether the upstream purpose, responsibility boundaries, acceptance criteria, forbidden actions, unresolved / design-deferred items, and intended target-phase transfer are inherited into Requirement 13-16 without omission, weakening, unsupported additions, or drift.

Do not assume the requirements are correct because they mention the upstream files. Judge the actual transfer.

## Out Of Scope

- Correctness of `design.md`
- Correctness or implementation-readiness of `tasks.md`
- Whether design/tasks already carry the requirements correctly
- Implementation code changes
- Commit, push, spec.json mutation, phase approval, or reopen movement

## Finding Policy

Return findings as YAML with a top-level `findings` list. Each finding must include:

- `severity`: CRITICAL, ERROR, WARN, or INFO
- `target_location`: file and section / requirement
- `description`: concrete issue
- `rationale`: why it matters
- `recommendation`: what should change

Use `ERROR` for omissions, weakened requirements, unsupported additions, or responsibility-boundary drift that make requirements unsafe to approve.
Use `WARN` for ambiguity or traceability weakness that should be fixed before downstream design/tasks review.
Use `INFO` only for non-blocking observations.

If there are no substantive findings, return `findings: []`.

## Sensitive Information Check

No API keys, access tokens, passwords, personal contact information, or non-public third-party confidential data are intentionally included in this review target.


## .reviewcompass/specs/workflow-management/reviews/2026-06-19-workflow-management-requirements-vertical-redo-review-run-v2/review_summary.md

# Review run summary: 2026-06-19-workflow-management-requirements-vertical-redo-review-run-v2

variant: implementation_review_independent_3way_codex_operator

## Role assignments

| role | path | provider | model |
| --- | --- | --- | --- |
| primary | api | openai-api | gpt-5.4 |
| adversarial | api | anthropic-api | claude-opus-4-8 |
| judgment | api | gemini-api | gemini-3.1-pro-preview |

## Model results

| model_id | parse_status | triage_status | findings | severity | raw |
| --- | --- | --- | ---: | --- | --- |
| gpt-5.4 | parsed | no_findings | 0 | - | raw/gpt-5.4.round-1.txt |
| claude-opus-4-8 | parsed | triage_pending | 4 | ERROR:1, INFO:1, WARN:2 | raw/claude-opus-4-8.round-1.txt |
| gemini-3.1-pro-preview | parsed | no_findings | 0 | - | raw/gemini-3.1-pro-preview.round-1.txt |

## Next steps

1. Read raw responses for any parse_failed or triage_pending model.
2. Move finding-level judgments into triage.yaml.
3. Present the variant, role assignments, raw/model summary, same-root clusters, and three-level triage to the user.
4. Stop at the 利用者提示ゲート before asking proxy_model, editing implementation, updating spec.json, or moving phases.
5. Resolve human_required items before treating the run as complete.


## .reviewcompass/specs/workflow-management/reviews/2026-06-19-workflow-management-requirements-vertical-redo-review-run-v2/user-visible-triage-gate.md

# User Visible Triage Gate

status: resolved_by_proxy_model
review_run_id: 2026-06-19-workflow-management-requirements-vertical-redo-review-run-v2

## Presented Materials

- `review_summary.md`
- `variant-role-assignment.yaml`
- `raw-review-triage-summary.md`
- `triage.yaml`

## Current Proposed Triage

- C1: should-fix
- C2: should-fix
- C3: should-fix
- C4: leave-as-is

## Proxy Model Resolution

- proxy_model: `openai-api / gpt-5.5`
- variant: `proxy_model_openai_gpt_55`
- decision prompt: `proxy-decision-prompt.md`
- raw response: `proxy-decision-response.yaml`
- parsed decisions: `proxy-decision-decisions.yaml`
- approval record: `proxy-approval.yaml`

Final labels:

- C1: `should-fix`
- C2: `should-fix`
- C3: `should-fix`
- C4: `leave-as-is`

## Stop Rule

The proxy_model gate is resolved. Do not mutate `spec.json`, advance `stages/in-progress/reopen-procedure-2026-06-19.yaml`, or move the phase until the `should-fix` items are applied or explicitly left unresolved by a later decision.


## .reviewcompass/specs/workflow-management/reviews/2026-06-19-workflow-management-requirements-vertical-redo-review-run/invalidation.md

# Review Run Invalidation

status: invalid_for_vertical_intent_transfer_review
date: 2026-06-19
invalidated_by: Codex session user correction

## Scope

This review-run must not be used as the formal requirements triad-review evidence for the Requirement 13-16 vertical redo.

It may be retained only as evidence of the failed review-prompt construction pattern.

## Reason

The generated model prompts included `.reviewcompass/specs/workflow-management/requirements.md` as the target document, but the upstream decision materials were included only as path references.

That is insufficient for a vertical intent-transfer review. The models could not directly inspect the upstream purpose, responsibility boundaries, acceptance criteria, forbidden actions, unresolved items, or intended transfer decisions from:

- `docs/reviews/reopen-classification-2026-06-19-wm-requirement-13-16-vertical-redo.md`
- `docs/notes/2026-06-18-integrated-design-selection-execution-layers.md`
- `docs/notes/working/2026-06-18-mechanized-workflow-execution-design.md`
- `docs/notes/working/2026-06-19-integrated-design-requirements-missing.md`
- `docs/operations/SESSION_WORKFLOW_GUIDE.md#vertical-intent-transfer-review`

As a result, findings in this run are not valid evidence that upstream intent was or was not correctly inherited into Requirement 13-16. They may still be read as informal requirements-only observations.

## Invalidated Artifacts

- `review-target.md`
- `prompts/*.prompt.md`
- `raw/*.txt`
- `parsed/*.yaml`
- `rounds.yaml`
- `model-result-summary.yaml`
- `triage.yaml`
- `review_summary.md`
- `proxy-decision-prompt.md`

## Corrective Discipline

The discipline has been updated so that future vertical intent-transfer review prompts must not list source materials only by path. They must materialize the upstream content as excerpts or structured summaries that include purpose, responsibility boundaries, acceptance criteria, forbidden actions, unresolved or design-deferred items, and the intended transfer into the target phase.


## .reviewcompass/specs/workflow-management/reviews/2026-06-19-workflow-management-requirements-vertical-redo-review-run/prompts/claude-opus-4-8.round-1.prompt.md

prompt_id: anthropic_review
provider: anthropic-api
model_id: claude-opus-4-8

# Task
Review the target document for the requested phase and criteria.

# Phase
triad-review

# Criteria
# Requirements Triad Review Target: Workflow Management Requirement 13-16 Vertical Redo

## Review Target

This review judges only `.reviewcompass/specs/workflow-management/requirements.md`, specifically Requirement 13 through Requirement 16 and the directly related change intent / traceability text.

Do not judge `design.md` or `tasks.md` as review targets in this run. They may be mentioned only as downstream context if needed to detect unsupported requirements-level additions or missing requirements-level intent.

## Source Materials

Use these source materials as upstream decision materials for intent-transfer analysis:

- `docs/reviews/reopen-classification-2026-06-19-wm-requirement-13-16-vertical-redo.md`
- `docs/notes/2026-06-18-integrated-design-selection-execution-layers.md`
- `docs/notes/working/2026-06-18-mechanized-workflow-execution-design.md`
- `docs/notes/working/2026-06-19-integrated-design-requirements-missing.md`
- `docs/operations/SESSION_WORKFLOW_GUIDE.md#vertical-intent-transfer-review`

## Required Check

Independently review whether the upstream decision materials' purpose, responsibility boundaries, acceptance criteria, and forbidden actions have been inherited into Requirement 13 through Requirement 16 without omission, weakening, unsupported additions, or drift.

Pay particular attention to:

- Requirement 13: operation contract vocabulary, required_action mapping, single source of truth boundary between operation contracts and registry/preflight, read-only confirmation boundary, and fail-closed treatment for missing or stale contract references.
- Requirement 14: approval gate semantics, side track stack, workflow-state snapshot, read-only versus mutating operations, and proxy_model versus human-only decision boundaries.
- Requirement 15: structured effective prompt as a language-task specification, separation from mechanical tasks, machine-checkable prompt audit, and LLM judge audit as non-approving auxiliary analysis.
- Requirement 16: Phase 0 through Phase 6 ordering, phase completion conditions, no cross-phase implementation mixing, active reopen scope versus historical reopened flags, impact review scope, and proxy_model triage decision applicability predicates.

## Finding Policy

Return findings as YAML with a top-level `findings` list. Each finding must include:

- `severity`: CRITICAL, ERROR, WARN, or INFO
- `target_location`: file and section/requirement
- `description`: concrete issue
- `rationale`: why it matters
- `recommendation`: what should change

Use `ERROR` for omissions, weakened requirements, unsupported additions, or boundary drift that could make the requirements phase unsafe to approve.
Use `WARN` for ambiguity or traceability weakness that should be fixed before downstream design/tasks review if it affects later implementation readiness.
Use `INFO` only for non-blocking observations.

If there are no substantive findings, return `findings: []`.

## Out Of Scope

- Correctness of `design.md`
- Correctness or implementation-readiness of `tasks.md`
- Whether design/tasks already carry the requirements correctly
- Implementation code changes
- Commit, push, spec.json phase movement, or approval decisions

## Sensitive Information Check

No API keys, access tokens, passwords, personal contact information, or non-public third-party confidential data are intentionally included in this review target.


# Output contract
Return YAML only.
The top-level key must be exactly findings.
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
.reviewcompass/specs/workflow-management/requirements.md

# Target document
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
11. 本機能は `next --json` の目標応答スキーマを `.reviewcompass/schema/next_action_response.schema.json` として JSON Schema 形式で定義する。本スキーマは受入9が定める振る舞い契約（唯一アクション選択・進行中作業単位の有無による null/非 null の切り替え）をスキーマとして表現する。（1）最上位の必須フィールドは `verdict`（文字列）・`exit_code`（整数）・`next_action`（オブジェクト）・`reasons`（配列）・`current_state`（オブジェクト）の5つとし、`verdict` は最上位だけに置き `next_action` 内には含めない。（2）`next_action` の最低限の必須フィールドは `kind`（文字列・`required_action` の分類子、値域は design で確定）・`required_action`（受入10のスキーマを参照）・`active_gate`（文字列または null）・`feature`（文字列または null）・`phase`（文字列または null）・`stage`（文字列または null）・`required_feature_scope`（配列）・`blocked_by`（オブジェクトまたは null）・`future_gates`（配列）・`state_refs`（オブジェクト）の10フィールドとする。これに加え、`repair_reasons`（配列）は `repair_workflow_state` 時に必須となる条件付きフィールド（非空配列・最低1要素）とし、`action_parameters`（オブジェクト）は `run_maintenance` のみを対象とする必須の条件付きフィールドとして定義する。6フィールド（`maintenance_action`・`allowed_scope`・`allowed_files`・`completion_conditions`・`active_stack_frame_id`・`parent_frame_id`）はすべて required とし、追加フィールドの許可・禁止は design で確定する。（3）`feature` はリスト型を許容せず、取り得る値は「単一フィーチャー名」・`"all_features"`（review-wave のような真に横断的な実行単位の場合のみ）・null（進行中の作業単位がない場合）の3種類に限る。複数フィーチャーが影響範囲に入る場合は `required_feature_scope` または `future_gates` に置く。（4）受入9の null/非 null 規則をスキーマで表現する。進行中の作業単位（active workflow unit）がない場合、`feature`・`phase`・`stage`・`active_gate` はすべて null とする。作業単位がある（reopen 第3過程または通常 workflow の gate 実行時）場合のみ、これらのフィールドは非 null とする。（5）後方互換のため `pending_gates`・`next_pending_gate` はオプションフィールドとして定義し、このスキーマの正本フィールドは `future_gates`・`active_gate` とする。これらの後方互換フィールドが存在する場合は対応する正本フィールドと一致させること（`next --json` の実装側の不変条件として要求する。JSON Schema での表現は design で確定する）。新規のコンシューマは正本フィールドのみを参照してよい。（6）`required_action` の値ごとにフィールドの値制約（相互排他）がある。以下は D-003 §4.2 で確定している制約であり、スキーマはこれらを機械的に検証できる構造で表現する（スキーマ上の表現方法は design で確定）。① `commit_stop_point` の時：`active_gate=null`・`phase=null`・`stage=null`・`blocked_by.type="commit_stop_point"`。② `run_reopen_pending_gate` の時：`active_gate` 非 null・`phase`/`stage` は `active_gate` と一致・`blocked_by=null`。③ `run_reopen_drafting` の時：`active_gate` は `stages/<phase>.yaml#drafting` 形式・`phase`/`stage` はその drafting 単位と一致。④ `repair_workflow_state` の時：`active_gate=null`・`phase=null`・`stage=null`・`repair_reasons` に修復理由を含める。⑤ `wait_for_human_decision` の時：`blocked_by.type` で停止理由を区別。⑥ `run_maintenance` の時：`action_parameters` に `maintenance_action`・`allowed_scope`・`allowed_files`・`completion_conditions`・`active_stack_frame_id`・`parent_frame_id` を含める。上記①〜⑥の制約は D-003 §4.2 で確定している制約の全てであり、これ以外の `required_action` 種別には確定した追加フィールド制約はない（universal 必須フィールドのみが適用される）。

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
5. 承認ゲートを必須とする単純操作は、最低限 `commit_stop_point`、`apply_approved_reopen_plan`、`run_reopen_start`、`advance_reopen_after_commit_stop_point`、`advance_reopen_after_approval_stop_point`、`finalize_reopen`、`repair_workflow_state` を含む。これらは `approval_required: true` として扱い、実行前に明示的な人間判断記録を必要とする。この列挙は複合操作の分岐条件を否定しない。`run_maintenance` は maintenance YAML または内部操作の承認要求に従い、`run_workflow_stage` は stage 種別に従う。
6. `record_human_decision` は承認対象操作ではなく、承認ゲートを構成する判断記録操作として扱う。`effect_kind` は判断記録を書き込む場合は `state_mutation` とし、`approval_required` は常に `false` とする。`record_human_decision` の完了だけでは、対象 operation の `approval_required: true` を満たしたことにしてはならない。
7. `run_reopen_pending_gate` は active gate 種別に応じて operation contract を分岐する。`triad-review` と `review-wave` は外部レビュー実行を伴う `external_call`、`alignment` は LLM が整合確認材料を生成する `write`、`approval` は承認要求を構造化する `state_mutation` として扱う。drafting は `run_reopen_drafting` として分離する。
8. `run_maintenance` と `run_workflow_stage` は、内部で実行する操作または stage 種別によって `effect_kind` と `approval_required` が変わる複合操作として扱う。複合操作を単一代表値、list 型、内部ステップ分解のいずれで表すかは design で確定するが、LLM が都度推測する形にはしない。design で確定するまでの最小規則として、複合操作は分岐条件、内部 step、各 step の `effect_kind`、最大副作用、承認要否の集約規則を持つものとして扱う。
9. 複合操作の schema 表現は Phase 1 の未確定事項として扱う。候補は、最大副作用の `effect_kind` を代表値として注記する、`effect_kind` を list 型にする、複合操作を単一 enum の内部ステップへ分解する、の3案を最低限保持する。また、`record_human_decision` が記録する判断と承認対象の `required_action` を、セッション識別子、タイムスタンプ、操作 ID、または同等の識別子で結びつける方法を design で確定する。
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
11. 承認ゲートは proxy_model が代行できる判断と、人間だけが承認できる判断を機械可読に区別する。少なくとも commit、push、spec.json 更新、phase approval、reopen finalize、approval_required な不可逆操作の実行許可は human-only decision として扱い、proxy_model decision だけで通過させてはならない。proxy_model は所見 triage や補助判断を代行できるが、human-only decision の承認主体を置換しない。
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



## .reviewcompass/specs/workflow-management/reviews/2026-06-19-workflow-management-requirements-vertical-redo-review-run/prompts/gemini-3.1-pro-preview.round-1.prompt.md

prompt_id: gemini_review
provider: gemini-api
model_id: gemini-3.1-pro-preview

# Task
Review the target document for the requested phase and criteria.

# Phase
triad-review

# Criteria
# Requirements Triad Review Target: Workflow Management Requirement 13-16 Vertical Redo

## Review Target

This review judges only `.reviewcompass/specs/workflow-management/requirements.md`, specifically Requirement 13 through Requirement 16 and the directly related change intent / traceability text.

Do not judge `design.md` or `tasks.md` as review targets in this run. They may be mentioned only as downstream context if needed to detect unsupported requirements-level additions or missing requirements-level intent.

## Source Materials

Use these source materials as upstream decision materials for intent-transfer analysis:

- `docs/reviews/reopen-classification-2026-06-19-wm-requirement-13-16-vertical-redo.md`
- `docs/notes/2026-06-18-integrated-design-selection-execution-layers.md`
- `docs/notes/working/2026-06-18-mechanized-workflow-execution-design.md`
- `docs/notes/working/2026-06-19-integrated-design-requirements-missing.md`
- `docs/operations/SESSION_WORKFLOW_GUIDE.md#vertical-intent-transfer-review`

## Required Check

Independently review whether the upstream decision materials' purpose, responsibility boundaries, acceptance criteria, and forbidden actions have been inherited into Requirement 13 through Requirement 16 without omission, weakening, unsupported additions, or drift.

Pay particular attention to:

- Requirement 13: operation contract vocabulary, required_action mapping, single source of truth boundary between operation contracts and registry/preflight, read-only confirmation boundary, and fail-closed treatment for missing or stale contract references.
- Requirement 14: approval gate semantics, side track stack, workflow-state snapshot, read-only versus mutating operations, and proxy_model versus human-only decision boundaries.
- Requirement 15: structured effective prompt as a language-task specification, separation from mechanical tasks, machine-checkable prompt audit, and LLM judge audit as non-approving auxiliary analysis.
- Requirement 16: Phase 0 through Phase 6 ordering, phase completion conditions, no cross-phase implementation mixing, active reopen scope versus historical reopened flags, impact review scope, and proxy_model triage decision applicability predicates.

## Finding Policy

Return findings as YAML with a top-level `findings` list. Each finding must include:

- `severity`: CRITICAL, ERROR, WARN, or INFO
- `target_location`: file and section/requirement
- `description`: concrete issue
- `rationale`: why it matters
- `recommendation`: what should change

Use `ERROR` for omissions, weakened requirements, unsupported additions, or boundary drift that could make the requirements phase unsafe to approve.
Use `WARN` for ambiguity or traceability weakness that should be fixed before downstream design/tasks review if it affects later implementation readiness.
Use `INFO` only for non-blocking observations.

If there are no substantive findings, return `findings: []`.

## Out Of Scope

- Correctness of `design.md`
- Correctness or implementation-readiness of `tasks.md`
- Whether design/tasks already carry the requirements correctly
- Implementation code changes
- Commit, push, spec.json phase movement, or approval decisions

## Sensitive Information Check

No API keys, access tokens, passwords, personal contact information, or non-public third-party confidential data are intentionally included in this review target.


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
.reviewcompass/specs/workflow-management/requirements.md

# Target document
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
11. 本機能は `next --json` の目標応答スキーマを `.reviewcompass/schema/next_action_response.schema.json` として JSON Schema 形式で定義する。本スキーマは受入9が定める振る舞い契約（唯一アクション選択・進行中作業単位の有無による null/非 null の切り替え）をスキーマとして表現する。（1）最上位の必須フィールドは `verdict`（文字列）・`exit_code`（整数）・`next_action`（オブジェクト）・`reasons`（配列）・`current_state`（オブジェクト）の5つとし、`verdict` は最上位だけに置き `next_action` 内には含めない。（2）`next_action` の最低限の必須フィールドは `kind`（文字列・`required_action` の分類子、値域は design で確定）・`required_action`（受入10のスキーマを参照）・`active_gate`（文字列または null）・`feature`（文字列または null）・`phase`（文字列または null）・`stage`（文字列または null）・`required_feature_scope`（配列）・`blocked_by`（オブジェクトまたは null）・`future_gates`（配列）・`state_refs`（オブジェクト）の10フィールドとする。これに加え、`repair_reasons`（配列）は `repair_workflow_state` 時に必須となる条件付きフィールド（非空配列・最低1要素）とし、`action_parameters`（オブジェクト）は `run_maintenance` のみを対象とする必須の条件付きフィールドとして定義する。6フィールド（`maintenance_action`・`allowed_scope`・`allowed_files`・`completion_conditions`・`active_stack_frame_id`・`parent_frame_id`）はすべて required とし、追加フィールドの許可・禁止は design で確定する。（3）`feature` はリスト型を許容せず、取り得る値は「単一フィーチャー名」・`"all_features"`（review-wave のような真に横断的な実行単位の場合のみ）・null（進行中の作業単位がない場合）の3種類に限る。複数フィーチャーが影響範囲に入る場合は `required_feature_scope` または `future_gates` に置く。（4）受入9の null/非 null 規則をスキーマで表現する。進行中の作業単位（active workflow unit）がない場合、`feature`・`phase`・`stage`・`active_gate` はすべて null とする。作業単位がある（reopen 第3過程または通常 workflow の gate 実行時）場合のみ、これらのフィールドは非 null とする。（5）後方互換のため `pending_gates`・`next_pending_gate` はオプションフィールドとして定義し、このスキーマの正本フィールドは `future_gates`・`active_gate` とする。これらの後方互換フィールドが存在する場合は対応する正本フィールドと一致させること（`next --json` の実装側の不変条件として要求する。JSON Schema での表現は design で確定する）。新規のコンシューマは正本フィールドのみを参照してよい。（6）`required_action` の値ごとにフィールドの値制約（相互排他）がある。以下は D-003 §4.2 で確定している制約であり、スキーマはこれらを機械的に検証できる構造で表現する（スキーマ上の表現方法は design で確定）。① `commit_stop_point` の時：`active_gate=null`・`phase=null`・`stage=null`・`blocked_by.type="commit_stop_point"`。② `run_reopen_pending_gate` の時：`active_gate` 非 null・`phase`/`stage` は `active_gate` と一致・`blocked_by=null`。③ `run_reopen_drafting` の時：`active_gate` は `stages/<phase>.yaml#drafting` 形式・`phase`/`stage` はその drafting 単位と一致。④ `repair_workflow_state` の時：`active_gate=null`・`phase=null`・`stage=null`・`repair_reasons` に修復理由を含める。⑤ `wait_for_human_decision` の時：`blocked_by.type` で停止理由を区別。⑥ `run_maintenance` の時：`action_parameters` に `maintenance_action`・`allowed_scope`・`allowed_files`・`completion_conditions`・`active_stack_frame_id`・`parent_frame_id` を含める。上記①〜⑥の制約は D-003 §4.2 で確定している制約の全てであり、これ以外の `required_action` 種別には確定した追加フィールド制約はない（universal 必須フィールドのみが適用される）。

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
5. 承認ゲートを必須とする単純操作は、最低限 `commit_stop_point`、`apply_approved_reopen_plan`、`run_reopen_start`、`advance_reopen_after_commit_stop_point`、`advance_reopen_after_approval_stop_point`、`finalize_reopen`、`repair_workflow_state` を含む。これらは `approval_required: true` として扱い、実行前に明示的な人間判断記録を必要とする。この列挙は複合操作の分岐条件を否定しない。`run_maintenance` は maintenance YAML または内部操作の承認要求に従い、`run_workflow_stage` は stage 種別に従う。
6. `record_human_decision` は承認対象操作ではなく、承認ゲートを構成する判断記録操作として扱う。`effect_kind` は判断記録を書き込む場合は `state_mutation` とし、`approval_required` は常に `false` とする。`record_human_decision` の完了だけでは、対象 operation の `approval_required: true` を満たしたことにしてはならない。
7. `run_reopen_pending_gate` は active gate 種別に応じて operation contract を分岐する。`triad-review` と `review-wave` は外部レビュー実行を伴う `external_call`、`alignment` は LLM が整合確認材料を生成する `write`、`approval` は承認要求を構造化する `state_mutation` として扱う。drafting は `run_reopen_drafting` として分離する。
8. `run_maintenance` と `run_workflow_stage` は、内部で実行する操作または stage 種別によって `effect_kind` と `approval_required` が変わる複合操作として扱う。複合操作を単一代表値、list 型、内部ステップ分解のいずれで表すかは design で確定するが、LLM が都度推測する形にはしない。design で確定するまでの最小規則として、複合操作は分岐条件、内部 step、各 step の `effect_kind`、最大副作用、承認要否の集約規則を持つものとして扱う。
9. 複合操作の schema 表現は Phase 1 の未確定事項として扱う。候補は、最大副作用の `effect_kind` を代表値として注記する、`effect_kind` を list 型にする、複合操作を単一 enum の内部ステップへ分解する、の3案を最低限保持する。また、`record_human_decision` が記録する判断と承認対象の `required_action` を、セッション識別子、タイムスタンプ、操作 ID、または同等の識別子で結びつける方法を design で確定する。
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
11. 承認ゲートは proxy_model が代行できる判断と、人間だけが承認できる判断を機械可読に区別する。少なくとも commit、push、spec.json 更新、phase approval、reopen finalize、approval_required な不可逆操作の実行許可は human-only decision として扱い、proxy_model decision だけで通過させてはならない。proxy_model は所見 triage や補助判断を代行できるが、human-only decision の承認主体を置換しない。
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



## .reviewcompass/specs/workflow-management/reviews/2026-06-19-workflow-management-requirements-vertical-redo-review-run/prompts/gpt-5.4.round-1.prompt.md

prompt_id: openai_review
provider: openai-api
model_id: gpt-5.4

# Task
Review the target document for the requested phase and criteria.

# Phase
triad-review

# Criteria
# Requirements Triad Review Target: Workflow Management Requirement 13-16 Vertical Redo

## Review Target

This review judges only `.reviewcompass/specs/workflow-management/requirements.md`, specifically Requirement 13 through Requirement 16 and the directly related change intent / traceability text.

Do not judge `design.md` or `tasks.md` as review targets in this run. They may be mentioned only as downstream context if needed to detect unsupported requirements-level additions or missing requirements-level intent.

## Source Materials

Use these source materials as upstream decision materials for intent-transfer analysis:

- `docs/reviews/reopen-classification-2026-06-19-wm-requirement-13-16-vertical-redo.md`
- `docs/notes/2026-06-18-integrated-design-selection-execution-layers.md`
- `docs/notes/working/2026-06-18-mechanized-workflow-execution-design.md`
- `docs/notes/working/2026-06-19-integrated-design-requirements-missing.md`
- `docs/operations/SESSION_WORKFLOW_GUIDE.md#vertical-intent-transfer-review`

## Required Check

Independently review whether the upstream decision materials' purpose, responsibility boundaries, acceptance criteria, and forbidden actions have been inherited into Requirement 13 through Requirement 16 without omission, weakening, unsupported additions, or drift.

Pay particular attention to:

- Requirement 13: operation contract vocabulary, required_action mapping, single source of truth boundary between operation contracts and registry/preflight, read-only confirmation boundary, and fail-closed treatment for missing or stale contract references.
- Requirement 14: approval gate semantics, side track stack, workflow-state snapshot, read-only versus mutating operations, and proxy_model versus human-only decision boundaries.
- Requirement 15: structured effective prompt as a language-task specification, separation from mechanical tasks, machine-checkable prompt audit, and LLM judge audit as non-approving auxiliary analysis.
- Requirement 16: Phase 0 through Phase 6 ordering, phase completion conditions, no cross-phase implementation mixing, active reopen scope versus historical reopened flags, impact review scope, and proxy_model triage decision applicability predicates.

## Finding Policy

Return findings as YAML with a top-level `findings` list. Each finding must include:

- `severity`: CRITICAL, ERROR, WARN, or INFO
- `target_location`: file and section/requirement
- `description`: concrete issue
- `rationale`: why it matters
- `recommendation`: what should change

Use `ERROR` for omissions, weakened requirements, unsupported additions, or boundary drift that could make the requirements phase unsafe to approve.
Use `WARN` for ambiguity or traceability weakness that should be fixed before downstream design/tasks review if it affects later implementation readiness.
Use `INFO` only for non-blocking observations.

If there are no substantive findings, return `findings: []`.

## Out Of Scope

- Correctness of `design.md`
- Correctness or implementation-readiness of `tasks.md`
- Whether design/tasks already carry the requirements correctly
- Implementation code changes
- Commit, push, spec.json phase movement, or approval decisions

## Sensitive Information Check

No API keys, access tokens, passwords, personal contact information, or non-public third-party confidential data are intentionally included in this review target.


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
.reviewcompass/specs/workflow-management/requirements.md

# Target document
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
11. 本機能は `next --json` の目標応答スキーマを `.reviewcompass/schema/next_action_response.schema.json` として JSON Schema 形式で定義する。本スキーマは受入9が定める振る舞い契約（唯一アクション選択・進行中作業単位の有無による null/非 null の切り替え）をスキーマとして表現する。（1）最上位の必須フィールドは `verdict`（文字列）・`exit_code`（整数）・`next_action`（オブジェクト）・`reasons`（配列）・`current_state`（オブジェクト）の5つとし、`verdict` は最上位だけに置き `next_action` 内には含めない。（2）`next_action` の最低限の必須フィールドは `kind`（文字列・`required_action` の分類子、値域は design で確定）・`required_action`（受入10のスキーマを参照）・`active_gate`（文字列または null）・`feature`（文字列または null）・`phase`（文字列または null）・`stage`（文字列または null）・`required_feature_scope`（配列）・`blocked_by`（オブジェクトまたは null）・`future_gates`（配列）・`state_refs`（オブジェクト）の10フィールドとする。これに加え、`repair_reasons`（配列）は `repair_workflow_state` 時に必須となる条件付きフィールド（非空配列・最低1要素）とし、`action_parameters`（オブジェクト）は `run_maintenance` のみを対象とする必須の条件付きフィールドとして定義する。6フィールド（`maintenance_action`・`allowed_scope`・`allowed_files`・`completion_conditions`・`active_stack_frame_id`・`parent_frame_id`）はすべて required とし、追加フィールドの許可・禁止は design で確定する。（3）`feature` はリスト型を許容せず、取り得る値は「単一フィーチャー名」・`"all_features"`（review-wave のような真に横断的な実行単位の場合のみ）・null（進行中の作業単位がない場合）の3種類に限る。複数フィーチャーが影響範囲に入る場合は `required_feature_scope` または `future_gates` に置く。（4）受入9の null/非 null 規則をスキーマで表現する。進行中の作業単位（active workflow unit）がない場合、`feature`・`phase`・`stage`・`active_gate` はすべて null とする。作業単位がある（reopen 第3過程または通常 workflow の gate 実行時）場合のみ、これらのフィールドは非 null とする。（5）後方互換のため `pending_gates`・`next_pending_gate` はオプションフィールドとして定義し、このスキーマの正本フィールドは `future_gates`・`active_gate` とする。これらの後方互換フィールドが存在する場合は対応する正本フィールドと一致させること（`next --json` の実装側の不変条件として要求する。JSON Schema での表現は design で確定する）。新規のコンシューマは正本フィールドのみを参照してよい。（6）`required_action` の値ごとにフィールドの値制約（相互排他）がある。以下は D-003 §4.2 で確定している制約であり、スキーマはこれらを機械的に検証できる構造で表現する（スキーマ上の表現方法は design で確定）。① `commit_stop_point` の時：`active_gate=null`・`phase=null`・`stage=null`・`blocked_by.type="commit_stop_point"`。② `run_reopen_pending_gate` の時：`active_gate` 非 null・`phase`/`stage` は `active_gate` と一致・`blocked_by=null`。③ `run_reopen_drafting` の時：`active_gate` は `stages/<phase>.yaml#drafting` 形式・`phase`/`stage` はその drafting 単位と一致。④ `repair_workflow_state` の時：`active_gate=null`・`phase=null`・`stage=null`・`repair_reasons` に修復理由を含める。⑤ `wait_for_human_decision` の時：`blocked_by.type` で停止理由を区別。⑥ `run_maintenance` の時：`action_parameters` に `maintenance_action`・`allowed_scope`・`allowed_files`・`completion_conditions`・`active_stack_frame_id`・`parent_frame_id` を含める。上記①〜⑥の制約は D-003 §4.2 で確定している制約の全てであり、これ以外の `required_action` 種別には確定した追加フィールド制約はない（universal 必須フィールドのみが適用される）。

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
5. 承認ゲートを必須とする単純操作は、最低限 `commit_stop_point`、`apply_approved_reopen_plan`、`run_reopen_start`、`advance_reopen_after_commit_stop_point`、`advance_reopen_after_approval_stop_point`、`finalize_reopen`、`repair_workflow_state` を含む。これらは `approval_required: true` として扱い、実行前に明示的な人間判断記録を必要とする。この列挙は複合操作の分岐条件を否定しない。`run_maintenance` は maintenance YAML または内部操作の承認要求に従い、`run_workflow_stage` は stage 種別に従う。
6. `record_human_decision` は承認対象操作ではなく、承認ゲートを構成する判断記録操作として扱う。`effect_kind` は判断記録を書き込む場合は `state_mutation` とし、`approval_required` は常に `false` とする。`record_human_decision` の完了だけでは、対象 operation の `approval_required: true` を満たしたことにしてはならない。
7. `run_reopen_pending_gate` は active gate 種別に応じて operation contract を分岐する。`triad-review` と `review-wave` は外部レビュー実行を伴う `external_call`、`alignment` は LLM が整合確認材料を生成する `write`、`approval` は承認要求を構造化する `state_mutation` として扱う。drafting は `run_reopen_drafting` として分離する。
8. `run_maintenance` と `run_workflow_stage` は、内部で実行する操作または stage 種別によって `effect_kind` と `approval_required` が変わる複合操作として扱う。複合操作を単一代表値、list 型、内部ステップ分解のいずれで表すかは design で確定するが、LLM が都度推測する形にはしない。design で確定するまでの最小規則として、複合操作は分岐条件、内部 step、各 step の `effect_kind`、最大副作用、承認要否の集約規則を持つものとして扱う。
9. 複合操作の schema 表現は Phase 1 の未確定事項として扱う。候補は、最大副作用の `effect_kind` を代表値として注記する、`effect_kind` を list 型にする、複合操作を単一 enum の内部ステップへ分解する、の3案を最低限保持する。また、`record_human_decision` が記録する判断と承認対象の `required_action` を、セッション識別子、タイムスタンプ、操作 ID、または同等の識別子で結びつける方法を design で確定する。
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
11. 承認ゲートは proxy_model が代行できる判断と、人間だけが承認できる判断を機械可読に区別する。少なくとも commit、push、spec.json 更新、phase approval、reopen finalize、approval_required な不可逆操作の実行許可は human-only decision として扱い、proxy_model decision だけで通過させてはならない。proxy_model は所見 triage や補助判断を代行できるが、human-only decision の承認主体を置換しない。
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



## .reviewcompass/specs/workflow-management/reviews/2026-06-19-workflow-management-requirements-vertical-redo-review-run/proxy-decision-prompt.md

# proxy_model Triage Decision Prompt

You are the proxy_model for a ReviewCompass requirements triad-review.

Decide the final triage label for each finding below. The review target is only:

- `.reviewcompass/specs/workflow-management/requirements.md`
- Requirement 13 through Requirement 16
- upstream intent transfer into requirements, not design/tasks correctness

Use the upstream-intent criterion:

- `must-fix`: the finding identifies an omission, weakening, unsupported addition, or responsibility-boundary drift that must be corrected before the requirements triad-review can complete.
- `should-fix`: the finding identifies ambiguity or traceability weakness that should be corrected, but the requirement can still proceed if the fix is tracked.
- `leave-as-is`: the finding is not supported by the requirements text or upstream-intent scope, is already covered, or asks for design-level detail that should not be forced into requirements.

Return only YAML with this shape:

```yaml
proxy_model_id: gpt-5.5
decision_prompt_path: proxy-decision-prompt.md
raw_response_path: proxy-decision-raw.yaml
decisions:
  - finding_id: <exact finding id>
    final_label: must-fix | should-fix | leave-as-is
    rationale: <short but specific reason>
    rejected_options:
      must-fix: <why rejected, if final_label is not must-fix>
      should-fix: <why rejected, if final_label is not should-fix>
      leave-as-is: <why rejected, if final_label is not leave-as-is>
```

For every finding whose original severity is ERROR, or whose final label is `must-fix`, include `rejected_options` for the unselected important alternatives so that the approval record can be audited.

## Requirement Excerpts

### Requirement 13

AC3 says the 19-vocabulary table must cover all 19 `required_action` terms and not blur conditional actions with representative values.

AC4 says the table must machine-readably hold, at minimum, `required_action`, `effect_kind`, `approval_required`, `phase_boundary`, `sequence`, executor, branch-condition existence, and referenced preconditions / postconditions for each `required_action`.

AC5 says approval-gated simple operations include at minimum `commit_stop_point`, `apply_approved_reopen_plan`, `run_reopen_start`, `advance_reopen_after_commit_stop_point`, `advance_reopen_after_approval_stop_point`, `finalize_reopen`, and `repair_workflow_state`; these are treated as `approval_required: true` and require explicit human decision records before execution. It also says this list does not deny complex-operation branch conditions, `run_maintenance` follows maintenance YAML or internal-operation approvals, and `run_workflow_stage` follows stage kind.

AC6 says `record_human_decision` is not an approval target, but a decision-recording operation; its completion alone must not satisfy approval for an `approval_required: true` operation.

AC7 says `run_reopen_pending_gate` branches by active gate kind: `triad-review` and `review-wave` are `external_call`, `alignment` is `write`, `approval` is `state_mutation`, and drafting is separated as `run_reopen_drafting`.

AC8 says `run_maintenance` and `run_workflow_stage` are complex operations whose `effect_kind` and `approval_required` vary by internal operation or stage kind. Until design finalizes representation, a complex operation has branch conditions, internal steps, each step's `effect_kind`, maximum side effect, and approval aggregation rule.

AC11 says operation contract and operation registry / preflight have a single machine-readable source-of-truth boundary; registry / preflight refer to or read from that source and do not execute, update, or consume approvals.

AC12 says missing, stale, digest/version drift, or duplicate source fields between operation contract and registry / preflight must be mechanically detected and fail closed.

### Requirement 14

AC5 says `staged_file_set` / digest are captured and checked at push, before pop, and before commit / push. Out-of-scope staged changes, unexpected digest changes, unapproved parent-child staged-file overlap, and pop digest/set mismatches are WARN or higher in Phase 3 and `DEVIATION` or `repair_workflow_state` in Phase 5.

AC7 says side-track max depth defaults to 2; exceeding depth warns in Phase 3 and blocks in Phase 5. Depth excess or scope drift becomes `repair_workflow_state` or an equivalent stopped state.

AC8 says workflow-state snapshot is emitted as `.reviewcompass/runtime/workflow-state-snapshot.yaml`, as a byproduct of `next --json`, and does not replace the `next --json` output contract.

AC10 says stale, manually updated, or uncorrelatable snapshots are not trusted. Canonical state is always `next --json` and state refs; the snapshot is visualization/audit support.

AC11 says proxy_model can substitute for some decisions but cannot replace human-only decisions such as commit, push, spec.json update, phase approval, reopen finalize, or approval-required irreversible operations.

AC12 says side-track stack, approval gate record, and workflow-state snapshot must distinguish storage, read-only operations, and mutating operations; push/pop/consume/invalidate/save and current/snapshot/inspect must not be blurred.

### Requirement 15

AC3 says mechanical tasks are not embedded in effective prompts as procedure; operation contract, preflight, runner, and guard own them. Effective prompts represent checked preconditions and the LLM language task.

AC5 says first-layer machine checks cover file/anchor existence, required structural sections, length bounds, unregistered action kinds, target manifest consistency, output/postcondition correspondence, machine-checked preconditions only, and on-completion consistency. Commit-mixing checks against side-track stack or operation preflight staged-file sets are Requirement 12 / 14 responsibility and are referenceable from effective-prompt audit.

AC6 says Phase 6 LLM judge audit is auxiliary structured gap analysis and does not automate semantic final approval.

AC7 says LLM judge output must be schema-conforming structured output; Phase 6 is optional and after Phase 5 mechanical enforcement.

### Requirement 16

AC5-9 define Phase 2 through Phase 6 order: read-only registry, warning-only preflight, structured prompts, mechanical blocking, then LLM judge semantic audit.

AC10 says each Phase is committed only after `next --json` can return to normal work or an explicit stopped state; phase-spanning intermediate states must not be mixed into one commit.

AC11 says this reopen scope is requirements -> design -> tasks -> implementation replay; historical `spec.json.reopened` must not be equated with current active scope.

AC13 says proxy_model triage applicability depends on evidence completeness, finding/cluster coverage, approval gate record, operation contract `approval_required`, review-wave impact evidence, and human-only boundaries; any human-required evidence or missing/conflicting source blocks proxy-only passage.

AC14 says human-required predicates and conflict resolution are design-finalized; human-only boundary, unresolved approval gate, `approval_required: true` operation, and unresolved review-wave impact evidence outrank proxy_model applicability.

## Findings To Decide

### F1

- finding_id: `2026-06-19-workflow-management-requirements-vertical-redo-review-run-gpt-5.4-primary-001`
- original severity: ERROR
- location: Requirement 13 AC5
- summary: AC5 allegedly introduces unsupported addition by requiring approval for `repair_workflow_state` as a simple operation with `approval_required: true`.
- rationale: Upstream treats workflow-state repair as a fail-closed machine-detected stop/repair path, not necessarily human-approved for every repair action.

### F2

- finding_id: `2026-06-19-workflow-management-requirements-vertical-redo-review-run-gpt-5.4-primary-002`
- original severity: ERROR
- location: Requirement 14 AC8-10
- summary: Snapshot requirements allegedly omit an explicit read-only boundary and could drift into mutating state-management.
- rationale: Snapshot is byproduct/support, but text does not explicitly forbid snapshot generation/update from mutating workflow state.

### F3

- finding_id: `2026-06-19-workflow-management-requirements-vertical-redo-review-run-gpt-5.4-primary-003`
- original severity: WARN
- location: Requirement 15 AC6-7
- summary: LLM judge is auxiliary, but output is not explicitly forbidden from approving, clearing, or overriding machine gates, human-only decisions, or operation-contract postconditions.

### F4

- finding_id: `2026-06-19-workflow-management-requirements-vertical-redo-review-run-gpt-5.4-primary-004`
- original severity: WARN
- location: Requirement 16 AC5-9
- summary: Phase sequencing is mostly preserved, but dormant or partially wired later-phase enforcement behind feature flags during earlier phases is not explicitly prohibited.

### F5

- finding_id: `2026-06-19-workflow-management-requirements-vertical-redo-review-run-claude-opus-4-8-adversarial-001`
- original severity: ERROR
- location: Requirement 13 AC5 / AC7
- summary: AC3 says all 19 terms are covered, but AC5's approval-required list may leave remaining read/state terms' true/false values under-emphasized; the reviewer asks to state that the AC4 table has `approval_required` for every term and that AC5 examples do not shrink that coverage.

### F6

- finding_id: `2026-06-19-workflow-management-requirements-vertical-redo-review-run-claude-opus-4-8-adversarial-002`
- original severity: WARN
- location: Requirement 13 AC11 / AC12
- summary: Single-source-of-truth direction between operation contract and registry/preflight may be ambiguous; reviewer asks to fix operation contract as source and registry/preflight as derived/read side.

### F7

- finding_id: `2026-06-19-workflow-management-requirements-vertical-redo-review-run-claude-opus-4-8-adversarial-003`
- original severity: WARN
- location: Requirement 14 AC5 / AC7
- summary: `repair_workflow_state` versus `DEVIATION` choice is left as an `or`; reviewer asks for minimal rules or explicit deferral to design.

### F8

- finding_id: `2026-06-19-workflow-management-requirements-vertical-redo-review-run-claude-opus-4-8-adversarial-004`
- original severity: WARN
- location: Requirement 15 AC5
- summary: Effective prompt audit can reference commit-mixing checks, but it is ambiguous whether it consumes results or reimplements the checks; reviewer asks to state reference-only and no reimplementation.

### F9

- finding_id: `2026-06-19-workflow-management-requirements-vertical-redo-review-run-claude-opus-4-8-adversarial-005`
- original severity: INFO
- location: Requirement 16 AC11
- summary: Active reopen scope distinction is inherited, but priority among active-scope records is not stated in Req16; reviewer suggests a cross-reference to Requirement 12 AC13.


## .reviewcompass/specs/workflow-management/reviews/2026-06-19-workflow-management-requirements-vertical-redo-review-run/review-target.md

# Requirements Triad Review Target: Workflow Management Requirement 13-16 Vertical Redo

## Review Target

This review judges only `.reviewcompass/specs/workflow-management/requirements.md`, specifically Requirement 13 through Requirement 16 and the directly related change intent / traceability text.

Do not judge `design.md` or `tasks.md` as review targets in this run. They may be mentioned only as downstream context if needed to detect unsupported requirements-level additions or missing requirements-level intent.

## Source Materials

Use these source materials as upstream decision materials for intent-transfer analysis:

- `docs/reviews/reopen-classification-2026-06-19-wm-requirement-13-16-vertical-redo.md`
- `docs/notes/2026-06-18-integrated-design-selection-execution-layers.md`
- `docs/notes/working/2026-06-18-mechanized-workflow-execution-design.md`
- `docs/notes/working/2026-06-19-integrated-design-requirements-missing.md`
- `docs/operations/SESSION_WORKFLOW_GUIDE.md#vertical-intent-transfer-review`

## Required Check

Independently review whether the upstream decision materials' purpose, responsibility boundaries, acceptance criteria, and forbidden actions have been inherited into Requirement 13 through Requirement 16 without omission, weakening, unsupported additions, or drift.

Pay particular attention to:

- Requirement 13: operation contract vocabulary, required_action mapping, single source of truth boundary between operation contracts and registry/preflight, read-only confirmation boundary, and fail-closed treatment for missing or stale contract references.
- Requirement 14: approval gate semantics, side track stack, workflow-state snapshot, read-only versus mutating operations, and proxy_model versus human-only decision boundaries.
- Requirement 15: structured effective prompt as a language-task specification, separation from mechanical tasks, machine-checkable prompt audit, and LLM judge audit as non-approving auxiliary analysis.
- Requirement 16: Phase 0 through Phase 6 ordering, phase completion conditions, no cross-phase implementation mixing, active reopen scope versus historical reopened flags, impact review scope, and proxy_model triage decision applicability predicates.

## Finding Policy

Return findings as YAML with a top-level `findings` list. Each finding must include:

- `severity`: CRITICAL, ERROR, WARN, or INFO
- `target_location`: file and section/requirement
- `description`: concrete issue
- `rationale`: why it matters
- `recommendation`: what should change

Use `ERROR` for omissions, weakened requirements, unsupported additions, or boundary drift that could make the requirements phase unsafe to approve.
Use `WARN` for ambiguity or traceability weakness that should be fixed before downstream design/tasks review if it affects later implementation readiness.
Use `INFO` only for non-blocking observations.

If there are no substantive findings, return `findings: []`.

## Out Of Scope

- Correctness of `design.md`
- Correctness or implementation-readiness of `tasks.md`
- Whether design/tasks already carry the requirements correctly
- Implementation code changes
- Commit, push, spec.json phase movement, or approval decisions

## Sensitive Information Check

No API keys, access tokens, passwords, personal contact information, or non-public third-party confidential data are intentionally included in this review target.


## .reviewcompass/specs/workflow-management/reviews/2026-06-19-workflow-management-requirements-vertical-redo-review-run/review_summary.md

# Review run summary: 2026-06-19-workflow-management-requirements-vertical-redo-review-run

variant: implementation_review_independent_3way_codex_operator

## Role assignments

| role | path | provider | model |
| --- | --- | --- | --- |
| primary | api | openai-api | gpt-5.4 |
| adversarial | api | anthropic-api | claude-opus-4-8 |
| judgment | api | gemini-api | gemini-3.1-pro-preview |

## Model results

| model_id | parse_status | triage_status | findings | severity | raw |
| --- | --- | --- | ---: | --- | --- |
| gpt-5.4 | parsed | triage_pending | 4 | ERROR:2, WARN:2 | raw/gpt-5.4.round-1.txt |
| claude-opus-4-8 | parsed | triage_pending | 5 | ERROR:1, INFO:1, WARN:3 | raw/claude-opus-4-8.round-1.txt |
| gemini-3.1-pro-preview | parsed | no_findings | 0 | - | raw/gemini-3.1-pro-preview.round-1.txt |

## Next steps

1. Read raw responses for any parse_failed or triage_pending model.
2. Move finding-level judgments into triage.yaml.
3. Present the variant, role assignments, raw/model summary, same-root clusters, and three-level triage to the user.
4. Stop at the 利用者提示ゲート before asking proxy_model, editing implementation, updating spec.json, or moving phases.
5. Resolve human_required items before treating the run as complete.


## docs/operations/SESSION_WORKFLOW_GUIDE.md

# SESSION_WORKFLOW_GUIDE：セッション運営ガイドライン

最終更新：2026-06-10（現行のセッション運営契約として整理）

本文書は ReviewCompass の開発セッションを確実に回すための運用ガイドラインである。作業開始、レビュー、利用者判断、コミット、完了報告の共通手順を定める。

本文書は運用文書（`docs/operations/` 配下）であり、ReviewCompass の実行時手順を定める。仕様・設計・タスクの正本と矛盾する場合は、該当正本を確認し、必要に応じて reopen 手続きに乗せる。

## 1. セッション開始時の必読フロー（5 分以内）

セッション開始時は **作業着手前に必ず**次を順番に確認する。記憶や前回会話だけを根拠に作業へ入らない。

### 1.1 必読 5 件

順序は重要：

1. **`TODO_NEXT_SESSION.md`**（最新進捗）
   - 前セッション末尾の到達点、次の作業候補、未消化所見
   - 「§0 重要事項」「§1 起動手順」「§3 次の作業候補」を最低限読む
   - 直近の `docs/sessions/session-*.md` も併読し、TODO に圧縮された経緯の詳細を確認する

2. **`docs/operations/WORKFLOW_NAVIGATION.md`**（次 action 判定）
   - `tools/check-workflow-action.py next --json` の読み方
   - 判定点ごとの required disciplines / required inputs / effective prompt の扱い

3. **`docs/operations/WORKFLOW_PRECHECK.md`**（機械判定の入口）
   - `spec-set`、`commit`、`push`、`next`、`reopen-start` の実行前条件
   - 機械判定で停止した場合の扱い

4. **`learning/workflow/carry-forward-register/reviewcompass-import.yaml`**（持ち越し所見の正本）
   - 機能横断波及所見の未消化件数と内容を把握
   - 正本と履歴 source を混同しない

5. **`docs/extraction-mapping.md`**（抽出進捗）
   - 各機能の状態（未着手／抽出中／抽出済／確認済）
   - 機能ごとの実施履歴

### 1.2 確認後の git 状態把握

- `git log --oneline -10`：直近のコミット履歴
- `git status`：未コミット変更の有無

### 1.3 ワークフロー上の現在位置の確認

- 現在どのフェーズか（intent ／ requirements ／ design ／ tasks ／ implementation）
- 現在どの段か（drafting ／ triad-review ／ review-wave ／ alignment ／ approval の 5 段）
- 残機能と消化予定所見

## 2. ワークフロー段の役割と順序

### 2.1 全体構造

```
intent 層（人間担当）
  ↓
機能分離
  ↓
requirements 段：drafting → triad-review → review-wave → alignment → approval
  ↓
design 段：drafting → triad-review → review-wave → alignment → approval
  ↓
tasks 段：drafting → triad-review → review-wave → alignment → approval
  ↓
implementation 段：drafting → triad-review → review-wave → alignment → approval
```

各フェーズは drafting／triad-review／review-wave／alignment／approval の 5 段で進める。

### 2.2 各段の役割（責務分離後）

- **drafting**：各機能の草案作成のみ。1 機能ずつ独立に進める。actor=llm（または human）。requirements／design／tasks の drafting は文書起草を意味する。implementation の drafting は文書起草ではなく、tasks.md に従ったテストと実装コードの生成を意味する。
- **tasks drafting の粒度**：tasks 段の drafting では、対象機能の設計書 §14 要件追跡表（Req 受入単位 × 担当タスク単位）を骨格として tasks.md を作成する。tasks.md は implementation drafting へ直接入れる粒度で書く。各タスクには、実装対象ファイル、最初に書く失敗テスト、実装順序、完了条件、検証コマンド、禁止事項、停止条件を含める。implementation-plan.md や implementation-drafting.md のような別の実装前計画文書を正本成果物として要求しない。
- **triad-review**：機能内の 3 役レビュー（主役・敵対役・判定役）と機能内対処の実施。手動 dogfooding または subagent_mediated（サブエージェント仲介方式）で実施。actor=llm
- **review-wave**：複数機能を横断する複数ラウンドレビュー。機能横断波及所見と同根所見（異なる機能で同じ性格の所見が独立に発見された組）を集約し、一貫した対処方針で全該当機能の仕様文書に反映する
- **alignment**：LLM 自動判定による整合確認段（actor=llm）
- **approval**：人間または別モデルによる承認段（actor=human または proxy_model）

drafting と triad-review を別段にする理由は、誰が何をしたかを段単位で明確に記録し、草案作成者と判定者の分離を機械検査可能にするためである。

<a id="vertical-intent-transfer-review"></a>

### 2.2.1 上流意図伝達の必須検査

各 phase の triad-review／review-wave／alignment では、対象 phase の成果物だけでなく、上流成果物または上流判断材料からの意図伝達を必須検査項目とする。review prompt は、少なくとも「上流の目的・責務境界・受入条件・禁止事項が、対象成果物へ欠落・弱体化・逸脱・未根拠追加なく引き継がれているか」を問わなければならない。

- **requirements review**：`上流判断材料 → requirements.md` を確認し、reopen 分類根拠、利用者判断、計画メモ、設計メモなどの目的・責務境界・受入条件・禁止事項が要件へ欠落なく落ちているかを検査する。design.md / tasks.md は参照資料であり、審査対象ではない
- **design review**：`requirements.md → design.md` を確認し、要件の目的・境界・受入条件が設計へ欠落なく落ちているかを検査する
- **tasks review**：`requirements.md → design.md → tasks.md` を確認し、要件と設計の意図が implementation-ready なタスク粒度へ落ちているかを検査する
- **implementation review**：`requirements.md → design.md → tasks.md → implementation` を確認し、実装がタスクだけでなく上流意図から逸脱していないかを検査する

review prompt は、review target / source materials / out of scope を明示する。審査対象は現在 phase の成果物に限定し、source materials は背景・意図伝達確認のための参照資料として扱う。下流 phase の成果物が source materials に含まれる場合でも、その correctness を現在 phase の review で判定してはならない。

source materials をパス名だけで列挙してはならない。縦方向監査の review prompt には、判断に必要な上流本文または要点抽出を、モデルが推測せず読める形で含める。要点抽出を使う場合は、少なくとも上流の目的、責務境界、受入条件、禁止事項、未確定事項、対象 phase へ引き継ぐべき判断を分けて記録する。上流資料を読んでいない場合は review-run を開始してはならない。prompt 内で上流資料の中身が確認できない場合も review-run を開始してはならない。

tasks review では、単に tasks.md の粒度や項目数を見るだけでは不十分である。たとえば T-016〜T-019 を審査する場合は、Requirement 13〜16 の意図が design.md の設計判断を経由して、欠落・弱体化・勝手な追加なしに implementation-ready な作業単位へ落ちているかを必須で確認する。

### 2.3 段の進め方の規律

- **drafting 段の草案完成** → 当該機能の triad-review 段に進む（機能単位で逐次進行）
- **triad-review 段で 3 役レビューと機能内対処** を完了 → 当該機能の drafting／triad-review がそろう
- **全機能で drafting ＋ triad-review を完了** してから review-wave に進む（部分的に review-wave を始めない）
- **review-wave の所見を消化** してから alignment に進む
- **alignment で LLM 自動判定** を通過してから approval に進む
- **approval で利用者または別モデル承認** を得てから次フェーズに進む

### 2.4 「次の機能の drafting に進むべき」状況の判断

triad-review 段で 3 役レビューを行った所見が **機能横断の波及所見**だった場合、当該機能の triad-review で対処せず、carry-forward register に持ち越して **次の機能の drafting に進む**。

## 3. 修正案件の波及種別と処理段

### 3.1 用語の使い分け

両用語は **対象方向が異なる正当な技術用語** であり、優劣はない：

- **遡及（そきゅう）**：**上流フェーズへの影響**。下流段の作業で発見された問題が、上流段（過去フェーズ）の修正を要するもの。例：実装段で発見した不整合が要件段の書き直しを要する
- **波及（はきゅう）**：**同フェーズ内の他機能（フィーチャー）への影響**。ある機能のレビューが別機能との不整合を露出させるもの。例：foundation 要件の修正が runtime／evaluation 要件にも影響する

所見を分類するときは、上流フェーズへ戻る必要があるか、同フェーズ内の他機能へ広がるかを分けて判断する。

### 3.2 修正案件の 4 種別（＋ 2 補助種別）

レビューで露出する所見は次の種別に分類する：

| 種別 | 内容 | 例 |
|---|---|---|
| **機能内対処** | 当該機能の仕様修正のみで完結 | 表現修正、機能内の語彙不統一訂正 |
| **波及（同フェーズ・横方向）** | 同フェーズ内の他機能の仕様修正も必要 | A-001：foundation 要件と runtime 要件の `not_run` 欠落 |
| **遡及（上流フェーズ・縦方向）** | 上流フェーズの仕様修正が必要 | 設計段で「要件段の Req 6 受入 8 に矛盾あり」と発見 |
| **遡及 ＋ 波及（縦 ＋ 横）** | 上流フェーズの複数機能に影響 | 設計段で発見した要件段の不整合が複数機能の要件文書に波及 |

補助種別：

- **leave-as-is（修正不要）**：判定役が「修正不要」と判断したもの、対処せず記録のみ
- **延期**：「将来フェーズで対処」と判定役が明示したもの（例：F-004 の配置時対処）

### 3.3 種別ごとの処理段と方法

#### (a) 機能内対処

- **発見されるタイミング**：drafting 段（起草者の自己発見）／ triad-review 段（3 役レビュー）
- **処理する段**：当該機能の **triad-review 段** で対処（drafting に戻して草案修正、または triad-review 段内で直接修正）
- **方法**：当該機能の仕様文書を直接修正
- **次段への進行**：当該機能の triad-review 段が `completed` 状態になってから次機能へ
- **記録先**：レビュー記録（`.reviewcompass/specs/<機能>/reviews/<日付>-<種別>.md`）の §4 統合節に「対処済み」と記録

##### (a-1) must-fix 所見の対処手順

triad-review 段で判定役が must-fix と判定した所見の対処は、起草者（LLM または人間）が独自判断で仕様文書を修正することを禁ずる。利用者と必ず議論し、各所見の対処方針を 1 件ずつ平易な日本語で説明して合意を得てから反映する。

**手順**：

1. must-fix 所見を 1 件ずつ取り上げる。複数所見が論理的に連動する場合は連動単位でまとめる（例：F-001 と F-007 が同一事象を別観点で扱う場合）
2. 各所見について、対処方針の提案を次の構造で平易に説明する：
   - その判断が必要になった経緯（要件文書や上流文書からの導出）
   - 候補案の列挙（必ず複数）
   - 各候補案の利点と弱点
   - **後段で発生し得る問題の深掘り**：下流仕様（他機能の design／tasks／implementation）、対象アプリへの配置可能性、機械検証時の挙動、実装フェーズの運用、将来の拡張性
   - 推奨案とその根拠
3. 「現状維持」を推奨する場合も、現状維持の弱点を検証してから示す
4. 一括処理（複数論点を一気に決着）を避け、各論点を個別に深掘りする
5. 利用者の判断を得てから、仕様文書を 1 件ずつ Edit で修正する
6. 各修正後に grep または Read で機械的に照合し、反映を確認する
7. レビュー記録（reviews/...）の §4 統合節に「対処方針・利用者承認の根拠・反映箇所」を記録する

**深掘りの具体内容**（推奨案を提示する際に必ず想定する事項）：

- foundation 機能の場合：対象アプリへの配置可能性、配布対象外資産との分離、リポジトリ内資産の規則との整合
- 値域・語彙の固定：将来拡張時の改訂コスト、機械検証時の不正値検出
- 責務境界：foundation と runtime（または他機能）の責務分離、上流が下流の実装方針に踏み込まない原則
- 不変性：成果物の追記性、生証拠は不変の原則
- 依存関係：他機能が当該仕様を取り込む際の参照可否

**禁則**：

- 利用者と議論せずに must-fix 所見の対処内容を独自に確定する
- 「現状維持を推奨」と表層的に提案する（弱点検証を欠く）
- 候補案を 1 つしか提示しない（代替案との比較を欠く）
- 後段影響を想定しない推奨

<a id="3.3-a-2"></a>

##### (a-2) review-run 後の proxy_model 判断代行手順

API 経由の review-run 後に、人間の個別判断を proxy_model が代行する場合も、メインセッション LLM が重要件を独自に確定して実装へ進むことを禁ずる。proxy_model 代行は「人間判断を省略する」ものではなく、判断主体を別モデルへ移す運用である。

**proxy_model 判断依頼前の利用者提示ゲート**：

API review-run が完了したら、proxy_model 判断依頼、実装修正、spec.json 更新、フェーズ移行のいずれにも進む前に、メインセッション LLM は次を利用者へ提示して停止する。この提示ゲートを完了する前に proxy_model を呼び出してはいけない。

1. 使用 variant 名
2. role ごとの path／provider／model（例：primary／adversarial／judgment の割当）
3. モデル別 raw 結果概要（parse 状態、所見数、severity 内訳、raw path）
4. 同根所見クラスタの一覧
5. `must-fix`／`should-fix`／`leave-as-is` の三段階トリアージ案
6. `must-fix` 候補ごとの平易な説明、候補案、各案の利点と弱点、後段影響、推薦案
7. proxy_model に判断させる場合の対象 finding／cluster、判断範囲、不可逆操作（commit／push／spec.json 更新／フェーズ移行）を含まないこと

variant が未確定、または role 割当が曖昧な場合は review-run を開始しない。既定 variant が CLI 経路を含む等、実行環境と合わない場合は、設定ファイルを読んで候補 variant と role 割当を利用者へ説明し、選択理由を review-run 記録に残す。

**役割分担**：

1. メインセッション LLM は raw レビューを集約し、三段階トリアージの下書きを作る。parsed YAML だけでなく raw response も読み、同根所見をまとめ、`must-fix` ／ `should-fix` ／ `leave-as-is` の候補を作る
2. メインセッション LLM は重要件ごとに、平易な問題説明、候補案、各案の利点と弱点、後段影響、推薦案を作る
3. proxy_model は重要件の採用案・判断理由・最終ラベルを決定する。実装は担当しない
4. メインセッション LLM は proxy_model の raw response を保存し、`proxy-decisions/<finding-id>.decision.yaml` と `approval-proxy-<日付>.yaml` に構造化する
5. 機械ガードは proxy decision の充足を検査する。未判断、raw 欠落、候補案欠落、採用案欠落、判断理由欠落、triage 最終ラベルとの不一致があれば実装へ進まない
6. メインセッション LLM は機械ガード通過後、採用された修正だけを TDD で実装する
7. コミット・プッシュ・spec.json 更新・フェーズ移行は人間の明示承認を要求する。proxy_model はこれらの不可逆操作を代行しない

**重要件の判定閾値**：

- `must-fix`、`ERROR`、`CRITICAL` は必ず重要件として扱う
- `should-fix` でも、上流仕様、データ契約、機械ガード、証跡保持、ワークフロー権限境界、複数モデルの同根指摘に関わるものは重要件として扱う
- 同根指摘とは、複数モデルの所見が同じ対象ファイル・同じ出力契約・同じ機械ガード・同じ証跡・同じ原因に触れているものをいう。表現が異なっても、対象または原因が一致する場合は同根として扱う
- 正本削除、機械ガード削除、重要件閾値の引き下げ、承認証跡の削除、検証対象範囲の縮小は、コミット等と同じく人間の明示承認を要する不可逆操作として扱う
- 判断に迷うものは重要件側に倒し、proxy_model 判断または人間判断へ回す

**proxy_model への入力証跡**：

- proxy_model へ渡す判断材料には、メインセッション LLM の要約だけでなく、元 review raw への参照または抜粋を必ず含める
- `proxy-decisions/<finding-id>.prompt.md` を作成する前に、[[llm-as-judge-prompting]] の手順（材料揃え → 問い設計 → 選択肢なし分析）でプロンプトを設計する
- `proxy-decisions/<finding-id>.prompt.md` に、元 review raw 参照、問題説明、候補案セット、推薦案、判断してほしい最終ラベルを保存する
- `proxy-decisions/<finding-id>.decision.yaml` には、`candidate_options`、`source_raw_paths`、`decision_prompt_path`、採用案、棄却案理由、判断理由、最終ラベルを保存する
- proxy_model が元 review raw を読めない形の判断材料しか受け取っていない場合、その decision は実装着手の承認証跡として扱わない
- 現行の軽量ガードは、proxy_model_id の文字列一致、decision file の finding_id 一致、final_label 一致、prompt/raw/候補案証跡の存在を検査する。API 署名や暗号学的な生成元証明は将来課題とする

**証跡配置**：

- `raw/`：各モデルの生応答
- `triage.yaml`：メインセッション LLM による三段階トリアージ
- `proxy-decisions/<finding-id>.prompt.md`：proxy_model に渡した判断材料
- `proxy-decisions/<finding-id>.raw.txt`：proxy_model の生応答
- `proxy-decisions/<finding-id>.decision.yaml`：採用案、判断理由、最終ラベル、棄却案理由
- `approval-proxy-<日付>.yaml`：実装着手を許可する proxy approval record

**並列化可能な単位**：

- proxy_model への判断依頼は、同根所見クラスタ単位で並列化できる
- TDD 実装は、互いに同じファイルを更新しない実装単位、または入出力契約が独立しているタスク単位で並列化できる
- 共通スキーマ・共通ビルダー・同一ファイルを触る修正は直列で扱う
- 生成物、共有 helper、推移的契約、同じ出力 manifest、同じ traceability 出力を共有する修正は直列で扱う
- 並列実装の統合前に、メインセッション LLM が triage、proxy decision、テスト結果、ファイル差分を再照合する
- 並列処理で新しい判断問題が出た場合、その単位は停止し、proxy_model 判断または人間判断へ戻す
- 承認済み finding の実装中に見つけた未承認の便乗リファクタ、隣接挙動変更、対象外 cleanup は実施しない。必要なら新しい判断問題として停止する

**実装サブ担当 LLM の扱い**：

- 実装サブ担当 LLM は、原則として別スレッドかつ分離 worktree で扱う
- 同じ repo での並列実装は原則禁止し、読み取り調査または差分を残さない確認に限定する
- メインセッション LLM は、対象 finding、proxy decision、触ってよいファイル、期待テスト、禁止事項、停止条件を実装サブ担当へ渡す
- 実装サブ担当は、指定範囲外のファイル変更、判断変更、コミット、プッシュ、spec.json 更新、フェーズ移行を行わない
- 実装サブ担当が新しい判断問題、上流仕様への疑義、許可ファイル外の修正必要性を見つけた場合、その作業単位を停止してメインセッション LLM に戻す

**別スレッド生成物の扱い**：

- 別スレッド・分離 worktree で発生した生成物は、実装差分、検証結果、判断根拠、作業ノイズに分類する
- 実装差分は、メインセッション LLM が確認したうえで本線 worktree への取り込み候補にする
- 検証結果と判断根拠は、必要な要約だけを review-run、session record、または docs/notes に保存する
- 判断に影響した失敗試行、失敗パッチ、途中ログは work_noise から decision_basis へ昇格し、メインセッション LLM が要約または該当箇所を保存する
- 作業ノイズは本線 repo に取り込まない。作業ログ、一時メモ、途中のテスト出力、失敗パッチ案は原則としてサブ worktree 側に閉じる
- 本線へ戻す標準単位は、パッチ、テスト結果サマリ、未解決事項の 3 点とする

<a id="3.3-a-3"></a>

##### (a-3) 操縦 LLM 別の API 既定 variant と独立性原則（本節を正本とする）

セッションを操縦（起草・修正）する LLM と、その成果物を検証する LLM の系列を分離する。
自己レビューによる独立性低下を防ぐための原則であり、利用者承認済み
（設計記録 `docs/notes/2026-06-10-deployment-multi-llm-entry-design.md` §3.6、2026-06-11 個別承認）。
本節がこの原則と既定 variant 選択規則の正本である（仕様への昇格は実アプリ pilot 後に再検討、
MLE-DEC-004、2026-06-12 利用者決定）。

**独立性の原則**：

1. 単独検証役（1 体での post-write 検証など）は、操縦 LLM と別系列を必須とする
2. 3 役構成の adversarial（反証役）と judgment（判定役）は、操縦 LLM と別系列を必須とする
3. 3 役構成の primary（検出役）は、操縦 LLM と同系列を許容する（最終判定を持たず、
   残り 2 役の独立で全体の独立性が保たれるため）
4. proxy_model（人の判断の代行）は、操縦 LLM と別系列を必須とする

**操縦 LLM 別の既定 variant**（実体は `config/api-settings.yaml`）：

- **Claude Code 操縦時**：接尾辞なしの `*_independent_3way` 系
  （post_write_verification／yaml_audit／implementation_review の 3 用途。
  primary=anthropic/claude-sonnet-4-6、adversarial=openai/gpt-5.5、
  judgment=gemini/gemini-3.1-pro-preview）
- **Codex CLI 操縦時**：`*_independent_3way_codex_operator` 系
  （primary=openai/gpt-5.4、adversarial=anthropic/claude-opus-4-8、
  judgment=gemini/gemini-3.1-pro-preview）
- judgment（gemini-3.1-pro-preview）と小規模 1 体検証（`post_write_verification_google`）は
  両操縦で共用し、操縦を切り替えても判定基準の連続性を保つ
- 既存 variant の改名は行わない（規律文書・過去 run 記録・spec からの参照保全）。
  別の LLM が操縦する場合（将来）は同じ原則で役を回転して対応する

対象アプリ向けの同内容の案内は `templates/entry/AGENT_ENTRY.template.md` §10 と
`docs/operations/INITIAL_SETUP_LLM_GUIDE.md` にあり、本節と整合させて保守する。

#### (b) 波及（同フェーズ・他機能への影響）

- **発見されるタイミング**：triad-review 段（3 役が他機能との不整合に気づく）／ review-wave 段（機能横断レビュー）
- **処理する段**：**review-wave 段**（フェーズ終端の機能横断段、全機能の drafting ＋ triad-review 完了後に開始）
- **方法**：
  1. triad-review 段で波及と判定されたら **当該機能では対処せず**、carry-forward register に追記
  2. 「次の機能の drafting」に進む（個別機能の段では対処しない）
  3. 全機能の drafting ＋ triad-review が完了したら、review-wave 段で集約消化
  4. 影響を受ける全機能の仕様文書を一括修正（依存順を守る、例：foundation を先に修正してから runtime）
- **記録先**：`learning/workflow/carry-forward-register/reviewcompass-import.yaml` の各所見項目、消化後は `status: resolved` と `resolution` を更新

#### (c) 遡及（上流フェーズへの影響）

- **発見されるタイミング**：任意の下流段（triad-review／review-wave／alignment／approval のいずれか）
- **処理方法**：[REOPEN_PROCEDURE.md](REOPEN_PROCEDURE.md) の 4 過程手順を起動。当該段の作業を停止し、上流フェーズに戻る
- **手戻り種別判定**：N（intent）／R（requirements）／D（design）／A（tasks）／I（implementation）× 深さ 0〜4 の二次元表記で判定
- **再実施対象決定**：第1過程で trigger_map（再実施対象段の決定表）を参照して決める。actor=human の段（approval 等）に来たら作業を止めて承認待ち
- **記録先**：種別判定の根拠を `docs/reviews/reopen-classification-<日付>.md` に残す、機能単位 spec.json の `reopened` 履歴と `recheck` フラグを更新

#### (d) 遡及 ＋ 波及の組合せ

- **発見されるタイミング**：任意の下流段
- **処理方法**：reopen で上流フェーズに戻り、上流フェーズの review-wave 段で波及所見として集約消化、その後下流に伝播
  1. **第 1 段階**：reopen 手続きで上流フェーズに戻り、影響範囲を特定（trigger_map）
  2. **第 2 段階**：上流フェーズで carry-forward register に波及所見として追記し、当該フェーズの review-wave 段で消化
  3. **第 3 段階**：上流フェーズの alignment ＋ approval を再実施
  4. **第 4 段階**：下流フェーズの alignment ＋ approval を再実施（trigger_map で連鎖再実施対象として決定）
- **記録先**：reopen 記録 ＋ carry-forward register の両方

#### (e) leave-as-is と延期

- **leave-as-is**：判定役が「修正不要」と判断したもの。対処せず、レビュー記録に判定根拠を残すのみ
- **延期**：将来のフェーズで対処する判定。レビュー記録に延期理由と対処予定フェーズを残し、当該フェーズ着手時のチェックリストに追記

### 3.4 振り分け判断のフロー（triad-review 段で実施）

triad-review 段の判定役は、各所見について次の振り分けを行う：

```
所見発見
  ↓
当該機能の仕様修正のみで完結するか？
  ├── YES → 機能内対処（triad-review 段内で対処）
  └── NO
      ↓
  他機能の仕様修正も必要か？
  ├── YES（同フェーズ内のみ） → carry-forward register に追記、review-wave 段で処理
  ├── YES（上流フェーズに戻る必要あり、単機能） → reopen 手続きを起動
  └── YES（上流フェーズに戻る必要あり、複数機能） → reopen ＋ 上流の review-wave で集約処理
  
別判定：
  ├── 修正不要 → leave-as-is（記録のみ）
  └── 将来フェーズで対処 → 延期（チェックリスト追記）
```

### 3.5 段ごとの露出と処理段の対応表

| 段 | 主に露出する所見 | 当該段内で処理する所見 | 次段に持ち越す所見 |
|---|---|---|---|
| drafting | 起草中の自己発見 | 機能内（草案に直接反映） | なし |
| triad-review | 機能内 ／ 波及 ／ 遡及 | **機能内** のみ | 波及 → review-wave、遡及 → reopen |
| review-wave | 波及（横断ラウンド中の追加発見も） | **波及** | 遡及あり → reopen |
| alignment | 自動判定の不整合検出 | （自動判定が通過するまで前段に戻す） | 遡及あり → reopen |
| approval | 重大見落とし、利用者または別モデルによる指摘 | （承認しない） | reopen で上流戻し |

### 3.6 機能横断波及所見の管理ルール

- 各機能の triad-review 段で発見されたら、即時 carry-forward register に追記
- 追記項目：所見 ID（A-XXX 形式）、検出セッション、波及範囲（影響を受ける機能と仕様箇所）、対処方針、依存関係
- review-wave／alignment／approval の機能横断段着手時、全件を消化対象とする
- 消化後、各所見に「✅ 対処済み（YYYY-MM-DD、要件 review-wave）」ラベルを追加

## 4. サブエージェント方式の運用条件

### 4.1 位置づけ

- メインセッションは草案作成とレビュー結果の取りまとめを担う
- 3 役レビューは、メインセッションから分離された reviewer session または外部 API 検証者で実行する
- review-run の実行形は adapter と provider 設定に従う

### 4.2 モデル割り当て（規律）

3 役（主役・敵対役・判定役）は、メイン LLM から分離した実行主体が担う。メイン LLM は草案作成と三役レビュー結果の取りまとめのみを担い、3 役のいずれにもならない。

各役のモデルは `runtime/config/reviewcompass.yaml` または review-run の provider 設定で指定する。利用者が設定で変更できる。

**モデル能力配分の規律**：

- **主役と敵対役は必ず異なるモデルを使う**（敵対役の独立性確保のため）
- 判定役は主役または敵対役と同じモデルを使うことを許容する
- 敵対役と判定役には、反証生成と責務境界判断を担う十分な能力のモデルを割り当てる

### 4.3 サブエージェント呼び出し時の規律

- **プロンプトに自己完結性を持たせる**：サブエージェントは別 session で、メインの作業文脈を共有しない
- **参照文書の引用は事後検証**：サブエージェントの引用には節番号や参照先の誤りが発生しうる。メインセッションが grep やリンク検査で確認する
- **ファイル書き込みは原則禁止**：読み取りと分析のみ。例外的にレビュー記録の §2 や carry-forward register への追記提案を許容
- **モデル指定**：利用中の adapter が提供する model / provider 指定方法に従う。外部 API 経由では provider 設定を参照する

### 4.4 レビュー記録の必須フィールド

レビュー記録の front-matter に次を必須化：

```yaml
author:
  identity: <adapter_main_session>
  model: <model-id>
  role: drafter
reviewer:
  identity: <adapter_reviewer_session>
  model: <model-id>
  role: final_judgment
  separation_from_author: true
```

`author.identity` と `reviewer.identity` が異名であることを機械検査の対象とする。重要なのは provider 名ではなく、起草者と判定者が分離していることを記録できることである。

### 4.5 mode 値

レビュー記録の `mode` は `subagent_mediated`（正式値）。foundation のレビューモード語彙正本（Requirement 6 受入 6）の 3 値のうちのひとつ。

## 5. 利用者判断が必要な論点の見極め

### 5.1 利用者判断必須の項目

次のいずれかに該当する場合、LLM は単独で確定せず、利用者の明示承認を仰ぐ：

- **正本方針変更**：仕様・設計・タスク・運用規律の意味を変える修正
- **大規模再設計**：既存の責務境界、機械判定、成果物配置を大きく変更する場合
- **機能横断の権限分担**：複数機能にまたがる責務分担の決定（例：A-007 の self-improvement と workflow-management の権限調停）
- **判定境界の判断**：must-fix／should-fix／leave-as-is の境界が曖昧な場合
- **承認・コミット・push・フェーズ移行**：すべて利用者明示承認必須
- **作業の打ち切り・先送りの誘導**：利用者の明示承認なく「続きは次セッションで」等と作業を終了・先送りに誘導しない

### 5.2 LLM が自律的に決められる項目

- **抽出時のクリーニング作業の細部**（機能名置換、自己適用前提除去等）
- **観点 5（検証可能性）の機械判定可能な所見の指摘**
- **レビュー記録の構造化**（front-matter、節構成）

### 5.3 判断の記録規律

利用者判断の結果は次の場所に記録：

- **正本方針変更**：該当する仕様・設計・タスク・運用規律に決定日付付きで記載
- **機能横断対処方針**：carry-forward register の該当所見に対処方針として追記
- **重大論点**：レビュー記録の §1 主役レビュー、§4 統合の「利用者判断履歴」節に記録

### 5.4 セッション記録の作成規律

原則として毎セッション、セッション終了時または重要判断後に `docs/sessions/session-<N>-<YYYY-MM-DD>.md` を作成または更新する。特に、重要な判断・承認・レビュー結果・修正経緯が発生した場合は必須とする。これは会話全文の逐語ログではなく、後で経緯を確認できる要約記録とする。

`<N>` は `docs/sessions/` に存在する既存の最大セッション番号に 1 を加えた番号とする。同日の複数セッションでも番号を進め、同じ番号を再利用しない。
1 session につき 1 ファイルとし、同一 session 内で重要判断が複数回発生した場合は同じファイルへ追記する。重要判断ごとに別番号を消費しない。
並行セッションや未コミット作業により採番が衝突した場合、メインセッション LLM は既存記録・git 状態・未コミット差分を確認し、利用者が採番を確定するまで正式な新規セッション記録を作成しない。採番確定前に記録が必要な場合は、`docs/sessions/drafts/session-<YYYY-MM-DD>-<short-topic>.md` に一時草案を置き、正式番号確定後に `docs/sessions/session-<N>-<YYYY-MM-DD>.md` へ移動する。移動後は draft ファイルを残さず、正式ファイルに草案内容が統合済みであることを確認する。

メインセッション LLM はセッション記録の草案作成責任を持つ。利用者判断の引用・承認範囲・未確定事項に曖昧さがある場合は、記録前に利用者へ確認する。
コンテキスト切れや中断により当該 LLM が記録できない場合、次セッションが草案を引き継ぐ。草案がない場合は、TODO、review-run、approval record、git diff から経緯を再構成して記録する。

最低限、次を記録する：

- このセッションで実施した作業
- 利用者が承認した判断と、その対象
- API レビューや独立検証の結果と三段階トリアージ
- 修正した主要ファイルと検証結果
- 失敗・見落とし・再発防止に必要な気づき
- 次セッションへの引き継ぎ

推奨見出しは既存 session 記録と同型とし、最低限次を含める：

1. サマリ（このセッションでやったこと）
2. 気づき・特筆点
3. コミット一覧（該当する場合）
4. 次セッションへの引き継ぎ

`TODO_NEXT_SESSION.md` は次セッション向けの入口メモであり、詳細な経緯記録の正本ではない。詳細経緯は `docs/sessions/` に残し、TODO には必要な参照だけを置く。

## 6. コミット規律

### 6.1 コミット単位

- **正本文書更新 ＋ 基盤整備**：1〜2 コミット（方針確定、運用ファイル整備）
- **機能ごとに 1 コミット**：仕様文書 ＋ 運用文書 ＋ レビュー記録の 3 ファイル（または schema/template 等の関連ファイル）
- **機能横断段（review-wave／alignment／approval）**：1 コミット（複数機能の小修正をまとめる）

### 6.2 コミット順序

依存マップ順に従う：

1. foundation
2. runtime
3. evaluation
4. analysis
5. workflow-management
6. self-improvement
7. conformance-evaluation

### 6.3 コミットメッセージ規律

- **平易な日本語**：英語技術用語の連発を避け、完全な日本語の文で書く
- **題名**：機能名 ＋ 作業種別（例：「foundation 機能の requirements 抽出と 3 役レビュー」）
- **本文**：作成・更新ファイルの列挙、主な反映内容、機能横断所見の持ち越し有無
- **Co-Authored-By**：利用中の adapter と利用者方針に従う。自動付与を前提にしない

### 6.4 コミット前確認

- `git status` で対象ファイルを確認
- `git diff --cached` で内容確認（必要に応じて）
- `--no-verify` や `--no-gpg-sign` は使わない（規律）

### 6.5 不可逆操作の進行報告最小化

commit、push、spec.json workflow_state 変更、フェーズ移行などの不可逆操作では、利用者が操作を明示指示した後の正常系進行報告を原則として省く。LLM は必要な確認、stage、承認 record、guard、実操作、事後確認を実行してよいが、各内部手順を逐一会話へ説明しない。

途中報告を行うのは、利用者判断または追加承認が必要な場合に限る。例：承認 record の期限切れや対象不一致、precheck failure、post-write / reopen / in-progress による遮断、sandbox escalation が必要な場合、staged 内容が変わり再承認が必要な場合。

正常完了時の報告は、実行結果だけに絞る。commit なら commit hash、`git status` の clean 性、`next --json` の要点を示す。push なら push 先と結果、`git status` の clean 性を示す。詳細な手順ログ、precheck の全文、stage したファイル一覧、nonce / challenge の値は、利用者が求めた場合または失敗調査に必要な場合だけ示す。

### 6.6 push

push は **利用者明示承認**を仰いでから実行。LLM が自律的に push しない。

## 7. 作業完了時レポート

作業を終えて利用者へ返答するときは、adapter や利用モデルに依存しない会話末尾の運用契約として、最低限次を示す：

- **作業サマリ**：このターンで実施した変更、判断、未変更の範囲
- **検証結果**：実行したテスト、確認コマンド、`post_write_verification` の要否と結果
- **現在状態**：`git status` と `next --json` の要点
- **次タスク**：次に着手すべき具体的な作業、または workflow が要求する次 action

未実施・失敗・承認待ち・保留判断がある場合は、完了扱いにせず明記する。commit、push、workflow_state 更新、spec.json 更新などの不可逆または状態変更を伴う操作は、実際に成功した場合だけ作業サマリに記録する。

`next --json` が `post_write_verification`、`reopen_in_progress`、`resume_in_progress`、`unknown` など `completed` 以外を返している場合、次タスクには任意の改善候補ではなく、その workflow 状態に従う次 action を示す。

### 7.1 進捗説明の平易化

進捗説明では、内部処理名をそのまま主文にせず、利用者が理解しやすい作業状態で述べる。まず次の順で短く示す：

1. 今どの段階か
2. 何をしたか
3. 次に何をするか

必要な場合だけ、内部用語を括弧で補足する。

避ける表現：

- 停止点を消費
- gate を通過
- required_action
- pending_gate
- workflow_state を更新

言い換え例：

- 「tasks approval の停止点を消費」ではなく「tasks 段の承認を完了済みとして記録」
- 「implementation drafting を完了」ではなく「implementation 段のコードとテストを作成」
- 「次の required_action は run_reopen_pending_gate」ではなく「次は現在の段のレビュー作業」

### 7.2 利用者操作が必要な停止点の表示

承認、コミット、push、判断など、利用者の短い返信で次へ進む停止点では、完了報告の末尾に次の 1 行を示す：

```text
次に必要な操作: <操作語>
```

`<操作語>` は、利用者がそのまま返信できる短い語にする。

例：

- `次に必要な操作: 承認`
- `次に必要な操作: コミット`
- `次に必要な操作: push`
- `次に必要な操作: 判断`

複数の選択肢が必要な場合だけ、候補を短く並べる。通常は候補を 1 つに絞る。内部用語、長い説明、手順ログをこの行に混ぜない。

このレポートは会話末尾の完了報告であり、workflow_state や `spec.json` の正本を代替しない。

## 8. 用語ガイド

### 8.1 「遡及」と「波及」

両用語は対象方向で使い分ける：

- **遡及（そきゅう）**：上流フェーズへの影響（時間軸＝過去方向）
- **波及（はきゅう）**：同フェーズ内の他機能への影響（横方向＝機能間）

両方とも正当な技術用語で、避けるべき／推奨という関係ではない。所見の性格を正確に表すために使い分ける。

### 8.2 判定値の使い分け

- **must-fix**：仕様の致命的または重要な欠落、修正必須
- **should-fix**：仕様の改善余地、修正推奨
- **leave-as-is**：仕様として問題なし、修正不要

### 8.3 機能内と機能横断

- **機能内対処**：当該機能の drafting 段で本セッション内に修正
- **機能横断持ち越し**：carry-forward register に集約、review-wave／alignment／approval の機能横断段で対処

### 8.4 サブエージェント関連

- **メインセッション**：作業の入口となる LLM session。草案作成とレビュー結果の取りまとめを担い、3 役レビューの判定者とは分離する
- **サブエージェント**：敵対役・判定役を実行する別 session または外部 API 検証者。利用中の adapter が利用可能な実行形に従う
- **mode = `subagent_mediated`**：サブエージェント方式のレビュー記録の mode 値

## 9. 関連文書

- ワークフローナビゲーション：[WORKFLOW_NAVIGATION.md](WORKFLOW_NAVIGATION.md)
- 事前検査：[WORKFLOW_PRECHECK.md](WORKFLOW_PRECHECK.md)
- reopen 手順：[REOPEN_PROCEDURE.md](REOPEN_PROCEDURE.md)
- 抽出進捗：[../extraction-mapping.md](../extraction-mapping.md)
- 機能横断波及所見：正本 [../../learning/workflow/carry-forward-register/reviewcompass-import.yaml](../../learning/workflow/carry-forward-register/reviewcompass-import.yaml)、履歴 source [../../learning/workflow/carry-forward-register/sources/reviewcompass-pending-cross-feature-findings.md](../../learning/workflow/carry-forward-register/sources/reviewcompass-pending-cross-feature-findings.md)
- レビュー記録雛形：[../../templates/review/manual_dogfooding_review_template.md](../../templates/review/manual_dogfooding_review_template.md)
- TODO：[../../TODO_NEXT_SESSION.md](../../TODO_NEXT_SESSION.md)

## 10. 本ガイドラインの改訂規律

- 本ガイドラインは運用文書として更新可能
- セッションの経緯記録は `docs/sessions/` に残し、本文書には現行の運用契約だけを置く
- 規律変更（§2〜§8）は利用者明示承認後に反映
- 改訂時は最終更新日付を更新


## docs/operations/WORKFLOW_DISCIPLINE_MAP.yaml

# next_action ごとの直前必読規律マップ。
# `tools/check-workflow-action.py next --json` はこの内容を
# `next_action.required_disciplines` として返す。
# 作業対象の状態台帳や持ち越し一覧は規律ではないため、
# `required_inputs` の抽象入力として返す。
# `decision_points` は機械可読な判定点の全体カタログである。
# `by_kind`、`by_stage`、`required_inputs` は既存実装が読む実行時マップとして維持する。
default:
  - docs/operations/WORKFLOW_NAVIGATION.md
decision_points:
  next_action_kind:
    - id: stage
      prompt_source_refs:
        - docs/operations/WORKFLOW_NAVIGATION.md
        - docs/disciplines/discipline_workflow_state_truth_source.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: cross_feature_stage
      prompt_source_refs:
        - docs/operations/WORKFLOW_NAVIGATION.md
        - docs/disciplines/discipline_workflow_state_truth_source.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: commit_stop_point
      prompt_source_refs:
        - docs/operations/WORKFLOW_NAVIGATION.md#commit_stop_point
        - docs/disciplines/discipline_approval_operation.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: upstream_recheck
      prompt_source_refs:
        - docs/operations/WORKFLOW_NAVIGATION.md
        - docs/operations/REOPEN_PROCEDURE.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: reopen_classification_required
      prompt_source_refs:
        - docs/operations/WORKFLOW_NAVIGATION.md
        - docs/operations/REOPEN_PROCEDURE.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: completed
      prompt_source_refs:
        - docs/operations/WORKFLOW_NAVIGATION.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: unknown
      prompt_source_refs:
        - docs/operations/WORKFLOW_NAVIGATION.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: feature_definition_required
      prompt_source_refs:
        - docs/operations/WORKFLOW_NAVIGATION.md#feature_definition_required
        - docs/operations/INITIAL_SETUP_LLM_GUIDE.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: post_write_verification
      prompt_source_refs:
        - docs/operations/WORKFLOW_NAVIGATION.md#post_write_verification
        - docs/disciplines/discipline_post_write_verification.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: lightweight_self_check
      prompt_source_refs:
        - docs/operations/WORKFLOW_NAVIGATION.md#lightweight_self_check
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: post_write_policy_violation
      prompt_source_refs:
        - docs/operations/WORKFLOW_NAVIGATION.md#post_write_policy_violation
        - docs/disciplines/discipline_post_write_verification.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: post_write_human_decision_required
      prompt_source_refs:
        - docs/operations/WORKFLOW_NAVIGATION.md#post_write_human_decision_required
        - docs/disciplines/discipline_post_write_verification.md
        - docs/disciplines/discipline_approval_operation.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: reopen_in_progress
      prompt_source_refs:
        - docs/operations/WORKFLOW_NAVIGATION.md#reopen_in_progress
        - docs/operations/REOPEN_PROCEDURE.md
        - docs/disciplines/discipline_approval_operation.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: maintenance_in_progress
      prompt_source_refs:
        - docs/operations/WORKFLOW_NAVIGATION.md#maintenance_in_progress
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: resume_in_progress
      prompt_source_refs:
        - docs/operations/WORKFLOW_NAVIGATION.md#resume_in_progress
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: reopen_started
      prompt_source_refs:
        - docs/operations/WORKFLOW_PRECHECK.md#reopen-start
        - docs/operations/WORKFLOW_PRECHECK_DETAILS.md#commit
        - docs/operations/REOPEN_PROCEDURE.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: reopen_start_failed
      prompt_source_refs:
        - docs/operations/WORKFLOW_PRECHECK.md#reopen-start
        - docs/operations/WORKFLOW_PRECHECK_DETAILS.md#commit
        - docs/operations/REOPEN_PROCEDURE.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
  workflow_stage:
    - id: candidate-proposal
      prompt_source_refs:
        - docs/operations/WORKFLOW_NAVIGATION.md
        - stages/feature-partitioning/2026-05-24-proposal.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: review
      prompt_source_refs:
        - docs/operations/WORKFLOW_NAVIGATION.md
        - stages/intent.yaml
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: drafting
      prompt_source_refs:
        - docs/operations/WORKFLOW_NAVIGATION.md
        - docs/operations/REOPEN_PROCEDURE.md
        - docs/disciplines/discipline_workflow_state_truth_source.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: triad-review
      prompt_source_refs:
        - docs/operations/WORKFLOW_NAVIGATION.md
        - docs/operations/SESSION_WORKFLOW_GUIDE.md#3.3-a-2
        - docs/operations/SESSION_WORKFLOW_GUIDE.md#vertical-intent-transfer-review
        - docs/disciplines/discipline_approval_operation.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: review-wave
      prompt_source_refs:
        - docs/operations/WORKFLOW_NAVIGATION.md
        - docs/operations/SESSION_WORKFLOW_GUIDE.md#vertical-intent-transfer-review
        - learning/workflow/carry-forward-register/reviewcompass-import.yaml
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: alignment
      prompt_source_refs:
        - docs/operations/WORKFLOW_NAVIGATION.md
        - docs/operations/SESSION_WORKFLOW_GUIDE.md#vertical-intent-transfer-review
        - docs/disciplines/discipline_workflow_state_truth_source.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: approval
      prompt_source_refs:
        - docs/operations/WORKFLOW_NAVIGATION.md
        - docs/operations/WORKFLOW_PRECHECK.md#spec-set
        - docs/operations/WORKFLOW_PRECHECK_DETAILS.md#spec-set
        - docs/disciplines/discipline_approval_operation.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
  precheck_subcommand:
    - id: spec-set
      prompt_source_refs:
        - docs/operations/WORKFLOW_PRECHECK.md#spec-set
        - docs/operations/WORKFLOW_PRECHECK_DETAILS.md#spec-set
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: commit
      prompt_source_refs:
        - docs/operations/WORKFLOW_PRECHECK.md#commit
        - docs/operations/WORKFLOW_PRECHECK_DETAILS.md#commit
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: push
      prompt_source_refs:
        - docs/operations/WORKFLOW_PRECHECK.md#push
        - docs/operations/WORKFLOW_PRECHECK_DETAILS.md#push
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: autonomous-plan
      prompt_source_refs:
        - docs/operations/WORKFLOW_PRECHECK.md
        - docs/operations/WORKFLOW_PRECHECK_DETAILS.md#autonomous-plan
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: autonomous-plan-template
      prompt_source_refs:
        - docs/operations/WORKFLOW_PRECHECK.md
        - docs/operations/WORKFLOW_PRECHECK_DETAILS.md#autonomous-plan-template
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: autonomous-plan-record-integration
      prompt_source_refs:
        - docs/operations/WORKFLOW_PRECHECK.md
        - docs/operations/WORKFLOW_PRECHECK_DETAILS.md#autonomous-plan-record-integration
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: autonomous-ledger-audit
      prompt_source_refs:
        - docs/operations/WORKFLOW_PRECHECK.md
        - docs/operations/WORKFLOW_PRECHECK_DETAILS.md#autonomous-ledger-audit
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: audit-commit
      prompt_source_refs:
        - docs/operations/WORKFLOW_PRECHECK.md#audit-commit
        - docs/operations/WORKFLOW_PRECHECK_DETAILS.md#audit-commit
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: next
      prompt_source_refs:
        - docs/operations/WORKFLOW_NAVIGATION.md
        - docs/operations/WORKFLOW_DISCIPLINE_MAP.yaml
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: reopen-start
      prompt_source_refs:
        - docs/operations/WORKFLOW_PRECHECK.md#reopen-start
        - docs/operations/WORKFLOW_PRECHECK_DETAILS.md#commit
        - docs/operations/REOPEN_PROCEDURE.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
  operation_prompt:
    - id: commit
      prompt_source_refs:
        - docs/operations/COMMIT_OPERATION_CARD.md#commit-operation-card
      effective_prompt_policy: one_effective_prompt_per_decision_point
  reopen_required_action:
    - id: classify_and_rollback_flags
      prompt_source_refs:
        - docs/operations/REOPEN_PROCEDURE.md
        - docs/operations/WORKFLOW_NAVIGATION.md#reopen_in_progress
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: repair_canonical_documents
      prompt_source_refs:
        - docs/operations/REOPEN_PROCEDURE.md
        - docs/operations/WORKFLOW_NAVIGATION.md#reopen_in_progress
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: rerun_alignment_approval_chain
      prompt_source_refs:
        - docs/operations/REOPEN_PROCEDURE.md
        - docs/operations/WORKFLOW_NAVIGATION.md#reopen_in_progress
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: run_reopen_pending_gate
      prompt_source_refs:
        - docs/operations/REOPEN_PROCEDURE.md
        - docs/operations/WORKFLOW_NAVIGATION.md#reopen_in_progress
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: run_reopen_drafting
      prompt_source_refs:
        - docs/operations/REOPEN_PROCEDURE.md
        - docs/operations/WORKFLOW_NAVIGATION.md#reopen_in_progress
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: wait_for_human_approval
      prompt_source_refs:
        - docs/operations/REOPEN_PROCEDURE.md
        - docs/disciplines/discipline_approval_operation.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: finalize_reopen
      prompt_source_refs:
        - docs/operations/REOPEN_PROCEDURE.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: reopen_completed
      prompt_source_refs:
        - docs/operations/REOPEN_PROCEDURE.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: inspect_reopen_state
      prompt_source_refs:
        - docs/operations/WORKFLOW_NAVIGATION.md#reopen_in_progress
        - docs/operations/REOPEN_PROCEDURE.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
  review_run_triage_command:
    - id: list-pending
      prompt_source_refs:
        - docs/operations/SESSION_WORKFLOW_GUIDE.md#3.3-a-2
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: decide
      prompt_source_refs:
        - docs/operations/SESSION_WORKFLOW_GUIDE.md#3.3-a-2
        - docs/disciplines/discipline_approval_operation.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: manifest-template
      prompt_source_refs:
        - docs/operations/SESSION_WORKFLOW_GUIDE.md#3.3-a-2
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: write-manifest
      prompt_source_refs:
        - docs/operations/SESSION_WORKFLOW_GUIDE.md#3.3-a-2
        - docs/disciplines/discipline_post_write_verification.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: assert-apply-fixes-ready
      prompt_source_refs:
        - docs/operations/SESSION_WORKFLOW_GUIDE.md#3.3-a-2
        - docs/disciplines/discipline_approval_operation.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: assert-review-report-ready
      prompt_source_refs:
        - docs/operations/SESSION_WORKFLOW_GUIDE.md#3.3-a-2
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: generate-review-report
      prompt_source_refs:
        - docs/operations/SESSION_WORKFLOW_GUIDE.md#3.3-a-2
      effective_prompt_policy: one_effective_prompt_per_decision_point
  post_write_manifest_gate:
    - id: post_write_manifest_completed
      prompt_source_refs:
        - docs/operations/WORKFLOW_NAVIGATION.md#post_write_verification
        - docs/disciplines/discipline_post_write_verification.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: post_write_manifest_human_required
      prompt_source_refs:
        - docs/operations/WORKFLOW_NAVIGATION.md#post_write_human_decision_required
        - docs/disciplines/discipline_post_write_verification.md
        - docs/disciplines/discipline_approval_operation.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: post_write_manifest_missing_or_invalid
      prompt_source_refs:
        - docs/operations/WORKFLOW_NAVIGATION.md#post_write_verification
        - docs/disciplines/discipline_post_write_verification.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: post_write_policy_violation
      prompt_source_refs:
        - docs/operations/WORKFLOW_NAVIGATION.md#post_write_policy_violation
        - docs/disciplines/discipline_post_write_verification.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
  proxy_model_decision_gate:
    - id: user_visible_triage_gate
      prompt_source_refs:
        - docs/operations/SESSION_WORKFLOW_GUIDE.md#3.3-a-2
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: proxy_decision_prompt
      prompt_source_refs:
        - docs/operations/SESSION_WORKFLOW_GUIDE.md#3.3-a-2
        - docs/disciplines/discipline_approval_operation.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: proxy_decision_file
      prompt_source_refs:
        - docs/operations/SESSION_WORKFLOW_GUIDE.md#3.3-a-2
        - docs/disciplines/discipline_approval_operation.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: proxy_approval_record
      prompt_source_refs:
        - docs/operations/SESSION_WORKFLOW_GUIDE.md#3.3-a-2
        - docs/disciplines/discipline_approval_operation.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
  conformance_evaluation_gate:
    - id: mv6_prompt_isolation
      prompt_source_refs:
        - docs/operations/WORKFLOW_NAVIGATION.md
        - .reviewcompass/specs/conformance-evaluation/tasks.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: reopen_handoff_package
      prompt_source_refs:
        - docs/operations/REOPEN_PROCEDURE.md
        - .reviewcompass/specs/conformance-evaluation/design.md
        - .reviewcompass/specs/conformance-evaluation/tasks.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
  yaml_audit_gate:
    - id: yaml_audit_scope
      prompt_source_refs:
        - docs/disciplines/discipline_yaml_audit.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: yaml_audit_post_write_check
      prompt_source_refs:
        - docs/disciplines/discipline_yaml_audit.md
        - docs/disciplines/discipline_post_write_verification.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
by_kind:
  stage:
    - docs/disciplines/discipline_workflow_state_truth_source.md
  cross_feature_stage:
    - docs/disciplines/discipline_workflow_state_truth_source.md
  post_write_verification:
    - docs/operations/WORKFLOW_NAVIGATION.md#post_write_verification
    - docs/disciplines/discipline_post_write_verification.md
  lightweight_self_check:
    - docs/operations/WORKFLOW_NAVIGATION.md#lightweight_self_check
  post_write_policy_violation:
    - docs/operations/WORKFLOW_NAVIGATION.md#post_write_policy_violation
    - docs/disciplines/discipline_post_write_verification.md
  post_write_human_decision_required:
    - docs/operations/WORKFLOW_NAVIGATION.md#post_write_human_decision_required
    - docs/disciplines/discipline_post_write_verification.md
    - docs/disciplines/discipline_approval_operation.md
  reopen_in_progress:
    - docs/operations/REOPEN_PROCEDURE.md
    - docs/disciplines/discipline_approval_operation.md
  maintenance_in_progress:
    - docs/operations/WORKFLOW_NAVIGATION.md#maintenance_in_progress
  resume_in_progress:
    - docs/operations/WORKFLOW_NAVIGATION.md#resume_in_progress
  feature_definition_required:
    - docs/operations/WORKFLOW_NAVIGATION.md#feature_definition_required
    - docs/operations/INITIAL_SETUP_LLM_GUIDE.md
by_stage:
  drafting:
    - docs/operations/REOPEN_PROCEDURE.md
    - docs/disciplines/discipline_workflow_state_truth_source.md
  triad-review:
    - docs/operations/SESSION_WORKFLOW_GUIDE.md#3.3-a-2
    - docs/operations/SESSION_WORKFLOW_GUIDE.md#vertical-intent-transfer-review
    - docs/disciplines/discipline_approval_operation.md
  review-wave:
    - docs/operations/SESSION_WORKFLOW_GUIDE.md#vertical-intent-transfer-review
  alignment:
    - docs/operations/SESSION_WORKFLOW_GUIDE.md#vertical-intent-transfer-review
    - docs/disciplines/discipline_workflow_state_truth_source.md
  approval:
    - docs/disciplines/discipline_approval_operation.md
    - docs/operations/WORKFLOW_PRECHECK.md#spec-set
    - docs/operations/WORKFLOW_PRECHECK_DETAILS.md#spec-set
required_inputs:
  by_stage:
    drafting:
      - id: target_feature_documents
        role: stage_entry_context
        source_type: feature_document_set
        purpose: Read the current feature state and phase documents before updating the phase artifact.
        resolver:
          kind: next_action_template
          paths:
            - .reviewcompass/specs/{feature}/spec.json
            - .reviewcompass/specs/{feature}/requirements.md
            - .reviewcompass/specs/{feature}/design.md
            - .reviewcompass/specs/{feature}/tasks.md
        read_policy: current_feature_documents
      - id: reopen_procedure_state
        role: workflow_state_context
        source_type: reopen_in_progress_file
        purpose: Read the reopen state and downstream impact decisions before drafting.
        resolver:
          kind: next_action_template
          paths:
            - "{file}"
        read_policy: reopen_state
    triad-review:
      - id: target_feature_documents
        role: stage_entry_context
        source_type: feature_document_set
        purpose: Read the current feature state and phase documents before starting triad-review, including upstream intent transfer from requirements to design to tasks to implementation as applicable.
        resolver:
          kind: next_action_template
          paths:
            - .reviewcompass/specs/{feature}/spec.json
            - .reviewcompass/specs/{feature}/requirements.md
            - .reviewcompass/specs/{feature}/design.md
            - .reviewcompass/specs/{feature}/tasks.md
        read_policy: current_feature_documents
      - id: triad_review_run_artifacts
        role: review_run_context
        source_type: review_run_artifact_set
        purpose: Prepare or read the review-run bundle, raw responses, model summaries, variant/role assignments, same-root finding clusters, and three-level triage records for this triad-review. Before proxy_model, implementation edits, spec.json updates, or phase movement, present the user-visible triage gate described in SESSION_WORKFLOW_GUIDE.md#3.3-a-2 and stop.
        resolver:
          kind: next_action_template
          base_path_pattern: .reviewcompass/specs/{feature}/reviews/*-{feature}-{phase}-review-run
        required_artifacts:
          - review-target.md
          - raw/
          - rounds.yaml
          - model-result-summary.yaml
          - triage.yaml
          - raw-review-triage-summary.md
          - variant-role-assignment
          - user-visible-triage-gate
        read_policy: review_run_bundle_and_triage
      - id: vertical_intent_transfer_check
        role: review_prompt_requirement
        source_type: upstream_intent_transfer_contract
        purpose: Ensure triad-review checks that upstream purpose, responsibility boundaries, acceptance criteria, and forbidden actions are inherited into the target phase without omission, weakening, unsupported additions, or drift.
        resolver:
          kind: static_reference
          path: docs/operations/SESSION_WORKFLOW_GUIDE.md#vertical-intent-transfer-review
        phase_chains:
          requirements:
            - upstream_decision_materials
            - requirements.md
          design:
            - requirements.md
            - design.md
          tasks:
            - requirements.md
            - design.md
            - tasks.md
          implementation:
            - requirements.md
            - design.md
            - tasks.md
            - implementation
        review_target_by_phase:
          requirements:
            review_target: requirements.md
            source_materials:
              - upstream_decision_materials
              - reopen_classification_record
              - planning_notes
              - user_decisions
            out_of_scope:
              - downstream_artifacts_not_review_target
              - design.md correctness
              - tasks.md correctness
        prompt_materialization_contract:
          source_materials_must_not_be_path_only: true
          required_prompt_material:
            - upstream_excerpt_or_structured_summary
            - target_phase_artifact_excerpt
            - review_target
            - out_of_scope
          upstream_summary_fields:
            - purpose
            - responsibility_boundaries
            - acceptance_criteria
            - forbidden_actions
            - unresolved_or_design_deferred_items
            - intended_target_phase_transfer
          blocking_conditions:
            - block_review_run_when_upstream_material_unread
            - block_review_run_when_prompt_contains_only_source_paths
            - block_review_run_when_upstream_summary_omits_required_fields
        required_question: upstream目的・責務境界・受入条件・禁止事項が対象成果物へ欠落・弱体化・逸脱・未根拠追加なく引き継がれているか。
        read_policy: include_in_review_prompt
    review-wave:
      - id: cross_feature_stage_artifacts
        role: stage_output_contract
        source_type: artifact_location_contract
        purpose: Record cross-feature stage evidence under the cross-feature namespace instead of any single feature. Standard path is .reviewcompass/specs/_cross_feature/reviews/{date}-{phase}-{stage}.md.
        resolver:
          kind: static_path_template
          path: .reviewcompass/specs/_cross_feature/reviews/{date}-{phase}-{stage}.md
        read_policy: create_or_update_stage_artifact
      - id: unresolved_cross_scope_items
        role: stage_entry_context
        source_type: carry_forward_register
        purpose: Read unresolved items carried forward from prior reviews or adjacent scopes before starting this stage.
        resolver:
          kind: project_state
          path: learning/workflow/carry-forward-register/reviewcompass-import.yaml
        read_policy: unresolved_items_only
      - id: vertical_intent_transfer_check
        role: review_prompt_requirement
        source_type: upstream_intent_transfer_contract
        purpose: Ensure review-wave preserves upstream intent while resolving cross-feature findings, and does not weaken or add unsupported requirements when carrying fixes across features.
        resolver:
          kind: static_reference
          path: docs/operations/SESSION_WORKFLOW_GUIDE.md#vertical-intent-transfer-review
        required_question: 上流の目的・責務境界・受入条件・禁止事項が、横断対処後の対象成果物へ欠落・弱体化・逸脱・未根拠追加なく引き継がれているか。
        read_policy: include_in_review_prompt

