"""Work checklist helpers for per-unit execution lists."""

from datetime import datetime, timezone
from pathlib import Path

import yaml


DEFAULT_CHECKLIST_DIR = ".reviewcompass/runtime/work-units/checklists"
DEFAULT_CHECKLIST_EVIDENCE_DIR = ".reviewcompass/evidence/work-units/checklists"
DEFAULT_BACKLOG_ROOT = ".reviewcompass/backlog"
DEFAULT_BACKLOG_INDEX_PATH = ".reviewcompass/backlog/index.yaml"
SCHEMA_VERSION = "work-checklist-v1"
ALLOWED_ITEM_STATUSES = {"pending", "active", "done", "blocked"}
STATUS_MARKERS = {
  "done": "[x]",
  "active": "[>]",
  "pending": "[ ]",
  "blocked": "[!]",
}


def _now_iso():
  return datetime.now(timezone.utc).isoformat()


def _result(verdict, reasons, checklist=None, path=None, evidence_path=None):
  response = {
    "verdict": verdict,
    "reasons": reasons,
  }
  if checklist is not None:
    response["checklist"] = checklist
  if path is not None:
    response["path"] = str(path)
  if evidence_path is not None:
    response["evidence_path"] = str(evidence_path)
  return response


def _checklist_path(cwd, checklist_id):
  return Path(cwd) / DEFAULT_CHECKLIST_DIR / f"{checklist_id}.yaml"


def _evidence_path(cwd, checklist_id):
  return Path(cwd) / DEFAULT_CHECKLIST_EVIDENCE_DIR / f"{checklist_id}.yaml"


def _relative_checklist_path(checklist_id):
  return Path(DEFAULT_CHECKLIST_DIR) / f"{checklist_id}.yaml"


def _relative_evidence_path(checklist_id):
  return Path(DEFAULT_CHECKLIST_EVIDENCE_DIR) / f"{checklist_id}.yaml"


def _write_yaml(path, data):
  path.parent.mkdir(parents=True, exist_ok=True)
  path.write_text(
    yaml.safe_dump(data, allow_unicode=True, sort_keys=False),
    encoding="utf-8",
  )


def _read_checklist(cwd, checklist_id):
  path = _checklist_path(cwd, checklist_id)
  if not path.exists():
    return None, [f"checklist not found: {checklist_id}"]
  try:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
  except (OSError, UnicodeDecodeError, yaml.YAMLError) as exc:
    return None, [f"checklist を読めません: {path}: {exc}"]
  if not isinstance(data, dict):
    return None, ["checklist は mapping である必要があります"]
  if data.get("schema_version") != SCHEMA_VERSION:
    return None, ["schema_version は work-checklist-v1 である必要があります"]
  if not isinstance(data.get("items"), list):
    return None, ["items は list である必要があります"]
  return data, []


def _find_item(checklist, item_id):
  for item in checklist.get("items", []):
    if isinstance(item, dict) and item.get("id") == item_id:
      return item
  return None


def _progress(checklist):
  progress = {
    "total": 0,
    "done": 0,
    "active": 0,
    "pending": 0,
    "blocked": 0,
    "active_item_ids": [],
    "blocked_item_ids": [],
  }
  for item in checklist.get("items", []):
    if not isinstance(item, dict):
      continue
    progress["total"] += 1
    status = item.get("status")
    if status in {"done", "active", "pending", "blocked"}:
      progress[status] += 1
    if status == "active":
      progress["active_item_ids"].append(item.get("id"))
    elif status == "blocked":
      progress["blocked_item_ids"].append(item.get("id"))
  return progress


def _normalize_checklist(checklist):
  for item in checklist.get("items", []):
    if not isinstance(item, dict):
      continue
    item["checked"] = item.get("status") == "done"
  checklist["progress"] = _progress(checklist)
  return checklist


def _write_checklist(path, checklist):
  _write_yaml(path, _normalize_checklist(checklist))


def _item_record(item_id, title):
  return {
    "id": item_id,
    "title": title,
    "status": "pending",
    "checked": False,
    "child_checklist_id": None,
  }


def _display_lines(checklist):
  lines = []
  for item in checklist.get("items", []):
    if not isinstance(item, dict):
      continue
    marker = STATUS_MARKERS.get(item.get("status"), "[?]")
    lines.append(f"{marker} {item.get('id')} {item.get('title')}")
  return lines


def start(cwd, checklist_id, unit_id, title, source_ref, reason):
  return start_with_items(
    cwd,
    checklist_id,
    unit_id,
    title,
    source_ref,
    reason,
    items=[],
  )


