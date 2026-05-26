"""tools/api_providers/config_loader.py

API 設定ファイル config/api-settings.yaml の読み込みと variant 解決を担う。
計画書 §5.9.7.1（API 経路先取り実装、yaml 命名規約 connection／default／variants）参照。
"""
from pathlib import Path
from typing import Optional, Union

import yaml


def load_config(yaml_path: Union[str, Path]) -> dict:
  """yaml ファイルを読んで辞書を返す。

  ファイルがなければ FileNotFoundError を投げる（Path.open の標準挙動）。
  """
  path = Path(yaml_path)
  with path.open("r", encoding="utf-8") as f:
    return yaml.safe_load(f)


def resolve_variant(config: dict, variant_name: Optional[str] = None) -> dict:
  """variant 名から役設定セットを返す。

  variant_name=None なら config["default"]、指定があれば config["variants"][variant_name]。
  存在しない variant 名は KeyError。
  """
  if variant_name is None:
    return config["default"]
  variants = config.get("variants", {})
  if variant_name not in variants:
    raise KeyError(f"variant '{variant_name}' not found in variants")
  return variants[variant_name]


def resolve_role(variant_config: dict, role_name: str) -> dict:
  """役名から役設定を返す。

  存在しない役名は KeyError。
  """
  if role_name not in variant_config:
    raise KeyError(f"role '{role_name}' not found in variant config")
  return variant_config[role_name]


def resolve_connection_settings(role_config: dict, connection_defaults: dict) -> dict:
  """connection 既定値と役レベル上書きをマージして接続設定を返す。

  役レベルに timeout_seconds／max_retries が指定されていれば優先、
  未指定なら connection_defaults から継承する（フラット直書き方式、計画書 §5.9.7.1 確定）。
  """
  settings = dict(connection_defaults)
  for key in ("timeout_seconds", "max_retries"):
    if key in role_config:
      settings[key] = role_config[key]
  return settings
