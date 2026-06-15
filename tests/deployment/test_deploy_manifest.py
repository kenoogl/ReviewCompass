from fnmatch import fnmatch
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = REPO_ROOT / "deploy-manifest.yaml"

REQUIRED_ALLOWLIST = {
  "pyproject.toml",
  "runtime/runtime_core/**/*.py",
  "runtime/runtime_core/**/*.yaml",
  "tools/api_providers/run_review.py",
  "tools/api_providers/run_role.py",
  "tools/session-record-backfill.py",
  "tools/session-record-extractor.py",
  "tools/session_record_extractor/*.py",
  "tools/conformance-evaluation-check.py",
  "tools/check-workflow-action.py",
  "tools/self-improvement-check.py",
  "learning/workflow/schemas/*.schema.json",
  "analysis/**",
  "evaluation/**",
  "templates/specs/spec.json.template",
  "templates/hooks/session-record-capture-previous.sh.template",
}

REQUIRED_EXCLUDES = {
  ".reviewcompass/post-write-verification/**",
  ".reviewcompass/effective-prompts/**",
  ".reviewcompass/approvals/**",
  ".reviewcompass/specs/*/reviews/**",
  ".reviewcompass/specs/*/conformance/**",
  ".reviewcompass/evidence/**",
  ".reviewcompass/runtime/**",
  "docs/notes/**",
  "tools/experiments/**",
  "tools/**/tests/**",
  "tests/**",
  "learning/workflow/carry-forward-register/sources/**",
  "learning/workflow/deployment-readiness/**",
  "learning/workflow/replication-pilots/**",
}


def _load_manifest():
  assert MANIFEST_PATH.is_file(), "deploy-manifest.yaml が存在しない"
  data = yaml.safe_load(MANIFEST_PATH.read_text(encoding="utf-8"))
  assert isinstance(data, dict)
  return data


def _repo_files():
  return [
    str(path.relative_to(REPO_ROOT))
    for path in REPO_ROOT.rglob("*")
    if path.is_file() and ".git" not in path.parts
  ]


def _matches(pattern, paths):
  if any(ch in pattern for ch in "*?["):
    return [path for path in paths if fnmatch(path, pattern)]
  return [pattern] if (REPO_ROOT / pattern).is_file() else []


def test_manifest_declares_initial_self_test_distribution():
  manifest = _load_manifest()
  assert manifest["name"] == "reviewcompass-initial-self-test"
  assert manifest["version"] == 1
  assert manifest["distribution_type"] == "initial_self_test"


def test_manifest_contains_required_allowlist_and_excludes():
  manifest = _load_manifest()
  includes = {entry["path"] for entry in manifest["include"]}
  excludes = {entry["path"] for entry in manifest["exclude"]}

  assert REQUIRED_ALLOWLIST.issubset(includes)
  assert REQUIRED_EXCLUDES.issubset(excludes)


def test_manifest_include_patterns_resolve_to_files():
  manifest = _load_manifest()
  repo_files = _repo_files()
  unresolved = [
    entry["path"]
    for entry in manifest["include"]
    if not _matches(entry["path"], repo_files)
  ]
  assert unresolved == []


def test_manifest_excludes_do_not_overlap_literal_includes():
  manifest = _load_manifest()
  excludes = [entry["path"] for entry in manifest["exclude"]]
  literal_includes = [
    entry["path"]
    for entry in manifest["include"]
    if not any(ch in entry["path"] for ch in "*?[")
  ]

  overlaps = [
    include
    for include in literal_includes
    for exclude in excludes
    if fnmatch(include, exclude)
  ]
  assert overlaps == []
