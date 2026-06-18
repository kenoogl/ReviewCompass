# workflow-management implementation triad-review target（phase1-schema-definitions）

run_id: 2026-06-19-workflow-management-implementation-phase1-schema-definitions-review-run
phase: implementation
gate: stages/implementation.yaml#triad-review
criteria: workflow_management_phase1_schema_definitions_implementation_triad_review

## 0. バリアント選定理由（実行前ゲートの記録）

- 使用バリアント：`implementation_review_independent_3way`（context: triad_review、API 3社独立）
- 役割：primary=anthropic-api/claude-sonnet-4-6、adversarial=openai-api/gpt-5.5、judgment=gemini-api/gemini-3.1-pro-preview
- 選定理由：design・tasks フェーズで使用したバリアントと同じ。API 3社独立（Anthropic・OpenAI・Google）で、CLI 経路を含まない API 専用のトリアードレビュー。

## 1. レビューの位置付け

reopen R-0（phase1-schema-definitions）の implementation フェーズ、T-015 実装の triad-review。

**背景**：
- requirements フェーズで AC10・AC11（`required_action` 語彙スキーマ・`next --json` 応答スキーマ定義）が承認された。
- design フェーズで §5.1/§5.2 の設計確定事項が承認された。
- tasks フェーズで T-015 の完了条件が承認された。
- 本レビューは T-015 の実装成果物（2 スキーマファイル）が仕様を正確に満たしているかを確認する。

**テスト済み事項（機械検証済み、本レビューで再確認不要）**：
- ファイルの存在確認
- JSON として有効であること
- `$schema` と `$id` が存在すること
- `required_action.schema.json` の `type: "string"` と `enum` 19値（過不足なし）
- `required_action.schema.json` の各値がスキーマを通過し、不正値が拒否されること
- `next_action_response.schema.json` の最上位 `type: "object"` と必須5フィールド
- `next_action_response.schema.json` の `next_action` 必須10フィールド
- `next_action_response.schema.json` の `required_action` に `$ref` または `enum` が存在すること
- `next --json` の出力に最上位5フィールドが存在すること

**本レビューで確認が必要な事項（テストでは検証できない部分）**：
1. `required_action` の `enum` 順序が D-003 §6 の優先順位順と一致しているか
2. `next_action` 内の `verdict: false` が仕様の意図（`verdict` を `next_action` 内で禁止する）を正しく実現しているか
3. `kind` の14値とその順序が仕様と一致しているか
4. `$ref: "urn:reviewcompass:schema:required_action"` の形式が正しいか（絶対 URN による基底 URI 解決不要の意図と合致するか）
5. 条件付き必須フィールドの `if/then` 定義が仕様の意図を正確に実現しているか
6. 仕様が意図した設計決定（`additionalProperties` 非指定の前向き拡張・後ろ向き互換の意図）と実装が合致しているか

## 2. 仕様（design.md §5）

### §5.1 required_action.schema.json の仕様確定事項

- `$schema`: `https://json-schema.org/draft/2020-12/schema`
- `$id`: `urn:reviewcompass:schema:required_action`
- `type`: `string`
- `enum`: D-003 §6 の優先順位順に19値（下記の順が正本）

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

### §5.2 next_action_response.schema.json の仕様確定事項

**最上位構造**：
- `$schema`: `https://json-schema.org/draft/2020-12/schema`
- `$id`: `urn:reviewcompass:schema:next_action_response`
- `type`: `object`
- 必須フィールド（5つ）: `verdict`・`exit_code`・`next_action`・`reasons`・`current_state`
- `additionalProperties` は指定しない（前向き拡張用：将来フィールドを追加してもスキーマ改訂なしに対応できるよう段階的拡張を妨げない。`$comment` に意図を記録する）

**`next_action` オブジェクト**：
- `type`: `object`
- 必須フィールド（10つ）: `kind`・`required_action`・`active_gate`・`feature`・`phase`・`stage`・`required_feature_scope`・`blocked_by`・`future_gates`・`state_refs`
- `additionalProperties` は指定しない（後ろ向き互換用：旧バージョンのツールが出力する `pending_gates`・`next_pending_gate` 等を許容するため。`$comment` に意図を記録する）
- `properties: { "verdict": false }`: `verdict` フィールドを `next_action` 内で明示禁止（`additionalProperties` を開放したまま特定フィールドのみを禁止する最も局所的な方法）

**`next_action` フィールド型定義**：

