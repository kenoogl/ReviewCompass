"""Implementation phase plan checks for Requirement 16."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

import yaml


DEFAULT_PLAN_PATH = "stages/workflow-management-implementation-phases.yaml"


def load_plan(cwd: str | Path, path: str = DEFAULT_PLAN_PATH) -> Dict[str, Any]:
  """implementation phase plan YAML を読む。"""
  plan_path = Path(cwd) / path
  data = yaml.safe_load(plan_path.read_text(encoding="utf-8"))
  if not isinstance(data, dict):
    raise ValueError("implementation phase plan は mapping である必要があります")
  return data


def check_phase_plan(
  plan: Dict[str, Any],
  *,
  feature: str,
  current_phase: Optional[int] = None,
  executed_operations: Optional[Iterable[str]] = None,
) -> Dict[str, Any]:
  """entry / exit / forbidden operation を read-only で検査する。"""
  reasons: List[str] = []
  if plan.get("feature") != feature:
    reasons.append(f"feature が一致しません: {plan.get('feature')} != {feature}")

  phases = plan.get("phases")
  if not isinstance(phases, list):
    reasons.append("phases は list である必要があります")
    phases = []

  phase_numbers = [phase.get("phase") for phase in phases if isinstance(phase, dict)]
  if phase_numbers != list(range(len(phase_numbers))) or set(phase_numbers) != set(range(7)):
    reasons.append("Phase 0〜6 の coverage / order が不正です")

  phase_number = current_phase
  if phase_number is None:
    phase_number = plan.get("active_phase", 0)
  phase = _find_phase(phases, phase_number)
  if phase is None:
    reasons.append(f"phase が見つかりません: {phase_number}")
    phase = {}

  _append_unsatisfied(reasons, phase.get("entry_criteria"), "entry")
  _append_unsatisfied(reasons, phase.get("exit_criteria"), "exit")
  _append_snapshot_evidence(reasons, phase.get("required_snapshot_evidence"))
  _append_commit_boundary(reasons, phase.get("commit_boundary"))

  executed = set(executed_operations or [])
  forbidden = set(phase.get("forbidden_operations") or [])
  forbidden_hits = sorted(executed & forbidden)
  if forbidden_hits:
    reasons.append("forbidden operation が実行されています: " + ", ".join(forbidden_hits))

  verdict = "OK" if not reasons else "DEVIATION"
  return {
    "verdict": verdict,
    "exit_code": 0 if verdict == "OK" else 2,
    "reasons": reasons,
    "current_state": {
      "feature": feature,
      "phase": phase_number,
      "phase_name": phase.get("name"),
      "executed_operations": sorted(executed),
    },
  }


def _find_phase(phases: List[Any], phase_number: int) -> Optional[Dict[str, Any]]:
  for phase in phases:
    if isinstance(phase, dict) and phase.get("phase") == phase_number:
      return phase
  return None


def _append_unsatisfied(reasons: List[str], criteria: Any, label: str) -> None:
  if not isinstance(criteria, list) or not criteria:
    reasons.append(f"{label} criteria がありません")
    return
  for criterion in criteria:
    if not isinstance(criterion, dict):
      reasons.append(f"{label} criterion は mapping である必要があります")
      continue
    if criterion.get("satisfied") is not True:
      reasons.append(f"{label} criterion 未充足: {criterion.get('id')}")


def _append_snapshot_evidence(reasons: List[str], evidence: Any) -> None:
  if evidence is None:
    return
  if not isinstance(evidence, list) or not evidence:
    reasons.append("snapshot evidence が非空 list ではありません")
    return
  for item in evidence:
    if not isinstance(item, dict):
      reasons.append("snapshot evidence は mapping である必要があります")
      continue
    if not item.get("path"):
      reasons.append(f"snapshot evidence path が欠落しています: {item.get('id')}")
    if item.get("fresh") is not True:
      reasons.append(f"snapshot evidence が fresh ではありません: {item.get('id')}")


def _append_commit_boundary(reasons: List[str], commit_boundary: Any) -> None:
  if not isinstance(commit_boundary, dict):
    reasons.append("commit_boundary が mapping ではありません")
    return
  if commit_boundary.get("required") is True:
    if not commit_boundary.get("evidence_ref"):
      reasons.append("commit_boundary.evidence_ref が欠落しています")
    if not commit_boundary.get("description"):
      reasons.append("commit_boundary.description が欠落しています")
