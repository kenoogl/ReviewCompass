"""Comparison model for inferred and existing upstream documents."""
import re
from pathlib import Path

from tools.conformance_evaluation.criteria import criterion_by_id
from tools.conformance_evaluation.evaluation_record import (
  conformance_dir,
  legacy_conformance_dir,
)


class ComparisonModel:
  def __init__(self):
    self.finding_counter = 0
    self.judgment_counter = 0

  @classmethod
  def for_feature(cls, root: Path, feature: str) -> "ComparisonModel":
    """既存記録の最大番号から採番を継続する（design §10.7）。

    凍結期（P3 まで）は新配置と凍結された旧配置を合算した走査範囲で
    最大番号を統合算出し、旧凍結記録との ID 重複・リセットを防ぐ。
    """
    model = cls()
    scan_roots = {
      conformance_dir(root, feature),
      legacy_conformance_dir(root, feature),
    }
    for scan_root in scan_roots:
      if not scan_root.is_dir():
        continue
      for path in scan_root.rglob("*"):
        if not path.is_file():
          continue
        try:
          text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
          continue
        for match in re.finditer(r"\bCF-(\d+)\b", text):
          model.finding_counter = max(model.finding_counter, int(match.group(1)))
        for match in re.finditer(r"\bJD-(\d+)\b", text):
          model.judgment_counter = max(model.judgment_counter, int(match.group(1)))
    return model

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
