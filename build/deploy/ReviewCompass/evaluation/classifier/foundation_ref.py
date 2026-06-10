"""foundation 語彙正本の参照専用ユーティリティ。"""
from pathlib import Path

import yaml

_THIS_DIR = Path(__file__).resolve().parent
_REPO_ROOT = _THIS_DIR.parents[1]
_METADATA_CONTRACT = _REPO_ROOT / "runtime/foundation/metadata_contract.yaml"


def vocabulary(name):
  """metadata_contract.yaml の vocabularies.<name> を参照のみで取得する。"""
  contract = yaml.safe_load(_METADATA_CONTRACT.read_text(encoding="utf-8"))
  return list(contract["vocabularies"][name])
