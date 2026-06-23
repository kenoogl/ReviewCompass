"""Work backlog helpers for pre-workflow candidate records."""

from datetime import datetime, timezone
from pathlib import Path

import yaml

from check_workflow_action import work_checklist, work_unit_stack


DEFAULT_BACKLOG_INDEX_PATH = ".reviewcompass/backlog/index.yaml"
BACKLOG_ROOT = ".reviewcompass/backlog"
CHECKLIST_RUNTIME_DIR = ".reviewcompass/runtime/work-units/checklists"
CHECKLIST_EVIDENCE_DIR = ".reviewcompass/evidence/work-units/checklists"
INDEX_SCHEMA_VERSION = "reviewcompass-backlog-index-v1"
ITEM_SCHEMA_VERSION = "reviewcompass-backlog-item-v1"
KIND_DIRECTORIES = {
  "plan": "plans",
  "issue": "issues",
  "todo": "todos",
}
RESERVED_ITEM_FIELDS = {
  "schema_version",
  "id",
  "kind",
  "title",
  "status",
  "source_unit_id",
  "created_at",
  "index_path",
  "provenance",
  "decisions",
}


def _now_iso():
  return datetime.now(timezone.utc).isoformat()


def _result(verdict, reasons, index=None, item=None, path=None):
  response = {
    "verdict": verdict,
    "reasons": reasons,
  }
  if index is not None:
    response["index"] = index
  if item is not None:
    response["item"] = item
  if path is not None:
    response["path"] = str(path)
  return response


def _index_path(cwd):
  return Path(cwd) / DEFAULT_BACKLOG_INDEX_PATH


def _relative_item_path(kind, item_id):
  return f"{BACKLOG_ROOT}/{KIND_DIRECTORIES[kind]}/{item_id}.yaml"


def _item_path(cwd, kind, item_id):
  return Path(cwd) / _relative_item_path(kind, item_id)


def _write_yaml(path, data):
  path.parent.mkdir(parents=True, exist_ok=True)
  path.write_text(
    yaml.safe_dump(data, allow_unicode=True, sort_keys=False),
    encoding="utf-8",
  )


def _empty_index():
  return {
    "schema_version": INDEX_SCHEMA_VERSION,
    "items": [],
  }


def _read_yaml(path, label):
  try:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
  except (OSError, UnicodeDecodeError, yaml.YAMLError) as exc:
    return None, [f"{label} を読めません: {path}: {exc}"]
  if not isinstance(data, dict):
    return None, [f"{label} は mapping である必要があります"]
  return data, []


def _read_body_file(body_file):
  if body_file is None:
    return {}, []
  data, reasons = _read_yaml(Path(body_file), "backlog body file")
  if reasons:
    return {}, reasons
  reserved = sorted(RESERVED_ITEM_FIELDS.intersection(data))
  if reserved:
    return {}, [
      "backlog body file は予約済み item fields を上書きできません: "
      + ", ".join(reserved)
    ]
  return data, []


def _read_index(cwd):
  path = _index_path(cwd)
  if not path.exists():
    return _empty_index(), []
  index, reasons = _read_yaml(path, "backlog index")
  if reasons:
    return _empty_index(), reasons
  if index.get("schema_version") != INDEX_SCHEMA_VERSION:
    return index, ["schema_version は reviewcompass-backlog-index-v1 である必要があります"]
  if not isinstance(index.get("items"), list):
    return index, ["items は list である必要があります"]
  return index, []


def _write_index(cwd, index):
  _write_yaml(_index_path(cwd), index)


def _index_entry(index, item_id):
  for entry in index.get("items", []):
    if isinstance(entry, dict) and entry.get("id") == item_id:
      return entry
  return None


def _read_item_by_entry(cwd, entry):
  path = Path(cwd) / entry["path"]
  item, reasons = _read_yaml(path, "backlog item")
  if reasons:
    return None, reasons
  if item.get("schema_version") != ITEM_SCHEMA_VERSION:
    return item, ["schema_version は reviewcompass-backlog-item-v1 である必要があります"]
  return item, []


