"""tools/api_providers/providers.py

API 経路のプロバイダー抽象層。
計画書 §5.9.7.1（API 経路先取り実装、設計案 P）参照。

本スクリプトは API 経路の役のみを実行する。CLI 経路の役は私（Claude Code）が
Agent ツールで処理するため、本スクリプトの対象外（claude-code-cli を渡すと ValueError）。
"""
import os
import time
from abc import ABC, abstractmethod
from typing import Tuple, Type

import httpx


class ProviderBase(ABC):
  """プロバイダー抽象基底クラス。

  各サブクラスは ENV_VAR_NAME（環境変数名）を上書きし、_build_request と _extract_text を実装する。
  send_request は本基底クラスで共通実装（HTTP POST ＋ リトライ機構 ＋ 失敗時例外 ＋ 文字列抽出）。
  abstractmethod があるため直接インスタンス化は TypeError で防止される。
  """

  ENV_VAR_NAME: str = ""

  def __init__(
    self,
    model: str,
    timeout_seconds: int = 60,
    max_retries: int = 1,
    initial_retry_delay_seconds: float = 5.0,
  ):
    self.model = model
    self.timeout_seconds = timeout_seconds
    self.max_retries = max_retries
    self.initial_retry_delay_seconds = initial_retry_delay_seconds
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
  def _build_request(self, prompt: str) -> Tuple[str, dict, dict]:
    """各プロバイダー固有のリクエスト構造（URL、ヘッダ、JSON ボディ）を返す。"""
    ...

  @abstractmethod
  def _extract_text(self, response_json: dict) -> str:
    """各プロバイダーのレスポンス JSON から文字列を取り出す。"""
    ...

  def _is_retryable_error(self, exc: Exception) -> bool:
    """リトライ対象の例外かを判定する。

    - httpx.TimeoutException：常にリトライ対象
    - httpx.HTTPStatusError：HTTP 5xx（サーバ側エラー）と 429（過負荷／レート制限）のみリトライ
    - その他：リトライ対象外
    """
    if isinstance(exc, httpx.TimeoutException):
      return True
    if isinstance(exc, httpx.HTTPStatusError):
      status = exc.response.status_code
      return status >= 500 or status == 429
    return False

  def send_request(self, prompt: str) -> str:
    """HTTP POST でリクエストを送り、レスポンスから文字列を返す。

    リトライ対象例外（HTTP 5xx／429、タイムアウト）は指数バックオフで再送する。
    リトライ回数は self.max_retries まで（既定 1 回）。
    リトライ対象外の例外（4xx の 429 以外など）は即座に投げる（fail-fast）。
    """
    url, headers, body = self._build_request(prompt)
    with httpx.Client(timeout=self.timeout_seconds) as client:
      for attempt in range(self.max_retries + 1):
        try:
          response = client.post(url, headers=headers, json=body)
          response.raise_for_status()
          return self._extract_text(response.json())
        except (httpx.HTTPStatusError, httpx.TimeoutException) as exc:
          if not self._is_retryable_error(exc):
            raise
          if attempt >= self.max_retries:
            raise
          delay = self.initial_retry_delay_seconds * (2 ** attempt)
          time.sleep(delay)


class AnthropicProvider(ProviderBase):
  """Anthropic API プロバイダー（POST /v1/messages）。"""

  ENV_VAR_NAME = "ANTHROPIC_API_KEY"
  URL = "https://api.anthropic.com/v1/messages"
  ANTHROPIC_VERSION = "2023-06-01"
  DEFAULT_MAX_TOKENS = 4096

  def _build_request(self, prompt: str) -> Tuple[str, dict, dict]:
    headers = {
      "x-api-key": self.api_key,
      "anthropic-version": self.ANTHROPIC_VERSION,
      "content-type": "application/json",
    }
    body = {
      "model": self.model,
      "messages": [{"role": "user", "content": prompt}],
      "max_tokens": self.DEFAULT_MAX_TOKENS,
    }
    return self.URL, headers, body

  def _extract_text(self, response_json: dict) -> str:
    return response_json["content"][0]["text"]


class OpenAIProvider(ProviderBase):
  """OpenAI API プロバイダー（POST /v1/chat/completions）。"""

  ENV_VAR_NAME = "OPENAI_API_KEY"
  URL = "https://api.openai.com/v1/chat/completions"

  def _build_request(self, prompt: str) -> Tuple[str, dict, dict]:
    headers = {
      "authorization": f"Bearer {self.api_key}",
      "content-type": "application/json",
    }
    body = {
      "model": self.model,
      "messages": [{"role": "user", "content": prompt}],
    }
    return self.URL, headers, body

  def _extract_text(self, response_json: dict) -> str:
    return response_json["choices"][0]["message"]["content"]


class GeminiProvider(ProviderBase):
  """Google Gemini API プロバイダー（POST /v1beta/models/{model}:generateContent）。

  エンドポイントは model 名を URL パスに含む形式（Anthropic／OpenAI と異なる）。
  認証は x-goog-api-key ヘッダーを使う。
  セッション 31（2026-05-27）の計画変更「7 モデル比較実験への拡大」で追加。
  """

  ENV_VAR_NAME = "GEMINI_API_KEY"
  URL_TEMPLATE = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

  def _build_request(self, prompt: str) -> Tuple[str, dict, dict]:
    url = self.URL_TEMPLATE.format(model=self.model)
    headers = {
      "x-goog-api-key": self.api_key,
      "content-type": "application/json",
    }
    body = {
      "contents": [
        {"parts": [{"text": prompt}]}
      ]
    }
    return url, headers, body

  def _extract_text(self, response_json: dict) -> str:
    return response_json["candidates"][0]["content"]["parts"][0]["text"]


_PROVIDER_REGISTRY = {
  "anthropic-api": AnthropicProvider,
  "openai-api": OpenAIProvider,
  "gemini-api": GeminiProvider,
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
