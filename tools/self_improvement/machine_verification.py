"""Machine verification checks for self-improvement workflow safety."""
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Callable, Iterable, Mapping

import yaml

from tools.self_improvement.proposal_model import ProposalError, validate_proposal


class VerificationStatus(str, Enum):
  OK = "OK"
  DEVIATION = "DEVIATION"


@dataclass(frozen=True)
class VerificationResult:
  check_id: str
  status: VerificationStatus
  reasons: list
  details: dict

  def to_dict(self) -> dict:
    return {
      "check_id": self.check_id,
      "status": self.status.value,
      "reasons": self.reasons,
      "details": self.details,
    }


class MachineVerification:
  def __init__(self, root: Path = None):
    self.root = Path(root) if root is not None else Path.cwd()

  def check_direct_discipline_writes(
    self,
    *,
    changed_files: Iterable[str],
    actor_feature: str,
  ) -> VerificationResult:
    changed = list(changed_files)
    violations = [
      path for path in changed
      if actor_feature == "self-improvement"
      and path.startswith(".reviewcompass/guidance/discipline_")
      and path.endswith(".md")
    ]
    if violations:
      return VerificationResult(
        check_id="MV-1",
        status=VerificationStatus.DEVIATION,
        reasons=[f"self-improvement direct discipline write detected: {path}" for path in violations],
        details={"changed_files": changed},
      )
    return VerificationResult(
      check_id="MV-1",
      status=VerificationStatus.OK,
      reasons=[],
      details={"changed_files": changed},
    )

  def check_proposal_required_fields(self, proposal_paths: Iterable[Path]) -> VerificationResult:
    reasons = []
    checked_paths = []
    for path in proposal_paths:
      checked_paths.append(str(path))
      proposal = self._load_yaml(Path(path))
      try:
        validate_proposal(proposal)
      except ProposalError as exc:
        reasons.append(f"{path}: {exc}")
    return self._result("MV-2", reasons, {"checked_paths": checked_paths})

  def check_materialization_commit_hashes(
    self,
    proposal_paths: Iterable[Path],
    *,
    commit_exists: Callable[[str], bool],
  ) -> VerificationResult:
    reasons = []
    checked_hashes = []
    skipped_null_count = 0
    for path in proposal_paths:
      proposal = self._load_yaml(Path(path))
      commit_hash = proposal.get("materialization_commit_hash")
      if commit_hash in (None, ""):
        skipped_null_count += 1
        continue
      checked_hashes.append(commit_hash)
      if not commit_exists(str(commit_hash)):
        reasons.append(f"{path}: materialization_commit_hash not found: {commit_hash}")
    return self._result(
      "MV-3",
      reasons,
      {
        "checked_hashes": checked_hashes,
        "skipped_null_count": skipped_null_count,
      },
    )

  def check_superseded_fields(self, proposal_paths: Iterable[Path]) -> VerificationResult:
    reasons = []
    checked_paths = []
    for path in proposal_paths:
      proposal = self._load_yaml(Path(path))
      if proposal.get("status") != "superseded":
        continue
      checked_paths.append(str(path))
      missing = [
        field for field in ("superseded_by", "superseded_at", "reopen_reason")
        if not proposal.get(field)
      ]
      if missing:
        reasons.append(f"{path}: missing superseded fields: {', '.join(missing)}")
    return self._result("MV-4", reasons, {"checked_paths": checked_paths})

  def run_all(
    self,
    *,
    changed_files: Iterable[str],
    actor_feature: str,
    proposal_paths: Iterable[Path],
    metric_date: str,
    commit_exists: Callable[[str], bool],
  ) -> dict:
    proposal_path_list = list(proposal_paths)
    checks = [
      self.check_direct_discipline_writes(
        changed_files=changed_files,
        actor_feature=actor_feature,
      ),
      self.check_proposal_required_fields(proposal_path_list),
      self.check_materialization_commit_hashes(
        proposal_path_list,
        commit_exists=commit_exists,
      ),
      self.check_superseded_fields(proposal_path_list),
    ]
    verdict = (
      VerificationStatus.DEVIATION
      if any(check.status == VerificationStatus.DEVIATION for check in checks)
      else VerificationStatus.OK
    )
    summary = {
      "verdict": verdict.value,
      "checks": [check.to_dict() for check in checks],
    }
    self._write_metrics(metric_date, summary)
    return summary

  def _result(self, check_id: str, reasons: list, details: dict) -> VerificationResult:
    status = VerificationStatus.DEVIATION if reasons else VerificationStatus.OK
    return VerificationResult(
      check_id=check_id,
      status=status,
      reasons=reasons,
      details=details,
    )

  def _load_yaml(self, path: Path) -> dict:
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(data, Mapping):
      return {}
    return dict(data)

  def _write_metrics(self, metric_date: str, summary: dict) -> None:
    path = (
      self.root
      / "learning"
      / "workflow"
      / "metrics"
      / f"{metric_date}-machine-verification.yaml"
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
      yaml.safe_dump(summary, allow_unicode=True, sort_keys=False),
      encoding="utf-8",
    )