| フィールド | 型 |
|---|---|
| `kind` | string enum（14値インライン定義） |
| `required_action` | `$ref: "urn:reviewcompass:schema:required_action"`（絶対 URN 参照により基底 URI 解決不要） |
| `active_gate` | string または null |
| `feature` | string または null |
| `phase` | string または null |
| `stage` | string または null |
| `required_feature_scope` | array of string |
| `blocked_by` | object または null |
| `future_gates` | array |
| `state_refs` | object |

**`kind` フィールドの14値（優先順位順）**：

| 優先順位 | 値 |
|---:|---|
| 1 | `resume_in_progress` |
| 2 | `reopen_in_progress` |
| 3 | `maintenance_in_progress` |
| 4 | `reopen_classification_required` |
| 5 | `post_write_verification` |
| 6 | `lightweight_self_check` |
| 7 | `post_write_policy_violation` |
| 8 | `post_write_human_decision_required` |
| 9 | `stage` |
| 10 | `cross_feature_stage` |
| 11 | `upstream_recheck` |
| 12 | `feature_definition_required` |
| 13 | `completed` |
| 14 | `unknown` |

**条件付き必須フィールド（`if/then` 構文で `next_action` 内に定義）**：
- `repair_reasons`（`type: array, minItems: 1`）: `required_action = "repair_workflow_state"` のとき必須
- `action_parameters`（`type: object`）: `required_action = "run_maintenance"` のとき必須。サブフィールド必須6つ（`maintenance_action`・`allowed_scope`・`allowed_files`・`completion_conditions`・`active_stack_frame_id`・`parent_frame_id`）

## 3. 実装成果物

### 3.1 required_action.schema.json

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "urn:reviewcompass:schema:required_action",
  "type": "string",
  "enum": [
    "repair_workflow_state",
    "run_post_write_verification",
    "wait_for_human_decision",
    "record_human_decision",
    "run_maintenance",
    "advance_reopen_after_commit_stop_point",
    "commit_stop_point",
    "draft_reopen_plan_candidates",
    "apply_approved_reopen_plan",
    "advance_reopen_after_approval_stop_point",
    "repair_canonical_documents",
    "run_reopen_drafting",
    "run_reopen_pending_gate",
    "collect_required_decisions",
    "finalize_reopen",
    "draft_reopen_classification",
    "run_reopen_start",
    "run_workflow_stage",
    "completed"
  ]
}
```

### 3.2 next_action_response.schema.json

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "urn:reviewcompass:schema:next_action_response",
  "$comment": "additionalProperties は指定しない（前向き拡張用：将来の実装で新フィールドを追加してもスキーマ改訂なしに対応できるよう、段階的拡張を妨げない）",
  "type": "object",
  "required": ["verdict", "exit_code", "next_action", "reasons", "current_state"],
  "properties": {
    "verdict": { "type": "string" },
    "exit_code": { "type": "integer" },
    "next_action": {
      "$comment": "additionalProperties は指定しない（後ろ向き互換用：旧バージョンのツールが出力する pending_gates・next_pending_gate 等を許容するため。最上位の前向き拡張とは目的が異なる）",
      "type": "object",
      "required": [
        "kind",
        "required_action",
        "active_gate",
        "feature",
        "phase",
        "stage",
        "required_feature_scope",
        "blocked_by",
        "future_gates",
        "state_refs"
      ],
      "properties": {
        "verdict": false,
        "kind": {
          "type": "string",
          "enum": [
            "resume_in_progress",
            "reopen_in_progress",
            "maintenance_in_progress",
            "reopen_classification_required",
            "post_write_verification",
            "lightweight_self_check",
            "post_write_policy_violation",
            "post_write_human_decision_required",
            "stage",
            "cross_feature_stage",
            "upstream_recheck",
            "feature_definition_required",
            "completed",
            "unknown"
          ]
        },
        "required_action": {
          "$ref": "urn:reviewcompass:schema:required_action"
        },
        "active_gate": {
          "oneOf": [{ "type": "string" }, { "type": "null" }]
        },
        "feature": {
          "oneOf": [{ "type": "string" }, { "type": "null" }]
        },
        "phase": {
          "oneOf": [{ "type": "string" }, { "type": "null" }]
        },
        "stage": {
          "oneOf": [{ "type": "string" }, { "type": "null" }]
        },
        "required_feature_scope": {
          "type": "array",
          "items": { "type": "string" }
        },
        "blocked_by": {
          "oneOf": [{ "type": "object" }, { "type": "null" }]
        },
        "future_gates": {
          "type": "array"
        },
        "state_refs": {
          "type": "object"
        },
        "pending_gates": {
          "type": "array"
        }
      },
      "allOf": [
        {
          "if": {
            "properties": { "required_action": { "const": "repair_workflow_state" } },
            "required": ["required_action"]
          },
          "then": {
            "required": ["repair_reasons"],
            "properties": {
              "repair_reasons": {
                "type": "array",
                "minItems": 1
              }
            }
          }
        },
        {
          "if": {
            "properties": { "required_action": { "const": "run_maintenance" } },
            "required": ["required_action"]
          },
          "then": {
            "required": ["action_parameters"],
            "properties": {
              "action_parameters": {
                "type": "object",
                "required": [
                  "maintenance_action",
                  "allowed_scope",
                  "allowed_files",
                  "completion_conditions",
                  "active_stack_frame_id",
                  "parent_frame_id"
                ]
              }
            }
          }
        }
      ]
    },
    "reasons": { "type": "array" },
    "current_state": { "type": "object" }
  }
}
```

