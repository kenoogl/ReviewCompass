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

from tools.api_providers.prepare_post_write_review import main as prepare_post_write_review
from tools.api_providers.run_review import main


def _make_config(tmp_path):
  config_path = tmp_path / "api-settings.yaml"
  config_path.write_text(
    """
connection:
  timeout_seconds: 60
  max_retries: 1
operation_defaults:
  api_review_prompt_quality:
    variant: prompt_quality_2way
  implementation_review:
    variant: implementation_review_independent_3way_codex_operator
  task_quality_review:
    variant: implementation_review_independent_3way_codex_operator
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
  prompt_quality_2way:
    context: prompt_quality
    variant_type: two_role
    required_roles: [adversarial, judgment]
    adversarial:
      path: api
      provider: anthropic-api
      model: claude-sonnet-4-6
    judgment:
      path: api
      provider: gemini-api
      model: gemini-3.1-pro-preview
  post_write_verification_google:
    context: post_write_verification
    variant_type: single_role
    required_roles: [primary]
    primary:
      path: api
      provider: gemini-api
      model: gemini-3.1-pro-preview
  implementation_review_independent_3way_codex_operator:
    context: triad_review
    variant_type: triad
    required_roles: [primary, adversarial, judgment]
    primary:
      path: api
      provider: openai-api
      model: gpt-5.4
    adversarial:
      path: api
      provider: anthropic-api
      model: claude-sonnet-4-6
    judgment:
      path: api
      provider: gemini-api
      model: gemini-3.1-pro-preview
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


def _write_prompt_manifest(
  path,
  target,
  *,
  decision_kind,
  language_constraints=None,
  unit_binding=None,
):
  source_sha = hashlib.sha256(target.read_bytes()).hexdigest()
  material_source = path.parent / "source-material.md"
  material_source.write_text("source material\n", encoding="utf-8")
  material_source_sha = hashlib.sha256(material_source.read_bytes()).hexdigest()
  constraints = language_constraints or [
    "Review language-level consistency only.",
  ]
  manifest = {
    "schema_version": "effective-prompt-manifest-v1",
    "decision_point": {
      "kind": decision_kind,
      "required_action": "run_post_write_verification",
    },
    "source_artifacts": [
      {
        "path": str(target),
        "sha256": f"sha256:{source_sha}",
      },
    ],
    "prompt_length": {
      "min_chars": 1,
      "max_chars": 20000,
      "failure_verdict": "DEVIATION",
    },
    "preconditions_checked": [
      {
        "name": "test-precondition",
        "machine_checked": True,
        "evidence_ref": str(target),
      },
    ],
    "language_task": {
      "constraints": constraints,
    },
    "review_prompt_materials": {
      "target_files": [
        {
          "path": str(target),
          "content_mode": "full_text",
          "content_sha256": f"sha256:{source_sha}",
        },
      ],
      "source_materials": [
        {
          "path": str(material_source),
          "content_mode": "full_text",
          "content_sha256": f"sha256:{material_source_sha}",
        },
      ],
    },
    "postconditions": [
      {
        "check_kind": "next_action_compatible",
        "source_ref": str(target),
      },
    ],
    "on_completion": {
      "allowed_followups": ["prompt-audit"],
      "forbidden_actions": ["commit", "push"],
      "next_required_action": "run_post_write_verification",
    },
  }
  if unit_binding is not None:
    manifest["unit_binding"] = unit_binding
  path.write_text(
    yaml.safe_dump(manifest, allow_unicode=True, sort_keys=False),
    encoding="utf-8",
  )
  return path


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
  assert output.count("\n") == 1
  assert output.startswith("[OK] run_review ")
  assert f"review_run_dir={review_run_dir}" in output
  assert f"summary={review_run_dir / 'review_summary.md'}" in output
  assert "roles=3" in output
  assert "findings=2" in output
  assert "parse_failed=0" in output

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


def test_run_review_uses_default_variant_for_operation(
  tmp_path,
  monkeypatch,
  capsys,
):
  """場面名から prompt-quality 既定 2 役 variant を解決する。"""
  monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
  monkeypatch.setenv("GEMINI_API_KEY", "test-key")
  target = tmp_path / "criteria-draft.md"
  target.write_text("API review criteria draft\n", encoding="utf-8")
  config_path = _make_config(tmp_path)
  review_run_dir = tmp_path / "prompt-quality-run"
  responses = {
    "anthropic-api": "findings: []\n",
    "gemini-api": "findings: []\n",
  }

  with patch(
    "tools.api_providers.run_review.get_provider",
    side_effect=_make_provider_factory(responses),
  ):
    exit_code = main(
      [
        "--default-variant-for", "api_review_prompt_quality",
        "--target", str(target),
        "--phase", "prompt-quality",
        "--criteria", "prompt quality",
        "--review-run-dir", str(review_run_dir),
        "--config", str(config_path),
      ]
    )

  assert exit_code == 0
  output = capsys.readouterr().out
  assert "roles=2" in output
  rounds = yaml.safe_load((review_run_dir / "rounds.yaml").read_text(encoding="utf-8"))
  triage = yaml.safe_load((review_run_dir / "triage.yaml").read_text(encoding="utf-8"))
  models = [item["model_id"] for item in rounds["model_results"]]
  assert models == ["claude-sonnet-4-6", "gemini-3.1-pro-preview"]
  assert [item["role"] for item in rounds["model_results"]] == [
    "adversarial",
    "judgment",
  ]
  assert triage["items"] == []
  review_summary = (review_run_dir / "review_summary.md").read_text(encoding="utf-8")
  assert "variant: prompt_quality_2way" in review_summary
  assert "| adversarial | api | anthropic-api | claude-sonnet-4-6 |" in review_summary
  assert "| judgment | api | gemini-api | gemini-3.1-pro-preview |" in review_summary
  assert "proxy_model" in review_summary
  assert "利用者提示ゲート" in review_summary


def test_run_review_uses_default_variant_for_implementation_review(
  tmp_path,
  monkeypatch,
  capsys,
):
  """場面名から implementation-review 既定 3 役 variant を解決する。"""
  monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
  monkeypatch.setenv("OPENAI_API_KEY", "test-key")
  monkeypatch.setenv("GEMINI_API_KEY", "test-key")
  target = tmp_path / "implementation.md"
  target.write_text("implementation target\n", encoding="utf-8")
  config_path = _make_config(tmp_path)
  review_run_dir = tmp_path / "implementation-review-run"
  responses = {
    "openai-api": "findings: []\n",
    "anthropic-api": "findings: []\n",
    "gemini-api": "findings: []\n",
  }

  with patch(
    "tools.api_providers.run_review.get_provider",
    side_effect=_make_provider_factory(responses),
  ):
    exit_code = main(
      [
        "--default-variant-for", "implementation_review",
        "--target", str(target),
        "--phase", "triad-review",
        "--criteria", "implementation review",
        "--review-run-dir", str(review_run_dir),
        "--config", str(config_path),
      ]
    )

  assert exit_code == 0
  output = capsys.readouterr().out
  assert "roles=3" in output
  rounds = yaml.safe_load((review_run_dir / "rounds.yaml").read_text(encoding="utf-8"))
  models = [item["model_id"] for item in rounds["model_results"]]
  assert models == ["gpt-5.4", "claude-sonnet-4-6", "gemini-3.1-pro-preview"]
  review_summary = (review_run_dir / "review_summary.md").read_text(encoding="utf-8")
  assert "variant: implementation_review_independent_3way_codex_operator" in review_summary
  assert "| primary | api | openai-api | gpt-5.4 |" in review_summary
  assert "| adversarial | api | anthropic-api | claude-sonnet-4-6 |" in review_summary
  assert "| judgment | api | gemini-api | gemini-3.1-pro-preview |" in review_summary


def test_run_review_uses_default_variant_for_task_quality_review(
  tmp_path,
  monkeypatch,
  capsys,
):
  """場面名から task-quality 既定 3 役 variant を解決する。"""
  monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
  monkeypatch.setenv("OPENAI_API_KEY", "test-key")
  monkeypatch.setenv("GEMINI_API_KEY", "test-key")
  target = tmp_path / "review-materials.yaml"
  target.write_text("task quality review materials\n", encoding="utf-8")
  config_path = _make_config(tmp_path)
  review_run_dir = tmp_path / "task-quality-review-run"
  responses = {
    "openai-api": "findings: []\n",
    "anthropic-api": "findings: []\n",
    "gemini-api": "findings: []\n",
  }

  with patch(
    "tools.api_providers.run_review.get_provider",
    side_effect=_make_provider_factory(responses),
  ):
    exit_code = main(
      [
        "--default-variant-for", "task_quality_review",
        "--target", str(target),
        "--phase", "task_quality_review",
        "--criteria", "task quality review",
        "--review-run-dir", str(review_run_dir),
        "--config", str(config_path),
      ]
    )

  assert exit_code == 0
  output = capsys.readouterr().out
  assert "roles=3" in output
  rounds = yaml.safe_load((review_run_dir / "rounds.yaml").read_text(encoding="utf-8"))
  models = [item["model_id"] for item in rounds["model_results"]]
  assert models == ["gpt-5.4", "claude-sonnet-4-6", "gemini-3.1-pro-preview"]
  review_summary = (review_run_dir / "review_summary.md").read_text(encoding="utf-8")
  assert "variant: implementation_review_independent_3way_codex_operator" in review_summary
  assert "| primary | api | openai-api | gpt-5.4 |" in review_summary
  assert "| adversarial | api | anthropic-api | claude-sonnet-4-6 |" in review_summary
  assert "| judgment | api | gemini-api | gemini-3.1-pro-preview |" in review_summary


def test_run_review_verbose_outputs_review_summary(tmp_path, monkeypatch, capsys):
  """--verbose では従来どおり review_summary.md の本文を stdout に出す。"""
  monkeypatch.setenv("GEMINI_API_KEY", "test-key")
  target = tmp_path / "target.md"
  target.write_text("レビュー対象\n", encoding="utf-8")
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
        "--criteria", "観点-1",
        "--review-run-dir", str(review_run_dir),
        "--round-id", "round-1",
        "--config", str(config_path),
        "--verbose",
      ]
    )

  assert exit_code == 0
  output = capsys.readouterr().out
  assert "variant: post_write_verification_google" in output
  assert "| primary | api | gemini-api | gemini-3.1-pro-preview |" in output
  assert "利用者提示ゲート" in output


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
  assert output.startswith("[OK] run_review ")
  assert "roles=1" in output
  assert "gemini-3.1-pro-preview" in output
  assert "claude-code-cli" not in output

  rounds = yaml.safe_load((review_run_dir / "rounds.yaml").read_text(encoding="utf-8"))
  assert [item["role"] for item in rounds["model_results"]] == ["primary"]


def test_run_review_blocks_post_write_when_next_action_is_policy_violation(
  tmp_path,
  monkeypatch,
  capsys,
):
  """post_write_policy_violation のまま review-run を開始しない。"""
  monkeypatch.setenv("GEMINI_API_KEY", "test-key")
  target = tmp_path / "target.md"
  target.write_text("post-write target body\n", encoding="utf-8")
  prompt_manifest = _write_prompt_manifest(
    tmp_path / "prompt-manifest.yaml",
    target,
    decision_kind="post_write_policy_violation",
  )
  config_path = _make_config(tmp_path)
  review_run_dir = tmp_path / "review-run"
  responses = {
    "gemini-api": "findings: []\n",
  }

  with patch(
    "tools.api_providers.run_review.get_provider",
    side_effect=_make_provider_factory(responses),
  ) as get_provider:
    exit_code = main(
      [
        "--target", str(target),
        "--phase", "post_write_verification",
        "--criteria", "post-write verification",
        "--review-run-dir", str(review_run_dir),
        "--config", str(config_path),
        "--prompt-manifest-path", str(prompt_manifest),
      ]
    )

  assert exit_code == 1
  assert get_provider.call_count == 0
  assert not (review_run_dir / "rounds.yaml").exists()
  assert "post_write_policy_violation" in capsys.readouterr().err


def test_run_review_blocks_post_write_when_prompt_manifest_audit_fails(
  tmp_path,
  monkeypatch,
  capsys,
):
  """prompt audit が DEVIATION の manifest では API runner を起動しない。"""
  monkeypatch.setenv("GEMINI_API_KEY", "test-key")
  target = tmp_path / "target.md"
  target.write_text("post-write target body\n", encoding="utf-8")
  prompt_manifest = _write_prompt_manifest(
    tmp_path / "prompt-manifest.yaml",
    target,
    decision_kind="post_write_verification",
    language_constraints=[
      "git commit after the review response is received.",
    ],
  )
  config_path = _make_config(tmp_path)
  review_run_dir = tmp_path / "review-run"
  responses = {
    "gemini-api": "findings: []\n",
  }

  with patch(
    "tools.api_providers.run_review.get_provider",
    side_effect=_make_provider_factory(responses),
  ) as get_provider:
    exit_code = main(
      [
        "--target", str(target),
        "--phase", "post_write_verification",
        "--criteria", "post-write verification",
        "--review-run-dir", str(review_run_dir),
        "--config", str(config_path),
        "--prompt-manifest-path", str(prompt_manifest),
      ]
    )

  assert exit_code == 1
  assert get_provider.call_count == 0
  assert not (review_run_dir / "rounds.yaml").exists()
  assert "prompt manifest audit" in capsys.readouterr().err


def test_run_review_blocks_post_write_when_unit_binding_mismatches_commit_unit(
  tmp_path,
  monkeypatch,
  capsys,
):
  """prompt manifest の unit_binding が現在の commit unit と違う場合は API を呼ばない。"""
  monkeypatch.setenv("GEMINI_API_KEY", "test-key")
  target = tmp_path / "target.md"
  target.write_text("post-write target body\n", encoding="utf-8")
  prompt_manifest = _write_prompt_manifest(
    tmp_path / "prompt-manifest.yaml",
    target,
    decision_kind="post_write_verification",
    unit_binding={
      "work_unit_id": "unit-old",
      "commit_unit_id": "commit-unit-old",
      "staged_digest": {
        "algorithm": "commit-unit-v1",
        "digest": "old-digest",
      },
    },
  )
  commit_unit_path = (
    tmp_path / ".reviewcompass" / "runtime" / "work-units" / "commit-unit.json"
  )
  commit_unit_path.parent.mkdir(parents=True)
  commit_unit_path.write_text(
    "{\n"
    '  "schema_version": "commit-unit-v1",\n'
    '  "work_unit_id": "unit-current",\n'
    '  "commit_unit_id": "commit-unit-current",\n'
    '  "staged_digest": {\n'
    '    "algorithm": "commit-unit-v1",\n'
    '    "digest": "current-digest"\n'
    "  }\n"
    "}\n",
    encoding="utf-8",
  )
  config_path = _make_config(tmp_path)
  review_run_dir = tmp_path / "review-run"
  responses = {
    "gemini-api": "findings: []\n",
  }

  with patch(
    "tools.api_providers.run_review.get_provider",
    side_effect=_make_provider_factory(responses),
  ) as get_provider:
    exit_code = main(
      [
        "--target", str(target),
        "--phase", "post_write_verification",
        "--criteria", "post-write verification",
        "--review-run-dir", str(review_run_dir),
        "--config", str(config_path),
        "--prompt-manifest-path", str(prompt_manifest),
      ]
    )

  assert exit_code == 1
  assert get_provider.call_count == 0
  assert not (review_run_dir / "rounds.yaml").exists()
  assert "unit binding" in capsys.readouterr().err


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
  assert output.startswith("[OK] run_review ")
  assert "roles=1" in output
  assert "model_ids=gemini-3.1-pro-preview" in output
  assert "| adversarial |" not in output
  assert "| judgment |" not in output

  triage = yaml.safe_load((review_run_dir / "triage.yaml").read_text(encoding="utf-8"))
  assert len(triage["items"]) == 1
  assert triage["items"][0]["source_model"] == "gemini-3.1-pro-preview"


def test_run_review_preserves_structured_fields_in_parsed_artifact(
  tmp_path,
  monkeypatch,
  capsys,
):
  """run_review でも findings 以外の検査結果を parsed 成果物に保持する。"""
  monkeypatch.setenv("GEMINI_API_KEY", "test-key")
  target = tmp_path / "target.md"
  target.write_text("レビュー対象\n", encoding="utf-8")
  config_path = _make_config(tmp_path)
  review_run_dir = tmp_path / "review-run"
  responses = {
    "gemini-api": """
verdict: insufficient
independent_reconstruction:
  judgment_items:
    - item_id: prompt_source_coverage
      question: source から preanalysis を引き出せるか
preanalysis_assessment:
  missing_perspectives:
    - upstream connection
prompt_sufficiency:
  information: insufficient
required_prompt_changes:
  - source を原文として渡す
findings: []
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
        "--phase", "prompt-quality",
        "--criteria", "preanalysis sufficiency",
        "--review-run-dir", str(review_run_dir),
        "--round-id", "round-1",
        "--config", str(config_path),
      ]
    )

  assert exit_code == 0
  capsys.readouterr()
  parsed_path = review_run_dir / "parsed" / "gemini-3.1-pro-preview.round-1.yaml"
  parsed = yaml.safe_load(parsed_path.read_text(encoding="utf-8"))
  assert parsed["verdict"] == "insufficient"
  assert parsed["independent_reconstruction"]["judgment_items"][0]["item_id"] == "prompt_source_coverage"
  assert parsed["preanalysis_assessment"]["missing_perspectives"] == ["upstream connection"]
  assert parsed["prompt_sufficiency"]["information"] == "insufficient"
  assert parsed["required_prompt_changes"] == ["source を原文として渡す"]
  assert parsed["findings"] == []


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
  assert rounds["effective_prompt_sha256_prefixed"] == "sha256:" + rounds["effective_prompt_sha256"]


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


