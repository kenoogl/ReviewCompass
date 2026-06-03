"""構造化参照の共通書式。"""
import json
from pathlib import Path


def artifact_ref(*, ref_type, target_path, target_id=None):
  """成果物への構造化参照を作る。"""
  return {
    "ref_type": ref_type,
    "target_path": target_path,
    "target_id": target_id,
  }


def resolve_artifact_ref(ref, *, base_dir):
  """構造化参照を base_dir 起点のファイルパスへ解決する。"""
  path = Path(base_dir) / ref["target_path"]
  if not path.is_file():
    raise FileNotFoundError(path)
  target_id = ref.get("target_id")
  if target_id is not None:
    _ensure_target_id_exists(path, target_id)
  return path


def _ensure_target_id_exists(path, target_id):
  payload = json.loads(path.read_text(encoding="utf-8"))
  if not _contains_target_id(payload, target_id):
    raise LookupError(f"target_id not found: {target_id}")


def _contains_target_id(payload, target_id):
  if isinstance(payload, dict):
    for key, value in payload.items():
      if (key == "id" or key.endswith("_id")) and value == target_id:
        return True
      if _contains_target_id(value, target_id):
        return True
  elif isinstance(payload, list):
    return any(_contains_target_id(item, target_id) for item in payload)
  return False
