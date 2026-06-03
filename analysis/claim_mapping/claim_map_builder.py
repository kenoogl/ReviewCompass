"""claim_map.json writer."""
import json
from pathlib import Path

import jsonschema


_SCHEMA_PATH = Path(__file__).with_name("claim_map.schema.json")


class ClaimMapBuilder:
  """shared/claim_map.json を書き出す。"""

  def write(self, output_root, *, claims):
    payload = {
      "claims": [self._normalize_claim(claim) for claim in claims],
    }
    self._validate(payload)
    path = Path(output_root) / "shared" / "claim_map.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
      json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
      encoding="utf-8",
    )
    return path

  @staticmethod
  def _normalize_claim(claim):
    normalized = dict(claim)
    normalized.setdefault("provenance_refs", [])
    normalized.setdefault("caveat_refs", [])
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
