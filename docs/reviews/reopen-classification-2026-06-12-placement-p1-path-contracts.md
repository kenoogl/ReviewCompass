---
date: 2026-06-12
classifier: claude_main_session
classification: R-0（conformance-evaluation）／D-0（workflow-management）
trigger_source: 配置規約の利用者決定 PLC-DEC-003〜005・009〜010（2026-06-12。決定台帳 docs/notes/2026-06-12-document-placement-stage2-decisions.md・移行計画 docs/notes/2026-06-12-document-placement-stage4-migration.md の P1 作業 #4）。証跡・実行時生成物の置き場を evidence／runtime 区画へ移すにあたり、旧パスを契約として明記する正本仕様を先に改めるため。
feature: conformance-evaluation・workflow-management（2 feature を同一根拠で個別に reopen する）
finding: placement-p1-path-contracts
---

## 分類根拠

配置規約（PLC-DEC-001〜012）の P1（新規分の新配置）は、次の 5 つのパス契約を変更する。いずれも承認済み仕様の本文が旧パスを契約として明記しており、実装先行ではなく仕様を先に確定する正順の手続き（先例：reopen-procedure-2026-06-12-parse-error-failclosed）とする。

| パス契約 | 現行（仕様本文の明記箇所） | 変更後 |
| --- | --- | --- |
| conformance 評価記録の配置先 | `<対象アプリ>/.reviewcompass/specs/<feature>/conformance/`（ce requirements 受入複数・design 配置図・tasks T-001 ほか） | `.reviewcompass/evidence/features/<feature>/conformance/` |
| 推定独立性ログの格納先 | `logs/estimation/<run_id>/prompt.log`（ce tasks MV-6 の命名規則例示） | `.reviewcompass/evidence/estimation/<run_id>/prompt.log` |
| effective prompt の保存先 | `.reviewcompass/effective-prompts/`（wm design・tasks T-004） | `.reviewcompass/runtime/effective-prompts/` |
| commit 承認記録の置き場 | `.reviewcompass/approvals/commit-approval.json`（wm design） | `.reviewcompass/runtime/approvals/commit-approval.json` |
| 検査ログの書き出し先 | `docs/logs/workflow-precheck.log`（wm design・tasks T-004 ほか） | `.reviewcompass/runtime/logs/workflow-precheck.log` |

手戻り種別：

- **conformance-evaluation：R-0**（requirements 起点、intent へは遡らない）。記録配置の契約は requirements の受入条件（評価記録・draft 草案・handoff の配置先）に明記されており、これが修正の最上流。intent・feature-partitioning は不変（記録の置き場の変更であり、機能の意図・分割・評価ロジックに影響しない）
- **workflow-management：D-0**（design 起点、requirements へは遡らない）。同 feature の requirements は 3 パスのいずれにも言及せず（grep で確認）、契約の明記は design（配置図・approvals・ログ）と tasks（T-004）が最上流

いずれも実装変更（ツールの書き込み先変更＋旧パス読み取り互換）を含むため、implementation の review 系 gate も再実施対象とする。MV-3 の「`conformance/` と `reviews/` のディレクトリ分離」契約は、`evidence/features/<feature>/` 配下でも同名サブディレクトリで維持され、意味は不変。

## 事実

- 現実装：`evaluation_record.py`・`post_hoc_intent_diff.py` は `.reviewcompass/specs/conformance-evaluation/conformance/` へ、`machine_verification.py` はルート `logs/estimation/` へ、`check-workflow-action.py` は `.reviewcompass/effective-prompts/`・`.reviewcompass/approvals/commit-approval.json`・`docs/logs/workflow-precheck.log` へ書く（棚卸し記録 §5）
- 変更後の挙動（仕様化する内容）：新規生成分から evidence／runtime 区画へ書く。旧パスは読み取り互換（二重読み）を P3 まで維持（PLC-DEC-011）。既存ファイルは移動しない（PLC-DEC-009）
- 検証対象判定（post-write target detection）は変更しない（設計記録 §4。新区画は `.reviewcompass/` 配下のため現行判定で対象外、fail-closed 維持）

## feature impact 判定

| feature | decision | impact_basis | rationale |
| --- | --- | --- | --- |
| conformance-evaluation | reopen_existing_feature | contract_ownership | 評価記録・推定ログの配置契約（requirements 受入・design 配置図・tasks T-001／MV-6）と該当ツール実装を所有するため。 |
| workflow-management | reopen_existing_feature | contract_ownership | effective prompt・commit 承認記録・検査ログのパス契約（design・tasks T-004）と検査ツール実装を所有するため。 |
| foundation | no_reopen_existing_feature | no_implementation_impact | 共通語彙・状態入力に変更なし。 |
| runtime | no_reopen_existing_feature | no_implementation_impact | review-run の置き場はツールの CLI 引数渡しで、仕様は特定パスを契約しない。接合面不変。 |
| evaluation | no_reopen_existing_feature | no_implementation_impact | 同上（run ディレクトリは引数渡し）。variant・トリアージ契約に変更なし。 |
| analysis | no_reopen_existing_feature | consumer_or_derivative_only | 記録の読み手であり、読み取りは新旧両置き場を対象にできる。 |
| self-improvement | no_reopen_existing_feature | consumer_or_derivative_only | 学習資産の置き場（learning/）は当面不変（PLC-DEC-008 の当面形）。 |

新 feature 判定：`no_new_feature`。

## 再実施対象

- **conformance-evaluation（R-0）**：正本修正のある requirements・design・tasks の各 `stages/<phase>.yaml#triad-review`〜`#approval`、および実装変更を行う implementation の同 gate（TDD：失敗テスト→実装→全テスト通過）
- **workflow-management（D-0）**：正本修正のある design・tasks の各 `stages/<phase>.yaml#triad-review`〜`#approval`、および同じく implementation の同 gate

impacted_downstream_phases：conformance-evaluation＝design／tasks／implementation、workflow-management＝tasks／implementation。

## 停止点

reopen-start により feature ごとの in-progress ファイルを発行し、spec.json のフラグ差し戻し（conformance-evaluation：requirements／design／tasks／implementation、workflow-management：design／tasks／implementation の各 alignment・approval を false、recheck 設定）を行ったうえで、第 1 過程停止点として差し戻し内容の利用者承認を待つ。この時点ではコミットしない。
