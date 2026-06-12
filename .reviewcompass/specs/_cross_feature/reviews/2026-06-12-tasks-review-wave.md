---
feature: all_features
phase: tasks
stage: review-wave
date: 2026-06-12
context: reopen R-0（docs/reviews/reopen-classification-2026-06-12-multi-llm-entry-spec-reflection.md）第3過程
---

# tasks review-wave（機能横断確認）実施記録

## 対象と範囲

reopen R-0 の tasks 変更（workflow-management tasks.md：T-002 スキーマ契約の実装検査代替・
T-003／T-005 参照語彙・T-004 契約追記と fail-closed 例外の追跡明示・対応表。
conformance-evaluation tasks.md：T-010 ほか文言追従 4 箇所）が、他 feature の tasks と
矛盾・波及しないことの確認。確認した feature 範囲：全 7 機能。

## 持ち越し件数

carry-forward register：未解決 0 件（requirements・design の review-wave から変動なし）。

## recheck 結果

1. **語彙の波及**：foundation／runtime／evaluation／analysis／self-improvement の tasks.md に
   `feature_order`・`phase_order` への言及はない（grep で確認）。
2. **スキーマ契約代替の波及**：T-002 のスキーマ（feature-dependency.schema.json）を参照していた
   他 feature の記述は conformance-evaluation T-010 完了条件 4（DVT-C002）のみで、これは
   「workflow-management のスキーマ拡張（連想配列許容、Req 8 受入 2）との整合」という仕様レベルの
   合意を指す。Req 8 受入 2 の 2 形式許容契約は不変であり、検証手段が JSON Schema から実装検査へ
   変わっても T-010 の合意内容（連想配列構造の許容）は影響を受けない。過去の解除記録
   （DVT-C002 解除済 2026-05-29）は歴史的記録として書き換えない。
3. **同根所見クラスタ**：tasks triad-review の全所見は workflow-management tasks 内で完結し、
   他 feature の tasks 修正を要するものはない。

## 実行した検証コマンド

- `grep feature_order|phase_order` による他 5 機能 tasks への波及確認（該当なし）
- carry-forward register の未解決件数集計（0 件）

## 判断結果

機能横断の波及なし。tasks review-wave は pass とし、alignment（整合チェック）へ進む。
