"""構造化参照の共通書式。"""
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
  return path

