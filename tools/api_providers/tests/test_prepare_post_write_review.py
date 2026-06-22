# tools/api_providers/tests/test_prepare_post_write_review.py
# post-write API 検査前の review-target 生成テスト。

import hashlib
import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
  sys.path.insert(0, str(_PROJECT_ROOT))

import yaml

from tools.api_providers.prepare_post_write_review import main
from tools.check_workflow_action.prompt_audit import audit_manifest


def test_prepare_post_write_review_writes_review_target_and_metadata(tmp_path, capsys):
  """対象・観点・機微情報確認を review-run 配下に機械生成する。"""
  target = tmp_path / "docs" / "operations" / "WORKFLOW_PRECHECK.md"
  target.parent.mkdir(parents=True)
  target.write_text("commit preflight contract\n", encoding="utf-8")
  review_run_dir = tmp_path / ".reviewcompass" / "evidence" / "review-runs" / "run"

  exit_code = main(
    [
      "--target", str(target),
      "--review-run-dir", str(review_run_dir),
      "--criteria-id", "commit_instruction_preflight_contract_clearance",
      "--change-summary", "commit 指示後の preflight 契約を文書へ反映した。",
      "--review-question", "commit 指示後、git add より前に preflight が走る契約が明確か。",
    ]
  )

  assert exit_code == 0
  captured = capsys.readouterr()
  assert captured.out.count("\n") == 1
  assert captured.out.startswith("[OK] prepare_post_write_review ")
  review_target = review_run_dir / "review-target.md"
  metadata_path = review_run_dir / "review-target.yaml"
  assert f"review_target={review_target}" in captured.out
  assert f"metadata={metadata_path}" in captured.out
  assert review_target.is_file()
  assert metadata_path.is_file()
  content = review_target.read_text(encoding="utf-8")
  assert "commit_instruction_preflight_contract_clearance" in content
  assert "git add より前" in content
  assert "Sensitive Information Check" in content
  metadata = yaml.safe_load(metadata_path.read_text(encoding="utf-8"))
  assert metadata["criteria_file"] == str(review_target)
  assert metadata["criteria_file_sha256"] == hashlib.sha256(
    review_target.read_bytes()
  ).hexdigest()
  assert metadata["sensitive_information_check"]["status"] == "passed"
  assert metadata["target_files"][0]["sha256"] == hashlib.sha256(
    target.read_bytes()
  ).hexdigest()


def test_prepare_post_write_review_embeds_target_body_not_only_path_and_sha(tmp_path):
  """API review prompt の材料は path/SHA だけにせず target 本文を含める。"""
  target = tmp_path / "docs" / "operations" / "WORKFLOW_NAVIGATION.md"
  target.parent.mkdir(parents=True)
  target.write_text(
    "### post_write_policy_violation\n"
    "この地点では review-run を開始せず、未検証変更を分類する。\n",
    encoding="utf-8",
  )
  review_run_dir = tmp_path / ".reviewcompass" / "evidence" / "review-runs" / "run"

  exit_code = main(
    [
      "--target", str(target),
      "--review-run-dir", str(review_run_dir),
      "--criteria-id", "post_write_policy_violation_prompt_materialization",
      "--change-summary", "post-write policy violation の手順を固定する。",
    ]
  )

  assert exit_code == 0
  review_target = (review_run_dir / "review-target.md").read_text(encoding="utf-8")
  metadata = yaml.safe_load(
    (review_run_dir / "review-target.yaml").read_text(encoding="utf-8")
  )
  assert "## Target File Contents" in review_target
  assert "この地点では review-run を開始せず" in review_target
  assert metadata["target_files"][0]["content_mode"] == "full_text"
  assert metadata["target_files"][0]["content_sha256"] == hashlib.sha256(
    target.read_bytes()
  ).hexdigest()


