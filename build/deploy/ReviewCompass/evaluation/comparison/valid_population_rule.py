"""有効母集団規則。"""


class ValidPopulationRule:
  """標準比較母集団に valid かつ標準許容の実行のみを含める。"""

  def apply(self, runs):
    return [
      run for run in runs
      if run.get("classification") == "valid"
      and run.get("admission_status", "admitted_standard") == "admitted_standard"
    ]
