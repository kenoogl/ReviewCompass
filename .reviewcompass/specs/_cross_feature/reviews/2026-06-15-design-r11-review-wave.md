---
date: 2026-06-15
gate: stages/design.yaml#review-wave
feature: workflow-management
reopen: R-0（decision-source-lint）
decision: no_impact
carry_forward_unresolved: 0
---

# design review-wave（機能横断段）：Requirement 11 設計（重要決定の出典検査）

reopen R-0（`docs/reviews/reopen-classification-2026-06-15-wm-decision-source-lint.md`）の第3過程、design フェーズの review-wave（機能横断レビュー段）。design.md に追加した §Req 11 設計モデル（記録スキーマ・ロケータ・正規化規則・保留管理・内容なし語リスト・サブコマンドと接続点）が他機能へ波及するかを確認する。

## 持ち越し所見（carry-forward register）

正本：`learning/workflow/carry-forward-register/reviewcompass-import.yaml`。全 17 件が `status: resolved`。**未消化 0 件**。本 review-wave で新たに消化すべき持ち越しはない。

## 機能横断の影響判定

Req 11 設計モデルは workflow-management の責務（重要決定の出典検査・機械強制の設計）の内部に閉じる。各機能への波及は次のとおり。

| feature | 影響 | 根拠 |
| --- | --- | --- |
| workflow-management | 自機能（設計追加） | 本 reopen の所有機能。§Req 11 設計モデルを所有。 |
| foundation | なし | 共通契約・スキーマに変更なし。`.reviewcompass/decisions/` への配置と `decision_id` 命名則は workflow-management 内部の設計であり、foundation の共通スキーマを変更しない。 |
| runtime | なし | 実行契約に変更なし。`decision-source-lint` は読み取り専用（`--verify-pending` の例外のみ）であり、実行時生成物の契約を変えない。 |
| evaluation | なし | 評価契約に変更なし。 |
| analysis | なし | 横断分析とは別。本設計は個別決定記録の静的検査。 |
| self-improvement | なし | 規律変更の提案権は self-improvement が持つが、決定記録の出典検査は workflow-management の責務。規律本文・同期範囲に変更なし。 |
| conformance-evaluation | なし | 実装推定・照合に変更なし。 |

なお Req 11 設計では層 1 転写（`.reviewcompass/evidence/sessions/`）を逐語照合の入力に用いるが、これは既存の証跡を**読み取る**だけで生成契約を変更しない（requirements review-wave での確認済み）。

## 指標（review-wave-summary）

- carry-forward 未消化：0
- workflow-management の recheck：pending(design, tasks, implementation)
- 未充足依存：なし

## 判定

- **decision：no_impact**（他 6 機能への波及なし）。
- **carry-forward：未消化 0 件**。
- 本フェーズ（design）の下流（tasks／implementation）への伝播は、reopen の impacted_downstream_phases（design→tasks→implementation）で順次扱う。
