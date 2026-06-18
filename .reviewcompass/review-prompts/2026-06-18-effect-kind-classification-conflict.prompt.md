# 設計深掘りレビュー：effect_kind の分類と承認ゲートの判定基準

## 問題の状況

`docs/notes/2026-06-18-integrated-design-selection-execution-layers.md` の
§3 と §3.1 の間に次の矛盾がある。

### §3 の対応表（現状）

| required_action | effect_kind | 不可逆か |
|---|---|---|
| `repair_workflow_state` | `state_mutation` | はい |
| `apply_approved_reopen_plan` | `state_mutation` | はい |
| `run_reopen_start` | `state_mutation` | はい |
| `advance_reopen_after_commit_stop_point` | `state_mutation` | はい |
| `advance_reopen_after_approval_stop_point` | `state_mutation` | はい |
| `finalize_reopen` | `state_mutation` | はい |
| `commit_stop_point` | `irreversible_action` | はい |

（表には「不可逆か：はい」でも `effect_kind` が `state_mutation` の操作が6つある）

### §3.1 の記述（現状）

セクションタイトルが「`effect_kind: irreversible_action` が必要な操作」であり、
上記6つの操作（`repair_workflow_state`、`apply_approved_reopen_plan`、`run_reopen_start`、
`advance_reopen_after_commit_stop_point`、`advance_reopen_after_approval_stop_point`、
`finalize_reopen`）が承認ゲート必須の操作として列挙されている。

また §3.1 の末尾には次の説明が加わっている。

```
`record_human_decision` は「判断を記録する操作」（`effect_kind: state_mutation`）であり、
承認ゲートの対象操作ではなく、承認ゲートを構成する部品である。
```

### 矛盾の本質

§3 の表は「`state_mutation` であれば承認ゲート不要」と読める。
§3.1 は「上記の操作（`state_mutation`）は承認ゲートが必要」と言っている。

この2つは食い違っている。

承認ゲートを通すかどうかの判定基準が `effect_kind` だとすれば、
`state_mutation` とされている6つの操作は承認ゲートをスキップしてしまうことになる。

## レビューで答えてほしい問い

1. この6つの操作（`repair_workflow_state` など）は `effect_kind` として何が適切か。
   `state_mutation` のままでよいか、`irreversible_action` に変えるべきか。
   設計の観点から根拠を示すこと。

2. 承認ゲートを通すかどうかの判定基準は「`effect_kind` が `irreversible_action` であること」
   だけでよいか。それとも別の基準（別の軸）が必要か。

3. `effect_kind` の語彙（`state_mutation`・`irreversible_action`・`write`・`read`・`external_call`）
   の定義として、「元に戻せるかどうか」と「承認ゲートが必要かどうか」は同じ軸に乗せてよいか。
   それとも別の属性として分けるべきか。

## 出力形式

```yaml
findings:
  - severity: ERROR / WARN / INFO
    question_id: "1" / "2" / "3"
    description: |
      （分析内容）
    rationale: |
      （根拠）
```
