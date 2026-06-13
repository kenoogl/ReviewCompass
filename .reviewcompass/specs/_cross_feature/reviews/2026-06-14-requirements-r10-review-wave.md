# review-wave（機能横断波及）：requirements / Requirement 10（review-wave 要約コマンド、reopen R-0）

- 日付：2026-06-14
- 対象：workflow-management requirements への Requirement 10 新設
- reopen：R-0（分類記録 `docs/reviews/reopen-classification-2026-06-14-wm-review-wave-summary-command.md`）

## 判定：no_impact（機能横断波及なし）

Requirement 10 は workflow-management 内の新コマンド（ワークフロー状態の静的検査）であり、他 6 機能の requirements・契約・接合面を変更しない。

| feature | 波及 | 理由 |
| --- | --- | --- |
| foundation | なし | 共有語彙・スキーマに変更なし。要約コマンドは既存状態を読むだけ。 |
| runtime | なし | 実行契約・review-run 生成に変更なし。 |
| evaluation | なし | 評価契約に変更なし。 |
| analysis | なし | analysis は複数実行の二次分析。本コマンドは 1 回分の静的検査で別物。読み手として接合面不変。 |
| self-improvement | なし | 学習資産・提案フローに変更なし。 |
| conformance-evaluation | なし | 実装推定・照合に変更なし。 |

確認方法：本変更は新規要件の追加であり、他機能の requirements 本文・契約を参照・改変していない（Requirement 10 は workflow-management の既存 Requirement 1・2・8 のみを参照）。carry-forward register への新規持ち越しなし（持ち越し 0 件）。

## 結論

機能横断波及なし。下流（design／tasks／implementation）は workflow-management 内に閉じる。
