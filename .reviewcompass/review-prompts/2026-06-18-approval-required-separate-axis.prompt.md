# 設計深掘りレビュー：承認要否を別の属性として分離する

## これまでの議論のまとめ

ReviewCompass の operation contract（操作の契約）では `effect_kind`（副作用の種別）という属性が
「この操作は何をするか」と「承認ゲートが必要かどうか」の2役を担っている。

これが設計上の歪みを生んでいることが複数回のレビューで確認された。

具体的には：
- 同じ「状態変更（`state_mutation`）」でも承認が必要なものと不要なものがある
- `irreversible_action`（取り消し不能）という値は「何をするか」という種別ではなく「どのくらい危険か」という性質を表しており、他の4値（`read / write / state_mutation / external_call`）と異質

## 今回考える方向性

「承認が必要かどうか」を `effect_kind` から切り離し、別の属性として operation contract に持たせる。

この方向では次のような分類になる。

| 操作 | effect_kind（何をするか） | approval_required（承認が必要か） |
|---|---|---|
| `apply_approved_reopen_plan`（spec.json を書き換える） | `state_mutation` | true |
| `commit_stop_point`（git コミット） | `state_mutation` | true |
| `record_human_decision`（判断を記録する） | `state_mutation` | false |
| `run_post_write_verification`（外部レビューAPIを呼ぶ） | `external_call` | false |
| `repair_workflow_state`（状態修復コマンドの実行） | `state_mutation` | true |
| `finalize_reopen`（completed YAML への移動） | `state_mutation` | true |
| `wait_for_human_decision`（判断材料を提示する） | `read` | false |

## 分離で解消できること

- `effect_kind` は「何をするか」だけを表すようになり、承認要否の判断に使われなくなる
- `irreversible_action` という値は `effect_kind` の語彙から廃止できる（または別の意味に限定できる）
- 承認ゲートの判定は `approval_required: true` という独立した属性で機械的に行える

## 分離しても残る問題

`run_reopen_pending_gate`（ゲートを処理する操作）は実行時の状況（どのゲートに来たか）によって動作が変わる。

- 審査ゲートの場合 → 外部レビューAPIを呼ぶ（承認不要）
- 承認ゲートの場合 → 承認要求を設定する（`reopen-set-blocker` を実行する）

この操作の `approval_required` は、操作名だけでは決まらない。実行時の `active_gate` の値を参照しないと確定できない。

同様に `run_workflow_stage`（ワークフロー段を進める操作）も段の種別によって動作が変わる。

## Phase 5 への影響

現在 Phase 5 の計画は「`effect_kind: irreversible_action` に承認ゲートを機械的に強制する」と書かれている。

`approval_required` を別軸にした場合、この計画は「`approval_required: true` の操作に承認ゲートを機械的に強制する」という形に書き直される。

判定のロジックは単純になる（1つの属性を見ればよい）が、`approval_required` の値が正しく設定されているかの保証が必要になる。

## レビューで答えてほしい問い

1. `effect_kind` から `approval_required` を切り離す設計は、operation contract として成立するか。
   成立する場合、`effect_kind` の語彙（`irreversible_action` を含む）をどう整理すべきか。

2. `run_reopen_pending_gate` のように操作名だけでは `approval_required` が決まらない操作が存在する。
   この問題を operation contract の設計でどう扱うべきか。

3. `approval_required` の値が「正しく設定されている」ことを誰がどのように保証するか。
   現在の設計では `effect_kind: irreversible_action` という値がその役を担っていたが、
   属性を分離した場合、保証の仕組みが変わる。どのように保証するか。

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
