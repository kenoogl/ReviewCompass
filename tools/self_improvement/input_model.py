"""Input model for self-improvement workflow observations."""
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Mapping, Optional

import yaml


SOURCE_VALUES = (
  "review_record",
  "compliance_report",
  "user_audit",
  "observation_pattern",
)
MIN_OBSERVATION_LENGTH = 30


class ProvenanceError(ValueError):
  """Raised when provenance cannot be trusted."""


@dataclass(frozen=True)
class InputRecord:
  provenance: Mapping[str, str]
  payload: Mapping[str, object]


def build_provenance(*, source: str, location: str, observation: str) -> dict:
  if source not in SOURCE_VALUES:
    raise ProvenanceError(f"unknown_source: {source}")
  if len(observation) < MIN_OBSERVATION_LENGTH:
    raise ProvenanceError("short_observation")
  if not location:
    raise ProvenanceError("missing_location")
  return {
    "source": source,
    "location": location,
    "observation": observation,
  }


class InputModel:
  def __init__(self, root: Path):
    self.root = Path(root)

  @staticmethod
  def project_root() -> Path:
    return Path(__file__).resolve().parents[2]

  def load_sources(
    self,
    *,
    review_records: Iterable[Path],
    compliance_reports_dir: Optional[Path],
    user_audits: Iterable[Path],
    observation_patterns: Iterable[Path],
  ) -> List[InputRecord]:
    records: List[InputRecord] = []
    records.extend(self.load_files(review_records, source="review_record"))
    if compliance_reports_dir is not None:
      records.extend(self.load_compliance_reports(compliance_reports_dir))
    records.extend(self.load_files(user_audits, source="user_audit"))
    records.extend(self.load_files(observation_patterns, source="observation_pattern"))
    return records

  def load_compliance_reports(self, reports_dir: Path) -> List[InputRecord]:
    report_paths = sorted(Path(reports_dir).glob("*.yaml"))
    return self.load_files(report_paths, source="compliance_report")

  def load_files(self, paths: Iterable[Path], *, source: str) -> List[InputRecord]:
    records: List[InputRecord] = []
    for path in paths:
      records.extend(self._load_file(Path(path), source=source))
    return records

  def _load_file(self, path: Path, *, source: str) -> List[InputRecord]:
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    entries = data.get("records", [])
    if not isinstance(entries, list):
      raise ProvenanceError(f"records_must_be_list: {path}")
    return [self._record_from_entry(entry, source=source) for entry in entries]

  def _record_from_entry(self, entry: Mapping[str, object], *, source: str) -> InputRecord:
    if not isinstance(entry, Mapping):
      raise ProvenanceError("record_must_be_mapping")
    location = str(entry.get("location") or "")
    observation = str(entry.get("observation") or "")
    provenance = build_provenance(
      source=source,
      location=location,
      observation=observation,
    )
    return InputRecord(provenance=provenance, payload=dict(entry))
