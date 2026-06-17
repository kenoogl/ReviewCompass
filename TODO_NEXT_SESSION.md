# 次セッション継続用メモ

最終更新：2026-06-17。

この TODO は入口メモであり、作業順序の正本ではない。正本は常に `.venv/bin/python3 tools/check-workflow-action.py next --json` と各 feature の `spec.json`。

作業ディレクトリ：`/Users/Daily/Development/ReviewCompass/`
リポジトリ：`git@github.com:kenoogl/ReviewCompass.git`（main ブランチ）

## 1. 起動時に必ず行うこと

1. `.venv/bin/python3 tools/check-workflow-action.py next --json` を実行する。
2. `next_action.effective_prompt.effective_prompt_path` がある場合は、その本文を読む。
3. `git status --short` と `git log --oneline -5` で到達点を確認する。
4. `post_write_verification`、`reopen_in_progress`、`resume_in_progress`、`unknown` が返った場合は通常作業へ進まない。
5. commit / push / spec.json workflow_state 変更は不可逆操作として扱い、利用者の明示承認と guard を通す。

## 2. 現在位置

- `next --json`: `completed`
- 進行中手続き: なし
- 直近 commit:
  - `ebb2df47 Record effective prompt enforcement note`
  - `a5127ef6 Record workflow compliance improvement notes`
  - `0183005e Import next json redesign note`
  - `0d611816 Make next json action selection unique`
  - `7f346075 Reuse active commit approval transactions`
- D-003 reopen 以降の混乱は、退避・巻き戻し後に重要件だけを再取り込み済み。
- 退避先: `/private/tmp/reviewcompass-d003-rollback-20260617/`

## 3. 直近の重要メモ

- `docs/notes/2026-06-17-next-json-unique-state-redesign.md`
  - `next --json` を唯一の状態 / action selector とする設計メモ。
- `docs/notes/2026-06-17-next-json-effective-prompt-enforcement.md`
  - `next --json` 返値に紐づく effective prompt 必読、読了証跡、coverage audit、短文化の締め直しメモ。
- `docs/notes/2026-06-17-maintenance-workflow-compliance-improvement-candidates.md`
  - maintenance workflow 遵守、commit sandbox `.git/index.lock` preflight、maintenance / reopen / new workflow の使い分け候補。
- `docs/notes/2026-06-17-working-note-verification-trigger-policy.md`
  - 作業中メモを API post-write に反復投入せず、`lightweight_self_check` に分岐する候補。

## 4. 次作業候補

1. **`next --json` 一意性と effective prompt 強制の締め直し**
   - 入口: `WORKFLOW_DISCIPLINE_MAP.yaml` coverage audit、全 action への `effective_prompt` 付与、読了証跡、アンカー節抽出。
   - 注意: 他サブコマンドの JSON は次作業 selector ではない。次作業は必ず再度 `next --json` で決める。

2. **maintenance workflow protocol の明文化**
   - maintenance でも要件・設計・タスク相当の確認、TDD、実装後 review、post-write / lightweight self check の区別、completed 化をどう強制するかを決める。
   - retrospective 対象候補: `7f346075`、`0d611816`、`0183005e`、`a5127ef6`、`ebb2df47`。

3. **作業中メモの `lightweight_self_check` 化**
   - 作業中メモ / 修正候補メモ / rollback メモを API post-write ではなく軽量自己精査へ分岐する artifact class 判定を実装する。
   - 現状は暫定的に `lightweight_self_check` manifest を手で置いて guard を通している。

4. **commit sandbox preflight**
   - `guarded-git-commit.py` が `git commit` 直前に `.git/index.lock` 作成可否を preflight する。
   - 不可なら approval を消費せず、sandbox 外 guarded commit 再実行を一意 action として返す。

5. **実アプリ pilot**
   - P1 完了済み。
   - 配布前 smoke は合格済み。

6. **decision-source-lint の運用開始**
   - 仕組みは実装済みだが、構造化決定記録 `.reviewcompass/decisions/` はまだ 0 件。
   - 次に発生する重要決定から記録を始める。

## 5. 会話ログ取り込み

- 原則フック任せ。
- Claude は SessionEnd / SessionStart。
- Codex は TODO 更新後の PostToolUse で現セッション下書き保存、次 SessionStart で前セッション下書きを正式化。
- 手動 backfill は終了済みセッション 1 件だけに限定する。
- 一括 backfill は使わない。

## 6. 参照

- workflow navigation: `docs/operations/WORKFLOW_NAVIGATION.md`
- session guide: `docs/operations/SESSION_WORKFLOW_GUIDE.md`
- discipline map: `docs/operations/WORKFLOW_DISCIPLINE_MAP.yaml`
- carry-forward register: `learning/workflow/carry-forward-register/reviewcompass-import.yaml`

過去の詳細履歴は git log、`docs/notes/`、`stages/completed/` を正本とする。
