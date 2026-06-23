import importlib.util
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = REPO_ROOT / "deploy-manifest.yaml"
SCRIPT_PATH = REPO_ROOT / "tools" / "build-deploy-package.py"


def _load_module():
  spec = importlib.util.spec_from_file_location(
    "build_deploy_package",
    SCRIPT_PATH,
  )
  module = importlib.util.module_from_spec(spec)
  spec.loader.exec_module(module)
  return module


def test_build_package_copies_allowlisted_files_and_skips_excluded_files(tmp_path):
  module = _load_module()
  output_dir = tmp_path / "ReviewCompass"

  result = module.build_package(
    repo_root=REPO_ROOT,
    manifest_path=MANIFEST_PATH,
    output_dir=output_dir,
    clean=True,
  )

  copied_paths = {entry["path"] for entry in result["copied"]}
  assert "pyproject.toml" in copied_paths
  assert "runtime/prompts/primary_detection/primary_reviewer.prompt.md" in copied_paths
  assert "tools/check-workflow-action.py" in copied_paths
  assert "tools/session-record-backfill.py" in copied_paths
  assert "tools/session_record_extractor/record.py" in copied_paths
  assert "learning/workflow/schemas/proposal.schema.json" in copied_paths
  assert "templates/hooks/session-record-capture-current-on-session-end.sh.template" in copied_paths
  assert "analysis/README.md" in copied_paths
  assert "evaluation/intake/bundle_intake.py" in copied_paths

  assert (output_dir / "pyproject.toml").is_file()
  assert (
    output_dir / "runtime/prompts/primary_detection/primary_reviewer.prompt.md"
  ).is_file()
  assert (output_dir / "tools/session-record-backfill.py").is_file()
  assert (
    output_dir / "templates/hooks/session-record-capture-current-on-session-end.sh.template"
  ).is_file()
  assert not (output_dir / "docs/notes/2026-06-02-workflow-navigation-implementation-plan.md").exists()
  assert not (output_dir / "tools/api_providers/tests/test_run_review.py").exists()
  assert not (output_dir / "tools/experiments/judgment-aid-for-human.md").exists()
  assert not (
    output_dir / ".reviewcompass/post-write-verification/post-write-2026-06-10-004.yaml"
  ).exists()
  assert not (output_dir / "tests/deployment/test_deploy_manifest.py").exists()


def test_build_package_rejects_cleaning_repository_root():
  module = _load_module()

  with pytest.raises(ValueError, match="unsafe output directory"):
    module.build_package(
      repo_root=REPO_ROOT,
      manifest_path=MANIFEST_PATH,
      output_dir=REPO_ROOT,
      clean=True,
    )


def test_verify_package_contents_detects_unexpected_and_excluded_files(tmp_path):
  module = _load_module()
  output_dir = tmp_path / "ReviewCompass"
  module.build_package(
    repo_root=REPO_ROOT,
    manifest_path=MANIFEST_PATH,
    output_dir=output_dir,
    clean=True,
  )

  unexpected_file = output_dir / "local-only.txt"
  unexpected_file.write_text("must not ship\n", encoding="utf-8")
  excluded_file = output_dir / "docs/notes/internal-note.md"
  excluded_file.parent.mkdir(parents=True)
  excluded_file.write_text("must not ship\n", encoding="utf-8")

  result = module.verify_package_contents(
    repo_root=REPO_ROOT,
    manifest_path=MANIFEST_PATH,
    package_dir=output_dir,
  )

  assert result["ok"] is False
  assert result["unexpected_files"] == ["local-only.txt"]
  assert result["excluded_files"] == ["docs/notes/internal-note.md"]
