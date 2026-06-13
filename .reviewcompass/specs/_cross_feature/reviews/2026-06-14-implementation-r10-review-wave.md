# review-wave（機能横断波及）：implementation / Requirement 10（review-wave 要約コマンド、reopen R-0）
- 日付：2026-06-14／対象：review-wave-summary サブコマンド実装

## 判定：no_impact
変更は workflow-management の検査スクリプト（tools/check-workflow-action.py）内に閉じ、新サブコマンドの追加と専用テストのみ。他機能のコード・契約・接合面に変更なし。tests/tools/ 301 件 pass（回帰なし）。carry-forward への新規持ち越し 0 件。
