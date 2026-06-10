"""run_classification_index.json の生成。"""
import json
from pathlib import Path


class RunClassificationWriter:
  """classifications/run_classification_index.json を生成する。"""

  def write(self, analysis_root, results):
    path = Path(analysis_root) / "classifications" / "run_classification_index.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"entries": [result.to_index_entry() for result in results]}
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path
