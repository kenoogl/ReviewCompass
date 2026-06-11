# 次セッション継続用メモ

最終更新：2026-06-12。正本は `tools/check-workflow-action.py next --json` と各 feature の `spec.json`。この TODO は入口メモであり、作業順序の正本ではない。

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
- API review-run の結果は、raw・モデル別要約・三段階トリアージをまとめて提示してから次へ進む。
- 詳細の正本は `docs/operations/WORKFLOW_NAVIGATION_FOR_CLAUDE.md` §2 と `docs/operations/SESSION_WORKFLOW_GUIDE.md`。

## 3. 現在位置（2026-06-12 時点）

- `next --json`：`kind: completed`（全 7 feature の workflow_state 完了）。
- `main` と `origin/main` は `3730571` で同期済み。作業ツリー clean。
- 配布側複数 LLM 入口整備（設計記録：`docs/notes/2026-06-10-deployment-multi-llm-entry-design.md`）の実装計画ステップ 1〜5 と論点 5 が完了：ツール一般化（feature_order の外出し・立ち上げ案内・依存整合検査）、入口・hook・feature-dependency の各テンプレート、操縦 LLM 別の API 既定 variant、ガイド 3 文書の更新、配布物の再生成と模擬対象アプリでの実証。

## 4. 次作業

未完了の義務（アドホック開発の後始末。完了までがこの作業の完了条件、忘れないこと）：

1. conformance-evaluation を起動し、アドホック開発した内容（実装計画ステップ 1〜5）の差分を workflow-management 等の仕様へ反映する。
2. その際の改修候補：ツールが自分の実行時生成物（`docs/logs/workflow-precheck.log`、`.reviewcompass/effective-prompts/`）を post-write 検証対象から除外する根本対応（現状は初期設定ガイド §8 の `.gitignore` 追記で回避。2026-06-12 のステップ 5 実験で発見）。
3. 検討材料として記録済み：`learning/workflow/proposals/WP-001-finding-cause-attribution.yaml`（外れ所見の原因分類軸）。

候補タスク：

1. `docs/operations/INITIAL_DEPLOYMENT_USER_GUIDE.md` 第 9 節以降に従い、配布物の配置と実アプリ pilot を開始する。
2. completed 到達後の全体サマリを作る。
3. `post_hoc_intent_diff` の実データ試行結果を、将来の fixture または回帰確認に使うか判断する。
4. review-wave 改善メモに残した follow-up candidates を、次の改善候補として扱う。

## 5. 参照

- workflow navigation：`docs/operations/WORKFLOW_NAVIGATION.md`
- session guide：`docs/operations/SESSION_WORKFLOW_GUIDE.md`
- 複数 LLM 入口の設計記録：`docs/notes/2026-06-10-deployment-multi-llm-entry-design.md`
- carry-forward register：`learning/workflow/carry-forward-register/reviewcompass-import.yaml`

過去の完了事項の履歴は git log と `docs/notes/` の各記録を正本とする（本 TODO には残さない）。
