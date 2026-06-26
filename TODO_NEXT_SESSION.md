# 次セッション継続用メモ

最終更新：2026-06-26 セッション4（Mac ローカル）。最新状態は必ず `git log --oneline -5`、`git status`、`.venv/bin/python3 tools/check-workflow-action.py next --json` で確認する。

## 1. 今回（2026-06-26 セッション4）の完了作業

- **残存4件のテスト失敗をすべて修正**（コミット git:608bac79）
  - グループA（3件）：`CommitExitCodeTests` でファイル作成後に `git add` が欠如 → 追加・順序修正
  - グループB（1件）：`is_lightweight_self_check_target` が `docs/notes/review-runs/` を誤検出 → 除外条件追加
  - テスト 286件通過（全件）
- **issue を resolved に更新**（コミット git:05ee8bb9）
- **セッション記録が蓄積して新セッションでもコミットできない問題を調査・修正**（コミット git:46864601）
  - 原因：Claude Code アプリがセッション終了後も `last-prompt` / `mode` 等を jsonl に追記するため sha256 が変化していた
  - 修正：`SessionStart` フックで DONE_MARKER があっても sha256 が古ければ再取り込みするよう変更
- **過去4セッションのセッション記録を手動再取り込みしてコミット**（コミット git:d9c24309）
  - 2026-06-24〜26 の 4件（現セッション `fb8b24ee` は除く）

現時点のテスト状況：286件全通過。

## 2. 次セッションの最初にやること

### セッション記録のコミット

現セッション（`fb8b24ee`）の記録が untracked のままになっている。次セッション開始時に SessionStart フックが自動で再取り込みするが、取り込み済みであっても `git add` → コミットを確認する。

```
# 状態確認
git status | grep sessions/
# stale なら手動再取り込み
python3 tools/session-record-backfill.py \
  --session ~/.claude/projects/-Users-Daily-Development-ReviewCompass/fb8b24ee-a301-4651-902c-8ba5341d8f66.jsonl \
  --source claude \
  --evidence-dir .reviewcompass/evidence/sessions \
  --docs-dir docs/sessions
```

### 未コミットのファイル

- `.reviewcompass/backlog/todos/todo-2026-06-26-ppwm1-canonical-effective-prompt-fixation.yaml`（修正済みだが未コミット）
- `tests/tools/test_check_workflow_action.py`（軽微な変更が未コミット）

これらは内容を確認してからコミットする。

## 3. 横展開の課題（issue 記録済み・未着手）

- `issue-2026-06-24-approval-stage-proxy-actor-boundary-mismatch`：guide の approval 段の承認主体記述が human-only 境界と矛盾の疑い。
- `issue-2026-06-24-sandbox-guarded-commit-blocked`：WEB サンドボックスでは guarded commit が全方法で拒否される。

## 4. MWP-0：next --json kind 再設計（検討完了・実装未着手）

kind を41種類から7種類に整理する設計が確定済み。詳細は `docs/notes/2026-06-26-next-json-kind-redesign.md`。実装の優先順位は未決定。

## 5. 参照

- post-write 機械化計画（完了済み）：`.reviewcompass/backlog/plans/plan-2026-06-23-postwrite-prompt-mechanization-completion.yaml`
- セッション記録 issue（resolved）：`.reviewcompass/backlog/issues/issue-2026-06-26-post-write-tests-need-mechanization-not-fixture-rename.yaml`
- commit 手順：`.reviewcompass/guidance/COMMIT_OPERATION_CARD.md`
- backlog 操作カード：`.reviewcompass/guidance/WORKFLOW_NAVIGATION.md`

過去の詳細は git log、`docs/notes/`、`docs/sessions/` を正本とする。
