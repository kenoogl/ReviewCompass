"""role_diff_report.json の生成。"""
import json
from pathlib import Path


class RoleDiffWriter:
  """3 役別の所見差分を生成する。"""

  def write(self, analysis_root, findings):
    grouped = {}
    for finding in findings:
      key = (finding["feature"], finding["target"], finding["role"])
      entry = grouped.setdefault(key, {
        "feature": finding["feature"],
        "role": finding["role"],
        "findings_summary": {
          "by_severity": {},
          "by_final_label": {},
          "by_counter_status": {},
        },
        "target": finding["target"],
      })
      summary = entry["findings_summary"]
      severity = finding["severity"]
      summary["by_severity"][severity] = summary["by_severity"].get(severity, 0) + 1
      if finding.get("final_label"):
        label = finding["final_label"]
        summary["by_final_label"][label] = summary["by_final_label"].get(label, 0) + 1
      if finding.get("counter_status"):
        status = finding["counter_status"]
        summary["by_counter_status"][status] = summary["by_counter_status"].get(status, 0) + 1
    entries = list(grouped.values())
    payload = {
      "entries": entries,
      "entries_by_role": {entry["role"]: entry for entry in entries},
    }
    path = Path(analysis_root) / "roles" / "role_diff_report.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path
