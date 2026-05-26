# tools/api_providers/tests/test_providers.py
# プロバイダー抽象層と CLI 経路／API 経路の分岐のテスト（TDD 先行、初回は全件失敗を期待）。
# 計画書 §5.9.7.1（API 経路先取り実装、設計案 P）と
# config/api-settings.yaml の provider 値（claude-code-cli／anthropic-api／openai-api）に基づく。

import sys
from pathlib import Path

# プロジェクトルートを sys.path に追加してパッケージ import を可能にする
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
  sys.path.insert(0, str(_PROJECT_ROOT))

import pytest

# 実装は未着手。import 自体が失敗する状態が TDD の初期期待。
from tools.api_providers.providers import (
  get_provider,
  ProviderBase,
  AnthropicProvider,
  OpenAIProvider,
)


def test_get_provider_anthropic_api():
  """provider 名 anthropic-api から AnthropicProvider クラスを返す"""
  cls = get_provider("anthropic-api")
  assert cls is AnthropicProvider


def test_get_provider_openai_api():
  """provider 名 openai-api から OpenAIProvider クラスを返す"""
  cls = get_provider("openai-api")
  assert cls is OpenAIProvider


def test_get_provider_claude_code_cli_raises():
  """CLI 経路は本スクリプトの対象外（私が Agent ツールで処理）、ValueError"""
  with pytest.raises(ValueError):
    get_provider("claude-code-cli")


def test_get_provider_unknown_raises():
  """不明な provider 名で ValueError"""
  with pytest.raises(ValueError):
    get_provider("unknown-provider")


def test_anthropic_provider_requires_api_key(monkeypatch):
  """ANTHROPIC_API_KEY 未設定で初期化エラー"""
  monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
  with pytest.raises((KeyError, RuntimeError, EnvironmentError)):
    AnthropicProvider(model="claude-opus-4-7")


def test_openai_provider_requires_api_key(monkeypatch):
  """OPENAI_API_KEY 未設定で初期化エラー"""
  monkeypatch.delenv("OPENAI_API_KEY", raising=False)
  with pytest.raises((KeyError, RuntimeError, EnvironmentError)):
    OpenAIProvider(model="gpt-test")


def test_anthropic_provider_reads_env(monkeypatch):
  """環境変数 ANTHROPIC_API_KEY から API キーを読む"""
  monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key-anthropic")
  provider = AnthropicProvider(model="claude-opus-4-7")
  assert provider.api_key == "test-key-anthropic"


def test_openai_provider_reads_env(monkeypatch):
  """環境変数 OPENAI_API_KEY から API キーを読む"""
  monkeypatch.setenv("OPENAI_API_KEY", "test-key-openai")
  provider = OpenAIProvider(model="gpt-test")
  assert provider.api_key == "test-key-openai"


def test_provider_base_is_abstract():
  """ProviderBase は直接インスタンス化不可（abstract）"""
  with pytest.raises(TypeError):
    ProviderBase(model="test")


def test_provider_has_model_attribute(monkeypatch):
  """プロバイダーは model 属性を持つ"""
  monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
  provider = AnthropicProvider(model="claude-opus-4-7")
  assert provider.model == "claude-opus-4-7"
