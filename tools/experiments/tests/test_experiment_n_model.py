# tools/experiments/tests/test_experiment_n_model.py
# 実験用一時スクリプト _experiment_n_model.py のテスト（TDD 先行、初回は全件失敗を期待）。
# セッション 31（2026-05-27）の 7 モデル比較実験、第 4 段階 4-C で着手。
# 利用者明示承認の出典：「はい」（推奨案の組み合わせを承認、セッション 31）。
#
# スクリプト仕様（推奨案の組み合わせ）：
# - 責務範囲：対話履歴管理を含む（案 Q）
# - 出力形式：標準出力に YAML（案 b）
# - 保存先：tools/experiments/_experiment_n_model.py（案 (ii)）
# - 判定者指定：プロバイダー名 ＋ モデル名（案 (β)）
# - 引数：--provider／--model／--prompt-file／--history-file（省略可）／--turn-number（省略可）
# - 標準出力 YAML：provider／model／turn_number／duration_seconds／sent_messages_count／response_text

import sys
from pathlib import Path

# プロジェクトルートを sys.path に追加
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
  sys.path.insert(0, str(_PROJECT_ROOT))

import httpx
import pytest
import respx
import yaml

# 実装は未着手。tools.experiments._experiment_n_model の追加が TDD の目標。
from tools.experiments._experiment_n_model import (
  main,
  build_messages_from_history,
  load_prompt_file,
)


# --- A. プロンプトファイル読み込み（3 件） ---


def test_load_prompt_file(tmp_path):
  """指定されたパスのテキストファイルを読み込む"""
  prompt_path = tmp_path / "prompt.txt"
  prompt_path.write_text("テストプロンプト本文")
  result = load_prompt_file(str(prompt_path))
  assert result == "テストプロンプト本文"


def test_load_prompt_file_missing_raises(tmp_path):
  """存在しないファイルパスは FileNotFoundError"""
  with pytest.raises((FileNotFoundError, IOError)):
    load_prompt_file(str(tmp_path / "nonexistent.txt"))


def test_load_prompt_file_with_utf8(tmp_path):
  """UTF-8 日本語テキストを正しく読み込む"""
  prompt_path = tmp_path / "prompt.txt"
  prompt_path.write_text("UTF-8 日本語テスト", encoding="utf-8")
  result = load_prompt_file(str(prompt_path))
  assert "日本語テスト" in result


# --- B. 履歴ファイル読み込みとメッセージ組み立て（3 件） ---


def test_build_messages_from_history_no_history():
  """履歴ファイル省略時（None）は user メッセージ 1 件のみ"""
  result = build_messages_from_history("プロンプト本文", history_file_path=None)
  assert result == [{"role": "user", "content": "プロンプト本文"}]


def test_build_messages_from_history_with_history(tmp_path):
  """履歴ファイル指定時は履歴 ＋ 新プロンプト（user）が追加される"""
  history_path = tmp_path / "history.yaml"
  history_path.write_text(
    yaml.dump(
      [
        {"role": "user", "content": "前ターンの質問"},
        {"role": "assistant", "content": "前ターンの応答"},
      ],
      allow_unicode=True,
    ),
    encoding="utf-8",
  )
  result = build_messages_from_history("新プロンプト", str(history_path))
  assert result == [
    {"role": "user", "content": "前ターンの質問"},
    {"role": "assistant", "content": "前ターンの応答"},
    {"role": "user", "content": "新プロンプト"},
  ]


def test_build_messages_from_history_invalid_yaml(tmp_path):
  """不正な YAML 形式は ValueError または yaml.YAMLError"""
  history_path = tmp_path / "history.yaml"
  history_path.write_text("不正な内容: [unclosed", encoding="utf-8")
  with pytest.raises((yaml.YAMLError, ValueError)):
    build_messages_from_history("プロンプト", str(history_path))


# --- C. providers.py 連携（3 件） ---


@respx.mock
def test_main_calls_anthropic(monkeypatch, tmp_path):
  """anthropic-api への呼び出しが成功する"""
  monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
  prompt_path = tmp_path / "prompt.txt"
  prompt_path.write_text("質問テキスト")

  route = respx.post("https://api.anthropic.com/v1/messages").mock(
    return_value=httpx.Response(
      200, json={"content": [{"type": "text", "text": "Anthropic 応答"}]}
    )
  )

  exit_code = main(
    [
      "--provider", "anthropic-api",
      "--model", "claude-opus-4-7",
      "--prompt-file", str(prompt_path),
    ]
  )
  assert exit_code == 0
  assert route.called


@respx.mock
def test_main_calls_openai(monkeypatch, tmp_path):
  """openai-api への呼び出しが成功する"""
  monkeypatch.setenv("OPENAI_API_KEY", "test-key")
  prompt_path = tmp_path / "prompt.txt"
  prompt_path.write_text("質問")

  route = respx.post("https://api.openai.com/v1/chat/completions").mock(
    return_value=httpx.Response(
      200, json={"choices": [{"message": {"content": "OpenAI 応答"}}]}
    )
  )

  exit_code = main(
    [
      "--provider", "openai-api",
      "--model", "gpt-5.5",
      "--prompt-file", str(prompt_path),
    ]
  )
  assert exit_code == 0
  assert route.called


