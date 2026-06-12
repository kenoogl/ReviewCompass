---
type: conformance_evaluation
mode_internal: post_hoc_intent_diff
author: implementation
reviewer: workflow
---

# post_hoc_intent_diff

## Added Intent

既存のシステムに意図を後から追加した場合も、仕様駆動開発の手順に従って下流工程へ進める。

## Feature Partitioning

conformance-evaluation は既存仕様と実装コードから差分候補を抽出し、workflow-management は候補を reopen 手続きとして展開する。

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