def _add(cwd, kind, item_id, title, source_unit_id, source_ref, reason, body_file=None):
  reasons = []
  if kind not in KIND_DIRECTORIES:
    reasons.append(f"invalid kind: {kind}")
  if not item_id:
    reasons.append("id が必要です")
  if not title:
    reasons.append("title が必要です")
  if not source_unit_id:
    reasons.append("source_unit_id が必要です")
  if not source_ref:
    reasons.append("source_ref が必要です")
  if not reason:
    reasons.append("reason が必要です")
  body, body_reasons = _read_body_file(body_file)
  reasons.extend(body_reasons)
  index, index_reasons = _read_index(cwd)
  reasons.extend(index_reasons)
  if _index_entry(index, item_id) is not None:
    reasons.append(f"backlog item already exists: {item_id}")
  if kind in KIND_DIRECTORIES and _item_path(cwd, kind, item_id).exists():
    reasons.append(f"backlog item file already exists: {item_id}")
  if reasons:
    return _result("DEVIATION", reasons, index=index)

  created_at = _now_iso()
  relative_path = _relative_item_path(kind, item_id)
  item = {
    "schema_version": ITEM_SCHEMA_VERSION,
    "id": item_id,
    "kind": kind,
    "title": title,
    "status": "candidate",
    "source_unit_id": source_unit_id,
    "created_at": created_at,
    "index_path": DEFAULT_BACKLOG_INDEX_PATH,
    "provenance": {
      "created_by": "llm",
      "source_ref": source_ref,
      "reason": reason,
    },
    "decisions": [],
  }
  item.update(body)
  entry = {
    "id": item_id,
    "kind": kind,
    "title": title,
    "status": "candidate",
    "path": relative_path,
    "source_unit_id": source_unit_id,
    "created_at": created_at,
  }
  index["items"].append(entry)
  _write_yaml(_item_path(cwd, kind, item_id), item)
  _write_index(cwd, index)
  return _result("OK", [], index=index, item=item, path=relative_path)


def add_plan(cwd, item_id, title, source_unit_id, source_ref, reason, body_file=None):
  return _add(
    cwd,
    "plan",
    item_id,
    title,
    source_unit_id,
    source_ref,
    reason,
    body_file=body_file,
  )


def add_issue(cwd, item_id, title, source_unit_id, source_ref, reason):
  return _add(cwd, "issue", item_id, title, source_unit_id, source_ref, reason)


def add_todo(cwd, item_id, title, source_unit_id, source_ref, reason):
  return _add(cwd, "todo", item_id, title, source_unit_id, source_ref, reason)


def list_items(cwd):
  index, reasons = _read_index(cwd)
  return _result("DEVIATION" if reasons else "OK", reasons, index=index)


def show(cwd, item_id):
  index, reasons = _read_index(cwd)
  entry = _index_entry(index, item_id)
  if entry is None:
    reasons.append(f"backlog item not found: {item_id}")
  if reasons:
    return _result("DEVIATION", reasons, index=index)
  item, item_reasons = _read_item_by_entry(cwd, entry)
  if item_reasons:
    return _result("DEVIATION", item_reasons, index=index)
  return _result("OK", [], index=index, item=item, path=entry["path"])


def _select_single_promoted_todo(cwd):
  index, reasons = _read_index(cwd)
  if reasons:
    return None, _result("DEVIATION", reasons, index=index)
  promoted = [
    entry
    for entry in index.get("items", [])
    if (
      isinstance(entry, dict)
      and entry.get("kind") == "todo"
      and entry.get("status") == "promoted"
    )
  ]
  if len(promoted) == 1:
    return promoted[0]["id"], None
  if not promoted:
    return None, _result("DEVIATION", ["no promoted todo item found"], index=index)
  ids = ", ".join(entry.get("id", "<unknown>") for entry in promoted)
  return None, _result("DEVIATION", [f"multiple promoted todo items: {ids}"], index=index)


def _checklist_items_from_backlog_item(item):
  generated = []
  for index, task in enumerate(item.get("tasks", []), start=1):
    if isinstance(task, str):
      generated.append({
        "id": f"T-{index}",
        "title": task,
      })
    elif isinstance(task, dict) and task.get("title"):
      generated.append({
        "id": task.get("id") or f"T-{index}",
        "title": task["title"],
      })

  for phase in item.get("implementation_plan", {}).get("phases", []):
    if not isinstance(phase, dict):
      continue
    phase_id = phase.get("id")
    if not phase_id:
      continue
    for index, task in enumerate(phase.get("tasks", []), start=1):
      if isinstance(task, str):
        generated.append({
          "id": f"{phase_id}-{index}",
          "title": task,
        })
      elif isinstance(task, dict) and task.get("title"):
        generated.append({
          "id": task.get("id") or f"{phase_id}-{index}",
          "title": task["title"],
        })

  todos = item.get("todos", {})
  if isinstance(todos, dict):
    for entries in todos.values():
      if not isinstance(entries, list):
        continue
      for entry in entries:
        if isinstance(entry, dict) and entry.get("id") and entry.get("title"):
          generated.append({
            "id": entry["id"],
            "title": entry["title"],
          })

  for red_test in item.get("red_tests", []):
    if isinstance(red_test, dict) and red_test.get("id") and red_test.get("title"):
      generated.append({
        "id": red_test["id"],
        "title": red_test["title"],
      })
  return generated


