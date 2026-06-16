---
date: 2026-06-16
gate: stages/requirements.yaml#review-wave
feature: workflow-management
reopen: R-0（operation-registry-preflight-unified-design）
decision: no_impact
carry_forward_unresolved: 0
summary_evidence: .reviewcompass/specs/_cross_feature/reviews/2026-06-16-requirements-operation-registry-preflight-review-wave-summary.md
---

# requirements review-wave（機能横断段）：operation registry / preflight

reopen R-0（`docs/reviews/reopen-classification-2026-06-16-wm-operation-registry-preflight.md`）の第3過程、workflow-management requirements フェーズの review-wave（機能横断レビュー段）。Requirement 12（operation registry / preflight）が他機能の requirements 正本変更を要求するかを確認する。

## 機械サマリ

`tools/check-workflow-action.py review-wave-summary --out .reviewcompass/specs/_cross_feature/reviews/2026-06-16-requirements-operation-registry-preflight-review-wave-summary.md` を実行した。

- status: ok
- carry-forward 未消化: 0
- feature_order: foundation, runtime, evaluation, analysis, workflow-management, self-improvement, conformance-evaluation
- workflow-management: recheck pending（design, tasks, implementation）
- 未充足依存: self-improvement←workflow-management, conformance-evaluation←workflow-management

未充足依存は、現在の workflow-management reopen が完了していないために発生している一時状態であり、他機能へ新たな requirements 正本修正を要求するものではない。

## 持ち越し所見（carry-forward register）

正本：`learning/workflow/carry-forward-register/reviewcompass-import.yaml`。未消化の carry-forward は 0 件。本 review-wave で新たに消化すべき横断所見はない。

## 機能横断の影響判定

Requirement 12 は、workflow-management が所有する操作開始前検査、正本コマンド検証、pending / worktree 衝突検査、review artifact preflight、commit approval chain、session-record guard、deployment / export preflight、nested issue handling を要件化するものである。

全 feature は impact review scope に含める。ただし、requirements 正本を変更する直接所有者は workflow-management であり、他 feature は consumer / derivative として契約変更要否を確認する対象である。

本 review-wave では、次の切り分けを正本として扱う。

- **reopen scope**：`workflow-management` のみ。requirements 正本を実質変更したため、同 feature の requirements 後段と design／tasks／implementation の対象 gate を false に戻して再実施する。
- **impact review scope**：全 feature。foundation／runtime／evaluation／analysis／self-improvement／conformance-evaluation は `indirect_check_only` であり、現時点では正本再オープン対象ではない。
- **flag 方針**：`reopen_existing_feature` の feature は以降 flag を false に戻す。`indirect_check_only` の feature は、正本変更が必要と判定されない限り既存 flag を保持し、review-wave / downstream impact decision に「変更不要」を記録する。

| feature | 影響 | 根拠 |
| --- | --- | --- |
| workflow-management | 自機能（要件追加） | 本 reopen の所有機能。Requirement 12 の design／tasks／implementation を所有する。 |
| foundation | 正本変更不要 | operation registry が参照する語彙や証跡の考え方は foundation を読む可能性があるが、現時点で foundation の共通語彙・共有スキーマを追加変更しない。 |
| runtime | 正本変更不要 | session capture や bundle export と接続し得るが、Requirement 12 は workflow 操作開始前検査の契約であり、runtime の review execution / evidence writer 契約を変更しない。 |
| evaluation | 正本変更不要 | review-run や post-write verification の証跡を評価対象として読む可能性はあるが、評価分類・メトリクス契約を変更しない。 |
| analysis | 正本変更不要 | operation record や review evidence を後段で読む可能性はあるが、分析入力・出力契約を変更しない。 |
| self-improvement | 正本変更不要 | 手戻り削減候補を出す側・読む側として参照し得るが、改善提案ループや規律提案権の契約を変更しない。 |
| conformance-evaluation | 正本変更不要 | workflow-management の preflight 契約を照合対象として参照し得るが、実装由来契約抽出・reopen handoff の所有責務を変更しない。 |

## 判定

- **decision：no_impact**（他 6 機能への requirements 正本修正なし）。
- **carry-forward：未消化 0 件**。
- 全 feature impact review scope は、以後の design／tasks／implementation gate でも `feature_impact_decisions` と `required_feature_scope` により保持する。
- reopen scope と impact review scope は混同しない。他 feature の requirements flag を false に戻さなかった理由は、他 feature が `indirect_check_only` であり、この review-wave で requirements 正本変更不要と判定したためである。
- 下流（design／tasks／implementation）への縦方向の再展開は、reopen の `impacted_downstream_phases`（design／tasks／implementation）で扱う。
