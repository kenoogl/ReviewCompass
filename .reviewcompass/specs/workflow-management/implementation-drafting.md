# workflow-management implementation drafting 棚卸し

## 目的

workflow-management implementation.drafting の現時点の実装状況を、後続の triad-review と利用者判断で追えるようにする。

今回のターゲットは、自律・並列実行をできるだけ人の承認なしで進め、事後に履歴を確認できるようにすることである。不可逆操作である commit、push、spec.json 更新、フェーズ移行は引き続き人間の明示承認を要求する。

## 実装済み

### 自律・並列実行計画ガード

`tools/check-workflow-action.py autonomous-plan <plan.yaml>` を実装済み。

検査内容：

- `mode: autonomous_parallel` と `run_id`
- 人間または `proxy_model` の承認記録
- レビュー結果サマリと三段階トリアージの提示済みフラグ
- task ごとの `source_finding_ids`、担当、許可パス、期待テスト、停止条件
- 別スレッドまたはサブ担当の `separate_worktree`
- 依存関係のない並列 task の `allowed_paths` 衝突
- 統合ゲート
- 生成物分類
- 履歴台帳設定

### 自律・並列実行計画テンプレート

`tools/check-workflow-action.py autonomous-plan-template --run-id <run-id> --out <plan.yaml>` を実装済み。

生成される YAML は `autonomous-plan` の必須フィールドを満たし、そのまま検査可能である。実作業では、生成後に `tasks[]` の `source_finding_ids`、`allowed_paths`、`expected_tests` を実対象へ差し替える。

### 自律・並列実行履歴台帳

`autonomous-plan` 実行時に `docs/logs/autonomous-parallel/<run-id>.yaml` へ履歴台帳を書き出す。

台帳には、`run_id`、verdict、reasons、task IDs、承認根拠、統合ゲート、出力分類、current_state を記録する。

デプロイ後監査では plan ファイルが残らない可能性があるため、ledger を事後監査の正本とする。`autonomous-plan` は `execution_evidence_snapshot` を ledger に保存し、`completed_tasks`、`parallelized_operations`、`human_required_count` を plan なしで確認できるようにする。既存 ledger に snapshot がある場合、古い plan の再実行では snapshot を巻き戻さない。

`tools/check-workflow-action.py autonomous-ledger-audit <ledger.yaml>` を実装済み。これは plan ファイルなしで、ledger の `mode`、verdict、`execution_evidence_snapshot`、`integration_result` を検査する。

### 統合結果追記

`tools/check-workflow-action.py autonomous-plan-record-integration --ledger <ledger.yaml> --status <status> --tests "<tests>" --decision "<decision>"` を実装済み。

統合後に既存台帳へ `integration_result` を追記し、次を後から確認できる。

- 統合状態：`completed`、`blocked`、`rejected`
- 実行したテストまたは未実行理由
- メインセッション LLM の統合判断

`tools/api_providers/review_triage.py assert-review-report-ready` は、`integration_result` だけでなく `execution_evidence_snapshot` も要求する。これにより、自動実行報告の ready 判定は plan に依存せず、ledger 単独で監査可能な状態を前提にする。

### 正本仕様

`docs/operations/WORKFLOW_PRECHECK.md` に、次のサブコマンド仕様を追記済み。

- `autonomous-plan`
- `autonomous-plan-template`
- `autonomous-plan-record-integration`

## 未充足

workflow-management 全体の T-001〜T-011 は、まだ一括完了ではない。

現時点で特に残る事項：

- T-001〜T-003：`stages/` 配下の 9 ファイル体制と stage schema の実装は未完了部分がある。
- T-005：front-matter checker の独立モジュール化は未完了。
- T-006：不可逆操作ゲートは commit/push/spec-set を中心に実装済みだが、設計上の 4 種類すべてを専用モジュールへ分離する作業は未完了。
- T-007：reopen resolver の専用モジュール化は未完了。ただし `reopen-start` と `next` による進行中ファイル処理は部分実装済み。
- T-008：in-progress manager の専用モジュール化は未完了。ただし `next` は in-progress を優先して読める。
- T-009〜T-011：運用文書、規律変更接合面、統合テスト全体は未完了事項が残る。

今回の実装は、T-004 の検査スクリプト本体と、自律・並列実行を安全に始めて履歴を残すための追加ガードに集中している。

## 検証

実行済み：

- `python3 -m unittest tests.tools.test_check_workflow_action -v`
- `python3 -m pytest tests/tools/test_session_record_contract.py -q`
- `python3 -m pytest tests/tools/test_workflow_management_implementation_drafting.py -q`
- `python3 tools/check-workflow-action.py next --json`

結果：

- `tests.tools.test_check_workflow_action` は通過
- `tests/tools/test_session_record_contract.py` は通過
- `tests/tools/test_workflow_management_implementation_drafting.py` は通過予定の棚卸し検査
- `next` は `workflow-management / implementation / drafting` を返す

## drafting 完了判断

現時点では、workflow-management implementation.drafting の下書き成果物として、本棚卸しを作成した段階である。

推薦判断：

1. 本棚卸しをもとに implementation.drafting の triad-review へ進める。
2. triad-review では、T-004 周辺の実装を重点的に確認し、T-001〜T-011 全体の未充足を drafting 完了の阻害要因とするか、後続 implementation task として扱うかを判定する。
3. spec.json の `workflow-management.implementation.drafting=true` 更新は、人間の明示承認後に行う。
