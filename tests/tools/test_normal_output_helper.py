"""Normal output formatter boundary red tests."""

from tools import normal_output


def test_normal_output_formatter_declares_minimal_contract():
  """Shared formatter exposes the local verdict and mode vocabulary."""
  assert normal_output.NORMAL_OUTPUT_VERDICTS == [
    "OK",
    "WARN",
    "DEVIATION",
  ]
  assert normal_output.NORMAL_OUTPUT_MODES == [
    "human",
    "json",
    "verbose",
  ]


def test_normal_output_human_ok_keeps_one_short_line():
  """OK human output is a short status line without details."""
  record = {
    "verdict": "OK",
    "action": "make-post-write-manifest",
    "summary_fields": {
      "path": ".reviewcompass/post-write-verification/post-write-2026-07-01-003.yaml",
      "targets": 2,
    },
    "details": {
      "target_files": ["TODO_NEXT_SESSION.md", "tools/normal_output.py"],
      "sha256": {"TODO_NEXT_SESSION.md": "abc"},
    },
  }

  output = normal_output.render_human_output(record)

  assert output == (
    "[OK] make-post-write-manifest "
    "path=.reviewcompass/post-write-verification/post-write-2026-07-01-003.yaml "
    "targets=2\n"
  )
  assert "target_files" not in output
  assert "sha256" not in output


def test_normal_output_warning_and_deviation_keep_reasons_and_next_action():
  """WARN / DEVIATION output keeps concise stop reasons and next action."""
  record = {
    "verdict": "DEVIATION",
    "action": "commit-preflight",
    "reasons": [
      "post-write verification is pending",
      "staged file is outside allowed scope",
      "approval record is stale",
      "extra diagnostic kept for json only",
    ],
    "next_action": "run post-write verification",
  }

  output = normal_output.render_human_output(record)

  assert output.splitlines() == [
    "[DEVIATION] commit-preflight",
    "reason: post-write verification is pending",
    "reason: staged file is outside allowed scope",
    "reason: approval record is stale",
    "next: run post-write verification",
  ]
  assert "extra diagnostic" not in output


def test_normal_output_json_and_verbose_preserve_details():
  """Machine-readable and verbose modes keep detailed payloads available."""
  record = {
    "verdict": "OK",
    "action": "review-run",
    "summary_fields": {"run": "review-001"},
    "details": {"models": ["primary", "adversarial", "judgment"]},
  }

  json_payload = normal_output.render_json_output(record)
  verbose_output = normal_output.render_human_output(record, verbose=True)

  assert json_payload["details"]["models"] == [
    "primary",
    "adversarial",
    "judgment",
  ]
  assert "models" in verbose_output


def test_normal_output_stream_policy_routes_human_and_json():
  """Formatter defines stdout / stderr split for normal and diagnostic output."""
  assert normal_output.output_stream_for(verdict="OK", json_mode=False) == "stdout"
  assert normal_output.output_stream_for(verdict="WARN", json_mode=False) == "stderr"
  assert normal_output.output_stream_for(verdict="DEVIATION", json_mode=False) == "stderr"
  assert normal_output.output_stream_for(verdict="OK", json_mode=True) == "stdout"
