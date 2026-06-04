"""Comparison model for inferred and existing upstream documents."""
from tools.conformance_evaluation.criteria import criterion_by_id


class ComparisonModel:
  def __init__(self):
    self.finding_counter = 0
    self.judgment_counter = 0

  @staticmethod
  def format_next_id(prefix: str, number: int) -> str:
    width = 3 if number <= 999 else len(str(number))
    return f"{prefix}-{number:0{width}d}"

  def compare_one(self, *, criterion_id: str, existing: dict, inferred: dict) -> dict:
    criterion = criterion_by_id(criterion_id)
    mismatch_types = []
    if existing.get("section") != inferred.get("section"):
      mismatch_types.append("section_mismatch")
    if existing.get("claim") != inferred.get("claim"):
      mismatch_types.append("claim_mismatch")
    if set(existing.get("code_refs") or []) != set(inferred.get("code_refs") or []):
      mismatch_types.append("code_reference_mismatch")
    self.finding_counter += 1
    self.judgment_counter += 1
    return {
      "finding_id": self.format_next_id("CF", self.finding_counter),
      "judgment_id": self.format_next_id("JD", self.judgment_counter),
      "criterion_id": criterion.criterion_id,
      "axis": criterion.axis,
      "mismatch": bool(mismatch_types),
      "mismatch_types": mismatch_types,
    }

  def intent_difference(self, existing_intent: str, inferred_intent: str) -> dict:
    return {
      "reference_axis": "intent",
      "existing": existing_intent,
      "inferred": inferred_intent,
      "eligible_for_must_fix": False,
    }

