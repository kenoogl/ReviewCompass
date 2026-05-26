"""tools/api_providers/providers.py

API 経路のプロバイダー抽象層。
計画書 §5.9.7.1（API 経路先取り実装、設計案 P）参照。

本スクリプトは API 経路の役のみを実行する。CLI 経路の役は私（Claude Code）が
Agent ツールで処理するため、本スクリプトの対象外（claude-code-cli を渡すと ValueError）。
"""
import os
from abc import ABC, abstractmethod
from typing import Type


class ProviderBase(ABC):
  """プロバイダー抽象基底クラス。

  各サブクラスは ENV_VAR_NAME（環境変数名）を上書きし、send_request() を実装する。
  直接インスタンス化は abstractmethod で防止される。
  """

  ENV_VAR_NAME: str = ""

  def __init__(self, model: str):
    self.model = model
    self.api_key = self._read_api_key()

  def _read_api_key(self) -> str:
    """環境変数から API キーを読む。未設定時は RuntimeError。"""
    if not self.ENV_VAR_NAME:
      raise RuntimeError("ENV_VAR_NAME がサブクラスで未設定")
    api_key = os.environ.get(self.ENV_VAR_NAME)
    if not api_key:
      raise RuntimeError(
        f"環境変数 {self.ENV_VAR_NAME} が未設定。API キーを設定してください。"
      )
    return api_key

  @abstractmethod
  def send_request(self, prompt: str) -> str:
    """各プロバイダーが実装するリクエスト送信。本サイクルでは未実装（次サイクル予定）。"""
    ...


class AnthropicProvider(ProviderBase):
  """Anthropic API プロバイダー。"""

  ENV_VAR_NAME = "ANTHROPIC_API_KEY"

  def send_request(self, prompt: str) -> str:
    raise NotImplementedError("次サイクルで実装予定")


class OpenAIProvider(ProviderBase):
  """OpenAI API プロバイダー。"""

  ENV_VAR_NAME = "OPENAI_API_KEY"

  def send_request(self, prompt: str) -> str:
    raise NotImplementedError("次サイクルで実装予定")


_PROVIDER_REGISTRY = {
  "anthropic-api": AnthropicProvider,
  "openai-api": OpenAIProvider,
}


def get_provider(provider_name: str) -> Type[ProviderBase]:
  """provider 名から対応するプロバイダークラスを返す。

  - anthropic-api → AnthropicProvider
  - openai-api → OpenAIProvider
  - claude-code-cli → ValueError（CLI 経路は本スクリプトの対象外、私が Agent ツールで処理）
  - 不明な値 → ValueError
  """
  if provider_name == "claude-code-cli":
    raise ValueError(
      f"provider '{provider_name}' は CLI 経路であり本スクリプトの対象外。"
      "CLI 経路の役は Claude Code 内の Agent ツールで処理される。"
    )
  if provider_name not in _PROVIDER_REGISTRY:
    raise ValueError(f"不明なプロバイダー名: '{provider_name}'")
  return _PROVIDER_REGISTRY[provider_name]
