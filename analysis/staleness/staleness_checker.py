"""staleness propagation and regeneration register writer."""
from datetime import datetime, timezone
import json
from pathlib import Path

import jsonschema


REGENERATION_STATUSES = {
  "pending",
  "in_progress",
  "completed",
  "failed",
}

_SCHEMA_PATH = Path(__file__).with_name("staleness_register.schema.json")
_REGISTER_PATH = "shared/manifests/staleness_register.json"


class StalenessChecker:
  """timestamp 比較で再生成対象を登録する。"""

  def write_register(
    self,
    output_root,
    *,
    derived_artifacts,
    evaluation_staleness_entries,
    dependency_artifacts,
    conformance_results,
    detected_at,
  ):
    entries = self.detect(
      derived_artifacts=derived_artifacts,
      evaluation_staleness_entries=evaluation_staleness_entries,
      dependency_artifacts=dependency_artifacts,
      conformance_results=conformance_results,
      detected_at=detected_at,
    )
    payload = {"entries": entries}
    self._validate(payload)
    path = Path(output_root) / _REGISTER_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
      json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
      encoding="utf-8",
    )
    return path

  def detect(
    self,
    *,
    derived_artifacts,
    evaluation_staleness_entries,
    dependency_artifacts,
    conformance_results,
    detected_at,
  ):
    sources = [
      *self._evaluation_sources(evaluation_staleness_entries),
      *self._dependency_sources(dependency_artifacts),
      *self._conformance_sources(conformance_results),
    ]
    return [
      {
        "derived_artifact_ref": derived["derived_artifact_ref"],
        "stale_source_ref": source["stale_source_ref"],
        "detected_at": detected_at,
        "regeneration_status": "pending",
      }
      for derived in derived_artifacts
      for source in sources
      if self._is_newer(source["updated_at"], derived["generated_at"])
    ]

  @staticmethod
  def propagate_stale(artifacts, *, stale_source_ref, stale_reason):
    """派生成果物に陳腐化標識を伝播したコピーを返す。"""
    propagated = []
    for artifact in artifacts:
      entry = dict(artifact)
      entry["stale"] = True
      entry["stale_reason"] = stale_reason
      entry["stale_source_ref"] = stale_source_ref
      propagated.append(entry)
    return propagated

  @staticmethod
  def _evaluation_sources(entries):
    return [
      {
        "stale_source_ref": entry["stale_source_ref"],
        "updated_at": entry["updated_at"],
      }
      for entry in entries
    ]

  @staticmethod
  def _dependency_sources(artifacts):
    return [
      {
        "stale_source_ref": artifact["artifact_ref"],
        "updated_at": artifact["updated_at"],
      }
      for artifact in artifacts
    ]

  @staticmethod
  def _conformance_sources(results):
    return [
      {
        "stale_source_ref": result["result_ref"],
        "updated_at": result["updated_at"],
      }
      for result in results
    ]

  @staticmethod
  def _is_newer(source_updated_at, derived_generated_at):
    return _parse_timestamp(source_updated_at) > _parse_timestamp(derived_generated_at)

  @staticmethod
  def _schema():
    return json.loads(_SCHEMA_PATH.read_text(encoding="utf-8"))

  def _validate(self, payload):
    try:
      jsonschema.Draft202012Validator(self._schema()).validate(payload)
    except jsonschema.ValidationError as exc:
      raise ValueError(exc.message) from exc


def _parse_timestamp(value):
  if value.endswith("Z"):
    value = f"{value[:-1]}+00:00"
  parsed = datetime.fromisoformat(value)
  if parsed.tzinfo is None:
    return parsed.replace(tzinfo=timezone.utc)
  return parsed
