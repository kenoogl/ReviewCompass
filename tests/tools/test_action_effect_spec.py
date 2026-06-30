"""ActionEffectSpec の TDD red tests."""

import importlib.util
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "tools" / "check-workflow-action.py"


def load_module():
  tools_dir = str(REPO_ROOT / "tools")
  if tools_dir not in sys.path:
    sys.path.insert(0, tools_dir)
  spec = importlib.util.spec_from_file_location(
    "check_workflow_action_cli_action_effect_spec",
    SCRIPT,
  )
  module = importlib.util.module_from_spec(spec)
  spec.loader.exec_module(module)
  return module


def test_action_effect_spec_uses_exact_local_vocabulary():
  """ActionEffectSpec は局所語彙だけを受け付ける。"""
  module = load_module()

  assert module.ACTION_EFFECT_KIND_VALUES == [
    "read",
    "write",
    "state_mutation",
    "external_call",
    "irreversible_action",
  ]
  valid = module.validate_action_effect_spec({
    "schema_version": "action-effect-spec-v1",
    "action_id": "commit",
    "effects": [
      {"kind": "read", "target": "git_index"},
      {"kind": "irreversible_action", "target": "git_history"},
    ],
  })
  invalid = module.validate_action_effect_spec({
    "schema_version": "action-effect-spec-v1",
    "action_id": "commit",
    "effects": [
      {"kind": "network", "target": "origin"},
    ],
  })

  assert valid["verdict"] == "OK"
  assert invalid["verdict"] == "DEVIATION"
  assert "unknown effect kind: network" in invalid["reasons"]


def test_core_workflow_actions_expose_action_effect_specs():
  """next、commit、push、reopen-start は実行前 effect spec を返せる。"""
  module = load_module()

  specs = {
    action_id: module.build_workflow_action_effect_spec(action_id)
    for action_id in ["next", "commit", "push", "reopen-start"]
  }

  assert specs["next"]["schema_version"] == "action-effect-spec-v1"
  assert specs["next"]["action_id"] == "next"
  assert [effect["kind"] for effect in specs["next"]["effects"]] == ["read"]

  commit_kinds = [effect["kind"] for effect in specs["commit"]["effects"]]
  assert "read" in commit_kinds
  assert "write" in commit_kinds
  assert "state_mutation" in commit_kinds
  assert "irreversible_action" in commit_kinds
  assert ".git" in specs["commit"]["write_scope"]

  push_kinds = [effect["kind"] for effect in specs["push"]["effects"]]
  assert "external_call" in push_kinds
  assert "irreversible_action" in push_kinds

  reopen_kinds = [effect["kind"] for effect in specs["reopen-start"]["effects"]]
  assert "write" in reopen_kinds
  assert "state_mutation" in reopen_kinds
  assert "stages/in-progress/" in specs["reopen-start"]["write_scope"]


def test_commit_preflight_action_effect_scope_rejects_extra_staged_files():
  """commit preflight は effect spec 外の staged 変更を遮断できる。"""
  module = load_module()
  effect_spec = {
    "schema_version": "action-effect-spec-v1",
    "action_id": "commit",
    "effects": [
      {"kind": "write", "target": "allowed_paths"},
      {"kind": "irreversible_action", "target": "git_history"},
    ],
    "write_scope": [
      ".reviewcompass/backlog/index.yaml",
      "tools/check-workflow-action.py",
    ],
  }

  result = module.validate_commit_preflight_action_effect_scope(
    staged_files=[
      ".reviewcompass/backlog/index.yaml",
      "docs/out-of-scope.md",
    ],
    action_effect_spec=effect_spec,
  )

  assert result["verdict"] == "DEVIATION"
  assert result["extra_staged_files"] == ["docs/out-of-scope.md"]
  assert "staged file outside ActionEffectSpec write_scope: docs/out-of-scope.md" in result["reasons"]
