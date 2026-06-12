---
feature: all_features
phase: requirements
stage: review-wave
date: 2026-06-12
context: reopen R-0（docs/reviews/reopen-classification-2026-06-12-multi-llm-entry-spec-reflection.md）第3過程
---

# requirements review-wave（機能横断確認）実施記録

## 対象と範囲

reopen R-0 の requirements 変更（workflow-management Requirement 8 受入 1〜3 改訂・受入 6〜8 新設・
Requirement 1 受入 4 参照修正、conformance-evaluation Requirement 7 受入 5 文言追従）が、
他 feature の requirements と矛盾・波及しないことの確認。確認した feature 範囲：全 7 機能。

## 持ち越し件数

carry-forward register（learning/workflow/carry-forward-register/reviewcompass-import.yaml）：
項目 17 件、未解決 0 件。未消化の機能横断持ち越し所見はない。

## recheck 結果

1. **語彙の波及**：foundation／runtime／evaluation／analysis／self-improvement の requirements.md に
   `feature_order`・`phase_order` への言及はなく、語彙統一の影響を受けない（grep で確認）。
   conformance-evaluation Requirement 7 受入 5 は文言追従済み（triad-review で意味不変を確認済み）。
2. **kind 語彙の波及**：`feature_definition_required` は workflow-management T-004 の契約であり、
   foundation の共有語彙（重大度・レビューモード・証拠区分等）に属さない
   （feature impact 判定どおり、foundation requirements に変更不要）。
3. **依存一覧の実体化**（stages/feature-dependency.yaml の 7 機能分転記、MLE-DEC-003）：
   転記元は承認済み分割提案書 §3 であり、依存の意味変更はない。各 feature の depends_on は
   提案書と一致（テスト 871 件通過で回帰なしを確認済み）。
4. **同根所見クラスタ**：triad-review round-1・round-2 の全クラスタ（A〜E、F1〜F4）は
   workflow-management requirements 内で完結し、他 feature の requirements 修正を要するものはない。

## 実行した検証コマンド

- `python3 tools/check-workflow-action.py next --json`（reopen_in_progress、gate 進行の確認）
- `python3 -m pytest tests/ --ignore=tests/self-improvement/test_t001_layout.py`（871 件通過）
- carry-forward register の未解決件数集計（上記 0 件）
- `grep feature_order|phase_order` による他 5 機能 requirements への波及確認（該当なし）

## 判断結果

機能横断の波及なし。requirements review-wave は pass とし、alignment（整合チェック）へ進む。
