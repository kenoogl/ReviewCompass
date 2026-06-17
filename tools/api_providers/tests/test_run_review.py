# tools/api_providers/tests/test_run_review.py
# 複数モデル review-run orchestrator の TDD テスト。

import sys
import json
import hashlib
from datetime import datetime, timedelta, timezone
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


def _write_external_api_approval(
  tmp_path,
  target,
  variant="post_write_verification_google",
  criteria="観点-1",
  review_run_dir=None,
  providers=None,
  models=None,
):
  review_run_dir = review_run_dir or tmp_path / "review-run"
  providers = providers or ["gemini-api"]
  models = models or ["gemini-3.5-flash"]
  approval_dir = tmp_path / ".reviewcompass" / "runtime" / "approvals"
  approval_dir.mkdir(parents=True, exist_ok=True)
  now = datetime.now(timezone.utc)
  target_sha = hashlib.sha256(target.read_bytes()).hexdigest()
  challenge_path = approval_dir / "external-api-approval-challenge.json"
  approval_path = approval_dir / "external-api-approval.json"
  common = {
    "schema_version": 1,
    "approved_action": "external_api_review",
    "approved_by": "user",
    "nonce": "0" * 48,
    "created_at": now.isoformat(),
    "expires_at": (now + timedelta(seconds=600)).isoformat(),
    "ttl_seconds": 600,
    "target_files": [str(target)],
    "target_sha256": {str(target): target_sha},
    "phase": "post_write_verification",
    "criteria": criteria,
    "variant": variant,
    "review_run_dir": str(review_run_dir),
    "providers": providers,
    "models": models,
    "consumed": False,
    "invalidated": False,
  }
  challenge_path.write_text(
    json.dumps({
      **common,
      "challenge_type": "external_api_approval",
    }, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8",
  )
  approval_path.write_text(
    json.dumps({
      **common,
      "source_text_redacted": "外部 API 送信を承認",
      "attestation_type": "external_api_review_nonce_binding",
      "guarantee_scope": "target_provider_phase_criteria_binding",
    }, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8",
  )
  return approval_path


def test_run_review_blocks_post_write_api_without_external_approval(tmp_path, monkeypatch, capsys):
  """post_write_verification の API 送信は external API 承認 record なしで止める。"""
  monkeypatch.setenv("GEMINI_API_KEY", "test-key")
  target = tmp_path / "target.md"
  target.write_text("レビュー対象\n", encoding="utf-8")
  config_path = _make_config(tmp_path)
  review_run_dir = tmp_path / "review-run"

  provider_factory = MagicMock(side_effect=_make_provider_factory({"gemini-api": "findings: []\n"}))
  with patch("tools.api_providers.run_review.get_provider", side_effect=provider_factory):
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

  assert exit_code == 1
  captured = capsys.readouterr()
  assert "external-api-approval" in captured.err
  provider_factory.assert_not_called()


def test_run_review_allows_post_write_api_with_matching_external_approval(tmp_path, monkeypatch, capsys):
  """実行引数と一致する external API 承認 record があれば API 送信へ進む。"""
  monkeypatch.setenv("GEMINI_API_KEY", "test-key")
  target = tmp_path / "target.md"
  target.write_text("レビュー対象\n", encoding="utf-8")
  config_path = _make_config(tmp_path)
  review_run_dir = tmp_path / "review-run"
  approval_path = _write_external_api_approval(
    tmp_path,
    target,
    review_run_dir=review_run_dir,
  )

  with patch(
    "tools.api_providers.run_review.get_provider",
    side_effect=_make_provider_factory({"gemini-api": "findings: []\n"}),
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
        "--external-api-approval-record", str(approval_path),
      ]
    )

  assert exit_code == 0
  output = capsys.readouterr().out
  assert "variant: post_write_verification_google" in output


def test_run_review_accepts_multiple_targets_with_matching_external_approval(tmp_path, monkeypatch, capsys):
  """post_write_verification は複数 target を 1 review-run に束ねて検証できる。"""
  monkeypatch.setenv("GEMINI_API_KEY", "test-key")
  target_a = tmp_path / "a.md"
  target_b = tmp_path / "b.md"
  target_a.write_text("A\n", encoding="utf-8")
  target_b.write_text("B\n", encoding="utf-8")
  config_path = _make_config(tmp_path)
  review_run_dir = tmp_path / "review-run"
  approval_dir = tmp_path / ".reviewcompass" / "runtime" / "approvals"
  approval_dir.mkdir(parents=True, exist_ok=True)
  now = datetime.now(timezone.utc)
  common = {
    "schema_version": 1,
    "approved_action": "external_api_review",
    "approved_by": "user",
    "nonce": "1" * 48,
    "created_at": now.isoformat(),
    "expires_at": (now + timedelta(seconds=600)).isoformat(),
    "ttl_seconds": 600,
    "target_files": [str(target_a), str(target_b)],
    "target_sha256": {
      str(target_a): hashlib.sha256(target_a.read_bytes()).hexdigest(),
      str(target_b): hashlib.sha256(target_b.read_bytes()).hexdigest(),
    },
    "phase": "post_write_verification",
    "criteria": "観点-1",
    "variant": "post_write_verification_google",
    "review_run_dir": str(review_run_dir),
    "providers": ["gemini-api"],
    "models": ["gemini-3.5-flash"],
    "consumed": False,
    "invalidated": False,
  }
  challenge_path = approval_dir / "external-api-approval-challenge.json"
  approval_path = approval_dir / "external-api-approval.json"
  challenge_path.write_text(
    json.dumps({**common, "challenge_type": "external_api_approval"}, ensure_ascii=False),
    encoding="utf-8",
  )
  approval_path.write_text(
    json.dumps({
      **common,
      "source_text_redacted": "承認",
      "attestation_type": "external_api_review_nonce_binding",
      "guarantee_scope": "target_provider_phase_criteria_binding",
    }, ensure_ascii=False),
    encoding="utf-8",
  )

  with patch(
    "tools.api_providers.run_review.get_provider",
    side_effect=_make_provider_factory({"gemini-api": "findings: []\n"}),
  ):
    exit_code = main(
      [
        "--variant", "post_write_verification_google",
        "--target", str(target_a),
        "--target", str(target_b),
        "--phase", "post_write_verification",
        "--criteria", "観点-1",
        "--review-run-dir", str(review_run_dir),
        "--round-id", "round-1",
        "--config", str(config_path),
        "--external-api-approval-record", str(approval_path),
      ]
    )

  assert exit_code == 0
  output = capsys.readouterr().out
  assert "variant: post_write_verification_google" in output
  rounds = yaml.safe_load((review_run_dir / "rounds.yaml").read_text(encoding="utf-8"))
  assert [item["path"] for item in rounds["target_files"]] == [
    str(target_a),
    str(target_b),
  ]


def test_run_review_executes_three_roles_and_creates_summary_and_triage(tmp_path, monkeypatch, capsys):
  """3 役を同じ review-run に集約し、summary と triage 下書きを生成する。"""
  monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
  monkeypatch.setenv("OPENAI_API_KEY", "test-key")
  monkeypatch.setenv("GEMINI_API_KEY", "test-key")
  target = tmp_path / "target.md"
  target.write_text("レビュー対象\n", encoding="utf-8")
  config_path = _make_config(tmp_path)
  review_run_dir = tmp_path / "review-run"
  approval_path = _write_external_api_approval(
    tmp_path,
    target,
    variant="default",
    review_run_dir=review_run_dir,
    providers=["anthropic-api", "openai-api", "gemini-api"],
    models=["claude-sonnet-4-6", "gpt-5.4", "gemini-3.1-pro-preview"],
  )
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
        "--external-api-approval-record", str(approval_path),
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
  approval_path = _write_external_api_approval(
    tmp_path,
    target,
    variant="default",
    review_run_dir=review_run_dir,
    providers=["anthropic-api", "openai-api", "gemini-api"],
    models=["claude-sonnet-4-6", "gpt-5.4", "gemini-3.1-pro-preview"],
  )
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
        "--external-api-approval-record", str(approval_path),
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
  approval_path = _write_external_api_approval(
    tmp_path,
    target,
    review_run_dir=review_run_dir,
  )
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
        "--external-api-approval-record", str(approval_path),
      ]
    )

  assert exit_code == 0
  output = capsys.readouterr().out
  assert "variant: post_write_verification_google" in output
  assert "gemini-3.5-flash" in output
  assert "claude-code-cli" not in output

  rounds = yaml.safe_load((review_run_dir / "rounds.yaml").read_text(encoding="utf-8"))
  assert [item["role"] for item in rounds["model_results"]] == ["primary"]


def test_run_review_respects_single_role_variant_required_roles(tmp_path, monkeypatch, capsys):
  """single_role variant は required_roles に従い primary だけを実行する。"""
  monkeypatch.setenv("GEMINI_API_KEY", "test-key")
  target = tmp_path / "target.md"
  target.write_text("レビュー対象\n", encoding="utf-8")
  config_path = _make_config(tmp_path)
  review_run_dir = tmp_path / "review-run"
  approval_path = _write_external_api_approval(
    tmp_path,
    target,
    review_run_dir=review_run_dir,
  )
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
        "--external-api-approval-record", str(approval_path),
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