def _default_checklist_id(item_id):
  return f"checklist-{item_id}"


def _active_or_source_unit_id(cwd, item):
  current = work_unit_stack.current(cwd)
  if current.get("verdict") == "OK" and isinstance(current.get("current"), dict):
    unit_id = current["current"].get("unit_id")
    if unit_id:
      return unit_id
  return item.get("source_unit_id")


def start_checklist(cwd, item_id, checklist_id, unit_id):
  if not item_id:
    item_id, selection_result = _select_single_promoted_todo(cwd)
    if selection_result is not None:
      return selection_result
  shown = show(cwd, item_id)
  if shown["verdict"] != "OK":
    return shown
  item = shown["item"]
  if item.get("kind") != "todo":
    return _result("DEVIATION", [f"backlog item は todo である必要があります: {item_id}"])

  checklist_items = _checklist_items_from_backlog_item(item)
  if not checklist_items:
    return _result("DEVIATION", [f"checklist item に変換できる項目がありません: {item_id}"])

  if not checklist_id:
    checklist_id = _default_checklist_id(item_id)
  if not unit_id:
    unit_id = _active_or_source_unit_id(cwd, item)

  response = work_checklist.start_with_items(
    cwd,
    checklist_id,
    unit_id,
    item.get("title") or item_id,
    shown["path"],
    "backlog TODO から runtime checklist を機械生成する",
    checklist_items,
    source_backlog_item_id=item_id,
    source_backlog_path=shown["path"],
  )
  response["index"] = shown["index"]
  response["item"] = item
  return response


def _find_checklist(cwd, item_id, checklist_id=None):
  for directory in (CHECKLIST_RUNTIME_DIR, CHECKLIST_EVIDENCE_DIR):
    root = Path(cwd) / directory
    if not root.exists():
      continue
    if checklist_id:
      path = root / f"{checklist_id}.yaml"
      if path.exists():
        checklist, reasons = _read_yaml(path, "checklist")
        if reasons:
          return None, None, reasons
        return checklist, path, []
      continue
    for path in sorted(root.glob("*.yaml")):
      checklist, reasons = _read_yaml(path, "checklist")
      if reasons:
        continue
      if checklist.get("source_backlog_item_id") == item_id:
        return checklist, path, []
  return None, None, [f"checklist not found for backlog item: {item_id}"]


def audit_checklist_coverage(cwd, item_id, checklist_id=None):
  if not item_id:
    item_id, selection_result = _select_single_promoted_todo(cwd)
    if selection_result is not None:
      return selection_result
  shown = show(cwd, item_id)
  if shown["verdict"] != "OK":
    return shown
  expected = _checklist_items_from_backlog_item(shown["item"])
  checklist, path, reasons = _find_checklist(cwd, item_id, checklist_id)
  if reasons:
    return _result("DEVIATION", reasons, index=shown["index"], item=shown["item"])

  expected_ids = [item["id"] for item in expected]
  actual_ids = [
    item.get("id")
    for item in checklist.get("items", [])
    if isinstance(item, dict)
  ]
  missing = [item_id for item_id in expected_ids if item_id not in actual_ids]
  extra = [item_id for item_id in actual_ids if item_id not in expected_ids]
  reasons = []
  if missing:
    reasons.append("missing checklist items: " + ", ".join(missing))
  response = _result(
    "DEVIATION" if reasons else "OK",
    reasons,
    index=shown["index"],
    item=shown["item"],
    path=str(path.relative_to(Path(cwd))),
  )
  response["coverage"] = {
    "expected_count": len(expected_ids),
    "actual_count": len(actual_ids),
    "missing_item_ids": missing,
    "extra_item_ids": extra,
    "semantic_review": {
      "triad_review_applicable": True,
      "reason": "機械的 coverage が OK の後、意味的十分性は 3者レビューで確認できる",
    },
  }
  return response


