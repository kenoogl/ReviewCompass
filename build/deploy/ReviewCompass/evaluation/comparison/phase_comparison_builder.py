"""フェーズ対応比較の生成。"""
import json
from pathlib import Path

from comparison.mode_population_rule import ModePopulationRule
from comparison.valid_population_rule import ValidPopulationRule


class PhaseComparisonBuilder:
  """comparisons/phase_comparisons.json を生成する。"""

  def write(self, analysis_root, runs):
    standard = ModePopulationRule().slice(runs)["standard_runtime_mediated"]
    included = ValidPopulationRule().apply(standard)
    by_phase = {}
    for run in included:
      bucket = by_phase.setdefault(run["phase_profile"], {
        "included_runs": [],
        "finding_count": 0,
      })
      bucket["included_runs"].append(run["run_id"])
      bucket["finding_count"] += run.get("finding_count", 0)
    payload = {
      "comparison_type": "phase",
      "included_runs": [run["run_id"] for run in included],
      "by_phase": by_phase,
    }
    path = Path(analysis_root) / "comparisons" / "phase_comparisons.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path