@respx.mock
def test_main_calls_gemini(monkeypatch, tmp_path):
  """gemini-api への呼び出しが成功する"""
  monkeypatch.setenv("GEMINI_API_KEY", "test-key")
  prompt_path = tmp_path / "prompt.txt"
  prompt_path.write_text("質問")

  route = respx.post(
    "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash:generateContent"
  ).mock(
    return_value=httpx.Response(
      200,
      json={
        "candidates": [
          {"content": {"parts": [{"text": "Gemini 応答"}], "role": "model"}}
        ]
      },
    )
  )

  exit_code = main(
    [
      "--provider", "gemini-api",
      "--model", "gemini-3.5-flash",
      "--prompt-file", str(prompt_path),
    ]
  )
  assert exit_code == 0
  assert route.called


# --- D. 出力形式（4 件） ---


@respx.mock
def test_main_outputs_yaml(monkeypatch, tmp_path, capsys):
  """標準出力が YAML としてパース可能"""
  monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
  prompt_path = tmp_path / "prompt.txt"
  prompt_path.write_text("質問")
  respx.post("https://api.anthropic.com/v1/messages").mock(
    return_value=httpx.Response(
      200, json={"content": [{"type": "text", "text": "応答"}]}
    )
  )

  main(
    [
      "--provider", "anthropic-api",
      "--model", "claude-opus-4-7",
      "--prompt-file", str(prompt_path),
    ]
  )
  captured = capsys.readouterr()
  parsed = yaml.safe_load(captured.out)
  assert isinstance(parsed, dict)


@respx.mock
def test_main_output_includes_provider_and_model(monkeypatch, tmp_path, capsys):
  """出力 YAML に provider と model が含まれる"""
  monkeypatch.setenv("OPENAI_API_KEY", "test-key")
  prompt_path = tmp_path / "prompt.txt"
  prompt_path.write_text("質問")
  respx.post("https://api.openai.com/v1/chat/completions").mock(
    return_value=httpx.Response(
      200, json={"choices": [{"message": {"content": "応答"}}]}
    )
  )

  main(
    [
      "--provider", "openai-api",
      "--model", "gpt-5.5",
      "--prompt-file", str(prompt_path),
    ]
  )
  captured = capsys.readouterr()
  parsed = yaml.safe_load(captured.out)
  assert parsed["provider"] == "openai-api"
  assert parsed["model"] == "gpt-5.5"


@respx.mock
def test_main_output_includes_duration_seconds(monkeypatch, tmp_path, capsys):
  """出力 YAML に duration_seconds（数値）が含まれる"""
  monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
  prompt_path = tmp_path / "prompt.txt"
  prompt_path.write_text("質問")
  respx.post("https://api.anthropic.com/v1/messages").mock(
    return_value=httpx.Response(
      200, json={"content": [{"type": "text", "text": "応答"}]}
    )
  )

  main(
    [
      "--provider", "anthropic-api",
      "--model", "claude-opus-4-7",
      "--prompt-file", str(prompt_path),
    ]
  )
  captured = capsys.readouterr()
  parsed = yaml.safe_load(captured.out)
  assert "duration_seconds" in parsed
  assert isinstance(parsed["duration_seconds"], (int, float))
  assert parsed["duration_seconds"] >= 0


@respx.mock
def test_main_output_response_text_matches(monkeypatch, tmp_path, capsys):
  """出力 YAML の response_text が API レスポンスと一致"""
  monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
  prompt_path = tmp_path / "prompt.txt"
  prompt_path.write_text("質問")
  respx.post("https://api.anthropic.com/v1/messages").mock(
    return_value=httpx.Response(
      200, json={"content": [{"type": "text", "text": "期待される応答テキスト"}]}
    )
  )

  main(
    [
      "--provider", "anthropic-api",
      "--model", "claude-opus-4-7",
      "--prompt-file", str(prompt_path),
    ]
  )
  captured = capsys.readouterr()
  parsed = yaml.safe_load(captured.out)
  assert parsed["response_text"] == "期待される応答テキスト"


# --- E. エラー処理（2 件） ---


def test_main_missing_required_args_raises():
  """必須引数欠落時は SystemExit（argparse のエラー）"""
  with pytest.raises(SystemExit):
    main([])


@respx.mock
def test_main_unknown_provider_returns_nonzero(monkeypatch, tmp_path):
  """不明なプロバイダー名で非ゼロ終了"""
  monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
  prompt_path = tmp_path / "prompt.txt"
  prompt_path.write_text("質問")

  exit_code = main(
    [
      "--provider", "unknown-provider",
      "--model", "any-model",
      "--prompt-file", str(prompt_path),
    ]
  )
  assert exit_code != 0