def start_with_items(
  cwd,
  checklist_id,
  unit_id,
  title,
  source_ref,
  reason,
  items,
  source_backlog_item_id=None,
  source_backlog_path=None,
):
  reasons = []
  if not checklist_id:
    reasons.append("checklist_id が必要です")
  if not unit_id:
    reasons.append("unit_id が必要です")
  if not title:
    reasons.append("title が必要です")
  if not source_ref:
    reasons.append("source_ref が必要です")
  if not reason:
    reasons.append("reason が必要です")
  path = _checklist_path(cwd, checklist_id)
  if path.exists():
    reasons.append(f"checklist already exists: {checklist_id}")
  for item in items:
    if not isinstance(item, dict):
      reasons.append("items は mapping の list である必要があります")
      continue
    if not item.get("id"):
      reasons.append("item id が必要です")
    if not item.get("title"):
      reasons.append("item title が必要です")
  if reasons:
    return _result("DEVIATION", reasons)

  checklist = {
    "schema_version": SCHEMA_VERSION,
    "checklist_id": checklist_id,
    "unit_id": unit_id,
    "title": title,
    "status": "active",
    "created_at": _now_iso(),
    "provenance": {
      "created_by": "llm",
      "source_ref": source_ref,
      "reason": reason,
    },
    "items": [
      _item_record(item["id"], item["title"])
      for item in items
      if isinstance(item, dict)
    ],
  }
  if source_backlog_item_id is not None:
    checklist["source_backlog_item_id"] = source_backlog_item_id
  if source_backlog_path is not None:
    checklist["source_backlog_path"] = source_backlog_path
  _write_checklist(path, checklist)
  return _result(
    "OK",
    [],
    checklist=checklist,
    path=_relative_checklist_path(checklist_id),
  )


def show(cwd, checklist_id):
  checklist, reasons = _read_checklist(cwd, checklist_id)
  if reasons:
    return _result("DEVIATION", reasons)
  _write_checklist(_checklist_path(cwd, checklist_id), checklist)
  response = _result(
    "OK",
    [],
    checklist=checklist,
    path=_relative_checklist_path(checklist_id),
  )
  response["progress"] = checklist["progress"]
  response["display_lines"] = _display_lines(checklist)
  return response


def add_item(cwd, checklist_id, item_id, title):
  checklist, reasons = _read_checklist(cwd, checklist_id)
  if reasons:
    return _result("DEVIATION", reasons)
  if not item_id:
    reasons.append("item_id が必要です")
  if not title:
    reasons.append("title が必要です")
  if _find_item(checklist, item_id) is not None:
    reasons.append(f"item already exists: {item_id}")
  if reasons:
    return _result("DEVIATION", reasons, checklist=checklist)

  checklist["items"].append({
    **_item_record(item_id, title),
  })
  _write_checklist(_checklist_path(cwd, checklist_id), checklist)
  return _result(
    "OK",
    [],
    checklist=checklist,
    path=_relative_checklist_path(checklist_id),
  )


def set_status(cwd, checklist_id, item_id, status):
  checklist, reasons = _read_checklist(cwd, checklist_id)
  if reasons:
    return _result("DEVIATION", reasons)
  if status not in ALLOWED_ITEM_STATUSES:
    reasons.append(f"invalid status: {status}")
  item = _find_item(checklist, item_id)
  if item is None:
    reasons.append(f"item not found: {item_id}")
  if reasons:
    return _result("DEVIATION", reasons, checklist=checklist)

  item["status"] = status
  _write_checklist(_checklist_path(cwd, checklist_id), checklist)
  return _result(
    "OK",
    [],
    checklist=checklist,
    path=_relative_checklist_path(checklist_id),
  )


def branch(cwd, checklist_id, item_id, child_checklist_id, child_title, source_ref, reason):
  checklist, reasons = _read_checklist(cwd, checklist_id)
  if reasons:
    return _result("DEVIATION", reasons)
  item = _find_item(checklist, item_id)
  if item is None:
    reasons.append(f"item not found: {item_id}")
  elif item.get("status") != "blocked":
    reasons.append("branch requires blocked item")
  if not child_checklist_id:
    reasons.append("child_checklist_id が必要です")
  if not child_title:
    reasons.append("child_title が必要です")
  child_path = _checklist_path(cwd, child_checklist_id)
  if child_path.exists():
    reasons.append(f"child checklist already exists: {child_checklist_id}")
  if reasons:
    return _result("DEVIATION", reasons, checklist=checklist)

  item["child_checklist_id"] = child_checklist_id
  child = {
    "schema_version": SCHEMA_VERSION,
    "checklist_id": child_checklist_id,
    "unit_id": checklist["unit_id"],
    "title": child_title,
    "status": "active",
    "created_at": _now_iso(),
    "parent_checklist_id": checklist_id,
    "parent_item_id": item_id,
    "provenance": {
      "created_by": "llm",
      "source_ref": source_ref,
      "reason": reason,
    },
    "items": [],
  }
  _write_checklist(_checklist_path(cwd, checklist_id), checklist)
  _write_checklist(child_path, child)
  response = _result(
    "OK",
    [],
    checklist=checklist,
    path=_relative_checklist_path(checklist_id),
  )
  response["child_checklist"] = child
  response["child_path"] = str(_relative_checklist_path(child_checklist_id))
  return response


