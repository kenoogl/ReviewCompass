# 書き込み後検証対象：reopen 分類記録（review-wave 要約コマンド、R-0）

検証者へ渡すのは合意内容（決定）と書き込み結果のみ。

## 合意内容（決定）

- 候補 2（review-wave 要約コマンドの実装）の reopen 分類を **R-0**（requirements 起点。intent・feature-partitioning へは遡らない）と確定した（2026-06-14、利用者決定「R-0でよい」）。
- 意図文書は改めず、既存の「段集合 YAML による静的検査」（workflow-management Requirement 1）の範囲に含める。
- 2026-06-13 記録の分類ラベル R-1 と、その併記説明文「requirements に追加し design→tasks→implementation へ連鎖」（種別定義上は R-0 の範囲）の食い違いを 2026-06-14 に利用者と確認のうえ、R-0 を採用して 2026-06-13 の記録を更新した。
- 要件正本は D-001（`docs/notes/2026-06-04-implementation-review-wave-improvements.md`・`docs/notes/2026-06-05-future-development-candidates.md`）。
- 再実施対象：requirements の triad-review〜approval（正本本文を修正するため）と、下流 design／tasks／implementation。
- feature impact：workflow-management のみ reopen_existing_feature（contract_ownership）。他 6 機能（foundation／runtime／evaluation／analysis／self-improvement／conformance-evaluation）は no_reopen_existing_feature（no_implementation_impact）。新 feature なし（no_new_feature）。

## 書き込み結果（docs/reviews/reopen-classification-2026-06-14-wm-review-wave-summary-command.md）

front-matter：date 2026-06-14、classifier claude_main_session、classification「R-0（workflow-management）」、feature workflow-management、finding review-wave-summary-command。trigger_source に、reopen 方針は 2026-06-12 利用者決定・分類は 2026-06-13 に R-1 記録（コミット fd5d1358）・2026-06-14 に R-1 ラベルと説明文の食い違いを確認のうえ R-0 採用（「R-0でよい」）と明記。

本文の主な記述：

- 分類根拠：D-001 は review-wave 横断確認指標（feature coverage・phase/stage 状態・triage 未解決/draft/human_required 件数・recheck 状態・依存状況・carry-forward 件数）を手動集計から機械生成へ移す新要件。手戻り種別は R-0（requirements 起点、intent・feature-partitioning へ遡らない）。
- intent：workflow-management の意図（INTENT.md 11.5「段集合 YAML による静的検査…」）の範囲内で、意図改訂は不要。
- feature-partitioning：1 回分のワークフロー状態の静的検査であり analysis（複数実行をまたぐ二次分析）とは別。workflow-management に属し再分割不要。
- R-1 からの変更理由：R-1 の trigger_map は intent・feature-partitioning へ遡るが、併記説明文は requirements 起点で下流連鎖＝R-0 範囲。ラベルと説明が食い違っていたため、2026-06-14 に利用者と確認して R-0 を採用。
- 事実：要件正本 D-001、検討実装（`tools/check-workflow-action.py` への review-wave-summary 相当サブコマンド追加、Markdown＋JSON 出力、`.reviewcompass/specs/_cross_feature/reviews/` 保存可）、出力項目一覧。
- feature impact 判定表：workflow-management＝reopen_existing_feature（contract_ownership）、他 6 機能＝no_reopen_existing_feature（no_implementation_impact）。新 feature 判定＝no_new_feature。
- 再実施対象：workflow-management（R-0）＝requirements の triad-review〜approval（新要件の起草を含む）と implementation の同 gate（TDD）。impacted_downstream_phases＝design／tasks／implementation。
- 停止点：reopen-start で in-progress ファイルを発行し、spec.json のフラグ差し戻し（requirements の alignment・approval を false、recheck＝upstream_change_pending true・impacted_downstream_phases に design／tasks／implementation）を行ったうえで第 1 過程停止点として利用者承認を待つ。コミットしない。
