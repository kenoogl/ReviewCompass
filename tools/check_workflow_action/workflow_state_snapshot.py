"""Workflow state snapshot helpers for workflow-management T-017."""

import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import yaml

from .side_track_stack import DEFAULT_SIDE_TRACK_STACK_PATH, current as current_side_track_stack


def _json_digest(value):
  payload = json.dumps(
    value,
    ensure_ascii=False,
    sort_keys=True,
    separators=(",", ":"),
  ).encode("utf-8")
  return "sha256:" + hashlib.sha256(payload).hexdigest()


def _read_yaml(path, default):
  try:
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
  except (OSError, UnicodeDecodeError, yaml.YAMLError):
    return default
  return default if data is None else data


def _read_json(path, default):
  try:
    return json.loads(Path(path).read_text(encoding="utf-8"))
  except (OSError, UnicodeDecodeError, json.JSONDecodeError):
    return default


def _run_git(cwd, args):
  return subprocess.run(
    ["git"] + args,
    cwd=str(cwd),
    capture_output=True,
    text=True,
  )


def _git_tree_summary(cwd):
  staged = []
  dirty = []
  status = _run_git(cwd, ["status", "--porcelain=v1"])
  if status.returncode == 0:
    for line in status.stdout.splitlines():
      if len(line) < 4:
        continue
      index_status = line[0]
      worktree_status = line[1]
      path = line[3:]
      if index_status not in (" ", "?"):
        staged.append(path)
      if worktree_status != " " or index_status == "?":
        dirty.append(path)

  return {
    "staged_paths": sorted(staged),
    "dirty_paths": sorted(dirty),
    "staged_file_set_digest": _json_digest(sorted(staged)),
    "worktree_dirty_path_digest": _json_digest(sorted(dirty)),
  }


def _load_specs(cwd):
  spec_paths = sorted((Path(cwd) / ".reviewcompass" / "specs").glob("*/spec.json"))
  specs = {}
  for path in spec_paths:
    specs[path.parent.name] = _read_json(path, {})
  return specs


def _select_current_work(specs):
  for feature, spec in specs.items():
    workflow_state = spec.get("workflow_state") if isinstance(spec, dict) else None
    if not isinstance(workflow_state, dict):
      continue
    for phase, stages in workflow_state.items():
      if not isinstance(stages, dict):
        continue
      for stage, completed in stages.items():
        if completed is False:
          return {
            "required_action": "run_workflow_stage",
            "title": f"{feature} {phase}.{stage}",
            "outer_node": {
              "kind": "workflow",
              "feature": feature,
              "phase": phase,
            },
            "inner_node": {
              "stage": stage,
            },
            "active_gate": f"{feature}:{phase}#{stage}",
          }
  return {
    "required_action": None,
    "title": "completed",
    "outer_node": {
      "kind": "workflow",
    },
    "inner_node": {},
    "active_gate": None,
  }


def _in_progress_summary(cwd):
  files = sorted((Path(cwd) / "stages" / "in-progress").glob("*.yaml"))
  pending_gates = []
  completed_gates = []
  drafting_completed_gates = []
  summaries = []
  for path in files:
    data = _read_yaml(path, {})
    relative = str(path.relative_to(cwd)) if path.is_relative_to(cwd) else str(path)
    summaries.append(relative)
    if isinstance(data, dict):
      pending_gates.extend(data.get("pending_gates") or [])
      completed_gates.extend(data.get("completed_gates") or data.get("completed_steps") or [])
      drafting_completed_gates.extend(data.get("drafting_completed_gates") or [])
  return {
    "in_progress_files": summaries,
    "pending_gates": pending_gates,
    "completed_gates": completed_gates,
    "drafting_completed_gates": drafting_completed_gates,
  }


def _post_write_manifest_summary(cwd):
  manifests = sorted((Path(cwd) / ".reviewcompass" / "post-write-verification").glob("*.yaml"))
  latest = str(manifests[-1].relative_to(cwd)) if manifests else None
  return {
    "latest_manifest": latest,
    "manifest_count": len(manifests),
  }


def _operation_contract_summary(cwd):
  path = Path(cwd) / "stages" / "operation-contracts.yaml"
  data = _read_yaml(path, {})
  operations = data.get("operations") if isinstance(data, dict) else []
  return {
    "path": "stages/operation-contracts.yaml",
    "exists": path.exists(),
    "operation_count": len(operations) if isinstance(operations, list) else 0,
    "digest": _json_digest(data),
  }


