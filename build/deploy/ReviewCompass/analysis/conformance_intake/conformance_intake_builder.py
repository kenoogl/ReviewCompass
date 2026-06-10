"""conformance intake writer."""
import json
from pathlib import Path

import jsonschema


_SCHEMA_PATH = Path(__file__).with_name("conformance_intake.schema.json")


class ConformanceIntakeBuilder:
  """shared/conformance/conformance_intake.json を書き出す。"""

  def write(
    self,
    output_root,
    *,
    conformance_run_ref,
    assessment_summary,
    violation_findings,
    compliance_rate,
    included_disciplines,
    intake_at,
  ):
    payload = {
      "conformance_run_ref": conformance_run_ref,
      "assessment_summary": assessment_summary,
      "violation_findings": violation_findings,
      "compliance_rate": compliance_rate,
      "included_disciplines": included_disciplines,
      "intake_at": intake_at,
    }
    self._validate(payload)
    path = Path(output_root) / "shared" / "conformance" / "conformance_intake.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
      json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
      encoding="utf-8",
    )
    return path

  @staticmethod
  def _schema():
    return json.loads(_SCHEMA_PATH.read_text(encoding="utf-8"))

  def _validate(self, payload):
    try:
      jsonschema.Draft202012Validator(self._schema()).validate(payload)
    except jsonschema.ValidationError as exc:
      missing = sorted(exc.validator_value) if exc.validator == "required" else []
      if missing:
        raise ValueError(", ".join(missing)) from exc
      raise ValueError(exc.message) from exc
