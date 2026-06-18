---
date: 2026-06-19
gate: stages/requirements.yaml#review-wave
feature: all_features
phase: requirements
stage: review-wave
reopen: R-0（integrated-design-requirements）
decision: existing_sufficient
carry_forward_unresolved: 0
summary_evidence: .reviewcompass/specs/_cross_feature/reviews/2026-06-19-requirements-integrated-design-review-wave-summary.md
---

# requirements review-wave：統合設計メモ反映

## 対象

reopen R-0（`docs/reviews/reopen-classification-2026-06-19-wm-integrated-design-requirements.md`）の第3過程、workflow-management requirements フェーズの review-wave（機能横断レビュー段）。

今回の requirements 変更は、Requirement 13〜16 に統合設計メモを反映し、triad-review の C1/C2 must-fix と C3〜C7 should-fix を補強したものである。主な対象は次の通り。

- operation contract と 19 `required_action` 対応
- 承認ゲート、side-track stack、commit mixing 防止
- 状態スナップショット
- 構造化有効プロンプト
- Phase 0〜6 の段階的実装計画
- proxy_model triage decision の機械処理化候補
- reopen scope と impact review scope の区別

## 機械サマリ

`tools/check-workflow-action.py review-wave-summary --out .reviewcompass/specs/_cross_feature/reviews/2026-06-19-requirements-integrated-design-review-wave-summary.md` を実行した。

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

今回の変更の直接所有者は workflow-management である。他 feature は operation contract、構造化有効プロンプト、状態スナップショット、proxy_model triage decision の consumer / derivative として影響確認対象に含める。

本 review-wave では、次の切り分けを正本として扱う。

- **reopen scope**：`workflow-management` のみ。requirements 正本を実質変更したため、同 feature の requirements 後段と design / tasks / implementation の対象 gate を再実施する。
- **impact review scope**：全 feature。foundation / runtime / evaluation / analysis / self-improvement / conformance-evaluation は consumer / derivative として確認する。
- **flag 方針**：他 feature については requirements 正本変更を要求しないため、既存 workflow flag を維持する。影響確認結果は本 review-wave と downstream impact decision に記録する。

| feature | 判定 | 根拠 |
| --- | --- | --- |
| foundation | existing_sufficient | `effect_kind`、`required_action`、review 証跡語彙を参照し得るが、今回の変更は workflow-management が所有する operation contract / preflight の要求であり、foundation の語彙正本や共有スキーマを変更しない。 |
| runtime | existing_sufficient | session capture、review-run、bundle/export、状態可視化を consumer として読む可能性はあるが、runtime の実行契約や evidence writer の正本変更は不要。 |
| evaluation | existing_sufficient | review-run や post-write verification 証跡を評価対象として読む可能性はあるが、評価分類・メトリクス・モデル比較契約の変更は不要。 |
| analysis | existing_sufficient | operation record や review evidence を後段分析で読む可能性はあるが、analysis の入力・出力契約を変更しない。 |
| workflow-management | reopen_existing_feature | 本 reopen の所有機能。Requirement 13〜16、triad-review 反映、review-wave / alignment / approval、および design / tasks / implementation の再実施対象である。 |
| self-improvement | existing_sufficient | 規律改善や workflow 改善候補を受ける consumer になり得るが、改善提案ループや規律提案権限の正本変更は不要。 |
| conformance-evaluation | existing_sufficient | workflow-management の operation contract / preflight / prompt audit を適合性確認対象として参照し得るが、conformance-evaluation の実装由来契約抽出や reopen handoff 契約は変更不要。 |

## 判定

- **decision: existing_sufficient**
- workflow-management 以外の feature について、requirements 正本変更は不要。
- consumer / derivative としての影響は、現行正本で受けられる。
- reopen scope と impact review scope は区別する。他 feature の workflow flag を false に戻さない理由は、他 feature が正本変更不要であり、consumer / derivative としての確認で足りるためである。
- 下流（design / tasks / implementation）への縦方向の再展開は、reopen の `impacted_downstream_phases`（design / tasks / implementation）で扱う。

## 証跡

- `.reviewcompass/specs/workflow-management/requirements.md`
- `.reviewcompass/specs/workflow-management/reviews/2026-06-19-workflow-management-requirements-integrated-design-review-run/proxy-decision-summary.md`
- `.reviewcompass/specs/workflow-management/reviews/2026-06-19-workflow-management-requirements-integrated-design-review-run/review-response.md`
- `.reviewcompass/post-write-verification/post-write-2026-06-19-254.yaml`
- `.reviewcompass/post-write-verification/post-write-2026-06-19-255.yaml`
- `.reviewcompass/specs/_cross_feature/reviews/2026-06-19-requirements-integrated-design-review-wave-summary.md`
