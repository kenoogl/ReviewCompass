"""Read-only operation registry views for workflow operations."""

from __future__ import annotations

from pathlib import Path
import shlex
from typing import Any, Dict, List, Tuple

from .operation_contracts import load_contracts


OPERATION_REGISTRY_SCHEMA_VERSION = "operation-registry-schema-v1"
OPERATION_REGISTRY_REQUIRED_FIELDS = [
  "operation_id",
  "kind",
  "canonical_commands",
  "required_args",
  "outputs",
  "serial_only",
  "conflicting_states",
]

CORE_OPERATION_INVENTORY = [
  {
    "operation_id": "commit",
    "kind": "repository_mutation",
    "canonical_commands": [
      "tools/commit-from-current-staged.py",
    ],
    "required_args": ["message", "rationale"],
    "outputs": ["git_commit"],
    "serial_only": True,
    "conflicting_states": ["post_write_verification", "reopen_in_progress"],
  },
  {
    "operation_id": "push",
    "kind": "remote_mutation",
    "canonical_commands": [
      "tools/check-workflow-action.py push --rationale <reason>",
    ],
    "required_args": ["rationale"],
    "outputs": ["remote_ref_update"],
    "serial_only": True,
    "conflicting_states": ["uncommitted_changes"],
  },
  {
    "operation_id": "post-write-manifest",
    "kind": "verification_artifact",
    "canonical_commands": [
      "tools/api_providers/review_triage.py write-manifest --review-run-dir <dir>",
      "tools/make-post-write-manifest.py --review-run-dir <dir>",
    ],
    "required_args": ["review-run-dir"],
    "outputs": [".reviewcompass/post-write-verification/*.yaml"],
    "serial_only": True,
    "conflicting_states": ["target_manifest_mismatch"],
  },
  {
    "operation_id": "review-run",
    "kind": "external_review",
    "canonical_commands": [
      "tools/api_providers/run_review.py --review-run-dir <dir>",
    ],
    "required_args": ["review-run-dir", "target", "phase"],
    "outputs": ["raw/", "parsed/", "rounds.yaml", "model-result-summary.yaml"],
    "serial_only": True,
    "conflicting_states": ["existing_review_run_dir"],
  },
  {
    "operation_id": "reopen",
    "kind": "workflow_state",
    "canonical_commands": [
      "tools/check-workflow-action.py reopen-start --json",
      "tools/check-workflow-action.py reopen-advance-step --json",
      "tools/check-workflow-action.py reopen-finalize --json",
    ],
    "required_args": ["file", "rationale"],
    "outputs": ["stages/in-progress/reopen-*.yaml", "stages/completed/reopen-*.yaml"],
    "serial_only": True,
    "conflicting_states": ["another_reopen_in_progress"],
  },
  {
    "operation_id": "session-record",
    "kind": "session_evidence",
    "canonical_commands": [
      "tools/session-record-draft.py",
      "tools/session-record-promote-draft.py",
      "tools/session-record-capture-previous-codex.py",
    ],
    "required_args": ["session"],
    "outputs": [".reviewcompass/evidence/sessions/*.md", "docs/sessions/*.md"],
    "serial_only": False,
    "conflicting_states": ["duplicate_session_record"],
  },
]


def build_operation_list(cwd: str | Path) -> Dict[str, Any]:
  """operation contracts を read-only registry 表示へ整形する。"""
  contracts, _raw, reasons = load_contracts(Path(cwd))
  operations: List[Dict[str, Any]] = []
  for contract in contracts.values():
    operations.append(_operation_entry(contract))
  verdict = "OK" if not reasons else "DEVIATION"
  return {
    "verdict": verdict,
    "exit_code": 0 if verdict == "OK" else 2,
    "operation_mode": "read_only",
    "operations": sorted(operations, key=lambda item: item["operation_id"]),
    "reasons": reasons,
  }


def build_operation_registry_schema(cwd: str | Path) -> Dict[str, Any]:
  """Return the read-only schema contract for operation registry entries."""
  _ = Path(cwd)
  return {
    "verdict": "OK",
    "exit_code": 0,
    "operation_mode": "read_only",
    "schema_version": OPERATION_REGISTRY_SCHEMA_VERSION,
    "registry_contract": {
      "required_fields": OPERATION_REGISTRY_REQUIRED_FIELDS,
      "inventory_contract": {
        "consumer": "operation-registry-inventory",
        "required_schema_version": OPERATION_REGISTRY_SCHEMA_VERSION,
        "operation_id_policy": "stable-user-operation-id",
      },
      "validation_contract": {
        "consumer": "operation-registry-validate",
        "missing_command_path_verdict": "DEVIATION",
        "operation_mode": "read_only",
      },
    },
    "reasons": [],
  }


