"""Read-only entrypoint inventory for workflow operation coverage."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List


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
