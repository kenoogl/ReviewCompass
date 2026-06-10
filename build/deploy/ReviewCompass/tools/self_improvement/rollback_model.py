"""Rollback history model for workflow improvement proposals."""
import re
from pathlib import Path
from typing import Mapping

import yaml

from tools.self_improvement.impact_analysis import INTERNAL_LINK_PATTERN


ROLLBACK_METHODS = (
  "archive_restoration",
  "status_downgrade",
  "git_revert",
)
REQUIRED_FIELDS = (
  "rollback_id",
  "target_proposal_id",
  "rollback_method",
  "rollback_reason",
  "rollback_date",
  "related_artifacts",
)
RB_PATTERN = re.compile(r"^RB-(?P<number>[0-9]+)$")
ROLLBACK_ID_DIRECTORIES = (
  "proposals",
  "approved-updates",
  "rejected-updates",
  "rollback",
)


class RollbackError(ValueError):
  """Raised when a rollback record cannot be trusted."""


def validate_rollback_record(record: Mapping[str, object]) -> None:
  missing = [field for field in REQUIRED_FIELDS if field not in record]
  if missing:
    raise RollbackError(f"missing_required_fields: {missing}")
  method = record["rollback_method"]
  if method not in ROLLBACK_METHODS:
    raise RollbackError(f"unknown_rollback_method: {method}")
  if not isinstance(record["related_artifacts"], list):
    raise RollbackError("related_artifacts_must_be_list")


class RollbackModel:
  def __init__(self, root: Path):
    self.root = Path(root)

  @staticmethod
  def project_root() -> Path:
    return Path(__file__).resolve().parents[2]

  def create_rollback_record(
    self,
    *,
    target_proposal_id: str,
    rollback_method: str,
    rollback_reason: str,
    rollback_date: str,
    related_artifacts: list,
  ) -> dict:
    record = {
      "rollback_id": self.next_rollback_id(),
      "target_proposal_id": target_proposal_id,
      "rollback_method": rollback_method,
      "rollback_reason": rollback_reason,
      "rollback_date": rollback_date,
      "related_artifacts": list(related_artifacts),
    }
    validate_rollback_record(record)
    path = (
      self.root
      / "learning"
      / "workflow"
      / "rollback"
      / f"{rollback_date}-{record['rollback_id']}.yaml"
    )
    self._write_yaml(path, record)
    return record

  def next_rollback_id(self) -> str:
    max_number = 0
    workflow_root = self.root / "learning" / "workflow"
    for directory in ROLLBACK_ID_DIRECTORIES:
      for path in sorted((workflow_root / directory).glob("*.yaml")):
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        if not isinstance(data, Mapping):
          continue
        rollback_id = self._rollback_identifier(data)
        match = RB_PATTERN.match(rollback_id)
        if match:
          max_number = max(max_number, int(match.group("number")))
    next_number = max_number + 1
    width = 3 if next_number <= 999 else len(str(next_number))
    return f"RB-{next_number:0{width}d}"

  def symlink_recreation_plan(self, *, memory_link: str, repo_target: str) -> dict:
    checks = [
      "confirm_memory_link_path",
      "confirm_repo_target_exists",
      "remove_stale_link_if_needed",
      "create_symbolic_link",
      "verify_link_resolves_to_repo_target",
    ]
    return {
      "memory_link": memory_link,
      "repo_target": repo_target,
      "steps": [
        {
          "step": index,
          "action": action,
          "machine_check": True,
        }
        for index, action in enumerate(checks, start=1)
      ],
    }

  def trace_history(self, proposal_id: str) -> dict:
    proposal = self._find_proposal(proposal_id)
    rollbacks = []
    rollback_root = self.root / "learning" / "workflow" / "rollback"
    for path in sorted(rollback_root.glob("*.yaml")):
      data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
      if isinstance(data, Mapping) and data.get("target_proposal_id") == proposal_id:
        rollbacks.append({
          "path": self._relative(path),
          "rollback_id": data.get("rollback_id"),
          "rollback_method": data.get("rollback_method"),
        })
    return {
      "proposal": proposal,
      "rollbacks": rollbacks,
    }

  def check_archive_restoration_integrity(
    self,
    *,
    restored_discipline_path: str,
    archive_readme_path: str,
    report_date: str,
  ) -> dict:
    restored_path = self.root / restored_discipline_path
    archive_path = self.root / archive_readme_path
    text = restored_path.read_text(encoding="utf-8")
    metadata = self._front_matter(text)
    links = INTERNAL_LINK_PATTERN.findall(text)
    archive_text = archive_path.read_text(encoding="utf-8") if archive_path.exists() else ""
    result = {
      "check": "archive_restoration_integrity",
      "restored_discipline_path": restored_discipline_path,
      "archive_readme_path": archive_readme_path,
      "front_matter_valid": all(metadata.get(field) for field in ("name", "status")),
      "internal_links": links,
      "archive_readme_consistent": metadata.get("name", "") in archive_text,
    }
    report_path = (
      self.root
      / "docs"
      / "discipline-compliance-reports"
      / f"{report_date}-rollback.yaml"
    )
    self._write_yaml(report_path, result)
    return result

  def _find_proposal(self, proposal_id: str) -> dict:
    for directory in ("proposals", "approved-updates", "rejected-updates"):
      root = self.root / "learning" / "workflow" / directory
      for path in sorted(root.glob("*.yaml")):
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        if isinstance(data, Mapping) and data.get("proposal_id") == proposal_id:
          return {
            "path": self._relative(path),
            "status": data.get("status"),
          }
    raise RollbackError(f"proposal_not_found: {proposal_id}")

  def _front_matter(self, text: str) -> dict:
    if not text.startswith("---"):
      return {}
    parts = text.split("---", 2)
    if len(parts) < 3:
      return {}
    data = yaml.safe_load(parts[1]) or {}
    return data if isinstance(data, dict) else {}

  def _write_yaml(self, path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
      yaml.safe_dump(data, allow_unicode=True, sort_keys=False),
      encoding="utf-8",
    )

  def _rollback_identifier(self, data: Mapping[str, object]) -> str:
    rollback_id = str(data.get("rollback_id", ""))
    if RB_PATTERN.match(rollback_id):
      return rollback_id
    return str(data.get("proposal_id", ""))

  def _relative(self, path: Path) -> str:
    return str(path.relative_to(self.root))
