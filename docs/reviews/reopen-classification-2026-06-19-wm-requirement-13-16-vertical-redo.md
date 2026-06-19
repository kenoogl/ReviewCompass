---
feature: workflow-management
date: 2026-06-19
classification: R-0
source_review: .reviewcompass/specs/workflow-management/reviews/2026-06-19-workflow-management-tasks-vertical-intent-regeneration-review-run/raw-review-triage-summary.md
supersedes_reopen: docs/reviews/reopen-classification-2026-06-19-wm-task-granularity-regeneration.md
---

# Reopen Classification: Requirement 13〜16 Vertical Redo

## 判定

`workflow-management` の Requirement 13〜16 を基点とする R-0 reopen とする。

## 理由

tasks 粒度不足として開始した現 reopen では、T-016〜T-019 を implementation-ready な粒度へ再生成し、縦方向意図監査を導入した。しかし、縦方向意図監査つき再レビューにより、問題は tasks.md の粒度だけではなく、requirements → design → tasks の意図伝達と設計権限境界にあることが判明した。

特に次の 2 点は、tasks 側だけで修正すると design authority を越える危険がある。

1. T-016 の operation registry / operation contract 正本境界
   - `stages/operation-registry.yaml` と `stages/operation-contracts.yaml` の分離、single source of truth、digest / version 同期規則が、design で十分に確定しているかを再確認する必要がある。
2. T-017 / T-019 の proxy / human decision 境界
   - Requirement 14、Requirement 16、approval 規律の間で、proxy_model が代行できない human-only decision の根拠と機械可読 predicate を明確にする必要がある。

このため、現在の tasks 起点 reopen は superseded として閉じ、Requirement 13〜16 を基点に requirements / design / tasks を縦方向に再生成する。

## 再実施範囲

- requirements
  - Requirement 13〜16 の目的・責務境界・受入条件・禁止事項を縦方向監査観点で再確認する。
  - 必要な場合のみ、operation registry / contract 正本境界、proxy / human decision 境界を要件として補う。
- design
  - Requirement 13 / 14 / 16 設計モデルを再生成する。
  - tasks に設計判断を押し出さないよう、正本境界と機械可読 predicate を design で確定する。
- tasks
  - design で確定した境界を T-016〜T-019 の red test、実装順序、完了条件、禁止事項、停止条件へ落とし直す。

## 範囲外

- Requirement 1〜12 の全面再生成。
- implementation 実装コードの作成。
- proxy_model 判断、spec 更新、gate 移動、commit はそれぞれの停止点で別途扱う。

## 根拠

- `.reviewcompass/specs/workflow-management/reviews/2026-06-19-workflow-management-tasks-vertical-intent-regeneration-review-run/raw-review-triage-summary.md`
- `docs/notes/working/2026-06-19-vertical-intent-review-audit-experiment.md`
- `docs/operations/SESSION_WORKFLOW_GUIDE.md#vertical-intent-transfer-review`
