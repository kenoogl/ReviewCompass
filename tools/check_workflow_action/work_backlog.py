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


def add_todo(cwd, item_id, title, source_unit_id, source_ref, reason, body_file=None):
  return _add(
    cwd,
    "todo",
    item_id,
    title,
    source_unit_id,
    source_ref,
    reason,
    body_file=body_file,
  )


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


def start_checklist(cwd, item_id, checklist_id, unit_id, mutation_boundary_confirmed=False):
  if not mutation_boundary_confirmed:
    return _result(
      "DEVIATION",
      [
        "mutation boundary confirmation is required before work-backlog start-checklist",
      ],
      item={
        "operation_mode": "mutating",
        "planned_mutation": "create runtime checklist from backlog TODO",
        "required_confirmation": "--mutation-boundary-confirmed",
      },
    )
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


def _linked_todo_entries(cwd, index, plan_id, plan_path):
  linked = []
  reasons = []
  for entry in index.get("items", []):
    if not isinstance(entry, dict):
      continue
    if entry.get("kind") != "todo":
      continue
    todo, item_reasons = _read_item_by_entry(cwd, entry)
    if item_reasons:
      reasons.extend(item_reasons)
      continue
    if _todo_links_plan(todo, plan_id, plan_path):
      source_plan_slice = todo.get("source_plan_slice")
      phase_id = None
      if isinstance(source_plan_slice, dict):
        phase_id = source_plan_slice.get("phase_id")
      linked.append({
        "id": entry.get("id"),
        "path": entry.get("path"),
        "status": entry.get("status"),
        "title": entry.get("title"),
        "source_plan_slice_phase_id": phase_id,
      })
  return linked, reasons


def _implementation_slices(plan):
  implementation_plan = plan.get("implementation_plan")
  entries = []
  if isinstance(implementation_plan, list):
    entries = implementation_plan
  elif isinstance(implementation_plan, dict):
    phases = implementation_plan.get("phases")
    if isinstance(phases, list):
      entries = phases

  slices = []
  for entry in entries:
    if not isinstance(entry, dict):
      continue
    phase_id = entry.get("id") or entry.get("phase_id")
    if not phase_id:
      continue
    slices.append({
      "phase_id": phase_id,
      "title": entry.get("title"),
    })
  return slices


def _execution_slice_by_phase(plan):
  by_phase = {}
  for entry in plan.get("execution_slices", []):
    if not isinstance(entry, dict):
      continue
    phase_id = entry.get("phase_id")
    if phase_id:
      by_phase[phase_id] = entry
  return by_phase


def _linked_todo_by_phase(linked):
  by_phase = {}
  unscoped = []
  for entry in linked:
    phase_id = entry.get("source_plan_slice_phase_id")
    if phase_id:
      by_phase.setdefault(phase_id, []).append(entry)
    else:
      unscoped.append(entry)
  return by_phase, unscoped


def _derive_slice_status(execution_slice, linked_todos):
  if linked_todos:
    if isinstance(execution_slice, dict):
      status = execution_slice.get("status")
      if status in {"completed", "deferred", "not_required"}:
        return status
    return "todo_created"
  if isinstance(execution_slice, dict):
    status = execution_slice.get("status")
    if isinstance(status, str) and status:
      return status
  return "not_materialized"


def _materialization_for_plan(cwd, plan, linked):
  execution_by_phase = _execution_slice_by_phase(plan)
  linked_by_phase, unscoped_todos = _linked_todo_by_phase(linked)
  materialized = []
  for index, slice_entry in enumerate(_implementation_slices(plan)):
    phase_id = slice_entry["phase_id"]
    execution_slice = execution_by_phase.get(phase_id, {})
    linked_todos = linked_by_phase.get(phase_id, [])
    if not linked_todos and index == 0 and unscoped_todos:
      linked_todos = unscoped_todos
    primary_todo = linked_todos[0] if linked_todos else {}
    status = _derive_slice_status(execution_slice, linked_todos)
    checklist_id = execution_slice.get("checklist_id")
    if not checklist_id and primary_todo:
      checklist, _path, _reasons = _find_checklist(cwd, primary_todo.get("id"))
      if isinstance(checklist, dict):
        checklist_id = checklist.get("checklist_id")
        if status == "todo_created":
          status = "checklist_started"
    materialized.append({
      "phase_id": phase_id,
      "title": slice_entry.get("title") or execution_slice.get("title"),
      "status": status,
      "todo_id": execution_slice.get("todo_id") or primary_todo.get("id"),
      "todo_path": execution_slice.get("todo_path") or primary_todo.get("path"),
      "checklist_id": checklist_id,
      "checklist_evidence_path": execution_slice.get("checklist_evidence_path"),
    })
  return materialized


