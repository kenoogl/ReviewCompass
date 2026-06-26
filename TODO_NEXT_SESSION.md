# 次セッション継続用メモ

最終更新：2026-06-26（Mac ローカル）。最新状態は必ず `git log --oneline -4`、`git status`、`python3 tools/check-workflow-action.py next --json` で確認する。

## 1. 今回（2026-06-26）の完了作業

- `WORKFLOW_NAVIGATION.md` の `run_reopen_drafting` 説明で `next_drafting_gate` → `active_gate` に1行変更。3社 API レビュー済み（run: `2026-06-26-workflow-navigation-active-gate-postwrite`）。commit `01e4986a`。
- `review_triage.py` のバグ修正：`docs/sessions/auto-*` を post-write 対象から誤判定していた問題を解消。テスト4件追加。同 commit に同梱。
- `next --json` は `completed`・push 済み（`3d1d653c..8ec30a29`）。

## 2. 最優先：post-write 手順の機械化（根本原因）

**`plan-2026-06-23-postwrite-prompt-mechanization-completion.yaml`** の実装が追いついていない。

今回のセッションで同じ問題が再発した：
- post_write_verification 状態になった際に `run_review.py` の代わりに Agent ツールで Claude モデルのみに投げた（プロトコル違反）
- main preanalysis（事前検討）を省略してレビューを投げた

根本原因：LLM が「どのツールをどう使うか」を判断する余地が残っている。手順選択・材料選定・コマンド実行を機械処理に寄せることで防げる。同じ問題が 2026-06-12・2026-06-21 にも記録されている。

## 3. テスト20件失敗（未対処）

`tests/tools/test_check_workflow_action.py` の post-write 関連テストが20件失敗している。詳細は `docs/notes/2026-06-26-test-check-workflow-action-post-write-failures.md`。

原因：テストが `docs/notes/` を post_write_verification 対象と期待しているが、現実装では `lightweight_self_check` に分類される。テスト側のパスを `docs/disciplines/` 等に変更するか、実装側を見直すかを判断する。

## 4. MWP-0：next --json kind 再設計（検討完了・実装未着手）

kind を41種類から7種類に整理する設計が確定済み。詳細は `docs/notes/2026-06-26-next-json-kind-redesign.md`。実装の優先順位・着手時期は未決定。

## 5. 横展開の課題（issue 記録済み・未着手）

- `issue-2026-06-24-approval-stage-proxy-actor-boundary-mismatch`：guide の approval 段の承認主体記述が human-only 境界と矛盾の疑い。
- `issue-2026-06-24-sandbox-guarded-commit-blocked`：WEB サンドボックスでは classifier がエージェントの commit を全方法で拒否。

（`issue-2026-06-24-post-write-target-judgment-mismatch` は今回の `review_triage.py` 修正で一部対処済み）

## 6. 参照

- 機械化計画：`docs/notes/2026-06-21-llm-boundary-and-postwrite-prompt-mechanization-plan.md`
- kind 再設計：`docs/notes/2026-06-26-next-json-kind-redesign.md`
- commit 手順：`.reviewcompass/guidance/COMMIT_OPERATION_CARD.md`

過去の詳細は git log、`docs/notes/`、`docs/sessions/` を正本とする。
