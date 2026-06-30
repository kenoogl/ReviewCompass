# design.md §5.2 and §5.3 excerpt
# Source: .reviewcompass/specs/workflow-management/design.md
# Sections: §5.2 (relevant to reason/reasons) and §5.3 (kind detail fields)

## §5.2 next_action_response.schema.json — 最上位構造（抜粋）

**最上位必須フィールド（5つ）**：
- `verdict`（文字列）
- `exit_code`（整数）
- `next_action`（オブジェクト）
- `reasons`（配列）
- `current_state`（オブジェクト）

**`next_action` 必須フィールド（10つ）**：
`kind`・`required_action`・`active_gate`・`feature`・`phase`・`stage`・
`required_feature_scope`・`blocked_by`・`future_gates`・`state_refs`

Note: The `reasons` array is a top-level required field. It is not the same as any
field within `next_action`. The design document does not provide an explicit description
of what the `reasons` array contains or how it differs from `next_action`-level fields.

## §5.3 kind 詳細フィールド設計 — 全 kind 共通フィールド（原文）

| フィールド | 役割 |
|-----------|------|
| `kind` | 現在地のカテゴリ（7値） |
| `required_action` | 次にすべき操作の名前（機械が読む） |
| `reason` | 状態の説明（人間が読む） |

Note: The `reason` field is listed here as a `next_action`-level common field. It
is not listed in §5.2's next_action required fields (10 mandatory fields). The design
document does not contain a section that explicitly contrasts `next_action.reason`
with the top-level `reasons` array.

## T-020 先送り事項(b) — 原文

```
next_action 内の reason フィールドと最上位の reasons 配列の責務差を設計書と実装で明確化する。
```

T-020 完了条件一覧（5項目）には、先送り事項(b) に対応する明示的な検証項目が含まれていない。
