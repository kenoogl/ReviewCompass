# 書き込み後検証対象：reopen 分類記録（裁定負荷対策 lint、R-0）

検証者へ渡すのは合意内容（決定）と書き込み結果のみ。

## 合意内容（決定）

- 裁定負荷対策 lint（TODO §4 候補 5）の reopen 分類を **R-0**（requirements 起点。intent・feature-partitioning へは遡らない）と確定した（2026-06-15、利用者決定「提案の方針でOK」。提案時に R-0／所有 workflow-management／新 Requirement 11 を提示し承認）。
- 所有 feature は **workflow-management**。意図文書は改めず、既存の「段集合 YAML による静的検査・修復手続きの機械強制」（intent/INTENT.md §11.5）の範囲に含める。
- 新設するもの：(あ) 構造化した重要決定の記録形式（決定 ID・決定文言・出典〔引用＋セッション ID＋個別か束ねか〕）、(い) その記録を入力に 3 検査を行う lint。検査＝(i) 束ね検出（複数の重要決定が同一出典を共有していたら確定扱いにさせない）、(ii) 逐語照合（出典の引用が層 1 転写＝`.reviewcompass/evidence/sessions/` に逐語で存在するか機械照合）、(iii) 内容性（「OK」「承認」等の中身なし返事だけを唯一の出典として不可）。重要種別＝不可逆操作・規律変更・仕様/計画変更に限定。
- 検査方針の確定は 2026-06-14 利用者決定。going-forward の新規重要決定から適用し、過去の散文台帳は遡及移行しない。
- ルールは既存（discipline_approval_operation＝確定記述に出典必須・出典なし禁止・機械検査は承認の代替でない、discipline_plain_explanation_each_step＝重要承認は 1 件ずつ）の機械強制であり、新規ルールの追加ではない。PLC-DEC-007 の誤記録がその違反の動機事例。
- 再実施対象：requirements の alignment〜approval（新要件の起草を含む）と、下流 design／tasks／implementation。
- feature impact：workflow-management のみ reopen_existing_feature（contract_ownership）。他 6 機能（foundation／runtime／evaluation／analysis／self-improvement／conformance-evaluation）は no_reopen_existing_feature（no_implementation_impact）。新 feature なし（no_new_feature）。

## 書き込み結果（docs/reviews/reopen-classification-2026-06-15-wm-decision-source-lint.md）

front-matter：date 2026-06-15、classifier claude_main_session、classification「R-0（workflow-management）」、feature workflow-management、finding decision-source-lint。trigger_source に、TODO §4 候補 5、動機事例 PLC-DEC-007 の誤記録、方針は 2026-06-13 利用者決定「(b) で対応」、検査方針の確定は 2026-06-14 利用者決定（束ね検出・逐語照合・内容性、重要種別限定）、本 reopen 起動は 2026-06-15 利用者決定「提案の方針でOK」と明記。

本文の主な記述：

- 分類根拠：重要決定の出典・束ね・逐語一致を機械検査する lint と、構造化した重要決定の記録形式を新設。手戻り種別は R-0（requirements 起点、intent・feature-partitioning へ遡らない）。
- intent：workflow-management の意図（intent/INTENT.md §11.5「段集合 YAML による静的検査…修復手続きの機械強制」）の範囲内で、(a) 新しい検査対象への静的検査かつ (b) 既存規律の機械強制であり、意図改訂は不要。
- feature-partitioning：1 件の決定記録に対する静的検査と既存規律の機械強制であり、analysis（複数実行をまたぐ二次分析）とは別。workflow-management に属し再分割不要。
- R-0 と R-1 の分岐点：分岐点は「重要決定の記録形式という新しい成果物を意図に明記するか」。意図には明記せず既存の静的検査・機械強制に含む判断で R-0 採用（2026-06-15 利用者決定）。
- 事実：動機事例の正本（PLC-DEC-007 訂正欄）、既存ルール 2 件、確定した 3 検査の内容、検討する実装（記録形式の新設、`tools/check_workflow_action/` 配下の既存 lint〔document_link_lint・deployment_independence_lint・placement_freeze〕に倣う lint、`tools/check-workflow-action.py` のサブコマンドおよび／または commit 直前ゲートへ接続、出力は fail-closed）。スキーマ・接続点・過去台帳の扱いは requirements／design で確定。
- feature impact 判定表：workflow-management＝reopen_existing_feature（contract_ownership）、他 6 機能＝no_reopen_existing_feature（no_implementation_impact）。新 feature 判定＝no_new_feature。
- 再実施対象：workflow-management（R-0）＝requirements の alignment〜approval（新要件の起草を含む）と implementation の同 gate（TDD）。impacted_downstream_phases＝design／tasks／implementation。
- 停止点：reopen-start で in-progress ファイルを発行し、spec.json のフラグ差し戻し（requirements の alignment・approval を false、recheck＝upstream_change_pending true・impacted_downstream_phases に design／tasks／implementation）を行ったうえで第 1 過程停止点として利用者承認を待つ。コミットしない。
