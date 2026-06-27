# レビュー：Claim C（verification_type の設計値と実装値の不一致）

## 背景

ReviewCompass の `next --json` は `kind: "verification_pending"` を返すとき、`verification_type` サブフィールドで「検証の種別」を示す。MWP-0 の設計書 §5.3 は旧来の kind 値を統合し、`verification_type` で種別を区別することを定めた。

---

## 設計書の定義（design.md §5.3）

設計書 §5.3 の表（line 545-549）：

| `verification_type` | 意味 | 旧 kind |
|--------------------|------|--------|
| `pending` | 検証待ち・未着手 | `post_write_verification` |
| `policy_violation` | 禁止変更が混入 | `post_write_policy_violation` |
| `human_decision_required` | 未解決の重大所見あり | `post_write_human_decision_required` |

「旧 kind」列は、統合前の kind 値を示している。設計の意図は `post_write_verification` という旧値を `pending` という新値に改名することにある。

---

## 実装の実態（check-workflow-action.py）

実装で使われている `verification_type` の値：

| 実装の値 | 設計書の期待値 |
|---------|-------------|
| `"post_write_verification"` | `"pending"` のはず |
| `"policy_violation"` | 一致 ✓ |
| `"human_decision_required"` | 一致 ✓ |
| `"lightweight_self_check"` | 設計書の表に記載なし |

---

## WORKFLOW_DISCIPLINE_MAP.yaml での利用状況

```yaml
# decision_points（カタログ）
decision_points:
  next_action_verification_type:
    - id: post_write_verification    # ← 実装の値（設計書では "pending" のはず）
    - id: policy_violation           # ✓
    - id: human_decision_required    # ✓
    - id: lightweight_self_check     # 設計書の表に記載なし

# ルックアップ
by_verification_type:
  post_write_verification:           # ← 実装の値でキーを定義
    - (参照先リスト)
  lightweight_self_check:            # 設計書に記載なし
    - (参照先リスト)
```

`by_verification_type` は実行時にルックアップに使われるキーである。もし実装の `"post_write_verification"` を設計書の `"pending"` に変更すると、このルックアップが機能しなくなる。

---

## テストの状況

`tests/tools/test_effective_prompt_contract.py` は `next_action_verification_type` の期待値として `"post_write_verification"` を使っている（設計書の `"pending"` ではない）。

---

## 審査してほしいこと

1. 設計書の表は `"pending"` を新しい値として定義し、`"post_write_verification"` を「旧 kind」として位置づけている。実装・カタログ・テストが一貫して旧値 `"post_write_verification"` を使っている状況をどう評価するか
2. `lightweight_self_check` が設計書の表に記載されていないことは問題か
3. 問題があるとすれば、修正すべきは実装・カタログか、それとも設計書か。その根拠は何か

自由に分析してよい。選択肢の枠を超えた指摘も歓迎する。

---

## 回答形式

- **所見**：問題あり / 問題なし / その他
- **根拠**
- **重大度**：must-fix / should-fix / leave-as-is / 設計書更新のみ
- **提案**（must-fix / should-fix の場合）
