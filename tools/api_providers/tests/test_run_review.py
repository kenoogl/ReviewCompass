# tools/api_providers/tests/test_run_review.py
# 複数モデル review-run orchestrator の TDD テスト。

import sys
import hashlib
from pathlib import Path
from unittest.mock import MagicMock, patch

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
  sys.path.insert(0, str(_PROJECT_ROOT))

import yaml

from tools.api_providers.run_review import main


def _make_config(tmp_path):
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
    model: claude-sonnet-4-6
  adversarial:
    path: api
    provider: openai-api
    model: gpt-5.4
  judgment:
    path: api
    provider: gemini-api
    model: gemini-3.1-pro-preview
variants:
  post_write_verification_google:
    context: post_write_verification
    variant_type: single_role
    required_roles: [primary]
    primary:
      path: api
      provider: gemini-api
      model: gemini-3.5-flash
""",
    encoding="utf-8",
  )
  return config_path


def _make_provider_factory(responses):
  """provider 名に応じたモック provider class を返す factory。"""
  def factory(provider_name):
    mock_instance = MagicMock()
    mock_instance.send_request.return_value = responses[provider_name]
    return MagicMock(return_value=mock_instance)

  return factory


def test_run_review_executes_three_roles_and_creates_summary_and_triage(tmp_path, monkeypatch, capsys):
  """3 役を同じ review-run に集約し、summary と triage 下書きを生成する。"""
  monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
  monkeypatch.setenv("OPENAI_API_KEY", "test-key")
  monkeypatch.setenv("GEMINI_API_KEY", "test-key")
  target = tmp_path / "target.md"
  target.write_text("レビュー対象\n", encoding="utf-8")
  config_path = _make_config(tmp_path)
  review_run_dir = tmp_path / "review-run"
  responses = {
    "anthropic-api": """
findings:
  - severity: ERROR
    target_location: target.md
    description: 契約違反の可能性
    rationale: 仕様に影響する
""",
    "openai-api": "findings: []\n",
    "gemini-api": """
findings:
  - severity: WARN
    target_location: target.md
    description: 説明不足
    rationale: 読み手に補足が必要
