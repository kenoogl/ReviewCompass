---
date: 2026-06-08
classifier: codex_main_session
classification: I-4
trigger_source: 完了済み workflow への intent 追記。intent/INTENT.md に「レビュー収集処理が事前設定の写像にならない」を追加した後、正式な reopen 手続きを経ずに下流再確認を先行実施したため、遡及的に正式運用へ戻す。
feature: all_features
finding: completed-workflow-intent-update
---

## 分類根拠

完了済み workflow に対し、`intent/INTENT.md` へ「レビュー収集処理が事前設定の写像にならない」という意味を持つ追記を行った。既に完了済みの上流正本を変更したため、単なる下流再確認ではなく reopen 手続きで扱う。

今回の変更元は intent であり、影響範囲は feature-partitioning、requirements、design、tasks、implementation まで届く。既存の trigger_map で intent から implementation までの連鎖再実施を表す分類は `I-4` である。したがって本 reopen は `I-4` として扱う。

`next` の候補分類 `N-0` は、上流正本の更新元 phase だけを見た機械的な入口候補である。一方、本件は完了済み workflow 全体への intent 変更であり、REOPEN_PROCEDURE §4 の「意図の問題：intent を修正 → 全機能の下流を reopen 対象に → 連鎖再実施」に従い、全下流段を対象にする。

## 事実

- `intent/INTENT.md` に §3.7 と §4.7 として、レビュー収集処理を事前設定の写像にしない意図を追記した。
- その後、feature-partitioning、各 feature の requirements/design/tasks/implementation-drafting に再確認記録を追加した。
- しかし、その作業は reopen in-progress を立てず、正式な第1過程の分類・フラグ差し戻し・承認停止点を経ていなかった。
- 2026-06-08 に `next` 判定を修正し、今後は完了済み workflow の上流正本変更が `reopen_classification_required` へ進むようにした。

## 連鎖再実施対象

`I-4` の trigger_map に従い、次を対象にする。

- `stages/intent.yaml#review`
- `stages/intent.yaml#approval`
- `stages/feature-partitioning.yaml#candidate-proposal`
- `stages/feature-partitioning.yaml#approval`
- `stages/requirements.yaml#alignment`
- `stages/requirements.yaml#approval`
- `stages/design.yaml#alignment`
- `stages/design.yaml#approval`
- `stages/tasks.yaml#alignment`
- `stages/tasks.yaml#approval`
- `stages/implementation.yaml#alignment`
- `stages/implementation.yaml#approval`

対象 feature は全 7 機能である。

## 第1過程で差し戻す状態

全 feature の `spec.json` について、次を行う。

- `reopened.intent`、`reopened.feature-partitioning`、`reopened.requirements`、`reopened.design`、`reopened.tasks`、`reopened.implementation` を `true` にする。
- `workflow_state.intent.review` と `workflow_state.intent.approval` を `false` にする。
- `workflow_state.feature-partitioning.candidate-proposal` と `workflow_state.feature-partitioning.approval` を `false` にする。
- `workflow_state.requirements.alignment` と `workflow_state.requirements.approval` を `false` にする。
- `workflow_state.design.alignment` と `workflow_state.design.approval` を `false` にする。
- `workflow_state.tasks.alignment` と `workflow_state.tasks.approval` を `false` にする。
- `workflow_state.implementation.alignment` と `workflow_state.implementation.approval` を `false` にする。
- `recheck.upstream_change_pending` を `true` にする。
- `recheck.impacted_downstream_phases` を `["feature-partitioning", "requirements", "design", "tasks", "implementation"]` にする。

## 停止点

第1過程の完了後、フラグ差し戻し内容と再実施範囲について利用者承認を待つ。
