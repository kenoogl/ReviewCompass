"""Interfaces between self-improvement and adjacent features."""
import json
from pathlib import Path

import yaml

from tools.self_improvement.effect_measurement import EffectMeasurement


def foundation_reference_contract() -> dict:
  return {
    "discipline_check_schema": "foundation",
    "review_mode_vocabulary": "foundation",
    "state_axis_vocabulary": "foundation",
    "policy": "reference_only_no_redefinition",
  }


def assert_commit_fields_are_independent(
  *,
  target_commit: str,
  materialization_commit_hash: str,
) -> dict:
  return {
    "target_commit_owner": "conformance-evaluation",
    "materialization_commit_hash_owner": "self-improvement",
    "independent": target_commit != materialization_commit_hash,
  }


class InterfaceAdapter:
  def __init__(self, root: Path):
    self.root = Path(root)

  @staticmethod
  def project_root() -> Path:
    return Path(__file__).resolve().parents[2]

  def read_evaluation_role_diff_report(self, report_path: Path) -> dict:
    return json.loads(Path(report_path).read_text(encoding="utf-8"))

  def write_analysis_metrics(self, *, metric_date: str) -> Path:
    return EffectMeasurement(self.root).write_metrics(metric_date=metric_date)

  def workflow_management_input_contract(self, proposal_path: Path) -> dict:
    proposal_path = Path(proposal_path)
    proposal = yaml.safe_load(proposal_path.read_text(encoding="utf-8")) or {}
    target = (
      self.root
      / "learning"
      / "workflow"
      / "approved-updates"
      / proposal_path.name
    )
    return {
      "proposal_id": proposal["proposal_id"],
      "approved_state_owner": "self-improvement",
      "materialization_owner": "workflow-management",
      "source_path": self._relative(proposal_path),
      "approved_updates_path": self._relative(target),
      "move_operation": "git_mv_required",
      "approved_means": "self_improvement_approval_time",
      "materialized_at_means": "workflow_management_completion_time",
    }

  def _relative(self, path: Path) -> str:
    return str(path.relative_to(self.root))