def test_run_review_accepts_prepare_post_write_prompt_manifest(
  tmp_path,
  monkeypatch,
):
  """prepare_post_write_review が生成した manifest は runner preflight を通る。"""
  monkeypatch.setenv("GEMINI_API_KEY", "test-key")
  target = tmp_path / "docs" / "operations" / "WORKFLOW_NAVIGATION.md"
  target.parent.mkdir(parents=True)
  target.write_text("post-write target body\n", encoding="utf-8")
  source = tmp_path / ".reviewcompass" / "guidance" / "API_REVIEW_PROMPT_QUALITY.md"
  source.parent.mkdir(parents=True)
  source.write_text("source material body\n", encoding="utf-8")
  review_run_dir = tmp_path / "review-run"
  prepare_exit_code = prepare_post_write_review(
    [
      "--target", str(target),
      "--source-material", str(source),
      "--review-run-dir", str(review_run_dir),
      "--criteria-id", "post_write_prompt_manifest_acceptance",
      "--change-summary", "post-write prompt manifest を検証する。",
    ]
  )
  assert prepare_exit_code == 0
  config_path = _make_config(tmp_path)
  responses = {"gemini-api": "findings: []\n"}

  with patch(
    "tools.api_providers.run_review.get_provider",
    side_effect=_make_provider_factory(responses),
  ) as get_provider:
    exit_code = main(
      [
        "--variant", "post_write_verification_google",
        "--target", str(target),
        "--phase", "post_write_verification",
        "--criteria-file", str(review_run_dir / "review-target.md"),
        "--review-run-dir", str(review_run_dir),
        "--config", str(config_path),
        "--prompt-manifest-path", str(review_run_dir / "prompt-manifest.yaml"),
      ]
    )

  assert exit_code == 0
  assert get_provider.call_count == 1
  rounds = yaml.safe_load((review_run_dir / "rounds.yaml").read_text(encoding="utf-8"))
  assert rounds["prompt_manifest_path"] == str(review_run_dir / "prompt-manifest.yaml")


