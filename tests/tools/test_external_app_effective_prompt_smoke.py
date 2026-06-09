import hashlib
import json
import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import yaml

from tools.api_providers.run_role import main as run_role_main


ROOT = Path(__file__).resolve().parents[2]
CHECK_WORKFLOW = ROOT / "tools" / "check-workflow-action.py"
FEATURE_ORDER = [
  "foundation",
  "runtime",
  "evaluation",
  "analysis",
  "workflow-management",
  "self-improvement",
  "conformance-evaluation",
]


def _write_specs_for_external_app(cwd):
  complete_five_stage = {
    "drafting": True,
    "triad-review": True,
    "review-wave": True,
    "alignment": True,
    "approval": True,
  }
  pending_implementation = {
    "drafting": False,
    "triad-review": False,
    "review-wave": False,
    "alignment": False,
    "approval": False,
  }
  for feature in FEATURE_ORDER:
    spec_dir = cwd / ".reviewcompass" / "specs" / feature
    spec_dir.mkdir(parents=True, exist_ok=True)
    spec = {
      "feature_name": feature,
      "language": "ja",
      "workflow_state": {
        "intent": {
          "drafting": True,
          "review": True,
          "approval": True,
        },
        "feature-partitioning": {
          "candidate-proposal": True,
          "approval": True,
        },
        "requirements": dict(complete_five_stage),
        "design": dict(complete_five_stage),
        "tasks": dict(complete_five_stage),
        "implementation": dict(pending_implementation),
      },
      "recheck": {
        "upstream_change_pending": False,
        "impacted_downstream_phases": [],
      },
    }
    (spec_dir / "spec.json").write_text(
      json.dumps(spec, ensure_ascii=False, indent=2),
      encoding="utf-8",
    )


def _write_api_config(cwd):
  config_path = cwd / "api-settings.yaml"
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
""",
    encoding="utf-8",
  )
  return config_path


def test_external_app_next_effective_prompt_feeds_review_run_rounds(tmp_path, monkeypatch):
  """外部アプリ root で next が作った effective prompt を review-run に記録できる。"""
  app_root = tmp_path / "external-app"
  app_root.mkdir()
  target = app_root / "app.md"
  target.write_text("small external app\n", encoding="utf-8")
  _write_specs_for_external_app(app_root)
  config_path = _write_api_config(app_root)

  result = subprocess.run(
    [sys.executable, str(CHECK_WORKFLOW), "next", "--json"],
    cwd=str(app_root),
    capture_output=True,
    text=True,
    timeout=10,
  )

  assert result.returncode == 0, result.stderr
  next_payload = json.loads(result.stdout)
  effective_prompt = next_payload["next_action"]["effective_prompt"]
  effective_prompt_path = app_root / effective_prompt["effective_prompt_path"]
  assert effective_prompt_path.is_file()
  assert effective_prompt["effective_prompt_sha256"] == hashlib.sha256(
    effective_prompt_path.read_bytes()
  ).hexdigest()

  monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
  provider_instance = MagicMock()
  provider_instance.send_request.return_value = "findings: []\n"
  provider_cls = MagicMock(return_value=provider_instance)
  review_run_dir = app_root / ".reviewcompass" / "review-runs" / "smoke-run"
  with patch("tools.api_providers.run_role.get_provider", return_value=provider_cls):
    exit_code = run_role_main(
      [
        "--role", "primary",
        "--target", str(target),
        "--phase", "implementation",
        "--criteria", "external_app_smoke",
        "--config", str(config_path),
        "--review-run-dir", str(review_run_dir),
        "--round-id", "round-1",
        "--effective-prompt-path", str(effective_prompt_path),
        "--effective-prompt-sha256", effective_prompt["effective_prompt_sha256"],
      ]
    )

  assert exit_code == 0
  rounds = yaml.safe_load((review_run_dir / "rounds.yaml").read_text(encoding="utf-8"))
  assert rounds["effective_prompt_path"] == str(effective_prompt_path)
  assert rounds["effective_prompt_sha256"] == effective_prompt["effective_prompt_sha256"]
