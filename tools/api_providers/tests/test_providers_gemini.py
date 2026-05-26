# tools/api_providers/tests/test_providers_gemini.py
# Google Gemini プロバイダーのテスト（TDD 先行、初回は全件失敗を期待）。
# 計画書 §5.9.7.1（API 経路先取り実装、設計案 P）とセッション 31（2026-05-27）の
# 計画変更「7 モデル比較実験への拡大、google gemini API を追加」に基づく。
# 利用者明示承認の出典：「対象モデルを拡大し、google gemini API を追加する。
# gemini-3.5-flash，gemini-3.1-pro-preview を対象」（セッション 31）。
#
# Gemini API の特徴：
# - エンドポイント形式：https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent
#   model 名を URL パスに含むため、Anthropic／OpenAI とは URL 組み立てが異なる
# - 認証方式：ヘッダー x-goog-api-key（既存パターンに整合）
# - リクエスト形式：contents 配列に parts.text を入れる
# - レスポンス形式：candidates[0].content.parts[0].text からテキストを抽出

import sys
from pathlib import Path

# プロジェクトルートを sys.path に追加
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
  sys.path.insert(0, str(_PROJECT_ROOT))

import httpx
import pytest
import respx

# 実装は未着手。GeminiProvider と get_provider("gemini-api") の追加が TDD の目標。
from tools.api_providers.providers import (
  get_provider,
  GeminiProvider,
)


# --- レジストリ登録（2 件） ---


def test_get_provider_gemini_api():
  """provider 名 gemini-api から GeminiProvider クラスを返す"""
  cls = get_provider("gemini-api")
  assert cls is GeminiProvider


def test_gemini_provider_is_registered_in_known_providers():
  """既存の anthropic-api／openai-api と並んで gemini-api が登録されている"""
  # get_provider の不明値エラーを使って、登録されていることを間接確認
  # 登録されていれば例外は出ない
  cls = get_provider("gemini-api")
  assert cls is not None


# --- 環境変数と初期化（3 件） ---


def test_gemini_provider_requires_api_key(monkeypatch):
  """GEMINI_API_KEY 未設定で初期化エラー"""
  monkeypatch.delenv("GEMINI_API_KEY", raising=False)
  with pytest.raises((KeyError, RuntimeError, EnvironmentError)):
    GeminiProvider(model="gemini-3.5-flash")


def test_gemini_provider_reads_env(monkeypatch):
  """環境変数 GEMINI_API_KEY から API キーを読む"""
  monkeypatch.setenv("GEMINI_API_KEY", "test-key-gemini")
  provider = GeminiProvider(model="gemini-3.5-flash")
  assert provider.api_key == "test-key-gemini"


def test_gemini_provider_has_model_attribute(monkeypatch):
  """プロバイダーは model 属性を持つ"""
  monkeypatch.setenv("GEMINI_API_KEY", "test-key")
  provider = GeminiProvider(model="gemini-3.1-pro-preview")
  assert provider.model == "gemini-3.1-pro-preview"


# --- send_request のリクエスト送信（5 件） ---


@respx.mock
def test_gemini_send_request_calls_correct_url(monkeypatch):
  """Gemini の URL（モデル名を含む）に POST する"""
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
  provider.send_request("hello")
  assert route.called


@respx.mock
def test_gemini_send_request_url_changes_with_model(monkeypatch):
  """model 名を変えると URL のパスも変わる"""
  monkeypatch.setenv("GEMINI_API_KEY", "test-key")
  route = respx.post(
    "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-pro-preview:generateContent"
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
  provider = GeminiProvider(model="gemini-3.1-pro-preview")
  provider.send_request("hello")
  assert route.called


@respx.mock
def test_gemini_send_request_uses_api_key_header(monkeypatch):
  """x-goog-api-key ヘッダに API キーが入る"""
  monkeypatch.setenv("GEMINI_API_KEY", "test-key-gemini")
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
  provider.send_request("hello")
  request = route.calls[0].request
  assert request.headers["x-goog-api-key"] == "test-key-gemini"


@respx.mock
def test_gemini_send_request_includes_prompt_in_body(monkeypatch):
  """リクエストボディの contents.parts.text に prompt が含まれる"""
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
  provider.send_request("プロンプト本文テキスト")
  body = route.calls[0].request.content.decode("utf-8")
  assert "プロンプト本文テキスト" in body


@respx.mock
def test_gemini_send_request_extracts_text_from_response(monkeypatch):
  """レスポンス JSON の candidates[0].content.parts[0].text を返す"""
  monkeypatch.setenv("GEMINI_API_KEY", "test-key")
  respx.post(
    "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash:generateContent"
  ).mock(
    return_value=httpx.Response(
      200,
      json={
        "candidates": [
          {"content": {"parts": [{"text": "Gemini からの応答"}], "role": "model"}}
        ]
      },
    )
  )
  provider = GeminiProvider(model="gemini-3.5-flash")
  result = provider.send_request("質問")
  assert result == "Gemini からの応答"


# --- エラー処理とリトライ機構の継承（2 件） ---


@respx.mock
def test_gemini_send_request_http_error_raises(monkeypatch):
  """HTTP 4xx／5xx で例外を投げる（既存のリトライ機構が動く）"""
  monkeypatch.setenv("GEMINI_API_KEY", "test-key")
  respx.post(
    "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash:generateContent"
  ).mock(return_value=httpx.Response(400, json={"error": {"message": "Bad request"}}))
  provider = GeminiProvider(model="gemini-3.5-flash")
  with pytest.raises(httpx.HTTPStatusError):
    provider.send_request("hello")


@respx.mock
def test_gemini_send_request_retries_on_500(monkeypatch):
  """HTTP 500 で max_retries までリトライする（既存のリトライ機構を継承）"""
  monkeypatch.setenv("GEMINI_API_KEY", "test-key")
  # 1 回目 500、2 回目 200 を返すように side_effect で順次レスポンス指定
  route = respx.post(
    "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash:generateContent"
  ).mock(
    side_effect=[
      httpx.Response(500, json={"error": {"message": "Internal server error"}}),
      httpx.Response(
        200,
        json={
          "candidates": [
            {"content": {"parts": [{"text": "ok"}], "role": "model"}}
          ]
        },
      ),
    ]
  )
  # 初期リトライ遅延を 0 にして高速化
  provider = GeminiProvider(
    model="gemini-3.5-flash",
    max_retries=1,
    initial_retry_delay_seconds=0,
  )
  result = provider.send_request("hello")
  assert result == "ok"
  assert route.call_count == 2
