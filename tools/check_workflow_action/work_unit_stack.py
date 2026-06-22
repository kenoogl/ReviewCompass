"""Work unit stack helpers for mechanized blocking-unit entry and exit."""

from datetime import datetime, timezone
from pathlib import Path

import yaml


DEFAULT_WORK_UNIT_STACK_PATH = ".reviewcompass/runtime/work-units/stack.yaml"
DEFAULT_BLOCKING_EVIDENCE_DIR = ".reviewcompass/evidence/work-units/blocking-units"
SCHEMA_VERSION = "work-unit-stack-v1"


def _now_iso():
  return datetime.now(timezone.utc).isoformat()


def empty_stack():
  return {
    "schema_version": SCHEMA_VERSION,
    "frames": [],
  }


def _result(verdict, reasons, stack=None, current=None):
  response = {
    "verdict": verdict,
    "reasons": reasons,
  }
  if stack is not None:
    response["stack"] = stack
  if "current" not in response:
    response["current"] = current
  return response


def _read_yaml(path, default):
  path = Path(path)
  if not path.exists():
    return default, []
  try:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
  except (OSError, UnicodeDecodeError, yaml.YAMLError) as exc:
    return default, [f"work unit stack を読めません: {path}: {exc}"]
  if data is None:
    return default, []
  if not isinstance(data, dict):
    return default, ["work unit stack は mapping である必要があります"]
  data.setdefault("schema_version", SCHEMA_VERSION)
  data.setdefault("frames", [])
  return data, []


def _write_yaml(path, data):
  path = Path(path)
  path.parent.mkdir(parents=True, exist_ok=True)
  path.write_text(
    yaml.safe_dump(data, allow_unicode=True, sort_keys=False),
    encoding="utf-8",
  )


def _stack_path(cwd, path=None):
  return Path(cwd) / (path or DEFAULT_WORK_UNIT_STACK_PATH)


def _evidence_path(cwd, unit_id):
  return Path(cwd) / DEFAULT_BLOCKING_EVIDENCE_DIR / f"{unit_id}.yaml"


def current(cwd, path=None):
  stack, reasons = _read_yaml(_stack_path(cwd, path), empty_stack())
  frames = stack.get("frames")
  current_frame = frames[-1] if isinstance(frames, list) and frames else None
  return _result(
    "DEVIATION" if reasons else "OK",
    reasons,
    stack=stack,
    current=current_frame,
  )


def _validate_enter_blocking(stack, unit_id, parent_unit_id, title, reason, return_conditions):
  reasons = []
  if not unit_id:
    reasons.append("unit_id が必要です")
  if not parent_unit_id:
    reasons.append("parent_unit_id が必要です")
  if not title:
    reasons.append("title が必要です")
  if not reason:
    reasons.append("reason が必要です")
  if not return_conditions:
    reasons.append("return_condition が 1 件以上必要です")
  frames = stack.get("frames")
  if not isinstance(frames, list):
    reasons.append("frames は list である必要があります")
  elif any(frame.get("unit_id") == unit_id for frame in frames if isinstance(frame, dict)):
    reasons.append(f"unit_id は既に stack に存在します: {unit_id}")
  return reasons


def enter_blocking(
  cwd,
  unit_id,
  parent_unit_id,
  title,
  reason,
  return_conditions,
  path=None,
):
  stack_path = _stack_path(cwd, path)
  stack, reasons = _read_yaml(stack_path, empty_stack())
  reasons.extend(
    _validate_enter_blocking(
      stack,
      unit_id,
      parent_unit_id,
      title,
      reason,
      return_conditions,
    )
  )
  if reasons:
    return _result("DEVIATION", reasons, stack=stack)

  frame = {
    "unit_id": unit_id,
    "kind": "blocking",
    "parent_unit_id": parent_unit_id,
    "title": title,
    "reason": reason,
    "status": "active",
    "entered_at": _now_iso(),
    "return_conditions": list(return_conditions),
  }
  stack["frames"].append(frame)
  _write_yaml(stack_path, stack)
  response = _result("OK", [], stack=stack, current=frame)
  response["path"] = str(Path(path or DEFAULT_WORK_UNIT_STACK_PATH))
  return response


def exit_blocking(cwd, unit_id, completion_summary, path=None):
  stack_path = _stack_path(cwd, path)
  stack, reasons = _read_yaml(stack_path, empty_stack())
  frames = stack.get("frames")
  if not isinstance(frames, list):
    reasons.append("frames は list である必要があります")
  elif not frames:
    reasons.append("work unit stack が空です")
  else:
    top = frames[-1]
    if top.get("unit_id") != unit_id:
      reasons.append("top work unit だけを exit できます")
    elif top.get("kind") != "blocking":
      reasons.append("blocking unit だけを exit-blocking できます")
  if not completion_summary:
    reasons.append("completion_summary が必要です")
  if reasons:
    return _result("DEVIATION", reasons, stack=stack)

  completed = dict(frames[-1])
  completed["status"] = "completed"
  completed["exited_at"] = _now_iso()
  completed["completion_summary"] = completion_summary
  completed["returned_to"] = {
    "unit_id": completed.get("parent_unit_id"),
  }
  _write_yaml(_evidence_path(cwd, unit_id), completed)

  remaining = dict(stack)
  remaining["frames"] = frames[:-1]
  _write_yaml(stack_path, remaining)
  response = _result(
    "OK",
    [],
    stack=remaining,
    current=remaining["frames"][-1] if remaining["frames"] else None,
  )
  response["completed"] = completed
  response["returned_to"] = completed["returned_to"]
  response["evidence_path"] = str(Path(DEFAULT_BLOCKING_EVIDENCE_DIR) / f"{unit_id}.yaml")
  return response
