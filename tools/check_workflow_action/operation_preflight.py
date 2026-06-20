"""Read-only operation preflight for workflow-management Requirement 12."""

import json
import re
import subprocess
import sys
from pathlib import Path

from .operation_registry import (
  find_operation,
  load_registry,
  validate_operation,
)


ALLOWED_VERDICTS = ["OK", "WARN", "DEVIATION"]
ALLOWED_SEQUENCE_MODES = ["parallel_ok", "serial_only"]
EXIT_CODE_CONTRACT = {
  "OK": 0,
  "WARN": 1,
  "DEVIATION": 2,
}

NEXT_DIMENSION_KEYS = [
  "current_mainline",
  "required_action",
  "phase",
  "stage",
  "reopen_scope",
  "impact_review_scope",
  "direct_features",
  "indirect_features",
  "flag_policy",
  "next_pending_gate",
  "next_drafting_gate",
  "pending_gates",
  "completed_gates",
  "superseded_gates",
  "state_files",
]


def _repo_root():
  return Path(__file__).resolve().parents[2]


def _script_path():
  return Path(__file__).resolve().parents[1] / "check-workflow-action.py"


def _entrypoint_path(cwd, entrypoint):
  if not isinstance(entrypoint, str) or not entrypoint:
    return None
  path = Path(entrypoint)
  if path.is_absolute():
    return path
  cwd_path = Path(cwd) / path
  if cwd_path.is_file():
    return cwd_path
  repo_path = _repo_root() / path
  if repo_path.is_file():
    return repo_path
  return cwd_path


def _python_executable(cwd):
  for candidate in [
    Path(cwd) / ".venv" / "bin" / "python3",
    _repo_root() / ".venv" / "bin" / "python3",
  ]:
    if candidate.is_file():
      return str(candidate)
  return sys.executable


def _run_next(cwd):
  result = subprocess.run(
    [sys.executable, str(_script_path()), "next", "--json"],
    cwd=str(cwd),
    capture_output=True,
    text=True,
    timeout=30,
  )
  if result.returncode not in (0, 1, 2):
    return None, [result.stderr or "next --json の実行に失敗しました"]
  try:
    return json.loads(result.stdout), []
  except json.JSONDecodeError:
    return None, ["next --json の出力を JSON として読めません"]


def _adapt_next_action(next_data):
  action = (next_data or {}).get("next_action")
  if not isinstance(action, dict):
    return None
  phase = action.get("phase")
  stage = action.get("stage")
  pending_gate = action.get("next_pending_gate")
  if not isinstance(pending_gate, str):
    pending_gates = action.get("pending_gates")
    if isinstance(pending_gates, list) and pending_gates:
      pending_gate = pending_gates[0]
  if (phase is None or stage is None) and isinstance(pending_gate, str):
    phase_stage = _phase_stage_from_gate(pending_gate)
    phase = phase or phase_stage.get("phase")
    stage = stage or phase_stage.get("stage")
  return {
    "current_mainline": action.get("kind"),
    "required_action": action.get("required_action"),
    "phase": phase,
    "stage": stage,
    "reopen_scope": list(action.get("direct_features") or []),
    "impact_review_scope": list(action.get("required_feature_scope") or action.get("feature") or []),
    "direct_features": list(action.get("direct_features") or []),
    "indirect_features": list(action.get("indirect_features") or []),
    "flag_policy": {
      "feature_impact_scope_basis": action.get("feature_impact_scope_basis"),
    },
    "next_pending_gate": action.get("next_pending_gate"),
    "next_drafting_gate": action.get("next_drafting_gate"),
    "pending_gates": list(action.get("pending_gates") or []),
    "completed_gates": list(action.get("completed_steps") or []),
    "superseded_gates": [
      step for step in list(action.get("completed_steps") or [])
      if "superseded" in step
    ],
    "state_files": [action["file"]] if action.get("file") else [],
  }


def _phase_stage_from_gate(gate):
  prefix = "stages/"
  suffix = gate
  if suffix.startswith(prefix):
    suffix = suffix[len(prefix):]
  if "#" not in suffix:
    return {"phase": None, "stage": None}
  phase_part, stage = suffix.split("#", 1)
  if phase_part.endswith(".yaml"):
    phase_part = phase_part[:-len(".yaml")]
  return {
    "phase": phase_part or None,
    "stage": stage or None,
  }


