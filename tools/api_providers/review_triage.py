"""tools/api_providers/review_triage.py

review-run の triage 下書きを一覧化し、人判断の反映と manifest 雛形生成を行う。
"""
import argparse
import hashlib
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
  sys.path.insert(0, str(_PROJECT_ROOT))

import yaml  # noqa: E402

FINAL_LABELS = ("must-fix", "should-fix", "leave-as-is")


def _load_yaml_dict(path: Path) -> Dict[str, Any]:
  data = yaml.safe_load(path.read_text(encoding="utf-8"))
  return data if isinstance(data, dict) else {}


def _dump_yaml(path: Path, data: Dict[str, Any]) -> None:
  path.write_text(
    yaml.safe_dump(data, allow_unicode=True, sort_keys=False),
    encoding="utf-8",
  )


def _sha256_file(path: Path) -> str:
  return hashlib.sha256(path.read_bytes()).hexdigest()


def _recommendation_for(item: Dict[str, Any]) -> Dict[str, str]:
  severity = str(item.get("severity_normalized") or item.get("severity_original") or "INFO").upper()
  if severity in ("CRITICAL", "ERROR"):
    return {
      "label": "must-fix",
      "reason": "仕様・契約・比較可能性に影響する可能性があるため、人判断の優先度が高い。",
    }
  if severity == "WARN":
    return {
      "label": "should-fix",
      "reason": "後続の読みやすさや保守性に影響する可能性があるため、可能なら反映する。",
    }
  return {
    "label": "leave-as-is",
    "reason": "情報提供または軽微な表現指摘として扱い、必要時だけ反映する。",
  }


def _triage_path(run_dir: Path) -> Path:
  return run_dir / "triage.yaml"


def _summary_path(run_dir: Path) -> Path:
  return run_dir / "model-result-summary.yaml"


def list_pending(review_run_dir: str) -> str:
  """human_required の triage item を Markdown 表で返す。"""
  run_dir = Path(review_run_dir)
  triage = _load_yaml_dict(_triage_path(run_dir))
  items = triage.get("items")
  if not isinstance(items, list):
    items = []

  lines = [
    f"# Pending triage: {run_dir.name}",
    "",
    "| finding_id | model | severity | summary | recommendation | reason |",
    "| --- | --- | --- | --- | --- | --- |",
  ]
  for item in items:
    if not isinstance(item, dict):
      continue
    if item.get("decision_status") != "human_required":
      continue
    recommendation = _recommendation_for(item)
    lines.append(
      "| {finding_id} | {model} | {severity} | {summary} | {label} | {reason} |".format(
        finding_id=item.get("finding_id"),
        model=item.get("source_model"),
        severity=item.get("severity_normalized") or item.get("severity_original"),
        summary=item.get("plain_language_summary"),
        label=recommendation["label"],
        reason=recommendation["reason"],
      )
    )
  return "\n".join(lines) + "\n"


def _count_summary_for_model(items: List[Dict[str, Any]], model_id: str) -> Dict[str, int]:
  counts = {
    "must_fix_count": 0,
    "should_fix_count": 0,
    "leave_as_is_count": 0,
    "human_required_count": 0,
  }
  for item in items:
    if item.get("source_model") != model_id:
      continue
    if item.get("decision_status") == "human_required":
      counts["human_required_count"] += 1
      continue
    label = item.get("final_label")
    if label == "must-fix":
      counts["must_fix_count"] += 1
    elif label == "should-fix":
      counts["should_fix_count"] += 1
    elif label == "leave-as-is":
      counts["leave_as_is_count"] += 1
  return counts


def refresh_summary_from_triage(review_run_dir: str) -> None:
  """triage の決定状態を model-result-summary.yaml に反映する。"""
  run_dir = Path(review_run_dir)
  triage = _load_yaml_dict(_triage_path(run_dir))
  summary = _load_yaml_dict(_summary_path(run_dir))
  items = triage.get("items")
  models = summary.get("models")
  if not isinstance(items, list):
    items = []
  if not isinstance(models, list):
    models = []

  models_with_items = {
    item.get("source_model")
    for item in items
    if isinstance(item, dict) and item.get("source_model")
  }
  for model in models:
    if not isinstance(model, dict):
      continue
    model_id = model.get("model_id")
    if not model_id or model_id not in models_with_items:
      continue
    counts = _count_summary_for_model(items, model_id)
    model.update(counts)
    if counts["human_required_count"] > 0:
      model["triage_status"] = "triage_pending"
    else:
      model["triage_status"] = "triaged"
  _dump_yaml(_summary_path(run_dir), summary)


