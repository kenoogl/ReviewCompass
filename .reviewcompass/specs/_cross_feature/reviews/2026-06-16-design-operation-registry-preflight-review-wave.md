---
date: 2026-06-16
gate: stages/design.yaml#review-wave
feature: workflow-management
reopen: R-0（operation-registry-preflight-unified-design）
decision: no_impact
carry_forward_unresolved: 0
summary_evidence: .reviewcompass/specs/_cross_feature/reviews/2026-06-16-design-operation-registry-preflight-review-wave-summary.md
---

# design review-wave（機能横断段）：operation registry / preflight

reopen R-0（`docs/reviews/reopen-classification-2026-06-16-wm-operation-registry-preflight.md`）の第3過程、workflow-management design フェーズの review-wave。

本 review-wave は、workflow-management の `design.md` に追加した Requirement 12（operation registry / preflight）の設計モデルが、他 feature の design 正本を再オープンさせるかを確認する。

## 機械サマリ

`tools/check-workflow-action.py review-wave-summary --out .reviewcompass/specs/_cross_feature/reviews/2026-06-16-design-operation-registry-preflight-review-wave-summary.md` を実行した。

- status: ok
- carry-forward 未消化: 0
- feature_order: foundation, runtime, evaluation, analysis, workflow-management, self-improvement, conformance-evaluation
- workflow-management: recheck pending（design, tasks, implementation）
- 未充足依存: self-improvement←workflow-management, conformance-evaluation←workflow-management

未充足依存は、現在の workflow-management reopen が完了していないために発生している一時状態であり、他 feature へ新たな design 正本修正を要求するものではない。

## 持ち越し所見（carry-forward register）

正本：`learning/workflow/carry-forward-register/reviewcompass-import.yaml`。未消化の carry-forward は 0 件。本 review-wave で新たに消化すべき横断所見はない。

## 機能横断の影響判定

Requirement 12 の設計は、workflow-management が所有する workflow 操作開始前契約である。主な追加点は次である。

- operation registry schema と operation family / required checks。
- read-only preflight response schema と active state dimensions。
- command validation、worktree / pending / integrity conflict。
- review artifact preflight、commit approval chain、current-session formal record guard。
- nested issue handling、deployment / export preflight。
- `reopen_scope` と `impact_review_scope` の分離、および `next --json` 状態一意性。

全 feature は impact review scope に含める。ただし、design 正本を変更する直接所有者は workflow-management であり、他 feature は consumer / derivative として契約変更要否を確認する対象である。

| feature | 影響 | 根拠 |
| --- | --- | --- |
| workflow-management | 自機能（設計追加） | Requirement 12 の設計モデル、追跡表、XDI-WM-004、変更意図を所有する。 |
| foundation | 正本変更不要 | operation registry / preflight は workflow 操作契約であり、foundation の共通型・基盤責務を変更しない。 |
| runtime | 正本変更不要 | session record capture や deployment / export と接続し得るが、runtime の実行基盤設計を直接変更しない。 |
| evaluation | 正本変更不要 | review artifact や evidence を評価対象として参照し得るが、評価分類・メトリクス設計を変更しない。 |
| analysis | 正本変更不要 | operation evidence を分析入力として読む可能性はあるが、分析 feature の入出力設計を変更しない。 |
| self-improvement | 正本変更不要 | 手戻り削減候補を読む側として参照し得るが、改善提案ループの設計責務を変更しない。 |
| conformance-evaluation | 正本変更不要 | workflow-management の preflight 契約を照合対象として参照し得るが、実装由来契約抽出・handoff 設計を変更しない。 |

## 判定

- **decision：no_impact**（他 6 機能への design 正本修正なし）。
- **carry-forward：未消化 0 件**。
- reopen scope は `workflow-management` のみ、impact review scope は全 feature とする。
- 他 feature の design flag を false に戻さない理由は、他 feature が `indirect_check_only` であり、この review-wave で design 正本変更不要と判定したためである。
- 下流（tasks／implementation）への縦方向の再展開は、reopen の `impacted_downstream_phases`（tasks／implementation）で扱う。
