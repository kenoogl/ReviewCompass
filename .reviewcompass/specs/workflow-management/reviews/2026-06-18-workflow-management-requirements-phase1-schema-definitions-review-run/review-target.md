# workflow-management requirements triad-review target

run_id: 2026-06-18-workflow-management-requirements-phase1-schema-definitions-review-run
phase: requirements
gate: stages/requirements.yaml#triad-review
criteria: workflow_management_phase1_schema_definitions_requirements_reopen_triad_review

## 0. variant 選定理由（実行前ゲートの記録）

- 使用 variant：`implementation_review_independent_3way`（context: triad_review、API 3 社独立）
- 役割：primary=anthropic-api/claude-sonnet-4-6、adversarial=openai-api/gpt-5.5、judgment=gemini-api/gemini-3.1-pro-preview
- 選定理由：Claude Code 操縦時の triad_review 既定 variant（正本は config/api-settings.yaml コメント「接尾辞なしの independent_3way 系は Claude Code 操縦時の既定」）。CLI 経路を含む default variant は Claude Code 実行環境と合わないため使用しない。

## 1. レビューの位置付け

reopen R-0（分類記録 `docs/reviews/reopen-classification-2026-06-18-wm-phase1-schema-definitions.md`）の
第3過程、workflow-management requirements フェーズの triad-review。

背景：Phase 0（D-003 選択層 TDD 実装）の開始前提として、`required_action` 語彙スキーマ（受入10）と
`next --json` 応答スキーマ（受入11）の定義を要件化する。根拠は
`docs/notes/2026-06-18-integrated-design-selection-execution-layers.md` §7 item 2 および
`docs/notes/working/2026-06-16-next-json-unique-state-redesign.md` §4.1・§4.2。
**実装より先に仕様を確定する正順**であり、TDD の失敗テスト（`tests/tools/test_phase1_schema_definitions.py`、
17テスト）は作成済み。現時点でスキーマファイルは存在しない（意図的）。

## 2. 変更内容（requirements.md、受入10・11の追記）

### 2.1 受入10（Requirement 2 AC10）

```text
10. 本機能は `required_action` の19語彙（D-003 §6 の19段階優先順位に対応）を
    `.reviewcompass/schema/required_action.schema.json` として JSON Schema 形式で定義する。
    語彙は D-003 §6 の優先順位順に列挙し、`repair_workflow_state`〜`completed` の19値を
    `enum` として持つ。語彙の追加・変更はこのスキーマファイルの修正で完結し、実装コード側の
    列挙はこのファイルを正本とする。
```

### 2.2 受入11（Requirement 2 AC11）

```text
11. 本機能は `next --json` の目標応答スキーマを `.reviewcompass/schema/next_action_response.schema.json`
    として JSON Schema 形式で定義する。本スキーマは受入9が定める振る舞い契約（唯一アクション選択・
    進行中作業単位の有無による null/非 null の切り替え）をスキーマとして表現する。
    （1）最上位の必須フィールドは `verdict`・`exit_code`・`next_action`・`reasons`・`current_state` の5つ。
        `verdict` は最上位だけに置き `next_action` 内には含めない。
    （2）`next_action` の必須フィールドは10個（kind, required_action, active_gate, feature, phase, stage,
        required_feature_scope, blocked_by, future_gates, state_refs）。
        `repair_reasons`（配列）は `repair_workflow_state` 時に必須となる条件付きフィールド。
        `action_parameters`（オブジェクト）は `run_maintenance` 等で必須となる条件付きフィールド。
    （3）`feature` の取り得る値は「単一フィーチャー名」・`"all_features"`（真に横断的な場合のみ）・
        null（進行中作業単位がない場合）の3種類のみ。複数フィーチャーは `required_feature_scope` や
        `future_gates` に置く。
    （4）受入9の null/非 null 規則：進行中作業単位がない場合は feature/phase/stage/active_gate がすべて
        null。作業単位がある場合のみ非 null。
    （5）後方互換のため `pending_gates`・`next_pending_gate` はオプションフィールド。正本フィールドは
        `future_gates`・`active_gate`。
    （6）`required_action` の値ごとのフィールド制約（D-003 §4.2 確定）：
        ① commit_stop_point: active_gate=null, phase=null, stage=null, blocked_by.type="commit_stop_point"
        ② run_reopen_pending_gate: active_gate 非 null, phase/stage は active_gate と一致, blocked_by=null
        ③ run_reopen_drafting: active_gate は stages/<phase>.yaml#drafting 形式
        ④ repair_workflow_state: active_gate=null, phase=null, stage=null, repair_reasons に修復理由を含める
        ⑤ wait_for_human_decision: blocked_by.type で停止理由を区別
        ⑥ run_maintenance: action_parameters に maintenance_action 等6フィールドを含める
```

