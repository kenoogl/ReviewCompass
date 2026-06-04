# proxy review 判断代行と並列実装の正本化計画メモ

作成日：2026-06-04

## 目的

API review-run 後に、メインセッション LLM が raw レビューを集約して三段階トリアージし、重要件の判断を proxy_model が代行し、実装作業を必要に応じて別スレッド・分離 worktree へ切り出せるようにする。

本メモは、会話上の運用案を正本と機械ガードへ落とすための計画メモである。正本は `docs/operations/SESSION_WORKFLOW_GUIDE.md` と workflow-management 仕様であり、本メモは作業計画と段階導入の記録に限定する。

## 正本化する事項

1. メインセッション LLM は raw review を読み、モデル別要約、同根所見集約、三段階トリアージ下書き、候補案、推薦案を作る。
2. proxy_model は重要件について、採用案、判断理由、棄却案理由、最終ラベルを決める。
3. 機械ガードは proxy decision、raw response、候補案、採用案、判断理由、triage との整合を検査する。
4. 実装サブ担当 LLM は、原則として別スレッドかつ分離 worktree で扱う。
5. 別スレッド生成物は、実装差分、検証結果、判断根拠、作業ノイズに分類する。
6. 作業ノイズは本線 repo に取り込まない。
7. コミット、プッシュ、spec.json 更新、フェーズ移行は人間の明示承認を要求し、proxy_model は代行しない。

## 今回の実装範囲

- `review_triage.py` の approval record 検査で `approved_by: proxy_model` を扱う。
- proxy approval では `proxy_decisions` に finding ごとの decision file を要求する。
- decision file には `approved_by: proxy_model`、`proxy_model_id`、`decision_prompt_path`、`source_raw_paths`、`candidate_options`、`selected_option`、`final_label`、`rationale`、`rejected_options`、`raw_response_path` を要求する。
- `raw_response_path` の実体が存在しなければ fail-closed にする。
- `decision_prompt_path` と `source_raw_paths` の実体が存在しなければ fail-closed にする。
- `candidate_options` が空または欠落していれば fail-closed にする。
- `approved_final_labels` と decision file の `final_label` が一致しなければ fail-closed にする。

## 今回はまだ実装しない事項

- 別スレッド作成や分離 worktree 作成の自動化。
- サブ担当への依頼テンプレート生成。
- サブ担当差分の許可ファイル外変更検査。
- triage / proxy decision / diff / test result の統合照合コマンド。

これらは、proxy approval gate が安定した後に段階的に追加する。

## 追加対応：自律・並列モード実行前ガード

自律・並列モードは、実装を始める前に実行計画 YAML を作り、`tools/check-workflow-action.py autonomous-plan <plan.yaml>` で機械検査する。

このガードは、次の事項を fail-closed で検査する。

1. 実行計画が `mode: autonomous_parallel` と `run_id` を持つ。
2. 人間または `proxy_model` の承認記録があり、レビュー結果サマリと三段階トリアージが利用者へ提示済みである。
3. 各タスクに `source_finding_ids`、担当、許可パス、期待テスト、停止条件がある。
4. 別スレッドまたはサブ担当へ渡すタスクは `separate_worktree` を使う。
5. 依存関係のない並列タスクが同じ `allowed_paths` を更新しない。
6. 統合ゲートとして、メインセッション確認、差分範囲確認、テスト確認、判断根拠確認を要求する。
7. 生成物分類として、実装差分、検証結果、判断根拠、作業ノイズの扱いを明示し、作業ノイズは本線 repo へ取り込まない。
8. `history.ledger_path` を `docs/logs/autonomous-parallel/` 配下に置き、task 割当、判断根拠、統合結果を後から追えるようにする。

重要件の修正は、レビュー結果の三段階トリアージ後に、候補案、推薦案、判断理由を提示し、承認または proxy decision が記録されるまで実装に進めない。自律実行中でも、`important_decision_requires_approval` が停止条件として各タスクに入っていない計画は逸脱とする。

## 追加対応：実装差分型の自律・並列実行ログ

API review-run 型の自律・並列実行は raw response、triage、model-result-summary を証跡にする。一方、実装差分型の自律実行では、API raw/triage が存在しないことがある。この場合は `outputs_policy.implementation_diff: commit_candidate` を明示し、`execution_evidence.completed_tasks`、`execution_evidence.parallelized_operations`、`execution_evidence.human_required_count` を証跡にする。

今回の self-improvement implementation.drafting では、次の形で実装差分型をテストした。

1. T-001：成果物配置の準備
2. T-002：入力モデル
3. T-003：signal_extraction モデル

実装はメインセッション LLM が同一 worktree で直列に行い、並列化は仕様・リポジトリ文脈の読み取り、テスト、workflow gate 確認など、同時実行しても差分衝突しない作業に限定した。`docs/logs/autonomous-parallel/2026-06-04-self-improvement-implementation-drafting-plan.yaml` と同名 ledger に task 割当、完了タスク、並列化した操作、検証結果、統合判断を記録した。

このテストで、既存の `autonomous-plan` ガードが API review-run 型だけを想定し、実装差分型の `commit_candidate` を機械判定できないことが分かった。そのため、`tools/check-workflow-action.py autonomous-plan` を拡張し、`implementation_diff: commit_candidate` の場合は raw/triage 証跡の代わりに実装証跡を検査するようにした。これにより、実装差分型でも `human_required_count: 0`、完了タスク、統合ゲートを機械的に確認できる。

確認済みテスト：

- `python3 -m pytest tests/self-improvement -q`
- `python3 -m unittest tests.tools.test_check_workflow_action -v`
- `python3 tools/check-workflow-action.py autonomous-plan docs/logs/autonomous-parallel/2026-06-04-self-improvement-implementation-drafting-plan.yaml --json`
- `git diff --check`

