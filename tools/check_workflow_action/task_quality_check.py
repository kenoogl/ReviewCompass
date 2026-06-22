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


def _write_yaml(path, data):
  path.parent.mkdir(parents=True, exist_ok=True)
  path.write_text(
    yaml.safe_dump(data, allow_unicode=True, sort_keys=False),
    encoding="utf-8",
  )


def _read_text(path, label):
  try:
    return path.read_text(encoding="utf-8"), []
  except (OSError, UnicodeDecodeError) as exc:
    return "", [f"{label} を読めません: {path}: {exc}"]


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


def _review_questions():
  return [
    {
      "id": "granularity",
      "question": "Are checklist items concrete, non-overlapping, and sized for execution?",
      "expected_output": "Find missing granularity risks with item IDs and evidence.",
    },
    {
      "id": "ordering",
      "question": "Is the checklist order suitable for TDD and review-before-implementation flow?",
      "expected_output": "Find ordering risks without treating warnings as automatic failure.",
    },
    {
      "id": "upstream_connection",
      "question": "Does the checklist preserve the source TODO intent and stated scope?",
      "expected_output": "Find weakened, omitted, or broadened upstream intent.",
    },
    {
      "id": "red_test_sufficiency",
      "question": "Do red test items cover the task quality risks before implementation work?",
      "expected_output": "Find missing or under-specified red test coverage.",
    },
  ]


def _main_preanalysis(backlog_id, checklist_id, audit_result):
  quality = audit_result.get("quality", {})
  observations = [
    (
      f"Checklist covers {quality.get('actual_count')} actual items for "
      f"{quality.get('expected_count')} backlog-derived items."
    ),
  ]
  if quality.get("missing_item_ids"):
    observations.append(
      "Missing backlog-derived items: " + ", ".join(quality["missing_item_ids"])
    )
  if quality.get("ordering_warning_item_ids"):
    observations.append(
      "Ordering warnings: " + ", ".join(quality["ordering_warning_item_ids"])
    )
  return {
    "role": "main_llm_preanalysis",
    "status": "mechanically_seeded",
    "data_sources": [
      f"backlog:{backlog_id}",
      f"checklist:{checklist_id}",
      "task-quality-check audit result",
    ],
    "observations": observations,
    "reviewer_instruction": (
      "Treat this preanalysis as a hypothesis to inspect, not as an answer to copy."
    ),
  }


def _review_result_contract(output_dir):
  prompt_materials_path = Path(output_dir) / "review-materials.yaml"
  review_run_dir = ".reviewcompass/evidence/task-quality-review-runs/run"
  return {
    "roles": ["primary", "adversarial", "judgment"],
    "paths": {
      "prompt_materials": str(prompt_materials_path),
      "review_run_dir": review_run_dir,
      "prompts_dir": f"{review_run_dir}/prompts",
      "raw_results_dir": f"{review_run_dir}/raw-results",
      "normalized_results_dir": f"{review_run_dir}/normalized-results",
      "triage_decision_path": f"{review_run_dir}/triage-decision.yaml",
      "summary_path": f"{review_run_dir}/review-summary.yaml",
    },
  }


def _decision_boundary():
  return {
    "mechanical_gate": "audit_result.verdict must be OK",
    "blocking_finding_levels": ["critical", "major"],
    "review_output_does_not_authorize_changes": True,
    "accepted_when": [
      "audit_result.verdict == OK",
      "no unresolved critical/major findings",
      "judgment role does not request changes",
    ],
  }


def prepare_review_materials(cwd, backlog_id, checklist_id, output_dir):
  audit_result = audit(cwd, backlog_id, checklist_id)
  if audit_result.get("verdict") != "OK":
    return _result(
      "DEVIATION",
      ["audit must be OK before preparing review materials"]
      + audit_result.get("reasons", []),
      quality=audit_result.get("quality"),
      item=audit_result.get("item"),
      checklist=audit_result.get("checklist"),
      warnings=audit_result.get("warnings", []),
    )

  source_backlog_path = Path(cwd) / audit_result["checklist"]["source_backlog_path"]
  checklist_path = Path(cwd) / audit_result["path"]
  backlog_content, backlog_reasons = _read_text(source_backlog_path, "backlog item")
  checklist_content, checklist_reasons = _read_text(checklist_path, "checklist")
  reasons = backlog_reasons + checklist_reasons
  if reasons:
    return _result("DEVIATION", reasons)

  materials = {
    "schema_version": "task-quality-review-materials-v1",
    "review_target": {
      "backlog_id": backlog_id,
      "checklist_id": checklist_id,
    },
    "source_materials": [
      {
        "id": "backlog_todo",
        "path": str(source_backlog_path.relative_to(Path(cwd))),
        "content_mode": "full_text",
        "content": backlog_content,
      },
      {
        "id": "runtime_checklist",
        "path": str(checklist_path.relative_to(Path(cwd))),
        "content_mode": "full_text",
        "content": checklist_content,
      },
    ],
    "audit_result": audit_result,
    "main_preanalysis": _main_preanalysis(backlog_id, checklist_id, audit_result),
    "review_questions": _review_questions(),
    "review_result_contract": _review_result_contract(output_dir),
    "decision_boundary": _decision_boundary(),
    "sensitive_information_check": {
      "status": "not_required_for_local_materialization",
      "reason": "materials are generated locally before any API call",
    },
  }
  output_path = Path(output_dir) / "review-materials.yaml"
  _write_yaml(output_path, materials)
  response = _result(
    "OK",
    [],
    quality=audit_result.get("quality"),
    item=audit_result.get("item"),
    checklist=audit_result.get("checklist"),
    warnings=audit_result.get("warnings", []),
  )
  response["materials_path"] = str(output_path)
  response["materials"] = materials
  return response
