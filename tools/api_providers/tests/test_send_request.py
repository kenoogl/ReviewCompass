# tools/api_providers/tests/test_send_request.py
# send_request の実 API 呼び出しテスト（TDD 先行、初回は全件失敗を期待）。
# httpx で HTTP 直叩き、respx で HTTP リクエスト／レスポンスをモック化する。
# 計画書 §5.9.7.1（API 経路先取り実装）参照。

import sys
from pathlib import Path

# プロジェクトルートを sys.path に追加
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
  sys.path.insert(0, str(_PROJECT_ROOT))

import httpx
import pytest
import respx

from tools.api_providers.providers import AnthropicProvider, OpenAIProvider


# --- Anthropic 関連（4 件） ---


@respx.mock
def test_anthropic_send_request_calls_correct_url(monkeypatch):
  """Anthropic の URL に POST する"""
  monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
  route = respx.post("https://api.anthropic.com/v1/messages").mock(
    return_value=httpx.Response(
      200, json={"content": [{"type": "text", "text": "ok"}]}
    )
  )
  provider = AnthropicProvider(model="claude-opus-4-7")
  provider.send_request("hello")
  assert route.called


@respx.mock
def test_anthropic_send_request_uses_api_key_header(monkeypatch):
  """x-api-key ヘッダに API キーが入る"""
  monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key-anthropic")
  route = respx.post("https://api.anthropic.com/v1/messages").mock(
    return_value=httpx.Response(
      200, json={"content": [{"type": "text", "text": "ok"}]}
    )
  )
  provider = AnthropicProvider(model="claude-opus-4-7")
  provider.send_request("hello")
  request = route.calls[0].request
  assert request.headers["x-api-key"] == "test-key-anthropic"


@respx.mock
def test_anthropic_send_request_includes_prompt_in_body(monkeypatch):
  """リクエストボディの messages に prompt が含まれる"""
  monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
  route = respx.post("https://api.anthropic.com/v1/messages").mock(
    return_value=httpx.Response(
      200, json={"content": [{"type": "text", "text": "ok"}]}
    )
  )
  provider = AnthropicProvider(model="claude-opus-4-7")
  provider.send_request("ユーザー入力テキスト")
  body = route.calls[0].request.content.decode("utf-8")
  assert "ユーザー入力テキスト" in body


@respx.mock
def test_anthropic_send_request_extracts_text_from_response(monkeypatch):
  """レスポンス JSON の content[0].text を返す"""
  monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
  respx.post("https://api.anthropic.com/v1/messages").mock(
    return_value=httpx.Response(
      200, json={"content": [{"type": "text", "text": "回答テキスト"}]}
    )
  )
  provider = AnthropicProvider(model="claude-opus-4-7")
  result = provider.send_request("質問")
  assert result == "回答テキスト"


@respx.mock
def test_anthropic_send_request_extracts_first_text_part(monkeypatch):
  """Anthropic 応答で先頭 part が text でない場合も text part を返す"""
  monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
  respx.post("https://api.anthropic.com/v1/messages").mock(
    return_value=httpx.Response(
      200,
      json={
        "content": [
          {"type": "thinking", "thinking": "internal"},
          {"type": "text", "text": "回答テキスト"},
        ],
      },
    )
  )
  provider = AnthropicProvider(model="claude-sonnet-5")
  result = provider.send_request("質問")
  assert result == "回答テキスト"


@respx.mock
def test_anthropic_send_request_reports_missing_text_parts(monkeypatch):
  """Anthropic 応答に text part がない場合は構造情報つきで失敗する"""
  monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
  respx.post("https://api.anthropic.com/v1/messages").mock(
    return_value=httpx.Response(
      200,
      json={
        "stop_reason": "max_tokens",
        "content": [
          {"type": "thinking", "thinking": "internal"},
        ],
      },
    )
  )
  provider = AnthropicProvider(model="claude-sonnet-5")
  with pytest.raises(ValueError) as excinfo:
    provider.send_request("質問")
  message = str(excinfo.value)
  assert "Anthropic response has no text part" in message
  assert "stop_reason=max_tokens" in message
  assert "part_types=thinking" in message


# --- OpenAI 関連（4 件） ---


@respx.mock
def test_openai_send_request_calls_correct_url(monkeypatch):
  """OpenAI の URL に POST する"""
  monkeypatch.setenv("OPENAI_API_KEY", "test-key")
  route = respx.post("https://api.openai.com/v1/chat/completions").mock(
    return_value=httpx.Response(
      200, json={"choices": [{"message": {"content": "ok"}}]}
    )
  )
  provider = OpenAIProvider(model="gpt-test")
  provider.send_request("hello")
  assert route.called


@respx.mock
def test_openai_send_request_uses_bearer_token(monkeypatch):
  """Authorization ヘッダに Bearer トークン"""
  monkeypatch.setenv("OPENAI_API_KEY", "test-key-openai")
  route = respx.post("https://api.openai.com/v1/chat/completions").mock(
    return_value=httpx.Response(
      200, json={"choices": [{"message": {"content": "ok"}}]}
    )
  )
  provider = OpenAIProvider(model="gpt-test")
  provider.send_request("hello")
  request = route.calls[0].request
  assert request.headers["authorization"] == "Bearer test-key-openai"


@respx.mock
def test_openai_send_request_includes_prompt_in_body(monkeypatch):
  """リクエストボディの messages に prompt が含まれる"""
  monkeypatch.setenv("OPENAI_API_KEY", "test-key")
  route = respx.post("https://api.openai.com/v1/chat/completions").mock(
    return_value=httpx.Response(
      200, json={"choices": [{"message": {"content": "ok"}}]}
    )
  )
  provider = OpenAIProvider(model="gpt-test")
  provider.send_request("プロンプト本文")
  body = route.calls[0].request.content.decode("utf-8")
  assert "プロンプト本文" in body


@respx.mock
def test_openai_send_request_extracts_text_from_response(monkeypatch):
  """レスポンス JSON の choices[0].message.content を返す"""
  monkeypatch.setenv("OPENAI_API_KEY", "test-key")
  respx.post("https://api.openai.com/v1/chat/completions").mock(
    return_value=httpx.Response(
      200, json={"choices": [{"message": {"content": "回答内容"}}]}
    )
  )
  provider = OpenAIProvider(model="gpt-test")
  result = provider.send_request("質問")
  assert result == "回答内容"


# --- 共通（2 件） ---


@respx.mock
def test_send_request_passes_timeout_to_httpx(monkeypatch):
  """timeout_seconds がコンストラクタで指定でき、httpx に渡る"""
  monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
  respx.post("https://api.anthropic.com/v1/messages").mock(
    return_value=httpx.Response(
      200, json={"content": [{"type": "text", "text": "ok"}]}
    )
  )
  # timeout_seconds をコンストラクタで指定できることを確認（属性として保持）
  provider = AnthropicProvider(model="claude-opus-4-7", timeout_seconds=90)
  assert provider.timeout_seconds == 90
  provider.send_request("hello")


@respx.mock
def test_send_request_http_error_raises(monkeypatch):
  """HTTP 4xx／5xx で例外を投げる"""
  monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
  respx.post("https://api.anthropic.com/v1/messages").mock(
    return_value=httpx.Response(500, json={"error": "internal server error"})
  )
  provider = AnthropicProvider(model="claude-opus-4-7")
  with pytest.raises(httpx.HTTPStatusError):
    provider.send_request("hello")
