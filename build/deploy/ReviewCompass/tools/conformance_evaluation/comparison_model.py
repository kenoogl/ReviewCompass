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

  @staticmethod
  def _code_ref(ref: str) -> dict:
    path, _, lines = ref.partition(":")
    return {"path": path, "lines": lines or "unknown"}

  def compare_one(self, *, criterion_id: str, existing: dict, inferred: dict) -> dict:
    criterion = criterion_by_id(criterion_id)
    mismatch_types = []
    correspondence_type = "claim_correspondence"
    if existing.get("section") != inferred.get("section"):
      mismatch_types.append("section_mismatch")
      correspondence_type = "section_existence"
    if existing.get("claim") != inferred.get("claim"):
      mismatch_types.append("claim_mismatch")
      correspondence_type = "claim_correspondence"
    if set(existing.get("code_refs") or []) != set(inferred.get("code_refs") or []):
      mismatch_types.append("code_reference_mismatch")
      correspondence_type = "code_reference_alignment"
    self.finding_counter += 1
    self.judgment_counter += 1
    existing_text = str(existing.get("claim") or existing.get("section") or "")
    estimated_text = str(inferred.get("claim") or inferred.get("section") or "")
    description = (
      f"{criterion.criterion_id} detected {', '.join(mismatch_types) or 'no mismatch'} "
      f"between existing and estimated documents."
    )
    return {
      "finding_id": self.format_next_id("CF", self.finding_counter),
      "judgment_id": self.format_next_id("JD", self.judgment_counter),
      "finding_type": "discrepancy" if mismatch_types else "no_discrepancy",
      "criterion_id": criterion.criterion_id,
      "axis": criterion.axis,
      "correspondence_type": correspondence_type,
      "severity": "WARN" if mismatch_types else "INFO",
      "existing_text": existing_text,
      "estimated_text": estimated_text,
      "discrepancy_description": description,
      "implementation_code_refs": [
        self._code_ref(ref) for ref in existing.get("code_refs") or inferred.get("code_refs") or []
      ],
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
