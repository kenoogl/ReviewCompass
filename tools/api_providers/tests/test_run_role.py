# tools/api_providers/tests/test_run_role.py
# run_role エントリポイントのテスト（サブサイクル 4-C、TDD 先行）。
# 計画書 §5.9.7.1 の入出力契約に準拠する。
# プロバイダーは MagicMock で置換し、in-process でテストする。

import hashlib
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


def test_build_prompt_uses_anthropic_specific_template(tmp_target_file):
  """anthropic-api では code fence / review wrapper を禁止する専用テンプレートを使う。"""
  prompt = build_prompt(
    str(tmp_target_file),
    "post_write_verification",
    "観点-1",
    [],
    provider_name="anthropic-api",
    model="claude-sonnet-4-6",
  )
  assert "model_id: claude-sonnet-4-6" in prompt
  assert "Do not wrap the YAML in Markdown code fences" in prompt
  assert "Do not use review:" in prompt
  assert "top-level key must be exactly findings" in prompt


def test_build_prompt_uses_default_template_for_unknown_provider(tmp_target_file):
  """未知 provider では共通テンプレートへ fallback する。"""
  prompt = build_prompt(
    str(tmp_target_file),
    "post_write_verification",
    "観点-1",
    [],
    provider_name="unknown-provider",
    model="unknown-model",
  )
  assert "prompt_id: default_review" in prompt
  assert "top-level key must be exactly findings" in prompt
  assert "findings: []" in prompt


def test_build_prompt_does_not_replace_placeholders_inside_target_content(tmp_path):
  """対象文書内の template placeholder 文字列は本文として保持する。"""
  target = tmp_path / "target.md"
  target.write_text(
    "# Target\n{{ prior_findings }}\n{{ target_path }}\n",
    encoding="utf-8",
  )

  prompt = build_prompt(
    str(target),
    "post_write_verification",
    "観点-1",
    [],
    provider_name="anthropic-api",
    model="claude-sonnet-4-6",
  )

  assert "# Target\n{{ prior_findings }}\n{{ target_path }}" in prompt


def test_build_prompt_renders_prior_findings_in_provider_template(
  tmp_target_file,
  tmp_prior_finding,
):
  """provider template 経由でも前段所見がプロンプトへ入る。"""
  prompt = build_prompt(
    str(tmp_target_file),
    "post_write_verification",
    "観点-1",
    [str(tmp_prior_finding)],
    provider_name="openai-api",
    model="gpt-5.4",
  )

  assert "# 前段所見 1" in prompt
  assert "前段の所見" in prompt


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


# --- 5. raw / parsed / review-run 成果物 ---


def test_main_writes_raw_out_before_parse_failure(
  tmp_target_file, tmp_config, tmp_path, monkeypatch, capsys
):
  """parse 失敗時でも --raw-out に provider 生応答を保存する。"""
  monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
  raw_out = tmp_path / "raw.txt"
  mock_cls, _ = _make_mock_provider(send_response="not: [valid\n")
  with patch("tools.api_providers.run_role.get_provider", return_value=mock_cls):
    exit_code = main(
      [
        "--role", "primary",
        "--target", str(tmp_target_file),
        "--phase", "requirements",
        "--criteria", "観点-1",
        "--config", str(tmp_config),
        "--raw-out", str(raw_out),
      ]
    )

  assert exit_code != 0
  assert raw_out.read_text(encoding="utf-8") == "not: [valid\n"
  captured = capsys.readouterr()
  assert "エラー" in captured.err


def test_main_writes_parsed_out_on_parse_success(
  tmp_target_file, tmp_config, tmp_path, monkeypatch, capsys
):
  """parse 成功時に --parsed-out へ整形済み YAML を保存する。"""
  monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
  parsed_out = tmp_path / "parsed.yaml"
  mock_response = """
findings:
  - severity: INFO
    target_location: a.md
    description: 指摘なし
    rationale: テスト
"""
  mock_cls, _ = _make_mock_provider(send_response=mock_response)
  with patch("tools.api_providers.run_role.get_provider", return_value=mock_cls):
    exit_code = main(
      [
        "--role", "primary",
        "--target", str(tmp_target_file),
        "--phase", "requirements",
        "--criteria", "観点-1",
        "--config", str(tmp_config),
        "--parsed-out", str(parsed_out),
      ]
    )

  assert exit_code == 0
  captured = capsys.readouterr()
  assert captured.out.count("\n") == 1
  assert captured.out.startswith("[OK] run_role ")
  assert f"parsed={parsed_out}" in captured.out
  parsed = yaml.safe_load(parsed_out.read_text(encoding="utf-8"))
  assert parsed["role"] == "primary"
  assert parsed["model"] == "claude-opus-4-7"
  assert parsed["findings"][0]["severity"] == "INFO"