def test_prepare_post_write_review_embeds_source_material_body_separate_from_target(tmp_path):
  """source materials は path-only にせず、target と分離して本文を含める。"""
  target = tmp_path / "docs" / "operations" / "WORKFLOW_NAVIGATION.md"
  target.parent.mkdir(parents=True)
  target.write_text(
    "### post_write_verification\n"
    "書き込み後検証では、対象ファイル全体を確認する。\n",
    encoding="utf-8",
  )
  source = tmp_path / ".reviewcompass" / "guidance" / "API_REVIEW_PROMPT_QUALITY.md"
  source.parent.mkdir(parents=True)
  source.write_text(
    "# API Review Prompt Quality\n"
    "target / source materials / out of scope を分離する。\n",
    encoding="utf-8",
  )
  review_run_dir = tmp_path / ".reviewcompass" / "evidence" / "review-runs" / "run"

  exit_code = main(
    [
      "--target", str(target),
      "--source-material", str(source),
      "--review-run-dir", str(review_run_dir),
      "--criteria-id", "post_write_source_bundle_materialization",
      "--change-summary", "post-write review prompt の source bundle を機械化する。",
    ]
  )

  assert exit_code == 0
  review_target = (review_run_dir / "review-target.md").read_text(encoding="utf-8")
  metadata = yaml.safe_load(
    (review_run_dir / "review-target.yaml").read_text(encoding="utf-8")
  )
  assert "## Source Materials" in review_target
  assert "target / source materials / out of scope を分離する。" in review_target
  assert "## Target File Contents" in review_target
  assert metadata["target_files"][0]["path"] == str(target)
  assert metadata["source_materials"][0]["path"] == str(source)
  assert metadata["source_materials"][0]["content_mode"] == "full_text"
  assert metadata["source_materials"][0]["content_sha256"] == hashlib.sha256(
    source.read_bytes()
  ).hexdigest()


def test_prepare_post_write_review_writes_auditable_prompt_manifest(tmp_path):
  """生成した source bundle を API 起動前 audit に渡せる manifest へ固定する。"""
  target = tmp_path / "docs" / "operations" / "WORKFLOW_NAVIGATION.md"
  target.parent.mkdir(parents=True)
  target.write_text(
    "### post_write_verification\n"
    "書き込み後検証では、対象ファイル本文を review prompt に含める。\n",
    encoding="utf-8",
  )
  source = tmp_path / ".reviewcompass" / "guidance" / "API_REVIEW_PROMPT_QUALITY.md"
  source.parent.mkdir(parents=True)
  source.write_text(
    "# API Review Prompt Quality\n"
    "source material は path-only にしない。\n",
    encoding="utf-8",
  )
  review_run_dir = tmp_path / ".reviewcompass" / "evidence" / "review-runs" / "run"

  exit_code = main(
    [
      "--target", str(target),
      "--source-material", str(source),
      "--review-run-dir", str(review_run_dir),
      "--criteria-id", "post_write_source_bundle_materialization",
      "--change-summary", "post-write review prompt の source bundle を機械化する。",
    ]
  )

  assert exit_code == 0
  prompt_manifest_path = review_run_dir / "prompt-manifest.yaml"
  metadata = yaml.safe_load(
    (review_run_dir / "review-target.yaml").read_text(encoding="utf-8")
  )
  manifest = yaml.safe_load(prompt_manifest_path.read_text(encoding="utf-8"))
  assert metadata["recommended_run_review_args"]["prompt_manifest_path"] == str(
    prompt_manifest_path
  )
  assert manifest["decision_point"]["kind"] == "post_write_verification"
  assert manifest["review_prompt_materials"]["target_files"][0]["path"] == str(target)
  assert manifest["review_prompt_materials"]["target_files"][0]["content_mode"] == (
    "full_text"
  )
  assert manifest["review_prompt_materials"]["source_materials"][0]["path"] == str(
    source
  )
  assert manifest["review_prompt_materials"]["source_materials"][0]["content_mode"] == (
    "full_text"
  )
  assert audit_manifest(manifest)["verdict"] == "OK"


