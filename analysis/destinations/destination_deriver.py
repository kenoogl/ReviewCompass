"""destination-specific derived output writer."""
import json
from datetime import datetime, timezone
from pathlib import Path

import jsonschema
import yaml

from analysis.caveat_register.mixed_review_mode_detector import (
  detect_mixed_review_mode,
)
from analysis.common.reference_format import artifact_ref


_SCHEMA_PATH = Path(__file__).with_name("manifest.schema.json")
_EVIDENCE_REGISTER_PATH = "shared/evidence_register.json"
_CAVEAT_REGISTER_PATH = "shared/caveat_register.json"

_DESTINATION_SPECS = {
  "dashboard": {
    "granularity_profile": "operational",
    "summary_level": "summary",
    "outputs": {
      "operations_summary.json": "operations_summary",
    },
  },
  "weekly": {
    "granularity_profile": "weekly",
    "summary_level": "summary",
    "outputs": {
      "trend_summary.json": "trend_summary",
    },
  },
  "audit": {
    "granularity_profile": "event",
    "summary_level": "detail",
    "outputs": {
      "invalidation_index.json": "invalidation_index",
      "validator_failure_trace.json": "validator_failure_trace",
      "discipline_violation_index.json": "discipline_violation_index",
    },
  },
  "reports": {
    "granularity_profile": "claim",
    "summary_level": "detail",
    "outputs": {
      "claim_evidence_trace.json": "claim_evidence_trace",
      "treatment_comparison_report.json": "treatment_comparison_report",
      "mode_comparison_report.json": "mode_comparison_report",
    },
  },
}


