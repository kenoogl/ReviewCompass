"""Operation contract loader and consistency checks for Requirement 13."""

import hashlib
import json
from pathlib import Path

import yaml


DEFAULT_CONTRACTS_PATH = "stages/operation-contracts.yaml"
DEFAULT_REGISTRY_PATH = "stages/operation-registry.yaml"
DEFAULT_REQUIRED_ACTION_SCHEMA_PATH = ".reviewcompass/schema/required_action.schema.json"

CONTRACT_SCHEMA_VERSION = "operation-contract-v1"
COLLECTION_SCHEMA_VERSION = "operation-contracts-v1"

CONTRACT_DIGEST_PREFIX = "sha256:"

CONTRACT_FIELD_NAMES = {
  "effect_kind",
  "approval_required",
  "approval_contract_refs",
  "phase_boundary",
  "preconditions",
  "postconditions",
  "side_effects",
  "approval_aggregation",
  "branching",
  "max_effect_kind",
  "workflow_state_effect",
}

COMMIT_BOUNDARY_REQUIRED_ACTIONS = {
  "commit_stop_point",
  "apply_approved_reopen_plan",
  "run_reopen_start",
  "advance_reopen_after_commit_stop_point",
  "advance_reopen_after_approval_stop_point",
  "finalize_reopen",
  "repair_workflow_state",
}

BRANCHY_REQUIRED_ACTIONS = {
  "run_maintenance",
  "run_reopen_pending_gate",
  "run_workflow_stage",
}

VALID_EFFECT_KINDS = {
  "read",
  "write",
  "state_mutation",
  "external_call",
}

VALID_PHASE_BOUNDARIES = {
  "none",
  "within_phase",
  "phase_transition",
  "reopen_boundary",
  "commit_boundary",
  "push_boundary",
  "external_boundary",
}

REQUIRED_CONTRACT_FIELDS = [
  "schema_version",
  "operation_id",
  "required_action",
  "effect_kind",
  "approval_required",
  "approval_contract_refs",
  "phase_boundary",
  "sequence",
  "actor",
  "branching",
  "max_effect_kind",
  "preconditions",
  "postconditions",
  "side_effects",
  "commit_boundary",
  "workflow_state_effect",
  "canonical_invocation",
]

REQUIRED_BRANCH_FIELDS = [
  "branch_id",
  "condition",
  "internal_steps",
  "max_effect_kind",
  "approval_aggregation",
  "human_only_override_applies",
  "precondition_ids",
  "postcondition_ids",
]

REQUIRED_STEP_FIELDS = [
  "step_id",
  "effect_kind",
  "approval_required",
  "approval_contract_ref",
  "phase_boundary",
  "source_ref",
]


def _read_yaml(path):
  try:
    return yaml.safe_load(path.read_text(encoding="utf-8")), []
  except (OSError, UnicodeDecodeError, yaml.YAMLError) as exc:
    return None, [f"YAML を読めません: {path}: {exc}"]


def _read_json(path):
  try:
    return json.loads(path.read_text(encoding="utf-8")), []
  except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
    return None, [f"JSON を読めません: {path}: {exc}"]


def load_required_actions(cwd, schema_path=DEFAULT_REQUIRED_ACTION_SCHEMA_PATH):
  data, errors = _read_json(Path(cwd) / schema_path)
  if errors:
    return [], errors
  values = data.get("enum") if isinstance(data, dict) else None
  if not isinstance(values, list) or not all(isinstance(value, str) for value in values):
    return [], [f"required_action schema の enum が不正です: {schema_path}"]
  return values, []


def load_contracts(cwd, contracts_path=DEFAULT_CONTRACTS_PATH):
  data, errors = _read_yaml(Path(cwd) / contracts_path)
  if errors:
    return {}, data, errors
  if not isinstance(data, dict):
    return {}, data, [f"operation contracts の最上位は mapping である必要があります: {contracts_path}"]
  operations = data.get("operations")
  if not isinstance(operations, list):
    return {}, data, [f"operation contracts の operations は list である必要があります: {contracts_path}"]
  contracts = {}
  reasons = []
  for contract in operations:
    if not isinstance(contract, dict):
      reasons.append("operation contract は mapping である必要があります")
      continue
    operation_id = contract.get("operation_id")
    if not isinstance(operation_id, str) or not operation_id:
      reasons.append("operation contract の operation_id が不正です")
      continue
    if operation_id in contracts:
      reasons.append(f"operation contract operation_id が重複しています: {operation_id}")
      continue
    contracts[operation_id] = contract
  return contracts, data, reasons


