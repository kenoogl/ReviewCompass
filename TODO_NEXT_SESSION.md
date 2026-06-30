# 次セッション継続用メモ

最終更新：2026-06-30（Codex ローカル）。最新状態は必ず `git log --oneline -5`、`git status --short --branch`、`tools/check-workflow-action.py next --json` を直接確認する。

## 1. 現在状態

- この TODO 更新コミット後、`main` は `origin/main` より 1 commit ahead の想定。
- 最新 push 済みコミット：`b13d97ee maintenance workflow protocol planを完了へ更新`
- clean 状態の `tools/check-workflow-action.py next --json` は `kind: completed` を返す想定。
- 全 feature の workflow_state は implementation.approval まで完了済み。
- この TODO 更新コミット後の作業ツリーは clean の想定。

## 2. 直近で完了した作業

- MWP-0 A/B/C 論点は実装・テスト・コミット済み。
  - A：if/then 制約補完（`80943687` / `b978abd4`）
  - B：commit-preflight の kind 分離（`c8ead8fb`）
  - C：`next_action.reason` と最上位 `reasons` の責務差明確化（`e3e5b55a` / `0da4f15a`）
- workflow-management implementation の review-wave / alignment / approval は完了済み。
- approval 段の human-only 境界記述を修正済み（`72e2d720`）。
- sandbox / 非TTY 環境の guarded commit issue を完了済み（`102e9611`）。
- post-write target 判定を workflow specs 除外へ整合済み（`eef7cd7a`）。
- 旧試行の未追跡 post-write review-run と manifest は削除済み。
- TODO とセッション記録の現状反映をコミット・push 済み（`94582f51`）。
- maintenance workflow protocol plan は MWP-0 から MWP-3 まで完了し、plan / index とも completed へ更新済み（`b13d97ee`）。

## 3. 残っている未コミット変更

この TODO 更新コミット後はなし。

## 4. 次にやること

推奨候補は `.reviewcompass/backlog/plans/plan-2026-06-23-entrypoint-coverage-audit.yaml` の `ECA-1` から開始すること。
目的は、`next --json` の地点から LLM が記憶や前例で迷わず、登録済みの effective prompt / required_action / 機械処理 / evidence へ辿れるようにする入口棚卸しである。

実装計画：

1. 開始前確認
   - `git status --short --branch` と `tools/check-workflow-action.py next --json` を確認する。
   - 対象 plan がまだ `candidate` であることを確認し、作業範囲を `ECA-1` に限定する。
2. Red test 作成
   - 既存の `next_action.kind` を列挙できることを期待するテストを追加する。
   - 主要 CLI subcommand を列挙できることを期待するテストを追加する。
   - entrypoint ごとに `required_action`、expected effective prompt、evidence path の有無を記録できることを期待するテストを追加する。
   - 未登録入口、effective prompt 欠落、mechanized command 欠落を少なくとも WARN / DEVIATION 候補として検出できる赤テストを置く。
3. Red test 失敗確認
   - 実装を追加する前に、追加テストが期待どおり失敗することを確認する。
   - 失敗がテスト前提の誤りでないことを確認した段階で、テストのみをコミット停止点にする。
4. 実装
   - entrypoint inventory 用の read-only 関数または CLI subcommand を追加する。
   - 初期対象は `next_action.kind`、`tools/check-workflow-action.py` の主要 subcommand、user-initiated backlog/checklist operation、commit / push operation に限定する。
   - 出力には entrypoint id、kind、trigger、required_action、expected effective prompt、mechanized command、evidence path を含める。
   - 実行結果は機械処理しやすい JSON とし、LLM 向けの自由記述に依存しない。
5. 検証
   - 追加テストを通す。
   - 必要なら既存の workflow action / maintenance protocol 関連テストも通す。
   - `tools/check-workflow-action.py next --json` が従来どおり `kind: completed` を返すことを確認する。
6. 完了処理
   - `ECA-1` の完了範囲を plan に反映する。
   - TODO / セッション記録が必要なら更新する。
   - コミットし、必要に応じて push する。

## 5. 参照

- commit 手順：`.reviewcompass/guidance/COMMIT_OPERATION_CARD.md`
- ワークフロー操作ガイド：`.reviewcompass/guidance/WORKFLOW_NAVIGATION.md`
- 入口 coverage audit 計画：`.reviewcompass/backlog/plans/plan-2026-06-23-entrypoint-coverage-audit.yaml`
- operation registry / preflight 計画：`.reviewcompass/backlog/plans/plan-2026-06-23-operation-registry-preflight.yaml`
- effective prompt freshness audit 計画：`.reviewcompass/backlog/plans/plan-2026-06-23-effective-prompt-freshness-audit.yaml`
- kind 再設計メモ：`docs/notes/2026-06-26-next-json-kind-redesign.md`
- A 観点レビュー記録：`.reviewcompass/specs/workflow-management/reviews/2026-06-27-workflow-management-implementation-mwp0-ifthen-review-run/`
- B 観点レビュー記録：`.reviewcompass/specs/workflow-management/reviews/2026-06-27-workflow-management-implementation-mwp0-kind-sep-review-run/`
- C 観点レビュー記録：`.reviewcompass/specs/workflow-management/reviews/2026-06-27-workflow-management-implementation-mwp0-reason-review-run/`

過去の詳細は git log、`docs/notes/`、`docs/sessions/` を正本とする。
