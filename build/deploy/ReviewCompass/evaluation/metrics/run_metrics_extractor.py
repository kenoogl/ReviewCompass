"""実行レベルメトリクス抽出器。"""
import json
from pathlib import Path

import yaml

_THIS_DIR = Path(__file__).resolve().parent


class RunMetricsExtractor:
  """review_case.json から実行レベルメトリクスを抽出する。"""

  def extract(self, run_dir):
    run_dir = Path(run_dir)
    review_case_path = run_dir / "review_case.json"
    review_case = json.loads(review_case_path.read_text(encoding="utf-8"))
    return {
      "artifact_id": "run_metrics",
      "metric_level": "run",
      "run_id": review_case["run_id"],
      "target_id": review_case["target_id"],
      "phase_profile": review_case["phase_profile"],
      "treatment": review_case["treatment"],
      "finding_count": len(review_case.get("findings", [])),
      "derivation": {
        "source_artifact": str(review_case_path),
        "source_fields": ["findings[]"],
      },
    }

  @staticmethod
  def load_yaml_definition(name):
    filenames = {
      "core": "core_layer_definition.yaml",
      "phase_overlay": "phase_overlay_definition.yaml",
    }
    return yaml.safe_load((_THIS_DIR / filenames[name]).read_text(encoding="utf-8"))
