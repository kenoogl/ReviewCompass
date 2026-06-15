---
date: 2026-06-15
classifier: claude_main_session
classification: R-0（workflow-management）
trigger_source: TODO_NEXT_SESSION.md §4 候補 5（裁定負荷対策＝利用者決定の埋没防止）。動機事例＝PLC-DEC-007 の誤記録（6 論点の一括確認表＋包括「OK」により、利用者発言と食い違う決定文言が裁定されないまま台帳化）。方針は 2026-06-13 利用者決定「(b) で対応」、検査方針の確定は 2026-06-14 利用者決定（束ね検出・逐語照合・内容性の 3 検査、重要種別＝不可逆操作・規律変更・仕様/計画変更に限定）。本 reopen の起動は 2026-06-15 利用者決定「提案の方針でOK」。
feature: workflow-management
finding: decision-source-lint
---

## 分類根拠

重要決定（不可逆操作・規律変更・仕様/計画変更に限定）の確定記述について、出典の有無・束ね・逐語一致を機械検査する lint を新設する。あわせて、確実な機械検査を可能にする「構造化した重要決定の記録形式」（決定 ID・決定文言・出典〔引用＋セッション ID＋個別か束ねか〕）を新設する。going-forward の新規重要決定から適用し、過去の散文台帳は遡及移行しない。

手戻り種別：**R-0（requirements 起点。intent・feature-partitioning へは遡らない）**。

- intent（意図）：workflow-management の意図（`intent/INTENT.md` §11.5）は「軽量化方針に基づき、段集合 YAML による静的検査、所定手続きの階層構造、修復手続きの機械強制を担う」。本 lint は (a) 重要決定記録という新しい検査対象に対する静的検査であり、(b) 既存規律 `discipline_approval_operation`（確定記述に出典必須・出典なし禁止・「OK」等の中身なし返事を承認の代替にしない）と `discipline_plain_explanation_each_step`（重要承認は 1 件ずつ）の機械強制である。いずれも既存意図の範囲内であり、新しい意図を導入しない。意図文書の改訂は不要。
- feature-partitioning（機能分割）：本 lint と記録形式は、1 件の決定記録に対する静的検査と既存規律の機械強制であり、workflow-management の責務（段集合 YAML による静的検査・修復手続きの機械強制）で受けられる。analysis（複数実行をまたぐ二次分析・可視化・報告）とは別物。workflow-management に属することは明確で、再分割は不要。

### R-0 と R-1 の分岐点（利用者確認済み）

前例 Requirement 10（review-wave 要約コマンド）でも、R-0 か R-1 かの分岐点は「新しい成果物を意図文書に明記すべきか」であった。本件の分岐点は「重要決定の記録形式という新しい成果物を意図に明記するか」である。意図には明記せず、既存「静的検査・修復手続きの機械強制」に含むという判断で **R-0** を採用する（2026-06-15 利用者決定「提案の方針でOK」。提案時に R-0／workflow-management／新 Requirement 11 を提示し、特に R-0 でよいかを確認のうえ承認を得た）。

## 事実

- 動機事例の正本：PLC-DEC-007 の誤記録（訂正記録は `docs/notes/2026-06-12-document-placement-stage2-decisions.md` の PLC-DEC-007 2026-06-13 訂正欄）。失敗の核心＝一括承認の中に重要な件が埋もれ、他が問題なく見えて「OK」と返したため、重要件が正しく裁定されないまま確定した（裁定負荷）。
- ルールは既存：`docs/disciplines/discipline_approval_operation.md`（確定記述に出典必須・出典なし禁止・機械検査は承認の代替でない）、`docs/disciplines/discipline_plain_explanation_each_step.md`（重要承認は 1 件ずつ・承認前に平易説明）。PLC-DEC-007 はその違反であり、新規ルールの追加ではなく既存ルールの機械強制で対処する。
- 確定した検査方針（2026-06-14 利用者決定。重要種別＝不可逆操作・規律変更・仕様/計画変更に限定）：
  - (i) 束ね検出＝複数の重要決定が同一出典（同じ一回の「OK」）を共有していたら確定扱いにさせない。
  - (ii) 逐語照合＝出典の引用が会話転写（repo 取り込み済みの層 1＝`.reviewcompass/evidence/sessions/`）に逐語で存在するか機械照合する（でっち上げ・言い換えを弾く）。
  - (iii) 内容性＝「OK」「承認」等の中身なし返事だけを重要決定の唯一の出典として不可。
  - 文言が意図を汲むかの意味一致は機械では「検証可能化」までで、最終は人/判定役（転写と突き合わせ）。
- 検討する実装：(あ) 構造化した重要決定の記録形式（決定 ID・決定文言・出典〔引用＋セッション ID＋個別/束ね〕）の新設、(い) その記録を入力に 3 検査を行う lint（`tools/check_workflow_action/` 配下の既存 lint〔`document_link_lint.py`・`deployment_independence_lint.py`・`placement_freeze.py`〕に倣う）を新設し、`tools/check-workflow-action.py` のサブコマンドおよび／または commit 直前ゲートへ接続する。出力は fail-closed（重要決定が出典検査に通らなければ非ゼロ終了）。
- 出力・接続点の詳細（記録形式のスキーマ、lint のサブコマンド名、commit 直前ゲートへの組み込み可否）は requirements／design で確定する。過去の散文台帳を遡及移行しない方針は確定済み（上記「分類根拠」のとおり）であり、未決事項ではない。

## feature impact 判定

| feature | decision | impact_basis | rationale |
| --- | --- | --- | --- |
| workflow-management | reopen_existing_feature | contract_ownership | 段集合 YAML による静的検査・修復手続きの機械強制・不可逆操作の直前ゲート（Requirement 4）を所有。新要件（重要決定の出典検査 lint と記録形式）の要件・設計・実装を所有するため。 |
| foundation | no_reopen_existing_feature | no_implementation_impact | 共通契約・スキーマに変更なし。 |
| runtime | no_reopen_existing_feature | no_implementation_impact | 実行契約に変更なし。 |
| evaluation | no_reopen_existing_feature | no_implementation_impact | 評価契約に変更なし。 |
| analysis | no_reopen_existing_feature | no_implementation_impact | 横断分析は複数実行の二次分析であり、1 件の決定記録に対する静的検査である本 lint とは別。 |
| self-improvement | no_reopen_existing_feature | no_implementation_impact | self-improvement は規律の提案権を持つが、決定記録の出典・束ね・逐語照合の機械強制は workflow-management の責務。規律本文や同期範囲に変更なし。 |
| conformance-evaluation | no_reopen_existing_feature | no_implementation_impact | 実装推定・照合に変更なし。 |

新 feature 判定：no_new_feature（workflow-management の責務境界で受けられるため）。

## 再実施対象

- **workflow-management（R-0）**：正本修正のある requirements の `stages/requirements.yaml#alignment`〜`#approval`（新要件の起草を含む）、および実装変更を行う implementation の同 gate（TDD：失敗テスト → 実装 → 全テスト通過）。
- impacted_downstream_phases：design／tasks／implementation。

## 停止点

reopen-start により in-progress ファイルを発行し、spec.json のフラグ差し戻し（workflow-management：requirements の alignment・approval を false、recheck＝upstream_change_pending を true・impacted_downstream_phases に design／tasks／implementation を設定）を行ったうえで、第 1 過程停止点として差し戻し内容の利用者承認を待つ。この時点ではコミットしない。
