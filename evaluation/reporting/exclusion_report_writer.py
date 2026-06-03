"""exclusion_report.json の生成。"""
import json
from pathlib import Path


class ExclusionReportWriter:
  """valid 以外の実行を除外報告に出力する。"""

  def write(self, analysis_root, classifications):
    entries = []
    for item in classifications:
      if item["classification"] == "valid":
        continue
      reason_codes = list(item.get("reason_codes", []))
      entries.append({
        "run_id": item["run_id"],
        "classification": item["classification"],
        "reason_codes": reason_codes,
        "reason_details": self._details(reason_codes),
        "phase_profile": item.get("phase_profile"),
        "treatment": item.get("treatment"),
        "review_mode": item.get("review_mode"),
      })
    payload = {
      "summary": {"excluded_count": len(entries)},
      "entries": entries,
    }
    path = Path(analysis_root) / "classifications" / "exclusion_report.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path

  def _details(self, reason_codes):
    return [
      {"reason_code": code, "detail": code.replace("_", " ")}
      for code in reason_codes
    ]
