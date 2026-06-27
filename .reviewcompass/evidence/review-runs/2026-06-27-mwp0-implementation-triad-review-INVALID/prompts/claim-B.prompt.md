# レビュー：Claim B（blocking_phase サブフィールドの値が設計と一致しないか）

## 背景

ReviewCompass の `next --json` は `kind: "blocking_in_progress"` を返すとき、`blocking_phase` サブフィールドで「blocking 作業のどの段階か」を示す。MWP-0 の設計書 §5.3 は、旧来の複数の kind 値を1つの `blocking_in_progress` に統合し、サブフィールドで段階を区別することを定めた。

---

## 設計書の定義（design.md §5.3）

設計書 §5.3 の表（line 519-523）：

| `blocking_phase` | 意味 | 統合された旧 kind |
|-----------------|------|----------------|
| `required` | blocking 作業の開始が必要 | `blocking_unit_required` |
| `in_progress` | blocking 作業中 | `blocking_unit_in_progress` / `maintenance_in_progress` / `resume_in_progress` |
| `return_pending` | blocking 完了・親への復帰待ち | `parent_resume_pending` |

設計書 §5.3 の廃止宣言（line 537）（抜粋）：

> 廃止するフィールドと廃止する `blocking_phase` 値：`resuming`（`blocking_phase` 値・`in_progress` に統合。）

廃止リストに名前が挙がっているのは `resuming` のみ。`blocking_unit_required` / `blocking_unit_in_progress` / `parent_resume_pending` / `maintenance_in_progress` は廃止リストに明示されていないが、上の表で新3値との対応が定義されている。

---

## 実装の実態（check-workflow-action.py）

実装で使われている `blocking_phase` の値（各々の出現箇所）：

```python
# blocking unit が作業中の場合（line 6670付近）
{ "kind": "blocking_in_progress", "blocking_phase": "blocking_unit_in_progress", ... }
# 設計の期待値: "in_progress"

# 親への復帰待ちの場合（line 6703付近）
{ "kind": "blocking_in_progress", "blocking_phase": "parent_resume_pending", ... }
# 設計の期待値: "return_pending"

# 新しい blocking unit の開始が必要な場合（line 6738付近）
{ "kind": "blocking_in_progress", "blocking_phase": "blocking_unit_required", ... }
# 設計の期待値: "required"

# maintenance 中の場合（line 5464付近）
{ "kind": "blocking_in_progress", "blocking_phase": "maintenance_in_progress", ... }
# 設計の期待値: "in_progress"

# reopen 再開始中の場合（line 5527付近）
{ "kind": "blocking_in_progress", "blocking_phase": "resume_in_progress", ... }
# 設計の期待値: "in_progress"
```

---

## blocking_phase 値の利用状況

WORKFLOW_DISCIPLINE_MAP.yaml に `by_blocking_phase` セクションは存在しない（ルックアップに使われていない）。`blocking_phase` 値は、コマンド出力を読む人間が状態を理解するための診断情報として使われており、機械処理での参照は確認されていない。

テストは `blocking_phase` の値を直接検証していない（`kind: "blocking_in_progress"` の返却は確認するが、サブフィールドの値は確認しない）。

---

## 審査してほしいこと

1. 設計書の表（旧値から新3値への対応）は、実装がこの新3値を使うべきことを要求しているか。廃止リストに旧値が明示されていない点は、この判断に影響するか
2. `blocking_phase` 値が機械処理されていないという事実は、不一致の問題の重大度をどう変えるか
3. 旧値（`blocking_unit_in_progress` 等）は情報量が新値より豊富（`in_progress` 一つで `maintenance_in_progress` と `blocking_unit_in_progress` を区別できなくなる）。この点は修正の是非に影響するか
4. 修正が必要だとすれば、何をどう修正すべきか

自由に分析してよい。選択肢の枠を超えた指摘も歓迎する。

---

## 回答形式

- **所見**：問題あり / 問題なし / その他
- **根拠**
- **重大度**：must-fix / should-fix / leave-as-is
- **提案**（must-fix / should-fix の場合）
