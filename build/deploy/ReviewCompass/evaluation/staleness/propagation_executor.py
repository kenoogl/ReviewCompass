"""陳腐化伝播履行器。"""


class PropagationExecutor:
  """陳腐化フラグ付けまたは再導出の履行結果を返す。"""

  def execute(self, *, invalidated_run_ids, affected_artifact_ids, action):
    statuses = {
      "flag_stale": "stale_flagged",
      "rederive": "rederived",
    }
    return {
      "status": statuses[action],
      "action": action,
      "invalidated_run_ids": invalidated_run_ids,
      "affected_artifact_ids": affected_artifact_ids,
    }
