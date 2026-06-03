"""evidence_register.json writer."""
import json
from pathlib import Path

import jsonschema

from .binding_rules import maturity_for_evidence, preliminary_caveat_ref


_SCHEMA_PATH = Path(__file__).with_name("evidence_register.schema.json")


class EvidenceRegisterBuilder:
  """shared/evidence_register.json を書き出す。"""

  def write(self, output_root, *, evidences):
    entries = []
    for evidence in evidences:
      entry = self._normalize_evidence(evidence)
      if entry is not None:
        entries.append(entry)
    payload = {"entries": entries}
    self._validate(payload)
    path = Path(output_root) / "shared" / "evidence_register.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
      json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
      encoding="utf-8",
    )
    return path

  @staticmethod
  def _normalize_evidence(evidence):
    evidence_class = evidence["evidence_class"]
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
      "review_mode": evidence["review_mode"],
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
