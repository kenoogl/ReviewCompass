"""Approval model for workflow proposal state transitions."""
from pathlib import Path

import yaml


APPROVAL_WORDS = ("承認", "OK", "採用", "進めて", "はい")
ENFORCEMENT_APPROVAL_WORDS = ("正式化を承認", "enforced を承認", "enforced承認")
REJECTION_WORDS = ("却下", "不採用", "採用しない", "採用しません", "見送り")


class ApprovalError(ValueError):
  """Raised when an approval transition is not permitted."""


class ApprovalModel:
  def __init__(self, root: Path):
    self.root = Path(root)

  def approve(self, proposal_path: Path, *, approval_text: str) -> dict:
    proposal_path = Path(proposal_path)
    proposal = self._read(proposal_path)
    self._require_transition(proposal, "pending", "approved")
    self._require_approval(approval_text)
    if self._is_enforcement_status_change(proposal):
      self._require_enforcement_approval(approval_text)
    proposal["status"] = "approved"
    target = self.root / "learning" / "workflow" / "approved-updates" / proposal_path.name
    return self._write_transition(proposal_path, target, proposal, "pending", "approved")

  def reject(self, proposal_path: Path, *, approval_text: str) -> dict:
    proposal_path = Path(proposal_path)
    proposal = self._read(proposal_path)
    self._require_transition(proposal, "pending", "rejected")
    self._require_rejection(approval_text)
    proposal["status"] = "rejected"
    target = self.root / "learning" / "workflow" / "rejected-updates" / proposal_path.name
    return self._write_transition(proposal_path, target, proposal, "pending", "rejected")

  def supersede(
    self,
    proposal_path: Path,
    *,
    superseded_by: str,
    superseded_at: str,
    reopen_reason: str,
    approval_text: str,
    declaration: bool,
    new_conclusion: bool,
  ) -> dict:
    proposal_path = Path(proposal_path)
    proposal = self._read(proposal_path)
    self._require_transition(proposal, "approved", "superseded")
    self._require_approval(approval_text)
    if not all([declaration, new_conclusion, superseded_by, superseded_at, reopen_reason]):
      raise ApprovalError("missing_reopen_fields")
    proposal["status"] = "superseded"
    proposal["superseded_by"] = superseded_by
    proposal["superseded_at"] = superseded_at
    proposal["reopen_reason"] = reopen_reason
    self._write(proposal_path, proposal)
    return {
      "proposal_id": proposal["proposal_id"],
      "from_status": "approved",
      "to_status": "superseded",
      "source_path": self._relative(proposal_path),
      "target_path": self._relative(proposal_path),
      "move_operation": "none_status_only",
    }

  def _read(self, path: Path) -> dict:
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
      raise ApprovalError("proposal_must_be_mapping")
    return data

  def _write(self, path: Path, proposal: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
      yaml.safe_dump(proposal, allow_unicode=True, sort_keys=False),
      encoding="utf-8",
    )

  def _write_transition(
    self,
    source: Path,
    target: Path,
    proposal: dict,
    from_status: str,
    to_status: str,
  ) -> dict:
    self._write(target, proposal)
    if source != target and source.exists():
      source.unlink()
    return {
      "proposal_id": proposal["proposal_id"],
      "from_status": from_status,
      "to_status": to_status,
      "source_path": self._relative(source),
      "target_path": self._relative(target),
      "move_operation": "git_mv_required",
    }

  def _require_transition(self, proposal: dict, from_status: str, to_status: str) -> None:
    if proposal.get("status") != from_status:
      raise ApprovalError(
        f"invalid_transition: {proposal.get('status')} -> {to_status}"
      )

  def _require_approval(self, text: str) -> None:
    if any(word in text for word in REJECTION_WORDS):
      raise ApprovalError("explicit_user_approval_required")
    if not any(word in text for word in APPROVAL_WORDS):
      raise ApprovalError("explicit_user_approval_required")

  def _require_enforcement_approval(self, text: str) -> None:
    if not any(word in text for word in ENFORCEMENT_APPROVAL_WORDS):
      raise ApprovalError("explicit_enforcement_approval_required")

  def _require_rejection(self, text: str) -> None:
    if not any(word in text for word in REJECTION_WORDS):
      raise ApprovalError("explicit_user_rejection_required")

  def _is_enforcement_status_change(self, proposal: dict) -> bool:
    proposed_change = proposal.get("proposed_change") or {}
    return (
      proposal.get("proposal_type") == "status_change"
      and proposed_change.get("from") == "aspirational"
      and proposed_change.get("to") == "enforced"
    )

  def _relative(self, path: Path) -> str:
    return str(path.relative_to(self.root))
