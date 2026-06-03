"""取り込み許容判定器（evaluation tasks.md T-003）。"""
from dataclasses import asdict, dataclass
from pathlib import Path

import yaml

from .checksum_verifier import ChecksumVerifier

_REQUIRED_FIELDS = [
  "bundle_id",
  "run_id",
  "source_repository_id",
  "source_revision",
  "review_mode",
]


@dataclass(frozen=True)
class AdmissionResult:
  """許容判定結果。"""

  bundle_id: str
  run_id: str
  admission_status: str
  admission_reason_codes: list
  eligible_for_standard_comparison: bool
  eligible_for_exploratory_analysis: bool
  missing_fields: list

  def to_register_entry(self):
    entry = asdict(self)
    entry.pop("missing_fields")
    return entry


class AdmissionClassifier:
  """取り込み証拠を admitted_standard / admitted_exploratory / rejected に分類する。"""

  def __init__(self, checksum_verifier=None):
    self.checksum_verifier = checksum_verifier or ChecksumVerifier()

  def classify(self, bundle_dir, *, expected_versions=None):
    bundle_dir = Path(bundle_dir)
    manifest_path = bundle_dir / "bundle_manifest.yaml"
    if not manifest_path.is_file():
      return self._rejected(None, ["missing_bundle_manifest"], _REQUIRED_FIELDS)

    try:
      manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    except yaml.YAMLError:
      return self._rejected(None, ["unreadable_bundle_manifest"], _REQUIRED_FIELDS)

    if not isinstance(manifest, dict):
      return self._rejected(None, ["unreadable_bundle_manifest"], _REQUIRED_FIELDS)

    missing = [field for field in _REQUIRED_FIELDS if not manifest.get(field)]
    if missing:
      return self._rejected(manifest, ["missing_required_fields"], missing)

    checksum = self.checksum_verifier.verify(bundle_dir)
    if not checksum.ok:
      reason_codes = ["checksum_mismatch"]
      if checksum.missing_files:
        reason_codes.append("checksum_missing_file")
      return self._rejected(manifest, reason_codes, [])

    if self._has_version_mismatch(manifest, expected_versions or {}):
      return AdmissionResult(
        bundle_id=manifest["bundle_id"],
        run_id=manifest["run_id"],
        admission_status="admitted_exploratory",
        admission_reason_codes=["version_mismatch"],
        eligible_for_standard_comparison=False,
        eligible_for_exploratory_analysis=True,
        missing_fields=[],
      )

    return AdmissionResult(
      bundle_id=manifest["bundle_id"],
      run_id=manifest["run_id"],
      admission_status="admitted_standard",
      admission_reason_codes=[],
      eligible_for_standard_comparison=True,
      eligible_for_exploratory_analysis=True,
      missing_fields=[],
    )

  def _rejected(self, manifest, reason_codes, missing_fields):
    manifest = manifest or {}
    return AdmissionResult(
      bundle_id=manifest.get("bundle_id"),
      run_id=manifest.get("run_id"),
      admission_status="rejected",
      admission_reason_codes=reason_codes,
      eligible_for_standard_comparison=False,
      eligible_for_exploratory_analysis=False,
      missing_fields=missing_fields,
    )

  def _has_version_mismatch(self, manifest, expected_versions):
    for field, expected in expected_versions.items():
      if expected is not None and manifest.get(field) != expected:
        return True
    return False
