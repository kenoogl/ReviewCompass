---
type: conformance_evaluation
mode_internal: post_hoc_intent_diff
author: implementation
reviewer: workflow
---

# post_hoc_intent_diff

## Added Intent

レビューの収集処理は、規則ファイル照合や固定プロンプトの単純写像ではなく、実際の大規模言語モデルの判断に基づいて発見と判断を生成する。プロンプトや規則ファイルなどの事前設定は、収集対象や入力範囲の固定には使ってよいが、観測結果（発見の件数・内容・構造）を縛ってはならない。

## Feature Partitioning

stages/feature-partitioning/2026-05-24-proposal.md は、conformance-evaluation を規律遵守検査、workflow-management を所定手続き・reopen・整合ゲート管理の責務として定義している。

## Candidates

- candidate_id: PHID-CE-001
  feature: conformance-evaluation
  phase: implementation
  classification: implementation_change_candidate
  needs_human_decision: false
  reasoning_summary: 追加 intent は既存コードと既存仕様を照合して下流候補を作る必要があるため、conformance-evaluation の既存システム差分抽出として扱う。
- candidate_id: PHID-WM-001
  feature: workflow-management
  phase: tasks
  classification: downstream_impact_candidate
  needs_human_decision: false
  reasoning_summary: 差分候補は仕様本文を直接更新せず、workflow-management の reopen 手続きへ引き渡して既存 feature reopen または新規 feature 必要性を判定する。
  handoff_target: workflow-management