def test_main_updates_review_run_artifacts(
  tmp_target_file, tmp_config, tmp_path, monkeypatch, capsys
):
  """--review-run-dir 指定時に raw、parsed、rounds、summary、target manifest を生成する。"""
  monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
  review_run_dir = tmp_path / "review-run"
  mock_response = """
findings:
  - severity: WARN
    target_location: a.md
    description: 要確認
    rationale: テスト
"""
  mock_cls, _ = _make_mock_provider(send_response=mock_response)
  with patch("tools.api_providers.run_role.get_provider", return_value=mock_cls):
    exit_code = main(
      [
        "--role", "primary",
        "--target", str(tmp_target_file),
        "--phase", "post_write_verification",
        "--criteria", "観点-1",
        "--config", str(tmp_config),
        "--review-run-dir", str(review_run_dir),
        "--round-id", "round-1",
      ]
    )

  assert exit_code == 0
  captured = capsys.readouterr()
  assert captured.out.count("\n") == 1
  assert captured.out.startswith("[OK] run_role ")
  assert "role=primary" in captured.out
  assert "model=claude-opus-4-7" in captured.out
  assert "findings=1" in captured.out
  assert f"review_run_dir={review_run_dir}" in captured.out
  raw_path = review_run_dir / "raw" / "claude-opus-4-7.round-1.txt"
  parsed_path = review_run_dir / "parsed" / "claude-opus-4-7.round-1.yaml"
  assert raw_path.is_file()
  assert parsed_path.is_file()

  target_manifest = yaml.safe_load(
    (review_run_dir / "target-manifest.yaml").read_text(encoding="utf-8")
  )
  rounds = yaml.safe_load((review_run_dir / "rounds.yaml").read_text(encoding="utf-8"))
  summary = yaml.safe_load(
    (review_run_dir / "model-result-summary.yaml").read_text(encoding="utf-8")
  )

  assert target_manifest["target_files"][0]["path"] == str(tmp_target_file)
  model_result = rounds["model_results"][0]
  assert model_result["model_id"] == "claude-opus-4-7"
  assert model_result["raw_path"] == "raw/claude-opus-4-7.round-1.txt"
  assert model_result["parsed_path"] == "parsed/claude-opus-4-7.round-1.yaml"
  assert model_result["parse_status"] == "parsed"
  assert len(model_result["raw_sha256"]) == 64
  assert len(model_result["parsed_sha256"]) == 64

  summary_model = summary["models"][0]
  assert summary_model["model_id"] == "claude-opus-4-7"
  assert summary_model["parse_status"] == "parsed"
  assert summary_model["triage_status"] == "triage_pending"
  assert summary_model["findings_count"] == 1
  assert summary_model["findings_count_by_severity"]["WARN"] == 1


def test_main_verbose_outputs_formatted_yaml_with_artifact_sink(
  tmp_target_file, tmp_config, tmp_path, monkeypatch, capsys
):
  """--verbose では保存先があっても整形済み YAML を stdout に出す。"""
  monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
  parsed_out = tmp_path / "parsed.yaml"
  mock_cls, _ = _make_mock_provider(send_response="findings: []\n")
  with patch("tools.api_providers.run_role.get_provider", return_value=mock_cls):
    exit_code = main(
      [
        "--role", "primary",
        "--target", str(tmp_target_file),
        "--phase", "requirements",
        "--criteria", "観点-1",
        "--config", str(tmp_config),
        "--parsed-out", str(parsed_out),
        "--verbose",
      ]
    )

  assert exit_code == 0
  captured = capsys.readouterr()
  parsed = yaml.safe_load(captured.out)
  assert parsed["role"] == "primary"
  assert parsed["findings"] == []


