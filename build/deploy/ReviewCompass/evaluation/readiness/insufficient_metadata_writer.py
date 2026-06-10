"""insufficient_metadata_report.json の生成。"""
import json
from pathlib import Path


class InsufficientMetadataWriter:
  """classifications/insufficient_metadata_report.json を生成する。"""

  def write(self, analysis_root, results, *, detected_at):
    path = Path(analysis_root) / "classifications" / "insufficient_metadata_report.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    entries = []
    for result in results:
      if result.ok:
        continue
      entries.append({
        "run_id": result.run_id,
        "missing_fields": result.missing_fields,
        "evidence_class": result.evidence_class,
        "affected_derived_artifacts": result.affected_derived_artifacts,
        "detected_at": detected_at,
      })
    path.write_text(
      json.dumps({"entries": entries}, ensure_ascii=False, indent=2),
      encoding="utf-8",
    )
    return path
