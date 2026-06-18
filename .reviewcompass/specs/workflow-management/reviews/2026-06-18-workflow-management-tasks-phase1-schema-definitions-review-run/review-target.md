# workflow-management tasks triad-review target（phase1-schema-definitions）

run_id: 2026-06-18-workflow-management-tasks-phase1-schema-definitions-review-run
phase: tasks
gate: stages/tasks.yaml#triad-review
criteria: workflow_management_phase1_schema_definitions_tasks_triad_review

## 0. バリアント選定理由（実行前ゲートの記録）

- 使用バリアント：`implementation_review_independent_3way`（context: triad_review、API 3社独立）
- 役割：primary=anthropic-api/claude-sonnet-4-6、adversarial=openai-api/gpt-5.5、judgment=gemini-api/gemini-3.1-pro-preview
- 選定理由：design フェーズで使用したバリアントと同じ。API 3社独立（Anthropic・OpenAI・Google）で、CLI 経路を含まない API 専用のトリアードレビュー。

## 1. レビューの位置付け

reopen R-0（phase1-schema-definitions）の第3過程、workflow-management tasks フェーズの triad-review。

**背景**：requirements フェーズで AC10・AC11（`required_action` 語彙スキーマ・`next --json` 応答スキーマ定義）が承認され、design フェーズでその設計確定事項（§5.1/§5.2）が承認された。その下流影響として、tasks.md に T-015（Phase 1 最小スキーマ定義ファイルの作成）を追加した。本レビューはその追加内容の妥当性を確認する。

**目的**：
1. T-015 の責務・成果物・完了条件が requirements AC10/AC11 と整合しているか
2. T-015 の完了条件（3点）が `tests/tools/test_phase1_schema_definitions.py` の17テストと整合しているか
3. T-015 の前提タスク（T-004・T-011）の設定が妥当か
4. design.md §5.1/§5.2 の設計確定事項と T-015 の責務・成果物の対応が正確か

## 2. 変更内容（tasks.md への T-015 追加）

### 2.1 タスク総数の更新（前文）

変更前：
```
`workflow-management` 全体で 14 タスク（T-012 は ...
```

変更後：
```
`workflow-management` 全体で 15 タスク（T-012 は 2026-06-14 reopen R-0、T-013 は 2026-06-15 reopen R-0 decision-source-lint、T-014 は 2026-06-16 reopen R-0 operation registry / preflight、T-015 は 2026-06-18 reopen R-0 phase1-schema-definitions で追加）。
```

### 2.2 T-015 の追加（T-014 の後に挿入）

```markdown
### T-015：Phase 1 最小スキーマ定義ファイルの作成（Req 2 受入 10・11、reopen R-0 2026-06-18）

- **対応設計節**：design.md §軽量版検査スクリプトモデル §5（§5.1 required_action.schema.json・§5.2 next_action_response.schema.json）
- **対応要件**：Requirement 2 受入 10・11
- **責務**：`.reviewcompass/schema/required_action.schema.json` と `.reviewcompass/schema/next_action_response.schema.json` の 2 ファイルを TDD で作成する。スキーマ形式は JSON Schema Draft 2020-12。テストファイル `tests/tools/test_phase1_schema_definitions.py` の 17 テストを通過させることで実装の正しさを担保する。スキーマの設計仕様は design.md §5 を正本とし、コード内に語彙を直書きしない。
- **前提タスク**：T-004（`check-workflow-action.py` が参照するスキーマの実体）、T-011（回帰テスト統合）
- **成果物**：
  - `.reviewcompass/schema/required_action.schema.json`（Req 2 受入 10）
  - `.reviewcompass/schema/next_action_response.schema.json`（Req 2 受入 11）
- **完了条件**：
  1. `required_action.schema.json` が design §5.1 の設計（`$schema: https://json-schema.org/draft/2020-12/schema`・`$id: urn:reviewcompass:schema:required_action`・`type: string`・`enum` 19語彙）を満たす
  2. `next_action_response.schema.json` が design §5.2 の設計（最上位5フィールド必須・`next_action` 10フィールド必須・条件付き必須フィールド・`properties: { "verdict": false }`・`kind` 14値インライン enum・`$ref: "urn:reviewcompass:schema:required_action"`）を満たす
  3. `python3 -m pytest tests/tools/test_phase1_schema_definitions.py -v` の 17 テストが全て pass する（exit 0）
