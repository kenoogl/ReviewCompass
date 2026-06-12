---
feature: all_features
phase: all
stage: completed-summary
date: 2026-06-12
status: completed
record_type: completed-workflow-summary
supersedes: 2026-06-09-completed-workflow-summary.md
---

# ReviewCompass Completed Workflow Summary（2026-06-12 現時点版）

## Summary

2026-06-12 時点で、ReviewCompass の全 7 feature は intent、feature-partitioning、requirements、design、tasks、implementation の全段を完了している。`tools/check-workflow-action.py next --json` は `kind: completed` を返し、作業ツリーは clean、`main` は `origin/main` と `b4543bd3` で同期している。

本記録は 2026-06-09 版（`2026-06-09-completed-workflow-summary.md`）の現時点改訂版である。completed は一度きりの到達点ではなく、reopen（承認済み仕様の開き直し手続き）のたびに失われ再到達する機械状態であり、06-09 版以降に 2 件の reopen と運用準備・アドホック開発の仕様反映を経て、本日再々到達した断面を記録する。

この文書は、完了後に次の運用・リリース・追加改善を検討するための全体サマリである。作業順序の正本ではない。今後も作業開始時は `tools/check-workflow-action.py next --json` と各 feature の `spec.json` を正本として扱う。

## Completed Scope

対象 feature（06-09 版から不変）:

- `foundation`
- `runtime`
- `evaluation`
- `analysis`
- `workflow-management`
- `self-improvement`
- `conformance-evaluation`

対象 phase / stage:

| Phase | Completed stages |
| --- | --- |
| intent | drafting, review, approval |
| feature-partitioning | candidate-proposal, approval |
| requirements | drafting, triad-review, review-wave, alignment, approval |
| design | drafting, triad-review, review-wave, alignment, approval |
| tasks | drafting, triad-review, review-wave, alignment, approval |
| implementation | drafting, triad-review, review-wave, alignment, approval |

各 feature の完了役割は 06-09 版の Feature Outcomes を正本として引き継ぐ（変更なし）。

## 06-09 版以降の到達点（56 コミット、13f3e493..b4543bd3）

### 1. completed follow-up の正式化（2026-06-09）

将来計画候補 9 件（D-021／D-004／D-005／D-025／D-027／D-008／D-019／D-020／D-023）を、conformance 評価（`gap_found`）を経て正式な completed follow-up 成果物へ昇格した。残る仕様・設計の隙間は所有権記録で引き継ぎ、仕様更新は reopen 経由に経路付けた。完了レポート契約・readiness データスキーマと lint・配布 lint push ガードもここで追加。

- 記録：`.reviewcompass/specs/conformance-evaluation/conformance/2026-06-09-completed-followup-conformance.md`、`docs/notes/2026-06-09-formal-completed-followup-summary.md`、`docs/notes/2026-06-09-completed-followup-contract-ownership.md`

### 2. effective prompt 機構（2026-06-09〜10）

判定点ごとに規律・入力・次タスク方針を 1 本に束ねた effective prompt を生成・記録する機構を導入した（`WORKFLOW_DISCIPLINE_MAP.yaml` を元資料の正本とし、`next` が `.reviewcompass/effective-prompts/` へ保存、`effective_prompt_path`／`sha256`／`loaded` を返す）。文書リンクの commit ガードも追加。

### 3. 初期デプロイ一式（2026-06-09〜10）

deploy manifest、配布物生成ツール（`tools/build-deploy-package.py`）、配布物検査、外部アプリ root への smoke、初期導入利用者ガイド、初期設定 LLM ガイド、Claude／Codex adapter 整合を整備した。smoke は `.venv` 依存（`httpx`）。

### 4. 配布側複数 LLM 入口整備（2026-06-10〜12、アドホック開発の仕様反映まで）

操縦 LLM（Claude／Codex）を問わず対象アプリへ配布・導入できる入口を整備した。実装先行のアドホック開発として実施し、事後に conformance 評価（`gap_found`、契約 8 件 MLE-C-001〜008・隙間 6 件 MLE-GAP-001〜006）→ 利用者決定 → reopen R-0 で正本仕様へ反映した。

- 内容：feature 一覧解決の一般化（`feature_order` キー・探索順・立ち上げ案内 `feature_definition_required`・依存整合検査）、入口／hook／feature-dependency テンプレート配布、操縦 LLM 別の API 既定 variant、ガイド 3 文書更新
- 仕様反映先：workflow-management の requirements（Requirement 8 受入 6〜8）・design（配布テンプレート契約の設計境界）・tasks（T-004 の kind 語彙）、規律文書（`WORKFLOW_NAVIGATION.md`・`WORKFLOW_DISCIPLINE_MAP.yaml`）
- 記録：`docs/notes/2026-06-10-deployment-multi-llm-entry-design.md`、`.reviewcompass/specs/conformance-evaluation/conformance/2026-06-12-completed-followup-conformance.md`、`stages/completed/reopen-procedure-2026-06-12.yaml`、`stages/completed/maintenance-2026-06-11-feature-order-generalization.yaml`

