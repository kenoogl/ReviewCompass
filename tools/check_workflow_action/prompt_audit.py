"""Effective prompt manifest の read-only 監査。"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

import yaml


MACHINE_ACTION_TERMS = (
  "execute operation",
  "consume approval gate",
  "mutate side-track stack",
  "mutate side track stack",
  "create review-run artifacts",
  "create review run artifacts",
  "git commit",
  "git push",
  "spec-set",
)

STATE_MUTATION_TERMS = (
  "mutate workflow state",
  "update workflow state",
  "write spec.json",
  "spec.json を更新",
  "workflow_state を更新",
)

DIRECT_FOLLOWUP_TERMS = (
  "commit",
  "push",
  "spec-set",
  "spec.json を更新",
)

NEGATION_PREFIXES = (
  "do not ",
  "don't ",
  "never ",
  "no ",
  "禁止",
)


def load_manifest(path: str | Path) -> Dict[str, Any]:
  """YAML/JSON manifest を mapping として読む。"""
  with Path(path).open(encoding="utf-8") as f:
    data = yaml.safe_load(f)
  if not isinstance(data, dict):
    raise ValueError("prompt manifest は YAML mapping である必要があります")
  return data


def audit_manifest(
  manifest: Dict[str, Any],
  *,
  current_next_action: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
  """manifest が言語判断用の範囲を越えていないかを判定する。"""
  reasons: List[str] = []
  _audit_language_task(manifest.get("language_task"), reasons)
  _audit_on_completion(manifest.get("on_completion"), reasons, current_next_action)
  verdict = "OK" if not reasons else "DEVIATION"
  return {
    "verdict": verdict,
    "exit_code": 0 if verdict == "OK" else 2,
    "reasons": reasons,
    "current_state": {
      "schema_version": manifest.get("schema_version"),
      "decision_point": manifest.get("decision_point"),
      "on_completion": manifest.get("on_completion"),
    },
  }


def _audit_language_task(language_task: Any, reasons: List[str]) -> None:
  if not isinstance(language_task, dict):
    reasons.append("language_task が mapping ではありません")
    return
  constraints = language_task.get("constraints")
  if not isinstance(constraints, list):
    reasons.append("language_task.constraints が list ではありません")
    return
  for constraint in constraints:
    if not isinstance(constraint, str):
      reasons.append("language_task.constraints は文字列である必要があります")
      continue
    text = _normalized(constraint)
    if _is_negative_constraint(text):
      continue
    if _contains_any(text, MACHINE_ACTION_TERMS) or _contains_any(text, STATE_MUTATION_TERMS):
      reasons.append(
        "language_task.constraints に machine/state mutation instruction が含まれています"
      )
      return


def _audit_on_completion(
  on_completion: Any,
  reasons: List[str],
  current_next_action: Optional[Dict[str, Any]],
) -> None:
  if not isinstance(on_completion, dict):
    reasons.append("on_completion が mapping ではありません")
    return

  allowed_followups = on_completion.get("allowed_followups")
  forbidden_actions = on_completion.get("forbidden_actions")
  if not isinstance(allowed_followups, list) or not isinstance(forbidden_actions, list):
    reasons.append("on_completion allowed_followups/forbidden_actions が list ではありません")
    return

  allowed_texts = [str(value) for value in allowed_followups]
  forbidden_texts = [str(value) for value in forbidden_actions]
  if any(_contains_any(_normalized(value), DIRECT_FOLLOWUP_TERMS) for value in allowed_texts):
    reasons.append("on_completion.allowed_followups に直接操作指示が含まれています")

  normalized_allowed = {_normalized(value) for value in allowed_texts}
  normalized_forbidden = {_normalized(value) for value in forbidden_texts}
  overlap = sorted(normalized_allowed & normalized_forbidden)
  if overlap:
    reasons.append(
      "on_completion allowed_followups と forbidden_actions が矛盾しています: "
      + ", ".join(overlap)
    )

  if current_next_action is None:
    return
  expected = current_next_action.get("required_action")
  actual = on_completion.get("next_required_action")
  if expected and actual != expected:
    reasons.append(
      "on_completion.next_required_action が next_action_compatible ではありません"
    )


def _normalized(value: str) -> str:
  return " ".join(value.lower().split())


def _is_negative_constraint(text: str) -> bool:
  return any(text.startswith(prefix) for prefix in NEGATION_PREFIXES)


def _contains_any(text: str, terms: Iterable[str]) -> bool:
  return any(term in text for term in terms)
