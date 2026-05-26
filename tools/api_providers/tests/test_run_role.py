# tools/api_providers/tests/test_run_role.py
# run_role エントリポイントのテスト（サブサイクル 4-C、TDD 先行）。
# 計画書 §5.9.7.1 の入出力契約に準拠する。
# プロバイダーは MagicMock で置換し、in-process でテストする。

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

# プロジェクトルートを sys.path に追加
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
  sys.path.insert(0, str(_PROJECT_ROOT))

import pytest
import yaml

from tools.api_providers.run_role import build_prompt, main


# --- fixtures ---


@pytest.fixture
def tmp_target_file(tmp_path):
  target = tmp_path / "target.md"
  target.write_text("対象文書の内容\n要件の本文を記載", encoding="utf-8")
  return target


@pytest.fixture
def tmp_prior_finding(tmp_path):
  prior = tmp_path / "prior.yaml"
  prior.write_text(
    "findings:\n  - severity: WARN\n    description: 前段の所見\n",
    encoding="utf-8",
  )
  return prior


@pytest.fixture
def tmp_config(tmp_path):
  config_path = tmp_path / "api-settings.yaml"
  config_path.write_text(
    """
connection:
  timeout_seconds: 60
  max_retries: 1
default:
  primary:
    path: api
    provider: anthropic-api
    model: claude-opus-4-7
  adversarial:
    path: api
    provider: anthropic-api
    model: claude-sonnet-4-6
  judgment:
    path: api
    provider: anthropic-api
    model: claude-opus-4-7
""",
    encoding="utf-8",
  )
  return config_path


def _make_mock_provider(send_response="findings: []\n", side_effect=None):
  """get_provider をモック化する補助関数。"""
  mock_instance = MagicMock()
  if side_effect is not None:
    mock_instance.send_request.side_effect = side_effect
  else:
    mock_instance.send_request.return_value = send_response
  mock_cls = MagicMock(return_value=mock_instance)
  return mock_cls, mock_instance


# --- 1. build_prompt の正常系 ---


def test_build_prompt_includes_target_content(tmp_target_file):
  """build_prompt の出力に対象文書の内容が含まれる。"""
  prompt = build_prompt(str(tmp_target_file), "requirements_triad_review", "観点-1", [])
  assert "対象文書の内容" in prompt
  assert "要件の本文を記載" in prompt


def test_build_prompt_includes_phase(tmp_target_file):
  """build_prompt の出力に段名が含まれる。"""
  prompt = build_prompt(str(tmp_target_file), "design_triad_review", "観点-1", [])
  assert "design_triad_review" in prompt


def test_build_prompt_includes_criteria(tmp_target_file):
  """build_prompt の出力に観点識別子が含まれる。"""
  prompt = build_prompt(str(tmp_target_file), "requirements", "観点-3", [])
  assert "観点-3" in prompt


def test_build_prompt_includes_prior_finding(tmp_target_file, tmp_prior_finding):
  """build_prompt の出力に前段所見の内容が含まれる。"""
  prompt = build_prompt(
    str(tmp_target_file),
    "requirements",
    "観点-1",
    [str(tmp_prior_finding)],
  )
  assert "前段の所見" in prompt


def test_build_prompt_includes_multiple_prior_findings(tmp_target_file, tmp_path):
  """build_prompt が複数の前段所見をすべて含む。"""
  p1 = tmp_path / "prior1.yaml"
  p1.write_text(
    "findings:\n  - description: 所見 アルファ\n", encoding="utf-8"
  )
  p2 = tmp_path / "prior2.yaml"
  p2.write_text(
    "findings:\n  - description: 所見 ベータ\n", encoding="utf-8"
  )
  prompt = build_prompt(
    str(tmp_target_file),
    "requirements",
    "観点-1",
    [str(p1), str(p2)],
  )
  assert "所見 アルファ" in prompt
  assert "所見 ベータ" in prompt


# --- 2. main の正常系 ---


