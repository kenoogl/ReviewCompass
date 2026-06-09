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

## 2026-06-08 tasks 再確認への対応

intent の「レビュー収集処理を事前設定の写像にしない」意図に伴い、workflow-management tasks.md の変更を implementation 観点で再確認した。

- T-004 の `next` による上流更新再展開は、`tools/check-workflow-action.py next --json` と `tests/tools/test_check_workflow_action.py` の upstream recheck 系テストで受けられている
- 2026-06-08 の reopen 判定修正により、完了済み workflow の上流正本更新は `upstream_recheck` ではなく `reopen_classification_required` として返す。`tools/check-workflow-action.py` と `tests/tools/test_check_workflow_action.py` は intent → feature-partitioning、requirements → design、tasks → implementation の代表経路を検証する
- T-006 の不可逆操作直前ゲートは、`tools/check-workflow-action.py` の commit／push／spec-set／phase-transition 系検査と `tests/tools/test_check_workflow_action.py` で受けられている
- T-008 の session 跨ぎ状態管理は、`stages/in-progress/` 優先判定、maintenance side track 判定、post-write pending 判定として `tools/check-workflow-action.py` と `tests/tools/test_check_workflow_action.py` で受けられている
- T-002 の機能依存マップ一元化は、`stages/feature-dependency.yaml` の `feature_order`／`depends_on` 参照と `tests/tools/test_check_workflow_action.py` で受けられている

確認結果として、実装済み workflow-management は次作業を事前設定の写像として固定せず、現在の成果物・進行中状態・post-write manifest・機能依存マップを読み直して `next_action` を機械判定している。完了済み workflow の上流正本更新は reopen 分類へ送るよう修正済みである。

## 2026-06-09 後追い intent 下流再展開への対応

追加 intent を既存システムに適用する今回の reopen では、workflow-management は CE の差分候補を実行命令として直接適用せず、reopen 手続きの候補として受け取る。

実装確認結果：

- `tools/check-workflow-action.py` は、`pending_gates` が triad-review を指していても `drafting_completed_gates` または `completed_gates` に該当 phase の drafting がなければ `run_reopen_drafting` を返す
- `tests/tools/test_check_workflow_action.py` の `test_next_reopen_requires_drafting_before_triad_review` がこの逸脱防止を検査する
- reopen 完了時の `downstream_impact_decisions` coverage 検査は、完了 gate の判断記録欠落を遮断する
- CE T-016 の出力は `.reviewcompass/specs/conformance-evaluation/conformance/2026-06-09-post-hoc-intent-diff.md` に記録され、workflow-management はそのうち `downstream_impact_candidate` を reopen 判断として扱う

今回、workflow-management の追加コード変更は不要と判断した。理由は、tasks 段までで追加した Requirement 9 / XDI-WM-002 の実装上の受け皿が既に `next`、reopen in-progress state、完了時 coverage 検査に存在するためである。

### Requirement 9 / XDI-WM-002 実装対応表

| 要素 | 実装 | テスト |
| --- | --- | --- |
| 後追い intent の reopen 進行中状態を優先する | `tools/check-workflow-action.py:build_in_progress_next_action` | `tests/tools/test_check_workflow_action.py::NextNavigationTests::test_next_reads_reopen_in_progress_next_step` |
| triad-review の前に drafting を要求する | `tools/check-workflow-action.py:_resolve_reopen_next_gate` | `tests/tools/test_check_workflow_action.py::NextNavigationTests::test_next_reopen_requires_drafting_before_triad_review` |
| 全 feature scope を feature impact decisions から返す | `tools/check-workflow-action.py:reopen_feature_scope_from_data` | `tests/tools/test_check_workflow_action.py::NextNavigationTests::test_next_reopen_uses_feature_impact_decisions_as_review_scope` |
| 完了済み gate も downstream decision で覆う | `tools/check-workflow-action.py:validate_reopen_completion_impact_decisions` | `tests/tools/test_check_workflow_action.py::CommitExitCodeTests::test_commit_blocks_completed_reopen_missing_completed_gate_decision` |
| downstream decision があれば reopen 完了 commit を許可する | `tools/check-workflow-action.py:validate_reopen_completion_impact_decisions` | `tests/tools/test_check_workflow_action.py::CommitExitCodeTests::test_commit_allows_completed_reopen_with_completed_gate_decisions` |
| 影響 phase を gate 判断で覆る | `tools/check-workflow-action.py:validate_reopen_completion_impact_decisions` | `tests/tools/test_check_workflow_action.py::CommitExitCodeTests::test_commit_blocks_completed_reopen_when_impacted_phase_is_uncovered` |

CE T-016 の試行結果は、WM が直接ファイルへ自動反映する入力ではない。WM は CE 候補を受け、reopen の各 gate で `downstream_impact_decisions` に人間または承認済み判断を記録する。これにより、候補抽出と正式な workflow 遷移を分離する。

追加で、drafting-before-review の中核回帰テストを単独実行した。

- `.venv/bin/python3 -m unittest tests.tools.test_check_workflow_action.NextNavigationTests.test_next_reopen_requires_drafting_before_triad_review -v`：pass

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
