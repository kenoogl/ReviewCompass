"""mode_diff.json writer."""
import json
from pathlib import Path

import jsonschema
import yaml


_SCHEMA_PATH = Path(__file__).with_name("mode_diff.schema.json")
_REPO_ROOT = Path(__file__).resolve().parents[2]
_FOUNDATION_CONTRACT = _REPO_ROOT / "runtime" / "foundation" / "metadata_contract.yaml"


def foundation_review_modes():
  """foundation metadata contract の review_mode 語彙を返す。"""
  payload = yaml.safe_load(_FOUNDATION_CONTRACT.read_text(encoding="utf-8"))
  return set(payload["vocabularies"]["review_mode"])


class ModeDiffBuilder:
  """shared/convergence/mode_diff.json を書き出す。"""

  def write(self, output_root, *, entries):
    payload = {"entries": [self._normalize_entry(entry) for entry in entries]}
    self._validate(payload)
    path = Path(output_root) / "shared" / "convergence" / "mode_diff.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
      json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
      encoding="utf-8",
    )
    return path

  @staticmethod
  def _normalize_entry(entry):
    normalized = dict(entry)
    review_mode = normalized.get("review_mode")
    if review_mode not in foundation_review_modes():
      raise ValueError("review_mode")
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