def _materialization_summary(slices):
  by_status = {}
  for entry in slices:
    status = entry.get("status") or "unknown"
    by_status[status] = by_status.get(status, 0) + 1
  terminal = {"completed", "deferred", "not_required"}
  return {
    "total": len(slices),
    "by_status": by_status,
    "terminal_count": sum(
      1 for entry in slices if entry.get("status") in terminal
    ),
    "not_materialized_count": by_status.get("not_materialized", 0),
  }


def _next_materialization_candidates(slices):
  candidates = []
  for entry in slices:
    if entry.get("status") != "not_materialized":
      continue
    candidates.append({
      "phase_id": entry.get("phase_id"),
      "title": entry.get("title"),
      "recommended_next_action": "add-todo",
    })
  return candidates


def _quote_command_text(value):
  if value is None:
    return "\"\""
  return "\"" + str(value).replace("\"", "\\\"") + "\""


def _recommended_materialization_commands(plan, plan_id, plan_path, slices):
  source_unit_id = plan.get("source_unit_id") or "<source-unit-id>"
  add_todo = []
  for candidate in _next_materialization_candidates(slices):
    title = candidate.get("title") or candidate.get("phase_id") or "<title>"
    phase_id = candidate.get("phase_id") or "<phase-id>"
    add_todo.append(
      "work-backlog add-todo --id <todo-id> "
      f"--title {_quote_command_text(title)} "
      f"--source-unit-id {source_unit_id} "
      f"--source-ref {plan_path}#{phase_id} "
      "--reason <reason> "
      "--body-file <yaml-with-source_plan_id-source_plan_slice>"
    )
  start_checklist = [
    (
      "work-backlog start-checklist "
      f"--id {entry['todo_id']} --mutation-boundary-confirmed"
    )
    for entry in slices
    if entry.get("todo_id")
  ]
  return {
    "add_todo": add_todo,
    "start_checklist": start_checklist,
    "body_file_requirements": [
      f"source_plan_id: {plan_id}",
      f"source_plan_path: {plan_path}",
      "source_plan_slice.phase_id must match the selected implementation_plan slice",
    ],
  }


def _missing_execution_slice_phase_ids(plan):
  execution_by_phase = _execution_slice_by_phase(plan)
  return [
    entry["phase_id"]
    for entry in _implementation_slices(plan)
    if entry["phase_id"] not in execution_by_phase
  ]


def _relative_file_exists(cwd, path):
  if not isinstance(path, str) or not path:
    return True
  return (Path(cwd) / path).is_file()


def _completed_evidence_reference_reasons(cwd, label, evidence_path):
  if not isinstance(evidence_path, str) or not evidence_path:
    return []
  path = Path(cwd) / evidence_path
  if not path.is_file():
    return [f"{label} missing: {evidence_path}"]
  checklist, reasons = work_checklist._read_checklist_file(path)
  if reasons:
    return [f"{label} invalid: {evidence_path}: " + "; ".join(reasons)]
  missing = [
    key
    for key in ("completed_at", "completion_summary")
    if not checklist.get(key)
  ]
  if checklist.get("status") != "completed" or missing:
    return [f"{label} is not completed evidence: {evidence_path}"]
  return []


def _stale_execution_slice_link_reasons(cwd, plan_id, plan):
  reasons = []
  for entry in plan.get("execution_slices", []):
    if not isinstance(entry, dict):
      continue
    phase_id = entry.get("phase_id") or "<unknown-phase>"
    todo_path = entry.get("todo_path")
    if not _relative_file_exists(cwd, todo_path):
      reasons.append(
        f"{plan_id} execution_slices {phase_id} todo_path missing: {todo_path}"
      )
    checklist_evidence_path = entry.get("checklist_evidence_path")
    if not _relative_file_exists(cwd, checklist_evidence_path):
      reasons.append(
        f"{plan_id} execution_slices {phase_id} checklist_evidence_path missing: {checklist_evidence_path}"
      )
    else:
      label = f"{plan_id} execution_slices {phase_id} checklist_evidence_path"
      reasons.extend(
        _completed_evidence_reference_reasons(cwd, label, checklist_evidence_path)
      )
  return reasons


