---
date: 2026-06-17
record_type: implementation-note
status: active
topic: next-json-unique-state-implementation
source_material: /private/tmp/reviewcompass-d003-rollback-20260617/files/docs/notes/2026-06-16-next-json-unique-state-redesign.md
---

# next --json 唯一状態 selector 実装メモ

## 目的

本 maintenance は、D-003 rollback 退避資料に保存した `next --json` 唯一 action selector 再設計のうち、最初に実行可能な範囲を実装する。

目的は D-003 を再開することではない。`next --json` が複数の状態次元をそのまま投影し、pending reopen gate が blocker や commit stop point を上書きしてしまう直接の selector 欠陥を取り除くことである。

## 採用した契約

`next --json` は状態要約ではなく action selector である。返す `required_action` は常に 1 つだけである。

`active_gate`、`feature`、`phase`、`stage` は、選択された action が active workflow unit を持つ場合だけ具体値を持つ。maintenance、人間判断待ち、reopen commit stop point、reopen 第2過程の正本修正は、active workflow unit を持たない action として扱う。

maintenance は `required_action=run_maintenance` を使う。maintenance YAML 内の具体的な作業名は `maintenance_action` と `action_parameters.maintenance_action` に分離して返す。

この実装範囲における reopen 選択優先順位は次のとおりである。

1. `current_blocker` があれば `wait_for_human_decision` を返す。
2. `commit_stop_point: true` があれば `commit_stop_point` を返す。
3. reopen 第3過程で pending gate があれば `run_reopen_drafting` または `run_reopen_pending_gate` を返す。
4. その他の reopen step は step 単位の action を返す。

これにより、blocker または commit stop point が存在する状態で `pending_gates[0]` が active になることを防ぐ。

## 実装範囲

- `tools/check-workflow-action.py`
  - `select_reopen_next_action_fields` を追加した。
  - reopen next action に `active_gate` と `blocked_by` を追加した。
  - maintenance の `required_action` と `maintenance_action` を分離した。
- `tests/tools/test_check_workflow_action.py`
  - maintenance action の分離を検証する。
  - reopen commit stop point が pending gate より優先されることを検証する。
  - blocker 優先と active gate の null 化を検証する。
  - reopen drafting と pending gate 実行で active gate が入ることを検証する。
- SDD
  - requirements、design、tasks に唯一 selector 契約を記録した。

## 未実装範囲

rollback 退避資料の設計メモには、今回の最初の実装範囲を超える作業が含まれている。残件は次のとおりである。

- side track stack frame の push / pop コマンド
- commit stop point の post-commit 遷移用 protected operation ledger
- `advance_reopen_after_commit_stop_point`
- reopen plan の不変条件違反に対する `repair_workflow_state`
- structured classification から reopen plan を導出する compiler
- 完全な `future_gates` / `state_refs` schema

これらは、この selector 契約が安定した後に、別の maintenance 単位として実装する。
