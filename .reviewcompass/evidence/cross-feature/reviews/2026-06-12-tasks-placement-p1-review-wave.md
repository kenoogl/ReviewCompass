---
feature: all_features
phase: tasks
stage: review-wave
date: 2026-06-12
status: completed
record_type: reopen-review-wave
related_reopen: stages/in-progress/reopen-procedure-2026-06-12-placement-p1-ce.yaml
---

# reopen R-0（placement-p1）tasks review-wave 実施記録

## 対象と確認範囲

conformance-evaluation tasks の配置契約変更（6 箇所＋triad-review 3 round で追加した T-009／T-007／
T-012／T-001 の凍結期タスク・テスト要件）が、他 6 機能の tasks に波及しないかを確認した。

## 検証方法と結果

機械検査：全 7 機能の requirements.md・design.md・tasks.md に対する旧パス参照の grep
（`specs/<feature>/conformance`・`specs/conformance-evaluation/conformance`・`logs/estimation`）で全機能 0 件
（tasks 確定本文の時点で再実行し、requirements・design の review-wave 時と同一結果）。

追加確認：追加したタスク・テスト要件（書き込み先切替・フォールバック・凍結違反検出・採番統合・
推定ログの凍結期契約）はいずれも conformance-evaluation 所有のツール（evaluation_record.py・
comparison_model.py・machine_verification.py 等）と同テストに閉じ、他機能のタスク境界に新たな
接合面を作らない。workflow-management 側のパス契約は並行 reopen（D-0）の対象。

## 判断

- 波及：なし（no_impact）
- 機能横断の持ち越し：0 件
