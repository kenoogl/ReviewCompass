"""取り込み登録（ingestion_register.json）の生成。"""
import json
from pathlib import Path


class IngestionRegisterWriter:
  """imports/ingestion_register.json に取り込み履歴を追記する。"""

  def append(self, analysis_root, entry):
    register_path = Path(analysis_root) / "imports" / "ingestion_register.json"
    register_path.parent.mkdir(parents=True, exist_ok=True)
    if register_path.exists():
      register = json.loads(register_path.read_text(encoding="utf-8"))
    else:
      register = {"entries": []}
    register.setdefault("entries", []).append(entry)
    register_path.write_text(
      json.dumps(register, ensure_ascii=False, indent=2),
      encoding="utf-8",
    )
    return register_path
