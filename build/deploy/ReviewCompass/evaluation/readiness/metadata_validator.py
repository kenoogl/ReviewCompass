"""評価準備メタデータ検査器。"""
from dataclasses import dataclass
from pathlib import Path

import yaml

_THIS_DIR = Path(__file__).resolve().parent
_REQUIRED_FIELDS_SCHEMA = _THIS_DIR / "required_fields_schema.yaml"


@dataclass(frozen=True)
class MetadataValidationResult:
  """必須メタデータ検査結果。"""

  run_id: str
  ok: bool
  standard_aggregation_allowed: bool
  missing_fields: list
  evidence_class: str
  affected_derived_artifacts: list
  failure_kind: str


class MetadataValidator:
  """標準集計前に必須メタデータを検査する。"""

  def __init__(self):
    schema = yaml.safe_load(_REQUIRED_FIELDS_SCHEMA.read_text(encoding="utf-8"))
    self.required_fields = list(schema["required_fields"])

  def validate(self, run_dir):
    run_dir = Path(run_dir)
    manifest_path = run_dir / "run_manifest.yaml"
    try:
      manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError):
      return MetadataValidationResult(
        run_id=None,
        ok=False,
        standard_aggregation_allowed=False,
        missing_fields=self.required_fields,
        evidence_class="invalid",
        affected_derived_artifacts=[],
        failure_kind="fatal",
      )

    missing = [field for field in self.required_fields if not manifest.get(field)]
    if missing:
      return MetadataValidationResult(
        run_id=manifest.get("run_id"),
        ok=False,
        standard_aggregation_allowed=False,
        missing_fields=missing,
        evidence_class="analysis_blocked",
        affected_derived_artifacts=self._affected_artifacts(),
        failure_kind="analysis_blocked",
      )

    return MetadataValidationResult(
      run_id=manifest["run_id"],
      ok=True,
      standard_aggregation_allowed=True,
      missing_fields=[],
      evidence_class=manifest["evidence_class"],
      affected_derived_artifacts=[],
      failure_kind="none",
    )

  def _affected_artifacts(self):
    return [
      "metrics/run_metrics.json",
      "metrics/finding_metrics.json",
      "metrics/treatment_metrics.json",
      "comparisons/treatment_comparisons.json",
      "comparisons/phase_comparisons.json",
    ]