def _audit_materialization_record(cwd, entry, plan, index):
  plan_id = entry["id"]
  plan_path = entry.get("path") or _relative_item_path("plan", plan_id)
  linked, linked_reasons = _linked_todo_entries(cwd, index, plan_id, plan_path)
  linked_reasons.extend(_stale_execution_slice_link_reasons(cwd, plan_id, plan))
  materialization_slices = _materialization_for_plan(cwd, plan, linked)
  missing = _missing_execution_slice_phase_ids(plan)
  return {
    "plan_id": plan_id,
    "path": plan_path,
    "status": entry.get("status"),
    "linked_todo_ids": [item["id"] for item in linked],
    "materialization": {
      "slices": materialization_slices,
      "summary": _materialization_summary(materialization_slices),
      "next_candidates": _next_materialization_candidates(materialization_slices),
    },
    "missing_execution_slice_phase_ids": missing,
    "linked_reasons": linked_reasons,
  }


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
    if entry.get("kind") != "todo":
      continue
    item, item_reasons = _read_item_by_entry(cwd, entry)
    if item_reasons:
      reasons.extend(item_reasons)
      continue
    for history in item.get("execution_history", []) or []:
      if not isinstance(history, dict):
        continue
      label = (
        f"{entry['id']} execution_history "
        f"{history.get('checklist_id') or '<unknown-checklist>'} evidence_path"
      )
      reasons.extend(
        _completed_evidence_reference_reasons(
          cwd,
          label,
          history.get("evidence_path"),
        )
      )
    if entry.get("status") not in {"promoted", "active"}:
      continue
    if item.get("execution_history"):
      continue
    if not _has_runtime_or_evidence_checklist(cwd, entry["id"]):
      reasons.append(
        f"{entry['id']} has no active checklist or checklist evidence"
      )

  return _result("DEVIATION" if reasons else "OK", reasons, index=index)


def plan_todo_bridge(cwd, plan_id):
  shown = show(cwd, plan_id)
  if shown["verdict"] != "OK":
    return shown
  plan = shown["item"]
  if plan.get("kind") != "plan":
    return _result("DEVIATION", [f"backlog item は plan である必要があります: {plan_id}"])

  plan_path = shown["path"]
  linked, reasons = _linked_todo_entries(cwd, shown["index"], plan_id, plan_path)
  reasons.extend(_stale_execution_slice_link_reasons(cwd, plan_id, plan))
  linked_ids = [entry["id"] for entry in linked]
  response = _result(
    "DEVIATION" if reasons or not linked else "OK",
    reasons,
    index=shown["index"],
    item=plan,
    path=plan_path,
  )
  response["plan"] = {
    "id": plan_id,
    "path": plan_path,
    "title": plan.get("title"),
  }
  response["linked_todos"] = linked
  response["linked_todo_ids"] = linked_ids
  materialization_slices = _materialization_for_plan(cwd, plan, linked)
  response["materialization"] = {
    "slices": materialization_slices,
    "summary": _materialization_summary(materialization_slices),
    "next_candidates": _next_materialization_candidates(materialization_slices),
  }
  response["recommended_commands"] = _recommended_materialization_commands(
    plan,
    plan_id,
    plan_path,
    materialization_slices,
  )
  if not linked:
    response["reasons"].append("linked backlog TODO not found")
    response["next_steps"] = [
      (
        "work-backlog add-todo --id <todo-id> --title <title> "
        f"--source-unit-id {plan.get('source_unit_id')} "
        f"--source-ref {plan_path} --reason <reason> "
        "--body-file <yaml-with-source_plan_id-source_plan_path>"
      ),
      (
        "body file must include source_plan_id: "
        f"{plan_id} and source_plan_path: {plan_path}"
      ),
    ]
    return response

  first_todo_id = linked_ids[0]
  response["next_steps"] = [
    (
      "work-backlog start-checklist "
      f"--id {first_todo_id} --mutation-boundary-confirmed"
    ),
    f"work-backlog audit-checklist-coverage --id {first_todo_id} --checklist-id <checklist-id>",
    f"task-quality-check audit --backlog-id {first_todo_id} --checklist-id <checklist-id>",
  ]
  if len(linked) > 1:
    response["warnings"] = [
      "multiple linked TODOs found; choose one TODO before starting checklist"
    ]
  return response


