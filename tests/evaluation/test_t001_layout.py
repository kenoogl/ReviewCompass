"""T-001 のテスト：分析成果物配置の構造と命名規約。

対応タスク：evaluation tasks.md T-001
対応設計節：design.md §分析成果物配置、§配置の根拠
対応要件：Requirement 5 受入 1、3

テスト要件（tasks.md T-001 より）：
- 配置仕様 YAML の解析テスト
- 必須サブディレクトリ宣言の存在検査（8 件）
"""
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]

LAYOUT_SPEC = REPO_ROOT / "evaluation/analysis_layout/layout_spec.yaml"
LAYOUT_README = REPO_ROOT / "evaluation/analysis_layout/README.md"
EVALUATION_DOC = REPO_ROOT / "docs/operations/EVALUATION.md"

EXPECTED_REQUIRED_DIRS = {
  "imports",
  "manifests",
  "classifications",
  "metrics",
  "comparisons",
  "caveats",
  "modes",
  "roles",
}


def _load_layout_spec():
  if not LAYOUT_SPEC.is_file():
    pytest.fail(f"配置仕様 YAML が存在しない：{LAYOUT_SPEC}")
  with LAYOUT_SPEC.open(encoding="utf-8") as f:
    return yaml.safe_load(f)


def test_layout_spec_exists():
  """layout_spec.yaml が存在する（成果物）。"""
  assert LAYOUT_SPEC.is_file(), f"layout_spec.yaml が存在しない：{LAYOUT_SPEC}"


def test_layout_readme_exists():
  """analysis_layout/README.md が存在する（成果物）。"""
  assert LAYOUT_README.is_file(), f"README.md が存在しない：{LAYOUT_README}"


def test_evaluation_operations_doc_exists():
  """docs/operations/EVALUATION.md が存在する（成果物）。"""
  assert EVALUATION_DOC.is_file(), f"EVALUATION.md が存在しない：{EVALUATION_DOC}"


def test_layout_spec_is_parseable():
  """配置仕様 YAML が解析可能（テスト要件：YAML 解析テスト）。"""
  spec = _load_layout_spec()
  assert isinstance(spec, dict), "layout_spec.yaml がマッピングとして解析できない"


def test_layout_spec_declares_analysis_root():
  """分析成果物ルートのパターン（experiments/analysis）が宣言されている。"""
  spec = _load_layout_spec()
  assert spec.get("analysis_root") == "experiments/analysis", (
    "analysis_root が experiments/analysis として宣言されていない"
  )


def test_layout_spec_declares_required_directories():
  """必須サブディレクトリ 8 件が宣言されている（完了条件 1）。"""
  spec = _load_layout_spec()
  declared = {entry["path"] for entry in spec["required_directories"]}
  assert declared == EXPECTED_REQUIRED_DIRS, (
    f"必須サブディレクトリの宣言が design.md §分析成果物配置 と一致しない：{declared}"
  )


def test_layout_spec_required_directory_count_is_8():
  """必須サブディレクトリの宣言件数が 8 件（完了条件 1）。"""
  spec = _load_layout_spec()
  assert len(spec["required_directories"]) == 8, (
    "必須サブディレクトリの宣言件数が 8 件でない"
  )


def test_layout_spec_each_directory_has_purpose():
  """各必須サブディレクトリ宣言に配置目的（purpose）が記されている。"""
  spec = _load_layout_spec()
  for entry in spec["required_directories"]:
    assert entry.get("purpose"), f"配置目的が欠落：{entry.get('path')}"


def test_layout_spec_declares_manifest_requirements():
  """analysis_run_manifest.yaml の必須項目が宣言されている（完了条件 2）。"""
  spec = _load_layout_spec()
  required = set(spec["analysis_run_manifest"]["required_fields"])
  expected = {
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
  assert required == expected, (
    f"analysis_run_manifest.yaml の必須項目が設計と一致しない：{required}"
  )


def test_evaluation_doc_describes_raw_and_derived_separation():
  """EVALUATION.md に生実行証拠と分析成果物の分離原則が記述されている。"""
  text = EVALUATION_DOC.read_text(encoding="utf-8")
  assert "生実行証拠" in text and "分析成果物" in text and "分離" in text, (
    "EVALUATION.md に生実行証拠と分析成果物の分離原則がない"
  )


def test_evaluation_doc_describes_manifest_required_items():
  """EVALUATION.md に analysis_run_manifest.yaml の必須項目が記述されている。"""
  text = EVALUATION_DOC.read_text(encoding="utf-8")
  assert "analysis_run_manifest.yaml" in text and "analysis_logic_version" in text, (
    "EVALUATION.md に analysis_run_manifest.yaml の必須項目記述がない"
  )


def test_evaluation_doc_describes_version_coverage_recording():
  """EVALUATION.md に版被覆記録の運用ルールが記述されている。"""
  text = EVALUATION_DOC.read_text(encoding="utf-8")
  assert "protocol_version_coverage" in text
  assert "runtime_version_coverage" in text
  assert "prompt_set_version_coverage" in text
