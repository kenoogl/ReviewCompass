# workflow-management design triad-review target（phase1-schema-definitions）

run_id: 2026-06-18-workflow-management-design-phase1-schema-definitions-review-run
phase: design
gate: stages/design.yaml#triad-review
criteria: workflow_management_phase1_schema_definitions_design_triad_review

## 0. バリアント選定理由（実行前ゲートの記録）

- 使用バリアント：`implementation_review_independent_3way`（context: triad_review、API 3社独立）
- 役割：primary=anthropic-api/claude-sonnet-4-6、adversarial=openai-api/gpt-5.5、judgment=gemini-api/gemini-3.1-pro-preview
- 選定理由：Claude Code 操縦時の triad_review 既定バリアント（正本は config/api-settings.yaml コメント「接尾辞なしの independent_3way 系は Claude Code 操縦時の既定」）。CLI 経路を含む default バリアントは Claude Code 実行環境と合わないため使用しない。

## 1. レビューの位置付け

reopen R-0（phase1-schema-definitions）の第3過程、workflow-management design フェーズの triad-review。

背景：requirements フェーズで AC10・AC11（`required_action` 語彙スキーマ・`next --json` 応答スキーマ定義）が承認された。その下流影響として、design.md に AC10・AC11 の設計確定事項（スキーマ定義節 §5）を追記した。本レビューはその追記内容の妥当性を確認する。

目的：
- §5.1（`required_action.schema.json`）の設計確定事項（`$schema`・`$id`・`type`・`enum` 19語彙順）が、requirements.md 受入10・D-003 §6 と整合するか確認する
- §5.2（`next_action_response.schema.json`）の設計確定事項（最上位5フィールド・`next_action` 10フィールド・条件付き必須フィールド・`$ref`・後方互換フィールド整合規則）が、requirements.md 受入11と整合するか確認する
- ファイル配置（`.reviewcompass/schema/` 配下）とアーキテクチャ図への追記が設計として整合するか確認する

## 2. 変更内容（design.md への追記）

### 2.1 ヘッダ日付の更新（1行）

```
最終更新：2026-06-18（Req 2 受入 10・11 スキーマ定義節を追記、reopen R-0 対応）
```

### 2.2 リポジトリ配置図への追記（2行）

`tools/check-workflow-action.py` の後に追加：

```
├── .reviewcompass/schema/               # ワークフロー管理スキーマ定義（Req 2 受入 10・11）
│   ├── required_action.schema.json      # required_action 19語彙スキーマ（Req 2 受入 10）
│   └── next_action_response.schema.json # next --json 応答スキーマ（Req 2 受入 11）
```

### 2.3 §5 スキーマ定義節の追加（Req 2 末尾）

Req 3「起草者と判定者の分離モデル」の手前に追加：

---

**§5 スキーマ定義（Phase 1 最小スキーマ、Req 2 受入 10・11）**

本節は `next --json` の語彙と応答形式を機械検証可能な JSON Schema として定義する。2 ファイルを `.reviewcompass/schema/` 配下に置く。スキーマ形式はいずれも JSON Schema Draft 2020-12 を使う。実装コードはこの 2 ファイルを語彙と応答構造の正本として参照し、コード内に語彙を直書きしない。

**§5.1 required_action.schema.json（Req 2 受入 10）**

`required_action` の取り得る値を列挙する語彙ファイル。

- **`$schema`**：`https://json-schema.org/draft/2020-12/schema`
- **`$id`**：`urn:reviewcompass:schema:required_action`
- **`type`**：`string`
- **`enum`**：D-003 §6 の優先順位順に 19 値を列挙する（この順が正本）

| 優先順位 | 値 |
|---:|---|
| 1 | `repair_workflow_state` |
| 2 | `run_post_write_verification` |
| 3 | `wait_for_human_decision` |
| 4 | `record_human_decision` |
| 5 | `run_maintenance` |
| 6 | `advance_reopen_after_commit_stop_point` |
| 7 | `commit_stop_point` |
| 8 | `draft_reopen_plan_candidates` |
| 9 | `apply_approved_reopen_plan` |
| 10 | `advance_reopen_after_approval_stop_point` |
| 11 | `repair_canonical_documents` |
| 12 | `run_reopen_drafting` |
| 13 | `run_reopen_pending_gate` |
| 14 | `collect_required_decisions` |
| 15 | `finalize_reopen` |
| 16 | `draft_reopen_classification` |
| 17 | `run_reopen_start` |
| 18 | `run_workflow_stage` |
| 19 | `completed` |

語彙の追加・変更はこのファイルの `enum` 修正で完結する。

**§5.2 next_action_response.schema.json（Req 2 受入 11）**

`next --json` の目標応答スキーマ。

**最上位構造の設計確定事項**

- **`$schema`**：`https://json-schema.org/draft/2020-12/schema`
- **`$id`**：`urn:reviewcompass:schema:next_action_response`
- **`type`**：`object`
- **必須フィールド（5つ）**：`verdict`（文字列）・`exit_code`（整数）・`next_action`（オブジェクト）・`reasons`（配列）・`current_state`（オブジェクト）
- **`additionalProperties`**：最上位は指定しない（実装の段階的拡張を妨げない）

**`next_action` オブジェクトの設計確定事項**

- **`type`**：`object`
- **必須フィールド（10つ）**：`kind`・`required_action`・`active_gate`・`feature`・`phase`・`stage`・`required_feature_scope`・`blocked_by`・`future_gates`・`state_refs`
- **`additionalProperties`**：指定しない（後方互換フィールド `pending_gates`・`next_pending_gate` 等を許容する）