def decide_item(
  review_run_dir: str,
  finding_id: str,
  final_label: str,
  decision_reason: str,
  decision_actor: str,
) -> bool:
  """1 finding の人判断を反映する。見つかった場合 True。"""
  run_dir = Path(review_run_dir)
  triage = _load_yaml_dict(_triage_path(run_dir))
  items = triage.get("items")
  if not isinstance(items, list):
    items = []

  found = False
  now = datetime.now(timezone.utc).isoformat()
  for item in items:
    if not isinstance(item, dict):
      continue
    if item.get("finding_id") != finding_id:
      continue
    item["final_label"] = final_label
    item["decision_status"] = "decided"
    item["decision_actor"] = decision_actor
    item["decision_actor_type"] = "human"
    item["decision_at"] = now
    item["decision_reason"] = decision_reason
    found = True
    break

  if not found:
    return False

  unresolved = [
    item for item in items
    if isinstance(item, dict) and item.get("decision_status") == "human_required"
  ]
  triage["triage_status"] = "draft" if unresolved else "decided"
  _dump_yaml(_triage_path(run_dir), triage)
  refresh_summary_from_triage(review_run_dir)
  return True


def _path_string(path: Path) -> str:
  try:
    return str(path.relative_to(Path.cwd()))
  except ValueError:
    return str(path)


def build_manifest_template(review_run_dir: str) -> Dict[str, Any]:
  """post-write-verification manifest 雛形を返す。"""
  run_dir = Path(review_run_dir)
  target_manifest = _load_yaml_dict(run_dir / "target-manifest.yaml")
  rounds = _load_yaml_dict(run_dir / "rounds.yaml")
  triage = _load_yaml_dict(run_dir / "triage.yaml")
  summary_path = run_dir / "model-result-summary.yaml"
  target_files = [
    item.get("path")
    for item in target_manifest.get("target_files", [])
    if isinstance(item, dict) and item.get("path")
  ]
  target_sha256 = {
    item.get("path"): item.get("sha256")
    for item in target_manifest.get("target_files", [])
    if isinstance(item, dict) and item.get("path") and item.get("sha256")
  }
  models = [
    item.get("model_id")
    for item in rounds.get("model_results", [])
    if isinstance(item, dict) and item.get("model_id")
  ]
  unresolved = 0
  for item in triage.get("items", []):
    if isinstance(item, dict) and item.get("decision_status") == "human_required":
      unresolved += 1

  status = "completed" if unresolved == 0 else "pending"
  return {
    "status": status,
    "target_files": target_files,
    "target_sha256": target_sha256,
    "required_verifiers": models,
    "completed_verifiers": models,
    "unresolved_substantive_findings": unresolved,
    "review_run": {
      "path": _path_string(run_dir),
      "summary_path": _path_string(summary_path),
    },
    "notes": "Generated template; verify target_files cover current post-write targets before use.",
  }


def _parse_argv(argv: Optional[List[str]]) -> argparse.Namespace:
  parser = argparse.ArgumentParser(description="review-run triage helper")
  subparsers = parser.add_subparsers(dest="command", required=True)

  list_parser = subparsers.add_parser("list-pending")
  list_parser.add_argument("--review-run-dir", required=True)

  decide_parser = subparsers.add_parser("decide")
  decide_parser.add_argument("--review-run-dir", required=True)
  decide_parser.add_argument("--finding-id", required=True)
  decide_parser.add_argument("--final-label", required=True, choices=FINAL_LABELS)
  decide_parser.add_argument("--decision-reason", required=True)
  decide_parser.add_argument("--decision-actor", required=True)

  manifest_parser = subparsers.add_parser("manifest-template")
  manifest_parser.add_argument("--review-run-dir", required=True)

  return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
  args = _parse_argv(argv)
  try:
    if args.command == "list-pending":
      sys.stdout.write(list_pending(args.review_run_dir))
      return 0
    if args.command == "decide":
      found = decide_item(
        args.review_run_dir,
        args.finding_id,
        args.final_label,
        args.decision_reason,
        args.decision_actor,
      )
      if not found:
        sys.stderr.write(f"finding_id not found: {args.finding_id}\n")
        return 1
      return 0
    if args.command == "manifest-template":
      sys.stdout.write(
        yaml.safe_dump(
          build_manifest_template(args.review_run_dir),
          allow_unicode=True,
          sort_keys=False,
        )
      )
      return 0
  except Exception as exc:
    sys.stderr.write(f"エラー：{type(exc).__name__}: {exc}\n")
    return 1
  return 1


if __name__ == "__main__":
  sys.exit(main())
