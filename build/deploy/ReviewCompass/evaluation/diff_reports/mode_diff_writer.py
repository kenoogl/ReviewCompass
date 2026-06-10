"""mode_diff_report.json の生成。"""
import json
from pathlib import Path

_THIS_DIR = Path(__file__).resolve().parent


class ModeDiffWriter:
  """レビューモード別の所見差分を生成する。"""

  def write(self, analysis_root, findings):
    grouped = {}
    for finding in findings:
      key = (finding["feature"], finding["target"], finding["review_mode"])
      entry = grouped.setdefault(key, {
        "feature": finding["feature"],
        "review_mode": finding["review_mode"],
        "findings_by_severity": {},
        "target": finding["target"],
      })
      severity = finding["severity"]
      entry["findings_by_severity"][severity] = (
        entry["findings_by_severity"].get(severity, 0) + 1
      )
    entries = list(grouped.values())
    payload = {
      "entries": entries,
      "entries_by_mode": {entry["review_mode"]: entry for entry in entries},
    }
    path = Path(analysis_root) / "modes" / "mode_diff_report.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path

  @staticmethod
  def load_schema():
    return _THIS_DIR / "diff_report_schema.yaml"
