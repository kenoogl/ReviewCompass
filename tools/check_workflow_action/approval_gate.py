"""Approval gate record validation for workflow-management T-017."""

REQUIRED_RECORD_FIELDS = [
  "decision_id",
  "decision",
  "decision_scope",
  "target_operation_id",
  "target_required_action",
  "target_artifact",
  "target_artifact_digest",
  "staged_file_set_digest",
  "binding_kind",
  "decided_by",
  "decided_at",
  "source_ref",
  "source_digest",
  "rationale",
  "next_action_expectation",
  "consumed",
]

VALID_DECISIONS = {
  "approved",
  "rejected",
  "deferred",
  "changes_requested",
}
VALID_DECISION_SCOPES = {
  "human_only",
  "proxy_allowed",
  "advisory_only",
}
WAIT_ONLY_REQUIRED_ACTIONS = {
  "wait_for_human_decision",
  "collect_required_decisions",
  "completed",
}
HUMAN_ONLY_REQUIRED_ACTIONS = {
  "commit_stop_point",
  "apply_approved_reopen_plan",
  "run_reopen_start",
  "advance_reopen_after_commit_stop_point",
  "advance_reopen_after_approval_stop_point",
  "finalize_reopen",
  "repair_workflow_state",
}


def _result(verdict, reasons):
  return {
    "verdict": verdict,
    "reasons": reasons,
  }


def derived_decision_scope(operation_contract):
  """Derive the required decision scope from an operation contract."""
  if not isinstance(operation_contract, dict):
    return None

  required_action = operation_contract.get("required_action")
  if required_action in HUMAN_ONLY_REQUIRED_ACTIONS:
    return "human_only"

  if operation_contract.get("approval_required") is True:
    return "human_only"

  if operation_contract.get("phase_boundary") in {
    "commit_boundary",
    "push_boundary",
    "reopen_boundary",
    "external_boundary",
  }:
    return "human_only"

  if operation_contract.get("effect_kind") in {"state_mutation", "external_call"}:
    actor = operation_contract.get("actor")
    actor_kind = actor.get("kind") if isinstance(actor, dict) else None
    if actor_kind == "human":
      return "human_only"
    return "proxy_allowed"

  return "advisory_only"


def _allows_binding_none(operation_contract):
  if not isinstance(operation_contract, dict):
    return False
  return (
    operation_contract.get("required_action") in WAIT_ONLY_REQUIRED_ACTIONS
    and operation_contract.get("approval_required") is False
    and operation_contract.get("effect_kind") == "read"
    and operation_contract.get("phase_boundary") == "none"
  )


def _validate_binding(
  record,
  operation_contract,
  current_target_artifact_digest=None,
  current_staged_file_set_digest=None,
):
  reasons = []
  binding_kind = record.get("binding_kind")
  target_digest = record.get("target_artifact_digest")
  staged_digest = record.get("staged_file_set_digest")

  if binding_kind == "artifact_digest":
    if not target_digest:
      reasons.append("binding_kind=artifact_digest には target_artifact_digest が必要です")
  elif binding_kind == "staged_file_set_digest":
    if not staged_digest:
      reasons.append("binding_kind=staged_file_set_digest には staged_file_set_digest が必要です")
  elif binding_kind == "both":
    if not target_digest:
      reasons.append("binding_kind=both には target_artifact_digest が必要です")
    if not staged_digest:
      reasons.append("binding_kind=both には staged_file_set_digest が必要です")
  elif binding_kind == "none":
    if not _allows_binding_none(operation_contract):
      reasons.append("binding_kind=none は read-only / wait-only operation に限ります")
  else:
    reasons.append(f"binding_kind が不正です: {binding_kind}")

  if (
    current_target_artifact_digest is not None
    and target_digest is not None
    and target_digest != current_target_artifact_digest
  ):
    reasons.append("target_artifact_digest が現在の対象 digest と一致しません")

  if (
    current_staged_file_set_digest is not None
    and staged_digest is not None
    and staged_digest != current_staged_file_set_digest
  ):
    reasons.append("staged_file_set_digest が現在の staged digest と一致しません")

  return reasons


def validate_approval_gate_record(
  record,
  operation_contract=None,
  current_target_artifact_digest=None,
  current_staged_file_set_digest=None,
):
  """Validate an approval gate record and contract-derived scope."""
  reasons = []
  if not isinstance(record, dict):
    return _result("DEVIATION", ["approval gate record は mapping である必要があります"])

  for field in REQUIRED_RECORD_FIELDS:
    if field not in record:
      reasons.append(f"approval gate record field が欠落しています: {field}")

  if record.get("schema_version") not in (None, "approval-gate-v1"):
    reasons.append(f"schema_version が不正です: {record.get('schema_version')}")

  if "decision" in record and record.get("decision") not in VALID_DECISIONS:
    reasons.append(f"decision が不正です: {record.get('decision')}")

  if "decision_scope" in record and record.get("decision_scope") not in VALID_DECISION_SCOPES:
    reasons.append(f"decision_scope が不正です: {record.get('decision_scope')}")

  if "consumed" in record and not isinstance(record.get("consumed"), bool):
    reasons.append("consumed は boolean である必要があります")

  reasons.extend(
    _validate_binding(
      record,
      operation_contract,
      current_target_artifact_digest=current_target_artifact_digest,
      current_staged_file_set_digest=current_staged_file_set_digest,
    )
  )

  expected_scope = derived_decision_scope(operation_contract)
  if expected_scope is not None and record.get("decision_scope") != expected_scope:
    reasons.append(
      "decision_scope が operation contract から導出した値と一致しません: "
      f"{record.get('decision_scope')} != {expected_scope}"
    )

  return _result("DEVIATION" if reasons else "OK", reasons)


def allows_target_operation(record, operation_contract):
  """Return whether a record permits the target irreversible operation."""
  validation = validate_approval_gate_record(record, operation_contract=operation_contract)
  reasons = list(validation.get("reasons") or [])
  if validation.get("verdict") != "OK":
    return {
      "verdict": "DEVIATION",
      "allowed": False,
      "reasons": reasons,
    }

  if record.get("decision") != "approved":
    reasons.append(f"approved 以外の decision は不可逆操作を許可しません: {record.get('decision')}")

  if record.get("consumed") is True:
    reasons.append("approval gate record は既に consumed です")

  if record.get("decision_scope") == "human_only" and record.get("decided_by") == "proxy_model":
    reasons.append("human_only decision は proxy_model では承認できません")

  if record.get("target_required_action") != operation_contract.get("required_action"):
    reasons.append(
      "target_required_action が operation contract と一致しません: "
      f"{record.get('target_required_action')} != {operation_contract.get('required_action')}"
    )

  operation_id = operation_contract.get("operation_id")
  if operation_id is not None and record.get("target_operation_id") != operation_id:
    reasons.append(
      "target_operation_id が operation contract と一致しません: "
      f"{record.get('target_operation_id')} != {operation_id}"
    )

  return {
    "verdict": "DEVIATION" if reasons else "OK",
    "allowed": not reasons,
    "reasons": reasons,
  }