def test_run_review_blocks_vertical_review_when_source_materials_are_paths_only(
  tmp_path,
  monkeypatch,
  capsys,
):
  """縦方向監査で source materials がパスだけなら API 送信前に遮断する。"""
  monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
  monkeypatch.setenv("OPENAI_API_KEY", "test-key")
  monkeypatch.setenv("GEMINI_API_KEY", "test-key")
  target = tmp_path / "requirements.md"
  target.write_text("Requirement 13 本文\n", encoding="utf-8")
  criteria_file = tmp_path / "review-target.md"
  criteria_file.write_text(
    "# Requirements Triad Review Target\n\n"
    "## Source Materials\n\n"
    "Use these source materials as upstream decision materials:\n\n"
    "- `docs/reviews/reopen-classification.md`\n"
    "- `docs/notes/integrated-design.md`\n\n"
    "## Required Check\n\n"
    "Check whether upstream purpose, responsibility boundaries, acceptance criteria, "
    "and forbidden actions were inherited into requirements.md.\n",
    encoding="utf-8",
  )
  config_path = _make_config(tmp_path)
  review_run_dir = tmp_path / "review-run"
  provider_factory = _make_provider_factory({
    "anthropic-api": "findings: []\n",
    "openai-api": "findings: []\n",
    "gemini-api": "findings: []\n",
  })

  with patch("tools.api_providers.run_review.get_provider", side_effect=provider_factory) as get_provider:
    exit_code = main(
      [
        "--target", str(target),
        "--phase", "triad-review",
        "--criteria-file", str(criteria_file),
        "--review-run-dir", str(review_run_dir),
        "--config", str(config_path),
      ]
    )

  captured = capsys.readouterr()
  assert exit_code == 1
  assert "vertical intent transfer prompt preflight failed" in captured.err
  assert "source materials are listed only as paths" in captured.err
  assert not get_provider.called
  assert not (review_run_dir / "prompts").exists()


