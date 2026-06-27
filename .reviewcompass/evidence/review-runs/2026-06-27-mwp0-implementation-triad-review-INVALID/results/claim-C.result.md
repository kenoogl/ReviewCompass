# レビュー結果：Claim C

- **所見**：問題あり（ただし設計書側が誤り）
- **重大度**：設計書更新のみ

## 判断

実装・カタログ・テストが一貫して正しく、設計書 §5.3 の表記が追いついていない。

## 根拠

**1. 実装の 4 値はすべて設計的に必要**
- `post_write_verification`：API を呼ぶ post-write 検証（`run_post_write_verification`）の未完了
- `lightweight_self_check`：API 不要の軽量自己精査（`review_working_note_without_api`）の未完了
- 両者は `required_action` が異なり、対象ファイルの分類条件も異なる別物。設計書の表が `"pending"` 1 行に集約しすぎている

**2. 実装・カタログ・テストの三者が完全一致**
- `test_effective_prompt_contract.py` の期待値・`WORKFLOW_DISCIPLINE_MAP.yaml` の `next_action_verification_type` カタログおよび `by_verification_type` テーブル・実装コードの出力値が 4 値すべてで一致

**3. 設計書の `"pending"` への改名は他の箇所に根拠なし**
- `by_verification_type.get(verification_type)` のランタイムルックアップが壊れるため、実装側の変更は有害

**混乱の根本原因**：設計書の「旧 kind → 新 verification_type」という体裁が「`post_write_verification` を廃止して `pending` に改名する」という誤読を生んでいる。実際の MWP-0 の変更は `kind` 値の統合であり、`verification_type` 側の値は改名していない。

## 提案

設計書 §5.3 の表（line 545-549）を実態に合わせて修正する（実装変更なし）：

| `verification_type` | 意味 | 旧 kind |
|--------------------|------|--------|
| `post_write_verification` | API 検証待ち・未着手（旧値から継続採用） | `post_write_verification`（同値） |
| `policy_violation` | 禁止変更が混入 | `post_write_policy_violation` |
| `human_decision_required` | 未解決の重大所見あり | `post_write_human_decision_required` |
| `lightweight_self_check` | API 不要の軽量自己精査 | （新規追加） |
