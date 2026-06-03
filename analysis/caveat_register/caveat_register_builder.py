"""caveat_register.json writer."""
import json
from pathlib import Path

import jsonschema


_SCHEMA_PATH = Path(__file__).with_name("caveat_register.schema.json")


class CaveatRegisterBuilder:
  """shared/caveat_register.json を書き出す。"""

  def write(self, output_root, *, caveats):
    payload = {
      "entries": [self._normalize_caveat(caveat) for caveat in caveats],
    }
    self._validate(payload)
    path = Path(output_root) / "shared" / "caveat_register.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
      json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
      encoding="utf-8",
    )
    return path

  @staticmethod
  def _normalize_caveat(caveat):
    normalized = dict(caveat)
    normalized.setdefault("applies_to_claim_refs", [])
    normalized.setdefault("applies_to_artifact_refs", [])
    return normalized

  @staticmethod
  def _schema():
    return json.loads(_SCHEMA_PATH.read_text(encoding="utf-8"))

  def _validate(self, payload):
    try:
      jsonschema.Draft202012Validator(self._schema()).validate(payload)
    except jsonschema.ValidationError as exc:
      if exc.validator == "anyOf":
        raise ValueError("applies_to_claim_refs or applies_to_artifact_refs required") from exc
      missing = sorted(exc.validator_value) if exc.validator == "required" else []
      if missing:
        raise ValueError(", ".join(missing)) from exc
      raise ValueError(exc.message) from exc
