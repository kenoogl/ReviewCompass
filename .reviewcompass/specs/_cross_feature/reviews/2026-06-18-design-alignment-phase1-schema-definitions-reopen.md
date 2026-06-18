---
feature: workflow-management
phase: design
stage: alignment
date: 2026-06-18
reopen_id: reopen-procedure-2026-06-18
reopen_scope: phase1-schema-definitions
verdict: existing_sufficient
---

# design / alignment：reopen R-0（phase1-schema-definitions）

## 整合確認：requirements ⇔ design

| 受入基準 | 要求内容 | design §5 の記述 | 判定 |
|---|---|---|---|
| AC10 | `required_action.schema.json` をスキーマファイルとして定義する | §5.1 に `$id`, `$schema`, `type`, `enum`（19語彙）を明記 | 整合 |
| AC11 | `next_action_response.schema.json` をスキーマファイルとして定義する | §5.2 に最上位5フィールド・`next_action` 10フィールド・条件付き必須フィールド・後方互換規則を明記 | 整合 |
| AC11（verdict） | `verdict` は最上位にのみあり `next_action` 内には含めない | `properties: { "verdict": false }` を `next_action` の設計確定事項に追加 | 整合 |
| AC10（$ref） | `next_action_response` から `required_action` スキーマを参照する | `$ref: "urn:reviewcompass:schema:required_action"`（絶対 URN）で参照 | 整合 |

## 設計強化の確認

以下の設計強化は requirements の受入基準に明示されていないが、受入基準の意図を超えない範囲での仕様詳細化であり、逸脱なし：

- `kind` を 14値インライン enum として定義（WORKFLOW_NAVIGATION.md §2 との整合強化）
- `additionalProperties` の理由区別を明記（`$comment` への記録指示を含む）
- `repair_reasons` の `type: array, minItems: 1` の明記

## 判断

**existing_sufficient**：design.md の §5 変更は requirements.md の AC10/AC11 と整合する。要件に追加・削除・変更は不要。design/tasks/implementation での追加対応は引き続き reopen R-0 の残作業として追跡する。
