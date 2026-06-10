"""analysis intake reader."""
import json
from pathlib import Path

import yaml


class IntakeReader:
  """evaluation と conformance-evaluation の成果物を読み込む。"""

  def read(
    self,
    *,
    evaluation_root,
    conformance_root,
    output_root,
    analysis_logic_version,
    generated_at,
  ):
    evaluation_root = Path(evaluation_root)
    conformance_root = Path(conformance_root)
    output_root = Path(output_root)

    failures = []
    evaluation_manifest = {}

    if not evaluation_root.is_dir():
      failures.append(
        self._failure(
          "upstream_evaluation_missing",
          evaluation_root,
          detected_at=generated_at,
          failure_kind="missing",
        )
      )
    else:
      try:
        evaluation_manifest = self._read_evaluation_inputs(evaluation_root)
      except (OSError, json.JSONDecodeError, yaml.YAMLError) as exc:
        failures.append(
          self._failure(
            "upstream_evaluation_unreadable",
            evaluation_root,
            str(exc),
            detected_at=generated_at,
            failure_kind="unreadable",
          )
        )
      else:
        if self._has_stale_entries(evaluation_root):
          failures.append(
            self._failure(
              "upstream_evaluation_stale",
              evaluation_root,
              detected_at=generated_at,
              failure_kind="stale",
            )
          )

    if not conformance_root.is_dir():
      failures.append(
        self._failure(
          "conformance_evaluation_missing",
          conformance_root,
          detected_at=generated_at,
          failure_kind="missing",
        )
      )
    elif not failures:
      try:
        self._read_conformance_inputs(conformance_root)
      except (OSError, json.JSONDecodeError) as exc:
        failures.append(
          self._failure(
            "conformance_evaluation_missing",
            conformance_root,
            str(exc),
            detected_at=generated_at,
            failure_kind="unreadable",
          )
        )

    self._write_outputs(
      output_root=output_root,
      failures=failures,
      evaluation_manifest=evaluation_manifest,
      analysis_logic_version=analysis_logic_version,
      generated_at=generated_at,
    )
    return {
      "ok": not failures,
      "failures": failures,
    }

  @staticmethod
  def _failure(reason, path, detail=None, *, detected_at, failure_kind):
    failure = {
      "failure_id": f"{reason}:{Path(path).name or 'root'}",
      "intake_failure_reason": reason,
      "source_path": str(path),
      "affected_destinations": ["dashboard", "weekly", "audit", "reports"],
      "detected_at": detected_at,
      "failure_kind": failure_kind,
    }
    if detail:
      failure["detail"] = detail
    return failure

  @staticmethod
  def _read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))

  @staticmethod
  def _read_yaml(path):
    return yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}

  def _read_evaluation_inputs(self, evaluation_root):
    self._read_json(evaluation_root / "comparisons" / "treatment_comparisons.json")
    self._read_json(evaluation_root / "classifications" / "exclusion_report.json")
    return self._read_yaml(evaluation_root / "manifests" / "analysis_run_manifest.yaml")

  def _read_conformance_inputs(self, conformance_root):
    candidates = sorted(conformance_root.glob("*.json"))
    if not candidates:
      raise FileNotFoundError("conformance json artifact is missing")
    for candidate in candidates:
      self._read_json(candidate)

  def _has_stale_entries(self, evaluation_root):
    path = evaluation_root / "manifests" / "staleness_register.json"
    if not path.exists():
      return False
    payload = self._read_json(path)
    return any(entry.get("stale") is True for entry in payload.get("entries", []))

  def _write_outputs(
    self,
    *,
    output_root,
    failures,
    evaluation_manifest,
    analysis_logic_version,
    generated_at,
  ):
    manifests_dir = output_root / "shared" / "manifests"
    manifests_dir.mkdir(parents=True, exist_ok=True)
    (manifests_dir / "intake_failure_report.json").write_text(
      json.dumps({"entries": failures}, ensure_ascii=False, indent=2) + "\n",
      encoding="utf-8",
    )
    manifest = {
      "analysis_logic_version": analysis_logic_version,
      "input_run_set": evaluation_manifest.get("input_run_set", []),
      "generated_at": generated_at,
      "metric_set_version": evaluation_manifest.get("metric_set_version"),
      "phase_metric_profile_version": evaluation_manifest.get(
        "phase_metric_profile_version"
      ),
      "comparison_contract_version": evaluation_manifest.get(
        "comparison_contract_version"
      ),
      "protocol_version_coverage": evaluation_manifest.get(
        "protocol_version_coverage",
        [],
      ),
      "runtime_version_coverage": evaluation_manifest.get(
        "runtime_version_coverage",
        [],
      ),
      "prompt_set_version_coverage": evaluation_manifest.get(
        "prompt_set_version_coverage",
        [],
      ),
      "analysis_run_id": evaluation_manifest.get("analysis_run_id"),
      "analysis_started_at": evaluation_manifest.get("analysis_started_at"),
      "analysis_completed_at": generated_at,
      "output_artifact_ids": ["intake_failure_report"],
    }
    (manifests_dir / "analysis_manifest.yaml").write_text(
      yaml.safe_dump(manifest, allow_unicode=True, sort_keys=False),
      encoding="utf-8",
    )
