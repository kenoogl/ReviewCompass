import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import MagicMock, patch

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
  sys.path.insert(0, str(_PROJECT_ROOT))

import yaml

from tools.api_providers.external_api_approval import prompt_material_findings
from tools.api_providers.run_proxy_decision import main


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
    provider: openai-api
    model: gpt-5.4
variants:
  proxy_model_openai_gpt_55:
    context: proxy_model
    variant_type: single_role
    required_roles: [primary]
    primary:
      path: api
      provider: openai-api
      model: gpt-5.5
      timeout_seconds: 300
""",
    encoding="utf-8",
  )
  return config_path


def _write_external_approval(
  tmp_path,
  prompt,
  *,
  provider="openai-api",
  model="gpt-5.5",
  expires_delta=timedelta(hours=1),
  allowed_prompt_glob=None,
):
  approval_path = tmp_path / "external-api-approval.yaml"
  expires_at = (datetime.now(timezone.utc) + expires_delta).isoformat()
  approval_path.write_text(
    f"""
schema_version: external-api-approval-v1
approved_action: external_api_proxy_model
approved_by: user
provider: {provider}
model: {model}
allowed_prompt_globs:
  - {allowed_prompt_glob or str(prompt)}
purpose:
  - proxy_model_decision
material_policy:
  allow_reviewcompass_internal_specs: true
  require_secret_scan: true
  forbid_credentials: true
  forbid_personal_identifiers: true
  forbid_third_party_confidential: true
expires_at: {expires_at}
consumed: false
""",
    encoding="utf-8",
  )
  return approval_path


def test_run_proxy_decision_records_raw_parsed_and_metadata(tmp_path, monkeypatch, capsys):
  monkeypatch.setenv("OPENAI_API_KEY", "test-key")
  prompt = tmp_path / "proxy-decision-prompt.md"
  prompt.write_text("# prompt\n", encoding="utf-8")
  review_run_dir = tmp_path / "review-run"
  config_path = _make_config(tmp_path)
  response = """
proxy_model_id: gpt-5.5
decision_prompt_path: proxy-decision-prompt.md
raw_response_path: proxy-decision-response.yaml
decisions:
  - finding_id: F1
    final_label: should-fix
    rationale: 補強すべきだが blocking ではない
    rejected_options:
      must-fix: selected ではない
      should-fix: selected
      leave-as-is: 境界補強の価値がある
"""

  provider_instance = MagicMock()
  provider_instance.send_messages.return_value = response
  provider_class = MagicMock(return_value=provider_instance)

  with patch("tools.api_providers.run_proxy_decision.get_provider", return_value=provider_class):
    exit_code = main(
      [
        "--variant", "proxy_model_openai_gpt_55",
        "--prompt-file", str(prompt),
        "--review-run-dir", str(review_run_dir),
        "--config", str(config_path),
      ]
    )

  assert exit_code == 0
  output = capsys.readouterr().out
  assert output.startswith("[OK] run_proxy_decision ")
  assert "provider=openai-api" in output
  assert "model=gpt-5.5" in output

  raw = review_run_dir / "proxy-decision-response.yaml"
  parsed_path = review_run_dir / "proxy-decision-decisions.yaml"
  metadata_path = review_run_dir / "proxy-decision-metadata.yaml"
  assert raw.read_text(encoding="utf-8") == response

  parsed = yaml.safe_load(parsed_path.read_text(encoding="utf-8"))
  assert parsed["proxy_model_id"] == "gpt-5.5"
  assert parsed["decisions"][0]["finding_id"] == "F1"

  metadata = yaml.safe_load(metadata_path.read_text(encoding="utf-8"))
  assert metadata["variant"] == "proxy_model_openai_gpt_55"
  assert metadata["provider"] == "openai-api"
  assert metadata["model"] == "gpt-5.5"
  assert metadata["prompt_path"] == str(prompt)
  assert metadata["raw_response_path"] == "proxy-decision-response.yaml"
  assert metadata["parsed_decisions_path"] == "proxy-decision-decisions.yaml"


def test_run_proxy_decision_accepts_external_api_approval_record(
  tmp_path,
  monkeypatch,
):
  monkeypatch.setenv("OPENAI_API_KEY", "test-key")
  prompt = tmp_path / "proxy-decision-prompt.md"
  prompt.write_text("# prompt\n", encoding="utf-8")
  review_run_dir = tmp_path / "review-run"
  config_path = _make_config(tmp_path)
  approval_path = _write_external_approval(tmp_path, prompt)
  response = """
