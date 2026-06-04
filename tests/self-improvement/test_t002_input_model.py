"""T-002 のテスト：入力モデルと来歴情報。

対応タスク：self-improvement tasks.md T-002
対応設計節：design.md §6.1〜§6.4
対応要件：Requirement 2 受入 1〜4
"""
import json

import pytest
import yaml

from tools.self_improvement.input_model import (
  InputModel,
  ProvenanceError,
  build_provenance,
)


LONG_OBSERVATION = "規律違反の観察内容が十分な長さで記録され、原因と場面を後から追跡できる"


def _write_yaml(path, data):
  path.parent.mkdir(parents=True, exist_ok=True)
  path.write_text(
    yaml.safe_dump(data, allow_unicode=True, sort_keys=False),
    encoding="utf-8",
  )


def test_t002_builds_provenance_with_required_three_fields():
  provenance = build_provenance(
    source="review_record",
    location="reviews/2026-06-04-review.yaml",
    observation=LONG_OBSERVATION,
  )

  assert provenance == {
    "source": "review_record",
    "location": "reviews/2026-06-04-review.yaml",
    "observation": LONG_OBSERVATION,
  }


def test_t002_rejects_unknown_source_fail_closed():
  with pytest.raises(ProvenanceError, match="unknown_source"):
    build_provenance(
      source="runtime_report",
      location="reports/runtime.yaml",
      observation=LONG_OBSERVATION,
    )


def test_t002_rejects_short_observation_fail_closed():
  with pytest.raises(ProvenanceError, match="short_observation"):
    build_provenance(
      source="user_audit",
      location="audits/user.md",
      observation="短すぎる観察",
    )


def test_t002_loads_all_five_input_sources_with_provenance(tmp_path):
  _write_yaml(
    tmp_path / "reviews" / "review.yaml",
    {"records": [{"location": "reviews/review.yaml", "observation": LONG_OBSERVATION}]},
  )
  _write_yaml(
    tmp_path / "docs" / "discipline-compliance-reports" / "2026-06-03.yaml",
    {"records": [{"location": "docs/discipline-compliance-reports/2026-06-03.yaml", "observation": LONG_OBSERVATION}]},
  )
  _write_yaml(
    tmp_path / "audits" / "user.yaml",
    {"records": [{"location": "audits/user.yaml", "observation": LONG_OBSERVATION}]},
  )
  _write_yaml(
    tmp_path / "observations" / "pattern.yaml",
    {"records": [{"location": "observations/pattern.yaml", "observation": LONG_OBSERVATION}]},
  )
  _write_yaml(
    tmp_path / "docs" / "discipline-compliance-reports" / "2026-06-04.yaml",
    {"records": [{"location": "docs/discipline-compliance-reports/2026-06-04.yaml", "observation": LONG_OBSERVATION}]},
  )

  records = InputModel(tmp_path).load_sources(
    review_records=[tmp_path / "reviews" / "review.yaml"],
    compliance_reports_dir=tmp_path / "docs" / "discipline-compliance-reports",
    user_audits=[tmp_path / "audits" / "user.yaml"],
    observation_patterns=[tmp_path / "observations" / "pattern.yaml"],
  )

  sources = [record.provenance["source"] for record in records]
  assert sources.count("review_record") == 1
  assert sources.count("compliance_report") == 2
  assert sources.count("user_audit") == 1
  assert sources.count("observation_pattern") == 1
  assert all(set(record.provenance) == {"source", "location", "observation"} for record in records)


def test_t002_compliance_reports_are_loaded_in_timeline_order(tmp_path):
  reports_dir = tmp_path / "docs" / "discipline-compliance-reports"
  _write_yaml(
    reports_dir / "2026-06-04.yaml",
    {"records": [{"location": "late.yaml", "observation": LONG_OBSERVATION}]},
  )
  _write_yaml(
    reports_dir / "2026-06-03.yaml",
    {"records": [{"location": "early.yaml", "observation": LONG_OBSERVATION}]},
  )

  records = InputModel(tmp_path).load_compliance_reports(reports_dir)

  assert [record.provenance["location"] for record in records] == ["early.yaml", "late.yaml"]


def test_t002_provenance_schema_documents_owned_constraints():
  schema = json.loads(
    (InputModel.project_root() / "tools" / "self_improvement" / "schemas" / "provenance.schema.json")
    .read_text(encoding="utf-8")
  )

  assert schema["properties"]["source"]["enum"] == [
    "review_record",
    "compliance_report",
    "user_audit",
    "observation_pattern",
  ]
  assert schema["properties"]["observation"]["minLength"] == 30
  assert schema["required"] == ["source", "location", "observation"]
