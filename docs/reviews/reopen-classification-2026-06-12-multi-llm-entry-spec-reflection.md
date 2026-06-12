---
date: 2026-06-12
classifier: claude_main_session
classification: R-0
trigger_source: 2026-06-12 の conformance 評価（gap_found）。アドホック開発「配布側複数 LLM 入口整備」（実装計画ステップ 1〜5 ＋ 論点 5）の実装由来契約を、workflow-management 等の仕様正本へ反映するため。利用者は 2026-06-12 に語彙調停の案 A（MLE-DEC-001）と reopen 起動を承認した。
feature: workflow-management
finding: multi-llm-entry-adhoc-spec-gap
---

## 分類根拠

conformance 評価記録
`.reviewcompass/specs/conformance-evaluation/conformance/2026-06-12-completed-followup-conformance.md`
は、completed 到達後にアドホック開発された実装契約（MLE-C-001〜008）が仕様正本に未反映である
gap（MLE-GAP-001〜006）を確定した。本 reopen はこの gap のうち、利用者決定済みの範囲
（MLE-HANDOFF-001〜003・005〜007）を正本へ反映する。

手戻り種別は `R-0`（requirements 起点、intent へは遡らない）とする。根拠：

- 修正の最上流フェーズは requirements である（workflow-management Requirement 8 への
  feature 一覧解決契約の追記、Requirement 1 受入 4・Requirement 8 受入 3 の語彙修正）。
- intent は意味変更なし。自己適用型レビュー基盤という意図、および複数 LLM 対応の方向は
  既存 intent と設計記録（docs/notes/2026-06-10-deployment-multi-llm-entry-design.md、
  利用者個別承認済み）の範囲内である。
- feature-partitioning は対象外。機能の境界・依存・順序の**意味**は不変であり、変わるのは
  順序表の保管キー名（`feature_order`）と解決場所（探索順）だけである
  （stages/feature-partitioning/2026-05-24-proposal.md の 7 機能・依存・並び順はそのまま）。

語彙調停は利用者決定済み：案 A（仕様側を実装語彙 `feature_order` へ寄せる。
MLE-DEC-001、2026-06-12、reopen handoff package に記録）。

## 事実

- 実装・テスト・配布物は先行して完成済み（コミット 702c00c〜3730571、TDD・回帰・post-write
  検証・模擬対象アプリ実証の証跡あり）。本 reopen は仕様を実装へ追認させる方向であり、
  実装コードの変更を含まない。
- ツール一般化は maintenance side track
  （stages/completed/maintenance-2026-06-11-feature-order-generalization.yaml）で実施され、
  同記録の out_of_scope_note が本件の仕様反映を別義務として明示している。
- 反映内容の草案は draft-only で作成済み
  （.reviewcompass/specs/conformance-evaluation/conformance/2026-06-12-spec-update-drafts/）。
- evaluation 仕様への操縦 LLM 別 variant 既定の昇格（MLE-GAP-005／MLE-HANDOFF-004）は
  利用者判断待ちのため、本 reopen に含めない。

## feature impact 判定

| feature | decision | impact_basis | rationale |
| --- | --- | --- | --- |
| workflow-management | reopen_existing_feature | contract_ownership | feature 一覧解決・next 判定種別・配布テンプレート契約の正本（requirements・design・tasks）を所有し、直接修正するため。 |
| conformance-evaluation | reopen_existing_feature | contract_ownership | 自仕様（Requirement 7 受入 5、design §13.5、tasks T-010 ほか）の `phase_order` 表記が、MLE-DEC-001 の語彙確定により意味不変の文言追従を要するため。 |
| evaluation | no_reopen_existing_feature | no_implementation_impact | 本 reopen の変更（語彙・探索順・判定種別・テンプレート契約）は evaluation の契約を変えない。MLE-HANDOFF-004（variant 既定の仕様昇格）は利用者判断待ちで、判断後に必要なら別手続きとする。 |
| foundation | no_reopen_existing_feature | no_implementation_impact | next_action の kind 語彙は foundation が所有する共有語彙（重大度・レビューモード・証拠区分等）に含まれず、workflow-management T-004 の契約である。 |
| runtime | no_reopen_existing_feature | no_implementation_impact | 入口テンプレートは配布物の場所を記入欄方式で扱い、runtime 承認済みの config.yaml 必須 5 項目契約に触れない（設計記録 §3.1 で再オープン回避を確認済み）。 |
| analysis | no_reopen_existing_feature | consumer_or_derivative_only | conformance 出力の読み手であり、6 criteria の接合面は不変のため。 |
| self-improvement | no_reopen_existing_feature | consumer_or_derivative_only | 規律改善の入力として読む側であり、接合面は不変。WP-001 は提案のまま仕様化しない。 |

新 feature 判定：`no_new_feature`（すべて既存 feature の責務境界で受けられる）。

## 再実施対象

`R-0` の trigger_map は `stages/requirements.yaml#alignment` と `stages/requirements.yaml#approval`
を返す。これを基線とし、REOPEN_PROCEDURE.md §3「正本本文を修正した phase は、その phase の
triad-review／review-wave／alignment／approval を再実施対象に加える」に従い、正本修正のある
requirements・design・tasks の全 review 系 gate を加える。implementation は正本修正なし
（実装先行のため確認のみ）とし、alignment／approval の再確認を対象にする。

- `stages/requirements.yaml#triad-review`〜`#approval`（正本修正：workflow-management、conformance-evaluation）
- `stages/design.yaml#triad-review`〜`#approval`（同上）
- `stages/tasks.yaml#triad-review`〜`#approval`（同上）
- `stages/implementation.yaml#alignment`／`#approval`（確認のみ、修正なし見込み）

impacted_downstream_phases：design／tasks／implementation。

## 停止点

reopen-start により in-progress ファイルを発行し、spec.json のフラグ差し戻し
（workflow-management・conformance-evaluation の requirements／design／tasks の
alignment・approval を false、recheck.upstream_change_pending=true）を行ったうえで、
第1過程停止点として差し戻し内容の利用者承認を待つ。この時点ではコミットしない。
