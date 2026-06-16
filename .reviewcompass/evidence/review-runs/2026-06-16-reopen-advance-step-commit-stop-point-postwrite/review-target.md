diff --git a/docs/operations/WORKFLOW_PRECHECK_DETAILS.md b/docs/operations/WORKFLOW_PRECHECK_DETAILS.md
index 3b58df72..95a138d1 100644
--- a/docs/operations/WORKFLOW_PRECHECK_DETAILS.md
+++ b/docs/operations/WORKFLOW_PRECHECK_DETAILS.md
@@ -156,7 +156,7 @@ tools/guarded-git-commit.py -m "<commit message>" --rationale "<理由>"
 - `completed_steps` に `--completed-step` を追記する
 - `reopen_step_records` に `from_step`、`completed_step`、`rationale`、`evidence` を追記する
 - `--from-step 1` の成功時は `step_number: 2`、`next_step: 第2過程：正本修正`、`current_blocker: null` を保存する
-- `--from-step 2` の成功時は `step_number: 2`、`next_step: 第2過程：停止点コミット`、`current_blocker: 第2過程の停止点としてコミットが必要` を保存する
+- `--from-step 2` の成功時は `step_number: 2`、`next_step: 第2過程：停止点コミット`、`current_blocker: null`、`commit_stop_point: true`、`commit_stop_point_reason: 第2過程の正本修正完了` を保存する
 - 成功時は exit 0、上記の前提違反や入力不正は DEVIATION として exit 2 を返す
 
 <a id="reopen-advance-gate"></a>
