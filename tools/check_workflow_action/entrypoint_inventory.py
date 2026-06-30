"""Read-only entrypoint inventory for workflow operation coverage."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

import yaml


NEXT_ACTION_KINDS = [
  "completed",
  "verification_pending",
  "maintenance_in_progress",
  "maintenance_review_required",
  "maintenance_post_write_required",
  "maintenance_completion_required",
  "reopen_in_progress",
  "reopen_classification_required",
  "blocking_unit_in_progress",
  "parent_resume_pending",
  "commit_candidate",
  "commit_mixing_risk",
]


CLI_SUBCOMMANDS = [
  {
    "id": "next",
    "trigger": "workflow state query",
    "command": "tools/check-workflow-action.py next --json",
    "required_action": "read_next_action",
    "effective_prompt": "next_action_kind:*",
  },
  {
    "id": "commit-preflight",
    "trigger": "commit request",
    "command": "tools/check-workflow-action.py commit-preflight --json",
    "required_action": "prepare_commit",
    "effective_prompt": None,
  },
  {
    "id": "work-backlog start-checklist",
    "trigger": "user-initiated backlog TODO execution",
    "command": "tools/check-workflow-action.py work-backlog start-checklist",
    "required_action": "create_runtime_checklist_from_backlog_todo",
    "effective_prompt": "operation_prompt:user_initiated_plan_to_todo_bridge",
  },
  {
    "id": "work-checklist show",
    "trigger": "runtime checklist progress query",
    "command": "tools/check-workflow-action.py work-checklist show",
    "required_action": "show_runtime_checklist",
    "effective_prompt": None,
  },
  {
    "id": "push",
    "trigger": "push request",
    "command": "tools/check-workflow-action.py push --rationale <reason>",
    "required_action": "push_preflight",
    "effective_prompt": "operation_prompt:push",
  },
  {
    "id": "operation-prompt",
    "trigger": "operation prompt selection",
    "command": "tools/check-workflow-action.py operation-prompt --json",
    "required_action": "select_operation_prompt",
    "effective_prompt": "operation_prompt:*",
  },
]


def build_entrypoint_inventory(cwd: str | Path) -> Dict[str, Any]:
  """Return a machine-readable, read-only list of known entrypoints."""
  _ = Path(cwd)
  entrypoints: List[Dict[str, Any]] = []
  entrypoints.extend(_next_action_kind_entries())
  entrypoints.extend(_cli_subcommand_entries())
  return {
    "verdict": "OK",
    "exit_code": 0,
    "operation_mode": "read_only",
    "entrypoints": entrypoints,
    "reasons": [],
  }


def build_entrypoint_registry_schema(cwd: str | Path) -> Dict[str, Any]:
  """Return the read-only schema contract for entrypoint registry entries."""
  _ = Path(cwd)
  return {
    "verdict": "OK",
    "exit_code": 0,
    "operation_mode": "read_only",
    "schema_version": "entrypoint-registry-schema-v1",
    "registry_contract": {
      "required_fields": [
        "entrypoint_id",
        "kind",
        "trigger",
        "decision_point_ref",
        "effective_prompt_ref",
        "required_action",
        "mechanized_command",
        "evidence_contract",
      ],
      "responsibility_boundary": {
        "discipline_map": {
          "source_ref": ".reviewcompass/guidance/WORKFLOW_DISCIPLINE_MAP.yaml",
          "owns": ["decision_point_ref", "effective_prompt_ref"],
        },
        "entrypoint_registry": {
          "owns": [
            "entrypoint_id",
            "kind",
            "trigger",
            "required_action",
            "mechanized_command",
            "evidence_contract",
          ],
        },
      },
      "coverage_audit_contract": {
        "consumer": "entrypoint coverage audit",
        "required_schema_version": "entrypoint-registry-schema-v1",
        "missing_registry_entry_verdict": "WARN",
      },
    },
    "reasons": [],
  }


def build_entrypoint_coverage_audit(cwd: str | Path) -> Dict[str, Any]:
  """Return read-only coverage status for known workflow entrypoints."""
  root = Path(cwd)
  inventory = build_entrypoint_inventory(root)
  registry_schema = build_entrypoint_registry_schema(root)
  discipline_points = _load_discipline_decision_points(root)
  effective_prompt_names = _effective_prompt_names(root)
  entrypoint_coverage = []
  findings = []

  for entry in inventory["entrypoints"]:
    coverage = _coverage_entry(entry, discipline_points, effective_prompt_names)
    entrypoint_coverage.append(coverage)
    findings.extend(_coverage_findings(coverage))

  verdict = "WARN" if findings else "OK"
  return {
    "verdict": verdict,
    "exit_code": 0,
    "operation_mode": "read_only",
    "registry_schema_version": registry_schema["schema_version"],
    "finding_policy": {
      "unregistered_entrypoint_severity": "WARN",
      "missing_discipline_map_severity": "WARN",
      "missing_effective_prompt_severity": "WARN",
    },
    "coverage_summary": {
      "total_entrypoints": len(entrypoint_coverage),
      "covered_entrypoints": _covered_entrypoint_count(entrypoint_coverage),
      "warning_candidate_count": len(findings),
    },
    "entrypoint_coverage": entrypoint_coverage,
    "findings": findings,
    "reasons": [finding["message"] for finding in findings],
  }


def _next_action_kind_entries() -> List[Dict[str, Any]]:
  entries = []
  for kind in NEXT_ACTION_KINDS:
    entries.append({
      "entrypoint_id": f"next_action_kind:{kind}",
      "kind": "next_action_kind",
      "trigger": "tools/check-workflow-action.py next --json",
      "decision_point_ref": {
        "group": "next_action_kind",
        "id": kind,
      },
      "required_action": kind,
      "expected_effective_prompt": f"next_action_kind:{kind}",
      "mechanized_command": "tools/check-workflow-action.py next --json",
      "evidence_path": None,
    })
  return entries


def _cli_subcommand_entries() -> List[Dict[str, Any]]:
  entries = []
  for command in CLI_SUBCOMMANDS:
    entries.append({
      "entrypoint_id": f"cli_subcommand:{command['id']}",
      "kind": "cli_subcommand",
      "trigger": command["trigger"],
      "decision_point_ref": None,
      "required_action": command["required_action"],
      "expected_effective_prompt": command["effective_prompt"],
      "mechanized_command": command["command"],
      "evidence_path": None,
    })
  return entries


def _load_discipline_decision_points(cwd: Path) -> Dict[str, set[str]]:
  path = cwd / ".reviewcompass/guidance/WORKFLOW_DISCIPLINE_MAP.yaml"
  try:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
  except (OSError, yaml.YAMLError, UnicodeDecodeError):
    return {}
  decision_points = data.get("decision_points") if isinstance(data, dict) else None
  if not isinstance(decision_points, dict):
    return {}
  result: Dict[str, set[str]] = {}
  for group, entries in decision_points.items():
    if not isinstance(entries, list):
      continue
    result[str(group)] = {
      str(entry["id"])
      for entry in entries
      if isinstance(entry, dict) and isinstance(entry.get("id"), str)
    }
  return result


def _effective_prompt_names(cwd: Path) -> set[str]:
  prompt_dirs = [
    cwd / ".reviewcompass/runtime/effective-prompts",
    cwd / ".reviewcompass/guidance/effective-prompts",
  ]
  names: set[str] = set()
  for prompt_dir in prompt_dirs:
    if not prompt_dir.is_dir():
      continue
    names.update(
      path.name.removesuffix(".prompt.md")
      for path in prompt_dir.glob("*.prompt.md")
    )
  return names


def _coverage_entry(
  entry: Dict[str, Any],
  discipline_points: Dict[str, set[str]],
  effective_prompt_names: set[str],
) -> Dict[str, Any]:
  decision_point_ref = entry.get("decision_point_ref")
  expected_effective_prompt = entry.get("expected_effective_prompt")
  return {
    "entrypoint_id": entry["entrypoint_id"],
    "kind": entry["kind"],
    "registry_status": "registered",
    "discipline_map_status": _discipline_map_status(decision_point_ref, discipline_points),
    "effective_prompt_status": _effective_prompt_status(
      expected_effective_prompt,
      effective_prompt_names,
    ),
    "mechanized_action_status": _mechanized_action_status(entry),
    "decision_point_ref": decision_point_ref,
    "effective_prompt_ref": expected_effective_prompt,
    "mechanized_command": entry.get("mechanized_command"),
  }


def _discipline_map_status(
  decision_point_ref: Any,
  discipline_points: Dict[str, set[str]],
) -> str:
  if decision_point_ref is None:
    return "not_applicable"
  if not isinstance(decision_point_ref, dict):
    return "missing"
  group = decision_point_ref.get("group")
  entry_id = decision_point_ref.get("id")
  if not isinstance(group, str) or not isinstance(entry_id, str):
    return "missing"
  if entry_id in discipline_points.get(group, set()):
    return "covered"
  return "missing"


def _effective_prompt_status(expected_ref: Any, effective_prompt_names: set[str]) -> str:
  if expected_ref is None:
    return "not_applicable"
  if not isinstance(expected_ref, str):
    return "missing"
  group, _, entry_id = expected_ref.partition(":")
  if not group or not entry_id:
    return "missing"
  if entry_id == "*":
    prefix = f"{group}-"
    return "covered" if any(name.startswith(prefix) for name in effective_prompt_names) else "missing"
  prompt_name = f"{group}-{entry_id}"
  return "covered" if prompt_name in effective_prompt_names else "missing"


def _mechanized_action_status(entry: Dict[str, Any]) -> str:
  if entry.get("mechanized_command"):
    return "covered"
  return "missing"


def _covered_entrypoint_count(entrypoint_coverage: List[Dict[str, Any]]) -> int:
  covered_count = 0
  for entry in entrypoint_coverage:
    statuses = [
      entry["registry_status"],
      entry["discipline_map_status"],
      entry["effective_prompt_status"],
      entry["mechanized_action_status"],
    ]
    if all(status in ("registered", "covered", "not_applicable") for status in statuses):
      covered_count += 1
  return covered_count


def _coverage_findings(coverage: Dict[str, Any]) -> List[Dict[str, str]]:
  checks = [
    ("registry_status", "registered", "entrypoint registry coverage is missing"),
    ("discipline_map_status", "covered", "discipline map coverage is missing"),
    ("effective_prompt_status", "covered", "effective prompt coverage is missing"),
    ("mechanized_action_status", "covered", "mechanized action coverage is missing"),
  ]
  findings = []
  for field, covered_value, message in checks:
    status = coverage[field]
    if status in (covered_value, "not_applicable"):
      continue
    findings.append({
      "severity": "WARN",
      "entrypoint_id": coverage["entrypoint_id"],
      "field": field,
      "status": status,
      "message": f"{coverage['entrypoint_id']}: {message}",
    })
  return findings
