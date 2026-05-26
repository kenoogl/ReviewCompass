# tools/api_providers/tests/test_send_messages.py
# マルチターン対話に対応する send_messages のテスト（TDD 先行、初回は全件失敗を期待）。
# セッション 31（2026-05-27）の計画変更「7 モデル比較実験、案 Y（providers.py 拡張）」に基づく。
# 利用者明示承認の出典：「Y」（セッション 31、案 Y の採用）。
#
# send_messages の仕様：
# - 引数：messages_list（[{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}, ...]）
# - 各プロバイダーが内部で固有形式に変換
#   - Anthropic／OpenAI：messages 配列にそのまま渡す
#   - Gemini：contents 配列に変換、role は user → user／assistant → model に置換、content → parts.text に変換
# - 既存の send_request(prompt) は send_messages([{"role": "user", "content": prompt}]) を呼ぶ薄いラッパー

import sys
from pathlib import Path

# プロジェクトルートを sys.path に追加
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
  sys.path.insert(0, str(_PROJECT_ROOT))

import json

import httpx
import pytest
import respx

from tools.api_providers.providers import (
  AnthropicProvider,
  OpenAIProvider,
  GeminiProvider,
)


# --- Anthropic 関連（3 件） ---


@respx.mock
def test_anthropic_send_messages_single_user(monkeypatch):
  """単一の user メッセージで送信できる"""
  monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
  route = respx.post("https://api.anthropic.com/v1/messages").mock(
    return_value=httpx.Response(
      200, json={"content": [{"type": "text", "text": "応答"}]}
    )
  )
  provider = AnthropicProvider(model="claude-opus-4-7")
  result = provider.send_messages([{"role": "user", "content": "質問テキスト"}])
  assert result == "応答"
  assert route.called
  body = json.loads(route.calls[0].request.content.decode("utf-8"))
  assert body["messages"] == [{"role": "user", "content": "質問テキスト"}]


@respx.mock
def test_anthropic_send_messages_multi_turn(monkeypatch):
  """複数ターン（user/assistant 交互）で送信できる"""
  monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
  route = respx.post("https://api.anthropic.com/v1/messages").mock(
    return_value=httpx.Response(
      200, json={"content": [{"type": "text", "text": "最終判断"}]}
    )
  )
  provider = AnthropicProvider(model="claude-opus-4-7")
  messages = [
    {"role": "user", "content": "質問 1"},
    {"role": "assistant", "content": "回答 1"},
    {"role": "user", "content": "質問 2"},
  ]
  result = provider.send_messages(messages)
  assert result == "最終判断"
  body = json.loads(route.calls[0].request.content.decode("utf-8"))
  assert body["messages"] == messages


@respx.mock
def test_anthropic_send_messages_includes_assistant_in_body(monkeypatch):
  """assistant ロールのメッセージがリクエスト body の messages に含まれる"""
  monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
  route = respx.post("https://api.anthropic.com/v1/messages").mock(
    return_value=httpx.Response(
      200, json={"content": [{"type": "text", "text": "ok"}]}
    )
  )
  provider = AnthropicProvider(model="claude-opus-4-7")
  messages = [
    {"role": "user", "content": "u1"},
    {"role": "assistant", "content": "a1（事実応答）"},
    {"role": "user", "content": "u2"},
  ]
  provider.send_messages(messages)
  body = route.calls[0].request.content.decode("utf-8")
  assert "a1（事実応答）" in body


# --- OpenAI 関連（3 件） ---


@respx.mock
def test_openai_send_messages_single_user(monkeypatch):
  """単一の user メッセージで送信できる"""
  monkeypatch.setenv("OPENAI_API_KEY", "test-key")
  route = respx.post("https://api.openai.com/v1/chat/completions").mock(
    return_value=httpx.Response(
      200, json={"choices": [{"message": {"content": "応答"}}]}
    )
  )
  provider = OpenAIProvider(model="gpt-test")
  result = provider.send_messages([{"role": "user", "content": "質問テキスト"}])
  assert result == "応答"
  body = json.loads(route.calls[0].request.content.decode("utf-8"))
  assert body["messages"] == [{"role": "user", "content": "質問テキスト"}]


@respx.mock
def test_openai_send_messages_multi_turn(monkeypatch):
  """複数ターン（user/assistant 交互）で送信できる"""
  monkeypatch.setenv("OPENAI_API_KEY", "test-key")
  route = respx.post("https://api.openai.com/v1/chat/completions").mock(
    return_value=httpx.Response(
      200, json={"choices": [{"message": {"content": "最終判断"}}]}
    )
  )
  provider = OpenAIProvider(model="gpt-test")
  messages = [
    {"role": "user", "content": "質問 1"},
    {"role": "assistant", "content": "回答 1"},
    {"role": "user", "content": "質問 2"},
  ]
  result = provider.send_messages(messages)
  assert result == "最終判断"
  body = json.loads(route.calls[0].request.content.decode("utf-8"))
  assert body["messages"] == messages


@respx.mock
def test_openai_send_messages_includes_assistant_in_body(monkeypatch):
  """assistant ロールのメッセージがリクエスト body の messages に含まれる"""
  monkeypatch.setenv("OPENAI_API_KEY", "test-key")
  route = respx.post("https://api.openai.com/v1/chat/completions").mock(
    return_value=httpx.Response(
      200, json={"choices": [{"message": {"content": "ok"}}]}
    )
  )
  provider = OpenAIProvider(model="gpt-test")
  messages = [
    {"role": "user", "content": "u1"},
    {"role": "assistant", "content": "a1（事実応答）"},
    {"role": "user", "content": "u2"},
  ]
  provider.send_messages(messages)
  body = route.calls[0].request.content.decode("utf-8")
  assert "a1（事実応答）" in body


