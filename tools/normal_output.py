"""正常系 human output を短くそろえるための helper。"""

from typing import Any, Dict, Iterable, Optional


def _format_value(value: Any) -> str:
  text = str(value)
  return text.replace("\n", "\\n")


def _format_fields(fields: Optional[Dict[str, Any]]) -> str:
  if not fields:
    return ""
  parts = [
    f"{key}={_format_value(value)}"
    for key, value in fields.items()
    if value is not None
  ]
  return " " + " ".join(parts) if parts else ""


def status_line(verdict: str, action: str, fields: Optional[Dict[str, Any]] = None) -> str:
  return f"[{verdict}] {action}{_format_fields(fields)}\n"


def join_values(values: Iterable[Any]) -> str:
  return ",".join(str(value) for value in values)