def test_main_records_multiple_targets_in_review_run_artifacts(
  tmp_config, tmp_path, monkeypatch
):
  """--target 複数指定時に全対象を manifest と rounds に記録する。"""
  monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
  first_target = tmp_path / "first.md"
  second_target = tmp_path / "second.md"
  first_target.write_text("first\n", encoding="utf-8")
  second_target.write_text("second\n", encoding="utf-8")
  review_run_dir = tmp_path / "review-run"
  mock_cls, mock_instance = _make_mock_provider(send_response="findings: []\n")

  with patch("tools.api_providers.run_role.get_provider", return_value=mock_cls):
    exit_code = main(
      [
        "--role", "primary",
        "--target", str(first_target),
        "--target", str(second_target),
        "--phase", "post_write_verification",
        "--criteria", "観点-1",
        "--config", str(tmp_config),
        "--review-run-dir", str(review_run_dir),
      ]
    )

  assert exit_code == 0
  sent_prompt = mock_instance.send_request.call_args.args[0]
  assert str(first_target) in sent_prompt
  assert str(second_target) in sent_prompt
  target_manifest = yaml.safe_load(
    (review_run_dir / "target-manifest.yaml").read_text(encoding="utf-8")
  )
  rounds = yaml.safe_load((review_run_dir / "rounds.yaml").read_text(encoding="utf-8"))
  assert [item["path"] for item in target_manifest["target_files"]] == [
    str(first_target),
    str(second_target),
  ]
  assert [item["path"] for item in rounds["target_files"]] == [
    str(first_target),
    str(second_target),
  ]


def test_main_records_effective_prompt_metadata_in_rounds(
  tmp_target_file, tmp_config, tmp_path, monkeypatch
):
  """effective prompt のパスと sha256 を rounds.yaml に記録する。"""
  monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
  review_run_dir = tmp_path / "review-run"
  effective_prompt = tmp_path / ".reviewcompass" / "effective-prompts" / "stage.prompt.md"
  effective_prompt.parent.mkdir(parents=True)
  effective_prompt.write_text("# Effective Prompt\n\nbody\n", encoding="utf-8")
  mock_cls, _ = _make_mock_provider(send_response="findings: []\n")
  with patch("tools.api_providers.run_role.get_provider", return_value=mock_cls):
    exit_code = main(
      [
        "--role", "primary",
        "--target", str(tmp_target_file),
        "--phase", "post_write_verification",
        "--criteria", "観点-1",
        "--config", str(tmp_config),
        "--review-run-dir", str(review_run_dir),
        "--round-id", "round-1",
        "--effective-prompt-path", str(effective_prompt),
      ]
    )

  assert exit_code == 0
  rounds = yaml.safe_load((review_run_dir / "rounds.yaml").read_text(encoding="utf-8"))
  assert rounds["effective_prompt_path"] == str(effective_prompt)
  assert rounds["effective_prompt_sha256"] == hashlib.sha256(
    effective_prompt.read_bytes()
  ).hexdigest()


def test_main_updates_review_run_artifacts_on_parse_failure(
  tmp_target_file, tmp_config, tmp_path, monkeypatch
):
  """parse 失敗時も review-run に raw と parse_failed 状態を残す。"""
  monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
  review_run_dir = tmp_path / "review-run"
  mock_cls, _ = _make_mock_provider(send_response="findings: [broken\n")
  with patch("tools.api_providers.run_role.get_provider", return_value=mock_cls):
    exit_code = main(
      [
        "--role", "primary",
        "--target", str(tmp_target_file),
        "--phase", "post_write_verification",
        "--criteria", "観点-1",
        "--config", str(tmp_config),
        "--review-run-dir", str(review_run_dir),
        "--round-id", "round-1",
      ]
    )

  assert exit_code != 0
  raw_path = review_run_dir / "raw" / "claude-opus-4-7.round-1.txt"
  assert raw_path.read_text(encoding="utf-8") == "findings: [broken\n"

  rounds = yaml.safe_load((review_run_dir / "rounds.yaml").read_text(encoding="utf-8"))
  summary = yaml.safe_load(
    (review_run_dir / "model-result-summary.yaml").read_text(encoding="utf-8")
  )
  model_result = rounds["model_results"][0]
  assert model_result["parse_status"] == "parse_failed"
  assert model_result["parsed_path"] is None
  assert model_result["follow_up_action"] == "format_pending"
  summary_model = summary["models"][0]
  assert summary_model["parse_status"] == "parse_failed"
  assert summary_model["triage_status"] == "triage_pending"