def build_operation_registry_inventory(cwd: str | Path) -> Dict[str, Any]:
  """Return core operation command inventory without executing operations."""
  root = Path(cwd)
  operations = [_inventory_entry(item) for item in CORE_OPERATION_INVENTORY]
  findings = _validate_operation_entries(root, operations)
  verdict = "DEVIATION" if findings else "OK"
  return {
    "verdict": verdict,
    "exit_code": 0 if verdict == "OK" else 2,
    "operation_mode": "read_only",
    "schema_version": OPERATION_REGISTRY_SCHEMA_VERSION,
    "operations": operations,
    "findings": findings,
    "reasons": [finding["message"] for finding in findings],
  }


def validate_operation_registry(
  cwd: str | Path,
  registry_file: str | Path | None = None,
) -> Dict[str, Any]:
  """Validate operation registry command paths without running commands."""
  root = Path(cwd)
  if registry_file is None:
    operations = [_inventory_entry(item) for item in CORE_OPERATION_INVENTORY]
    registry_path = None
    load_reasons: List[str] = []
  else:
    registry_path = Path(registry_file)
    if not registry_path.is_absolute():
      registry_path = root / registry_path
    operations, load_reasons = _load_registry_operations(registry_path)
  findings = []
  for reason in load_reasons:
    findings.append({
      "kind": "registry_load_error",
      "severity": "DEVIATION",
      "operation_id": None,
      "message": reason,
    })
  findings.extend(_validate_operation_entries(root, operations))
  verdict = "DEVIATION" if findings else "OK"
  return {
    "verdict": verdict,
    "exit_code": 0 if verdict == "OK" else 2,
    "operation_mode": "read_only",
    "schema_version": OPERATION_REGISTRY_SCHEMA_VERSION,
    "registry_file": str(registry_path) if registry_path is not None else None,
    "operation_count": len(operations),
    "findings": findings,
    "reasons": [finding["message"] for finding in findings],
  }


def build_serial_runner_plan(cwd: str | Path, operation_id: str) -> Dict[str, Any]:
  """Return a read-only execution plan for serial-only operations."""
  _ = Path(cwd)
  operation = _core_operation_by_id(operation_id)
  if operation is None:
    reason = f"{operation_id}: operation registry に存在しません"
    return {
      "verdict": "DEVIATION",
      "exit_code": 2,
      "operation_mode": "read_only",
      "operation_id": operation_id,
      "sequence_mode": None,
      "steps": [],
      "checkpoints": [],
      "findings": [{
        "kind": "unknown_operation",
        "severity": "DEVIATION",
        "operation_id": operation_id,
        "message": reason,
      }],
      "reasons": [reason],
      "next_step": "stop",
    }
  if not operation.get("serial_only"):
    reason = f"{operation_id}: serial_only operation ではないため parallel 対象から除外して停止します"
    return {
      "verdict": "DEVIATION",
      "exit_code": 2,
      "operation_mode": "read_only",
      "operation_id": operation_id,
      "sequence_mode": "parallel_ok",
      "steps": [],
      "checkpoints": [],
      "findings": [{
        "kind": "serial_only_required",
        "severity": "DEVIATION",
        "operation_id": operation_id,
        "message": reason,
      }],
      "reasons": [reason],
      "next_step": "stop",
    }
  if operation_id == "commit":
    return _commit_serial_runner_plan(operation_id)
  return _generic_serial_runner_plan(operation)


def _operation_entry(contract: Dict[str, Any]) -> Dict[str, Any]:
  return {
    "operation_id": contract.get("operation_id"),
    "canonical_commands": _canonical_commands(contract.get("canonical_invocation")),
    "effect_kind": contract.get("effect_kind"),
    "approval_required": contract.get("approval_required"),
    "sequence": contract.get("sequence"),
    "pending_conflicts": [],
    "pending_conflicts_status": "none_detected",
  }


def _core_operation_by_id(operation_id: str) -> Dict[str, Any] | None:
  for operation in CORE_OPERATION_INVENTORY:
    if operation["operation_id"] == operation_id:
      return operation
  return None


def _commit_serial_runner_plan(operation_id: str) -> Dict[str, Any]:
  return {
    "verdict": "OK",
    "exit_code": 0,
    "operation_mode": "read_only",
    "operation_id": operation_id,
    "sequence_mode": "serial_only",
    "steps": [
      _plan_step(
        "commit-preflight",
        ".venv/bin/python3 tools/check-workflow-action.py commit-preflight --json",
        "read-only commit preflight",
      ),
      _plan_step(
        "approval-input",
        "TTY user approval line",
        "stop for user-provided approval relay",
      ),
      _plan_step(
        "guarded-commit",
        ".venv/bin/python3 tools/commit-from-current-staged.py",
        "guarded commit through standard runner",
      ),
      _plan_step(
        "postcondition-check",
        "git status --short --branch",
        "confirm commit result and repository state",
      ),
    ],
    "checkpoints": [
      _checkpoint("nonce", "commit approval nonce exists and matches staged target"),
      _checkpoint("ttl", "commit approval challenge has not expired"),
      _checkpoint("consumed", "approval and delegation are not already consumed"),
      _checkpoint("target_digest", "approval target digest matches staged content"),
      _checkpoint("staged_file_set_digest", "delegation staged file set digest matches"),
      _checkpoint("staged_content_approval_digest", "delegation content digest matches"),
    ],
    "findings": [],
    "reasons": [],
    "next_step": "stop_for_user_approval",
  }