def _checklist_has_source(path, item_id):
  checklist, reasons = _read_yaml(path, "checklist")
  if reasons:
    return False
  return checklist.get("source_backlog_item_id") == item_id


def _todo_links_plan(todo, plan_id, plan_path):
  if todo.get("source_plan_id") == plan_id:
    return True
  if todo.get("source_plan_path") == plan_path:
    return True
  if todo.get("parent_plan_id") == plan_id:
    return True
  provenance = todo.get("provenance") if isinstance(todo.get("provenance"), dict) else {}
  source_ref = provenance.get("source_ref")
  if isinstance(source_ref, str):
    return plan_id in source_ref or plan_path in source_ref
  return False


def _has_linked_todo(cwd, index, plan_id, plan_path):
  for entry in index.get("items", []):
    if not isinstance(entry, dict):
      continue
    if entry.get("kind") != "todo":
      continue
    todo, reasons = _read_item_by_entry(cwd, entry)
    if reasons:
      continue
    if _todo_links_plan(todo, plan_id, plan_path):
      return True
  return False


def _has_runtime_or_evidence_checklist(cwd, item_id):
  for directory in (CHECKLIST_RUNTIME_DIR, CHECKLIST_EVIDENCE_DIR):
    root = Path(cwd) / directory
    if not root.exists():
      continue
    for path in sorted(root.glob("*.yaml")):
      if _checklist_has_source(path, item_id):
        return True
  return False


def audit_checklist_bridge(cwd):
  index, reasons = _read_index(cwd)
  if reasons:
    return _result("DEVIATION", reasons, index=index)

  for entry in index.get("items", []):
    if not isinstance(entry, dict):
      continue
    if entry.get("kind") != "todo" or entry.get("status") not in {"promoted", "active"}:
      continue
    item, item_reasons = _read_item_by_entry(cwd, entry)
    if item_reasons:
      reasons.extend(item_reasons)
      continue
    if item.get("execution_history"):
      continue
    if not _has_runtime_or_evidence_checklist(cwd, entry["id"]):
      reasons.append(
        f"{entry['id']} has no active checklist or checklist evidence"
      )

  return _result("DEVIATION" if reasons else "OK", reasons, index=index)


def audit_plan_todo_bridge(cwd):
  index, reasons = _read_index(cwd)
  if reasons:
    return _result("DEVIATION", reasons, index=index)

  for entry in index.get("items", []):
    if not isinstance(entry, dict):
      continue
    if entry.get("kind") != "plan" or entry.get("status") not in {"promoted", "active"}:
      continue
    item, item_reasons = _read_item_by_entry(cwd, entry)
    if item_reasons:
      reasons.extend(item_reasons)
      continue
    if item.get("execution_history"):
      continue
    plan_id = entry["id"]
    plan_path = entry.get("path") or _relative_item_path("plan", plan_id)
    if _has_linked_todo(cwd, index, plan_id, plan_path):
      continue
    if _has_runtime_or_evidence_checklist(cwd, plan_id):
      continue
    reasons.append(
      f"{plan_id} has no linked TODO/checklist evidence"
    )

  return _result("DEVIATION" if reasons else "OK", reasons, index=index)


def _decide(cwd, item_id, decision, decision_ref, reason):
  index, reasons = _read_index(cwd)
  entry = _index_entry(index, item_id)
  if entry is None:
    reasons.append(f"backlog item not found: {item_id}")
  if not decision_ref:
    reasons.append("decision_ref が必要です")
  if not reason:
    reasons.append("reason が必要です")
  if reasons:
    return _result("DEVIATION", reasons, index=index)
  item, item_reasons = _read_item_by_entry(cwd, entry)
  if item_reasons:
    return _result("DEVIATION", item_reasons, index=index)

  item["status"] = decision
  entry["status"] = decision
  item.setdefault("decisions", []).append({
    "decision": decision,
    "decision_ref": decision_ref,
    "reason": reason,
    "decided_at": _now_iso(),
  })
  _write_yaml(Path(cwd) / entry["path"], item)
  _write_index(cwd, index)
  return _result("OK", [], index=index, item=item, path=entry["path"])


def promote(cwd, item_id, decision_ref, reason):
  return _decide(cwd, item_id, "promoted", decision_ref, reason)


def complete(cwd, item_id, decision_ref, reason):
  return _decide(cwd, item_id, "completed", decision_ref, reason)


def reject(cwd, item_id, decision_ref, reason):
  return _decide(cwd, item_id, "rejected", decision_ref, reason)
