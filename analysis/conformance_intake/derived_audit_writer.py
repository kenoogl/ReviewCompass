"""derived audit conformance writer."""
import json
from pathlib import Path

from analysis.common.reference_format import artifact_ref


SOURCE_INTAKE_PATH = "shared/conformance/conformance_intake.json"


class DerivedAuditWriter:
  """destinations/audit/conformance_violations_detail.json を書き出す。"""

  def write(self, output_root, *, intake_path):
    intake = json.loads(Path(intake_path).read_text(encoding="utf-8"))
    payload = {
      "source_intake_ref": artifact_ref(
        ref_type="analysis_artifact",
        target_path=SOURCE_INTAKE_PATH,
      ),
      "conformance_run_ref": intake["conformance_run_ref"],
      "violation_findings": intake["violation_findings"],
      "included_disciplines": intake["included_disciplines"],
    }
    path = Path(output_root) / "destinations" / "audit" / "conformance_violations_detail.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
      json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
      encoding="utf-8",
    )
    return path
