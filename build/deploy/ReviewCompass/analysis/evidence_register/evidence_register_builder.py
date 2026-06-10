"""evidence_register.json writer."""
import json
from pathlib import Path

import jsonschema

from .binding_rules import (
  foundation_vocabulary,
  maturity_for_evidence,
  preliminary_caveat_ref,
)


_SCHEMA_PATH = Path(__file__).with_name("evidence_register.schema.json")
_EXCLUSION_REGISTER_PATH = "shared/evidence_exclusion_register.json"


class EvidenceRegisterBuilder:
  """shared/evidence_register.json を書き出す。"""

  def write(self, output_root, *, evidences):
    root = Path(output_root)
    entries = []
    exclusions = []
    for evidence in evidences:
      entry = self._normalize_evidence(evidence)
      if entry is not None:
        entries.append(entry)
      else:
        exclusions.append(self._exclusion_entry(evidence))
    payload = {"entries": entries}
    self._validate(payload)
    path = self._write_json(root / "shared" / "evidence_register.json", payload)
    if exclusions:
      self._write_json(
        root / _EXCLUSION_REGISTER_PATH,
        {"entries": exclusions},
      )
    return path

  @staticmethod
  def _normalize_evidence(evidence):
    evidence_class = evidence["evidence_class"]
    if evidence_class not in foundation_vocabulary("evidence_class"):
      raise ValueError(f"unknown evidence_class: {evidence_class}")
    review_mode = evidence["review_mode"]
    if review_mode not in foundation_vocabulary("review_mode"):
      raise ValueError(f"unknown review_mode: {review_mode}")
    maturity_label = maturity_for_evidence(
      evidence_class,
      eligible_for_standard_comparison=evidence.get(
        "eligible_for_standard_comparison",
        False,
      ),
    )
    if maturity_label is None:
      return None

    entry = {
      "evidence_id": evidence["evidence_id"],
      "artifact_ref": evidence["artifact_ref"],
      "source_analysis_manifest_ref": evidence["source_analysis_manifest_ref"],
      "input_run_set_ref": evidence["input_run_set_ref"],
      "evidence_class": evidence_class,
      "review_mode": review_mode,
      "maturity_label": maturity_label,
      "caveat_refs": list(evidence.get("caveat_refs", [])),
      "supersedes": list(evidence.get("supersedes", [])),
      "superseded_by": list(evidence.get("superseded_by", [])),
      "stale": evidence["stale"],
      "generated_at": evidence["generated_at"],
    }
    if evidence_class == "exploratory" and not entry["caveat_refs"]:
      entry["caveat_refs"].append(preliminary_caveat_ref())
    for optional in ("stale_reason", "stale_source_ref"):
      if optional in evidence:
        entry[optional] = evidence[optional]
    return entry

  @staticmethod
  def _exclusion_entry(evidence):
    return {
      "evidence_id": evidence["evidence_id"],
      "artifact_ref": evidence["artifact_ref"],
      "evidence_class": evidence["evidence_class"],
      "exclusion_reason": evidence["evidence_class"],
    }

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

  @staticmethod
  def _write_json(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
      json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
      encoding="utf-8",
    )
    return path
