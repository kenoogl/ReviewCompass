"""Proxy triage decision checks for Requirement 16."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

import yaml


DEFAULT_DECISION_FILE = "proxy-triage-decision.yaml"


def human_required_evaluation_order() -> List[str]:
  """human-required predicate の固定評価順を返す。"""
  return [
    "coverage_and_evidence",
    "finding_to_operation_mapping",
    "operation_contract",
    "approval_gate_record",
    "review_wave_impact",
    "priority_resolution",
  ]


def load_decision(run_dir: str | Path) -> Dict[str, Any]:
  """review-run 内の proxy triage decision を読む。"""
  path = Path(run_dir) / DEFAULT_DECISION_FILE
  data = yaml.safe_load(path.read_text(encoding="utf-8"))
  if not isinstance(data, dict):
    raise ValueError("proxy triage decision は mapping である必要があります")
  return data


def check_decision(decision: Dict[str, Any]) -> Dict[str, Any]:
  """decision file の最低限の completeness を検査する。"""
  reasons = []
  for field in [
    "raw_response_path",
    "decision_prompt_path",
    "candidate_decisions",
    "selected_decision",
    "reasoning_summary",
    "final_application_target",
  ]:
    if not decision.get(field):
      reasons.append(f"proxy-triage-decision field が欠落しています: {field}")
  reasons.extend(validate_coverage(decision)["reasons"])
  reasons.extend(validate_approval_scope(decision)["reasons"])
  verdict = "OK" if not reasons else "DEVIATION"
  return {
    "verdict": verdict,
    "exit_code": 0 if verdict == "OK" else 2,
    "reasons": reasons,
    "current_state": {
      "decision_id": decision.get("decision_id"),
      "target_findings": decision.get("target_findings"),
    },
  }


def validate_coverage(decision: Dict[str, Any]) -> Dict[str, Any]:
  """target findings と selected decision の coverage を照合する。"""
  target = set(decision.get("target_findings") or [])
  selected = decision.get("selected_decision")
  selected_ids = set()
  if isinstance(selected, dict):
    selected_ids = set(selected.get("finding_ids") or [])
  reasons = []
  if not target or target != selected_ids:
    reasons.append(
      "coverage mismatch: target_findings と selected_decision.finding_ids が一致しません"
    )
  verdict = "OK" if not reasons else "DEVIATION"
  return {"verdict": verdict, "exit_code": 0 if verdict == "OK" else 2, "reasons": reasons}


def validate_approval_scope(decision: Dict[str, Any]) -> Dict[str, Any]:
  """review triage decision scope と apply-fixes scope を照合する。"""
  scope = decision.get("approval_scope")
  reasons = []
  if not isinstance(scope, dict):
    reasons.append("approval scope がありません")
  else:
    review_scope = set(scope.get("review_triage_decide") or [])
    apply_scope = set(scope.get("apply_fixes") or [])
    if review_scope != apply_scope:
      reasons.append("approval scope mismatch: review_triage_decide と apply_fixes が一致しません")
  verdict = "OK" if not reasons else "DEVIATION"
  return {"verdict": verdict, "exit_code": 0 if verdict == "OK" else 2, "reasons": reasons}


def evaluate_human_required(
  *,
  decision: Dict[str, Any],
  operation_contract: Dict[str, Any],
  approval_gate: Any,
  review_wave_impact: Dict[str, Any],
) -> Dict[str, Any]:
  """proxy apply を止める human-required 条件を評価する。"""
  blocking_reasons: List[str] = []
  coverage_result = validate_coverage(decision)
  if coverage_result["verdict"] != "OK":
    blocking_reasons.extend(coverage_result["reasons"])
  if operation_contract.get("approval_required") is True:
    blocking_reasons.append(
      f"approval_required operation: {operation_contract.get('operation_id')}"
    )
  if isinstance(approval_gate, dict):
    if approval_gate.get("decision_scope") == "human_only":
      blocking_reasons.append("human_only approval gate blocks proxy apply")
    if approval_gate.get("decision") != "approved":
      blocking_reasons.append("unresolved approval gate blocks proxy apply")
  if review_wave_impact.get("unresolved") is True:
    blocking_reasons.append("unresolved review-wave impact blocks proxy apply")
  verdict = "OK" if not blocking_reasons else "DEVIATION"
  return {
    "verdict": verdict,
    "exit_code": 0 if verdict == "OK" else 2,
    "blocks_proxy_apply": bool(blocking_reasons),
    "blocking_reasons": blocking_reasons,
    "checked_records": ["approval_gate_record"],
    "checked_contracts": [operation_contract.get("operation_id")],
    "source_refs": ["stages/operation-contracts.yaml"],
  }


def resolve_active_reopen_scope(
  *,
  spec_reopened: Dict[str, Any],
  reopen_record: Any,
) -> Dict[str, Any]:
  """spec.json.reopened を active scope とみなさないことを検査する。"""
  if not isinstance(reopen_record, dict):
    return {
      "verdict": "DEVIATION",
      "exit_code": 2,
      "active_reopen_scope": [],
      "reasons": [
        "active reopen scope は reopen record から解決する必要があり、spec.json.reopened は履歴です"
      ],
      "history_reopened": spec_reopened,
    }
  scope = reopen_record.get("active_reopen_scope")
  if not scope:
    return {
      "verdict": "DEVIATION",
      "exit_code": 2,
      "active_reopen_scope": [],
      "reasons": ["active reopen scope が欠落しています"],
      "history_reopened": spec_reopened,
    }
  return {
    "verdict": "OK",
    "exit_code": 0,
    "active_reopen_scope": scope,
    "reasons": [],
    "history_reopened": spec_reopened,
  }


def evaluate_review_wave_consumer_impact(
  *,
  review_wave_summary: Dict[str, Any],
  carry_forward_register: Any,
  downstream_impact_decisions: List[Any],
  spec_recheck: Dict[str, Any],
) -> Dict[str, Any]:
  """consumer impact が未解決なら proxy apply を止める。"""
  blocking_reasons: List[str] = []
  impacts = review_wave_summary.get("consumer_impacts")
  has_unresolved = any(
    isinstance(impact, dict) and impact.get("status") == "unresolved"
    for impact in impacts or []
  )
  if has_unresolved and carry_forward_register is None:
    blocking_reasons.append("carry-forward register is required for unresolved consumer impact")
  if has_unresolved and not downstream_impact_decisions:
    blocking_reasons.append("downstream impact decisions are required")
  if has_unresolved and not spec_recheck.get("impacted_downstream_phases"):
    blocking_reasons.append("spec recheck impacted_downstream_phases is required")
  verdict = "OK" if not blocking_reasons else "DEVIATION"
  return {
    "verdict": verdict,
    "exit_code": 0 if verdict == "OK" else 2,
    "blocks_proxy_apply": bool(blocking_reasons),
    "blocking_reasons": blocking_reasons,
  }
