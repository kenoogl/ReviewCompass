---
date: 2026-06-15
gate: stages/tasks.yaml#review-wave
feature: workflow-management
reopen: R-0（decision-source-lint）
decision: no_impact
---

# tasks review-wave：Req 11 タスク追記（reopen R-0 2026-06-15）

reopen R-0 の第3過程、tasks フェーズの review-wave 段。T-013 タスク定義の他 6 機能への波及を確認する。

## 確認対象

tasks.md への追記内容：
- T-013：重要決定の出典検査（decision-source-lint サブコマンド）の新タスク定義
- 要件追跡表 Req 11 行（7 行）
- 変更意図 Req 11 追記

## 他機能への波及確認

| 機能 | 関係 | 判定 |
| --- | --- | --- |
| foundation | T-013 は `check-workflow-action.py` のサブコマンド追加。foundation の語彙正本（review_mode 等）を参照するが再定義しない。foundation の段集合・スキーマに変更なし。 | 波及なし |
| conformance-evaluation | conformance-evaluation は仕様適合評価を担うが、T-013 の decision-source-lint は workflow-management 内部の重要決定管理に閉じる。CE の入力ファイルや出力スキーマに変更なし。 | 波及なし |
| self-improvement | T-013 は重要決定の出典検査のみ。self-improvement との接合面（docs/disciplines/ 変更の所定手続き）は T-010 が担い、T-013 には直接関係しない。 | 波及なし |
| cross-spec-alignment | T-013 は workflow-management 内部の静的検査。cross-spec-alignment の機能横断整合手続きに変更なし。 | 波及なし |
| runtime | T-013 の成果物は `check-workflow-action.py` の追加サブコマンドと設定ファイル。runtime の段集合・証跡スキーマに変更なし。 | 波及なし |
| evaluation | T-013 は evaluation が参照する review-wave・triage 等のスキーマを変更しない。evaluation の入力・出力に変更なし。 | 波及なし |

## 持ち越し台帳確認

carry-forward register（`learning/workflow/carry-forward-register/reviewcompass-import.yaml`）の全件 resolved 済み、未消化 0 件（2026-06-15 時点）。

## 判定

- **decision：no_impact**（T-013 タスク定義は workflow-management 内部に閉じ、他 6 機能の契約・スキーマに変更なし。carry-forward 未消化 0 件）。
