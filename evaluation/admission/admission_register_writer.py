"""許容判定登録（admission_register.json）の生成。"""
import json
from pathlib import Path


class AdmissionRegisterWriter:
  """imports/admission_register.json に許容判定結果を追記する。"""

  def append(self, analysis_root, result):
    register_path = Path(analysis_root) / "imports" / "admission_register.json"
    register_path.parent.mkdir(parents=True, exist_ok=True)
    if register_path.exists():
      register = json.loads(register_path.read_text(encoding="utf-8"))
    else:
      register = {"entries": []}
    register.setdefault("entries", []).append(result.to_register_entry())
    register_path.write_text(
      json.dumps(register, ensure_ascii=False, indent=2),
      encoding="utf-8",
    )
    return register_path
