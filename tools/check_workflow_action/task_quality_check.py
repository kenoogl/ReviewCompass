"""Task/checklist derivation quality checks."""

from pathlib import Path

import yaml

from check_workflow_action import work_backlog


CHECKLIST_RUNTIME_DIR = ".reviewcompass/runtime/work-units/checklists"
CHECKLIST_EVIDENCE_DIR = ".reviewcompass/evidence/work-units/checklists"


def _result(
  verdict,
  reasons,
  quality=None,
  item=None,
  checklist=None,
  path=None,
  warnings=None,
):
  response = {
    "verdict": verdict,
    "reasons": reasons,
  }
  if warnings is not None:
    response["warnings"] = warnings
  if quality is not None:
    response["quality"] = quality
  if item is not None:
    response["item"] = item
  if checklist is not None:
    response["checklist"] = checklist
  if path is not None:
    response["path"] = str(path)
  return response


def _read_yaml(path, label):
  try:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
  except (OSError, UnicodeDecodeError, yaml.YAMLError) as exc:
    return None, [f"{label} を読めません: {path}: {exc}"]
  if not isinstance(data, dict):
    return None, [f"{label} は mapping である必要があります"]
  return data, []


def _find_checklist(cwd, checklist_id):
  if not checklist_id:
    return None, None, ["checklist_id が必要です"]
  for directory in (CHECKLIST_RUNTIME_DIR, CHECKLIST_EVIDENCE_DIR):
    path = Path(cwd) / directory / f"{checklist_id}.yaml"
    if not path.exists():
      continue
    checklist, reasons = _read_yaml(path, "checklist")
    if reasons:
      return None, None, reasons
    return checklist, path, []
  return None, None, [f"checklist not found: {checklist_id}"]


def _duplicate_ids(items):
  seen = set()
  duplicates = []
  for item in items:
    if not isinstance(item, dict):
      continue
    item_id = item.get("id")
    if not item_id:
      continue
    if item_id in seen and item_id not in duplicates:
      duplicates.append(item_id)
    seen.add(item_id)
  return duplicates


def _empty_title_ids(items):
  empty = []
  for index, item in enumerate(items, start=1):
    if not isinstance(item, dict):
      empty.append(f"<non-mapping-{index}>")
      continue
    title = item.get("title")
    if not isinstance(title, str) or not title.strip():
      empty.append(item.get("id") or f"<missing-id-{index}>")
  return empty


def _red_test_ids(backlog_item):
  ids = []
  for red_test in backlog_item.get("red_tests", []):
    if isinstance(red_test, dict) and red_test.get("id"):
      ids.append(red_test["id"])
  return ids


def _ordering_warning_ids(items, red_test_ids):
  first_red_test_index = None
  first_implementation_index = None
  for index, item in enumerate(items):
    if not isinstance(item, dict):
      continue
    item_id = item.get("id")
    if item_id in red_test_ids:
      if first_red_test_index is None:
        first_red_test_index = index
    elif item_id:
      if first_implementation_index is None:
        first_implementation_index = index
  if first_red_test_index is None or first_implementation_index is None:
    return []
  if first_red_test_index > first_implementation_index:
    return [
      item.get("id")
      for item in items
      if isinstance(item, dict) and item.get("id") in red_test_ids
    ]
  return []


def audit(cwd, backlog_id, checklist_id):
  shown = work_backlog.show(cwd, backlog_id)
  if shown["verdict"] != "OK":
    return shown
  item = shown["item"]
  if item.get("kind") != "todo":
    return _result(
      "DEVIATION",
      [f"backlog item は todo である必要があります: {backlog_id}"],
      item=item,
    )

  checklist, path, checklist_reasons = _find_checklist(cwd, checklist_id)
  if checklist_reasons:
    return _result("DEVIATION", checklist_reasons, item=item)

  expected = work_backlog._checklist_items_from_backlog_item(item)
  expected_ids = [entry["id"] for entry in expected]
  items = checklist.get("items", [])
  if not isinstance(items, list):
    return _result("DEVIATION", ["checklist items は list である必要があります"], item=item)

  actual_ids = [
    entry.get("id")
    for entry in items
    if isinstance(entry, dict) and entry.get("id")
  ]
  missing = [item_id for item_id in expected_ids if item_id not in actual_ids]
  extra = [item_id for item_id in actual_ids if item_id not in expected_ids]
  duplicates = _duplicate_ids(items)
  empty_titles = _empty_title_ids(items)
  red_test_ids = _red_test_ids(item)
  missing_red_tests = [
    red_test_id for red_test_id in red_test_ids if red_test_id not in actual_ids
  ]
  ordering_warning_ids = _ordering_warning_ids(items, red_test_ids)
  reasons = []
  warnings = []

  source_id = checklist.get("source_backlog_item_id")
  source_path = checklist.get("source_backlog_path")
  if source_id != backlog_id:
    reasons.append(f"source backlog id mismatch: {source_id}")
  if source_path != shown.get("path"):
    reasons.append(f"source backlog path mismatch: {source_path}")
  if duplicates:
    reasons.append("duplicate item ids: " + ", ".join(duplicates))
  if empty_titles:
    reasons.append("empty item titles: " + ", ".join(empty_titles))
  if missing_red_tests:
    reasons.append("missing red test checklist items: " + ", ".join(missing_red_tests))
  if missing:
    reasons.append("missing backlog-derived checklist items: " + ", ".join(missing))
  if ordering_warning_ids:
    warnings.append(
      "red test items appear after implementation items: "
      + ", ".join(ordering_warning_ids)
    )

  quality = {
    "expected_count": len(expected_ids),
    "actual_count": len(actual_ids),
    "missing_item_ids": missing,
    "missing_red_test_item_ids": missing_red_tests,
    "extra_item_ids": extra,
    "duplicate_item_ids": duplicates,
    "empty_title_item_ids": empty_titles,
    "ordering_warning_item_ids": ordering_warning_ids,
    "source_backlog_item_id": source_id,
    "source_backlog_path": source_path,
  }
  return _result(
    "DEVIATION" if reasons else "OK",
    reasons,
    quality=quality,
    item=item,
    checklist=checklist,
    path=path.relative_to(Path(cwd)),
    warnings=warnings,
  )
