---
date: 2026-06-15
gate: stages/tasks.yaml#alignment
feature: workflow-management
reopen: R-0
reopen_topic: commit-approval-nonce
decision: existing_sufficient
---

# tasks alignment（整合確認）：commit 承認 nonce 実装タスク

reopen R-0 の第3過程、workflow-management tasks フェーズの alignment 段。Requirement 4 受入 6〜7、design.md §不可逆操作の直前ゲートモデル §2.1、tasks.md の T-004／T-006／T-011 追記の整合を確認する。

## 要件・設計との整合

| 対象 | tasks.md での受け方 | 整合判定 |
| --- | --- | --- |
| Requirement 4 受入 6 | T-004 に `commit-approval` サブコマンド、T-006 に nonce challenge、target digest、validation、invalidate、consume、consume 永続化失敗の責務、T-011 に統合テストを割り当てた。 | 整合。 |
| Requirement 4 受入 7 | T-006 に schema 禁止フィールド、判定入力限定、`attestation_type`、`guarantee_scope`、XDI invariant を割り当てた。 | 整合。 |
| design.md §2.1 | UTC ISO-8601、TTL 10 分、`now_utc`、clock rollback、canonical digest `commit-approval-v1`、exact index validation、redaction helper、source omission enum まで tasks.md に展開済み。 | 整合。 |
| 既存 T-004 | CLI 入口と JSON 出力契約を追加しただけで、既存 `next`／`spec-set`／`commit`／`push` の責務を壊さない。 | 整合。 |
| 既存 T-006 | commit 直前ゲートの既存責務を nonce challenge で強化する。不可逆操作の種類は増やさない。 | 整合。 |
| 既存 T-011 | 全体テストに統合される形であり、既存のテスト戦略と矛盾しない。 | 整合。 |

## triad-review 反映確認

- tasks triad-review C1〜C4 は `must-fix` として反映済み。
- C5〜C6 は `should-fix` として反映済み。
- `triage.yaml` に `decision_status: human_required` または `final_label: null` は残っていない。

## 判定

- **decision：existing_sufficient**。
- tasks.md の追記は requirements/design と整合し、追加の tasks 改訂は不要。
- implementation では TDD で `commit_approval.py`、commit gate validation、redaction、schema、consume／invalidate の実装へ進む必要がある。
