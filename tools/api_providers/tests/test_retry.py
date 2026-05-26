# tools/api_providers/tests/test_retry.py
# リトライ機構のテスト（サブサイクル 4-A、TDD 先行）。
# HTTP 5xx／429／タイムアウトをリトライ対象とし、指数バックオフで再送する。
# 4xx（429 以外）はリトライ対象外（fail-fast）。
# 計画書 §5.9.7（API 経路と障害対応）参照。

import sys
from pathlib import Path
from unittest.mock import patch

# プロジェクトルートを sys.path に追加
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
  sys.path.insert(0, str(_PROJECT_ROOT))

import httpx
import pytest
import respx

from tools.api_providers.providers import AnthropicProvider, OpenAIProvider


_ANTHROPIC_URL = "https://api.anthropic.com/v1/messages"
_OPENAI_URL = "https://api.openai.com/v1/chat/completions"

_OK_ANTHROPIC = {"content": [{"type": "text", "text": "ok"}]}
_OK_OPENAI = {"choices": [{"message": {"content": "ok"}}]}


@pytest.fixture(autouse=True)
def _set_api_keys(monkeypatch):
  """全テスト共通：API キーの環境変数を設定。"""
  monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key-anthropic")
  monkeypatch.setenv("OPENAI_API_KEY", "test-key-openai")


# --- 1. 成功経路（リトライ不要） ---


@respx.mock
def test_no_retry_on_success():
  """1 回目で 200 OK ならリトライなしで成功、time.sleep は呼ばれない。"""
  respx.post(_ANTHROPIC_URL).mock(return_value=httpx.Response(200, json=_OK_ANTHROPIC))
  provider = AnthropicProvider(
    model="claude-opus-4-7",
    max_retries=2,
    initial_retry_delay_seconds=0.01,
  )
  with patch("tools.api_providers.providers.time.sleep") as mock_sleep:
    result = provider.send_request("hello")
  assert result == "ok"
  assert mock_sleep.call_count == 0


# --- 2. リトライ対象例外でのリトライ成功 ---


@respx.mock
def test_retry_on_500_then_success():
  """1 回目 500、2 回目 200 ならリトライ 1 回で成功。"""
  respx.post(_ANTHROPIC_URL).mock(
    side_effect=[
      httpx.Response(500, text="server error"),
      httpx.Response(200, json={"content": [{"type": "text", "text": "ok after retry"}]}),
    ]
  )
  provider = AnthropicProvider(
    model="claude-opus-4-7",
    max_retries=2,
    initial_retry_delay_seconds=0.01,
  )
  with patch("tools.api_providers.providers.time.sleep") as mock_sleep:
    result = provider.send_request("hello")
  assert result == "ok after retry"
  assert mock_sleep.call_count == 1


@respx.mock
def test_retry_on_429_then_success():
  """1 回目 429（過負荷／レート制限）、2 回目 200 ならリトライ 1 回で成功。"""
  respx.post(_ANTHROPIC_URL).mock(
    side_effect=[
      httpx.Response(429, text="rate limited"),
      httpx.Response(200, json=_OK_ANTHROPIC),
    ]
  )
  provider = AnthropicProvider(
    model="claude-opus-4-7",
    max_retries=2,
    initial_retry_delay_seconds=0.01,
  )
  with patch("tools.api_providers.providers.time.sleep") as mock_sleep:
    result = provider.send_request("hello")
  assert result == "ok"
  assert mock_sleep.call_count == 1


@respx.mock
def test_retry_on_timeout_then_success():
  """1 回目タイムアウト、2 回目 200 ならリトライ 1 回で成功。"""
  respx.post(_ANTHROPIC_URL).mock(
    side_effect=[
      httpx.TimeoutException("timed out"),
      httpx.Response(200, json=_OK_ANTHROPIC),
    ]
  )
  provider = AnthropicProvider(
    model="claude-opus-4-7",
    max_retries=2,
    initial_retry_delay_seconds=0.01,
  )
  with patch("tools.api_providers.providers.time.sleep") as mock_sleep:
    result = provider.send_request("hello")
  assert result == "ok"
  assert mock_sleep.call_count == 1


# --- 3. リトライ対象外（fail-fast） ---


