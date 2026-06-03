"""T-005 のテスト：評価準備メタデータ検査器と不十分性診断。

対応タスク：evaluation tasks.md T-005
対応設計節：design.md §評価準備メタデータの検査
対応要件：Requirement 6 受入 1〜5

テスト要件（tasks.md T-005 より）：
- 必須メタデータ欠落時の拒否テスト
- insufficient_metadata_report.json 出力テスト
- 致命的失敗と analysis_blocked の弁別テスト
"""
import json

import yaml

from readiness.insufficient_metadata_writer import InsufficientMetadataWriter
from readiness.metadata_validator import MetadataValidator


def _write_run(tmp_path, *, updates=None):
  run_dir = tmp_path / "run-001"
  run_dir.mkdir()
  manifest = {
    "run_id": "run-001",
    "target_id": "target-001",
    "source_repository_id": "repo-001",
    "source_revision": "rev-001",
    "phase_profile": "design",
    "treatment": "judgment",
    "review_mode": "runtime_mediated",
    "protocol_version": "protocol-1",
    "runtime_version": "runtime-1",
    "prompt_set_version": "prompt-1",
    "evidence_class": "valid",
  }
  if updates:
    for key, value in updates.items():
      if value is None:
        manifest.pop(key, None)
      else:
        manifest[key] = value
  (run_dir / "run_manifest.yaml").write_text(
    yaml.safe_dump(manifest, allow_unicode=True, sort_keys=False),
    encoding="utf-8",
  )
  return run_dir


def test_required_fields_schema_is_parseable():
  """required_fields_schema.yaml が解析可能で必須項目を宣言する。"""
  schema = MetadataValidator().required_fields
  assert "run_id" in schema
  assert "protocol_version" in schema
  assert "prompt_set_version" in schema


def test_complete_metadata_allows_standard_aggregation(tmp_path):
  """必須メタデータが揃う場合は標準集計を許可する。"""
  result = MetadataValidator().validate(_write_run(tmp_path))
  assert result.ok is True
  assert result.standard_aggregation_allowed is True
  assert result.missing_fields == []


def test_missing_identifier_rejects_standard_aggregation(tmp_path):
  """必須識別子欠落時は標準集計を拒否する。"""
  result = MetadataValidator().validate(_write_run(tmp_path, updates={"run_id": None}))
  assert result.ok is False
  assert result.standard_aggregation_allowed is False
  assert result.evidence_class == "analysis_blocked"
  assert result.missing_fields == ["run_id"]


def test_missing_version_rejects_standard_aggregation(tmp_path):
  """必須版情報欠落時は標準集計を拒否する。"""
  result = MetadataValidator().validate(_write_run(tmp_path, updates={"protocol_version": None}))
  assert result.ok is False
  assert result.standard_aggregation_allowed is False
  assert result.evidence_class == "analysis_blocked"
  assert result.missing_fields == ["protocol_version"]


def test_fatal_failure_is_distinct_from_analysis_blocked(tmp_path):
  """manifest が読めない致命的失敗は analysis_blocked と区別される。"""
  run_dir = _write_run(tmp_path)
  (run_dir / "run_manifest.yaml").write_text(":\n", encoding="utf-8")
  result = MetadataValidator().validate(run_dir)
  assert result.ok is False
  assert result.failure_kind == "fatal"
  assert result.evidence_class == "invalid"


def test_insufficient_metadata_report_has_required_5_fields(tmp_path):
  """insufficient_metadata_report.json に 5 項目を出力する。"""
  result = MetadataValidator().validate(_write_run(tmp_path, updates={"prompt_set_version": None}))
  path = InsufficientMetadataWriter().write(
    tmp_path / "experiments" / "analysis",
    [result],
    detected_at="2026-06-03T12:00:00+09:00",
  )

  report = json.loads(path.read_text(encoding="utf-8"))
  entry = report["entries"][0]
  assert set(entry) == {
    "run_id",
    "missing_fields",
    "evidence_class",
    "affected_derived_artifacts",
    "detected_at",
  }
  assert entry["missing_fields"] == ["prompt_set_version"]
  assert entry["evidence_class"] == "analysis_blocked"
