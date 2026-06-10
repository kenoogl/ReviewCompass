"""レビューモード母集団規則。"""


class ModePopulationRule:
  """runtime_mediated を標準、それ以外を mode 別 slice とする。"""

  def slice(self, runs):
    standard = [
      run for run in runs
      if run.get("review_mode") == "runtime_mediated"
      and run.get("admission_status", "admitted_standard") == "admitted_standard"
    ]
    by_review_mode = {}
    for run in runs:
      mode = run.get("review_mode")
      if mode == "runtime_mediated":
        continue
      by_review_mode.setdefault(mode, []).append(run)
    return {
      "standard_runtime_mediated": standard,
      "by_review_mode": by_review_mode,
    }
