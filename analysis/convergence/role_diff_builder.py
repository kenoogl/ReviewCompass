"""role_diff.json writer."""
import json
from pathlib import Path

import jsonschema


_SCHEMA_PATH = Path(__file__).with_name("role_diff.schema.json")


class RoleDiffBuilder:
  """shared/convergence/role_diff.json を書き出す。"""

  def write(self, output_root, *, entries):
    payload = {"entries": [self._normalize_entry(entry) for entry in entries]}
    self._validate(payload)
    path = Path(output_root) / "shared" / "convergence" / "role_diff.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
      json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
      encoding="utf-8",
    )
    return path

  @staticmethod
  def _normalize_entry(entry):
    normalized = dict(entry)
    role = normalized.get("role")
    summary = normalized.get("findings_summary") or {}
    if role == "judgment" and "by_final_label" not in summary:
      raise ValueError("by_final_label")
    if role == "adversarial" and "by_counter_status" not in summary:
      raise ValueError("by_counter_status")
    return normalized

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
