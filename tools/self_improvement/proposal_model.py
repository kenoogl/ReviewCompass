"""Proposal model for self-improvement workflow updates."""
import re
from pathlib import Path
from typing import Iterable, Mapping, Optional

import yaml


PROPOSAL_TYPES = (
  "new_discipline",
  "update",
  "status_change",
  "archive",
  "consolidation",
)
STATUS_VALUES = (
  "pending",
  "approved",
  "rejected",
  "superseded",
)
REQUIRED_FIELDS = (
  "proposal_id",
  "proposal_type",
  "target_discipline_path",
  "motivating_evidence",
  "proposed_change",
  "expected_effect",
  "status",
)
WORKFLOW_DIRECTORIES = (
  "proposals",
  "approved-updates",
  "rejected-updates",
  "rollback",
)
TARGET_DISCIPLINE_PATTERN = re.compile(r"^docs/disciplines/discipline_.*\.md$")
RELATED_DISCIPLINE_PATTERN = re.compile(r"^docs/disciplines/discipline_.*\.md$")
ID_PATTERN = re.compile(r"^(?P<prefix>[A-Z]+)-(?P<number>[0-9]+)$")


class ProposalError(ValueError):
  """Raised when a proposal cannot be trusted."""


def validate_proposal(proposal: Mapping[str, object]) -> None:
  missing = [field for field in REQUIRED_FIELDS if field not in proposal]
  if missing:
    raise ProposalError(f"missing_required_fields: {missing}")

  proposal_type = proposal["proposal_type"]
  if proposal_type not in PROPOSAL_TYPES:
    raise ProposalError(f"unknown_proposal_type: {proposal_type}")
  status = proposal["status"]
  if status not in STATUS_VALUES:
    raise ProposalError(f"unknown_status: {status}")
  target_path = str(proposal["target_discipline_path"])
  if not TARGET_DISCIPLINE_PATTERN.match(target_path):
    raise ProposalError(f"invalid_target_discipline_path: {target_path}")

  evidence = proposal["motivating_evidence"]
  if not isinstance(evidence, list) or not evidence:
    raise ProposalError("invalid_motivating_evidence")
  for item in evidence:
    if not isinstance(item, Mapping):
      raise ProposalError("invalid_motivating_evidence")
    if not {"source", "location", "observation"}.issubset(set(item)):
      raise ProposalError("invalid_motivating_evidence")

  _validate_type_specific(proposal_type, proposal)


def _validate_type_specific(proposal_type: str, proposal: Mapping[str, object]) -> None:
  proposed_change = proposal.get("proposed_change")
  if not isinstance(proposed_change, Mapping):
    raise ProposalError("invalid_proposed_change")

  if proposal_type == "new_discipline":
    if not proposed_change.get("draft_discipline"):
      raise ProposalError("missing_draft_discipline")
    if not proposed_change.get("relationship_notes"):
      raise ProposalError("missing_relationship_notes")
    related_disciplines = proposed_change.get("related_disciplines")
    if not isinstance(related_disciplines, list) or not related_disciplines:
      raise ProposalError("missing_related_disciplines")
    for path in related_disciplines:
      if not RELATED_DISCIPLINE_PATTERN.match(str(path)):
        raise ProposalError("invalid_related_disciplines")
  elif proposal_type == "update":
    if not proposed_change.get("change_diff"):
      raise ProposalError("missing_change_diff")
  elif proposal_type == "status_change":
    if not proposal.get("statistical_evidence"):
      raise ProposalError("missing_statistical_evidence")
  elif proposal_type == "archive":
    if not proposed_change.get("archive_readme_path"):
      raise ProposalError("missing_archive_readme_path")
  elif proposal_type == "consolidation":
    source_paths = proposal.get("source_discipline_paths")
    if not isinstance(source_paths, list) or not source_paths:
      raise ProposalError("missing_source_discipline_paths")
    if not proposed_change.get("mapping_table"):
      raise ProposalError("missing_mapping_table")


class ProposalModel:
  def __init__(self, root: Path):
    self.root = Path(root)

  @staticmethod
  def project_root() -> Path:
    return Path(__file__).resolve().parents[2]

  def create_proposal(
    self,
    *,
    proposal_type: str,
    target_discipline_path: str,
    signal: Mapping[str, object],
    proposed_change: Mapping[str, object],
    expected_effect: str,
    source_discipline_paths: Optional[Iterable[str]] = None,
    statistical_evidence: Optional[Mapping[str, object]] = None,
  ) -> dict:
    if proposal_type not in PROPOSAL_TYPES:
      raise ProposalError(f"unknown_proposal_type: {proposal_type}")

    proposal = {
      "proposal_id": self.next_proposal_id("WP"),
      "proposal_type": proposal_type,
      "target_discipline_path": target_discipline_path,
      "motivating_evidence": list(signal.get("motivating_evidence_seed") or []),
      "proposed_change": dict(proposed_change),
      "expected_effect": expected_effect,
      "status": "pending",
    }
    if source_discipline_paths is not None:
      proposal["source_discipline_paths"] = list(source_discipline_paths)
    if statistical_evidence is not None:
      proposal["statistical_evidence"] = dict(statistical_evidence)

    validate_proposal(proposal)
    return proposal

  def next_proposal_id(self, prefix: str) -> str:
    max_number = 0
    for proposal_id in self._iter_existing_ids():
      match = ID_PATTERN.match(proposal_id)
      if not match or match.group("prefix") != prefix:
        continue
      max_number = max(max_number, int(match.group("number")))
    next_number = max_number + 1
    width = 3 if next_number <= 999 else len(str(next_number))
    return f"{prefix}-{next_number:0{width}d}"

  def _iter_existing_ids(self):
    workflow_root = self.root / "learning" / "workflow"
    for directory in WORKFLOW_DIRECTORIES:
      for path in sorted((workflow_root / directory).glob("*.yaml")):
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        if isinstance(data, Mapping) and isinstance(data.get("proposal_id"), str):
          yield data["proposal_id"]