@respx.mock
def test_no_retry_on_400():
  """1 回目 400（クライアント側エラー、429 を除く）は即失敗、リトライしない。"""
  respx.post(_ANTHROPIC_URL).mock(
    return_value=httpx.Response(400, text="bad request"),
  )
  provider = AnthropicProvider(
    model="claude-opus-4-7",
    max_retries=2,
    initial_retry_delay_seconds=0.01,
  )
  with patch("tools.api_providers.providers.time.sleep") as mock_sleep:
    with pytest.raises(httpx.HTTPStatusError):
      provider.send_request("hello")
  assert mock_sleep.call_count == 0


# --- 4. リトライ回数の上限 ---


@respx.mock
def test_exhaust_retries_with_500():
  """max_retries=1 で 500 が 2 回続けば HTTPStatusError を投げる。"""
  respx.post(_ANTHROPIC_URL).mock(return_value=httpx.Response(500, text="server error"))
  provider = AnthropicProvider(
    model="claude-opus-4-7",
    max_retries=1,
    initial_retry_delay_seconds=0.01,
  )
  with patch("tools.api_providers.providers.time.sleep") as mock_sleep:
    with pytest.raises(httpx.HTTPStatusError):
      provider.send_request("hello")
  # 1 回目失敗 → sleep 1 回 → 2 回目失敗 → リトライ上限到達 → 例外
  assert mock_sleep.call_count == 1


@respx.mock
def test_max_retries_zero_no_retry():
  """max_retries=0 ならリトライなし、500 で即失敗。"""
  respx.post(_ANTHROPIC_URL).mock(return_value=httpx.Response(500, text="server error"))
  provider = AnthropicProvider(
    model="claude-opus-4-7",
    max_retries=0,
    initial_retry_delay_seconds=0.01,
  )
  with patch("tools.api_providers.providers.time.sleep") as mock_sleep:
    with pytest.raises(httpx.HTTPStatusError):
      provider.send_request("hello")
  assert mock_sleep.call_count == 0


# --- 5. 指数バックオフ ---


@respx.mock
def test_exponential_backoff_delays():
  """max_retries=2、500 が 3 回続いて最後に成功、sleep が指数 2 倍で呼ばれる。"""
  respx.post(_ANTHROPIC_URL).mock(
    side_effect=[
      httpx.Response(500, text="server error"),
      httpx.Response(500, text="server error"),
      httpx.Response(200, json=_OK_ANTHROPIC),
    ]
  )
  provider = AnthropicProvider(
    model="claude-opus-4-7",
    max_retries=2,
    initial_retry_delay_seconds=0.5,
  )
  with patch("tools.api_providers.providers.time.sleep") as mock_sleep:
    result = provider.send_request("hello")
  assert result == "ok"
  assert mock_sleep.call_count == 2
  # 1 回目リトライ前：0.5 秒、2 回目リトライ前：1.0 秒（指数 2 倍）
  call_args = [call.args[0] for call in mock_sleep.call_args_list]
  assert call_args == [0.5, 1.0]


# --- 6. OpenAI プロバイダーでも同様にリトライ ---


@respx.mock
def test_openai_provider_retry_on_500():
  """OpenAIProvider でも 500 でリトライする。"""
  respx.post(_OPENAI_URL).mock(
    side_effect=[
      httpx.Response(500, text="server error"),
      httpx.Response(200, json=_OK_OPENAI),
    ]
  )
  provider = OpenAIProvider(
    model="gpt-test",
    max_retries=2,
    initial_retry_delay_seconds=0.01,
  )
  with patch("tools.api_providers.providers.time.sleep") as mock_sleep:
    result = provider.send_request("hello")
  assert result == "ok"
  assert mock_sleep.call_count == 1


# --- 7. 複数回リトライしてから成功 ---


@respx.mock
def test_multiple_retries_eventually_succeed():
  """max_retries=3、500 が 3 回続いて 4 回目で 200。リトライ 3 回で成功。"""
  respx.post(_ANTHROPIC_URL).mock(
    side_effect=[
      httpx.Response(500, text="error 1"),
      httpx.Response(500, text="error 2"),
      httpx.Response(500, text="error 3"),
      httpx.Response(200, json=_OK_ANTHROPIC),
    ]
  )
  provider = AnthropicProvider(
    model="claude-opus-4-7",
    max_retries=3,
    initial_retry_delay_seconds=0.01,
  )
  with patch("tools.api_providers.providers.time.sleep") as mock_sleep:
    result = provider.send_request("hello")
  assert result == "ok"
  assert mock_sleep.call_count == 3
