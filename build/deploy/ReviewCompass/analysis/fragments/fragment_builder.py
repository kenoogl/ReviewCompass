"""report fragment writer."""
import json
from pathlib import Path

import jsonschema


FRAGMENT_TYPES = {
  "claim_summary",
  "method_note",
  "limitation_note",
  "comparison_summary",
  "trend_summary",
}

MATURITY_ORDER = {
  "mature": 0,
  "preliminary": 1,
  "exploratory": 2,
}

_SCHEMA_PATH = Path(__file__).with_name("fragment.schema.json")


def conservative_maturity(source_artifact_refs):
  """出典群のうち最も保守的な maturity_label を返す。"""
  labels = [
    ref.get("maturity_label", "preliminary")
    for ref in source_artifact_refs
  ]
  unknown = [label for label in labels if label not in MATURITY_ORDER]
  if unknown:
    raise ValueError(f"unknown maturity_label: {', '.join(sorted(set(unknown)))}")
  return max(labels, key=lambda label: MATURITY_ORDER[label])


def source_maturity_labels(source_artifact_refs):
  """target_id ごとの出典 maturity_label を返す。"""
  values = {}
  for ref in source_artifact_refs:
    target_id = ref.get("target_id")
    if target_id is not None:
      values[str(target_id)] = ref.get("maturity_label", "preliminary")
  return values


class FragmentBuilder:
  """fragments/<fragment_id>.json を書き出す。"""

  def write(
    self,
    output_root,
    *,
    fragment_id,
    fragment_type,
    source_artifact_refs,
    text_stub,
    applicable_destinations,
    caveat_refs=None,
  ):
    payload = {
      "fragment_id": fragment_id,
      "fragment_type": fragment_type,
      "source_artifact_refs": source_artifact_refs,
      "maturity_label": conservative_maturity(source_artifact_refs),
      "source_maturity_labels": source_maturity_labels(source_artifact_refs),
      "text_stub": text_stub,
      "applicable_destinations": applicable_destinations,
    }
    if caveat_refs is not None:
      payload["caveat_refs"] = caveat_refs
    self._validate(payload)
    path = Path(output_root) / "fragments" / f"{fragment_id}.json"
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
      if exc.validator == "enum" and "fragment_type" in str(exc.absolute_path):
        raise ValueError("fragment_type") from exc
      missing = sorted(exc.validator_value) if exc.validator == "required" else []
      if missing:
        raise ValueError(", ".join(missing)) from exc
      raise ValueError(exc.message) from exc
