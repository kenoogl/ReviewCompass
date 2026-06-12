# 次セッション継続用メモ

最終更新：2026-06-12（夜）。正本は `tools/check-workflow-action.py next --json` と各 feature の `spec.json`。この TODO は入口メモであり、作業順序の正本ではない。

ReviewCompass は、複数 LLM のレビュー結果を raw で保存し、三段階トリアージと人間／proxy_model の判断を経て、仕様・実装・規律を改善するための自己適用型レビュー基盤である（詳細は `intent/` と各 feature の仕様を正本とする）。

作業ディレクトリ：`/Users/Daily/Development/ReviewCompass/`
リポジトリ：`git@github.com:kenoogl/ReviewCompass.git`（main ブランチ）

## 1. 起動時に必ず行うこと

1. `.venv/bin/python3 tools/check-workflow-action.py next --json` を実行し、`next_action` を作業順序の正本として扱う。
2. `git status --short` と `git log --oneline -5` で到達点を確認する。
3. `next_action.required_disciplines` に出た規律だけを、操作直前に読む。
4. `post_write_verification`、`reopen_in_progress`、`resume_in_progress`、`unknown` が返った場合は通常作業へ進まない。

## 2. 不可逆操作の規律（要点）

- commit・push・spec.json（workflow_state）・規律ファイルの変更は、利用者の明示承認が必要。commit は利用者から「コミット」と明示された場合だけ、`tools/guarded-git-commit.py` 経由で実行する。
- API review-run は実行前に variant と役ごとの provider／model を提示し、結果は raw・モデル別要約・三段階トリアージをまとめて提示してから次へ進む。操縦 LLM 別の既定 variant と独立性原則の正本は `docs/operations/SESSION_WORKFLOW_GUIDE.md` §3.3 (a-3)。
- 詳細の正本は `docs/operations/WORKFLOW_NAVIGATION_FOR_CLAUDE.md` §2 と `docs/operations/SESSION_WORKFLOW_GUIDE.md`。

## 3. 現在位置（2026-06-12 夜時点）

- `next --json`：`kind: completed`（全 7 feature の workflow_state 完了）。
- `main` と `origin/main` は `976655b9` で同期済み。作業ツリー clean。全テスト群 877 件通過。
- 本日完了した事項（記録が正本、ここは要約のみ）：
  1. アドホック開発（配布側複数 LLM 入口）の仕様反映：conformance 評価（`gap_found`）→ reopen R-0 で requirements／design／tasks へ反映（語彙は `feature_order` へ統一・案 A）。記録：`.reviewcompass/specs/conformance-evaluation/conformance/2026-06-12-completed-followup-conformance.md`、`stages/completed/reopen-procedure-2026-06-12.yaml`
  2. 操縦 LLM 別 variant 既定の正本化（evaluation 仕様へは昇格せず。MLE-DEC-004）
  3. 検査ツールの実行ログを post-write 検証対象から除外（義務 2 の根本対応。`stages/completed/maintenance-2026-06-12-postwrite-log-exclusion.yaml`）
  4. feature-dependency.yaml パース不能・空・非連想配列・非 UTF-8 の遮断分離（MLE-DEC-005。reopen 一式＋TDD。`stages/completed/reopen-procedure-2026-06-12-parse-error-failclosed.yaml`）
- 利用者決定の台帳：`.reviewcompass/specs/conformance-evaluation/conformance/2026-06-12-reopen-handoff-package.yaml` の `human_decisions`（MLE-DEC-001〜005）。

## 4. 次作業

予定済みの議論（利用者が「後から予定している」と明言。忘れないこと）：

1. 判断 2（実行時生成物）関連の議論：初期設定ガイド §8 の `.gitignore` 手順の扱い（ログは検査対象から除外済みのため簡素化余地あり）、`.reviewcompass/effective-prompts/` の生成物運用。

候補タスク：

1. **配布物の再生成と配布前 smoke**：本日ツール改修 2 件（ログ除外・遮断分離）が `build/deploy` に未反映。実アプリ pilot の前に必要。
2. `docs/operations/INITIAL_DEPLOYMENT_USER_GUIDE.md` 第 9 節以降に従い、配布物の配置と実アプリ pilot を開始する。
3. completed 到達後の全体サマリを作る。
4. `post_hoc_intent_diff` の実データ試行結果を、将来の fixture または回帰確認に使うか判断する。
5. review-wave 改善メモに残した follow-up candidates を、次の改善候補として扱う。
6. 検討材料として記録済み：`learning/workflow/proposals/WP-001-finding-cause-attribution.yaml`（外れ所見の原因分類軸）、evaluation_record.schema.json の mode_internal enum 追従（conformance 記録の付随観察）。

## 5. 参照

- workflow navigation：`docs/operations/WORKFLOW_NAVIGATION.md`
- session guide：`docs/operations/SESSION_WORKFLOW_GUIDE.md`
- 複数 LLM 入口の設計記録：`docs/notes/2026-06-10-deployment-multi-llm-entry-design.md`
- carry-forward register：`learning/workflow/carry-forward-register/reviewcompass-import.yaml`

過去の完了事項の履歴は git log と `docs/notes/`・`stages/completed/` の各記録を正本とする（本 TODO には残さない）。
