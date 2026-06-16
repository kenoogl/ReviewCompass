---
date: 2026-06-16
gate: stages/tasks.yaml#review-wave
feature: workflow-management
reopen: R-0（operation-registry-preflight-unified-design）
decision: no_impact
carry_forward_unresolved: 0
summary_evidence: .reviewcompass/specs/_cross_feature/reviews/2026-06-16-tasks-operation-registry-preflight-review-wave-summary.md
---

# tasks review-wave（機能横断段）：operation registry / preflight

reopen R-0（`docs/reviews/reopen-classification-2026-06-16-wm-operation-registry-preflight.md`）の第3過程、workflow-management tasks フェーズの review-wave。

本 review-wave は、workflow-management の `tasks.md` に追加した T-014（operation registry / read-only preflight）が、他 feature の tasks 正本を再オープンさせるかを確認する。

## 機械サマリ

`tools/check-workflow-action.py review-wave-summary --out .reviewcompass/specs/_cross_feature/reviews/2026-06-16-tasks-operation-registry-preflight-review-wave-summary.md` を実行した。

- status: ok
- carry-forward 未消化: 0
- feature_order: foundation, runtime, evaluation, analysis, workflow-management, self-improvement, conformance-evaluation
- workflow-management: recheck pending（design, tasks, implementation）
- 未充足依存: self-improvement←workflow-management, conformance-evaluation←workflow-management

未充足依存は、現在の workflow-management reopen が完了していないために発生している一時状態であり、他 feature へ新たな tasks 正本修正を要求するものではない。

## 持ち越し所見（carry-forward register）

正本：`learning/workflow/carry-forward-register/reviewcompass-import.yaml`。未消化の carry-forward は 0 件。本 review-wave で新たに消化すべき横断所見はない。

## 機能横断の影響判定

T-014 は、Requirement 12 の operation registry / read-only preflight を workflow-management の実装タスクへ落とすものである。主な追加点は次である。

- `stages/operation-registry.yaml` と operation registry / preflight helper の追加。
- `operation-preflight --operation-id <id> --json` サブコマンド。
- operation family ごとの必須 check。
- `next --json` active state dimensions の必須キー固定検証。
- review artifact / approval / bundle、serial_only approval chain、current-session formal record guard、nested issue、deployment / export、LLM 非依存の TDD テスト群。
- Phase 1 read-only preflight と Phase 2 runner-enabled operation の分離。

全 feature は impact review scope に含める。ただし、tasks 正本を変更する直接所有者は workflow-management であり、他 feature は consumer / derivative として契約変更要否を確認する対象である。

| feature | 影響 | 根拠 |
| --- | --- | --- |
| workflow-management | 自機能（tasks 追加） | Requirement 12 の実装タスク T-014 を所有する。 |
| foundation | 正本変更不要 | operation registry / preflight は workflow 操作契約であり、foundation の語彙・共有型 tasks を変更しない。 |
| runtime | 正本変更不要 | session record capture や deployment / export に接続し得るが、runtime tasks の実装責務を移さない。 |
| evaluation | 正本変更不要 | review artifact を評価対象として参照し得るが、evaluation tasks の分類・メトリクス実装を変更しない。 |
| analysis | 正本変更不要 | operation evidence を分析入力として読む可能性はあるが、analysis tasks の入出力実装を変更しない。 |
| self-improvement | 正本変更不要 | 手戻り削減候補を読む側として参照し得るが、self-improvement tasks の改善提案ループを変更しない。 |
| conformance-evaluation | 正本変更不要 | workflow-management の preflight 契約を照合対象として参照し得るが、conformance-evaluation tasks の所有責務を変更しない。 |

## 判定

- **decision：no_impact**（他 6 機能への tasks 正本修正なし）。
- **carry-forward：未消化 0 件**。
- reopen scope は `workflow-management` のみ、impact review scope は全 feature とする。
- 他 feature の tasks flag を false に戻さない理由は、他 feature が `indirect_check_only` であり、この review-wave で tasks 正本変更不要と判定したためである。
- 下流（implementation）への縦方向の再展開は、reopen の `impacted_downstream_phases`（implementation）で扱う。