proxy_model_id: gpt-5.5
decisions: []
"""

  provider_instance = MagicMock()
  provider_instance.send_messages.return_value = response
  provider_class = MagicMock(return_value=provider_instance)

  with patch("tools.api_providers.run_proxy_decision.get_provider", return_value=provider_class):
    exit_code = main(
      [
        "--variant", "proxy_model_openai_gpt_55",
        "--prompt-file", str(prompt),
        "--review-run-dir", str(review_run_dir),
        "--config", str(config_path),
        "--external-approval-record", str(approval_path),
      ]
    )

  assert exit_code == 0
  metadata = yaml.safe_load(
    (review_run_dir / "proxy-decision-metadata.yaml").read_text(encoding="utf-8")
  )
  assert metadata["external_approval_record_path"] == str(approval_path)


def test_run_proxy_decision_accepts_policy_mapping_response(
  tmp_path,
  monkeypatch,
):
  monkeypatch.setenv("OPENAI_API_KEY", "test-key")
  prompt = tmp_path / "proxy-decision-prompt.md"
  prompt.write_text("# prompt\n", encoding="utf-8")
  review_run_dir = tmp_path / "review-run"
  config_path = _make_config(tmp_path)
  response = """
proxy_model_id: gpt-5.5
decision_scope: c1_fix_policy
selected_policy_category: local_fix_with_modifications
required_design_changes:
  - Rewrite Requirement 12 placement wording.
"""

  provider_instance = MagicMock()
  provider_instance.send_messages.return_value = response
  provider_class = MagicMock(return_value=provider_instance)

  with patch("tools.api_providers.run_proxy_decision.get_provider", return_value=provider_class):
    exit_code = main(
      [
        "--variant", "proxy_model_openai_gpt_55",
        "--prompt-file", str(prompt),
        "--review-run-dir", str(review_run_dir),
        "--config", str(config_path),
      ]
    )

  assert exit_code == 0
  parsed = yaml.safe_load(
    (review_run_dir / "proxy-decision-decisions.yaml").read_text(encoding="utf-8")
  )
  assert parsed["decision_scope"] == "c1_fix_policy"
  assert parsed["selected_policy_category"] == "local_fix_with_modifications"


def test_run_proxy_decision_rejects_external_api_approval_model_mismatch(
  tmp_path,
  monkeypatch,
):
  monkeypatch.setenv("OPENAI_API_KEY", "test-key")
  prompt = tmp_path / "proxy-decision-prompt.md"
  prompt.write_text("# prompt\n", encoding="utf-8")
  config_path = _make_config(tmp_path)
  approval_path = _write_external_approval(tmp_path, prompt, model="gpt-5.4")

  with patch("tools.api_providers.run_proxy_decision.get_provider") as get_provider:
    exit_code = main(
      [
        "--variant", "proxy_model_openai_gpt_55",
        "--prompt-file", str(prompt),
        "--review-run-dir", str(tmp_path / "review-run"),
        "--config", str(config_path),
        "--external-approval-record", str(approval_path),
      ]
    )

  assert exit_code == 1
  get_provider.assert_not_called()


def test_run_proxy_decision_rejects_external_api_approval_expired(
  tmp_path,
  monkeypatch,
):
  monkeypatch.setenv("OPENAI_API_KEY", "test-key")
  prompt = tmp_path / "proxy-decision-prompt.md"
  prompt.write_text("# prompt\n", encoding="utf-8")
  config_path = _make_config(tmp_path)
  approval_path = _write_external_approval(
    tmp_path,
    prompt,
    expires_delta=timedelta(seconds=-1),
  )

  with patch("tools.api_providers.run_proxy_decision.get_provider") as get_provider:
    exit_code = main(
      [
        "--variant", "proxy_model_openai_gpt_55",
        "--prompt-file", str(prompt),
        "--review-run-dir", str(tmp_path / "review-run"),
        "--config", str(config_path),
        "--external-approval-record", str(approval_path),
      ]
    )

  assert exit_code == 1
  get_provider.assert_not_called()


def test_run_proxy_decision_rejects_external_api_approval_secret_in_prompt(
  tmp_path,
  monkeypatch,
):
  monkeypatch.setenv("OPENAI_API_KEY", "test-key")
  prompt = tmp_path / "proxy-decision-prompt.md"
  prompt.write_text("OPENAI_API_KEY=sk-test-secret\n", encoding="utf-8")
  config_path = _make_config(tmp_path)
  approval_path = _write_external_approval(tmp_path, prompt)

  with patch("tools.api_providers.run_proxy_decision.get_provider") as get_provider:
    exit_code = main(
      [
        "--variant", "proxy_model_openai_gpt_55",
        "--prompt-file", str(prompt),
        "--review-run-dir", str(tmp_path / "review-run"),
        "--config", str(config_path),
        "--external-approval-record", str(approval_path),
      ]
    )

  assert exit_code == 1
  get_provider.assert_not_called()


def test_external_api_approval_material_scan_allows_date_paths():
  prompt = (
    ".reviewcompass/specs/workflow-management/reviews/"
    "2026-06-20-workflow-management-design-vertical-redo/"
    "proxy-decision-prompt.md\n"
  )

  assert prompt_material_findings(prompt) == []


def test_external_api_approval_material_scan_rejects_personal_identifiers():
  prompt = "Contact: reviewer@example.com / +1 415 555 0101\n"

  assert "prompt contains possible personal identifier" in prompt_material_findings(
    prompt
  )


def test_run_proxy_decision_rejects_non_single_role_variant(tmp_path, monkeypatch):
  monkeypatch.setenv("OPENAI_API_KEY", "test-key")
  prompt = tmp_path / "proxy-decision-prompt.md"
  prompt.write_text("# prompt\n", encoding="utf-8")
  config_path = tmp_path / "api-settings.yaml"
  config_path.write_text(
    """
