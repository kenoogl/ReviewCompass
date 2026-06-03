"""T-002 のテスト：analysis intake reader。

対応タスク：analysis tasks.md T-002
対応設計節：design.md §全体構造 段 1、§取り込み失敗のモデル
対応要件：Requirement 1 受入 4、Requirement 4 受入 1〜3

テスト要件（tasks.md T-002 より）：
- 正常系の読み込みテスト
- 4 値の失敗理由ごとの検知テスト
- runtime 生証拠への一次参照がないことの構造検査
- analysis_manifest.yaml スキーマ検証テスト
"""
import importlib
import json
from pathlib import Path

import jsonschema
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]


def _reader_class():
  module = importlib.import_module("analysis.intake.intake_reader")
  return module.IntakeReader


def _write_json(path, payload):
  path.parent.mkdir(parents=True, exist_ok=True)
  path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")


def _write_yaml(path, payload):
  path.parent.mkdir(parents=True, exist_ok=True)
  path.write_text(
    yaml.safe_dump(payload, allow_unicode=True, sort_keys=False),
    encoding="utf-8",
  )


def _setup_evaluation_root(tmp_path, *, stale=False, unreadable=False):
  root = tmp_path / "experiments" / "analysis"
  _write_json(
    root / "comparisons" / "treatment_comparisons.json",
    {"comparison_type": "treatment", "included_runs": ["run-001"]},
  )
  _write_json(
    root / "classifications" / "exclusion_report.json",
    {"entries": []},
  )
  _write_yaml(
    root / "manifests" / "analysis_run_manifest.yaml",
    {
      "analysis_logic_version": "eval-1",
      "input_run_set": ["run-001"],
      "generated_at": "2026-06-03T12:00:00+09:00",
      "output_artifact_ids": ["treatment_comparisons"],
    },
  )
  _write_json(
    root / "manifests" / "staleness_register.json",
    {"entries": [{"artifact_id": "treatment_comparisons", "stale": stale}]},
  )
  if unreadable:
    (root / "comparisons" / "treatment_comparisons.json").write_text(
      "{not-json",
      encoding="utf-8",
    )
  return root


def _setup_conformance_root(tmp_path):
  root = tmp_path / "experiments" / "conformance"
  _write_json(
    root / "conformance_run.json",
    {"conformance_run_id": "conf-001", "compliance_rate": 1.0},
  )
  return root


def _setup_unreadable_conformance_root(tmp_path):
  root = tmp_path / "experiments" / "conformance"
  root.mkdir(parents=True)
  (root / "conformance_run.json").write_text("{not-json", encoding="utf-8")
  return root


def _failure_report(output_root):
  return json.loads(
    (
      output_root / "shared" / "manifests" / "intake_failure_report.json"
    ).read_text(encoding="utf-8")
  )


def test_intake_reader_reads_evaluation_and_conformance_outputs(tmp_path):
  """正常系では evaluation / conformance-evaluation 成果物を読み込める。"""
  evaluation_root = _setup_evaluation_root(tmp_path)
  conformance_root = _setup_conformance_root(tmp_path)
  output_root = tmp_path / "analysis-output"

  result = _reader_class()().read(
    evaluation_root=evaluation_root,
    conformance_root=conformance_root,
    output_root=output_root,
    analysis_logic_version="analysis-1",
    generated_at="2026-06-03T12:30:00+09:00",
  )

  assert result["ok"] is True
  assert result["failures"] == []
  assert (output_root / "shared" / "manifests" / "intake_failure_report.json").is_file()
  manifest = yaml.safe_load(
    (output_root / "shared" / "manifests" / "analysis_manifest.yaml").read_text(
      encoding="utf-8",
    )
  )
  assert manifest["analysis_logic_version"] == "analysis-1"
  assert manifest["input_run_set"] == ["run-001"]