def test_run_review_allows_vertical_review_with_structured_upstream_summary(
  tmp_path,
  monkeypatch,
):
  """縦方向監査でも上流要点が実体化されていれば API 送信できる。"""
  monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
  monkeypatch.setenv("OPENAI_API_KEY", "test-key")
  monkeypatch.setenv("GEMINI_API_KEY", "test-key")
  target = tmp_path / "requirements.md"
  target.write_text("Requirement 13 本文\n", encoding="utf-8")
  criteria_file = tmp_path / "review-target.md"
  criteria_file.write_text(
    "# Requirements Vertical Intent Review\n\n"
    "## Source Materials\n\n"
    "- `docs/notes/upstream.md`\n\n"
    "## Upstream Structured Summary\n\n"
    "- purpose: 操作契約を機械可読にし、LLM の推測を減らす。\n"
    "- responsibility_boundaries: registry は read-only consumer、contract が正本。\n"
    "- acceptance_criteria: 19 required_action の effect_kind と approval_required を持つ。\n"
    "- forbidden_actions: source materials をパスだけで扱わない。承認不要操作を勝手に承認済みにしない。\n"
    "- unresolved_or_design_deferred_items: 複合操作の物理表現は design で確定する。\n"
    "- intended_target_phase_transfer: Requirement 13 に正本境界と承認要否を渡す。\n\n"
    "## Required Check\n\n"
    "Check whether upstream purpose, responsibility boundaries, acceptance criteria, "
    "and forbidden actions were inherited into requirements.md.\n",
    encoding="utf-8",
  )
  config_path = _make_config(tmp_path)
  review_run_dir = tmp_path / "review-run"
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
        "--phase", "triad-review",
        "--criteria-file", str(criteria_file),
        "--review-run-dir", str(review_run_dir),
        "--config", str(config_path),
      ]
    )

  assert exit_code == 0
  rounds = yaml.safe_load((review_run_dir / "rounds.yaml").read_text(encoding="utf-8"))
  assert len(rounds["model_results"]) == 3
