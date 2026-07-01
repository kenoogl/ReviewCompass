"""workflow next_action 由来の API review criteria を生成する。"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
  sys.path.insert(0, str(_PROJECT_ROOT))

import yaml  # noqa: E402

from tools.api_providers.api_review_prompt_builder import (  # noqa: E402
  SourceMaterial,
  build_api_review_criteria_from_next_action,
)
from tools.normal_output import status_line  # noqa: E402


def _sha256_file(path: Path) -> str:
  return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_next_action(path: Path) -> Dict[str, Any]:
  data = json.loads(path.read_text(encoding="utf-8"))
  if isinstance(data, dict) and isinstance(data.get("next_action"), dict):
    return data["next_action"]
  if isinstance(data, dict):
    return data
  raise ValueError("next action file must contain an object")


def _list_value(data: Dict[str, Any], key: str) -> List[str]:
  value = data.get(key)
  if value is None:
    return []
  if not isinstance(value, list):
    raise ValueError(f"source material {key} must be a list")
  return [str(item) for item in value]


def _source_material_from_dict(data: Dict[str, Any]) -> SourceMaterial:
  return SourceMaterial(
    key=str(data.get("key") or ""),
    purpose=str(data.get("purpose") or ""),
    source_paths=_list_value(data, "source_paths"),
    source_anchors=_list_value(data, "source_anchors"),
    content=data.get("content"),
    purpose_field=data.get("purpose_field"),
    responsibility_boundaries=_list_value(data, "responsibility_boundaries"),
    acceptance_criteria=_list_value(data, "acceptance_criteria"),
    forbidden_actions=_list_value(data, "forbidden_actions"),
    unresolved_or_deferred=(
      _list_value(data, "unresolved_or_deferred")
      or _list_value(data, "unresolved_or_design_deferred_items")
    ),
    intended_target_phase_transfer=_list_value(
      data,
      "intended_target_phase_transfer",
    ),
  )


def _load_source_materials(path: Path) -> List[SourceMaterial]:
  data = yaml.safe_load(path.read_text(encoding="utf-8"))
  if isinstance(data, dict):
    entries = data.get("source_materials")
  else:
    entries = data
  if not isinstance(entries, list) or not entries:
    raise ValueError("source_materials must be a non-empty list")
  materials = []
  for entry in entries:
    if not isinstance(entry, dict):
      raise ValueError("each source material must be an object")
    materials.append(_source_material_from_dict(entry))
  return materials


def _load_required_prompt_changes(path: Optional[str]) -> List[str]:
  if not path:
    return []
  data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
  if not isinstance(data, dict):
    raise ValueError("preanalysis audit record must be an object")
  changes = data.get("required_prompt_changes")
  if changes is None:
    changes = data.get("required_changes")
  if changes is None:
    return []
  if not isinstance(changes, list):
    raise ValueError("preanalysis audit required_prompt_changes must be a list")
  return [str(item) for item in changes]


def _parse_argv(argv: Optional[List[str]]) -> argparse.Namespace:
  parser = argparse.ArgumentParser(
    description="workflow next_action から API review criteria を生成する。",
  )
  parser.add_argument("--next-action-file", required=True, help="next --json の出力")
  parser.add_argument("--review-run-dir", required=True, help="criteria 出力先")
  parser.add_argument(
    "--source-materials-file",
    required=True,
    help="構造化 source materials YAML",
  )
  parser.add_argument(
    "--preanalysis-audit-record",
    help="preanalysis sufficiency audit の parsed YAML。required_prompt_changes を criteria に反映する。",
  )
  parser.add_argument("--topic", required=True, help="criteria topic")
  parser.add_argument("--target", required=True, action="append", help="review target")
  parser.add_argument("--judgment-item", required=True, help="単一の判断項目")
  parser.add_argument("--review-purpose", required=True, help="レビュー目的")
  parser.add_argument("--review-object", required=True, help="レビュー対象種別")
  parser.add_argument("--review-focus", action="append", default=[], help="重点観点")
  parser.add_argument("--in-scope", action="append", default=[], help="scope 内")
  parser.add_argument("--out-of-scope", action="append", default=[], help="scope 外")
  return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
  args = _parse_argv(argv)
  try:
    next_action = _load_next_action(Path(args.next_action_file))
    source_materials = _load_source_materials(Path(args.source_materials_file))
    required_prompt_changes = _load_required_prompt_changes(
      args.preanalysis_audit_record
    )
    criteria = build_api_review_criteria_from_next_action(
      next_action=next_action,
      topic=args.topic,
      review_target_paths=args.target,
      judgment_item=args.judgment_item,
      review_purpose=args.review_purpose,
      review_object=args.review_object,
      review_focus=args.review_focus,
      scope_boundaries={
        "in_scope": args.in_scope,
        "out_of_scope": args.out_of_scope,
      },
      source_materials=source_materials,
      preanalysis_audit_changes=required_prompt_changes,
    )
  except Exception as exc:
    sys.stderr.write(f"エラー：prepare_api_review_criteria failed: {exc}\n")
    return 1

  run_dir = Path(args.review_run_dir)
  run_dir.mkdir(parents=True, exist_ok=True)
  generated_at = datetime.now(timezone.utc).isoformat()
  criteria_path = run_dir / "review-criteria.md"
  criteria_path.write_text(criteria, encoding="utf-8")
  effective_prompt = next_action.get("effective_prompt")
  if not isinstance(effective_prompt, dict):
    effective_prompt = {}
  metadata: Dict[str, Any] = {
    "run_id": run_dir.name,
    "feature": next_action.get("feature"),
    "workflow_phase": next_action.get("phase"),
    "review_stage": next_action.get("stage"),
    "criteria_file": str(criteria_path),
    "criteria_file_sha256": _sha256_file(criteria_path),
    "source_materials_file": str(Path(args.source_materials_file)),
    "generated_at": generated_at,
    "required_prompt_changes_count": len(required_prompt_changes),
    "recommended_run_review_args": {
      "criteria_file": str(criteria_path),
      "phase": next_action.get("stage") or next_action.get("phase"),
    },
  }
  if args.preanalysis_audit_record:
    metadata["preanalysis_audit_record"] = str(Path(args.preanalysis_audit_record))
  if effective_prompt.get("effective_prompt_path"):
    metadata["effective_prompt_path"] = effective_prompt["effective_prompt_path"]
    metadata["recommended_run_review_args"]["effective_prompt_path"] = (
      effective_prompt["effective_prompt_path"]
    )
  if effective_prompt.get("effective_prompt_sha256"):
    metadata["effective_prompt_sha256"] = effective_prompt["effective_prompt_sha256"]
    metadata["recommended_run_review_args"]["effective_prompt_sha256"] = (
      effective_prompt["effective_prompt_sha256"]
    )
  metadata_path = run_dir / "review-criteria.yaml"
  metadata_path.write_text(
    yaml.safe_dump(metadata, allow_unicode=True, sort_keys=False),
    encoding="utf-8",
  )
  sys.stdout.write(status_line(
    "OK",
    "prepare_api_review_criteria",
    {
      "criteria": criteria_path,
      "metadata": metadata_path,
      "targets": len(args.target),
    },
  ))
  return 0


if __name__ == "__main__":
  sys.exit(main())