残る次作業は self-improvement T-004（提案モデル）である。5 種類の proposal、必須 7 フィールド、proposal_id 採番、`proposal.schema.json`、種別ごとの追加要件を TDD で実装する。重要判断や不可逆操作が出た場合だけ停止し、通常の実装・検証は自律的に進める。コミット、プッシュ、spec.json 更新、フェーズ移行は引き続き人間の明示承認を必要とする。

## 追加対応：デプロイ後監査の正本を ledger にする

自律・並列モードでは、`*-plan.yaml` は実行前に「これからどう進めるか」を検査するための artifact である。デプロイ後に必ず提供されるとは限らないため、事後監査の正本にしてはいけない。事後監査の正本は `docs/logs/autonomous-parallel/*.yaml` の ledger とする。

この境界を機械的に守るため、`autonomous-plan` は ledger に `execution_evidence_snapshot` を保存する。snapshot には、plan なしで監査するために必要な `completed_tasks`、`parallelized_operations`、`human_required_count` を含める。既存 ledger に snapshot がある場合、古い plan を再実行しても snapshot を巻き戻さない。

また、`tools/check-workflow-action.py autonomous-ledger-audit <ledger.yaml>` を追加し、plan ファイルなしで次を検査できるようにする。

1. ledger が `mode: autonomous_parallel`、`verdict: OK`、`exit_code: 0` を持つ。
2. `execution_evidence_snapshot.completed_tasks` が空でない。
3. `execution_evidence_snapshot.parallelized_operations` が配列である。
4. `execution_evidence_snapshot.human_required_count` が 0 である。
5. `integration_result.status`、`integration_result.tests`、`integration_result.decision` が存在する。

これにより、実行前検査は plan、デプロイ後監査は ledger という責務分離を明確にし、計画ファイルが消えても履歴確認できる状態を保つ。

## 追加対応：同種問題の横展開

上記修正後に、同じ「デプロイ後に一時 artifact がないと監査できない」問題が他にもないか精査した。結果、過去の workflow-management 自律・並列実行 ledger と review-run 報告 ready 判定に同種の穴があった。

対応内容：

1. `docs/logs/autonomous-parallel/2026-06-04-workflow-management-implementation-review-run.yaml` に `execution_evidence_snapshot` を補完し、`autonomous-ledger-audit` で plan なし監査できる状態にした。
2. `tools/api_providers/review_triage.py assert-review-report-ready` で、`ledger.integration_result` だけでなく `ledger.execution_evidence_snapshot` も要求するようにした。
3. `evaluation/metrics/dogfooding_metrics_extractor.py` が `ledger.execution_evidence_snapshot` から `completed_task_count`、`parallelized_operation_count`、`human_required_count` を抽出するようにした。
4. `.reviewcompass/specs/workflow-management/implementation-drafting.md` に、ledger がデプロイ後監査正本であること、`execution_evidence_snapshot` と `autonomous-ledger-audit` を使うことを追記した。

後続課題：

- `authorization.approval_record_path` が `conversation:` を指す場合、デプロイ後に会話ログが同梱されないと承認内容を再確認できない。急ぎの遮断条件ではないが、次の監査性強化では `authorization_snapshot` を ledger に保存することを検討する。
- self-improvement implementation.triad-review の所見 9 で、`rejected = 却下` の状態語彙は正本化済みだが、却下操作を成立させる入力語句が実装内 `REJECTION_WORDS` に閉じていたことを確認した。利用者判断により後続送りではなく即時対応とし、`approval-operation` 規律に明示的否定発言を追加し、T-006 で「採用しません」のような否定形が承認として誤検出されないことを検査する。

## 追加対応：review-run bundle は先例コピーではなく機能固有生成にする

implementation.triad-review の review-run 準備では、既存の workflow-management review-run をそのままコピー元にしない。workflow-management の実例は、raw response 保存、三段階トリアージ、plan/ledger、review summary、target manifest などの成果物構造が実際に動いた検証済みサンプルとして参照する。一方、レビュー観点、対象ファイル集合、重要所見の判定基準は、対象機能の intent、feature-partitioning、requirements、design、tasks から生成する。

理由は、機能軸そのものが intent から feature-partitioning を経て生成されるためである。開発するアプリが変われば、機能名、責務、隣接機能、受入基準、必要な証跡、テスト観点が変わる。したがって、review-run のひな形は特定機能の内容を持たず、フェーズ処理として不変な骨格だけを持つべきである。

共通骨格に入れる事項：

- `run_id`、対象 feature、phase/stage
- review target bundle と source manifest
- 3 役レビューの raw response 保存
- parsed、model-result-summary、triage、review summary の保存
- 三段階トリアージ
- 重要件は候補案、推薦案、判断理由を示し、承認または proxy decision の証跡ができるまで実装修正に進めないこと
- 自律・並列実行 plan/ledger と、事後監査用の ledger snapshot
- 人間判断、proxy_model 判断、不可逆操作の境界

機能ごとに生成する事項：

- レビュー観点
- 対象ファイル集合
- requirements/design/tasks/spec.json との対応
- 実装ファイルとテストファイルの対応
- 失敗時の影響と重要度
- 並列化できる作業単位
- 実装後に測るメトリクス

self-improvement implementation.triad-review では、workflow-management の guard 中心の観点を持ち込まず、規律と実体の双方向同期、提案権と実体変更権の分離、入力モデル、signal 抽出、提案、検証、承認、rollback、効果測定、機械検査、他機能接合、T-001〜T-011 の traceability を中心に review target bundle を作る。