def _quarantine_invalid_execution_history(cwd, item_id, item, target_paths):
  histories = item.get("execution_history")
  if not isinstance(histories, list):
    return False, []
  kept = []
  quarantined = []
  for history in histories:
    if not isinstance(history, dict):
      kept.append(history)
      continue
    evidence_path = history.get("evidence_path")
    label = (
      f"{item_id} execution_history "
      f"{history.get('checklist_id') or '<unknown-checklist>'} evidence_path"
    )
    invalid = bool(_completed_evidence_reference_reasons(cwd, label, evidence_path))
    if evidence_path in target_paths or invalid:
      quarantined_record = dict(history)
      quarantined_record["quarantined_at"] = _now_iso()
      quarantined_record["quarantine_reason"] = (
        "evidence_path does not point to completed checklist evidence"
      )
      quarantined.append(quarantined_record)
    else:
      kept.append(history)
  if not quarantined:
    return False, []
  item["execution_history"] = kept
  item.setdefault("quarantined_execution_history", []).extend(quarantined)
  return True, quarantined


def repair_active_checklist_evidence(cwd, checklist_id=None):
  checklist_result = work_checklist.repair_misplaced_evidence(
    cwd,
    checklist_id=checklist_id,
  )
  if checklist_result.get("verdict") != "OK":
    return checklist_result
  repaired_paths = {
    entry.get("evidence_path")
    for entry in checklist_result.get("repaired", [])
    if entry.get("evidence_path")
  }
  repaired_ids = {
    entry.get("checklist_id")
    for entry in checklist_result.get("repaired", [])
    if entry.get("checklist_id")
  }
  index, reasons = _read_index(cwd)
  if reasons:
    return _result("DEVIATION", reasons, index=index)

  plan_updates = []
  todo_updates = []
  for entry in index.get("items", []):
    if not isinstance(entry, dict):
      continue
    item, item_reasons = _read_item_by_entry(cwd, entry)
    if item_reasons:
      reasons.extend(item_reasons)
      continue
    changed = False
    if entry.get("kind") == "plan":
      for slice_entry in item.get("execution_slices", []) or []:
        if not isinstance(slice_entry, dict):
          continue
        evidence_path = slice_entry.get("checklist_evidence_path")
        linked_checklist_id = slice_entry.get("checklist_id")
        if evidence_path not in repaired_paths and linked_checklist_id not in repaired_ids:
          continue
        slice_entry["checklist_evidence_path"] = None
        if slice_entry.get("status") in {"evidence_recorded", "completed"}:
          slice_entry["status"] = "checklist_started"
        changed = True
        plan_updates.append({
          "plan_id": entry.get("id"),
          "phase_id": slice_entry.get("phase_id"),
          "checklist_id": linked_checklist_id,
        })
    elif entry.get("kind") == "todo":
      history_changed, quarantined = _quarantine_invalid_execution_history(
        cwd,
        entry.get("id"),
        item,
        repaired_paths,
      )
      if history_changed:
        changed = True
        todo_updates.append({
          "todo_id": entry.get("id"),
          "quarantined_count": len(quarantined),
        })
    if changed:
      _write_yaml(Path(cwd) / entry["path"], item)

  if reasons:
    return _result("DEVIATION", reasons, index=index)
  response = _result("OK", [], index=index)
  response["checklist_repair"] = checklist_result
  response["plan_updates"] = plan_updates
  response["todo_updates"] = todo_updates
  return response


def audit_plan_todo_bridge(cwd):
  index, reasons = _read_index(cwd)
  if reasons:
    return _result("DEVIATION", reasons, index=index)

  audited_plans = []
  for entry in index.get("items", []):
    if not isinstance(entry, dict):
      continue
    if entry.get("kind") != "plan":
      continue
    item, item_reasons = _read_item_by_entry(cwd, entry)
    if item_reasons:
      reasons.extend(item_reasons)
      continue
    audit_record = _audit_materialization_record(cwd, entry, item, index)
    audited_plans.append(audit_record)
    reasons.extend(audit_record.get("linked_reasons", []))
    if entry.get("status") not in {"promoted", "active"}:
      continue
    if item.get("execution_history"):
      continue
    if (
      not audit_record["linked_todo_ids"]
      and not _has_runtime_or_evidence_checklist(cwd, entry["id"])
    ):
      reasons.append(
        f"{entry['id']} has no linked TODO/checklist evidence"
      )
    not_materialized = [
      slice_entry.get("phase_id")
      for slice_entry in audit_record["materialization"]["slices"]
      if slice_entry.get("status") == "not_materialized"
    ]
    if not_materialized:
      reasons.append(
        f"{entry['id']} has not_materialized slices: "
        + ", ".join(not_materialized)
      )
      continue

  response = _result("DEVIATION" if reasons else "OK", reasons, index=index)
  response["audited_plans"] = audited_plans
  return response


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
