"""T-007 のテスト：設定 2 層モデル雛形（3 ファイル）。

対応タスク：foundation tasks.md T-007
対応設計節：design.md §10 設定と雛形のモデル
対応要件：Requirement 2（役と設定の抽象化）、Requirement 7 受入 3

テスト要件（tasks.md T-007 より）：
- 3 ファイルの YAML 解析テスト
- 必須項目存在テスト（config.yaml.template 5 項目、terminology.yaml.template 2 項目）
"""
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
CONFIG_DIR = REPO_ROOT / "runtime/config"

CONFIG_FILES = [
  "reviewcompass.yaml",
  "config.yaml.template",
  "terminology.yaml.template",
]

# config.yaml.template の必須 5 項目（tasks.md T-007、design.md §10）
CONFIG_TEMPLATE_REQUIRED = [
  "role_models",          # 役ごとのモデル識別子
  "project_language",     # 対象アプリの言語
  "protocol_version",     # 規約版
  "evidence_output_dir",  # 証拠出力先
  "default_phase_profile",  # 既定の phase および profile
]

# terminology.yaml.template の必須 2 項目（entries は空配列でも成立）
TERMINOLOGY_REQUIRED = ["version", "entries"]


def _load(filename):
  path = CONFIG_DIR / filename
  if not path.is_file():
    pytest.fail(f"設定雛形が存在しない：{filename}")
  with path.open(encoding="utf-8") as f:
    return yaml.safe_load(f)


@pytest.mark.parametrize("filename", CONFIG_FILES)
def test_yaml_parses(filename):
  """3 ファイルが YAML として解析可能で辞書である。"""
  data = _load(filename)
  assert isinstance(data, dict), f"{filename} のトップが辞書でない"


@pytest.mark.parametrize("key", CONFIG_TEMPLATE_REQUIRED)
def test_config_template_required_keys(key):
  """config.yaml.template が必須 5 項目を持つ。"""
  data = _load("config.yaml.template")
  assert key in data, f"config.yaml.template に必須項目が欠落：{key}"


def test_config_template_has_exactly_5_required():
  """config.yaml.template の必須 5 項目がすべて揃っている。"""
  data = _load("config.yaml.template")
  for key in CONFIG_TEMPLATE_REQUIRED:
    assert key in data, f"必須項目が欠落：{key}"


@pytest.mark.parametrize("key", TERMINOLOGY_REQUIRED)
def test_terminology_required_keys(key):
  """terminology.yaml.template が必須 2 項目（version／entries）を持つ。"""
  data = _load("terminology.yaml.template")
  assert key in data, f"terminology.yaml.template に必須項目が欠落：{key}"
