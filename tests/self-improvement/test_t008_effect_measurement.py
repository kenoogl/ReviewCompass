"""T-008 のテスト：効果測定モデル。

対応タスク：self-improvement tasks.md T-008
対応設計節：design.md §12.1〜§12.6
対応要件：Requirement 8 受入 1〜5
"""
import json
from pathlib import Path

import yaml

from tools.self_improvement.effect_measurement import EffectMeasurement


def _write_yaml(path, data):
  path.parent.mkdir(parents=True, exist_ok=True)
  path.write_text(
    yaml.safe_dump(data, allow_unicode=True, sort_keys=False),
    encoding="utf-8",
  )


def _proposal(proposal_id, proposal_type, status, **extra):
  proposal = {
    "proposal_id": proposal_id,
    "proposal_type": proposal_type,
    "status": status,
  }
  proposal.update(extra)
  return proposal


def test_t008_calculates_all_seven_metrics(tmp_path):
  _write_yaml(
    tmp_path / "docs" / "discipline-compliance-reports" / "2026-06-04.yaml",
    {"checked_count": 10, "violation_count": 2},
  )
  _write_yaml(
    tmp_path / "learning" / "workflow" / "approved-updates" / "WP-001.yaml",
    _proposal(
      "WP-001",
      "status_change",
      "approved",
      proposed_change={"from": "aspirational", "to": "enforced"},
      submitted_at="2026-06-01",
      materialized_at="2026-06-04T00:00:00+09:00",
    ),
  )
  _write_yaml(
    tmp_path / "learning" / "workflow" / "approved-updates" / "WP-002.yaml",
    _proposal("WP-002", "archive", "superseded", submitted_at="2026-06-02", materialized_at="2026-06-04T00:00:00+09:00"),
  )
  _write_yaml(
    tmp_path / "learning" / "workflow" / "rejected-updates" / "WP-003.yaml",
    _proposal("WP-003", "update", "rejected"),
  )
  _write_yaml(
    tmp_path / "learning" / "workflow" / "proposals" / "WP-004.yaml",
    _proposal("WP-004", "new_discipline", "pending"),
  )
  _write_yaml(
    tmp_path / "learning" / "workflow" / "rollback" / "2026-06-04-RB-001.yaml",
    {"rollback_id": "RB-001", "target_proposal_id": "WP-001"},
  )

  metrics = EffectMeasurement(tmp_path).calculate_metrics(metric_date="2026-06-04")

  assert metrics["metric_date"] == "2026-06-04"
  assert metrics["discipline_compliance_rate"] == 0.8
  assert metrics["promotion_count"] == 1
  assert metrics["archive_count"] == 1
  assert metrics["proposal_counts_by_type"] == {
    "archive": 1,
    "new_discipline": 1,
    "status_change": 1,
    "update": 1,
  }
  assert metrics["adoption_rate"] == 2 / 3
  assert metrics["rollback_rate"] == 1.0
  assert metrics["average_days_to_adoption"] == 2.5


def test_t008_average_days_to_adoption_uses_materialized_at_not_approved_at(tmp_path):
  _write_yaml(
    tmp_path / "learning" / "workflow" / "approved-updates" / "WP-001.yaml",
    _proposal(
      "WP-001",
      "update",
      "approved",
      submitted_at="2026-06-01",
      materialized_at="2026-06-05T12:00:00+09:00",
    ),
  )

  metrics = EffectMeasurement(tmp_path).calculate_metrics(metric_date="2026-06-04")

  assert metrics["average_days_to_adoption"] == 4.0


def test_t008_adoption_rate_counts_superseded_as_adopted_and_excludes_pending(tmp_path):
  proposals = [
    ("approved-updates", "WP-001", "update", "approved"),
    ("approved-updates", "WP-002", "update", "superseded"),
    ("rejected-updates", "WP-003", "update", "rejected"),
    ("proposals", "WP-004", "update", "pending"),
  ]
  for directory, proposal_id, proposal_type, status in proposals:
    _write_yaml(
      tmp_path / "learning" / "workflow" / directory / f"{proposal_id}.yaml",
      _proposal(proposal_id, proposal_type, status),
    )

  metrics = EffectMeasurement(tmp_path).calculate_metrics(metric_date="2026-06-04")

  assert metrics["adoption_rate"] == 2 / 3
  assert metrics["adoption_rate_formula"] == "(approved + superseded) / (approved + rejected + superseded)"


def test_t008_rollback_rate_uses_approved_count(tmp_path):
  for proposal_id in ["WP-001", "WP-002"]:
    _write_yaml(
      tmp_path / "learning" / "workflow" / "approved-updates" / f"{proposal_id}.yaml",
      _proposal(proposal_id, "update", "approved"),
    )
  _write_yaml(
    tmp_path / "learning" / "workflow" / "rollback" / "2026-06-04-RB-001.yaml",
    {"rollback_id": "RB-001", "target_proposal_id": "WP-001"},
  )

  metrics = EffectMeasurement(tmp_path).calculate_metrics(metric_date="2026-06-04")

  assert metrics["rollback_rate"] == 0.5


def test_t008_writes_metrics_as_time_series_yaml(tmp_path):
  path = EffectMeasurement(tmp_path).write_metrics(metric_date="2026-06-04")

  assert path == tmp_path / "learning" / "workflow" / "metrics" / "2026-06-04.yaml"
  data = yaml.safe_load(path.read_text(encoding="utf-8"))
  assert data["metric_date"] == "2026-06-04"
  assert set(data["manual_aggregation_steps"]) == {
    "find_wc",
    "grep_sort_uniq",
    "adoption_rate_calculation",
    "metrics_record",
  }


def test_t008_manual_aggregation_steps_are_reproducible():
  steps = EffectMeasurement.manual_aggregation_steps()

  assert steps == [
    {"id": "find_wc", "description": "find と wc で対象 YAML 件数を数える"},
    {"id": "grep_sort_uniq", "description": "grep、sort、uniq で種別と状態を集計する"},
    {"id": "adoption_rate_calculation", "description": "approved、rejected、superseded から採用率を算出する"},
    {"id": "metrics_record", "description": "learning/workflow/metrics/<日付>.yaml に記録する"},
  ]


def test_t008_metrics_schema_documents_owned_constraints():
  schema = json.loads(
    (EffectMeasurement.project_root() / "learning" / "workflow" / "schemas" / "metrics.schema.json")
    .read_text(encoding="utf-8")
  )

  assert schema["required"] == [
    "metric_date",
    "discipline_compliance_rate",
    "promotion_count",
    "archive_count",
    "proposal_counts_by_type",
    "adoption_rate",
    "rollback_rate",
    "average_days_to_adoption",
    "manual_aggregation_steps",
  ]
