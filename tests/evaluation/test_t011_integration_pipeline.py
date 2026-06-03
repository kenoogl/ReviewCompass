"""T-011 のテスト：evaluation 統合パイプライン。"""
import json

import yaml

from admission.admission_classifier import AdmissionClassifier
from classifier.run_classifier import RunClassifier
from comparison.treatment_comparison_builder import TreatmentComparisonBuilder
from diff_reports.mode_diff_writer import ModeDiffWriter
from diff_reports.role_diff_writer import RoleDiffWriter
from intake.bundle_intake import BundleIntake
from manifests.analysis_run_manifest_writer import AnalysisRunManifestWriter
from metrics.finding_metrics_extractor import FindingMetricsExtractor
from metrics.run_metrics_extractor import RunMetricsExtractor
from metrics.treatment_metrics_extractor import TreatmentMetricsExtractor
from readiness.metadata_validator import MetadataValidator
from reporting.exclusion_report_writer import ExclusionReportWriter
from staleness.handler_selection_logic import HandlerSelectionLogic


def _write_export_bundle(tmp_path):
  bundle_dir = tmp_path / "exports" / "bundle-001"
  run_dir = bundle_dir / "run" / "run-001"
  (run_dir / "validation").mkdir(parents=True)
  manifest = {
    "bundle_id": "bundle-001",
    "run_id": "run-001",
    "source_repository_id": "repo-001",
    "source_revision": "rev-001",
    "review_mode": "runtime_mediated",
    "protocol_version": "protocol-1",
    "prompt_set_version": "prompt-1",
  }
  run_manifest = {
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
  review_case = {
    "run_id": "run-001",
    "target_id": "target-001",
    "feature": "evaluation",
    "phase_profile": "design",
    "treatment": "judgment",
    "protocol_version": "protocol-1",
    "runtime_version": "runtime-1",
    "prompt_set_version": "prompt-1",
    "step_records": [
      {"step": "primary_detection", "step_outcome": "executed"},
      {"step": "adversarial_review", "step_outcome": "executed"},
      {"step": "judgment", "step_outcome": "executed"},
      {"step": "integration", "step_outcome": "executed"},
    ],
    "findings": [
      {
        "finding_id": "F-001",
        "severity": "ERROR",
        "counter_status": "counter_evidence_raised",
      },
    ],
  }
  (bundle_dir / "bundle_manifest.yaml").write_text(
    yaml.safe_dump(manifest, allow_unicode=True, sort_keys=False),
    encoding="utf-8",
  )
  (run_dir / "run_manifest.yaml").write_text(
    yaml.safe_dump(run_manifest, allow_unicode=True, sort_keys=False),
    encoding="utf-8",
  )
  (run_dir / "review_case.json").write_text(json.dumps(review_case), encoding="utf-8")
  (run_dir / "validation" / "validator_result.json").write_text("{}", encoding="utf-8")
  (run_dir / "validation" / "invalidation_markers.json").write_text("{}", encoding="utf-8")
  (bundle_dir / "checksums").mkdir()
  (bundle_dir / "checksums" / "bundle_checksums.json").write_text("{}", encoding="utf-8")
  return bundle_dir


def test_evaluation_pipeline_generates_downstream_artifacts(tmp_path):
  """固定入力から主要な evaluation 派生成果物を生成できる。"""
  bundle_dir = _write_export_bundle(tmp_path)
  analysis_root = tmp_path / "experiments" / "analysis"

  intake = BundleIntake().ingest(
    bundle_dir,
    analysis_root=analysis_root,
    ingested_at="2026-06-03T14:00:00+09:00",
  )
  admission = AdmissionClassifier().classify(intake.bundle_path)
  placed_run = intake.bundle_path / "run" / "run-001"
  readiness = MetadataValidator().validate(placed_run)
  classification = RunClassifier().classify(placed_run, admission_status=admission.admission_status)
  run_metrics = RunMetricsExtractor().extract(placed_run)
  finding_metrics = FindingMetricsExtractor().extract(placed_run)
  treatment_metrics = TreatmentMetricsExtractor().extract([finding_metrics])
  comparison_path = TreatmentComparisonBuilder().write(
    analysis_root,
    [{
      **classification.to_index_entry(),
      **run_metrics,
      "protocol_version": "protocol-1",
      "prompt_set_version": "prompt-1",
    }],
  )
  ExclusionReportWriter().write(analysis_root, [classification.to_index_entry()])
  ModeDiffWriter().write(analysis_root, [{
    "feature": "evaluation",
    "target": "target-001",
    "review_mode": "runtime_mediated",
    "role": "main",
    "severity": "ERROR",
  }])
  RoleDiffWriter().write(analysis_root, [{
    "feature": "evaluation",
    "target": "target-001",
    "review_mode": "runtime_mediated",
    "role": "main",
    "severity": "ERROR",
    "counter_status": "not_assessed",
  }])
  AnalysisRunManifestWriter().write(
    analysis_root,
    analysis_logic_version="eval-1",
    input_run_set=["run-001"],
    generated_at="2026-06-03T14:30:00+09:00",
    metric_set_version="metrics-1",
    phase_metric_profile_version="phase-1",
    comparison_contract_version="comparison-1",
    protocol_version_coverage=["protocol-1"],
    runtime_version_coverage=["runtime-1"],
    prompt_set_version_coverage=["prompt-1"],
    analysis_run_id="analysis-001",
    analysis_started_at="2026-06-03T14:00:00+09:00",
    analysis_completed_at="2026-06-03T14:30:00+09:00",
    output_artifact_ids=["run_metrics", "finding_metrics", "treatment_metrics"],
  )
  decision = HandlerSelectionLogic().select(
    invalidated_run_count=0,
    standard_run_count=1,
    exploratory_only=False,
  )

  assert readiness.ok is True
  assert classification.classification == "valid"
  assert treatment_metrics["treatments"]["judgment"]["counter_evidence_rate"] == 1
  assert json.loads(comparison_path.read_text(encoding="utf-8"))["included_runs"] == ["run-001"]
  assert decision.action == "flag_stale"
  assert (analysis_root / "manifests" / "analysis_run_manifest.yaml").is_file()
  assert (analysis_root / "modes" / "mode_diff_report.json").is_file()
  assert (analysis_root / "roles" / "role_diff_report.json").is_file()
