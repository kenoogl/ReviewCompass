"""staleness_register.json の生成。"""
import json
from pathlib import Path


class StalenessRegisterWriter:
  """manifests/staleness_register.json に陳腐化履歴を追記する。"""

  def append(self, analysis_root, entry):
    path = Path(analysis_root) / "manifests" / "staleness_register.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
      register = json.loads(path.read_text(encoding="utf-8"))
    else:
      register = {"entries": []}
    register.setdefault("entries", []).append(entry)
    path.write_text(json.dumps(register, ensure_ascii=False, indent=2), encoding="utf-8")
    return path
