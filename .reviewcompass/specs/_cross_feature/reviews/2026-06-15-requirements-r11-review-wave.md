---
date: 2026-06-15
gate: stages/requirements.yaml#review-wave
feature: workflow-management
reopen: R-0（decision-source-lint）
decision: no_impact
carry_forward_unresolved: 0
---

# requirements review-wave（機能横断段）：Requirement 11（重要決定の出典検査）

reopen R-0（`docs/reviews/reopen-classification-2026-06-15-wm-decision-source-lint.md`）の第3過程、workflow-management requirements フェーズの review-wave（機能横断レビュー段）。新設した Requirement 11（重要決定の出典検査＝束ね検出・逐語照合・内容性、および構造化した重要決定の記録形式）が他機能へ波及するかを確認する。

## 持ち越し所見（carry-forward register）

正本：`learning/workflow/carry-forward-register/reviewcompass-import.yaml`。全 17 件が `status: resolved`。**未消化 0 件**。本 review-wave で新たに消化すべき持ち越しはない。

## 機能横断の影響判定

Requirement 11 は workflow-management の責務（段集合 YAML による静的検査・修復手続きの機械強制・不可逆操作の直前ゲート）の内部に閉じる。各機能への波及は次のとおり。

| feature | 影響 | 根拠 |
| --- | --- | --- |
| workflow-management | 自機能（要件追加） | 本 reopen の所有機能。Req 11 の要件・設計・実装を所有。 |
| foundation | なし | 共通契約・スキーマに変更なし。重要決定の記録形式は workflow-management 所有の新成果物で、foundation の共通スキーマを変更しない（分類記録で確認・3 体検証済み）。 |
| runtime | なし | 実行契約に変更なし。lint は読み取り専用で実行時生成物の契約を変えない。 |
| evaluation | なし | 評価契約に変更なし。 |
| analysis | なし | 横断分析（複数実行の二次分析）とは別。本 lint は 1 件の決定記録に対する静的検査。 |
| self-improvement | なし | self-improvement は規律の提案権を持つが、決定記録の出典・束ね・逐語照合の機械強制は workflow-management の責務。規律本文・同期範囲に変更なし。 |
| conformance-evaluation | なし | 実装推定・照合に変更なし。 |

なお Requirement 11 受入3 は層 1 転写（`.reviewcompass/evidence/sessions/`）を逐語照合の入力に用いるが、これは session-record 系ツールが生成する既存の証跡を**読み取る**だけで、その生成契約（来歴刻印・再現性）を変更しない。したがって接合面の変更はない。

## 判定

- **decision：no_impact**（他 6 機能への波及なし）。
- **carry-forward：未消化 0 件**。
- 本フェーズ（requirements）から下流（design／tasks／implementation）への伝播は、reopen の impacted_downstream_phases（design／tasks／implementation）で扱う。design 以降で Requirement 11 の「design で確定」とした事項（記録スキーマ・出典ロケータの表現・保留の順序制御・接続点・内容なし語リスト・正規化規則）を詰める。
