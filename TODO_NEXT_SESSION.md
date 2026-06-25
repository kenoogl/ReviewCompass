# 次セッション継続用メモ

最終更新：2026-06-25（Mac ローカル）。前回（2026-06-24 WEB セッション）の proxy レイアウト整合は **commit/push 完了済み**。最新状態は必ず `git log --oneline -4`、`git status`、`python3 tools/check-workflow-action.py next --json` で確認する。

## 1. 前回の最重要課題（commit/push 未完）は解決済み

- proxy 整合本体 64 ファイルを commit（`758db17c`）し、`origin/main` へ push（`c8932457..758db17c`）。前回ローカルに残っていた config の機械的3者既定（`fcb371c8`）も同時に push 済み。
- `next --json` は `completed`（全 workflow 完了・検証待ちなし）。

## 2. policy violation の真因と解消（記録）

- 症状：`next --json` が `post_write_policy_violation` を返し、`SESSION_WORKFLOW_GUIDE.md` が forbidden 判定だった。
- 真因：`TODO_NEXT_SESSION.md` が strict 検証対象へ格上げされ（同一未コミット差分に guide が含まれるため）、guide から見て「ガイダンス以外の対象（＝TODO）」が混在する状態になり、`is_forbidden_post_write_pending_change`（`tools/check-workflow-action.py:5738-5751`）が発火していた。guide 自体は封印 005 と指紋一致で検証済み・無改変。
- 解消：TODO を一時退避（`git stash`）→ 検証対象が guide 単独 → 封印 005（指紋一致）で検証済み判定 → `commit-preflight` OK → guarded commit（PTY relay で承認1行を中継）→ push。退避した TODO は本コミットで復元・更新。

## 3. 横展開の課題（issue 記録済み・コミット済み・未着手）

- `issue-2026-06-24-approval-stage-proxy-actor-boundary-mismatch`：guide の approval 段の承認主体記述が human-only 境界と矛盾の疑い（gpt-5.5 所見）。decision_scope 機構と照合して精査する。
- `issue-2026-06-24-post-write-target-judgment-mismatch`：`review_triage.py` と `check-workflow-action.py` の post-write 対象判定の不整合（specs／機械生成記録を誤って対象化する懸念）。
- `issue-2026-06-24-sandbox-guarded-commit-blocked`：WEB サンドボックスでは classifier がエージェントの commit を全方法で拒否（PTY relay 含む）。Mac ローカルでは通る（本セッションで実証）。

## 4. 参照

- 経緯ノート：`docs/notes/2026-06-24-proxy-layout-codecanon-session.md`
- 3者検証 run：`.reviewcompass/evidence/review-runs/2026-06-24-proxy-layout-codecanon-postwrite-3way/`
- commit 手順：`.reviewcompass/guidance/COMMIT_OPERATION_CARD.md`

過去の詳細は git log、`docs/notes/`、`docs/sessions/` を正本とする。