connection: {}
default:
  variant_type: triad
  required_roles: [primary, adversarial, judgment]
  primary: {path: api, provider: openai-api, model: gpt-5.5}
  adversarial: {path: api, provider: openai-api, model: gpt-5.4}
  judgment: {path: api, provider: gemini-api, model: gemini-3.1-pro-preview}
""",
    encoding="utf-8",
  )

  exit_code = main(
    [
      "--prompt-file", str(prompt),
      "--review-run-dir", str(tmp_path / "review-run"),
      "--config", str(config_path),
    ]
  )

  assert exit_code == 1


def test_run_proxy_decision_preserves_raw_response_on_parse_failure(
  tmp_path,
  monkeypatch,
):
  monkeypatch.setenv("OPENAI_API_KEY", "test-key")
  prompt = tmp_path / "proxy-decision-prompt.md"
  prompt.write_text("# prompt\n", encoding="utf-8")
  review_run_dir = tmp_path / "review-run"
  config_path = _make_config(tmp_path)
  response = "proxy_model_id: gpt-5.5\nrationale: invalid: yaml\n"

  provider_instance = MagicMock()
  provider_instance.send_messages.return_value = response
  provider_class = MagicMock(return_value=provider_instance)

  with patch("tools.api_providers.run_proxy_decision.get_provider", return_value=provider_class):
    exit_code = main(
      [
        "--variant", "proxy_model_openai_gpt_55",
        "--prompt-file", str(prompt),
        "--review-run-dir", str(review_run_dir),
        "--config", str(config_path),
      ]
    )

  assert exit_code == 1
  assert (review_run_dir / "proxy-decision-response.yaml").read_text(
    encoding="utf-8"
  ) == response
  metadata = yaml.safe_load(
    (review_run_dir / "proxy-decision-metadata.yaml").read_text(encoding="utf-8")
  )
  assert metadata["parse_status"] == "parse_failed"
