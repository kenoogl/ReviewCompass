# workflow-management implementation review — MWP-0: reason vs reasons separation

run_id: 2026-06-27-workflow-management-implementation-mwp0-reason-review-run
criteria_id: wm-implementation-mwp0-reason-2026-06-27
phase: implementation
stage: triad-review
variant: implementation_review_independent_3way

## Change Summary

MWP-0 T-020 の先送り事項(b) として、`next_action` 内の `reason` フィールドと最上位の `reasons` 配列の責務分離を設計書と実装で明確化することが求められていた。

## Review Question

設計書（design §5.3）が示す `reason` フィールド（`next_action` 内）と最上位の `reasons` 配列の意味的な区別が、スキーマと設計書において十分に定義されているかを独立して分析してほしい。あなたが気づいた問題・疑問を率直に示してほしい。

分析は上記1点に限定せず、この責務分離に関して問題と判断したことは自由に指摘してよい。

## Scope / Out of Scope

**対象**：
- `next_action_response.schema.json` における `reason` フィールドの定義状況
- `design §5.2`・`§5.3` における `reason` と `reasons` の説明
- T-020 先送り事項(b)の達成状況

**対象外**：
- if/then 制約の完全性（別プロンプトで審査）
- kind 値分離（別プロンプトで審査）
- commit / push / spec.json 更新 / phase 完了 / 人間承認代行

---

## SOURCE MATERIAL: タスク定義（T-020 先送り事項(b)・完了条件）

```text
【T-020 先送り事項(b)】
next_action 内の reason フィールドと最上位の reasons 配列の責務差を設計書と実装で明確化する。

【T-020 完了条件（reason に関連する条件は完了条件の一覧に明示されていない）】
1. next --json の kind 値域が7値に限定されること（kind 分離）
2. commit-preflight サブコマンドが3値の kind を返すこと（kind 分離）
3. スキーマの if/then 制約の失敗テストが作成され通過すること
4. WORKFLOW_NAVIGATION.md の更新
5. 廃止表現の統一

注：先送り事項(b)（reason vs reasons の責務明確化）に対応する完了条件は T-020 の完了条件一覧に
明示されていない。
```

## SOURCE MATERIAL: 設計（design §5.2・§5.3）

```text
【design §5.2 — 最上位必須フィールド】
next_action_response.schema.json の必須フィールド（5つ）：
  verdict（文字列）・exit_code（整数）・next_action（オブジェクト）・reasons（配列）・current_state（オブジェクト）

next_action 必須フィールド（10つ）：
  kind・required_action・active_gate・feature・phase・stage・
  required_feature_scope・blocked_by・future_gates・state_refs
```

```text
【design §5.3 — 全 kind 共通フィールド（next_action 内）】
| フィールド      | 役割                               |
|----------------|-------------------------------------|
| kind           | 現在地のカテゴリ（7値）              |
| required_action| 次にすべき操作の名前（機械が読む）    |
| reason         | 状態の説明（人間が読む）             |

※ reason フィールドは §5.2 の next_action 必須フィールド10個に含まれていない
```

---

## FILE: .reviewcompass/schema/next_action_response.schema.json（next_action 定義部分）

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "urn:reviewcompass:schema:next_action_response",
  "type": "object",
  "required": ["verdict", "exit_code", "next_action", "reasons", "current_state"],
  "properties": {
    "next_action": {
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
        "kind": { "type": "string", "enum": ["in_progress","blocking_in_progress","verification_pending","reopen_in_progress","feature_definition_required","completed","unknown"] },
        "required_action": { "$ref": "urn:reviewcompass:schema:required_action" },
        "active_gate": { "oneOf": [{ "type": "string" }, { "type": "null" }] },
        "feature": { "oneOf": [{ "type": "string" }, { "type": "null" }] },
        "phase": { "oneOf": [{ "type": "string" }, { "type": "null" }] },
        "stage": { "oneOf": [{ "type": "null" }, { "type": "string" }] },
        "required_feature_scope": { "type": "array", "items": { "type": "string" } },
        "blocked_by": { "oneOf": [{ "type": "object" }, { "type": "null" }] },
        "future_gates": { "type": "array" },
        "state_refs": { "type": "object" },
        "pending_gates": { "type": "array" }
      },
      "allOf": [
        ... (if/then 制約省略)
      ]
    },
    "reasons": { "type": "array" },
    "current_state": { "type": "object" }
  }
}
```

**注意**：スキーマの `next_action.properties` に `reason` フィールドは定義されていない。
`next_action.required` にも `reason` は含まれていない。
設計書 §5.3 は `reason` を「全 kind 共通フィールド」として記述しているが、スキーマでは `next_action` の
`additionalProperties` は指定されていないため、`reason` フィールドは JSON の追加プロパティとして扱われる。

## Output Contract

所見は次の形式で出力してほしい。

```yaml
findings:
  - id: <連番（F-001 など）>
    severity: must-fix | should-fix | leave-as-is
    target: <対象ファイル名または箇所>
    summary: <1行の説明（日本語）>
    detail: <具体的な問題の説明。要件・設計の原文を引用して根拠を示す>
    suggestion: <修正の方向性（あれば）>
```

所見がない場合は `findings: []` を返してほしい。
