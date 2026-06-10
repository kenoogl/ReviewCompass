"""mixed review mode detector."""
from collections import Counter


LIMITATION_TYPES = {
  "invalid_data_exclusion",
  "partial_evidence",
  "methodological_limitation",
  "mixed_review_mode",
}


def detect_mixed_review_mode(evidence_entries, *, caveat_id="mixed-review-mode"):
  """review_mode が 2 値以上なら mixed_review_mode caveat を返す。"""
  counts = Counter(entry["review_mode"] for entry in evidence_entries)
  if len(counts) < 2:
    return None
  modes = sorted(counts)
  summary = ", ".join(f"{mode}: {counts[mode]}" for mode in modes)
  return {
    "caveat_id": caveat_id,
    "limitation_type": "mixed_review_mode",
    "narrative_note": f"review_mode values are mixed in this report set: {summary}",
    "review_modes": modes,
    "applies_to_artifact_refs": [
      {
        "ref_type": "evidence_entry",
        "target_path": "shared/evidence_register.json",
        "target_id": entry["evidence_id"],
      }
      for entry in evidence_entries
    ],
  }

