"""T-003 のテスト：取り込み許容判定器（admission）。

対応タスク：evaluation tasks.md T-003
対応設計節：design.md §取り込み証拠の許容判定状態、§判断 7
対応要件：Requirement 10 受入 2、3、4、5

テスト要件（tasks.md T-003 より）：
- 境界 7 ケース（不在／全欠落／読み取り不能／一部欠落／版不整合／全条件揃い／チェックサム不一致）
- 3 値正本ファイルの値テスト
- チェックサム照合テスト
"""
import hashlib
import importlib
import json
from pathlib import Path

import yaml

from admission.admission_classifier import AdmissionClassifier
from admission.admission_register_writer import AdmissionRegisterWriter
from admission.checksum_verifier import ChecksumVerifier

REPO_ROOT = Path(__file__).resolve().parents[2]
ADMISSION_VOCAB = REPO_ROOT / "evaluation/admission/admission_vocab.yaml"


def _write_bundle(tmp_path, *, manifest_updates=None, corrupt_checksum=False, invalid_yaml=False):
  bundle_dir = tmp_path / "imports" / "bundles" / "bundle-001"
  run_dir = bundle_dir / "run" / "run-001"
  (run_dir / "validation").mkdir(parents=True)
  run_manifest = {
    "run_id": "run-001",
    "source_repository_id": "repo-001",
    "source_revision": "rev-001",
    "review_mode": "runtime_mediated",
    "protocol_version": "protocol-1",
    "prompt_set_version": "prompt-1",
  }
  (run_dir / "run_manifest.yaml").write_text(
    yaml.safe_dump(run_manifest, allow_unicode=True, sort_keys=False),
    encoding="utf-8",
  )
  (run_dir / "review_case.json").write_text(json.dumps({"run_id": "run-001"}), encoding="utf-8")
  (run_dir / "validation" / "validator_result.json").write_text(
    json.dumps({"validator_status": "passed"}),
    encoding="utf-8",
  )
  (run_dir / "validation" / "invalidation_markers.json").write_text(
    json.dumps({"markers": []}),
    encoding="utf-8",
  )
  manifest = {
    "bundle_id": "bundle-001",
    "run_id": "run-001",
    "source_repository_id": "repo-001",
    "source_revision": "rev-001",
    "review_mode": "runtime_mediated",
    "protocol_version": "protocol-1",
    "prompt_set_version": "prompt-1",
  }
  if manifest_updates:
    for key, value in manifest_updates.items():
      if value is None:
        manifest.pop(key, None)
      else:
        manifest[key] = value
  if invalid_yaml:
    (bundle_dir / "bundle_manifest.yaml").write_text(":\n", encoding="utf-8")
  else:
    (bundle_dir / "bundle_manifest.yaml").write_text(
      yaml.safe_dump(manifest, allow_unicode=True, sort_keys=False),
      encoding="utf-8",
    )

  checksums = {}
  for path in sorted(p for p in run_dir.rglob("*") if p.is_file()):
    rel = str(path.relative_to(run_dir))
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    checksums[rel] = "sha256:" + digest
  if corrupt_checksum:
    checksums["review_case.json"] = "sha256:" + "0" * 64
  (bundle_dir / "checksums").mkdir()
  (bundle_dir / "checksums" / "bundle_checksums.json").write_text(
    json.dumps(checksums, ensure_ascii=False, indent=2),
    encoding="utf-8",
  )
  return bundle_dir


def test_admission_vocab_declares_3_values():
  """admission_vocab.yaml が 3 値正本を宣言する。"""
  spec = yaml.safe_load(ADMISSION_VOCAB.read_text(encoding="utf-8"))
  assert spec["values"] == ["admitted_standard", "admitted_exploratory", "rejected"]


def test_admission_classifier_imports_as_repo_package():
  """conftest の evaluation/ パス追加なしでも repo package として import できる。"""
  module = importlib.import_module("evaluation.admission.admission_classifier")
  assert module.AdmissionClassifier.__name__ == "AdmissionClassifier"


def test_missing_bundle_manifest_is_rejected(tmp_path):
  """境界 1：bundle_manifest.yaml 不在は rejected。"""
  bundle_dir = tmp_path / "imports" / "bundles" / "bundle-001"
  bundle_dir.mkdir(parents=True)
  result = AdmissionClassifier().classify(bundle_dir)
  assert result.admission_status == "rejected"
  assert "missing_bundle_manifest" in result.admission_reason_codes


