"""caveat_register.json の生成。"""
import json
from pathlib import Path


class CaveatRegisterWriter:
  """報告上残す注意点を登録する。"""

  def write(self, analysis_root, caveats):
    by_caveat_type = {}
    for caveat in caveats:
      caveat_type = caveat["caveat_type"]
      by_caveat_type[caveat_type] = by_caveat_type.get(caveat_type, 0) + 1
    payload = {
      "summary": {"by_caveat_type": by_caveat_type},
      "entries": caveats,
    }
    path = Path(analysis_root) / "caveats" / "caveat_register.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path
