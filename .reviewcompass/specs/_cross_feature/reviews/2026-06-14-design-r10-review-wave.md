# review-wave（機能横断波及）：design / Requirement 10（review-wave 要約コマンド、reopen R-0）

- 日付：2026-06-14／対象：workflow-management design §review-wave 要約コマンドモデル新設

## 判定：no_impact

要約コマンドの設計は workflow-management 内に閉じる（既存状態の読み取りと出力。他機能の契約・接合面に変更なし）。

| feature | 波及 | 理由 |
| --- | --- | --- |
| foundation | なし | 共有契約・スキーマ不変 |
| runtime | なし | 実行契約不変 |
| evaluation | なし | 評価契約不変 |
| analysis | なし | 複数実行の二次分析とは別系統。読み手として接合面不変 |
| self-improvement | なし | 不変 |
| conformance-evaluation | なし | 不変 |

carry-forward への新規持ち越しなし（0 件）。下流（tasks／implementation）は workflow-management 内に閉じる。
