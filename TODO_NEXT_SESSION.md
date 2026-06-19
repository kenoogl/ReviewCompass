# 次セッション継続用メモ

最終更新：2026-06-19（Codex セッション、`b06e3e2a` push 済み）。

この TODO は入口メモであり、作業順序の正本ではない。正本は各 feature の `spec.json` と `tools/check-workflow-action.py next --json` の機械判定である。

作業ディレクトリ：`/Users/Daily/Development/ReviewCompass/`
リポジトリ：`git@github.com:kenoogl/ReviewCompass.git`（main ブランチ）

## 1. 起動時に必ず行うこと

1. `.venv/bin/python3 tools/check-workflow-action.py next --json` を実行し、`next_action` を現在位置の機械判定として確認する。
2. `git status --short --branch` と `git log --oneline -5` で到達点を確認する。
3. `next_action.effective_prompt.effective_prompt_path` がある場合は、その本文を読む。
4. `post_write_verification`、`reopen_in_progress`、`resume_in_progress`、`unknown` が返った場合は、通常作業へ進まず、その action に従う。
5. commit / push / spec.json workflow_state 変更は不可逆操作として扱い、利用者の明示承認と guard を通す。

## 2. 現在位置

- `main` と `origin/main` は同期済み。
- 作業ツリーは clean。
- `next --json` は `completed`。
- 直近 commit: `b06e3e2a Remove implementation drafting artifacts`
- `implementation-drafting.md` は正式成果物として採用しない方針に変更済み。
- implementation drafting は文書作成ではなく、`tasks.md` に従ったテストと実装コードの生成を意味する。
- tasks drafting では、各タスクに次を含める必要がある。
  - 実装対象ファイル
  - 最初に書く失敗テスト
  - 実装順序
  - 完了条件
  - 検証コマンド
  - 禁止事項
  - 停止条件

## 3. 次作業

利用者指示：

> 次の作業は、タスク段からのreopenで、新しい規律に従ってタスクを再生成、実装を行う。

進め方：

1. tasks 段からの reopen として分類根拠を作成する。
2. `reopen-start` で in-progress 手続きを発行する。
3. 新しい tasks 粒度規律に従い、`workflow-management` の `tasks.md` を再生成する。
4. tasks 段の必要 gate を進める。
5. implementation drafting では、再生成した `tasks.md` に従って実際のテストと実装コードを書く。
6. 実装後は review / review-wave / alignment / approval の流れに従う。

注意：

- 作業開始前に `docs/operations/WORKFLOW_NAVIGATION.md` の `reopen_in_progress` と `reopen_classification_required` を確認する。
- `implementation-drafting.md` は作らない。
- 実装前計画文書を別成果物として増やさない。
- タスク記述が実装に足りない場合は、tasks.md の粒度を上げる。
- 平易な進捗説明を使う。「implementation drafting を完了」ではなく「コードとテストを作成」のように説明する。

## 4. 直近の完了事項

- `implementation-drafting.md` の全 spec 成果物を削除。
- 旧 `test_workflow_management_implementation_drafting.py` を削除。
- `test_workflow_management_task_granularity.py` を追加。
- `SESSION_WORKFLOW_GUIDE.md`、`workflow-management/tasks.md`、`.reviewcompass/README.md`、関連 notes を更新。
- 削除済み staged Markdown を commit guard が誤遮断しないよう、`tools/check-workflow-action.py` を修正。
- post-write verification 所見 0。
- commit `b06e3e2a` を `origin/main` へ push 済み。

## 5. 参照

- workflow navigation: `docs/operations/WORKFLOW_NAVIGATION.md`
- session guide: `docs/operations/SESSION_WORKFLOW_GUIDE.md`
- discipline map: `docs/operations/WORKFLOW_DISCIPLINE_MAP.yaml`
- workflow-management tasks: `.reviewcompass/specs/workflow-management/tasks.md`
- workflow-management spec: `.reviewcompass/specs/workflow-management/spec.json`

過去の詳細履歴は git log、`docs/notes/`、`docs/archive/todo/`、`docs/sessions/` を正本とする。