def _extract_help_options(cwd, entrypoint, subcommand):
  entrypoint_path = _entrypoint_path(cwd, entrypoint)
  if entrypoint_path is None or not entrypoint_path.is_file():
    return None, [f"entrypoint が存在しません: {entrypoint}"]
  cmd = [_python_executable(cwd), str(entrypoint_path)]
  if subcommand is not None:
    cmd.append(str(subcommand))
  cmd.append("--help")
  result = subprocess.run(
    cmd,
    cwd=str(cwd),
    capture_output=True,
    text=True,
    timeout=30,
  )
  if result.returncode != 0:
    detail = (result.stderr or result.stdout or "").strip().splitlines()
    suffix = f": {detail[-1]}" if detail else ""
    return None, [f"parser help を取得できません: {entrypoint} {subcommand}{suffix}"]
  text = result.stdout + "\n" + result.stderr
  return set(re.findall(r"(?<![\\w-])--[A-Za-z0-9][A-Za-z0-9-]*", text)), []


def _check_parser_invocation(operation, cwd, _next_action):
  invocation = operation.get("canonical_invocation") or {}
  entrypoint = invocation.get("entrypoint")
  subcommand = invocation.get("subcommand")
  options = invocation.get("options") or []
  allowed, reasons = _extract_help_options(cwd, entrypoint, subcommand)
  if reasons:
    return reasons
  for option in options:
    if option not in allowed:
      reasons.append(f"canonical_invocation option が parser help と一致しません: {option}")
  return reasons


def _check_workflow_binding(operation, _cwd, next_action):
  reasons = []
  binding = operation.get("workflow_binding") or {}
  if not binding or next_action is None:
    return reasons
  for key in ["phase", "stage"]:
    expected = binding.get(key)
    actual = next_action.get(key)
    if expected is not None and actual is not None and expected != actual:
      reasons.append(f"workflow_binding.{key} が next --json と矛盾しています: {expected} != {actual}")
  expected_kind = binding.get("next_action_kind")
  if expected_kind is not None and next_action.get("current_mainline") != expected_kind:
    reasons.append(
      "workflow_binding.next_action_kind が next --json と矛盾しています: "
      f"{expected_kind} != {next_action.get('current_mainline')}"
    )
  return reasons


def _check_next_active_state_dimensions(_operation, _cwd, next_action):
  reasons = []
  if next_action is None:
    return ["state_refs.next_action が取得できません"]
  missing = [key for key in NEXT_DIMENSION_KEYS if key not in next_action]
  if missing:
    reasons.append("state_refs.next_action の必須キーが欠落しています: " + ", ".join(missing))
  return reasons


def _check_scope_consistency(_operation, _cwd, next_action):
  if next_action is None:
    return []
  direct = set(next_action.get("direct_features") or [])
  impact = set(next_action.get("impact_review_scope") or [])
  if direct and impact and not direct.issubset(impact):
    return ["direct_features が impact_review_scope に含まれていません"]
  return []


def _deployment_path_reasons(cwd, operation):
  reasons = []
  for output in operation.get("planned_outputs") or []:
    path = Path(str(output))
    if path.is_absolute():
      reasons.append(
        "deployment/export の planned_outputs は明示された external output root "
        f"なしに絶対パスを探索できません: {output}"
      )
      continue
    if ".." in path.parts:
      reasons.append(f"deployment/export の planned_outputs に traversal が含まれています: {output}")
      continue
    resolved = (Path(cwd) / path).resolve()
    try:
      resolved.relative_to(Path(cwd).resolve())
    except ValueError:
      reasons.append(f"deployment/export の planned_outputs が作業 root 外を指しています: {output}")
  return reasons


def _check_planned_outputs(operation, cwd, _next_action):
  if not operation.get("planned_outputs"):
    return ["planned_outputs が空です"]
  if operation.get("operation_family") == "deployment_export":
    return _deployment_path_reasons(cwd, operation)
  return []


def _check_overwrite_policy(operation, _cwd, _next_action):
  if not operation.get("artifact_policy"):
    return ["artifact_policy がありません"]
  return []


def _check_external_output_root(operation, cwd, _next_action):
  if operation.get("operation_family") != "deployment_export":
    return []
  return _deployment_path_reasons(cwd, operation)


def _check_target_app_root(operation, _cwd, _next_action):
  required_inputs = set(operation.get("required_inputs") or [])
  options = set((operation.get("canonical_invocation") or {}).get("options") or [])
  if "target_app_root" in required_inputs or "--target-app-root" in options or "--smoke-external-app-root" in options:
    return []
  return ["target_app_root の入力または option が宣言されていません"]


def _check_required_input_contains(operation, name, aliases):
  values = set(operation.get("required_inputs") or [])
  if any(alias in values for alias in aliases):
    return []
  return [f"{name} に必要な required_inputs がありません"]


def _check_target_manifest_alignment(operation, _cwd, _next_action):
  return _check_required_input_contains(operation, "target_manifest_alignment", {"target-manifest.yaml", "target_manifest"})


