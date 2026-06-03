"""有効母集団規則。"""


class ValidPopulationRule:
  """標準比較母集団に valid 実行のみを含める。"""

  def apply(self, runs):
    return [run for run in runs if run.get("classification") == "valid"]
