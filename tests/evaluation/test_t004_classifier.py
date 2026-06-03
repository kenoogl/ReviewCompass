"""T-004 のテスト：実行分類器（run classifier）。

対応タスク：evaluation tasks.md T-004
対応設計節：design.md §分類モデル
対応要件：Requirement 1 受入 1〜6

テスト要件（tasks.md T-004 より）：
- 4 値分類の境界テスト
- 段省略整合チェックの 5 ステップ手順テスト
- レビューモードとの直交独立性テスト
- foundation 4 値正本の参照のみ使用の機械検証
"""
import json
from pathlib import Path

import yaml

from classifier.foundation_ref import vocabulary
from classifier.run_classification_writer import RunClassificationWriter
from classifier.run_classifier import RunClassifier
from classifier.step_omission_validator import StepOmissionValidator


def _write_run(tmp_path, *, evidence_class="valid", treatment="judgment", review_mode="runtime_mediated",
               step_records=None, omit_review_case=False):
  run_dir = tmp_path / "imports" / "bundles" / "bundle-001" / "run" / "run-001"
  run_dir.mkdir(parents=True)
  manifest = {
    "run_id": "run-001",
    "target_id": "target-001",
    "evidence_class": evidence_class,
    "treatment": treatment,
    "review_mode": review_mode,
  }
  (run_dir / "run_manifest.yaml").write_text(
    yaml.safe_dump(manifest, allow_unicode=True, sort_keys=False),
    encoding="utf-8",
  )
  if not omit_review_case:
    (run_dir / "review_case.json").write_text(
      json.dumps({
        "run_id": "run-001",
        "step_records": step_records or [
          {"step": "primary_detection", "step_outcome": "executed"},
          {"step": "adversarial_review", "step_outcome": "executed"},
          {"step": "judgment", "step_outcome": "executed"},
          {"step": "integration", "step_outcome": "executed"},
        ],
      }, ensure_ascii=False),
      encoding="utf-8",
    )
  return run_dir


def test_foundation_evidence_class_vocab_is_referenced():
  """foundation の evidence_class 4 値正本を参照できる。"""
  assert vocabulary("evidence_class") == [
    "valid",
    "invalid",
    "exploratory",
    "analysis_blocked",
  ]


def test_valid_run_is_classified_valid(tmp_path):
  """evidence_class=valid の実行は valid に分類される。"""
  run_dir = _write_run(tmp_path, evidence_class="valid")
  result = RunClassifier().classify(run_dir)
  assert result.classification == "valid"
  assert result.included_in_standard_metrics is True


def test_invalid_run_is_excluded_from_standard_metrics(tmp_path):
  """evidence_class=invalid の実行は標準メトリクスから除外される。"""
  run_dir = _write_run(tmp_path, evidence_class="invalid")
  result = RunClassifier().classify(run_dir)
  assert result.classification == "invalid"
  assert result.included_in_standard_metrics is False
  assert "evidence_class_invalid" in result.reason_codes


def test_missing_required_input_becomes_analysis_blocked(tmp_path):
  """必要入力欠落はデータ無効ではなく analysis_blocked として扱う。"""
  run_dir = _write_run(tmp_path, evidence_class="valid", omit_review_case=True)
  result = RunClassifier().classify(run_dir)
  assert result.classification == "analysis_blocked"
  assert "missing_required_input" in result.reason_codes


def test_rejected_admission_becomes_analysis_blocked(tmp_path):
  """取り込み許容判定 rejected は標準母集団に入れず analysis_blocked。"""
  run_dir = _write_run(tmp_path, evidence_class="valid")
  result = RunClassifier().classify(run_dir, admission_status="rejected")
  assert result.classification == "analysis_blocked"
  assert "admission_rejected" in result.reason_codes


def test_review_mode_is_orthogonal_to_validity(tmp_path):
  """api_mediated の内容上有効な実行をレビューモード理由で無効化しない。"""
  run_dir = _write_run(tmp_path, evidence_class="valid", review_mode="api_mediated")
  result = RunClassifier().classify(run_dir)
  assert result.classification == "valid"
  assert result.review_mode == "api_mediated"
  assert "review_mode_mismatch" not in result.reason_codes


def test_step_omission_validator_accepts_treatment_skips(tmp_path):
  """primary treatment の設計上省略を障害欠損として扱わない。"""
  step_records = [
    {"step": "primary_detection", "step_outcome": "executed"},
    {"step": "adversarial_review", "step_outcome": "skipped_by_treatment"},
    {"step": "judgment", "step_outcome": "skipped_by_treatment"},
    {"step": "integration", "step_outcome": "executed"},
  ]
  run_dir = _write_run(tmp_path, treatment="primary", step_records=step_records)
  result = StepOmissionValidator().validate(run_dir)
  assert result.ok is True
  assert result.failure_steps == []


def test_step_omission_validator_detects_failure_gap(tmp_path):
  """期待 executed の段が failed なら障害欠損として検出する。"""
  step_records = [
    {"step": "primary_detection", "step_outcome": "executed"},
    {"step": "adversarial_review", "step_outcome": "failed"},
    {"step": "judgment", "step_outcome": "skipped_by_treatment"},
    {"step": "integration", "step_outcome": "executed"},
  ]
  run_dir = _write_run(tmp_path, treatment="adversarial", step_records=step_records)
  result = StepOmissionValidator().validate(run_dir)
  assert result.ok is False
  assert result.failure_steps == ["adversarial_review"]


def test_step_failure_changes_valid_run_to_analysis_blocked(tmp_path):
  """段整合チェック失敗時は valid 入力でも analysis_blocked にする。"""
  step_records = [
    {"step": "primary_detection", "step_outcome": "executed"},
    {"step": "adversarial_review", "step_outcome": "failed"},
    {"step": "judgment", "step_outcome": "skipped_by_treatment"},
    {"step": "integration", "step_outcome": "executed"},
  ]
  run_dir = _write_run(tmp_path, treatment="adversarial", step_records=step_records)
  result = RunClassifier().classify(run_dir)
  assert result.classification == "analysis_blocked"
  assert "step_outcome_mismatch" in result.reason_codes


def test_run_classification_writer_outputs_index(tmp_path):
  """run_classification_index.json に分類結果を書き出す。"""
  run_dir = _write_run(tmp_path, evidence_class="exploratory")
  result = RunClassifier().classify(run_dir)
  path = RunClassificationWriter().write(tmp_path / "experiments" / "analysis", [result])
  index = json.loads(path.read_text(encoding="utf-8"))
  assert index["entries"][0]["run_id"] == "run-001"
  assert index["entries"][0]["classification"] == "exploratory"
