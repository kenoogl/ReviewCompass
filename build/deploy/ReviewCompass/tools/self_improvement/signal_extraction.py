"""Signal extraction for self-improvement workflow proposals."""
from pathlib import Path
from typing import Iterable, List, Mapping


SIGNAL_TYPES = (
  "discipline_absence",
  "discipline_violation",
  "discipline_obsolete",
  "discipline_conflict",
)

PROPOSAL_TYPE_BY_SIGNAL = {
  "discipline_absence": "new_discipline",
  "discipline_violation": "update",
  "discipline_obsolete": "archive",
  "discipline_conflict": "consolidation",
}


class SignalError(ValueError):
  """Raised when a signal cannot be trusted."""


def build_signal(
  *,
  signal_id: str,
  signal_type: str,
  observed_pattern: str,
  related_disciplines: Iterable[str],
  motivating_evidence_seed: Iterable[Mapping[str, object]],
) -> dict:
  related = list(related_disciplines)
  if signal_type not in SIGNAL_TYPES:
    raise SignalError(f"unknown_signal_type: {signal_type}")
  if signal_type in {"discipline_obsolete", "discipline_conflict"} and not related:
    raise SignalError("missing_related_disciplines")
  return {
    "signal_id": signal_id,
    "signal_type": signal_type,
    "observed_pattern": observed_pattern,
    "related_disciplines": related,
    "proposed_proposal_type": PROPOSAL_TYPE_BY_SIGNAL[signal_type],
    "motivating_evidence_seed": list(motivating_evidence_seed),
  }


class SignalExtractor:
  def __init__(self, *, violation_threshold: int = 3, obsolete_sessions_threshold: int = 5):
    self.violation_threshold = violation_threshold
    self.obsolete_sessions_threshold = obsolete_sessions_threshold

  @staticmethod
  def project_root() -> Path:
    return Path(__file__).resolve().parents[2]

  def extract(self, candidates: Iterable[Mapping[str, object]]) -> List[dict]:
    signals: List[dict] = []
    for candidate in candidates:
      signal_type = self._classify(candidate)
      if signal_type is None:
        continue
      signals.append(self._build_from_candidate(candidate, signal_type))
    return signals

  def _classify(self, candidate: Mapping[str, object]):
    conflicting_disciplines = list(candidate.get("conflicting_disciplines") or [])
    if len(conflicting_disciplines) >= 2:
      return "discipline_conflict"

    matching_discipline = candidate.get("matching_discipline")
    sessions_without_reference = int(candidate.get("sessions_without_reference") or 0)
    if matching_discipline and sessions_without_reference >= self.obsolete_sessions_threshold:
      return "discipline_obsolete"

    evidence_count = int(candidate.get("evidence_count") or 0)
    if matching_discipline and evidence_count >= self.violation_threshold:
      return "discipline_violation"
    if not matching_discipline and evidence_count > 0:
      return "discipline_absence"
    return None

  def _build_from_candidate(self, candidate: Mapping[str, object], signal_type: str) -> dict:
    related = self._related_disciplines(candidate, signal_type)
    return build_signal(
      signal_id=str(candidate["signal_id"]),
      signal_type=signal_type,
      observed_pattern=str(candidate["observed_pattern"]),
      related_disciplines=related,
      motivating_evidence_seed=list(candidate.get("motivating_evidence_seed") or []),
    )

  def _related_disciplines(self, candidate: Mapping[str, object], signal_type: str) -> List[str]:
    if signal_type == "discipline_conflict":
      return list(candidate.get("conflicting_disciplines") or [])
    if signal_type == "discipline_obsolete":
      return list(candidate.get("related_disciplines") or [])
    matching_discipline = candidate.get("matching_discipline")
    return [str(matching_discipline)] if matching_discipline else []
