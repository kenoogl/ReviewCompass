"""decision_unit_updater（決定単位への人間決定付加）（runtime tasks.md T-007）。

T-005 が生成した decisions/decision_units.json の各決定単位に、人間決定（承認・却下・保留）を
付加する。決定単位の生成自体は T-005 に集約し、本モジュールは付加のみを担う。
人間決定の不在（None）と明示的な保留／却下を機械的に区別する（要件 5 受入 3）。

対応設計節：design.md §決定単位モデル
対応要件：Requirement 5（人間決定の組み込み）
"""
import json
from pathlib import Path

from ..foundation_ref import vocabulary

# 明示的な人間決定値は foundation human_signoff_status 4 値正本のうち pending を除く 3 値を参照する。
# pending（＝不在）は human_decision=None で表し、明示保留（deferred）／却下（rejected）と区別する。
_EXPLICIT_DECISIONS = set(vocabulary("human_signoff_status")) - {"pending"}


class InvalidHumanDecision(Exception):
  """foundation 4 値に基づかない人間決定値を検出した違反（再定義禁止）。"""


class DecisionUnitUpdater:
  """decision_units.json の決定単位に人間決定を付加する。"""

  def __init__(self, run_dir):
    self.path = Path(run_dir) / "decisions" / "decision_units.json"

  def apply_decision(self, decision_unit_id, *, human_decision, timestamp, note=""):
    """指定した決定単位に人間決定を付加する。

    human_decision は foundation 由来の明示値（approved／rejected／deferred）に限る。
    """
    if human_decision not in _EXPLICIT_DECISIONS:
      raise InvalidHumanDecision(
        f"人間決定値は foundation 4 値正本の明示値 {sorted(_EXPLICIT_DECISIONS)} から："
        f"{human_decision!r}"
      )
    data = json.loads(self.path.read_text(encoding="utf-8"))
    for unit in data["decision_units"]:
      if unit["decision_unit_id"] == decision_unit_id:
        unit["human_decision"] = human_decision
        unit["human_decision_timestamp"] = timestamp
        unit["human_decision_note"] = note
        self.path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        return unit
    raise KeyError(f"決定単位が見つからない：{decision_unit_id!r}")