# --- Gemini 関連（4 件） ---


@respx.mock
def test_gemini_send_messages_single_user(monkeypatch):
  """単一の user メッセージで送信できる（contents.parts.text 形式に変換される）"""
  monkeypatch.setenv("GEMINI_API_KEY", "test-key")
  route = respx.post(
    "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash:generateContent"
  ).mock(
    return_value=httpx.Response(
      200,
      json={
        "candidates": [
          {"content": {"parts": [{"text": "応答"}], "role": "model"}}
        ]
      },
    )
  )
  provider = GeminiProvider(model="gemini-3.5-flash")
  result = provider.send_messages([{"role": "user", "content": "質問テキスト"}])
  assert result == "応答"
  body = json.loads(route.calls[0].request.content.decode("utf-8"))
  # Gemini 形式：contents 配列に role と parts.text を含む
  assert body["contents"] == [
    {"role": "user", "parts": [{"text": "質問テキスト"}]}
  ]


@respx.mock
def test_gemini_send_messages_multi_turn(monkeypatch):
  """複数ターン（user/assistant 交互）で送信できる"""
  monkeypatch.setenv("GEMINI_API_KEY", "test-key")
  route = respx.post(
    "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash:generateContent"
  ).mock(
    return_value=httpx.Response(
      200,
      json={
        "candidates": [
          {"content": {"parts": [{"text": "最終判断"}], "role": "model"}}
        ]
      },
    )
  )
  provider = GeminiProvider(model="gemini-3.5-flash")
  messages = [
    {"role": "user", "content": "質問 1"},
    {"role": "assistant", "content": "回答 1"},
    {"role": "user", "content": "質問 2"},
  ]
  result = provider.send_messages(messages)
  assert result == "最終判断"


@respx.mock
def test_gemini_send_messages_role_mapping(monkeypatch):
  """assistant ロールが model ロールにマッピングされる（Gemini の規約）"""
  monkeypatch.setenv("GEMINI_API_KEY", "test-key")
  route = respx.post(
    "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash:generateContent"
  ).mock(
    return_value=httpx.Response(
      200,
      json={
        "candidates": [
          {"content": {"parts": [{"text": "ok"}], "role": "model"}}
        ]
      },
    )
  )
  provider = GeminiProvider(model="gemini-3.5-flash")
  messages = [
    {"role": "user", "content": "u1"},
    {"role": "assistant", "content": "a1"},
  ]
  provider.send_messages(messages)
  body = json.loads(route.calls[0].request.content.decode("utf-8"))
  # assistant → model に置換されているか確認
  roles = [c["role"] for c in body["contents"]]
  assert roles == ["user", "model"]


@respx.mock
def test_gemini_send_messages_parts_text_format(monkeypatch):
  """content が parts.text 形式に変換される"""
  monkeypatch.setenv("GEMINI_API_KEY", "test-key")
  route = respx.post(
    "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash:generateContent"
  ).mock(
    return_value=httpx.Response(
      200,
      json={
        "candidates": [
          {"content": {"parts": [{"text": "ok"}], "role": "model"}}
        ]
      },
    )
  )
  provider = GeminiProvider(model="gemini-3.5-flash")
  provider.send_messages([{"role": "user", "content": "プロンプト本文"}])
  body = json.loads(route.calls[0].request.content.decode("utf-8"))
  assert body["contents"][0]["parts"] == [{"text": "プロンプト本文"}]


# --- 共通機能（3 件） ---


@respx.mock
def test_send_request_is_thin_wrapper_of_send_messages(monkeypatch):
  """既存の send_request(prompt) が send_messages([{user, prompt}]) を呼ぶ薄いラッパー（後方互換性）"""
  monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
  route = respx.post("https://api.anthropic.com/v1/messages").mock(
    return_value=httpx.Response(
      200, json={"content": [{"type": "text", "text": "ok"}]}
    )
  )
  provider = AnthropicProvider(model="claude-opus-4-7")
  result = provider.send_request("単一プロンプト")
  assert result == "ok"
  body = json.loads(route.calls[0].request.content.decode("utf-8"))
  # send_request の挙動が send_messages 経由でも変わらない
  assert body["messages"] == [{"role": "user", "content": "単一プロンプト"}]


def test_send_messages_empty_list_raises(monkeypatch):
  """空 messages リストで ValueError"""
  monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
  provider = AnthropicProvider(model="claude-opus-4-7")
  with pytest.raises(ValueError):
    provider.send_messages([])


@respx.mock
def test_send_messages_http_error_raises(monkeypatch):
  """HTTP 4xx／5xx で例外を投げる（既存のリトライ機構と整合）"""
  monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
  respx.post("https://api.anthropic.com/v1/messages").mock(
    return_value=httpx.Response(500, json={"error": "internal server error"})
  )
  provider = AnthropicProvider(model="claude-opus-4-7", max_retries=0)
  with pytest.raises(httpx.HTTPStatusError):
    provider.send_messages([{"role": "user", "content": "hello"}])