- **テスト要件（TDD：テストは作成済み、失敗状態）**：テストは `tests/tools/test_phase1_schema_definitions.py` に作成済みで commit 済み（失敗状態）。実装でテストを通過させる。テストの変更は禁止。
```

### 2.3 要件追跡表への2行追加

```
| Requirement 2 受入 10：required_action 語彙スキーマ定義 | T-015 |
| Requirement 2 受入 11：next_action_response 応答スキーマ定義 | T-015 |
```

## 3. レビュー観点

### 観点A：requirements との整合

- T-015 の対応要件「Requirement 2 受入 10・11」の記載は、requirements.md の実際の受入10・11の内容と整合しているか
- AC10（required_action 語彙スキーマ定義）、AC11（next_action_response 応答スキーマ定義）の責務をT-015 が適切にカバーしているか

### 観点B：設計（design.md §5）との整合

- T-015 の完了条件1が design §5.1 の設計確定事項（$schema・$id・type・enum 19語彙）と一致しているか
- T-015 の完了条件2が design §5.2 の設計確定事項（最上位5フィールド・next_action 10フィールド・properties: { "verdict": false }・kind 14値 enum・$ref 絶対URN）と一致しているか

### 観点C：テスト（tests/tools/test_phase1_schema_definitions.py）との整合

- 完了条件3が「17テスト全pass」と記載しているが、テストの17件の内訳と T-015 が要求する仕様が対応しているか
- テスト `test_next_action_required_fields` が要求する10フィールドは design §5.2 の必須フィールド10つと一致しているか

### 観点D：前提タスクの妥当性

- T-004 が前提タスクとして適切か（`check-workflow-action.py` がスキーマを参照するため）
- T-011 が前提タスクとして適切か（回帰テスト統合のため）
- T-001〜T-003 が前提として不要な理由に明らかな誤りはないか

## 4. 参照文書（レビューに必要な関連情報）

### 4.1 Requirement 2 受入 10・11 の本文（requirements.md から抜粋）

```
受入 10（required_action 語彙スキーマ定義）：
`required_action` の取り得る値を JSON Schema Draft 2020-12 形式で定義したファイル（`.reviewcompass/schema/required_action.schema.json`）が存在し、D-003 §6 の優先順位順に 19 語彙を列挙した `enum` フィールドを持ち、`$id: urn:reviewcompass:schema:required_action` を持つ。このスキーマは `next --json` の機械検証に使用できる。

受入 11（next_action_response 応答スキーマ定義）：
`next --json` の出力が準拠すべき JSON Schema Draft 2020-12 形式のスキーマファイル（`.reviewcompass/schema/next_action_response.schema.json`）が存在し、最上位に `verdict`・`exit_code`・`next_action`・`reasons`・`current_state` の 5 フィールドを必須とし、`next_action` オブジェクトに `kind`・`required_action`・`active_gate`・`feature`・`phase`・`stage`・`required_feature_scope`・`blocked_by`・`future_gates`・`state_refs` の 10 フィールドを必須とし、`verdict` フィールドを `next_action` 内で禁止し（`properties: { "verdict": false }`）、`next_action.required_action` が `.reviewcompass/schema/required_action.schema.json` の語彙に限定され（`$ref: "urn:reviewcompass:schema:required_action"`）、`kind` が 14 値のインライン `enum` で定義されている。
```

### 4.2 テスト17件の内訳

**TestRequiredActionSchema**（required_action.schema.json のテスト、9件）：

1. `test_file_exists` - ファイルの存在確認
2. `test_valid_json` - JSON として有効であること
3. `test_has_schema_id` - `$schema` と `$id` の存在確認
4. `test_type_is_string` - `type` が `"string"` であること
5. `test_enum_has_exactly_19_values` - `enum` がちょうど19値であること
6. `test_all_expected_values_present` - 期待する19語彙が全て存在すること
7. `test_no_extra_values` - 余分な値がないこと
8. `test_each_value_validates` - 各語彙値がスキーマを通過すること
9. `test_invalid_value_rejected` - 不正な値が拒否されること

**TestNextActionResponseSchema**（next_action_response.schema.json のテスト、8件）：

1. `test_file_exists` - ファイルの存在確認
2. `test_valid_json` - JSON として有効であること
3. `test_has_schema_id` - `$schema` と `$id` の存在確認
4. `test_top_level_is_object` - `type` が `"object"` であること
5. `test_required_top_level_fields` - 最上位5フィールド（verdict/exit_code/next_action/reasons/current_state）必須
6. `test_next_action_required_fields` - next_action の10フィールド（kind/required_action/active_gate/feature/phase/stage/required_feature_scope/blocked_by/future_gates/state_refs）必須
7. `test_required_action_ref_or_enum` - `next_action.required_action` に `$ref` または `enum` が存在すること
8. `test_current_next_json_output_validates` - 現在の `next --json` 出力が最上位5フィールドを持つこと（部分検証）

合計：17テスト。

### 4.3 design.md §3 との不一致メモ（参考情報）

design.md §3（`next --json` 選択器モデル）では「共通フィールドは `kind`、`required_action`、`active_gate`、`feature`、`phase`、`stage`、`blocked_by`、`action_parameters`、`state_refs`」と記述されているが、design.md §5.2 の「必須フィールド（10つ）」では `action_parameters` はなく `required_feature_scope` と `future_gates` が含まれている。T-015 の完了条件は §5.2 を正本としており、テストも §5.2 の10フィールドを要求しているため、T-015 の実装への影響はない。しかし §3 と §5.2 の間の不一致が設計文書内に存在することはレビュー時の確認事項となりうる。
