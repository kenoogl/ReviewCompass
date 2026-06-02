"""foundation_ref：foundation 契約の語彙・スキーマを参照のみで取得する共有ユーティリティ。

runtime は foundation の語彙正本（6 件）を再定義・縮約せず参照する（design.md §判断 6
contract consumer 原則）。本モジュールは metadata_contract.yaml の語彙と各スキーマの enum を
読み取る単一の参照口を提供し、再定義の混入を防ぐ。T-007／T-008／T-009 が利用する。

対応設計節：design.md §責務境界の明確化、§判断 6
"""
import json
from pathlib import Path

import yaml

_THIS_DIR = Path(__file__).resolve().parent
_REPO_ROOT = _THIS_DIR.parents[1]
_METADATA_CONTRACT = _REPO_ROOT / "runtime/foundation/metadata_contract.yaml"
_SCHEMA_DIR = _REPO_ROOT / "runtime/schemas"
_VALIDATOR_CONTRACT_DIR = _REPO_ROOT / "runtime/validators/contracts"


def vocabulary(name):
  """metadata_contract.yaml の語彙正本を参照のみで取得する（再定義禁止）。

  runtime が参照する対象例：run_status／validator_status／human_signoff_status／
         evidence_class／review_mode。confidence_label は推定タスク用で runtime の
         参照範囲外（tasks.md foundation contract consumer 原則、P-004）。
  """
  contract = yaml.safe_load(_METADATA_CONTRACT.read_text(encoding="utf-8"))
  return list(contract["vocabularies"][name])


def schema_enum(schema_filename, field):
  """runtime/schemas/ のスキーマ properties.<field>.enum を参照のみで取得する。"""
  schema = json.loads((_SCHEMA_DIR / schema_filename).read_text(encoding="utf-8"))
  return list(schema["properties"][field]["enum"])


def validator_contract_enum(schema_filename, field):
  """runtime/validators/contracts/ のスキーマ properties.<field>.enum を取得する。"""
  schema = json.loads((_VALIDATOR_CONTRACT_DIR / schema_filename).read_text(encoding="utf-8"))
  return list(schema["properties"][field]["enum"])
