"""T-006 のテスト：メトリクス抽出器。

対応タスク：evaluation tasks.md T-006
対応設計節：design.md §メトリクスモデル、§版管理モデル
対応要件：Requirement 3、Requirement 5 受入 2・4・5、Requirement 8、Requirement 2 受入 6
"""
import json

import yaml

from metrics.finding_metrics_extractor import FindingMetricsExtractor
from metrics.identifier_link_validator import IdentifierLinkValidator
from metrics.run_metrics_extractor import RunMetricsExtractor
from metrics.treatment_metrics_extractor import TreatmentMetricsExtractor
from manifests.analysis_run_manifest_writer import AnalysisRunManifestWriter


def _write_review_case(tmp_path):
  run_dir = tmp_path / "run-001"
  run_dir.mkdir()
  review_case = {
    "run_id": "run-001",
    "target_id": "target-001",
    "feature": "evaluation",
    "phase_profile": "design",
    "treatment": "judgment",
    "protocol_version": "protocol-1",
    "runtime_version": "runtime-1",
    "prompt_set_version": "prompt-1",
    "findings": [
      {"finding_id": "F-001", "severity": "ERROR", "counter_status": "counter_evidence_raised"},
      {"finding_id": "F-002", "severity": "WARN", "counter_status": "no_counter_evidence_after_challenge"},
      {"finding_id": "F-003", "severity": "INFO", "counter_status": "not_assessed"},
    ],
  }
  (run_dir / "review_case.json").write_text(
    json.dumps(review_case, ensure_ascii=False),
    encoding="utf-8",
  )
  return run_dir


def test_core_and_phase_overlay_definitions_are_parseable():
  """中核層と phase 重ね合わせ層の定義 YAML が解析可能。"""
  core = RunMetricsExtractor.load_yaml_definition("core")
  overlay = RunMetricsExtractor.load_yaml_definition("phase_overlay")
  assert "run_level" in core["metric_layers"]
  assert "design" in overlay["phase_overlays"]


def test_run_metrics_are_separated_from_finding_metrics(tmp_path):
  """実行レベルメトリクスは所見レベルメトリクスと分離して出力される。"""
  run_dir = _write_review_case(tmp_path)
  metrics = RunMetricsExtractor().extract(run_dir)
  assert metrics["metric_level"] == "run"
  assert metrics["run_id"] == "run-001"
  assert metrics["target_id"] == "target-001"
  assert metrics["finding_count"] == 3
  assert "finding_metrics" not in metrics


def test_finding_metrics_aggregate_counter_status(tmp_path):
  """所見レベルメトリクスは foundation counter_status を集計する。"""
  run_dir = _write_review_case(tmp_path)
  metrics = FindingMetricsExtractor().extract(run_dir)
  assert metrics["metric_level"] == "finding"
  assert metrics["counter_status_counts"] == {
    "counter_evidence_raised": 1,
    "no_counter_evidence_after_challenge": 1,
    "not_assessed": 1,
  }
  assert metrics["by_severity"] == {"ERROR": 1, "WARN": 1, "INFO": 1}


def test_treatment_metrics_calculate_counter_evidence_rate(tmp_path):
  """処理方式レベルメトリクスは反証発生率を生成する。"""
  run_dir = _write_review_case(tmp_path)
  finding_metrics = FindingMetricsExtractor().extract(run_dir)
  metrics = TreatmentMetricsExtractor().extract([finding_metrics])
  assert metrics["metric_level"] == "treatment"
  assert metrics["treatments"]["judgment"]["counter_evidence_rate"] == 1 / 3


def test_metrics_keep_derivation_paths(tmp_path):
  """派生メトリクスは生証拠からの導出経路を保持する。"""
  run_dir = _write_review_case(tmp_path)
  metrics = FindingMetricsExtractor().extract(run_dir)
  assert metrics["derivation"]["source_artifact"].endswith("review_case.json")
  assert "findings[].counter_status" in metrics["derivation"]["source_fields"]


def test_identifier_link_validator_accepts_outputs_with_run_and_target():
  """識別子連結保持機構は run_id / target_id を検査する。"""
  outputs = [
    {"artifact_id": "run_metrics", "run_id": "run-001", "target_id": "target-001"},
    {"artifact_id": "finding_metrics", "run_id": "run-001", "target_id": "target-001"},
  ]
  result = IdentifierLinkValidator().validate(outputs)
  assert result.ok is True
  assert result.missing_links == []


def test_identifier_link_validator_rejects_missing_target():
  """派生出力に target_id がなければ識別子連結違反。"""
  result = IdentifierLinkValidator().validate([{"artifact_id": "x", "run_id": "run-001"}])
  assert result.ok is False
  assert result.missing_links == [{"artifact_id": "x", "missing_fields": ["target_id"]}]


def test_analysis_run_manifest_writer_outputs_13_required_fields(tmp_path):
  """analysis_run_manifest.yaml に 13 必須項目を出力する。"""
  path = AnalysisRunManifestWriter().write(
    tmp_path / "experiments" / "analysis",
    analysis_logic_version="eval-1",
    input_run_set=["run-001"],
    generated_at="2026-06-03T12:30:00+09:00",
    metric_set_version="metrics-1",
    phase_metric_profile_version="phase-1",
    comparison_contract_version="comparison-1",
    protocol_version_coverage=["protocol-1"],
    runtime_version_coverage=["runtime-1"],
    prompt_set_version_coverage=["prompt-1"],
    analysis_run_id="analysis-001",
    analysis_started_at="2026-06-03T12:00:00+09:00",
    analysis_completed_at="2026-06-03T12:30:00+09:00",
    output_artifact_ids=["run_metrics"],
  )
  manifest = yaml.safe_load(path.read_text(encoding="utf-8"))
  assert set(manifest) == {
    "analysis_logic_version",
    "input_run_set",
    "generated_at",
    "metric_set_version",
    "phase_metric_profile_version",
    "comparison_contract_version",
    "protocol_version_coverage",
    "runtime_version_coverage",
    "prompt_set_version_coverage",
    "analysis_run_id",
    "analysis_started_at",
    "analysis_completed_at",
    "output_artifact_ids",
  }