""",
  }

  with patch(
    "tools.api_providers.run_review.get_provider",
    side_effect=_make_provider_factory(responses),
  ):
    exit_code = main(
      [
        "--variant", "default",
        "--target", str(target),
        "--phase", "post_write_verification",
        "--criteria", "観点-1",
        "--review-run-dir", str(review_run_dir),
        "--round-id", "round-1",
        "--config", str(config_path),
      ]
    )

  assert exit_code == 0
  output = capsys.readouterr().out
  assert "claude-sonnet-4-6" in output
  assert "gpt-5.4" in output
  assert "gemini-3.1-pro-preview" in output
  assert "triage_pending" in output
  assert "variant: default" in output
  assert "| primary | api | anthropic-api | claude-sonnet-4-6 |" in output
  assert "| adversarial | api | openai-api | gpt-5.4 |" in output
  assert "| judgment | api | gemini-api | gemini-3.1-pro-preview |" in output
  assert "proxy_model" in output
  assert "利用者提示ゲート" in output

  rounds = yaml.safe_load((review_run_dir / "rounds.yaml").read_text(encoding="utf-8"))
  summary = yaml.safe_load(
    (review_run_dir / "model-result-summary.yaml").read_text(encoding="utf-8")
  )
  triage = yaml.safe_load((review_run_dir / "triage.yaml").read_text(encoding="utf-8"))

  assert [item["role"] for item in rounds["model_results"]] == [
    "primary",
    "adversarial",
    "judgment",
  ]
  assert len(summary["models"]) == 3
  assert (review_run_dir / "review_summary.md").is_file()
  assert summary["models"][1]["triage_status"] == "no_findings"
  assert summary["models"][0]["triage_status"] == "triage_pending"

  assert triage["triage_status"] == "draft"
  assert len(triage["items"]) == 2
  assert {item["source_model"] for item in triage["items"]} == {
    "claude-sonnet-4-6",
    "gemini-3.1-pro-preview",
  }
  assert all(item["decision_status"] == "human_required" for item in triage["items"])
  assert all(item["final_label"] is None for item in triage["items"])
  review_summary = (review_run_dir / "review_summary.md").read_text(encoding="utf-8")
  assert "variant: default" in review_summary
  assert "proxy_model" in review_summary
  assert "利用者提示ゲート" in review_summary


def test_run_review_continues_after_one_role_parse_failure(tmp_path, monkeypatch):
  """1 役が parse 失敗しても raw を残し、他役の実行と summary 生成を続ける。"""
  monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
  monkeypatch.setenv("OPENAI_API_KEY", "test-key")
  monkeypatch.setenv("GEMINI_API_KEY", "test-key")
  target = tmp_path / "target.md"
  target.write_text("レビュー対象\n", encoding="utf-8")
  config_path = _make_config(tmp_path)
  review_run_dir = tmp_path / "review-run"
  responses = {
    "anthropic-api": "findings: [broken\n",
    "openai-api": "findings: []\n",
    "gemini-api": "findings: []\n",
  }

  with patch(
    "tools.api_providers.run_review.get_provider",
    side_effect=_make_provider_factory(responses),
  ):
    exit_code = main(
      [
        "--variant", "default",
        "--target", str(target),
        "--phase", "post_write_verification",
        "--criteria", "観点-1",
        "--review-run-dir", str(review_run_dir),
        "--round-id", "round-1",
        "--config", str(config_path),
      ]
    )

  assert exit_code == 1
  summary = yaml.safe_load(
    (review_run_dir / "model-result-summary.yaml").read_text(encoding="utf-8")
  )
  statuses = {item["model_id"]: item["parse_status"] for item in summary["models"]}
  assert statuses["claude-sonnet-4-6"] == "parse_failed"
  assert statuses["gpt-5.4"] == "parsed"
  assert statuses["gemini-3.1-pro-preview"] == "parsed"
  assert (review_run_dir / "raw" / "claude-sonnet-4-6.round-1.txt").is_file()
  triage = yaml.safe_load((review_run_dir / "triage.yaml").read_text(encoding="utf-8"))
  assert triage["triage_status"] == "draft"


def test_run_review_uses_post_write_default_variant_when_phase_is_post_write(tmp_path, monkeypatch, capsys):
  """post_write_verification は未指定 variant でも CLI default に落とさない。"""
  monkeypatch.setenv("GEMINI_API_KEY", "test-key")
  target = tmp_path / "target.md"
  target.write_text("レビュー対象\n", encoding="utf-8")
  config_path = _make_config(tmp_path)
  review_run_dir = tmp_path / "review-run"
  responses = {
    "gemini-api": "findings: []\n",
  }

  with patch(
    "tools.api_providers.run_review.get_provider",
    side_effect=_make_provider_factory(responses),
  ):
    exit_code = main(
      [
        "--target", str(target),
        "--phase", "post_write_verification",
        "--criteria", "観点-1",
        "--review-run-dir", str(review_run_dir),
        "--round-id", "round-1",
        "--config", str(config_path),
      ]
    )

  assert exit_code == 0
  output = capsys.readouterr().out
  assert "variant: post_write_verification_google" in output
  assert "gemini-3.5-flash" in output
  assert "claude-code-cli" not in output

  rounds = yaml.safe_load((review_run_dir / "rounds.yaml").read_text(encoding="utf-8"))
  assert [item["role"] for item in rounds["model_results"]] == ["primary"]


def test_run_review_records_multiple_targets_in_review_run_artifacts(tmp_path, monkeypatch):
  """run_review の複数 --target が target-manifest と rounds に残る。"""
  monkeypatch.setenv("GEMINI_API_KEY", "test-key")
  first_target = tmp_path / "first.md"
  second_target = tmp_path / "second.md"
  first_target.write_text("first\n", encoding="utf-8")
  second_target.write_text("second\n", encoding="utf-8")
  config_path = _make_config(tmp_path)
  review_run_dir = tmp_path / "review-run"
  responses = {"gemini-api": "findings: []\n"}

  with patch(
    "tools.api_providers.run_review.get_provider",
    side_effect=_make_provider_factory(responses),
  ):
    exit_code = main(
      [
        "--variant", "post_write_verification_google",
        "--target", str(first_target),
        "--target", str(second_target),
        "--phase", "post_write_verification",
        "--criteria", "観点-1",
        "--review-run-dir", str(review_run_dir),
        "--config", str(config_path),
      ]
    )

  assert exit_code == 0
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


def test_run_review_respects_single_role_variant_required_roles(tmp_path, monkeypatch, capsys):
  """single_role variant は required_roles に従い primary だけを実行する。"""
  monkeypatch.setenv("GEMINI_API_KEY", "test-key")
  target = tmp_path / "target.md"
  target.write_text("レビュー対象\n", encoding="utf-8")
  config_path = _make_config(tmp_path)
  review_run_dir = tmp_path / "review-run"
  responses = {
    "gemini-api": """
findings:
  - severity: INFO
    target_location: target.md
    description: 軽微な確認事項
    rationale: 補足確認
