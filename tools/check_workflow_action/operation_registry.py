"""Operation registry loader and schema checks for workflow preflight."""

from pathlib import Path

import yaml


DEFAULT_OPERATION_REGISTRY_PATH = "stages/operation-registry.yaml"

FORBIDDEN_LLM_FIELDS = {
  "llm",
  "provider",
  "model",
  "model_id",
  "proxy_model_id",
}

VALID_KINDS = {
  "irreversible",
  "review_artifact",
  "workflow_state",
  "evidence_capture",
  "deployment_export",
}

VALID_OPERATION_FAMILIES = {
  "review_artifact",
  "workflow_cli",
  "commit_approval_chain",
  "session_record_capture",
  "deployment_export",
  "nested_issue_control",
}

VALID_SEQUENCE_MODES = {
  "parallel_ok",
  "serial_only",
}

REQUIRED_FIELDS = [
  "operation_id",
  "kind",
  "operation_family",
  "canonical_invocation",
  "workflow_binding",
  "required_inputs",
  "target_identity",
  "planned_outputs",
  "sequence_mode",
  "worktree_policy",
  "pending_conflict_policy",
  "artifact_policy",
  "family_required_checks",
  "vocabulary_refs",
]

FAMILY_REQUIRED_CHECKS = {
  "review_artifact": {
    "target_manifest_alignment",
    "bundle_non_empty",
    "criteria_alignment",
    "document-type_alignment",
    "approval_record_alignment",
    "existing_artifact_drift",
    "staged-vs-unstaged_target_selection",
  },
  "workflow_cli": {
    "parser_invocation",
    "workflow_binding",
    "next_active_state_dimensions",
    "scope_consistency",
  },
  "commit_approval_chain": {
    "nonce",
    "target_digest",
    "staged_file_set_digest",
    "staged_content_approval_digest",
    "expiry",
    "consume",
    "invalidated",
    "target",
  },
  "session_record_capture": {
    "session_record_mode",
    "current_session_id",
    "target_session_id",
    "current_session_formal_output_forbidden",
  },
  "deployment_export": {
    "planned_outputs",
    "overwrite_policy",
    "external_output_root",
    "target_app_root",
  },
  "nested_issue_control": {
    "parent_task",
    "discovered_issue",
    "relation",
    "allowed_files",
    "return_condition",
    "nesting_depth",
  },
}


def _contains_forbidden_field(value, path="operation"):
  if isinstance(value, dict):
    for key, child in value.items():
      if key in FORBIDDEN_LLM_FIELDS:
        return f"{path}.{key}"
      found = _contains_forbidden_field(child, f"{path}.{key}")
      if found:
        return found
  elif isinstance(value, list):
    for index, child in enumerate(value):
      found = _contains_forbidden_field(child, f"{path}[{index}]")
      if found:
        return found
  return None


def load_registry(cwd, registry_path=DEFAULT_OPERATION_REGISTRY_PATH):
  path = Path(cwd) / registry_path
  if not path.is_file():
    return None, [f"operation registry がありません: {registry_path}"]
  try:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
  except (OSError, UnicodeDecodeError, yaml.YAMLError):
    return None, [f"operation registry を YAML として読めません: {registry_path}"]
  if not isinstance(data, dict):
    return None, ["operation registry の最上位は mapping である必要があります"]
  operations = data.get("operations")
  if not isinstance(operations, list):
    return None, ["operation registry の operations は list である必要があります"]
  return data, []


def find_operation(registry, operation_id):
  for operation in registry.get("operations", []):
    if isinstance(operation, dict) and operation.get("operation_id") == operation_id:
      return operation
  return None


def validate_operation(operation):
  reasons = []
  if not isinstance(operation, dict):
    return ["operation は mapping である必要があります"]

  forbidden = _contains_forbidden_field(operation)
  if forbidden:
    reasons.append(f"LLM/provider/model 系 field は registry に含められません: {forbidden}")

  for field in REQUIRED_FIELDS:
    if field not in operation:
      reasons.append(f"operation registry field が欠落しています: {field}")

  kind = operation.get("kind")
  if kind not in VALID_KINDS:
    reasons.append(f"未知の kind です: {kind}")

  family = operation.get("operation_family")
  if family not in VALID_OPERATION_FAMILIES:
    reasons.append(f"未知の operation_family です: {family}")

  sequence_mode = operation.get("sequence_mode")
  if sequence_mode not in VALID_SEQUENCE_MODES:
    reasons.append(f"未知の sequence_mode です: {sequence_mode}")

  invocation = operation.get("canonical_invocation")
  if not isinstance(invocation, dict):
    reasons.append("canonical_invocation は mapping である必要があります")
  else:
    for field in ["entrypoint", "options", "positional_args", "execution_context"]:
      if field not in invocation:
        reasons.append(f"canonical_invocation field が欠落しています: {field}")

  family_checks = operation.get("family_required_checks")
  if not isinstance(family_checks, list):
    reasons.append("family_required_checks は list である必要があります")
  elif family in FAMILY_REQUIRED_CHECKS:
    present = set(family_checks)
    for required in sorted(FAMILY_REQUIRED_CHECKS[family] - present):
      reasons.append(f"operation_family={family} の必須 check が欠落しています: {required}")

  if not isinstance(operation.get("vocabulary_refs"), list):
    reasons.append("vocabulary_refs は list である必要があります")

  for list_field in ["required_inputs", "target_identity", "planned_outputs"]:
    if list_field in operation and not isinstance(operation.get(list_field), list):
      reasons.append(f"{list_field} は list である必要があります")

  return reasons