def test_prepare_post_write_review_records_commit_unit_binding(tmp_path):
  """commit-unit record があれば review-target と manifest に unit binding を記録する。"""
  target = tmp_path / "docs" / "operations" / "WORKFLOW_NAVIGATION.md"
  target.parent.mkdir(parents=True)
  target.write_text(
    "### post_write_verification\n"
    "review evidence must bind to the active commit unit.\n",
    encoding="utf-8",
  )
  commit_unit_path = (
    tmp_path / ".reviewcompass" / "runtime" / "work-units" / "commit-unit.json"
  )
  commit_unit_path.parent.mkdir(parents=True)
  commit_unit_path.write_text(
    "{\n"
    '  "schema_version": "commit-unit-v1",\n'
    '  "commit_unit_id": "commit-unit-test",\n'
    '  "work_unit_id": "unit-blocking-test",\n'
    '  "staged_digest": {\n'
    '    "algorithm": "commit-unit-v1",\n'
    '    "digest": "abc123"\n'
    "  }\n"
    "}\n",
    encoding="utf-8",
  )
  review_run_dir = tmp_path / ".reviewcompass" / "evidence" / "review-runs" / "run"

  exit_code = main(
    [
      "--target", str(target),
      "--review-run-dir", str(review_run_dir),
      "--criteria-id", "post_write_commit_unit_binding",
      "--change-summary", "post-write review evidence を commit unit に束縛する。",
    ]
  )

  assert exit_code == 0
  metadata = yaml.safe_load(
    (review_run_dir / "review-target.yaml").read_text(encoding="utf-8")
  )
  manifest = yaml.safe_load(
    (review_run_dir / "prompt-manifest.yaml").read_text(encoding="utf-8")
  )
  assert metadata["unit_binding"] == {
    "work_unit_id": "unit-blocking-test",
    "commit_unit_id": "commit-unit-test",
    "staged_digest": {
      "algorithm": "commit-unit-v1",
      "digest": "abc123",
    },
  }
  assert manifest["unit_binding"] == metadata["unit_binding"]


def test_prepare_post_write_review_fails_closed_on_secret_like_target(tmp_path):
  """外部 API に送る前に secret らしい対象を止める。"""
  target = tmp_path / "docs" / "operations" / "SECRET.md"
  target.parent.mkdir(parents=True)
  target.write_text("OPENAI_API_KEY=sk-testsecret\n", encoding="utf-8")
  review_run_dir = tmp_path / ".reviewcompass" / "evidence" / "review-runs" / "run"

  exit_code = main(
    [
      "--target", str(target),
      "--review-run-dir", str(review_run_dir),
      "--criteria-id", "secret_check",
      "--change-summary", "secret check",
    ]
  )

  assert exit_code == 2
  assert not (review_run_dir / "review-target.md").exists()


def test_prepare_post_write_review_fails_closed_on_missing_source_material(tmp_path):
  """source material が存在しない場合は review-target を作らない。"""
  target = tmp_path / "docs" / "operations" / "WORKFLOW_NAVIGATION.md"
  target.parent.mkdir(parents=True)
  target.write_text("post-write target body\n", encoding="utf-8")
  missing_source = tmp_path / ".reviewcompass" / "guidance" / "MISSING.md"
  review_run_dir = tmp_path / ".reviewcompass" / "evidence" / "review-runs" / "run"

  exit_code = main(
    [
      "--target", str(target),
      "--source-material", str(missing_source),
      "--review-run-dir", str(review_run_dir),
      "--criteria-id", "missing_source",
      "--change-summary", "missing source check",
    ]
  )

  assert exit_code == 1
  assert not (review_run_dir / "review-target.md").exists()


def test_prepare_post_write_review_fails_closed_on_secret_like_source_material(tmp_path):
  """source material 側の secret らしい内容も外部 API 送信前に止める。"""
  target = tmp_path / "docs" / "operations" / "WORKFLOW_NAVIGATION.md"
  target.parent.mkdir(parents=True)
  target.write_text("post-write target body\n", encoding="utf-8")
  source = tmp_path / ".reviewcompass" / "guidance" / "API_REVIEW_PROMPT_QUALITY.md"
  source.parent.mkdir(parents=True)
  source.write_text("GEMINI_API_KEY=sk-testsecret\n", encoding="utf-8")
  review_run_dir = tmp_path / ".reviewcompass" / "evidence" / "review-runs" / "run"

  exit_code = main(
    [
      "--target", str(target),
      "--source-material", str(source),
      "--review-run-dir", str(review_run_dir),
      "--criteria-id", "secret_source",
      "--change-summary", "secret source check",
    ]
  )

  assert exit_code == 2
  assert not (review_run_dir / "review-target.md").exists()
