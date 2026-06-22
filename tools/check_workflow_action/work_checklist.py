"""Work checklist helpers for per-unit execution lists."""

from datetime import datetime, timezone
from pathlib import Path

import yaml


DEFAULT_CHECKLIST_DIR = ".reviewcompass/runtime/work-units/checklists"
DEFAULT_CHECKLIST_EVIDENCE_DIR = ".reviewcompass/evidence/work-units/checklists"
SCHEMA_VERSION = "work-checklist-v1"
ALLOWED_ITEM_STATUSES = {"pending", "active", "done", "blocked"}


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


def start(cwd, checklist_id, unit_id, title, source_ref, reason):
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
    "items": [],
  }
  _write_yaml(path, checklist)
  return _result(
    "OK",
    [],
    checklist=checklist,
    path=_relative_checklist_path(checklist_id),
  )


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
    "id": item_id,
    "title": title,
    "status": "pending",
    "child_checklist_id": None,
  })
  _write_yaml(_checklist_path(cwd, checklist_id), checklist)
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
  _write_yaml(_checklist_path(cwd, checklist_id), checklist)
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
  _write_yaml(_checklist_path(cwd, checklist_id), checklist)
  _write_yaml(child_path, child)
  response = _result(
    "OK",
    [],
    checklist=checklist,
    path=_relative_checklist_path(checklist_id),
  )
  response["child_checklist"] = child
  response["child_path"] = str(_relative_checklist_path(child_checklist_id))
  return response


def close(cwd, checklist_id, completion_summary):
  checklist, reasons = _read_checklist(cwd, checklist_id)
  if reasons:
    return _result("DEVIATION", reasons)
  if not completion_summary:
    reasons.append("completion_summary が必要です")
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
  checklist["completion_summary"] = completion_summary
  evidence_path = _evidence_path(cwd, checklist_id)
  _write_yaml(evidence_path, checklist)
  _write_yaml(_checklist_path(cwd, checklist_id), checklist)
  return _result(
    "OK",
    [],
    checklist=checklist,
    path=_relative_checklist_path(checklist_id),
    evidence_path=_relative_evidence_path(checklist_id),
  )
