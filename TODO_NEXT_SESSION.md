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
  - `3dc90dbc Correct API review entrypoint documentation`
  - `3147bdaa Document canonical API review procedure`
  - `be4d8c3e Load API keys from zshrc in API entrypoints`
  - `a3263fdf Remove external API approval guard`
  - `85b3bac5 Add external API approval guard`
- 作業ツリーは clean、`origin/main` へ push 済み。

## 3. 直近の重要メモ

- `docs/notes/2026-06-17-next-json-unique-state-redesign.md`
  - `next --json` を唯一の状態 / action selector とする設計メモ。
- `docs/notes/2026-06-17-next-json-effective-prompt-enforcement.md`
  - `next --json` 返値に紐づく effective prompt 必読、読了証跡、coverage audit、短文化の締め直しメモ。
- `docs/notes/2026-06-17-maintenance-workflow-compliance-improvement-candidates.md`
  - maintenance workflow 遵守、commit sandbox `.git/index.lock` preflight、maintenance / reopen / new workflow の使い分け、手続きの比例性の候補。
- `docs/notes/2026-06-17-working-note-verification-trigger-policy.md`
  - 作業中メモを API post-write に反復投入せず、`lightweight_self_check` に分岐する候補。
- `stages/completed/maintenance-2026-06-17-commit-sandbox-preflight.yaml`
  - commit sandbox preflight は実装・テスト・設計 / タスク反映まで完了済み。

## 4. 次作業候補

1. **作業中メモの `lightweight_self_check` 化**
   - 作業中メモ / 修正候補メモ / rollback メモを API post-write ではなく軽量自己精査へ分岐する artifact class 判定を実装する。

2. **maintenance workflow protocol の明文化**
   - maintenance でも要件・設計・タスク相当の確認、TDD、実装後 review、post-write / lightweight self check、completed 化をどう扱うかを正本化する。
   - まず 3 行宣言で試す: `変更分類`、`理由`、`手順`。

3. **`next --json` 一意性と effective prompt 強制の締め直し**
   - `WORKFLOW_DISCIPLINE_MAP.yaml` coverage audit、全 action への `effective_prompt` 付与、読了証跡、アンカー節抽出を行う。
   - 他サブコマンドの JSON は次作業 selector ではない。次作業は必ず再度 `next --json` で決める。

4. **実アプリ pilot**
   - 未着手。対象アプリ root と、対象アプリ側 LLM が参照できる ReviewCompass 配布物配置先を決めるところから始める。
   - 正本: `docs/operations/INITIAL_DEPLOYMENT_USER_GUIDE.md` §8、§9、§19、および `docs/operations/DEPLOYMENT.md` §8。
   - 配布前 smoke は実アプリ pilot 前の必要作業であり、現時点で完了済み扱いにしない。

5. **decision-source-lint の運用開始**
   - 仕組みは実装済み。次に重要決定が発生した時点で `.reviewcompass/decisions/` に構造化決定記録を作る。

完了済みとして候補から外したもの:

- **commit sandbox preflight**
  - `eb028df2 Add commit sandbox preflight` と `stages/completed/maintenance-2026-06-17-commit-sandbox-preflight.yaml` で完了済み。

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
