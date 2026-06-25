# 作業モード分類（workflow mode taxonomy）関連作業の索引

最終更新：2026-06-25。

## このメモの位置づけ

正式なワークフロー手続き（intent→requirements→design→tasks→implementation）以外の作業モード（maintenance／side-track／blocking unit／reopen／parent-resume／cross-feature／post-write verification）を整理する取り組みは、複数のファイルに散在している。本メモは、それらを 1 か所から辿れるようにする**俯瞰索引**である。正本仕様・運用規律・次判定そのものではなく、把握・判断材料の notes として扱う（軽量自己精査の対象）。

関係の整理は、中心 plan の `related`／`supersedes`／`provenance` フィールドと、2026-06-25 の俯瞰調査に基づく暫定整理である。各 plan の細部まで精読した結果ではない点に注意する。

## 中心：作業モード分類の定義

- [plan-2026-06-23-maintenance-workflow-protocol.yaml](../../.reviewcompass/backlog/plans/plan-2026-06-23-maintenance-workflow-protocol.yaml)（status: candidate）
  - **MWP-0「Clarify workflow mode taxonomy」** が中核。maintenance／side-track／blocking unit が「同列概念ではない」とし、次の 5 軸に分けて表す。
    1. `current_state`（現在状態）… `next --json` が返す機械状態（completed／maintenance_in_progress／blocking_unit_in_progress／post_write_verification）
    2. `work_class`（作業区分）… これから行う手続きの種類（normal workflow／maintenance／reopen／verification）
    3. `control_relation`（制御関係）… 本線・親作業との関係（mainline／side-track／blocking-unit／parent-resume）
    4. `permitted_scope`（許可範囲）… allowed_scope／allowed_files／completion_conditions（作業宣言の属性）
    5. `work_context`（作業文脈）… completed でも残る現在地（active_anchor／side_track_stack／return_target）
  - MWP-1：maintenance／reopen／新規 workflow の使い分け基準
  - MWP-2：maintenance の evidence フィールドと next-json 状態
  - MWP-3：commit 前 guard での未充足検出

## ① 発想の元になったメモ（notes）

- [2026-06-17-maintenance-workflow-compliance-improvement-candidates.md](2026-06-17-maintenance-workflow-compliance-improvement-candidates.md) … 直接の前身（中心 plan の `supersedes`／`source_ref`）
- [2026-06-16-next-json-unique-state-redesign.md](2026-06-16-next-json-unique-state-redesign.md) … 「次判定が唯一の現在地を返せない」根本欠陥
- [2026-06-16-workflow-recovery-smell-inventory.md](2026-06-16-workflow-recovery-smell-inventory.md) … 戻り先（return_target）が正本化されていない問題
- [2026-06-18-mechanized-workflow-execution-design.md](2026-06-18-mechanized-workflow-execution-design.md) … 機械化と人間判断の分離という中核思想

## ② 各軸を実装する関連計画（すべて status: candidate）

| 計画 | 主に担う軸 |
| --- | --- |
| [plan-2026-06-22-blocking-unit-control-improvements.yaml](../../.reviewcompass/backlog/plans/plan-2026-06-22-blocking-unit-control-improvements.yaml) | control_relation（blocking-unit）／work_context |
| [plan-2026-06-23-nested-issue-stack.yaml](../../.reviewcompass/backlog/plans/plan-2026-06-23-nested-issue-stack.yaml) | control_relation の親子（nested） |
| [plan-2026-06-23-operation-registry-preflight.yaml](../../.reviewcompass/backlog/plans/plan-2026-06-23-operation-registry-preflight.yaml) | 作業宣言の機械化／permitted_scope（中心 plan の related） |
| [plan-2026-06-23-commit-stop-point-and-approval-ux.yaml](../../.reviewcompass/backlog/plans/plan-2026-06-23-commit-stop-point-and-approval-ux.yaml) | completion_conditions／work_context（中心 plan の related） |
| [plan-2026-06-23-action-execution-spec.yaml](../../.reviewcompass/backlog/plans/plan-2026-06-23-action-execution-spec.yaml) | permitted_scope（read／write／state_mutation の区別） |
| [plan-2026-06-23-workflow-navigator-webui.yaml](../../.reviewcompass/backlog/plans/plan-2026-06-23-workflow-navigator-webui.yaml) | work_context の可視化 |

## ③ 個別モードの掘り下げ

- side-track：[2026-06-09-d027-side-track-state-model-checklist.md](2026-06-09-d027-side-track-state-model-checklist.md)（contract 定義・検証済み）
- nested issue：[2026-06-16-nested-issue-handling-smell.md](2026-06-16-nested-issue-handling-smell.md)
- reopen：[REOPEN_PROCEDURE.md](../../.reviewcompass/guidance/REOPEN_PROCEDURE.md)

## ④ すでに機構側に入っている対応（実装・規格・手引き）

- 実装：`tools/check_workflow_action/` の `side_track_stack.py`／`work_unit_stack.py`／`workflow_state_snapshot.py`／`operation_preflight.py`／`commit_unit.py`
- 規格：`.reviewcompass/schema/` の `next_action_response.schema.json`／`required_action.schema.json`／`operation_contract.schema.json` ほか
- 手引き：[WORKFLOW_NAVIGATION.md](../../.reviewcompass/guidance/WORKFLOW_NAVIGATION.md)、[WORKFLOW_DISCIPLINE_MAP.yaml](../../.reviewcompass/guidance/WORKFLOW_DISCIPLINE_MAP.yaml)

## ⑤ 整理作業の完了記録

- [maintenance-2026-06-23-workflow-mode-taxonomy-note.yaml](../../stages/completed/maintenance-2026-06-23-workflow-mode-taxonomy-note.yaml) … この分類を backlog に記録した作業の完了記録

## 現状の要点

- 5 軸の分類（MWP-0）と、各層の実装計画（②）は揃っているが、**分類体系そのものを正式な手引き（WORKFLOW_NAVIGATION）や `next --json` に統合する作業は未着手（candidate）**である。
- 機構側（④）には side-track／blocking unit／snapshot などの個別実装が既に入っているが、5 軸の用語で統一されてはいない。
- 次に進めるなら、MWP-0 の `system_reflection_candidates`（用語表の追加、`next --json` への work_class／control_relation 付与など）が着手点になる。
