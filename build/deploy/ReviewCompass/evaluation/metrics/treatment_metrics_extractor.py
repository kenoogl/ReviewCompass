"""処理方式レベルメトリクス抽出器。"""


class TreatmentMetricsExtractor:
  """所見メトリクス集合から treatment レベル集計を生成する。"""

  def extract(self, finding_metrics_list):
    treatments = {}
    for metrics in finding_metrics_list:
      treatment = metrics["treatment"]
      current = treatments.setdefault(treatment, {
        "run_ids": [],
        "target_ids": [],
        "finding_count": 0,
        "counter_evidence_count": 0,
      })
      current["run_ids"].append(metrics["run_id"])
      current["target_ids"].append(metrics["target_id"])
      counts = metrics["counter_status_counts"]
      finding_count = sum(counts.values())
      current["finding_count"] += finding_count
      current["counter_evidence_count"] += counts.get("counter_evidence_raised", 0)

    for current in treatments.values():
      denominator = current["finding_count"]
      current["counter_evidence_rate"] = (
        current["counter_evidence_count"] / denominator if denominator else 0
      )
    return {
      "artifact_id": "treatment_metrics",
      "metric_level": "treatment",
      "treatments": treatments,
    }
