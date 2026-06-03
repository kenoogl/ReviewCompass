"""所見レベルメトリクス抽出器。"""
import json
from pathlib import Path


class FindingMetricsExtractor:
  """review_case.json の findings から所見メトリクスを抽出する。"""

  def extract(self, run_dir):
    run_dir = Path(run_dir)
    review_case_path = run_dir / "review_case.json"
    review_case = json.loads(review_case_path.read_text(encoding="utf-8"))
    findings = review_case.get("findings", [])
    by_severity = {}
    counter_status_counts = {
      "counter_evidence_raised": 0,
      "no_counter_evidence_after_challenge": 0,
      "not_assessed": 0,
    }
    for finding in findings:
      severity = finding["severity"]
      by_severity[severity] = by_severity.get(severity, 0) + 1
      counter_status = finding["counter_status"]
      counter_status_counts[counter_status] = counter_status_counts.get(counter_status, 0) + 1

    return {
      "artifact_id": "finding_metrics",
      "metric_level": "finding",
      "run_id": review_case["run_id"],
      "target_id": review_case["target_id"],
      "phase_profile": review_case["phase_profile"],
      "treatment": review_case["treatment"],
      "by_severity": by_severity,
      "counter_status_counts": counter_status_counts,
      "derivation": {
        "source_artifact": str(review_case_path),
        "source_fields": ["findings[].severity", "findings[].counter_status"],
      },
    }