def _check_bundle_non_empty(operation, _cwd, _next_action):
  if operation.get("target_identity") or operation.get("planned_outputs"):
    return []
  return ["target_identity または planned_outputs が空です"]


def _check_criteria_alignment(operation, _cwd, _next_action):
  options = set((operation.get("canonical_invocation") or {}).get("options") or [])
  if "--criteria" in options:
    return []
  return ["canonical_invocation に --criteria がありません"]


def _check_document_type_alignment(operation, _cwd, _next_action):
  if operation.get("kind") == "review_artifact" and operation.get("operation_family") == "review_artifact":
    return []
  return ["review artifact の kind / operation_family が一致していません"]


def _check_approval_record_alignment(operation, _cwd, _next_action):
  options = set((operation.get("canonical_invocation") or {}).get("options") or [])
  if "--approval-record" in options or operation.get("operation_id") == "review_run_create":
    return []
  return ["approval record の option または免除条件がありません"]


def _check_existing_artifact_drift(operation, _cwd, _next_action):
  if operation.get("artifact_policy"):
    return []
  return ["artifact_policy がありません"]


def _check_staged_vs_unstaged_target_selection(operation, _cwd, _next_action):
  if operation.get("worktree_policy"):
    return []
  return ["worktree_policy がありません"]


def _input_value(operation, name):
  prefix = f"{name}="
  for value in operation.get("required_inputs") or []:
    if isinstance(value, str) and value.startswith(prefix):
      return value[len(prefix):]
  return None


def _looks_like_repo_file_input(value):
  if not isinstance(value, str) or not value:
    return False
  if "=" in value or "{" in value or "}" in value:
    return False
  if value.startswith("--"):
    return False
  if "/" in value:
    return True
  return Path(value).suffix in (".json", ".yaml", ".yml", ".md", ".txt")


def _missing_required_inputs(operation, cwd):
  missing = []
  for value in operation.get("required_inputs") or []:
    if not _looks_like_repo_file_input(value):
      continue
    path = Path(value)
    if path.is_absolute():
      missing.append(value)
      continue
    if not (Path(cwd) / path).exists():
      missing.append(value)
  return missing


def _check_required_inputs(operation, names):
  required_inputs = set(operation.get("required_inputs") or [])
  target_identity = set(operation.get("target_identity") or [])
  declared = required_inputs | target_identity
  missing = [
    name for name in names
    if name not in declared and _input_value(operation, name) is None
  ]
  if missing:
    return ["必須入力宣言が不足しています: " + ", ".join(missing)]
  return []


def _make_required_inputs_check(*names):
  def _check(operation, _cwd, _next_action):
    return _check_required_inputs(operation, names)
  return _check


def _check_current_session_formal_output_forbidden(operation, _cwd, _next_action):
  mode = _input_value(operation, "session_record_mode")
  current = _input_value(operation, "current_session_id")
  target = _input_value(operation, "target_session_id")
  if mode != "formal":
    return []
  if not current or not target:
    return ["formal session record は current_session_id と target_session_id が必要です"]
  if current == target:
    return ["formal session record は current session を対象にできません"]
  return []


CHECK_EXECUTORS = {
  "parser_invocation": _check_parser_invocation,
  "workflow_binding": _check_workflow_binding,
  "next_active_state_dimensions": _check_next_active_state_dimensions,
  "scope_consistency": _check_scope_consistency,
  "target_manifest_alignment": _check_target_manifest_alignment,
  "bundle_non_empty": _check_bundle_non_empty,
  "criteria_alignment": _check_criteria_alignment,
  "document-type_alignment": _check_document_type_alignment,
  "approval_record_alignment": _check_approval_record_alignment,
  "existing_artifact_drift": _check_existing_artifact_drift,
  "staged-vs-unstaged_target_selection": _check_staged_vs_unstaged_target_selection,
  "planned_outputs": _check_planned_outputs,
  "overwrite_policy": _check_overwrite_policy,
  "external_output_root": _check_external_output_root,
  "target_app_root": _check_target_app_root,
  "nonce": _make_required_inputs_check("nonce"),
  "target_digest": _make_required_inputs_check("target_digest"),
  "staged_file_set_digest": _make_required_inputs_check("staged_file_set"),
  "staged_content_approval_digest": _make_required_inputs_check("target_digest"),
  "expiry": _make_required_inputs_check("expiry"),
  "consume": _make_required_inputs_check("consume"),
  "invalidated": _make_required_inputs_check("invalidated"),
  "target": _make_required_inputs_check("target_digest"),
  "session_record_mode": _make_required_inputs_check("session_record_mode"),
  "current_session_id": _make_required_inputs_check("current_session_id"),
  "target_session_id": _make_required_inputs_check("target_session_id"),
  "current_session_formal_output_forbidden": _check_current_session_formal_output_forbidden,
  "parent_task": _make_required_inputs_check("parent_task"),
  "discovered_issue": _make_required_inputs_check("discovered_issue"),
  "relation": _make_required_inputs_check("relation"),
  "allowed_files": _make_required_inputs_check("allowed_files"),
  "return_condition": _make_required_inputs_check("return_condition"),
  "nesting_depth": _make_required_inputs_check("return_condition"),
}