def _record_backlog_execution(cwd, checklist, evidence_path):
  source_path = checklist.get("source_backlog_path")
  source_id = checklist.get("source_backlog_item_id")
  if not source_path or not source_id:
    return []
  backlog_path = Path(cwd) / source_path
  if not str(source_path).startswith(DEFAULT_BACKLOG_ROOT + "/"):
    return [f"source_backlog_path is outside backlog root: {source_path}"]
  try:
    item = yaml.safe_load(backlog_path.read_text(encoding="utf-8"))
  except (OSError, UnicodeDecodeError, yaml.YAMLError) as exc:
    return [f"source backlog item を読めません: {source_path}: {exc}"]
  if not isinstance(item, dict):
    return [f"source backlog item は mapping である必要があります: {source_path}"]
  if item.get("id") != source_id:
    return [f"source backlog item id mismatch: {source_id}"]
  index, index_reasons = _completed_backlog_index(cwd, source_id, source_path)
  if index_reasons:
    return index_reasons

  done_item_ids = {
    checklist_item.get("id")
    for checklist_item in checklist.get("items", [])
    if isinstance(checklist_item, dict) and checklist_item.get("status") == "done"
  }
  _mark_matching_backlog_items_done(item, done_item_ids)
  item.setdefault("execution_history", []).append({
    "checklist_id": checklist["checklist_id"],
    "evidence_path": str(evidence_path),
    "completion_summary": checklist["completion_summary"],
    "completed_at": checklist["completed_at"],
  })
  item["status"] = "completed"
  _write_yaml(backlog_path, item)
  _write_yaml(Path(cwd) / DEFAULT_BACKLOG_INDEX_PATH, index)
  return []


def _completed_backlog_index(cwd, source_id, source_path):
  index_path = Path(cwd) / DEFAULT_BACKLOG_INDEX_PATH
  try:
    index = yaml.safe_load(index_path.read_text(encoding="utf-8"))
  except (OSError, UnicodeDecodeError, yaml.YAMLError) as exc:
    return None, [f"backlog index を読めません: {DEFAULT_BACKLOG_INDEX_PATH}: {exc}"]
  if not isinstance(index, dict):
    return None, ["backlog index は mapping である必要があります"]
  if index.get("schema_version") != "reviewcompass-backlog-index-v1":
    return None, ["backlog index schema_version は reviewcompass-backlog-index-v1 である必要があります"]
  if not isinstance(index.get("items"), list):
    return None, ["backlog index items は list である必要があります"]
  for entry in index.get("items", []):
    if not isinstance(entry, dict) or entry.get("id") != source_id:
      continue
    if entry.get("path") != source_path:
      return None, [
        f"backlog index item path mismatch: {source_id}: "
        f"{entry.get('path')} != {source_path}"
      ]
    entry["status"] = "completed"
    return index, []
  return None, [f"backlog index item not found: {source_id}"]


def _mark_matching_backlog_items_done(backlog_item, done_item_ids):
  todos = backlog_item.get("todos")
  if isinstance(todos, dict):
    for entries in todos.values():
      if not isinstance(entries, list):
        continue
      for entry in entries:
        if isinstance(entry, dict) and entry.get("id") in done_item_ids:
          entry["status"] = "done"

  for red_test in backlog_item.get("red_tests", []):
    if isinstance(red_test, dict) and red_test.get("id") in done_item_ids:
      red_test["status"] = "done"

  phases = backlog_item.get("implementation_plan", {}).get("phases", [])
  for phase in phases:
    if not isinstance(phase, dict):
      continue
    for task in phase.get("tasks", []):
      if isinstance(task, dict) and task.get("id") in done_item_ids:
        task["status"] = "done"


def _completion_summary(checklist):
  progress = _progress(checklist)
  return (
    f"{checklist['checklist_id']} completed "
    f"{progress['done']}/{progress['total']} items"
  )


def close(cwd, checklist_id, completion_summary):
  checklist, reasons = _read_checklist(cwd, checklist_id)
  if reasons:
    return _result("DEVIATION", reasons)
  unfinished = [
    item.get("id")
    for item in checklist.get("items", [])
    if isinstance(item, dict) and item.get("status") != "done"
  ]
  if unfinished:
    reasons.append(f"unfinished items: {', '.join(unfinished)}")
  if reasons:
    return _result("DEVIATION", reasons, checklist=checklist)

  checklist["status"] = "completed"
  checklist["completed_at"] = _now_iso()
  if not completion_summary:
    completion_summary = _completion_summary(checklist)
  checklist["completion_summary"] = completion_summary
  evidence_path = _evidence_path(cwd, checklist_id)
  runtime_path = _checklist_path(cwd, checklist_id)
  _normalize_checklist(checklist)
  _write_yaml(evidence_path, checklist)
  reasons.extend(_record_backlog_execution(cwd, checklist, _relative_evidence_path(checklist_id)))
  if reasons:
    return _result("DEVIATION", reasons, checklist=checklist)
  runtime_path.unlink()
  return _result(
    "OK",
    [],
    checklist=checklist,
    path=_relative_evidence_path(checklist_id),
    evidence_path=_relative_evidence_path(checklist_id),
  )
