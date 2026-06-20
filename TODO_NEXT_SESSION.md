# 次セッション継続用メモ

最終更新：2026-06-21（Codex セッション、`f772a39a` まで commit / push 済み。`main` と `origin/main` は同期済み）。

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
- 直近 commit: `f772a39a Mark implementation approval complete`
- `next --json` は `completed`。
- すべての feature / phase / stage の `workflow_state` は完了済み。
- `workflow-management` の Requirement 13〜16 を基点にした reopen R-0 は、requirements / design / tasks / implementation まで完了済み。
- 進行中ファイルはない。
- 次の pending gate はない。

## 3. 次作業

次に行う本線 workflow 作業はない。次セッションでは、まず `next --json` と `git status --short --branch` を再確認し、`completed` / clean / synced が維持されていることを確認する。

新しい作業を始める場合：

1. 利用者の新規指示を受ける。
2. `next --json` が `completed` のままか確認する。
3. 必要なら新しい workflow / reopen / maintenance として開始条件を確認する。

進め方の注意：

- `next --json` が示す停止点を飛ばさない。
- commit / push は利用者の明示指示がある場合だけ実行する。
- triad-review の API review-run 前には、variant と role 割当を機械判定または設定から確定し、必要に応じて利用者に提示して停止する。
- review prompt は、上流資料のパス名だけでなく、必要な本文または要点を含める。単にパスだけを渡さない。
- 平易な進捗説明を使う。内部状態名を主語にせず、「今どの段階か」「何をしたか」「次に何をするか」を先に述べる。

## 4. 直近の完了事項

- Requirement 13〜16 を基点に、requirements/design/tasks/implementation を縦方向意図監査の結果へ合わせて再生成・修正。
- requirements triad-review を実施し、API 版 gpt-5.5 proxy_model 判定で C1〜C3 を should-fix として反映、C4 は leave-as-is。
- requirements review-wave を実施し、他 feature の requirements 正本変更は不要と確認。
- requirements alignment を完了し、Requirement 13〜16 と design/tasks の追跡、triad-review 修正反映、review-wave 影響確認を記録。
- design / tasks / implementation の triad-review、review-wave、alignment、approval を完了。
- implementation review-run の Req15 / Req16 API レビュー結果を同根クラスタへ整理し、triage 案と traceability report を保存。
- API レビュー用 prompt の品質課題を受け、汎用コア + カスタマイズ、main preanalysis、prompt audit、variant default 機械判定の考え方を整理・実装。
- `workflow-management` implementation approval 完了により、全 workflow_state が `completed` になった。
- Codex の commit 実行環境と利用者向け報告文の規律を明確化。
- commit 中の進行報告最小化規律を追加。
- commit 操作機械処理化に向け、失敗ケースメモを `docs/notes/working/2026-06-20-commit-operation-failure-cases.md` に追加。
- `main` を `origin/main` へ push 済み。直近 push 範囲の終端は `f772a39a`。

## 5. 参照

- workflow navigation: `docs/operations/WORKFLOW_NAVIGATION.md`
- session guide: `docs/operations/SESSION_WORKFLOW_GUIDE.md`
- discipline map: `docs/operations/WORKFLOW_DISCIPLINE_MAP.yaml`
- workflow-management tasks: `.reviewcompass/specs/workflow-management/tasks.md`
- workflow-management spec: `.reviewcompass/specs/workflow-management/spec.json`

過去の詳細履歴は git log、`docs/notes/`、`docs/archive/todo/`、`docs/sessions/` を正本とする。