def _generic_serial_runner_plan(operation: Dict[str, Any]) -> Dict[str, Any]:
  operation_id = operation["operation_id"]
  return {
    "verdict": "OK",
    "exit_code": 0,
    "operation_mode": "read_only",
    "operation_id": operation_id,
    "sequence_mode": "serial_only",
    "steps": [
      _plan_step(
        "operation-preflight",
        f".venv/bin/python3 tools/check-workflow-action.py operation-preflight --operation-id {operation_id} --json",
        "read-only operation preflight",
      ),
      _plan_step(
        "canonical-command",
        operation["canonical_commands"][0],
        "standard operation command",
      ),
      _plan_step(
        "postcondition-check",
        "git status --short --branch",
        "confirm operation result and repository state",
      ),
    ],
    "checkpoints": [],
    "findings": [],
    "reasons": [],
    "next_step": "stop_for_user_approval",
  }


def _plan_step(step_id: str, command: str, purpose: str) -> Dict[str, Any]:
  return {
    "id": step_id,
    "command": command,
    "purpose": purpose,
    "execution_mode": "not_executed",
  }


def _checkpoint(checkpoint_id: str, description: str) -> Dict[str, Any]:
  return {
    "id": checkpoint_id,
    "description": description,
    "execution_mode": "not_executed",
  }


def _canonical_commands(invocation: Any) -> List[str]:
  if not isinstance(invocation, dict):
    return []
  entrypoint = invocation.get("entrypoint")
  if not entrypoint:
    return []
  parts = [str(entrypoint)]
  subcommand = invocation.get("subcommand")
  if subcommand:
    parts.append(str(subcommand))
  options = invocation.get("options")
  if isinstance(options, list):
    parts.extend(str(option) for option in options)
  return [" ".join(parts)]


def _inventory_entry(item: Dict[str, Any]) -> Dict[str, Any]:
  return {
    "operation_id": item["operation_id"],
    "kind": item["kind"],
    "canonical_commands": list(item["canonical_commands"]),
    "required_args": list(item["required_args"]),
    "outputs": list(item["outputs"]),
    "serial_only": bool(item["serial_only"]),
    "conflicting_states": list(item["conflicting_states"]),
  }


def _load_registry_operations(path: Path) -> Tuple[List[Dict[str, Any]], List[str]]:
  try:
    import yaml

    data = yaml.safe_load(path.read_text(encoding="utf-8"))
  except (OSError, UnicodeDecodeError, yaml.YAMLError) as exc:
    return [], [f"operation registry を読めません: {path}: {exc}"]
  if not isinstance(data, dict):
    return [], [f"operation registry の最上位は mapping である必要があります: {path}"]
  operations = data.get("operations")
  if not isinstance(operations, list):
    return [], [f"operation registry の operations は list である必要があります: {path}"]
  return [item for item in operations if isinstance(item, dict)], []


def _validate_operation_entries(root: Path, operations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
  findings: List[Dict[str, Any]] = []
  for operation in operations:
    operation_id = operation.get("operation_id")
    for field in OPERATION_REGISTRY_REQUIRED_FIELDS:
      if field not in operation:
        findings.append({
          "kind": "missing_required_field",
          "severity": "DEVIATION",
          "operation_id": operation_id,
          "field": field,
          "message": f"{operation_id}: required field が欠落しています: {field}",
        })
    commands = operation.get("canonical_commands")
    if not isinstance(commands, list):
      continue
    for command in commands:
      entrypoint = _command_entrypoint(command)
      if not entrypoint or not _is_repo_relative_entrypoint(entrypoint):
        continue
      path = root / entrypoint
      if not path.exists():
        findings.append({
          "kind": "missing_command_path",
          "severity": "DEVIATION",
          "operation_id": operation_id,
          "entrypoint": entrypoint,
          "message": f"{operation_id}: canonical command path が存在しません: {entrypoint}",
        })
  return findings


def _command_entrypoint(command: Any) -> str | None:
  if isinstance(command, dict):
    entrypoint = command.get("entrypoint")
    return str(entrypoint) if entrypoint else None
  if isinstance(command, str):
    try:
      parts = shlex.split(command)
    except ValueError:
      parts = command.split()
    return parts[0] if parts else None
  return None


def _is_repo_relative_entrypoint(entrypoint: str) -> bool:
  if entrypoint.startswith("/") or entrypoint.startswith("<"):
    return False
  return "/" in entrypoint or entrypoint.endswith(".py")
