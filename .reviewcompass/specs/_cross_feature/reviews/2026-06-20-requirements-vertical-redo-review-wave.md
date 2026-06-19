---
date: 2026-06-20
gate: stages/requirements.yaml#review-wave
feature: all_features
phase: requirements
stage: review-wave
reopen: R-0（requirement-13-16-vertical-redo）
decision: existing_sufficient
carry_forward_unresolved: 0
summary_evidence: .reviewcompass/specs/_cross_feature/reviews/2026-06-20-requirements-vertical-redo-review-wave-summary.md
---

# requirements review-wave：Requirement 13〜16 縦方向やり直し

## 対象

reopen R-0（`docs/reviews/reopen-classification-2026-06-19-wm-requirement-13-16-vertical-redo.md`）の第3過程、workflow-management requirements フェーズの review-wave（機能横断レビュー段）。

今回の requirements 変更は、Requirement 13〜16 の縦方向意図監査をやり直し、triad-review で API 版 `gpt-5.5` proxy_model が `should-fix` と判定した次の補強を反映したものである。

- Requirement 13 受入 5：人間判断記録は承認ゲート全体の一部であり、`record_human_decision` 完了だけを承認成立として扱わないことを明記
- Requirement 13 受入 9：複合操作の schema 表現を design で選ぶ場合でも、受入 8 の最小制約を失わせないことを明記
- Requirement 14 受入 11：proxy_model 適用可否と human-required predicate 優先順位を Requirement 16 受入 13〜14 と整合させることを明記

あわせて、縦方向監査 prompt の規律として、source materials をパス名だけで列挙せず、上流本文または構造化要約を prompt に含めることを運用規律と機械 preflight に追加した。

## 機械サマリ

`tools/check-workflow-action.py review-wave-summary --out .reviewcompass/specs/_cross_feature/reviews/2026-06-20-requirements-vertical-redo-review-wave-summary.md` を実行した。

- status: ok
- carry-forward 未消化: 0
- feature_order: foundation, runtime, evaluation, analysis, workflow-management, self-improvement, conformance-evaluation
- workflow-management: recheck pending（design, tasks, implementation）
- 未充足依存: self-improvement←workflow-management, conformance-evaluation←workflow-management

未充足依存は、現在の workflow-management reopen が完了していないために発生している一時状態である。本 review-wave では、他 feature の requirements 正本を再オープンする必要は確認されなかった。

## 持ち越し所見

正本：`learning/workflow/carry-forward-register/reviewcompass-import.yaml`。

未消化の carry-forward は 0 件であり、本 review-wave で新たに消化すべき横断所見はない。

## 機能横断の影響判定

今回の変更の直接所有者は workflow-management である。operation contract、承認ゲート、構造化有効プロンプト、proxy_model triage decision、review-run / post-write verification / commit approval の開始前検査は workflow-management が所有する所定手続き・操作契約の範囲である。

本 review-wave では、次の切り分けを正本として扱う。

- **reopen scope**：`workflow-management` のみ。requirements 正本を実質変更したため、同 feature の requirements 後段と design / tasks / implementation の対象 gate を再実施する。
- **impact review scope**：全 feature。foundation / runtime / evaluation / analysis / self-improvement / conformance-evaluation は consumer / derivative として確認する。
- **flag 方針**：他 feature については requirements 正本変更を要求しないため、既存 workflow flag を維持する。影響確認結果は本 review-wave と downstream impact decision に記録する。

| feature | 判定 | 根拠 |
| --- | --- | --- |
| foundation | existing_sufficient | `effect_kind`、`required_action`、状態機械語彙を下支えするが、今回の補強は workflow-management 側の operation contract / approval gate / prompt preflight の要求であり、foundation の共通語彙や共有スキーマを変更しない。 |
| runtime | existing_sufficient | session capture、review-run、bundle/export、状態可視化を consumer として読む可能性はあるが、runtime の evidence writer や実行記録契約の正本変更は不要。 |
| evaluation | existing_sufficient | review-run や post-write verification 証跡を評価対象として読む可能性はあるが、評価分類・メトリクス・モデル比較契約の変更は不要。 |
| analysis | existing_sufficient | operation record や review evidence を後段分析で読む可能性はあるが、analysis の入力・出力契約を変更しない。 |
| workflow-management | reopen_existing_feature | 本 reopen の所有機能。Requirement 13〜16、triad-review 反映、review-wave / alignment / approval、および design / tasks / implementation の再実施対象である。 |
| self-improvement | existing_sufficient | 規律改善や workflow 改善候補を受ける consumer になり得るが、改善提案ループや規律変更提案権限の正本変更は不要。 |
| conformance-evaluation | existing_sufficient | workflow-management の operation contract / preflight / prompt audit を適合性確認対象として参照し得るが、conformance-evaluation の reopen handoff 契約や正本更新境界は変更不要。 |

## 縦方向意図伝達の確認

本 review-wave は横断影響の確認であり、requirements triad-review の再判定を置き換えない。縦方向意図伝達については、`2026-06-19-workflow-management-requirements-vertical-redo-review-run-v2` の triad-review と proxy_model 判定により、Requirement 13〜16 の目的・責務境界・受入条件・禁止事項が requirements へ反映されていることを確認済みである。

本段で追加確認した点は、横断対処によって上流意図を弱めたり、他 feature へ未根拠の正本変更を追加したりしていないことである。今回の判断は「他 feature への正本変更なし」であり、Requirement 16 受入 12 が求める consumer / derivative 確認を記録するものに留まる。

## 判定

- **decision: existing_sufficient**
- workflow-management 以外の feature について、requirements 正本変更は不要。
- consumer / derivative としての影響は、現行正本で受けられる。
- reopen scope と impact review scope は区別する。他 feature の workflow flag を false に戻さない理由は、他 feature が正本変更不要であり、consumer / derivative としての確認で足りるためである。
- 下流（design / tasks / implementation）への縦方向の再展開は、reopen の `impacted_downstream_phases`（design / tasks / implementation）で扱う。

## 証跡

- `.reviewcompass/specs/workflow-management/requirements.md`
- `.reviewcompass/specs/workflow-management/reviews/2026-06-19-workflow-management-requirements-vertical-redo-review-run-v2/review_summary.md`
- `.reviewcompass/specs/workflow-management/reviews/2026-06-19-workflow-management-requirements-vertical-redo-review-run-v2/triage.yaml`
- `.reviewcompass/specs/workflow-management/reviews/2026-06-19-workflow-management-requirements-vertical-redo-review-run-v2/proxy-decision-decisions.yaml`
- `.reviewcompass/specs/workflow-management/reviews/2026-06-19-workflow-management-requirements-vertical-redo-review-run-v2/raw-review-triage-summary.md`
- `.reviewcompass/specs/_cross_feature/reviews/2026-06-20-requirements-vertical-redo-review-wave-summary.md`
