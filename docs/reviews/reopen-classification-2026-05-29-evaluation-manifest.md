---
date: 2026-05-29
classifier: claude_code_main_session
classification: A-1
trigger_source: tasks フェーズの 2 軸整合性監査（縦軸）で確定した design への遡及所見（evaluation の analysis_run_manifest.yaml 必須項目の design↔tasks 不一致）
feature: evaluation
findings: [audit-2026-05-29 #3]
related: docs/reviews/tasks-alignment-audit-2026-05-29.md §5 #3
---

## 分類根拠

tasks フェーズの承認前 2 軸整合性監査（縦軸＝intent→tasks）で、evaluation の `analysis_run_manifest.yaml` の必須項目が design（行517-527）と tasks T-006（行105）で食い違うことが判明。発見フェーズは tasks（起点記号 A）、戻る先は design（manifest 項目定義は design §版管理モデルの正本）。よって種別 **A-1**（tasks で発見、design まで戻る、深さ 1）。

利用者は対処方針として **案2**（design を正本として実行識別 4 項目を追加し union 13 項目に統一、tasks も揃える）を選択（2026-05-29 セッション40）。正規再オープン手続き（REOPEN_PROCEDURE.md）。

## 問題の事実（#3）

`analysis_run_manifest.yaml` の最低限記録項目が design と tasks で異なる：
- 共通 5：`analysis_logic_version`／`input_run_set`／`protocol_version_coverage`／`runtime_version_coverage`／`prompt_set_version_coverage`
- design だけ 4（版管理用、Req 5 受入 5）：`generated_at`／`metric_set_version`／`phase_metric_profile_version`／`comparison_contract_version`
- tasks だけ 4（実行識別用、Req 5 受入 2）：`analysis_run_id`／`analysis_started_at`／`analysis_completed_at`／`output_artifact_ids`

両方とも別々の受入基準が要求するため、union（13 項目）が正しい。design がそれを取りこぼしていた。

## trigger_map A-1 による連鎖再実施対象（計画書 §5.6）

- stages/design.yaml#alignment
- stages/design.yaml#approval
- stages/tasks.yaml#alignment
- stages/tasks.yaml#approval

drafting／triad-review／review-wave は再実施対象外。evaluation の tasks は現在 review-wave 完了済み（本セッション）だが、design 再承認まで tasks alignment/approval は保留。

## spec.json フラグ差し戻し（第1過程ステップ6、承認後に実行）

evaluation/spec.json：
- `reopened.design`：false → **true**
- `workflow_state.design.alignment`：true → **false**
- `workflow_state.design.approval`：true → **false**
- `recheck.upstream_change_pending`：false → **true**
- `recheck.impacted_downstream_phases`：[] → **["tasks"]**
- `workflow_state.tasks.alignment`：（本セッションで未コミット設定した true を）**false** に戻す（design 再承認後に再設定）

## 正本修正の対象（第2過程で実施）

- **evaluation/design.md 行517-527**：`analysis_run_manifest.yaml` の最低限記録項目を 13 項目に統一（共通5＋版管理4＋実行識別4）。実行識別4項目（analysis_run_id／analysis_started_at／analysis_completed_at／output_artifact_ids）を追加し、Req 5 受入 2（派生出力から実行識別子・対象識別子への連結保持）の根拠を manifest に明示
- **evaluation/tasks.md T-006 行105**：design の 13 項目に揃え、design 行517-527 への誤引用（tasks 側リストを design のものとして記載）を訂正
