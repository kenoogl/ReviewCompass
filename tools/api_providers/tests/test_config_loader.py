# tools/api_providers/tests/test_config_loader.py
# yaml 読み込みと variant 解決のテスト（TDD 先行、初回は全件失敗を期待）。
# 計画書 §5.9.7.1（yaml の階層命名規約：connection／default／variants）と
# config/api-settings.yaml の構造に基づく。

import sys
from pathlib import Path

# プロジェクトルートを sys.path に追加してパッケージ import を可能にする
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
  sys.path.insert(0, str(_PROJECT_ROOT))

import pytest

# 実装は未着手。import 自体が失敗する状態が TDD の初期期待。
from tools.api_providers.config_loader import (
  load_config,
  resolve_variant,
  resolve_role,
  resolve_connection_settings,
  resolve_default_variant_name,
)


# テスト用の yaml 内容（config/api-settings.yaml の構造に準拠）
FIXTURE_YAML = """
connection:
  timeout_seconds: 60
  max_retries: 1

operation_defaults:
  api_review_prompt_quality:
    variant: prompt_quality_2way

default:
  primary:
    path: cli
    provider: claude-code-cli
    model: claude-opus-4-7
  adversarial:
    path: cli
    provider: claude-code-cli
    model: claude-sonnet-4-6
  judgment:
    path: cli
    provider: claude-code-cli
    model: claude-opus-4-7

variants:
  prompt_quality_2way:
    context: prompt_quality
    variant_type: two_role
    required_roles: [adversarial, judgment]
    adversarial:
      path: api
      provider: anthropic-api
      model: claude-sonnet-4-6
      timeout_seconds: 300
    judgment:
      path: api
      provider: gemini-api
      model: gemini-3.1-pro-preview
      timeout_seconds: 300

  baseline_claude_cli:
    primary:
      path: cli
      provider: claude-code-cli
      model: claude-opus-4-7
    adversarial:
      path: cli
      provider: claude-code-cli
      model: claude-sonnet-4-6
    judgment:
      path: cli
      provider: claude-code-cli
      model: claude-opus-4-7

  with_override:
    primary:
      path: api
      provider: openai-api
      model: gpt-test
      timeout_seconds: 90
    adversarial:
      path: cli
      provider: claude-code-cli
      model: claude-sonnet-4-6
    judgment:
      path: cli
      provider: claude-code-cli
      model: claude-opus-4-7
"""


@pytest.fixture
def yaml_path(tmp_path):
  """テスト用の yaml ファイルを一時ディレクトリに書き出す"""
  p = tmp_path / "api-settings.yaml"
  p.write_text(FIXTURE_YAML)
  return p


def test_load_config_returns_dict(yaml_path):
  """yaml を読んで辞書を返す"""
  config = load_config(yaml_path)
  assert isinstance(config, dict)


def test_load_config_has_three_top_keys(yaml_path):
  """connection／default／variants の 3 トップキーが揃う"""
  config = load_config(yaml_path)
  assert set(config.keys()) >= {"connection", "default", "variants"}


def test_resolve_variant_default_when_none(yaml_path):
  """variant=None で default 設定セットを返す"""
  config = load_config(yaml_path)
  variant = resolve_variant(config, None)
  assert "primary" in variant
  assert variant["primary"]["model"] == "claude-opus-4-7"


def test_resolve_variant_named(yaml_path):
  """variant 名で variants 配下の設定セットを返す"""
  config = load_config(yaml_path)
  variant = resolve_variant(config, "baseline_claude_cli")
  assert variant["primary"]["provider"] == "claude-code-cli"


def test_resolve_default_variant_name(yaml_path):
  """場面ごとの既定 variant 名を機械的に解決する"""
  config = load_config(yaml_path)

  assert resolve_default_variant_name(
    config,
    "api_review_prompt_quality",
  ) == "prompt_quality_2way"


def test_real_config_prompt_quality_default_uses_expected_api_roles():
  """実設定の prompt-quality 既定は sonnet-4-6 / gemini-3.1-pro-preview に固定する"""
  config = load_config(_PROJECT_ROOT / "config" / "api-settings.yaml")
  variant_name = resolve_default_variant_name(config, "api_review_prompt_quality")
  variant = resolve_variant(config, variant_name)

  assert variant["required_roles"] == ["adversarial", "judgment"]
  assert variant["adversarial"]["path"] == "api"
  assert variant["adversarial"]["provider"] == "anthropic-api"
  assert variant["adversarial"]["model"] == "claude-sonnet-4-6"
  assert variant["judgment"]["path"] == "api"
  assert variant["judgment"]["provider"] == "gemini-api"
  assert variant["judgment"]["model"] == "gemini-3.1-pro-preview"


def test_real_config_implementation_review_default_uses_codex_operator_api_roles():
  """実設定の implementation-review 既定は Codex 操縦用 3 役 variant に固定する。"""
  config = load_config(_PROJECT_ROOT / "config" / "api-settings.yaml")
  variant_name = resolve_default_variant_name(config, "implementation_review")
  variant = resolve_variant(config, variant_name)

  assert variant_name == "implementation_review_independent_3way_codex_operator"
  assert variant["required_roles"] == ["primary", "adversarial", "judgment"]
  assert variant["primary"]["path"] == "api"
  assert variant["primary"]["provider"] == "openai-api"
  assert variant["primary"]["model"] == "gpt-5.4"
  assert variant["adversarial"]["path"] == "api"
  assert variant["adversarial"]["provider"] == "anthropic-api"
  assert variant["adversarial"]["model"] == "claude-sonnet-4-6"
  assert variant["judgment"]["path"] == "api"
  assert variant["judgment"]["provider"] == "gemini-api"
  assert variant["judgment"]["model"] == "gemini-3.1-pro-preview"


def test_resolve_variant_unknown_raises(yaml_path):
  """存在しない variant 名で例外"""
  config = load_config(yaml_path)
  with pytest.raises(KeyError):
    resolve_variant(config, "nonexistent_variant")


def test_resolve_role_primary(yaml_path):
  """role=primary で primary 役設定を返す"""
  config = load_config(yaml_path)
  variant = resolve_variant(config, None)
  role_config = resolve_role(variant, "primary")
  assert role_config["path"] == "cli"
  assert role_config["model"] == "claude-opus-4-7"


def test_resolve_role_unknown_raises(yaml_path):
  """存在しない役名で例外"""
  config = load_config(yaml_path)
  variant = resolve_variant(config, None)
  with pytest.raises(KeyError):
    resolve_role(variant, "nonexistent_role")


def test_connection_defaults_inherited(yaml_path):
  """役レベルに timeout_seconds なしで connection 既定値が継承される"""
  config = load_config(yaml_path)
  variant = resolve_variant(config, "baseline_claude_cli")
  role_config = resolve_role(variant, "primary")
  settings = resolve_connection_settings(role_config, config["connection"])
  assert settings["timeout_seconds"] == 60
  assert settings["max_retries"] == 1


def test_connection_role_override(yaml_path):
  """役レベル timeout_seconds が connection 既定値を上書き、未指定は connection から継承"""
  config = load_config(yaml_path)
  variant = resolve_variant(config, "with_override")
  role_config = resolve_role(variant, "primary")
  settings = resolve_connection_settings(role_config, config["connection"])
  assert settings["timeout_seconds"] == 90
  assert settings["max_retries"] == 1


def test_load_config_missing_file_raises(tmp_path):
  """存在しないファイルで例外"""
  missing_path = tmp_path / "nonexistent.yaml"
  with pytest.raises(FileNotFoundError):
    load_config(missing_path)