def load_registry(cwd, registry_path=DEFAULT_REGISTRY_PATH):
  data, errors = _read_yaml(Path(cwd) / registry_path)
  if errors:
    return {}, data, errors
  if not isinstance(data, dict):
    return {}, data, [f"operation registry の最上位は mapping である必要があります: {registry_path}"]
  operations = data.get("operations")
  if not isinstance(operations, list):
    return {}, data, [f"operation registry の operations は list である必要があります: {registry_path}"]
  registry = {}
  reasons = []
  for operation in operations:
    if not isinstance(operation, dict):
      reasons.append("operation registry entry は mapping である必要があります")
      continue
    operation_id = operation.get("operation_id")
    if not isinstance(operation_id, str) or not operation_id:
      reasons.append("operation registry entry の operation_id が不正です")
      continue
    registry[operation_id] = operation
  return registry, data, reasons


def contract_digest(contract):
  normalized = json.dumps(
    contract,
    ensure_ascii=False,
    sort_keys=True,
    separators=(",", ":"),
  ).encode("utf-8")
  return CONTRACT_DIGEST_PREFIX + hashlib.sha256(normalized).hexdigest()


def _validate_contract_shape(contract):
  reasons = []
  operation_id = contract.get("operation_id", "<unknown>")
  for field in REQUIRED_CONTRACT_FIELDS:
    if field not in contract:
      reasons.append(f"{operation_id}: contract field が欠落しています: {field}")
  if contract.get("schema_version") != CONTRACT_SCHEMA_VERSION:
    reasons.append(f"{operation_id}: schema_version が不正です: {contract.get('schema_version')}")
  if contract.get("effect_kind") not in VALID_EFFECT_KINDS:
    reasons.append(f"{operation_id}: effect_kind が不正です: {contract.get('effect_kind')}")
  if contract.get("max_effect_kind") not in VALID_EFFECT_KINDS:
    reasons.append(f"{operation_id}: max_effect_kind が不正です: {contract.get('max_effect_kind')}")
  if contract.get("phase_boundary") not in VALID_PHASE_BOUNDARIES:
    reasons.append(f"{operation_id}: phase_boundary が不正です: {contract.get('phase_boundary')}")
  if not isinstance(contract.get("approval_required"), bool):
    reasons.append(f"{operation_id}: approval_required は boolean である必要があります")
  if not isinstance(contract.get("approval_contract_refs"), list):
    reasons.append(f"{operation_id}: approval_contract_refs は list である必要があります")

  sequence = contract.get("sequence")
  if not isinstance(sequence, dict):
    reasons.append(f"{operation_id}: sequence は mapping である必要があります")
  else:
    if sequence.get("mode") not in {"parallel_ok", "serial_only"}:
      reasons.append(f"{operation_id}: sequence.mode が不正です: {sequence.get('mode')}")
    if not isinstance(sequence.get("internal_steps"), list):
      reasons.append(f"{operation_id}: sequence.internal_steps は list である必要があります")

  branching = contract.get("branching")
  if not isinstance(branching, dict):
    reasons.append(f"{operation_id}: branching は mapping である必要があります")
  else:
    if not isinstance(branching.get("has_branches"), bool):
      reasons.append(f"{operation_id}: branching.has_branches は boolean である必要があります")
    branches = branching.get("branches")
    if not isinstance(branches, list):
      reasons.append(f"{operation_id}: branching.branches は list である必要があります")
    else:
      for branch in branches:
        if not isinstance(branch, dict):
          reasons.append(f"{operation_id}: branch は mapping である必要があります")
          continue
        for field in REQUIRED_BRANCH_FIELDS:
          if field not in branch:
            reasons.append(f"{operation_id}: branch field が欠落しています: {field}")
        steps = branch.get("internal_steps")
        if not isinstance(steps, list):
          reasons.append(f"{operation_id}: branch.internal_steps は list である必要があります")
          continue
        for step in steps:
          if not isinstance(step, dict):
            reasons.append(f"{operation_id}: branch internal step は mapping である必要があります")
            continue
          for field in REQUIRED_STEP_FIELDS:
            if field not in step:
              reasons.append(f"{operation_id}: branch internal step field が欠落しています: {field}")
          if step.get("effect_kind") not in VALID_EFFECT_KINDS:
            reasons.append(f"{operation_id}: branch step effect_kind が不正です: {step.get('effect_kind')}")
          if step.get("phase_boundary") not in VALID_PHASE_BOUNDARIES:
            reasons.append(f"{operation_id}: branch step phase_boundary が不正です: {step.get('phase_boundary')}")
          if not isinstance(step.get("approval_required"), bool):
            reasons.append(f"{operation_id}: branch step approval_required は boolean である必要があります")

  return reasons