### 2.3 Change Intent への追記

requirements.md の Change Intent セクションに 2026-06-18 R-0 の由来を追記済み（コミット 025603bd）。

## 3. 既存コンテキスト

受入10・11は次の既存受入基準と密接に関連する：

- 受入6（next サブコマンド）：AC10/AC11 のスキーマが対象とする `next --json` の出力仕様の正本
- 受入9（唯一 action selector）：AC11 が null/非 null 規則・active workflow unit を引用している
- D-003 §4.2、§6：AC10 の19語彙と AC11 の値制約の根拠文書

## 4. 審査対象ファイル

- `.reviewcompass/specs/workflow-management/requirements.md`（受入10・11の追記箇所を重点的に確認）
- `docs/reviews/reopen-classification-2026-06-18-wm-phase1-schema-definitions.md`（分類根拠）

## 5. レビュー観点

1. 受入10：スキーマファイルパス（`.reviewcompass/schema/required_action.schema.json`）は適切か。19値の
   enum という要件は D-003 §6 の優先順位リストと整合するか。「実装コード側の列挙はこのファイルを正本
   とする」という依存方向は明確か。

2. 受入11：5フィールドの最上位必須フィールドリストは完全か（`verdict` の配置制約を含む）。

3. 受入11：10フィールドの `next_action` 必須フィールドリストは AC9 の振る舞い契約を正しく反映するか。
   `action_parameters` が universal ではなく条件付きとして正確に分類されているか。

4. 受入11：`feature` の3種類（単一名・`"all_features"`・null）という制約は AC9 の「唯一 action
   selector」と整合するか。リスト型を許容しないという制約は明示されているか。

5. 受入11（3）：null/非 null 規則は AC9 の「active workflow unit の有無」を正確に写しているか。
   条件（active gate 実行中のみ非 null）は曖昧でないか。

6. 受入11（4）：後方互換フィールド（`pending_gates`・`next_pending_gate`）のオプション扱いは、
   既存コードベースとの互換性を維持するうえで十分に規定されているか。

7. 受入11（5）：6制約（①〜⑥）は D-003 §4.2 の制約集合を欠落なくカバーするか。スキーマ上の
   表現方法（design で確定）という留保は適切か。

8. 受入10・11の相互参照（AC11 が AC10 のスキーマを参照する構造）は明確に記述されているか。

9. 受入10・11は LLM/provider/model に依存しない要件として記述されているか（実装詳細を要件レベルに
   持ち込んでいないか）。

10. 受入10・11の追記は、下流フェーズ（design/tasks/implementation）で再展開が必要な影響をもたらすか。
    recheck フラグ（`upstream_change_pending: true`、`impacted_downstream_phases: [design, tasks, implementation]`）
    との整合はとれているか。

## 6. 期待する出力

構造化所見のみを返す。severity `ERROR` はブロッカー（requirements review-wave 通過前に必須修正）、
`WARN` は review-wave 前に修正すべき事項、`INFO` は非ブロッカーの観察。
各所見に `finding_id`、`severity`、`target`（該当受入番号または条項）、`description`、`recommendation` を含める。
