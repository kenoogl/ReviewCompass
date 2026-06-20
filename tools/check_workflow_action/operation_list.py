"""Read-only operation list for Requirement 16 Phase 2."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from .operation_contracts import load_contracts


def build_operation_list(cwd: str | Path) -> Dict[str, Any]:
  """operation contracts を read-only registry 表示へ整形する。"""
  contracts, _raw, reasons = load_contracts(Path(cwd))
  operations: List[Dict[str, Any]] = []
  for contract in contracts.values():
    operations.append(_operation_entry(contract))
  verdict = "OK" if not reasons else "DEVIATION"
  return {
    "verdict": verdict,
    "exit_code": 0 if verdict == "OK" else 2,
    "operation_mode": "read_only",
    "operations": sorted(operations, key=lambda item: item["operation_id"]),
    "reasons": reasons,
  }


def _operation_entry(contract: Dict[str, Any]) -> Dict[str, Any]:
  return {
    "operation_id": contract.get("operation_id"),
    "canonical_commands": _canonical_commands(contract.get("canonical_invocation")),
    "effect_kind": contract.get("effect_kind"),
    "approval_required": contract.get("approval_required"),
    "sequence": contract.get("sequence"),
    "pending_conflicts": [],
  }


def _canonical_commands(invocation: Any) -> List[str]:
  if not isinstance(invocation, dict):
    return []
  entrypoint = invocation.get("entrypoint")
  if not entrypoint:
    return []
  parts = [str(entrypoint)]
  subcommand = invocation.get("subcommand")
  if subcommand:
    parts.append(str(subcommand))
  options = invocation.get("options")
  if isinstance(options, list):
    parts.extend(str(option) for option in options)
  return [" ".join(parts)]
