---
date: 2026-06-14
classifier: claude_main_session
classification: R-0（workflow-management）
trigger_source: TODO_NEXT_SESSION.md §4 候補 2（review-wave 要約コマンドの実装）。reopen 方針は 2026-06-12 利用者決定、分類は 2026-06-13 に R-1 として記録（コミット fd5d1358・書き込み後検証 post-write-2026-06-13-012）。2026-06-14 セッションで分類ラベル R-1 と併記説明文（「requirements に追加し design→tasks→implementation へ連鎖」＝種別定義上 R-0 の範囲）の食い違いを利用者と確認し、意図文書を書き換えない（既存「静的検査」に含む）方針で R-0 を採用（利用者決定「R-0でよい」）。
feature: workflow-management
finding: review-wave-summary-command
---

## 分類根拠

D-001（review-wave summary command）は、review-wave の横断確認で用いた指標（feature coverage・phase/stage 状態・triage 未解決/draft/human_required 件数・recheck 状態・依存状況・carry-forward 件数）を手動集計から機械生成へ移すための新要件である。

手戻り種別：**R-0（requirements 起点。intent・feature-partitioning へは遡らない）**。

- intent（意図）：workflow-management の意図（`intent/INTENT.md` 11.5）は「軽量化方針に基づき、段集合 YAML による静的検査、所定手続きの階層構造、修復手続きの機械強制を担う」。要約コマンドはワークフロー状態の静的検査の具体例であり、既存意図の範囲内。意図文書の改訂は不要。
- feature-partitioning（機能分割）：本コマンドは 1 回分のワークフロー状態の静的検査であり、analysis（複数実行をまたぐ二次分析・可視化・報告）とは別物。workflow-management に属することは明確で、再分割は不要。

### R-1（2026-06-13 記録）からの変更理由

2026-06-13 の記録（`TODO_NEXT_SESSION.md`・コミット fd5d1358・書き込み後検証対象 `target.md`）は分類を R-1 とし、併記説明として「新要件として workflow-management の requirements に追加し design → tasks → implementation へ連鎖」と書いていた。しかし種別定義（`docs/plan/reconstruction-plan-2026-05-21.md` の trigger_map）では R-1 は intent#review・intent#approval・feature-partitioning#candidate-proposal・feature-partitioning#approval にも遡る種別であり、この説明文（requirements 起点で下流へ連鎖）は R-0 の範囲に一致する。ラベル R-1 と説明文の範囲が食い違っていた。

2026-06-14 セッションで本食い違いを利用者と確認し、「意図文書に要約・指標生成を明記すべきか」が分岐点であることを整理したうえで、意図には明記せず既存「静的検査」に含むという判断で R-0 を採用した（利用者決定「R-0でよい」）。本記録が以後の分類の正本であり、2026-06-13 の R-1 記録を更新する。

## 事実

- 要件正本：D-001（`docs/notes/2026-06-04-implementation-review-wave-improvements.md`・`docs/notes/2026-06-05-future-development-candidates.md`）。
- 検討する実装：`tools/check-workflow-action.py` または別 helper に `review-wave-summary` 相当のサブコマンドを追加。出力は Markdown と JSON の両方。`.reviewcompass/specs/_cross_feature/reviews/` に保存できる形式を用意する。
- 出力項目：feature coverage、phase/stage 状態、triage unresolved/draft/human_required count、recheck state、dependency status、carry-forward unresolved count。

## feature impact 判定

| feature | decision | impact_basis | rationale |
| --- | --- | --- | --- |
| workflow-management | reopen_existing_feature | contract_ownership | review-wave gate とワークフロー状態の静的検査を所有。新要件 D-001 の要件・設計・実装を所有するため。 |
| foundation | no_reopen_existing_feature | no_implementation_impact | 共通契約・スキーマに変更なし。 |
| runtime | no_reopen_existing_feature | no_implementation_impact | 実行契約に変更なし。 |
| evaluation | no_reopen_existing_feature | no_implementation_impact | 評価契約に変更なし。 |
| analysis | no_reopen_existing_feature | no_implementation_impact | 横断分析は複数実行の二次分析であり、1 回分の静的検査である本コマンドとは別。 |
| self-improvement | no_reopen_existing_feature | no_implementation_impact | 自己改善の範囲に変更なし。 |
| conformance-evaluation | no_reopen_existing_feature | no_implementation_impact | 実装推定・照合に変更なし。 |

新 feature 判定：no_new_feature。

## 再実施対象

- **workflow-management（R-0）**：正本修正のある requirements の `stages/requirements.yaml#triad-review`〜`#approval`（新要件の起草を含む）、および実装変更を行う implementation の同 gate（TDD：失敗テスト → 実装 → 全テスト通過）。
- impacted_downstream_phases：design／tasks／implementation。

## 停止点

reopen-start により in-progress ファイルを発行し、spec.json のフラグ差し戻し（workflow-management：requirements の alignment・approval を false、recheck＝upstream_change_pending を true・impacted_downstream_phases に design／tasks／implementation を設定）を行ったうえで、第 1 過程停止点として差し戻し内容の利用者承認を待つ。この時点ではコミットしない。