def test_intake_reader_reports_missing_evaluation_root(tmp_path):
  """evaluation 成果物が欠落していれば upstream_evaluation_missing を記録する。"""
  result = _reader_class()().read(
    evaluation_root=tmp_path / "missing-analysis",
    conformance_root=_setup_conformance_root(tmp_path),
    output_root=tmp_path / "analysis-output",
    analysis_logic_version="analysis-1",
    generated_at="2026-06-03T12:30:00+09:00",
  )

  assert result["ok"] is False
  assert result["failures"][0]["intake_failure_reason"] == "upstream_evaluation_missing"
  failure = _failure_report(tmp_path / "analysis-output")["entries"][0]
  assert set(failure) >= {
    "failure_id",
    "intake_failure_reason",
    "affected_destinations",
    "detected_at",
  }


def test_intake_reader_reports_unreadable_evaluation_artifact(tmp_path):
  """evaluation 成果物が読めなければ upstream_evaluation_unreadable を記録する。"""
  result = _reader_class()().read(
    evaluation_root=_setup_evaluation_root(tmp_path, unreadable=True),
    conformance_root=_setup_conformance_root(tmp_path),
    output_root=tmp_path / "analysis-output",
    analysis_logic_version="analysis-1",
    generated_at="2026-06-03T12:30:00+09:00",
  )

  assert result["ok"] is False
  assert result["failures"][0]["intake_failure_reason"] == "upstream_evaluation_unreadable"


def test_intake_reader_reports_stale_evaluation_artifact(tmp_path):
  """evaluation 成果物が陳腐化していれば upstream_evaluation_stale を記録する。"""
  result = _reader_class()().read(
    evaluation_root=_setup_evaluation_root(tmp_path, stale=True),
    conformance_root=_setup_conformance_root(tmp_path),
    output_root=tmp_path / "analysis-output",
    analysis_logic_version="analysis-1",
    generated_at="2026-06-03T12:30:00+09:00",
  )

  assert result["ok"] is False
  assert result["failures"][0]["intake_failure_reason"] == "upstream_evaluation_stale"


def test_intake_reader_reports_missing_conformance_root(tmp_path):
  """conformance-evaluation 成果物欠落は conformance_evaluation_missing として記録する。"""
  result = _reader_class()().read(
    evaluation_root=_setup_evaluation_root(tmp_path),
    conformance_root=tmp_path / "missing-conformance",
    output_root=tmp_path / "analysis-output",
    analysis_logic_version="analysis-1",
    generated_at="2026-06-03T12:30:00+09:00",
  )

  assert result["ok"] is False
  assert result["failures"][0]["intake_failure_reason"] == "conformance_evaluation_missing"


def test_intake_reader_distinguishes_unreadable_conformance_artifact(tmp_path):
  """conformance-evaluation の読取失敗は欠落と区別できる。"""
  result = _reader_class()().read(
    evaluation_root=_setup_evaluation_root(tmp_path),
    conformance_root=_setup_unreadable_conformance_root(tmp_path),
    output_root=tmp_path / "analysis-output",
    analysis_logic_version="analysis-1",
    generated_at="2026-06-03T12:30:00+09:00",
  )

  assert result["ok"] is False
  failure = result["failures"][0]
  assert failure["intake_failure_reason"] == "conformance_evaluation_missing"
  assert failure["failure_kind"] == "unreadable"
  assert "detail" in failure


def test_intake_failure_report_schema_requires_tracking_fields():
  """intake_failure_report schema は設計上の最低追跡項目を必須にする。"""
  schema_path = (
    REPO_ROOT / "analysis" / "intake" / "intake_failure_report.schema.json"
  )
  schema = json.loads(schema_path.read_text(encoding="utf-8"))
  validator = jsonschema.Draft202012Validator(schema)

  errors = list(
    validator.iter_errors(
      {
        "entries": [
          {
            "intake_failure_reason": "upstream_evaluation_missing",
            "source_path": "experiments/analysis",
          }
        ]
      }
    )
  )

  assert any("failure_id" in error.message for error in errors)
  assert any("affected_destinations" in error.message for error in errors)
  assert any("detected_at" in error.message for error in errors)


def test_intake_code_does_not_reference_runtime_raw_evidence():
  """analysis intake 実装は runtime 生証拠を一次参照しない。"""
  intake_dir = REPO_ROOT / "analysis" / "intake"
  sources = list(intake_dir.glob("*.py"))
  assert sources, "analysis/intake の Python 実装が存在しない"
  for source in sources:
    assert "experiments/runtime/" not in source.read_text(encoding="utf-8")