## 4. テスト実行結果（参考）

```
$ python3 -m pytest tests/tools/test_phase1_schema_definitions.py -v
collected 17 items

TestRequiredActionSchema::test_all_expected_values_present PASSED
TestRequiredActionSchema::test_each_value_validates PASSED
TestRequiredActionSchema::test_enum_has_exactly_19_values PASSED
TestRequiredActionSchema::test_file_exists PASSED
TestRequiredActionSchema::test_has_schema_id PASSED
TestRequiredActionSchema::test_invalid_value_rejected PASSED
TestRequiredActionSchema::test_no_extra_values PASSED
TestRequiredActionSchema::test_type_is_string PASSED
TestRequiredActionSchema::test_valid_json PASSED
TestNextActionResponseSchema::test_current_next_json_output_validates PASSED
TestNextActionResponseSchema::test_file_exists PASSED
TestNextActionResponseSchema::test_has_schema_id PASSED
TestNextActionResponseSchema::test_next_action_required_fields PASSED
TestNextActionResponseSchema::test_required_action_ref_or_enum PASSED
TestNextActionResponseSchema::test_required_top_level_fields PASSED
TestNextActionResponseSchema::test_top_level_is_object PASSED
TestNextActionResponseSchema::test_valid_json PASSED

17 passed in 0.68s
```

## 5. レビュー依頼

上記の仕様（§2）と実装成果物（§3）を照合し、以下の観点から分析してください。

テストで機械検証済みの事項（§1 テスト済み事項）は確認不要です。テストでは検証できない観点（§1 本レビューで確認が必要な事項）を中心に分析してください。

**観点A：required_action.schema.json の enum 順序**

`enum` の並び順が仕様（§2 §5.1 の優先順位表）と一致しているか確認してください。位置ズレ・欠落・余分な値がないかを確認してください。

**観点B：next_action_response.schema.json の verdict 禁止**

`properties: { "verdict": false }` という実装が、JSON Schema Draft 2020-12 において「`verdict` フィールドを `next_action` オブジェクト内で禁止する」という仕様の意図を正しく実現しているか分析してください。意図と異なる挙動が生じる可能性があれば指摘してください。

**観点C：kind の14値**

`next_action` 内 `kind` の enum が、仕様（§2 §5.2 の kind フィールドの値域）と値・順序ともに一致しているか確認してください。

**観点D：$ref の形式**

`required_action` フィールドの `"$ref": "urn:reviewcompass:schema:required_action"` という絶対 URN 参照が、JSON Schema Draft 2020-12 の仕様に照らして適切か分析してください。基底 URI 解決が不要になるという意図と合致しているかも含めて評価してください。

**観点E：条件付き必須フィールドの if/then 定義**

`allOf` に収めた2つの `if/then` ブロックが、仕様（§2 §5.2 条件付き必須フィールド）の意図を JSON Schema Draft 2020-12 として正しく実現しているか分析してください。条件が誤って発動するケース、発動しないケース、または `then` の効果が意図通り働かないケースがあれば指摘してください。

**観点F：設計意図との整合**

`additionalProperties` 非指定の判断（前向き拡張・後ろ向き互換）、`pending_gates` の型定義（後方互換フィールド）、`oneOf` による nullable 型定義など、仕様で明示された設計決定が実装に正しく反映されているか評価してください。

各観点について、「仕様を満たしている」「仕様と異なる」「改善の余地がある」のいずれかを判定し、その根拠を示してください。重大な問題（must-fix）、軽微な問題（should-fix）、許容範囲（leave-as-is）の3段階で重要度を示してください。
