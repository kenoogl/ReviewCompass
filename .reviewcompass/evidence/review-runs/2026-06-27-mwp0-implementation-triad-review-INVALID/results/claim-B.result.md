# レビュー結果：Claim B

- **所見**：問題あり
- **重大度**：should-fix

## 根拠

設計書 §5.3 は `blocking_phase` を3値（`required` / `in_progress` / `return_pending`）に整理した。セッション記録（2026-06-25）でも「`blocking_phase` は3値に絞れます」と明示的に合意されている。廃止リストに旧値が明示されていない理由は、旧値が `blocking_phase` の正式フィールド値として存在しなかったため（旧 kind 値を転用していたため）であり、判断を覆す要因にはならない。

## 重要な追加発見

`WORKFLOW_DISCIPLINE_MAP.yaml` に `by_blocking_phase` セクションはないが、**実装内（line 6775）に旧値 `"maintenance_in_progress"` をハードコードした機械的な参照が存在する**。この分岐は `blocking_phase == "maintenance_in_progress"` で条件判定しており、旧値のまま放置すると設計と実装の乖離が内部ロジックにも及んでいる。

## 情報量の問題

旧値（`blocking_unit_in_progress` 等）は新値より詳細だが、設計確定時の議論で「`required_action` フィールドで区別を担保する」と合意済み。情報量の差は修正を否定する根拠にならない。

## スキーマの問題

`next_action_response.schema.json` に `blocking_phase` の enum 定義がなく、スキーマバリデーションで旧値も通過してしまう。独立した問題として存在する。

## 提案

**実装修正（check-workflow-action.py）**

| 現在の値 | 修正後 | 行 |
|---------|--------|-----|
| `"blocking_unit_in_progress"` | `"in_progress"` | line 6670 |
| `"parent_resume_pending"` | `"return_pending"` | line 6703 |
| `"blocking_unit_required"` | `"required"` | line 6738 |
| `"maintenance_in_progress"` | `"in_progress"` | line 5464 |
| `"resume_in_progress"` | `"in_progress"` | line 5527 |
| `"maintenance_in_progress"` (比較条件) | `required_action == "run_maintenance"` との複合条件に変更 | line 6775 |

**スキーマ修正**：`blocking_phase` の enum（3値）を `next_action_response.schema.json` に追加する。

**テスト追加**：`blocking_phase` の値が新3値のいずれかであることをアサートするテストを先行追加（TDD）。
