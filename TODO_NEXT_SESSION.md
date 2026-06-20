# 次セッション継続用メモ

最終更新：2026-06-20（Codex セッション、`42b63f18` までローカル commit 済み。`origin/main` より 3 commits ahead）。

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

- `main` は `origin/main` より 3 commits ahead。
- 作業ツリーは clean。
- 直近 commit: `42b63f18 Record commit operation failure cases`
- `next --json` は `reopen_in_progress`。
- 現在の本筋は `workflow-management` の Requirement 13〜16 を基点にした reopen R-0。
- requirements は再生成、triad-review、review-wave、alignment、approval まで完了済み。
- 次の停止点は requirements approval 完了コミット後の記録消化。これを済ませると design triad-review へ進む。
- 進行中ファイル: `stages/in-progress/reopen-procedure-2026-06-19.yaml`
- 次の pending gate:
  - `stages/design.yaml#triad-review`
  - `stages/design.yaml#review-wave`
  - `stages/design.yaml#alignment`
  - `stages/design.yaml#approval`
  - `stages/tasks.yaml#triad-review`
  - `stages/tasks.yaml#review-wave`
  - `stages/tasks.yaml#alignment`
  - `stages/tasks.yaml#approval`

## 3. 次作業

次に行うこと：

1. requirements approval の停止点を完了済みとして記録する。
   - 対象 commit: `c09a6f9de1144a46fae98aea4a59b92384308c2b`
   - kind: `approval_complete`
   - gate: `stages/requirements.yaml#approval`
2. `next --json` を再実行し、design triad-review が次作業になることを確認する。
3. design triad-review の API review-run を開始する前に、使用 variant と role ごとの path／provider／model を利用者へ提示して停止する。
4. design triad-review では、requirements.md → design.md の意図伝達を必ず確認する。
   - Requirement 13〜16 の目的、責務境界、受入条件、禁止事項が design.md の設計判断へ落ちているかを見る。
   - design.md が審査対象で、requirements.md は上流資料。tasks.md はこの段では審査対象ではない。

進め方の注意：

- `next --json` が示す停止点を飛ばさない。
- commit / push は利用者の明示指示がある場合だけ実行する。
- triad-review の API review-run 前には、variant と role 割当を利用者に提示する。
- review prompt は、上流資料のパス名だけでなく、必要な本文または要点を含める。
- 平易な進捗説明を使う。内部状態名を主語にせず、「今どの段階か」「何をしたか」「次に何をするか」を先に述べる。

## 4. 直近の完了事項

- Requirement 13〜16 を基点に、requirements/design/tasks を縦方向意図監査の結果へ合わせて再生成。
- requirements triad-review を実施し、API 版 gpt-5.5 proxy_model 判定で C1〜C3 を should-fix として反映、C4 は leave-as-is。
- requirements review-wave を実施し、他 feature の requirements 正本変更は不要と確認。
- requirements alignment を完了し、Requirement 13〜16 と design/tasks の追跡、triad-review 修正反映、review-wave 影響確認を記録。
- 利用者承認により requirements approval を完了。
- Codex の commit 実行環境と利用者向け報告文の規律を明確化。
- commit 中の進行報告最小化規律を追加。
- commit 操作機械処理化に向け、失敗ケースメモを `docs/notes/working/2026-06-20-commit-operation-failure-cases.md` に追加。
- `main` を `origin/main` へ push 済みなのは `c09a6f9d` まで。`e544d680`、`0c146630`、`42b63f18` は未 push。

## 5. 参照

- workflow navigation: `docs/operations/WORKFLOW_NAVIGATION.md`
- session guide: `docs/operations/SESSION_WORKFLOW_GUIDE.md`
- discipline map: `docs/operations/WORKFLOW_DISCIPLINE_MAP.yaml`
- workflow-management tasks: `.reviewcompass/specs/workflow-management/tasks.md`
- workflow-management spec: `.reviewcompass/specs/workflow-management/spec.json`

過去の詳細履歴は git log、`docs/notes/`、`docs/archive/todo/`、`docs/sessions/` を正本とする。
