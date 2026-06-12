---
feature: all_features
phase: requirements
stage: review-wave
date: 2026-06-12
status: completed
record_type: reopen-review-wave
related_reopen: stages/in-progress/reopen-procedure-2026-06-12-placement-p1-ce.yaml
---

# reopen R-0（placement-p1）requirements review-wave 実施記録

## 対象と確認範囲

conformance-evaluation requirements の配置契約変更（Requirement 6 受入 2 のルート契約化ほか 5 箇所、
triad-review round-1／round-2 適用済み本文）が、他 6 機能の requirements に波及しないかを確認した。

## 検証方法と結果

機械検査：全 7 機能の requirements.md・design.md・tasks.md に対する旧パス参照の grep
（`specs/<feature>/conformance`・`specs/conformance-evaluation/conformance`・`logs/estimation`）。

- foundation／runtime／evaluation／analysis／workflow-management／self-improvement：**旧パス参照 0 件**
- analysis は conformance-evaluation を機能名で参照する（検査結果の一方向取り込み）が、
  記録の物理パスには依存しない（analysis Requirement 8 受入 5 は出力データの取り込み契約であり配置非依存）
- workflow-management のパス契約（effective prompt・approvals・検査ログ）は本 reopen と並行する
  同日 reopen（D-0、reopen-procedure-2026-06-12-placement-p1-wm.yaml）で扱い、本 gate の対象外

## 判断

- 波及：**なし**（no_impact）
- 機能横断の持ち越し：0 件
