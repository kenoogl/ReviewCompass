# レビュー対象：reopen R-0（review-wave-summary-command）workflow-management tasks 変更

## 0. variant 選定理由
- variant：implementation_review_independent_3way（claude-sonnet-4-6／gpt-5.5／gemini-3.1-pro-preview）。Claude Code 操縦時の API 既定。利用者「コミット点まで自律で進める」。

## 1. 位置付け
reopen R-0 の第3過程 tasks フェーズ triad-review。requirements・design は approval 済み。T-012（要約コマンド実装タスク）を新設。実装は本フェーズ確定後に implementation で TDD。

## 2. 変更内容（tasks.md）

### 2.1 新設タスク T-012：review-wave 横断確認の要約コマンド（Req 10）

> - 対応設計節：design §review-wave 要約コマンドモデル §1〜§6。対応要件：Requirement 10 受入 1〜5。
> - 責務：tools/check-workflow-action.py に review-wave-summary サブコマンドを追加。読み取り元（各 feature spec.json の workflow_state・recheck、stages/in-progress/、feature-dependency.yaml の feature_order、review-run の triage.yaml 群〔evidence/review-runs/ 優先・旧 _cross_feature/reviews/ 互換、run_id 単位重複排除〕、carry-forward register）から design §2 の算出定義で集計。出力 Markdown（既定）＋JSON（--json、design §3 安定スキーマ）情報同等。fail-closed（必須記録〔spec.json・feature-dependency.yaml〕欠落/解析不能・任意記録の解析不能で status:insufficient＋非ゼロ終了コード 2、任意記録の非在は 0 件 ok）。読み取り専用、保存は --out/--save で自身の出力のみ。既存関数（load_all_feature_specs・feature_order 解決・collect_recheck_items・review_triage 集計）を再利用。
> - 前提タスク：T-002・T-003・T-004。
> - 成果物：review-wave-summary サブコマンド（必要なら helper モジュール）、テストファイル。
> - 完了条件：design §1〜§6 を満たす、情報同等、安定スキーマ、fail-closed、読み取り専用、TDD 赤→緑→全テスト通過。
> - テスト要件（TDD、先に失敗テスト）：(1) 各指標集計、(2) JSON スキーマ・status 判定、(3) Markdown/JSON 情報同等、(4) fail-closed（必須欠落で exit2／任意 glob ゼロ件で ok）、(5) 読み取り専用（実行後 spec.json・triage 不変）、(6) draft は run 単位・unresolved/human_required は item 単位。

### 2.2 要件追跡表に Req 10 受入 1〜5 → T-012 の 5 行追加。タスク件数 11→12 に更新。

## 3. レビュー観点（criteria: tasks_r10_review_wave_summary_command）
1. T-012 が design §1〜§6 を漏れなくタスク化し、前提タスク（T-002/003/004）が妥当か。
2. テスト要件が TDD（先に失敗テスト）で、design の各契約（スキーマ・fail-closed・読み取り専用・集計軸）を検証可能か。
3. 完了条件が design と一致し、検証可能か。
4. 既存タスク（特に T-004 検査スクリプト本体）との責務重複・矛盾がないか。
5. 要件追跡の双方向整合（Req 10 受入 1〜5 ↔ T-012）。