def _run_family_checks(operation, cwd, next_action):
  checks = []
  for check_name in operation.get("family_required_checks") or []:
    executor = CHECK_EXECUTORS.get(check_name)
    if executor is None:
      checks.append({
        "name": check_name,
        "status": "not_implemented",
        "reasons": [f"family_required_check executor が未実装です: {check_name}"],
      })
      continue
    reasons = executor(operation, cwd, next_action)
    checks.append({
      "name": check_name,
      "status": "failed" if reasons else "ok",
      "reasons": reasons,
    })
  return checks


def _flatten_check_reasons(checks):
  reasons = []
  for check in checks:
    if check.get("status") in ("failed", "not_implemented"):
      reasons.extend(check.get("reasons") or [])
  return reasons


def _session_state_refs(operation):
  return {
    "current_session_id": _input_value(operation or {}, "current_session_id"),
    "target_session_id": _input_value(operation or {}, "target_session_id"),
    "session_record_mode": _input_value(operation or {}, "session_record_mode"),
  }


def _build_response(
  operation_id,
  operation=None,
  verdict="DEVIATION",
  reasons=None,
  next_action=None,
  checks=None,
  missing_inputs=None,
):
  reasons = list(reasons or [])
  checks = list(checks or [])
  if reasons:
    checks.insert(0, {"name": "registry_schema", "status": "failed", "reasons": reasons})
  response_reasons = reasons + _flatten_check_reasons(checks)
  sequence_mode = (operation or {}).get("sequence_mode")
  session_refs = _session_state_refs(operation)
  return {
    "schema_version": "operation-preflight-v1",
    "operation_id": operation_id,
    "verdict": verdict,
    "allowed_verdicts": ALLOWED_VERDICTS,
    "exit_code_contract": dict(EXIT_CODE_CONTRACT),
    "sequence_mode": sequence_mode,
    "allowed_sequence_modes": ALLOWED_SEQUENCE_MODES,
    "state_refs": {
      "next_action": next_action,
      "current_session_id": session_refs["current_session_id"],
      "target_session_id": session_refs["target_session_id"],
      "session_record_mode": session_refs["session_record_mode"],
      "workflow_state_files": next_action.get("state_files") if isinstance(next_action, dict) else [],
      "git_index": None,
    },
    "required_inputs": list((operation or {}).get("required_inputs") or []),
    "missing_inputs": list(missing_inputs or []),
    "template_available": False,
    "target_identity": list((operation or {}).get("target_identity") or []),
    "worktree_state": {},
    "pending_conflicts": [],
    "integrity_conflicts": [],
    "checks": checks or [{"name": "operation", "status": "ok", "reasons": []}],
    "planned_outputs": list((operation or {}).get("planned_outputs") or []),
    "canonical_commands": [],
    "next_step": "stop" if verdict == "DEVIATION" else "proceed",
    "reasons": response_reasons,
  }


def run_preflight(cwd, operation_id):
  registry, registry_errors = load_registry(cwd)
  if registry_errors:
    return _build_response(operation_id, verdict="DEVIATION", reasons=registry_errors)

  operation = find_operation(registry, operation_id)
  if operation is None:
    return _build_response(operation_id, verdict="DEVIATION", reasons=[f"operation_id が未登録です: {operation_id}"])

  validation_reasons = []
  validation_reasons.extend(validate_operation(operation))
  missing_inputs = _missing_required_inputs(operation, cwd)
  if missing_inputs:
    validation_reasons.append("必須入力が欠落しています: " + ", ".join(missing_inputs))

  next_data = None
  next_action = None
  if operation.get("operation_family") == "workflow_cli" or (operation.get("workflow_binding") or {}).get("phase"):
    next_data, next_errors = _run_next(cwd)
    validation_reasons.extend(next_errors)
    next_action = _adapt_next_action(next_data)

  checks = _run_family_checks(operation, cwd, next_action)
  check_reasons = _flatten_check_reasons(checks)

  verdict = "DEVIATION" if validation_reasons or check_reasons else "OK"
  return _build_response(
    operation_id,
    operation=operation,
    verdict=verdict,
    reasons=validation_reasons,
    next_action=next_action,
    checks=checks,
    missing_inputs=missing_inputs,
  )
