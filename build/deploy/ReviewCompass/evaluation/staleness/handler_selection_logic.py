"""陳腐化伝播履行手段の選択ロジック。"""
from dataclasses import dataclass


@dataclass(frozen=True)
class HandlerSelection:
  """陳腐化伝播履行手段の選択結果。"""

  action: str
  reason_code: str


class HandlerSelectionLogic:
  """初版の履行手段選択ロジック。"""

  def __init__(self, rederive_threshold=0.05):
    self.rederive_threshold = rederive_threshold

  def select(self, *, invalidated_run_count, standard_run_count, exploratory_only):
    if exploratory_only:
      return HandlerSelection(action="flag_stale", reason_code="exploratory_only")
    if standard_run_count == 0:
      return HandlerSelection(action="flag_stale", reason_code="no_standard_population")
    ratio = invalidated_run_count / standard_run_count
    if ratio >= self.rederive_threshold:
      return HandlerSelection(action="rederive", reason_code="large_standard_impact")
    return HandlerSelection(action="flag_stale", reason_code="small_standard_impact")