def test_main_outputs_formatted_yaml(tmp_target_file, tmp_config, monkeypatch, capsys):
  """main が正常系で整形済み YAML を標準出力に書く。"""
  monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
  mock_response = """
findings:
  - severity: WARN
    target_location: a.md
    description: テスト所見
    rationale: テスト根拠
"""
  mock_cls, _ = _make_mock_provider(send_response=mock_response)
  with patch("tools.api_providers.run_role.get_provider", return_value=mock_cls):
    exit_code = main(
      [
        "--role", "primary",
        "--target", str(tmp_target_file),
        "--phase", "requirements_triad_review",
        "--criteria", "観点-1",
        "--config", str(tmp_config),
      ]
    )
  assert exit_code == 0
  captured = capsys.readouterr()
  parsed = yaml.safe_load(captured.out)
  assert parsed["role"] == "primary"
  assert parsed["provider"] == "anthropic-api"
  assert parsed["model"] == "claude-opus-4-7"
  assert parsed["attempts"] == 1
  assert len(parsed["findings"]) == 1
  assert parsed["findings"][0]["severity"] == "WARN"


def test_main_duration_seconds_is_present(
  tmp_target_file, tmp_config, monkeypatch, capsys
):
  """main の出力に duration_seconds（所要時間）が含まれる。"""
  monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
  mock_cls, _ = _make_mock_provider()
  with patch("tools.api_providers.run_role.get_provider", return_value=mock_cls):
    main(
      [
        "--role", "primary",
        "--target", str(tmp_target_file),
        "--phase", "requirements",
        "--criteria", "観点-1",
        "--config", str(tmp_config),
      ]
    )
  captured = capsys.readouterr()
  parsed = yaml.safe_load(captured.out)
  assert "duration_seconds" in parsed
  assert isinstance(parsed["duration_seconds"], (int, float))
  assert parsed["duration_seconds"] >= 0


# --- 3. main の異常系 ---


def test_main_missing_required_args_raises():
  """必須引数が不足していたら SystemExit（argparse 既定動作）。"""
  with pytest.raises(SystemExit):
    main(["--role", "primary"])  # --target, --phase, --criteria が欠落


def test_main_provider_error_returns_nonzero(
  tmp_target_file, tmp_config, monkeypatch, capsys
):
  """プロバイダーが例外を投げたら非ゼロ終了、標準エラーに理由を出力。"""
  monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
  mock_cls, _ = _make_mock_provider(side_effect=RuntimeError("API 呼び出し失敗"))
  with patch("tools.api_providers.run_role.get_provider", return_value=mock_cls):
    exit_code = main(
      [
        "--role", "primary",
        "--target", str(tmp_target_file),
        "--phase", "requirements",
        "--criteria", "観点-1",
        "--config", str(tmp_config),
      ]
    )
  assert exit_code != 0
  captured = capsys.readouterr()
  assert "エラー" in captured.err or "error" in captured.err.lower()


# --- 4. variant 切替 ---


def test_main_uses_variant_when_specified(
  tmp_target_file, tmp_path, monkeypatch, capsys
):
  """--variant が指定されたら variants から役設定を取得する。"""
  monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
  monkeypatch.setenv("OPENAI_API_KEY", "test-key")
  config_path = tmp_path / "api-settings.yaml"
  config_path.write_text(
    """
connection:
  timeout_seconds: 60
  max_retries: 1
default:
  primary:
    path: api
    provider: anthropic-api
    model: claude-opus-4-7
variants:
  openai_variant:
    primary:
      path: api
      provider: openai-api
      model: gpt-test
""",
    encoding="utf-8",
  )
  mock_cls, _ = _make_mock_provider()
  with patch("tools.api_providers.run_role.get_provider", return_value=mock_cls):
    main(
      [
        "--role", "primary",
        "--variant", "openai_variant",
        "--target", str(tmp_target_file),
        "--phase", "requirements",
        "--criteria", "観点-1",
        "--config", str(config_path),
      ]
    )
  captured = capsys.readouterr()
  parsed = yaml.safe_load(captured.out)
  assert parsed["provider"] == "openai-api"
  assert parsed["model"] == "gpt-test"