### 5. 堅牢化 2 件（2026-06-12）

- 検査ツールの実行ログ（`docs/logs/workflow-precheck.log`）を post-write 検証対象から除外する根本対応（`stages/completed/maintenance-2026-06-12-postwrite-log-exclusion.yaml`）
- `feature-dependency.yaml` のパース不能・空・非連想配列・非 UTF-8 を、立ち上げ案内（OK）から遮断（DEVIATION、fail-closed）へ分離（MLE-DEC-005。reopen 一式＋TDD。`stages/completed/reopen-procedure-2026-06-12-parse-error-failclosed.yaml`）

### 6. 小規模追従（2026-06-12）

- 評価記録スキーマ `evaluation_record.schema.json` の `mode_internal` 列挙値を実記録 5 値へ追従（`stages/completed/maintenance-2026-06-12-evaluation-record-mode-enum.yaml`）
- 配布物を再生成（267 ファイル）し、堅牢化 2 件の反映を確認、配布物検査と外部アプリ root smoke に合格（`build/deploy/` は追跡対象外）

## 利用者決定の台帳（2026-06-12）

`.reviewcompass/specs/conformance-evaluation/conformance/2026-06-12-reopen-handoff-package.yaml` の `human_decisions`：

| ID | 決定 |
| --- | --- |
| MLE-DEC-001 | 語彙調停は案 A。仕様を実装語彙 `feature_order` へ寄せ、旧称 `phase_order` は由来注記で読み解く |
| MLE-DEC-002 | feature-dependency のスキーマ契約は実装検査（解決・整合検査の実装とテスト）で代替 |
| MLE-DEC-003 | `feature-dependency.yaml` の features を承認済み分割提案書から 7 機能分実体化 |
| MLE-DEC-004 | 操縦 LLM 別 variant 既定は evaluation 仕様へ昇格せず、`SESSION_WORKFLOW_GUIDE.md` §3.3 (a-3) を正本とする。昇格は実アプリ pilot 後に再検討 |
| MLE-DEC-005 | パース不能の遮断分離を根本対策として実施（triad-review r2 F4 の案 a 決定を利用者自身が改めた） |

## Review And Gate Evidence

完了判定は会話上の記憶ではなく機械状態へ固定されている（06-09 版から不変の原則）：

- `tools/check-workflow-action.py next --json` と feature ごとの `spec.json`
- review-run の raw / parsed / summary / triage / approval 記録
- post-write verification manifest、commit approval guard、carry-forward register
- 06-09 版以降の追加証跡：effective prompt 記録（`effective_prompt_path`／`sha256`）、文書リンク lint、配置非依存 lint、配布 readiness lint

検証状態（2026-06-12 実測）：既定 testpaths 599 件＋残り 7 群 429 件、計 1028 件通過、回帰なし。

## Current Operating Rule

通常ワークフロー上の未完了タスクはない。次に作業する場合は、まず以下を確認する。

```bash
.venv/bin/python3 tools/check-workflow-action.py next --json
git status --short
git log --oneline -5
```

`next --json` が `completed` 以外（`post_write_verification`、`reopen_in_progress`、`resume_in_progress`、`maintenance_in_progress`、`unknown` など）を返した場合は、通常作業へ進まずその指示に従う。`completed` が維持されている場合のみ、運用・リリース・追加改善などの新しい作業を別途定義する。

## Candidate Next Work

完了後の候補作業（2026-06-12 時点。入口は `TODO_NEXT_SESSION.md` §4）：

1. 配布物の配置と実アプリ pilot の開始（`docs/operations/INITIAL_DEPLOYMENT_USER_GUIDE.md` 第 9 節以降。配布物は再生成・smoke 済みで前提は整っている）
2. 判断 2（実行時生成物）関連の議論：初期設定ガイド §8 の `.gitignore` 手順の簡素化余地、`.reviewcompass/effective-prompts/` の生成物運用（利用者が後から予定していると明言）
3. `post_hoc_intent_diff` の実データ試行結果を、将来の fixture または回帰確認に使うかの判断
4. review-wave 改善メモの実質残件 2 件：review-wave 要約コマンドの実装、API レビュー証跡の機能側ポインタ要件の一般化（2026-06-12 棚卸しで確認。recheck 解除の正規ルールは対応済み）
5. 検討材料：`learning/workflow/proposals/WP-001-finding-cause-attribution.yaml`（外れ所見の原因分類軸）、`docs/notes/2026-06-11-agentic-flow-adoption-plan.md`