def _validate_commit_boundaries(contracts_by_action):
  reasons = []
  for required_action in sorted(COMMIT_BOUNDARY_REQUIRED_ACTIONS):
    contract = contracts_by_action.get(required_action)
    if contract is None:
      continue
    if contract.get("approval_required") is not True:
      reasons.append(f"{required_action}: approval_required=true である必要があります")
    if (contract.get("commit_boundary") or {}).get("required") is not True:
      reasons.append(f"{required_action}: commit_boundary.required=true である必要があります")
  record = contracts_by_action.get("record_human_decision")
  if record is not None:
    if record.get("approval_required") is not False:
      reasons.append("record_human_decision: approval_required=false である必要があります")
    if record.get("approval_satisfaction") != "does_not_satisfy_target_operation":
      reasons.append(
        "record_human_decision: approval_satisfaction は "
        "does_not_satisfy_target_operation である必要があります"
      )
  return reasons


def _validate_branchy_contracts(contracts_by_action):
  reasons = []
  for required_action in sorted(BRANCHY_REQUIRED_ACTIONS):
    contract = contracts_by_action.get(required_action)
    if contract is None:
      continue
    branching = contract.get("branching") or {}
    if branching.get("has_branches") is not True:
      reasons.append(f"{required_action}: branching.has_branches=true である必要があります")
    branches = branching.get("branches")
    if not isinstance(branches, list) or not branches:
      reasons.append(f"{required_action}: branching.branches が空です")
  return reasons


def _validate_registry_contract_refs(registry, contracts):
  reasons = []
  drift = []
  for operation_id, operation in registry.items():
    duplicated = sorted(CONTRACT_FIELD_NAMES.intersection(operation))
    if duplicated:
      reasons.append(f"{operation_id}: registry が contract 正本 field を複製しています: {', '.join(duplicated)}")
    reference = operation.get("operation_contract")
    if not isinstance(reference, dict):
      reasons.append(f"{operation_id}: operation_contract 参照がありません")
      drift.append(operation_id)
      continue
    for field in ["operation_id", "schema_version", "digest"]:
      if field not in reference:
        reasons.append(f"{operation_id}: operation_contract.{field} が欠落しています")
    contract_id = reference.get("operation_id")
    contract = contracts.get(contract_id)
    if contract is None:
      reasons.append(f"{operation_id}: 参照先 contract がありません: {contract_id}")
      drift.append(operation_id)
      continue
    if reference.get("schema_version") != contract.get("schema_version"):
      reasons.append(f"{operation_id}: contract schema_version drift")
      drift.append(operation_id)
    expected_digest = contract_digest(contract)
    if reference.get("digest") != expected_digest:
      reasons.append(f"{operation_id}: contract digest drift")
      drift.append(operation_id)
  return reasons, drift


def run_contract_check(cwd):
  required_actions, required_errors = load_required_actions(cwd)
  contracts, _contracts_data, contract_errors = load_contracts(cwd)
  registry, _registry_data, registry_errors = load_registry(cwd)

  reasons = []
  reasons.extend(required_errors)
  reasons.extend(contract_errors)
  reasons.extend(registry_errors)

  contracts_by_action = {}
  unknown_required_actions = []
  duplicate_required_actions = []
  for contract in contracts.values():
    reasons.extend(_validate_contract_shape(contract))
    required_action = contract.get("required_action")
    if required_action not in required_actions:
      unknown_required_actions.append(required_action)
    if required_action in contracts_by_action:
      duplicate_required_actions.append(required_action)
    contracts_by_action[required_action] = contract

  required_action_set = set(required_actions)
  mapped_required_actions = set(contracts_by_action)
  unmapped_required_actions = sorted(required_action_set - mapped_required_actions)
  extra_required_actions = sorted(mapped_required_actions - required_action_set)
  if unmapped_required_actions:
    reasons.append("required_action に未接続の operation contract があります")
  if extra_required_actions:
    reasons.append("operation contract が未知の required_action を参照しています")
  if duplicate_required_actions:
    reasons.append("required_action の contract mapping が重複しています")

  reasons.extend(_validate_commit_boundaries(contracts_by_action))
  reasons.extend(_validate_branchy_contracts(contracts_by_action))
  registry_ref_reasons, registry_drift = _validate_registry_contract_refs(registry, contracts)
  reasons.extend(registry_ref_reasons)

  verdict = "DEVIATION" if reasons else "OK"
  return {
    "schema_version": "operation-contract-check-v1",
    "verdict": verdict,
    "required_action_count": len(required_actions),
    "contract_count": len(contracts),
    "unmapped_required_actions": unmapped_required_actions,
    "unknown_required_actions": sorted(set(unknown_required_actions) | set(extra_required_actions)),
    "duplicate_required_actions": sorted(set(duplicate_required_actions)),
    "registry_contract_drift": sorted(set(registry_drift)),
    "reasons": reasons,
  }