class DestinationDeriver:
  """destinations 配下の派生成果物と manifest を書き出す。"""

  def derive(
    self,
    output_root,
    *,
    analysis_logic_version,
    derivation_contract_version,
    evidences,
    caveats,
  ):
    root = Path(output_root)
    evidence_entries = list(evidences)
    caveat_entries = self._caveat_entries(root, evidence_entries, caveats)
    evidence_refs = self._evidence_refs(evidence_entries)
    caveat_refs = self._caveat_refs(caveat_entries)
    review_mode_mixed = self._review_mode_mixed(evidence_entries)
    created = []

    created.append(
      self._write_json(
        root / _CAVEAT_REGISTER_PATH,
        {"entries": caveat_entries},
        root,
      )
    )

    for destination, spec in _DESTINATION_SPECS.items():
      created.extend(
        self._write_destination(
          root,
          destination=destination,
          spec=spec,
          analysis_logic_version=analysis_logic_version,
          derivation_contract_version=derivation_contract_version,
          evidence_entries=evidence_entries,
          evidence_refs=evidence_refs,
          caveat_refs=caveat_refs,
          review_mode_mixed=review_mode_mixed,
        )
      )

    return created

  def _write_destination(
    self,
    root,
    *,
    destination,
    spec,
    analysis_logic_version,
    derivation_contract_version,
    evidence_entries,
    evidence_refs,
    caveat_refs,
    review_mode_mixed,
  ):
    created = []
    manifest_path = root / "destinations" / destination / "manifest.yaml"
    manifest = {
      "destination": destination,
      "analysis_logic_version": analysis_logic_version,
      "derivation_contract_version": derivation_contract_version,
      "included_evidence_refs": evidence_refs,
      "included_caveat_refs": caveat_refs,
      "granularity_profile": spec["granularity_profile"],
      "summary_level": spec["summary_level"],
      "review_mode_mixed": review_mode_mixed,
    }
    superseded = self._superseded_versions(
      manifest_path,
      derivation_contract_version,
      destination,
    )
    if superseded:
      manifest["superseded_versions"] = superseded
    self._validate_manifest(manifest)
    created.append(self._write_yaml(manifest_path, manifest, root))

    for filename, output_type in spec["outputs"].items():
      payload = self._destination_payload(
        destination=destination,
        output_type=output_type,
        manifest_ref=artifact_ref(
          ref_type="destination_manifest",
          target_path=f"destinations/{destination}/manifest.yaml",
        ),
        evidence_entries=evidence_entries,
        evidence_refs=evidence_refs,
        caveat_refs=caveat_refs,
      )
      path = root / "destinations" / destination / filename
      created.append(self._write_json(path, payload, root))

    return created

  def _caveat_entries(self, root, evidence_entries, caveats):
    entries = self._existing_caveat_entries(root)
    mixed_caveat = detect_mixed_review_mode(evidence_entries)
    new_entries = [dict(caveat) for caveat in caveats]
    if mixed_caveat is not None:
      new_entries.append(mixed_caveat)
    seen = {entry.get("caveat_id") for entry in entries}
    for entry in new_entries:
      caveat_id = entry.get("caveat_id")
      if caveat_id in seen:
        continue
      entries.append(entry)
      seen.add(caveat_id)
    return entries

  @staticmethod
  def _existing_caveat_entries(root):
    path = Path(root) / _CAVEAT_REGISTER_PATH
    if not path.is_file():
      return []
    payload = json.loads(path.read_text(encoding="utf-8"))
    return [dict(entry) for entry in payload.get("entries", [])]

  @staticmethod
  def _evidence_refs(evidence_entries):
    return [
      artifact_ref(
        ref_type="evidence_entry",
        target_path=_EVIDENCE_REGISTER_PATH,
        target_id=entry["evidence_id"],
      )
      for entry in evidence_entries
    ]

  @staticmethod
  def _caveat_refs(caveat_entries):
    return [
      artifact_ref(
        ref_type="caveat_entry",
        target_path=_CAVEAT_REGISTER_PATH,
        target_id=entry["caveat_id"],
      )
      for entry in caveat_entries
    ]

  @staticmethod
  def _review_mode_mixed(evidence_entries):
    return len({entry["review_mode"] for entry in evidence_entries}) > 1

  def _destination_payload(
    self,
    *,
    destination,
    output_type,
    manifest_ref,
    evidence_entries,
    evidence_refs,
    caveat_refs,
  ):
    payload = {
      "output_type": output_type,
      "manifest_ref": manifest_ref,
      "included_evidence_refs": evidence_refs,
      "included_caveat_refs": caveat_refs,
    }
    if destination == "dashboard":
      payload.update(self._dashboard_payload(evidence_entries))
    elif destination == "weekly":
      payload.update(self._weekly_payload(evidence_entries))
    elif destination == "audit":
      payload.update(self._audit_payload(output_type, evidence_entries))
    elif destination == "reports":
      payload.update(self._reports_payload(output_type, evidence_entries))
    return payload

  def _dashboard_payload(self, evidence_entries):
    return {
      "findings_by_severity": self._count_by(evidence_entries, "severity"),
      "findings_by_phase": self._count_by(evidence_entries, "phase"),
      "in_progress_procedure_states": [],
      "derived_at": self._now_iso(),
      "coverage_period": self._coverage_period(evidence_entries),
    }

  def _weekly_payload(self, evidence_entries):
    return {
      "weekly_deltas": [],
      "top_findings": self._top_findings(evidence_entries),
      "compliance_rate_change": None,
      "period": self._coverage_period(evidence_entries),
    }

  @staticmethod
  def _audit_payload(output_type, evidence_entries):
    if output_type == "invalidation_index":
      return {"invalidation_markers": []}
    if output_type == "validator_failure_trace":
      return {
        "validator_failures": [
          entry for entry in evidence_entries
          if entry.get("validator_status") == "failed"
        ]
      }
    if output_type == "discipline_violation_index":
      return {"discipline_violations": []}
    return {}

  @staticmethod
  def _reports_payload(output_type, evidence_entries):
    if output_type == "claim_evidence_trace":
      return {
        "claim_evidence_trace": [
          {
            "claim_id": entry.get("claim_id"),
            "evidence_id": entry.get("evidence_id"),
          }
          for entry in evidence_entries
          if entry.get("claim_id")
        ]
      }
    if output_type == "treatment_comparison_report":
      return {"treatment_comparisons": DestinationDeriver._count_by(evidence_entries, "treatment")}
    if output_type == "mode_comparison_report":
      return {
        "mode_comparisons": DestinationDeriver._count_by(
          evidence_entries,
          "review_mode",
        )
      }
    return {}

  @staticmethod
  def _count_by(evidence_entries, key):
    counts = {}
    for entry in evidence_entries:
      value = entry.get(key)
      if value is None:
        continue
      counts[value] = counts.get(value, 0) + 1
    return counts

  @staticmethod
  def _top_findings(evidence_entries):
    return [
      {
        "finding_id": entry.get("finding_id"),
        "severity": entry.get("severity"),
        "evidence_id": entry.get("evidence_id"),
      }
      for entry in evidence_entries
      if entry.get("finding_id")
    ]

  @staticmethod
  def _coverage_period(evidence_entries):
    timestamps = sorted(
      entry["generated_at"]
      for entry in evidence_entries
      if entry.get("generated_at")
    )
    return {
      "start": timestamps[0] if timestamps else None,
      "end": timestamps[-1] if timestamps else None,
    }

  @staticmethod
  def _now_iso():
    return datetime.now(timezone.utc).isoformat()

  @staticmethod
  def _superseded_versions(manifest_path, derivation_contract_version, destination):
    if not manifest_path.is_file():
      return []
    previous = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    previous_version = previous["derivation_contract_version"]
    if previous_version == derivation_contract_version:
      return list(previous.get("superseded_versions", []))
    return [
      *previous.get("superseded_versions", []),
      {
        "version": previous_version,
        "manifest_path": f"destinations/{destination}/manifest.yaml",
      },
    ]

  @staticmethod
  def _write_json(path, payload, root):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
      json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
      encoding="utf-8",
    )
    return str(path.relative_to(root))

  @staticmethod
  def _write_yaml(path, payload, root):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
      yaml.safe_dump(payload, allow_unicode=True, sort_keys=False),
      encoding="utf-8",
    )
    return str(path.relative_to(root))

  @staticmethod
  def _schema():
    return json.loads(_SCHEMA_PATH.read_text(encoding="utf-8"))

  def _validate_manifest(self, payload):
    try:
      jsonschema.Draft202012Validator(self._schema()).validate(payload)
    except jsonschema.ValidationError as exc:
      raise ValueError(exc.message) from exc