**`next_action` フィールド型定義**

| フィールド | 型 |
|---|---|
| `kind` | string（値域は実装定義、WORKFLOW_NAVIGATION.md §2 の判定結果種別に対応） |
| `required_action` | `$ref: "./required_action.schema.json"`（19語彙に限定） |
| `active_gate` | string または null（作業単位がない場合は null） |
| `feature` | string または null（単一機能名・`"all_features"`・null の 3 種） |
| `phase` | string または null |
| `stage` | string または null |
| `required_feature_scope` | array of string |
| `blocked_by` | object または null |
| `future_gates` | array |
| `state_refs` | object |

**条件付き必須フィールド（`if/then` 構文で `next_action` 内に定義）**

- `repair_reasons`（非空配列）：`required_action = "repair_workflow_state"` のとき必須
- `action_parameters`（オブジェクト）：`required_action = "run_maintenance"` のとき必須。サブフィールド必須 6 つ（`maintenance_action`・`allowed_scope`・`allowed_files`・`completion_conditions`・`active_stack_frame_id`・`parent_frame_id`）

**後方互換フィールドの整合規則**

`pending_gates` が存在する場合は `future_gates` と一致させること（実装側の不変条件。JSON Schema では `if/then` または `unevaluatedProperties` で表現し、実装で保証する）。

---

### 2.4 変更意図節への追記

```text
- 2026-06-18 の reopen R-0（phase1-schema-definitions）として、§軽量版検査スクリプトモデル §5 に
  `required_action.schema.json`・`next_action_response.schema.json` のスキーマ定義節を追加し、
  ファイル配置・`$schema`・`$id`・`enum` 19語彙順・`next_action` 必須フィールド 10 個・
  条件付き必須フィールド（`repair_reasons`・`action_parameters`）・`$ref` による語彙参照・
  後方互換フィールド整合規則を確定した。§全体構造のリポジトリ配置図にも 2 ファイルを追記した。
  本改訂は仕様確定後に TDD で実装する正順の手続きである（失敗テスト
  `tests/tools/test_phase1_schema_definitions.py` は作成済み）。
```

## 3. 既存コンテキスト

§5 の設計は次の上流文書から直接導出した：

- **requirements.md 受入10**：`required_action.schema.json` のパス・JSON Schema 形式・19語彙列挙・実装コードの正本参照要件
- **requirements.md 受入11**：`next_action_response.schema.json` のパス・JSON Schema 形式・5フィールド最上位必須・10フィールド `next_action` 必須・条件付き必須フィールド・`$ref` 参照・後方互換フィールド
- **D-003 §6**：19語彙の優先順位（`repair_workflow_state`〜`completed`）
- **D-003 §4.2**：条件付き必須フィールドの値制約詳細（`action_parameters` の 6 サブフィールド名）

テストファイル `tests/tools/test_phase1_schema_definitions.py` が先行して作成済みであり、17テストが失敗している状態が正常（TDD 手順）。

## 4. 審査対象ファイル

主要対象：
- `.reviewcompass/specs/workflow-management/design.md`（追加箇所を重点的に確認）

参照対象（根拠確認用）：
- `.reviewcompass/specs/workflow-management/requirements.md`（受入10・11）
- `tests/tools/test_phase1_schema_definitions.py`（17テストの期待値との整合）

## 5. レビュー観点

1. **§5.1 `required_action.schema.json`の完全性**：19語彙の列挙順が D-003 §6 の優先順位と整合するか。`type: string` と `enum` の組み合わせは JSON Schema Draft 2020-12 として正しいか。

2. **§5.2 最上位5フィールドの妥当性**：`verdict`・`exit_code`・`next_action`・`reasons`・`current_state` の5つが `next --json` の実際の出力契約を正しく反映するか。`verdict` が最上位にのみあり `next_action` 内には含まれないという制約（受入11(1)）が設計に反映されているか。

3. **§5.2 `next_action` 10フィールドの妥当性**：10フィールドの列挙に漏れや余分がないか。`feature` の型定義（単一名・`"all_features"`・null の3種、リスト型不可）が受入11(3) と整合するか。

4. **条件付き必須フィールドの設計**：`if/then` 構文を使う設計が JSON Schema Draft 2020-12 として有効か。`repair_reasons` の「非空配列」という制約が表現できるか。`action_parameters` の 6 サブフィールドの必須化が設計として実装可能か。

5. **`$ref` 参照の妥当性**：`$ref: "./required_action.schema.json"` という相対パス参照が JSON Schema Draft 2020-12 で有効か。`$id` に `urn:` 形式を使う場合の相対パス解決に問題がないか。

6. **後方互換フィールド整合規則の明確性**：「`pending_gates` が存在する場合は `future_gates` と一致させること」という記述が実装者に対して明確な契約を与えるか。「実装側の不変条件」と「JSON Schema での表現」の間の責務分離が適切か。

7. **ファイル配置の整合性**：`.reviewcompass/schema/` というパスが、既存の `.reviewcompass/` 配下のディレクトリ体系と整合するか。ツール（`tools/check-workflow-action.py`）からスキーマファイルを参照する際の相対パス解決に問題がないか。

8. **設計と要件の完全性**：§5 の設計内容が受入10・11 の全項目を網羅しているか、または意図的に後回しにした事項があればその記録が適切か。
