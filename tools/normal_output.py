"""正常系 human output を短くそろえるための helper。"""

from typing import Any, Dict, Iterable, Optional


NORMAL_OUTPUT_VERDICTS = [
  "OK",
  "WARN",
  "DEVIATION",
]
NORMAL_OUTPUT_MODES = [
  "human",
  "json",
  "verbose",
]
MAX_HUMAN_REASONS = 3


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


def _summary_fields(record: Dict[str, Any]) -> Dict[str, Any]:
  fields = record.get("summary_fields")
  if isinstance(fields, dict):
    return fields
  return {}


def _details_fields(record: Dict[str, Any]) -> Dict[str, Any]:
  details = record.get("details")
  if isinstance(details, dict):
    return details
  return {}


def _reason_lines(record: Dict[str, Any]) -> Iterable[str]:
  reasons = record.get("reasons")
  if not isinstance(reasons, list):
    return []
  return [
    "reason: " + _format_value(reason)
    for reason in reasons[:MAX_HUMAN_REASONS]
  ]


def render_human_output(record: Dict[str, Any], verbose: bool = False) -> str:
  """判定 record から短い human output を生成する。"""
  verdict = str(record.get("verdict", "OK"))
  action = str(record.get("action", ""))
  if verdict == "OK" and not verbose:
    return status_line(verdict, action, _summary_fields(record))

  lines = [f"[{verdict}] {action}"]
  if verdict == "OK":
    fields = {
      **_summary_fields(record),
      **_details_fields(record),
    }
    suffix = _format_fields(fields)
    if suffix:
      lines[0] += suffix
  else:
    lines.extend(_reason_lines(record))
    next_action = record.get("next_action")
    if next_action:
      lines.append("next: " + _format_value(next_action))
    if verbose:
      details = _details_fields(record)
      if details:
        lines.append("details: " + _format_value(details))
  return "\n".join(lines) + "\n"


def render_json_output(record: Dict[str, Any]) -> Dict[str, Any]:
  """機械可読 output 用に record 全体を保持する。"""
  return dict(record)


def output_stream_for(verdict: str, json_mode: bool = False) -> str:
  """human/json output を出す stream 名を返す。"""
  if json_mode:
    return "stdout"
  if verdict == "OK":
    return "stdout"
  return "stderr"
