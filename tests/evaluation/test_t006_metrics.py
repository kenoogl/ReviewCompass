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
from metrics.dogfooding_metrics_extractor import DogfoodingMetricsExtractor
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


def test_phase_overlay_uses_canonical_four_document_phases():
  """phase overlay は intent / requirements / design / tasks の 4 相だけを宣言する。"""
  overlay = RunMetricsExtractor.load_yaml_definition("phase_overlay")
  assert set(overlay["phase_overlays"]) == {
    "intent",
    "requirements",
    "design",
    "tasks",
  }


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


def _write_dogfooding_sources(tmp_path):
  """dogfooding メトリクス用の最小入力証跡を書く。"""
  review_run_dir = tmp_path / "review-run"
  review_run_dir.mkdir()
  (review_run_dir / "model-result-summary.yaml").write_text(
    yaml.safe_dump(
      {
        "run_id": "review-run",
        "models": [
          {
            "model_id": "claude-sonnet-4-6",
            "raw_path": "raw/claude-sonnet-4-6.round-1.txt",
            "findings_count": 2,
            "must_fix_count": 1,
            "should_fix_count": 1,
            "leave_as_is_count": 0,
            "human_required_count": 0,
          },
          {
            "model_id": "gpt-5.4",
            "raw_path": "raw/gpt-5.4.round-1.txt",
            "findings_count": 1,
            "must_fix_count": 0,
            "should_fix_count": 1,
            "leave_as_is_count": 0,
            "human_required_count": 0,
          },
        ],
      },
      allow_unicode=True,
      sort_keys=False,
    ),
    encoding="utf-8",
  )
  (review_run_dir / "triage.yaml").write_text(
    yaml.safe_dump(
      {
        "run_id": "review-run",
        "decision_actor": "gpt-5.5",
        "decision_actor_type": "proxy_model",
        "items": [
          {"finding_id": "F-001", "final_label": "must-fix"},
          {"finding_id": "F-002", "final_label": "should-fix"},
          {"finding_id": "F-003", "final_label": "should-fix"},
        ],
      },
      allow_unicode=True,
      sort_keys=False,
    ),
    encoding="utf-8",
  )
  (review_run_dir / "must-fix-clusters.yaml").write_text(
    yaml.safe_dump(
      {
        "clusters": [
          {"cluster_id": "C-001", "proposed_final_label": "must-fix"},
        ],
      },
      allow_unicode=True,
      sort_keys=False,
    ),
    encoding="utf-8",
  )
  ledger_path = tmp_path / "autonomous-ledger.yaml"
  ledger_path.write_text(
    yaml.safe_dump(
      {
        "mode": "autonomous_parallel",
        "verdict": "OK",
        "exit_code": 0,
        "execution_evidence_snapshot": {
          "completed_tasks": ["target-bundle", "api-primary", "aggregate-review-run"],
          "parallelized_operations": ["api_review_calls", "local_test_checks"],
          "human_required_count": 0,
        },
        "integration_result": {
          "status": "completed",
          "tests": "pytest -q; unittest",
          "decision": "accepted",
        },
      },
      allow_unicode=True,
      sort_keys=False,
    ),
    encoding="utf-8",
  )
  workflow_log_path = tmp_path / "workflow-precheck.log"
  workflow_log_path.write_text(
    "\n".join(
      [
        json.dumps(
          {
            "action": {"subcommand": "next"},
            "verdict": "OK",
            "exit_code": 0,
            "reasons": [],
          },
          ensure_ascii=False,
        ),
        json.dumps(
          {
            "action": {"subcommand": "commit"},
            "verdict": "DEVIATION",
            "exit_code": 2,
            "reasons": [
              "ユーザ承認レコードは消費済みです",
              "stages/in-progress に進行中ファイルがあります",
            ],
          },
          ensure_ascii=False,
        ),
        json.dumps(
          {
            "action": {"subcommand": "push"},
            "verdict": "WARN",
            "exit_code": 1,
            "reasons": ["未消化所見 1 件以上"],
          },
          ensure_ascii=False,
        ),
      ]
    ) + "\n",
    encoding="utf-8",
  )
  return review_run_dir, ledger_path, workflow_log_path


def test_dogfooding_metrics_extract_review_run_and_workflow_precheck(tmp_path):
  """dogfooding 抽出器は review-run と workflow-precheck.log を最小スキーマに正規化する。"""
  review_run_dir, ledger_path, workflow_log_path = _write_dogfooding_sources(tmp_path)

  metrics = DogfoodingMetricsExtractor().extract(
    review_run_dir=review_run_dir,
    workflow_log_path=workflow_log_path,
    ledger_path=ledger_path,
  )

  assert metrics["artifact_id"] == "dogfooding_deployment_metrics"
  assert metrics["metric_level"] == "dogfooding_deployment"
  assert metrics["review_run"]["run_id"] == "review-run"
  assert metrics["review_run"]["model_count"] == 2
  assert metrics["review_run"]["raw_response_count"] == 2
  assert metrics["review_run"]["finding_count"] == 3
  assert metrics["review_run"]["human_required_count"] == 0
  assert metrics["review_run"]["triage_label_counts"] == {
    "must-fix": 1,
    "should-fix": 2,
    "leave-as-is": 0,
  }
  assert metrics["workflow_precheck"]["total_checks"] == 3
  assert metrics["workflow_precheck"]["by_verdict"] == {
    "OK": 1,
    "WARN": 1,
    "DEVIATION": 1,
  }
  assert metrics["workflow_precheck"]["blocked_count"] == 1
  assert metrics["workflow_precheck"]["warning_count"] == 1
  assert metrics["workflow_precheck"]["commit_approval_failure_count"] == 1
  assert metrics["workflow_precheck"]["in_progress_block_count"] == 1
  assert metrics["implementation"]["status"] == "completed"
  assert metrics["implementation"]["test_command_count"] == 2
  assert metrics["implementation"]["completed_task_count"] == 3
  assert metrics["implementation"]["parallelized_operation_count"] == 2
  assert metrics["implementation"]["human_required_count"] == 0
  assert any(
    path.endswith("workflow-precheck.log")
    for path in metrics["derivation"]["source_artifacts"]
  )
  assert "ledger.execution_evidence_snapshot" in metrics["derivation"]["source_fields"]
