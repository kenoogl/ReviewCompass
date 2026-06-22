"""Task/checklist derivation quality checks."""

from pathlib import Path

import yaml

from check_workflow_action import work_backlog


CHECKLIST_RUNTIME_DIR = ".reviewcompass/runtime/work-units/checklists"
CHECKLIST_EVIDENCE_DIR = ".reviewcompass/evidence/work-units/checklists"


def _result(verdict, reasons, quality=None, item=None, checklist=None, path=None):
  response = {
    "verdict": verdict,
    "reasons": reasons,
  }
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
  reasons = []

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
  if missing:
    reasons.append("missing backlog-derived checklist items: " + ", ".join(missing))

  quality = {
    "expected_count": len(expected_ids),
    "actual_count": len(actual_ids),
    "missing_item_ids": missing,
    "extra_item_ids": extra,
    "duplicate_item_ids": duplicates,
    "empty_title_item_ids": empty_titles,
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
  )
