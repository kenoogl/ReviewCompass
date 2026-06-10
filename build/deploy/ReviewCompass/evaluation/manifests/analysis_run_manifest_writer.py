"""analysis_run_manifest.yaml の生成。"""
from pathlib import Path

import yaml

_REQUIRED_FIELDS = [
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
]


class AnalysisRunManifestWriter:
  """manifests/analysis_run_manifest.yaml を生成する。"""

  def write(self, analysis_root, **fields):
    missing = [field for field in _REQUIRED_FIELDS if field not in fields]
    if missing:
      raise ValueError(f"analysis_run_manifest required fields missing: {missing}")
    path = Path(analysis_root) / "manifests" / "analysis_run_manifest.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {field: fields[field] for field in _REQUIRED_FIELDS}
    path.write_text(
      yaml.safe_dump(payload, allow_unicode=True, sort_keys=False),
      encoding="utf-8",
    )
    return path