def test_empty_manifest_is_rejected(tmp_path):
  """境界 2：必須項目が全欠落した manifest は rejected。"""
  bundle_dir = _write_bundle(tmp_path)
  (bundle_dir / "bundle_manifest.yaml").write_text("{}\n", encoding="utf-8")
  result = AdmissionClassifier().classify(bundle_dir)
  assert result.admission_status == "rejected"
  assert "missing_required_fields" in result.admission_reason_codes


def test_unreadable_manifest_is_rejected(tmp_path):
  """境界 3：読み取り不能な manifest は rejected。"""
  bundle_dir = _write_bundle(tmp_path, invalid_yaml=True)
  result = AdmissionClassifier().classify(bundle_dir)
  assert result.admission_status == "rejected"
  assert "unreadable_bundle_manifest" in result.admission_reason_codes


def test_partial_provenance_missing_is_rejected(tmp_path):
  """境界 4：必須来歴情報の一部欠落は rejected。"""
  bundle_dir = _write_bundle(tmp_path, manifest_updates={"source_revision": None})
  result = AdmissionClassifier().classify(bundle_dir)
  assert result.admission_status == "rejected"
  assert "missing_required_fields" in result.admission_reason_codes
  assert result.missing_fields == ["source_revision"]


def test_version_mismatch_is_admitted_exploratory(tmp_path):
  """境界 5：比較集合と版不整合なら admitted_exploratory。"""
  bundle_dir = _write_bundle(tmp_path, manifest_updates={"protocol_version": "protocol-2"})
  result = AdmissionClassifier().classify(
    bundle_dir,
    expected_versions={"protocol_version": "protocol-1", "prompt_set_version": "prompt-1"},
  )
  assert result.admission_status == "admitted_exploratory"
  assert "version_mismatch" in result.admission_reason_codes
  assert result.eligible_for_standard_comparison is False
  assert result.eligible_for_exploratory_analysis is True


def test_runtime_version_mismatch_is_admitted_exploratory(tmp_path):
  """runtime_version の比較集合不整合も admitted_exploratory。"""
  bundle_dir = _write_bundle(tmp_path, manifest_updates={"runtime_version": "runtime-2"})
  result = AdmissionClassifier().classify(
    bundle_dir,
    expected_versions={"runtime_version": "runtime-1"},
  )
  assert result.admission_status == "admitted_exploratory"
  assert "version_mismatch" in result.admission_reason_codes


def test_complete_bundle_is_admitted_standard(tmp_path):
  """境界 6：全条件が揃えば admitted_standard。"""
  bundle_dir = _write_bundle(tmp_path)
  result = AdmissionClassifier().classify(
    bundle_dir,
    expected_versions={"protocol_version": "protocol-1", "prompt_set_version": "prompt-1"},
  )
  assert result.admission_status == "admitted_standard"
  assert result.admission_reason_codes == []
  assert result.eligible_for_standard_comparison is True


def test_checksum_mismatch_is_rejected(tmp_path):
  """境界 7：チェックサム不一致は rejected。"""
  bundle_dir = _write_bundle(tmp_path, corrupt_checksum=True)
  result = AdmissionClassifier().classify(bundle_dir)
  assert result.admission_status == "rejected"
  assert "checksum_mismatch" in result.admission_reason_codes


def test_checksum_verifier_accepts_matching_bundle(tmp_path):
  """チェックサム照合器は一致する束を受理する。"""
  bundle_dir = _write_bundle(tmp_path)
  result = ChecksumVerifier().verify(bundle_dir)
  assert result.ok is True
  assert result.mismatches == []


def test_checksum_verifier_rejects_ambiguous_run_directory(tmp_path):
  """run/ 配下の run_id が複数なら構造違反として rejected 相当の失敗を返す。"""
  bundle_dir = _write_bundle(tmp_path)
  extra = bundle_dir / "run" / "run-002"
  extra.mkdir()
  result = ChecksumVerifier().verify(bundle_dir)
  assert result.ok is False
  assert "ambiguous_run_directory" in result.missing_files


def test_admission_register_writer_records_result(tmp_path):
  """admission_register.json に許容判定結果が追記される。"""
  bundle_dir = _write_bundle(tmp_path)
  result = AdmissionClassifier().classify(bundle_dir)
  register_path = AdmissionRegisterWriter().append(tmp_path / "experiments" / "analysis", result)

  register = json.loads(register_path.read_text(encoding="utf-8"))
  entry = register["entries"][0]
  assert entry["bundle_id"] == "bundle-001"
  assert entry["run_id"] == "run-001"
  assert entry["admission_status"] == "admitted_standard"
  assert entry["eligible_for_standard_comparison"] is True
  assert entry["eligible_for_exploratory_analysis"] is True
