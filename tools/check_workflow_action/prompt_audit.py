"""Effective prompt manifest の read-only 監査。"""

from __future__ import annotations

import re
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

REQUIRED_STRUCTURE_KEYS = (
  "decision_point",
  "source_artifacts",
  "prompt_length",
  "preconditions_checked",
  "language_task",
  "postconditions",
  "on_completion",
)

ALLOWED_DECISION_POINT_KINDS = (
  "stage",
  "cross_feature_stage",
  "reopen_in_progress",
  "maintenance_in_progress",
  "post_write_verification",
  "lightweight_self_check",
  "commit_stop_point",
  "upstream_recheck",
  "completed",
)

ALLOWED_POSTCONDITION_KINDS = (
  "next_action_compatible",
  "review_target_manifest_matches",
  "no_machine_task_leakage",
)

SHA256_PATTERN = re.compile(r"^sha256:[0-9a-f]{64}$")

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
  _audit_required_structure(manifest, reasons)
  _audit_decision_point(manifest.get("decision_point"), reasons)
  _audit_source_artifacts(manifest.get("source_artifacts"), reasons)
  _audit_prompt_length(manifest.get("prompt_length"), reasons)
  _audit_preconditions(manifest.get("preconditions_checked"), reasons)
  _audit_postconditions(manifest.get("postconditions"), reasons)
  _audit_language_task(manifest.get("language_task"), reasons)
  _audit_review_prompt_materials(
    manifest.get("decision_point"),
    manifest.get("review_prompt_materials"),
    reasons,
  )
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


def _audit_required_structure(manifest: Dict[str, Any], reasons: List[str]) -> None:
  for key in REQUIRED_STRUCTURE_KEYS:
    if key not in manifest:
      reasons.append(f"required structure が欠落しています: {key}")


def _audit_decision_point(decision_point: Any, reasons: List[str]) -> None:
  if not isinstance(decision_point, dict):
    reasons.append("decision_point が mapping ではありません")
    return
  kind = decision_point.get("kind")
  if kind not in ALLOWED_DECISION_POINT_KINDS:
    reasons.append(f"decision_point.kind が未知です: {kind}")
  required_action = decision_point.get("required_action")
  if not isinstance(required_action, str) or not required_action.strip():
    reasons.append("decision_point.required_action が空です")


def _audit_source_artifacts(source_artifacts: Any, reasons: List[str]) -> None:
  if not isinstance(source_artifacts, list) or not source_artifacts:
    reasons.append("source_artifacts が非空 list ではありません")
    return
  for index, artifact in enumerate(source_artifacts):
    if not isinstance(artifact, dict):
      reasons.append(f"source_artifacts[{index}] が mapping ではありません")
      continue
    path = artifact.get("path")
    sha256 = artifact.get("sha256")
    if not isinstance(path, str) or not path.strip():
      reasons.append(f"source_artifacts[{index}].path が空です")
    elif not Path(path).exists():
      reasons.append(f"source_artifacts の参照先が存在しません: {path}")
    if not isinstance(sha256, str) or not SHA256_PATTERN.match(sha256):
      reasons.append(f"source_artifacts[{index}].sha256 が sha256:<hex> 形式ではありません")


def _audit_prompt_length(prompt_length: Any, reasons: List[str]) -> None:
  if not isinstance(prompt_length, dict):
    reasons.append("prompt_length が mapping ではありません")
    return
  min_chars = prompt_length.get("min_chars")
  max_chars = prompt_length.get("max_chars")
  if not isinstance(min_chars, int) or not isinstance(max_chars, int):
    reasons.append("prompt_length.min_chars/max_chars は integer である必要があります")
  elif min_chars > max_chars:
    reasons.append("prompt_length.min_chars が max_chars を超えています")
  if prompt_length.get("failure_verdict") not in ("OK", "WARN", "DEVIATION"):
    reasons.append("prompt_length.failure_verdict が不正です")


def _audit_preconditions(preconditions: Any, reasons: List[str]) -> None:
  if not isinstance(preconditions, list) or not preconditions:
    reasons.append("preconditions_checked が非空 list ではありません")
    return
  for index, precondition in enumerate(preconditions):
    if not isinstance(precondition, dict):
      reasons.append(f"preconditions_checked[{index}] が mapping ではありません")
      continue
    if precondition.get("machine_checked") is not True:
      reasons.append(f"preconditions_checked[{index}] が machine_checked=true ではありません")
    evidence_ref = precondition.get("evidence_ref")
    if not isinstance(evidence_ref, str) or not evidence_ref.strip():
      reasons.append(f"preconditions_checked[{index}].evidence_ref が空です")


def _audit_postconditions(postconditions: Any, reasons: List[str]) -> None:
  if not isinstance(postconditions, list) or not postconditions:
    reasons.append("postconditions が非空 list ではありません")
    return
  for index, postcondition in enumerate(postconditions):
    if not isinstance(postcondition, dict):
      reasons.append(f"postconditions[{index}] が mapping ではありません")
      continue
    check_kind = postcondition.get("check_kind")
    if check_kind not in ALLOWED_POSTCONDITION_KINDS:
      reasons.append(f"postconditions[{index}].check_kind が未知です: {check_kind}")
    source_ref = postcondition.get("source_ref")
    if not isinstance(source_ref, str) or not source_ref.strip():
      reasons.append(f"postconditions[{index}].source_ref が空です")


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


def _audit_review_prompt_materials(
  decision_point: Any,
  materials: Any,
  reasons: List[str],
) -> None:
  if not isinstance(decision_point, dict):
    return
  if decision_point.get("kind") != "post_write_verification":
    return

  if not isinstance(materials, dict):
    reasons.append("review_prompt_materials が mapping ではありません")
    return

  for group_name in ("target_files", "source_materials"):
    entries = materials.get(group_name)
    if not isinstance(entries, list) or not entries:
      reasons.append(f"review_prompt_materials.{group_name} が非空 list ではありません")
      continue
    for index, entry in enumerate(entries):
      _audit_embedded_prompt_material_entry(group_name, index, entry, reasons)


def _audit_embedded_prompt_material_entry(
  group_name: str,
  index: int,
  entry: Any,
  reasons: List[str],
) -> None:
  prefix = f"review_prompt_materials.{group_name}[{index}]"
  if not isinstance(entry, dict):
    reasons.append(f"{prefix} が mapping ではありません")
    return
  path = entry.get("path")
  if not isinstance(path, str) or not path.strip():
    reasons.append(f"{prefix}.path が空です")
  elif not Path(path).exists():
    reasons.append(f"{prefix}.path の参照先が存在しません: {path}")
  if entry.get("content_mode") != "full_text":
    reasons.append(f"{prefix}.content_mode が full_text ではありません")
  content_sha256 = entry.get("content_sha256")
  if not isinstance(content_sha256, str) or not SHA256_PATTERN.match(content_sha256):
    reasons.append(f"{prefix}.content_sha256 が sha256:<hex> 形式ではありません")


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
