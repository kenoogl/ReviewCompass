---
date: 2026-06-20
gate: stages/design.yaml#review-wave
feature: all_features
phase: design
stage: review-wave
reopen: R-0（requirement-13-16-vertical-redo）
decision: existing_sufficient
carry_forward_unresolved: 0
summary_evidence: .reviewcompass/specs/_cross_feature/reviews/2026-06-20-design-vertical-redo-review-wave-summary.md
target_manifest: .reviewcompass/specs/workflow-management/reviews/2026-06-20-workflow-management-design-vertical-redo-review-run-v2/post-fix-target-manifest.yaml
gate_completion_authorized: true
approval_source: user message 2026-06-20「では進めてください」
---

# design review-wave：Requirement 13〜16 縦方向やり直し

## 対象

reopen R-0（`docs/reviews/reopen-classification-2026-06-19-wm-requirement-13-16-vertical-redo.md`）の第3過程、workflow-management design フェーズの review-wave（機能横断レビュー段）。

今回の design 変更は、Requirement 13〜16 の縦方向意図監査を design 正本へ反映し、design triad-review v2 の 15 件の所見を post-fix したものである。主な対象は次の通り。

- operation registry / operation contract / preflight の正本境界
- 19 `required_action` と operation contract field の対応
- `run_maintenance` / `run_workflow_stage` の branch / internal step / approval aggregation
- approval record binding、proxy_model と human-only approval の境界
- active reopen scope と impact review scope の分離
- Phase 0 completion criteria と D-003 traceability
- structured prompt length-bound source of truth
- design drafting 状態と implementation 完了状態の表現分離

## 機械サマリ

`tools/check-workflow-action.py review-wave-summary --out .reviewcompass/specs/_cross_feature/reviews/2026-06-20-design-vertical-redo-review-wave-summary.md` を実行した。

- status: ok
- carry-forward 未消化: 0
- feature_order: foundation, runtime, evaluation, analysis, workflow-management, self-improvement, conformance-evaluation
- workflow-management: recheck pending（design, tasks, implementation）
- 未充足依存: self-improvement←workflow-management, conformance-evaluation←workflow-management

未充足依存は、現在の workflow-management reopen が完了していないために発生している一時状態である。本 review-wave では、他 feature の design 正本を再オープンする必要は確認されなかった。

## 持ち越し所見

正本：`learning/workflow/carry-forward-register/reviewcompass-import.yaml`。

未消化の carry-forward は 0 件であり、本 review-wave で新たに消化すべき横断所見はない。

## 機能横断の影響判定

今回の design 変更の直接所有者は workflow-management である。他 feature は operation contract、workflow-state snapshot、structured effective prompt、approval / side-track 機構、proxy_model triage decision、review-run / post-write verification / commit approval の開始前検査を consumer / derivative として影響確認対象に含める。

本 review-wave では、次の切り分けを正本として扱う。

- **reopen scope**：`workflow-management` のみ。design 正本を実質変更したため、同 feature の design 後段と tasks / implementation の対象 gate を再実施する。
- **impact review scope**：全 feature。foundation / runtime / evaluation / analysis / self-improvement / conformance-evaluation は consumer / derivative として確認する。
- **flag 方針**：他 feature については design 正本変更を要求しないため、既存 workflow flag を維持する。影響確認結果は本 review-wave と downstream impact decision に記録する。

| feature | 判定 | 根拠 |
| --- | --- | --- |
| foundation | existing_sufficient | effect / phase / required_action のような共有語彙を下支えし得るが、今回の修正は workflow-management の operation contract / registry / preflight の所有境界と承認契約の具体化である。foundation の共通語彙や配置規約の正本変更は不要。 |
| runtime | existing_sufficient | runtime は session capture や evidence writer の供給側になり得るが、今回の変更は workflow-management が操作開始前に証跡・承認・状態をどう検査し、どう保存するかの設計である。runtime の実行終了境界や evidence writer 契約の変更は不要。 |
| evaluation | existing_sufficient | evaluation は review-run / post-write verification 証跡を評価対象として読む可能性があるが、structured prompt や triage decision の機械化は workflow-management 側の review operation 契約で扱える。evaluation の分類・メトリクス・モデル比較契約の変更は不要。 |
| analysis | existing_sufficient | analysis は workflow-management の運用証跡や snapshot を読む consumer になり得るが、公開される状態・証跡の正本は workflow-management 側で確定する前提を既に持つ。analysis design の正本変更は不要。 |
| workflow-management | reopen_existing_feature | 本 reopen の所有機能。Requirement 13〜16 の design 展開、triad-review v2 の post-fix、review-wave / alignment / approval、および tasks / implementation の再実施対象である。 |
| self-improvement | existing_sufficient | self-improvement は規律改善提案の consumer / upstream signal になり得るが、規律変更の実体操作は workflow-management の所定手続きと human-only approval 境界へ委ねる設計で足りる。self-improvement 正本変更は不要。 |
| conformance-evaluation | existing_sufficient | conformance-evaluation は workflow-management の operation contract / preflight / approval record / prompt audit を適合性確認対象として参照し得るが、reopen handoff や gap classification の正本変更は不要。 |

## 判定

- **decision: existing_sufficient**
- workflow-management 以外の feature について、design 正本変更は不要。
- consumer / derivative としての影響は、現行正本で受けられる。
- reopen scope と impact review scope は区別する。他 feature の workflow flag を false に戻さない理由は、他 feature が正本変更不要であり、consumer / derivative としての確認で足りるためである。
- 下流（tasks / implementation）への縦方向の再展開は、reopen の `impacted_downstream_phases`（design / tasks / implementation）で扱う。

## 証跡

- `.reviewcompass/specs/workflow-management/design.md`
- `.reviewcompass/specs/workflow-management/reviews/2026-06-20-workflow-management-design-vertical-redo-review-run-v2/post-fix-target-manifest.yaml`
- `.reviewcompass/specs/workflow-management/reviews/2026-06-20-workflow-management-design-vertical-redo-review-run-v2/triage.yaml`
- `.reviewcompass/specs/workflow-management/reviews/2026-06-20-workflow-management-design-vertical-redo-review-run-v2/post-fix-coverage-inventory.md`
- `.reviewcompass/specs/workflow-management/reviews/2026-06-20-workflow-management-design-vertical-redo-review-run-v2/integrated-post-fix-review.md`
- `.reviewcompass/specs/workflow-management/reviews/2026-06-20-workflow-management-design-vertical-redo-review-run-v2/integrated-post-fix-recheck.md`
- `.reviewcompass/specs/_cross_feature/reviews/2026-06-20-design-vertical-redo-review-wave-summary.md`

## 停止点

本記録は review-wave の軽量確認結果であり、利用者発言 2026-06-20「では進めてください」により `stages/design.yaml#review-wave` の gate 完了へ進める。phase transition、commit、push、reopen finalization は行わない。
