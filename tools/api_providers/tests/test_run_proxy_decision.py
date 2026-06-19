import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
  sys.path.insert(0, str(_PROJECT_ROOT))

import yaml

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