""",
  }

  with patch(
    "tools.api_providers.run_review.get_provider",
    side_effect=_make_provider_factory(responses),
  ):
    exit_code = main(
      [
        "--variant", "post_write_verification_google",
        "--target", str(target),
        "--phase", "post_write_verification",
        "--criteria", "観点-1",
        "--review-run-dir", str(review_run_dir),
        "--round-id", "round-1",
        "--config", str(config_path),
      ]
    )

  assert exit_code == 0
  output = capsys.readouterr().out
  assert "| primary | api | gemini-api | gemini-3.5-flash |" in output
  assert "| adversarial |" not in output
  assert "| judgment |" not in output

  triage = yaml.safe_load((review_run_dir / "triage.yaml").read_text(encoding="utf-8"))
  assert len(triage["items"]) == 1
  assert triage["items"][0]["source_model"] == "gemini-3.5-flash"


def test_run_review_records_effective_prompt_metadata(tmp_path, monkeypatch, capsys):
  """run_review でも effective prompt のパスと sha256 を rounds.yaml に記録する。"""
  monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
  monkeypatch.setenv("OPENAI_API_KEY", "test-key")
  monkeypatch.setenv("GEMINI_API_KEY", "test-key")
  target = tmp_path / "target.md"
  target.write_text("レビュー対象\n", encoding="utf-8")
  config_path = _make_config(tmp_path)
  review_run_dir = tmp_path / "review-run"
  effective_prompt = tmp_path / ".reviewcompass" / "effective-prompts" / "stage.prompt.md"
  effective_prompt.parent.mkdir(parents=True)
  effective_prompt.write_text("# Effective Prompt\n\nbody\n", encoding="utf-8")
  responses = {
    "anthropic-api": "findings: []\n",
    "openai-api": "findings: []\n",
    "gemini-api": "findings: []\n",
  }

  with patch(
    "tools.api_providers.run_review.get_provider",
    side_effect=_make_provider_factory(responses),
  ):
    exit_code = main(
      [
        "--target", str(target),
        "--phase", "implementation",
        "--criteria", "criteria",
        "--review-run-dir", str(review_run_dir),
        "--round-id", "round-1",
        "--config", str(config_path),
        "--effective-prompt-path", str(effective_prompt),
      ]
    )

  assert exit_code == 0
  capsys.readouterr()
  rounds = yaml.safe_load((review_run_dir / "rounds.yaml").read_text(encoding="utf-8"))
  assert rounds["effective_prompt_path"] == str(effective_prompt)
  assert len(rounds["effective_prompt_sha256"]) == 64


def test_run_review_uses_criteria_file_and_records_prompt_artifact(
  tmp_path,
  monkeypatch,
):
  """criteria-file の本文を使い、実送信プロンプトを review-run に保存する。"""
  monkeypatch.setenv("GEMINI_API_KEY", "test-key")
  target = tmp_path / "target.md"
  target.write_text("契約本文\n", encoding="utf-8")
  criteria_file = tmp_path / "review-target.md"
  criteria_file.write_text(
    "# Review Target\n\n"
    "commit instruction preflight の契約整合を確認する。\n"
    "git add より前に preflight が走ることを確認する。\n",
    encoding="utf-8",
  )
  config_path = _make_config(tmp_path)
  review_run_dir = tmp_path / "review-run"
  responses = {"gemini-api": "findings: []\n"}

  with patch(
    "tools.api_providers.run_review.get_provider",
    side_effect=_make_provider_factory(responses),
  ):
    exit_code = main(
      [
        "--variant", "post_write_verification_google",
        "--target", str(target),
        "--phase", "post_write_verification",
        "--criteria-file", str(criteria_file),
        "--review-run-dir", str(review_run_dir),
        "--config", str(config_path),
      ]
    )

  assert exit_code == 0
  rounds = yaml.safe_load((review_run_dir / "rounds.yaml").read_text(encoding="utf-8"))
  model_result = rounds["model_results"][0]
  prompt_path = review_run_dir / model_result["prompt_path"]
  assert rounds["criteria"] == criteria_file.read_text(encoding="utf-8")
  assert rounds["criteria_source_path"] == str(criteria_file)
  assert rounds["criteria_source_sha256"] == hashlib.sha256(
    criteria_file.read_bytes()
  ).hexdigest()
  assert prompt_path.is_file()
  assert "git add より前" in prompt_path.read_text(encoding="utf-8")
  assert model_result["prompt_sha256"] == hashlib.sha256(
    prompt_path.read_bytes()
  ).hexdigest()
