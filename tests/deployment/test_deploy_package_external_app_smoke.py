import importlib.util
from pathlib import Path

import yaml


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


def test_deploy_package_writes_review_run_to_external_app_root(tmp_path):
  module = _load_module()
  package_dir = tmp_path / "ReviewCompass"
  app_root = tmp_path / "external-app"
  module.build_package(
    repo_root=REPO_ROOT,
    manifest_path=MANIFEST_PATH,
    output_dir=package_dir,
    clean=True,
  )
  app_root.mkdir()

  result = module.smoke_test_external_app_root(
    package_dir=package_dir,
    app_root=app_root,
  )

  review_run_dir = app_root / ".reviewcompass/specs/demo/reviews/smoke-run"
  assert result["ok"] is True
  assert result["review_run_dir"] == str(review_run_dir)
  assert (review_run_dir / "raw/smoke-model.round-1.txt").is_file()
  assert (review_run_dir / "parsed/smoke-model.round-1.yaml").is_file()
  rounds = yaml.safe_load((review_run_dir / "rounds.yaml").read_text(encoding="utf-8"))
  target_manifest = yaml.safe_load(
    (review_run_dir / "target-manifest.yaml").read_text(encoding="utf-8")
  )
  assert rounds["model_results"][0]["provider"] == "smoke-provider"
  assert target_manifest["target_files"][0]["path"].endswith("app.md")
