# tools/api_providers/tests/test_post_write_review_flow.py
# post-write API review 前後の機械化入口の TDD テスト。

import hashlib
import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
  sys.path.insert(0, str(_PROJECT_ROOT))

import yaml

from tools.api_providers.post_write_review_flow import main


def _write_guidance_files(cwd):
  guidance = cwd / ".reviewcompass" / "guidance"
  guidance.mkdir(parents=True)
  api_quality = guidance / "API_REVIEW_PROMPT_QUALITY.md"
  api_quality.write_text(
    "# API Review Prompt Quality\n"
    "review prompt は target/source/out-of-scope を分離する。\n",
    encoding="utf-8",
  )
  post_write = guidance / "discipline_post_write_verification.md"
  post_write.write_text(
    "# Post-write Verification\n"
    "post-write review では対象本文と根拠本文を API に渡す。\n",
    encoding="utf-8",
  )
  return api_quality, post_write


def _write_next_action(path, kind, target_files=None):
  path.write_text(
    yaml.safe_dump(
      {
        "verdict": "OK",
        "exit_code": 0,
        "next_action": {
          "kind": kind,
          "target_files": target_files or [],
        },
      },
      allow_unicode=True,
      sort_keys=False,
    ),
    encoding="utf-8",
  )


def _write_clean_review_run(cwd, relative_target):
  run_dir = cwd / ".reviewcompass" / "evidence" / "review-runs" / "run"
  raw_dir = run_dir / "raw"
  raw_dir.mkdir(parents=True)
  raw_file = raw_dir / "gemini-3.1-pro-preview.round-1.txt"
  raw_file.write_text("findings: []\n", encoding="utf-8")
  target = cwd / relative_target
  target.parent.mkdir(parents=True, exist_ok=True)
  target.write_text("target\n", encoding="utf-8")
  target_sha = hashlib.sha256(target.read_bytes()).hexdigest()
  raw_sha = hashlib.sha256(raw_file.read_bytes()).hexdigest()
  target_files = [{"path": relative_target, "sha256": target_sha}]
  (run_dir / "target-manifest.yaml").write_text(
    yaml.safe_dump(
      {"run_id": run_dir.name, "target_files": target_files},
      allow_unicode=True,
      sort_keys=False,
    ),
    encoding="utf-8",
  )
  (run_dir / "rounds.yaml").write_text(
    yaml.safe_dump(
      {
        "round_id": "round-1",
        "purpose": "post_write_verification",
        "target_files": target_files,
        "model_results": [
          {
            "model_id": "gemini-3.1-pro-preview",
            "provider": "gemini-api",
            "role": "primary",
            "raw_path": "raw/gemini-3.1-pro-preview.round-1.txt",
            "raw_sha256": raw_sha,
            "parse_status": "parsed",
          },
        ],
      },
      allow_unicode=True,
      sort_keys=False,
    ),
    encoding="utf-8",
  )
  (run_dir / "model-result-summary.yaml").write_text(
    yaml.safe_dump(
      {
        "run_id": run_dir.name,
        "models": [
          {
            "model_id": "gemini-3.1-pro-preview",
            "raw_path": "raw/gemini-3.1-pro-preview.round-1.txt",
            "parse_status": "parsed",
            "triage_status": "no_findings",
            "findings_count": 0,
            "must_fix_count": 0,
            "should_fix_count": 0,
            "leave_as_is_count": 0,
            "human_required_count": 0,
          },
        ],
      },
      allow_unicode=True,
      sort_keys=False,
    ),
    encoding="utf-8",
  )
  (run_dir / "triage.yaml").write_text(
    yaml.safe_dump(
      {"run_id": run_dir.name, "triage_status": "draft", "items": []},
      allow_unicode=True,
      sort_keys=False,
    ),
    encoding="utf-8",
  )
  return run_dir


