"""Work backlog helpers for pre-workflow candidate records."""

from datetime import datetime, timezone
from pathlib import Path

import yaml


DEFAULT_BACKLOG_INDEX_PATH = ".reviewcompass/backlog/index.yaml"
BACKLOG_ROOT = ".reviewcompass/backlog"
INDEX_SCHEMA_VERSION = "reviewcompass-backlog-index-v1"
ITEM_SCHEMA_VERSION = "reviewcompass-backlog-item-v1"
KIND_DIRECTORIES = {
  "plan": "plans",
  "issue": "issues",
  "todo": "todos",
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


def _add(cwd, kind, item_id, title, source_unit_id, source_ref, reason):
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


def add_plan(cwd, item_id, title, source_unit_id, source_ref, reason):
  return _add(cwd, "plan", item_id, title, source_unit_id, source_ref, reason)


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


def reject(cwd, item_id, decision_ref, reason):
  return _decide(cwd, item_id, "rejected", decision_ref, reason)
