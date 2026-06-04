"""Effect measurement for workflow improvement proposals."""
from datetime import date, datetime
from pathlib import Path
from typing import Mapping

import yaml


PROPOSAL_DIRECTORIES = (
  "proposals",
  "approved-updates",
  "rejected-updates",
)
PROPOSAL_TYPES = (
  "new_discipline",
  "update",
  "status_change",
  "archive",
  "consolidation",
)


class EffectMeasurement:
  def __init__(self, root: Path):
    self.root = Path(root)

  @staticmethod
  def project_root() -> Path:
    return Path(__file__).resolve().parents[2]

  @staticmethod
  def manual_aggregation_steps() -> list:
    return [
      {"id": "find_wc", "description": "find と wc で対象 YAML 件数を数える"},
      {"id": "grep_sort_uniq", "description": "grep、sort、uniq で種別と状態を集計する"},
      {"id": "adoption_rate_calculation", "description": "approved、rejected、superseded から採用率を算出する"},
      {"id": "metrics_record", "description": "learning/workflow/metrics/<日付>.yaml に記録する"},
    ]

  def calculate_metrics(self, *, metric_date: str) -> dict:
    proposals = self._load_proposals()
    rollback_count = len(self._load_rollbacks())
    approved_count = self._count_status(proposals, "approved")
    rejected_count = self._count_status(proposals, "rejected")
    superseded_count = self._count_status(proposals, "superseded")
    adoption_denominator = approved_count + rejected_count + superseded_count
    adoption_rate = (
      (approved_count + superseded_count) / adoption_denominator
      if adoption_denominator
      else 0.0
    )
    rollback_rate = rollback_count / approved_count if approved_count else 0.0

    metrics = {
      "metric_date": metric_date,
      "discipline_compliance_rate": self._discipline_compliance_rate(),
      "promotion_count": self._promotion_count(proposals),
      "archive_count": self._archive_count(proposals),
      "proposal_counts_by_type": self._proposal_counts_by_type(proposals),
      "adoption_rate": adoption_rate,
      "adoption_rate_formula": "(approved + superseded) / (approved + rejected + superseded)",
      "rollback_rate": rollback_rate,
      "average_days_to_adoption": self._average_days_to_adoption(proposals),
      "manual_aggregation_steps": self.manual_aggregation_steps(),
    }
    return metrics

  def write_metrics(self, *, metric_date: str = None) -> Path:
    metric_date = metric_date or date.today().isoformat()
    metrics = self.calculate_metrics(metric_date=metric_date)
    metrics["manual_aggregation_steps"] = [
      step["id"] for step in self.manual_aggregation_steps()
    ]
    path = self.root / "learning" / "workflow" / "metrics" / f"{metric_date}.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
      yaml.safe_dump(metrics, allow_unicode=True, sort_keys=False),
      encoding="utf-8",
    )
    return path

  def _load_proposals(self) -> list:
    proposals = []
    workflow_root = self.root / "learning" / "workflow"
    for directory in PROPOSAL_DIRECTORIES:
      for path in sorted((workflow_root / directory).glob("*.yaml")):
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        if isinstance(data, Mapping):
          proposals.append(dict(data))
    return proposals

  def _load_rollbacks(self) -> list:
    rollback_root = self.root / "learning" / "workflow" / "rollback"
    rollbacks = []
    for path in sorted(rollback_root.glob("*.yaml")):
      data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
      if isinstance(data, Mapping):
        rollbacks.append(dict(data))
    return rollbacks

  def _discipline_compliance_rate(self) -> float:
    checked = 0
    violations = 0
    report_root = self.root / "docs" / "discipline-compliance-reports"
    for path in sorted(report_root.glob("*.yaml")):
      data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
      if not isinstance(data, Mapping):
        continue
      checked += int(data.get("checked_count") or 0)
      violations += int(data.get("violation_count") or 0)
    if checked == 0:
      return 0.0
    return (checked - violations) / checked

  def _promotion_count(self, proposals: list) -> int:
    return sum(
      1
      for proposal in proposals
      if proposal.get("status") == "approved"
      and proposal.get("proposal_type") == "status_change"
      and (proposal.get("proposed_change") or {}).get("from") == "aspirational"
      and (proposal.get("proposed_change") or {}).get("to") == "enforced"
    )

  def _archive_count(self, proposals: list) -> int:
    return sum(
      1
      for proposal in proposals
      if proposal.get("proposal_type") == "archive"
      and proposal.get("status") in ("approved", "superseded")
    )

  def _proposal_counts_by_type(self, proposals: list) -> dict:
    counts = {}
    for proposal in proposals:
      proposal_type = proposal.get("proposal_type")
      if proposal_type in PROPOSAL_TYPES:
        counts[proposal_type] = counts.get(proposal_type, 0) + 1
    return dict(sorted(counts.items()))

  def _count_status(self, proposals: list, status: str) -> int:
    return sum(1 for proposal in proposals if proposal.get("status") == status)

  def _average_days_to_adoption(self, proposals: list) -> float:
    durations = []
    for proposal in proposals:
      if proposal.get("status") not in ("approved", "superseded"):
        continue
      submitted_at = proposal.get("submitted_at")
      materialized_at = proposal.get("materialized_at")
      if not submitted_at or not materialized_at:
        continue
      durations.append(
        (self._iso_date(materialized_at) - self._iso_date(submitted_at)).days
      )
    return sum(durations) / len(durations) if durations else 0.0

  def _iso_date(self, value: str) -> date:
    text = str(value)
    if text.endswith("Z"):
      text = f"{text[:-1]}+00:00"
    if "T" in text:
      return datetime.fromisoformat(text).date()
    return date.fromisoformat(text)
