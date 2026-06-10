"""処理方式比較の生成。"""
import json
from pathlib import Path

from comparison.mode_population_rule import ModePopulationRule
from comparison.valid_population_rule import ValidPopulationRule
from comparison.version_consistency_validator import VersionConsistencyValidator


class TreatmentComparisonBuilder:
  """comparisons/treatment_comparisons.json を生成する。"""

  def write(self, analysis_root, runs):
    standard = ModePopulationRule().slice(runs)["standard_runtime_mediated"]
    included = ValidPopulationRule().apply(standard)
    by_treatment = {}
    for run in included:
      bucket = by_treatment.setdefault(run["treatment"], {
        "included_runs": [],
        "finding_count": 0,
      })
      bucket["included_runs"].append(run["run_id"])
      bucket["finding_count"] += run.get("finding_count", 0)
    version_result = VersionConsistencyValidator().validate(included)
    payload = {
      "comparison_type": "treatment",
      "included_runs": [run["run_id"] for run in included],
      "by_treatment": by_treatment,
      "version_consistency": {
        "ok": version_result.ok,
        "reason_codes": version_result.reason_codes,
      },
    }
    path = Path(analysis_root) / "comparisons" / "treatment_comparisons.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path
