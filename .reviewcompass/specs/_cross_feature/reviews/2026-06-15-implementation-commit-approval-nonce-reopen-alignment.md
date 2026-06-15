---
date: 2026-06-15
gate: stages/implementation.yaml#alignment
feature: workflow-management
reopen: R-0
reopen_topic: commit-approval-nonce
decision: existing_sufficient
---

# implementation alignment（整合確認）：commit 承認 nonce 実装

reopen R-0 の第3過程、workflow-management implementation フェーズの alignment 段。Requirement 4 受入 6〜7、design.md §不可逆操作の直前ゲートモデル §2.1、tasks.md の T-004／T-006／T-011、および実装済みコミットの整合を確認する。

## 要件・設計・タスクとの整合

| 対象 | 実装での受け方 | 整合判定 |
| --- | --- | --- |
| Requirement 4 受入 6 | `commit-approval prepare/record/invalidate`、nonce、target digest、staged exact index validation、期限・消費状態・approval/challenge 照合、commit 成功後 consume を実装した。 | 整合。 |
| Requirement 4 受入 7 | record / challenge schema で LLM/provider/model 系 field を禁止し、判定入力を staged file set、staged blob hash、target digest、nonce、expiry、consumed 状態へ限定した。 | 整合。 |
| design.md §2.1 | UTC ISO-8601、TTL 10 分、clock rollback fail-closed、`commit-approval-v1` canonical digest、stdin/no-store、redaction/residual secret omission、challenge consume を実装に展開した。 | 整合。 |
| tasks.md T-004 | `tools/check-workflow-action.py commit-approval` サブコマンドと JSON 出力契約を追加した。 | 整合。 |
| tasks.md T-006 | `tools/check_workflow_action/commit_approval.py` と `tools/guarded-git-commit.py` で commit 直前 gate、validation failure invalidation、consume、legacy fallback を扱う。 | 整合。 |
| tasks.md T-011 | nonce prepare/record/validation、redaction、malformed、gitlink、rename、consume 順序、進行中 session record 除外の回帰テストを追加した。 | 整合。 |

## review-run 反映確認

- implementation triad-review C1〜C4 は `must-fix` として TDD 対応済み。
- C5〜C7 は `should-fix` として TDD 対応済み。
- C8 は proxy_model 判断どおり this gate では `leave-as-is` / follow-up 扱い。
- recheck R1 は `must-fix`、R3 は `should-fix` として TDD 対応済み。
- recheck R2／R4／R5 は利用者判断どおり `leave-as-is`。
- staging helper は、guarded commit 前に進行中 session record を誤って stage しないための機械処理として追加済み。

## 検証

実行済み：

- `.venv/bin/python3 -m unittest tests.tools.test_check_workflow_action tests.tools.test_guarded_git_commit tests.tools.test_runtime_placement_freeze.CommitApprovalPlacementTests -v`
- `.venv/bin/python3 -m unittest tests.tools.test_commit_in_progress_session_guard tests.tools.test_push_ignores_in_progress_records -v`
- `git diff --check`
- `.venv/bin/python3 tools/check-workflow-action.py next --json`
- `.venv/bin/python3 tools/check-workflow-action.py review-wave-summary --out .reviewcompass/specs/_cross_feature/reviews/2026-06-15-implementation-commit-approval-nonce-review-wave.md --json`

## 判定

- **decision：existing_sufficient**。
- implementation の追加実装は requirements/design/tasks と整合し、追加の implementation 改訂は不要。
- 次は `stages/implementation.yaml#approval` の承認段である。
