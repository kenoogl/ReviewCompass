"""table source bundle writer."""
import json
from pathlib import Path

import jsonschema


_SCHEMA_PATH = Path(__file__).with_name("table_bundle.schema.json")


class TableBundleBuilder:
  """figures_tables/table_source_bundles/<table_id>.json を書き出す。"""

  def write(
    self,
    output_root,
    *,
    table_id,
    source_artifact_refs,
    field_projection,
    maturity_label,
    applicable_destinations,
    caveat_refs=None,
  ):
    payload = {
      "table_id": table_id,
      "source_artifact_refs": source_artifact_refs,
      "field_projection": field_projection,
      "maturity_label": maturity_label,
      "applicable_destinations": applicable_destinations,
    }
    if caveat_refs is not None:
      payload["caveat_refs"] = caveat_refs
    self._validate(payload)
    path = (
      Path(output_root)
      / "figures_tables"
      / "table_source_bundles"
      / f"{table_id}.json"
    )
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