def test_prepare_from_next_action_generates_review_materials(tmp_path, monkeypatch):
  """next --json の post_write_verification 地点から prepare 引数を機械確定する。"""
  monkeypatch.chdir(tmp_path)
  api_quality, post_write = _write_guidance_files(tmp_path)
  target = tmp_path / ".reviewcompass" / "guidance" / "WORKFLOW_NAVIGATION.md"
  target.parent.mkdir(parents=True, exist_ok=True)
  target.write_text(
    "### post_write_verification\n"
    "API review は prompt-manifest を preflight する。\n",
    encoding="utf-8",
  )
  next_action = tmp_path / "next.yaml"
  _write_next_action(
    next_action,
    "post_write_verification",
    [".reviewcompass/guidance/WORKFLOW_NAVIGATION.md"],
  )
  review_run_dir = tmp_path / ".reviewcompass" / "evidence" / "review-runs" / "auto"

  exit_code = main(
    [
      "prepare",
      "--next-action-file", str(next_action),
      "--review-run-dir", str(review_run_dir),
    ]
  )

  assert exit_code == 0
  review_target = review_run_dir / "review-target.md"
  prompt_manifest = review_run_dir / "prompt-manifest.yaml"
  metadata = yaml.safe_load(
    (review_run_dir / "review-target.yaml").read_text(encoding="utf-8")
  )
  manifest = yaml.safe_load(prompt_manifest.read_text(encoding="utf-8"))
  assert review_target.is_file()
  assert metadata["criteria_id"] == "post_write_verification__workflow_navigation"
  assert metadata["target_files"][0]["path"] == str(target)
  assert [entry["path"] for entry in metadata["source_materials"]] == [
    str(api_quality),
    str(post_write),
  ]
  assert metadata["recommended_run_review_args"]["prompt_manifest_path"] == str(
    prompt_manifest
  )
  assert manifest["review_prompt_materials"]["source_materials"][0]["content_mode"] == (
    "full_text"
  )
  content = review_target.read_text(encoding="utf-8")
  assert "## Source Materials" in content
  assert "review prompt は target/source/out-of-scope を分離する。" in content
  assert "## Target File Contents" in content
  assert "prompt-manifest を preflight" in content


def test_prepare_from_next_action_blocks_non_post_write_kind(tmp_path, monkeypatch):
  """post_write_verification 以外の地点では review-run 材料を作らない。"""
  monkeypatch.chdir(tmp_path)
  next_action = tmp_path / "next.yaml"
  _write_next_action(next_action, "completed")
  review_run_dir = tmp_path / ".reviewcompass" / "evidence" / "review-runs" / "auto"

  exit_code = main(
    [
      "prepare",
      "--next-action-file", str(next_action),
      "--review-run-dir", str(review_run_dir),
    ]
  )

  assert exit_code == 1
  assert not review_run_dir.exists()


def test_prepare_requires_commit_unit_when_blocking_unit_active(tmp_path, monkeypatch):
  """active blocking unit 中は commit unit なしで review-run 材料を作らない。"""
  monkeypatch.chdir(tmp_path)
  _write_guidance_files(tmp_path)
  target = tmp_path / ".reviewcompass" / "guidance" / "WORKFLOW_NAVIGATION.md"
  target.parent.mkdir(parents=True, exist_ok=True)
  target.write_text(
    "### post_write_verification\n"
    "API review は prompt-manifest を preflight する。\n",
    encoding="utf-8",
  )
  stack_path = tmp_path / ".reviewcompass" / "runtime" / "work-units" / "stack.yaml"
  stack_path.parent.mkdir(parents=True, exist_ok=True)
  stack_path.write_text(
    yaml.safe_dump(
      {
        "schema_version": "work-unit-stack-v1",
        "frames": [
          {
            "unit_id": "unit-blocking-test",
            "kind": "blocking",
            "parent_unit_id": "main-completed",
            "title": "Blocking test",
            "reason": "test",
            "return_conditions": ["done"],
          },
        ],
      },
      allow_unicode=True,
      sort_keys=False,
    ),
    encoding="utf-8",
  )
  next_action = tmp_path / "next.yaml"
  _write_next_action(
    next_action,
    "post_write_verification",
    [".reviewcompass/guidance/WORKFLOW_NAVIGATION.md"],
  )
  review_run_dir = tmp_path / ".reviewcompass" / "evidence" / "review-runs" / "auto"

  exit_code = main(
    [
      "prepare",
      "--next-action-file", str(next_action),
      "--review-run-dir", str(review_run_dir),
    ]
  )

  assert exit_code == 2
  assert not (review_run_dir / "review-target.md").exists()


def test_finalize_no_findings_writes_post_write_manifest(tmp_path, monkeypatch):
  """所見 0 件の review-run は承認なしで完了 manifest 生成へ接続できる。"""
  monkeypatch.chdir(tmp_path)
  run_dir = _write_clean_review_run(tmp_path, "docs/operations/reviewed.md")
  output_path = tmp_path / ".reviewcompass" / "post-write-verification" / "done.yaml"

  exit_code = main(
    [
      "finalize-no-findings",
      "--review-run-dir", str(run_dir),
      "--out", str(output_path),
    ]
  )

  assert exit_code == 0
  manifest = yaml.safe_load(output_path.read_text(encoding="utf-8"))
  assert manifest["status"] == "completed"
  assert manifest["target_files"] == ["docs/operations/reviewed.md"]