def _workflow_state_summary(cwd, specs):
  in_progress = _in_progress_summary(cwd)
  summary = {
    "spec_json": {
      "features": sorted(specs),
      "workflow_state": {
        feature: spec.get("workflow_state")
        for feature, spec in specs.items()
        if isinstance(spec, dict)
      },
      "recheck": {
        feature: spec.get("recheck")
        for feature, spec in specs.items()
        if isinstance(spec, dict) and "recheck" in spec
      },
    },
    "in_progress_files": in_progress["in_progress_files"],
    "pending_gates": in_progress["pending_gates"],
    "drafting_completed_gates": in_progress["drafting_completed_gates"],
    "completed_gates": in_progress["completed_gates"],
    "operation_contract": _operation_contract_summary(cwd),
  }
  return summary


def build_snapshot(cwd):
  """Build a read-only snapshot of workflow state and worktree digests."""
  cwd = Path(cwd)
  specs = _load_specs(cwd)
  current_work = _select_current_work(specs)
  side_track_result = current_side_track_stack(cwd / DEFAULT_SIDE_TRACK_STACK_PATH)
  active_side_tracks = side_track_result.get("stack", {}).get("frames", [])
  git_tree_summary = _git_tree_summary(cwd)
  workflow_state_summary = _workflow_state_summary(cwd, specs)
  next_action_source = {
    "current_work": current_work,
    "workflow_state_summary": workflow_state_summary,
  }

  return {
    "schema_version": "workflow-state-snapshot-v1",
    "generated_by": "tools/check_workflow_action/workflow_state_snapshot.py",
    "generated_at": datetime.now(timezone.utc).isoformat(),
    "source_next_action_sha256": _json_digest(next_action_source),
    "current_work": current_work,
    "active_side_tracks": active_side_tracks,
    "git_tree_summary": git_tree_summary,
    "post_write_manifest_summary": _post_write_manifest_summary(cwd),
    "workflow_state_summary": workflow_state_summary,
  }


def detect_drift(
  snapshot_path,
  current_next_action,
  current_next_action_sha256,
  current_git_tree_summary,
):
  """Detect whether a stored snapshot no longer matches current selector inputs."""
  snapshot = _read_yaml(snapshot_path, {})
  reasons = []
  if not isinstance(snapshot, dict):
    return {
      "verdict": "DEVIATION",
      "reasons": ["snapshot は mapping である必要があります"],
    }

  if snapshot.get("source_next_action_sha256") != current_next_action_sha256:
    reasons.append("source_next_action_sha256 が現在の next action と一致しません")

  snapshot_pending = (
    snapshot.get("workflow_state_summary", {}).get("pending_gates")
    if isinstance(snapshot.get("workflow_state_summary"), dict)
    else None
  )
  current_pending = current_next_action.get("pending_gates") if isinstance(current_next_action, dict) else None
  if snapshot_pending is not None and current_pending is not None and snapshot_pending != current_pending:
    reasons.append("pending_gates が snapshot と現在状態で一致しません")

  snapshot_summary = (
    snapshot.get("workflow_state_summary")
    if isinstance(snapshot.get("workflow_state_summary"), dict)
    else {}
  )
  current_summary = current_next_action.get("workflow_state_summary", {})
  if not isinstance(current_summary, dict):
    current_summary = {}

  for key in ["drafting_completed_gates", "completed_gates"]:
    snapshot_value = snapshot_summary.get(key)
    current_value = current_summary.get(key)
    if current_value is None and isinstance(current_next_action, dict):
      current_value = current_next_action.get(key)
    if snapshot_value is not None and current_value is not None and snapshot_value != current_value:
      reasons.append(f"{key} が snapshot と現在状態で一致しません")

  snapshot_contract = snapshot_summary.get("operation_contract")
  current_contract = current_summary.get("operation_contract")
  if current_contract is None and isinstance(current_next_action, dict):
    current_contract = current_next_action.get("operation_contract")
  snapshot_contract_digest = (
    snapshot_contract.get("digest") if isinstance(snapshot_contract, dict) else None
  )
  current_contract_digest = (
    current_contract.get("digest") if isinstance(current_contract, dict) else None
  )
  if (
    snapshot_contract_digest is not None
    and current_contract_digest is not None
    and snapshot_contract_digest != current_contract_digest
  ):
    reasons.append("operation_contract digest が snapshot と現在状態で一致しません")

  snapshot_git = snapshot.get("git_tree_summary") if isinstance(snapshot.get("git_tree_summary"), dict) else {}
  for key in ["staged_file_set_digest", "worktree_dirty_path_digest"]:
    if key in snapshot_git and key in current_git_tree_summary:
      if snapshot_git.get(key) != current_git_tree_summary.get(key):
        reasons.append(f"{key} が snapshot と現在状態で一致しません")

  return {
    "verdict": "DEVIATION" if reasons else "OK",
    "reasons": reasons,
  }
