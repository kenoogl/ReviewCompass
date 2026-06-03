"""比較セット内の版整合性検査。"""
from dataclasses import dataclass


@dataclass(frozen=True)
class VersionConsistencyResult:
  """版整合性検査結果。"""

  ok: bool
  reason_codes: list


class VersionConsistencyValidator:
  """protocol_version / prompt_set_version の混在を検出する。"""

  def validate(self, runs):
    reason_codes = []
    if len({run.get("protocol_version") for run in runs}) > 1:
      reason_codes.append("mixed_protocol_version")
    if len({run.get("prompt_set_version") for run in runs}) > 1:
      reason_codes.append("mixed_prompt_set_version")
    return VersionConsistencyResult(ok=not reason_codes, reason_codes=reason_codes)
