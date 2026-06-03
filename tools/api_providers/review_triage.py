"""tools/api_providers/review_triage.py

review-run の triage 下書きを一覧化し、人判断の反映と manifest 雛形生成を行う。
"""
import argparse
import hashlib
import subprocess
import sys
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
  sys.path.insert(0, str(_PROJECT_ROOT))

import yaml  # noqa: E402

FINAL_LABELS = ("must-fix", "should-fix", "leave-as-is")
IMPORTANT_SEVERITIES = ("CRITICAL", "ERROR")
TRIAGE_DECIDE_APPROVAL_ACTIONS = ("review_triage_decide", "review_run_triage")
MANIFEST_APPROVAL_ACTIONS = ("review_run_manifest", "review_run_triage")
POST_WRITE_VERIFICATION_DIR_PREFIXES = (
  "docs/plan/",
  "docs/disciplines/",
  "docs/operations/",
  "docs/notes/",
  "docs/experiments/",
)
POST_WRITE_VERIFICATION_MD_DIR_PREFIXES = (
  ".reviewcompass/specs/",
  "intent/",
  "templates/",
)
POST_WRITE_VERIFICATION_FILE_PATHS = (
  "AGENTS.md",
  "TODO_NEXT_SESSION.md",
)
POST_WRITE_VERIFICATION_FILE_PREFIXES = (
  "runtime/prompts/",
  "tools/api_providers/prompt_templates/",
)


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


def _parse_git_status_path(line: str) -> Optional[str]:
  """git status --short の行から path を取り出す。"""
  if len(line) < 4:
    return None
  path = line[3:]
  if " -> " in path:
    path = path.split(" -> ", 1)[1]
  return path.strip()


def _is_post_write_target(path: str) -> bool:
  """post-write-verification 対象の md 文書パスかを返す。"""
  if path.startswith("docs/archive/"):
    return False
  if path in POST_WRITE_VERIFICATION_FILE_PATHS:
    return True
  if any(path.startswith(prefix) for prefix in POST_WRITE_VERIFICATION_DIR_PREFIXES):
    return True
  if not path.endswith(".md"):
    return False
  if any(path.startswith(prefix) for prefix in POST_WRITE_VERIFICATION_FILE_PREFIXES):
    return True
  if any(path.startswith(prefix) for prefix in POST_WRITE_VERIFICATION_MD_DIR_PREFIXES):
    return True
  if path.startswith("docs/reviews/"):
    name = Path(path).name
    return (
      name.startswith("reopen-classification-")
      or "-audit-" in name
    ) and name.endswith(".md")
  return False


def _current_git_post_write_targets(cwd: Path) -> List[str]:
  """現在の git 変更から post-write 対象を返す。git 外では空リスト。"""
  try:
    result = subprocess.run(
      ["git", "status", "--short", "--untracked-files=all"],
      cwd=str(cwd),
      capture_output=True,
      text=True,
      timeout=10,
      check=False,
    )
  except (OSError, subprocess.SubprocessError):
    return []
  if result.returncode != 0:
    return []
  targets = []
  for line in result.stdout.splitlines():
    path = _parse_git_status_path(line)
    if path and _is_post_write_target(path):
      targets.append(path)
  return sorted(set(targets))


def _find_git_root(start: Path) -> Path:
  """start から上位へ .git を探し、見つからなければ現在ディレクトリを返す。"""
  current = start.resolve()
  if current.is_file():
    current = current.parent
  for candidate in [current] + list(current.parents):
    if (candidate / ".git").exists():
      return candidate
  return Path.cwd()


def _resolve_path(path: str, base_dir: Optional[Path] = None) -> Path:
  candidate = Path(path)
  if candidate.is_absolute():
    return candidate
  return (base_dir or Path.cwd()) / candidate


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


def _severity_for(item: Dict[str, Any]) -> str:
  return str(item.get("severity_normalized") or item.get("severity_original") or "INFO").upper()


def _is_important_item(item: Dict[str, Any], final_label: Optional[str] = None) -> bool:
  """重要件として人承認を要求する finding かを返す。"""
  label = final_label if final_label is not None else item.get("final_label")
  return _severity_for(item) in IMPORTANT_SEVERITIES or label == "must-fix"


def _load_approval_record(path: Optional[str]) -> Dict[str, Any]:
  if not path:
    return {}
  approval = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
  return approval if isinstance(approval, dict) else {}


def _approval_errors(
  approval: Dict[str, Any],
  run_id: str,
  allowed_actions: tuple,
  required_finding_ids: List[str],
  final_labels: Optional[Dict[str, str]] = None,
) -> List[str]:
  errors = []
  if not approval:
    return ["approval record is required"]
  if approval.get("approved_action") not in allowed_actions:
    errors.append("approved_action does not allow this review-run action")
  if approval.get("approved_by") != "user":
    errors.append("approved_by must be user")
  if approval.get("review_run_id") != run_id:
    errors.append("review_run_id does not match")
  if approval.get("summary_presented_to_user") is not True:
    errors.append("summary_presented_to_user must be true")
  if approval.get("triage_presented_to_user") is not True:
    errors.append("triage_presented_to_user must be true")
  if approval.get("consumed") is True:
    errors.append("approval record is already consumed")

  approved_ids = approval.get("approved_finding_ids")
  approved_id_set = set(approved_ids) if isinstance(approved_ids, list) else set()
  missing_ids = sorted(set(required_finding_ids) - approved_id_set)
  if missing_ids:
    errors.append(f"approved_finding_ids missing: {', '.join(missing_ids)}")

  approved_labels = approval.get("approved_final_labels")
  if final_labels and isinstance(approved_labels, dict):
    mismatched = [
      finding_id
      for finding_id, label in final_labels.items()
      if approved_labels.get(finding_id) != label
    ]
    if mismatched:
      errors.append(f"approved_final_labels mismatch: {', '.join(sorted(mismatched))}")
  return errors


def _require_review_run_approval(
  run_dir: Path,
  approval_record_path: Optional[str],
  allowed_actions: tuple,
  required_finding_ids: List[str],
  final_labels: Optional[Dict[str, str]] = None,
) -> None:
  if not required_finding_ids:
    return
  approval = _load_approval_record(approval_record_path)
  errors = _approval_errors(
    approval,
    run_dir.name,
    allowed_actions,
    required_finding_ids,
    final_labels,
  )
  if errors:
    raise ValueError("approval gate failed: " + "; ".join(errors))


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
  approval_record_path: Optional[str] = None,
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
    if _is_important_item(item, final_label):
      _require_review_run_approval(
        run_dir,
        approval_record_path,
        TRIAGE_DECIDE_APPROVAL_ACTIONS,
        [finding_id],
        {finding_id: final_label},
      )
    item["final_label"] = final_label
    item["decision_status"] = "decided"
    item["decision_actor"] = decision_actor
    item["decision_actor_type"] = "human" if decision_actor == "human" else "agent"
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


def unresolved_human_required_count(review_run_dir: str) -> int:
  """human_required が残る件数を返す。"""
  triage = _load_yaml_dict(_triage_path(Path(review_run_dir)))
  count = 0
  for item in triage.get("items", []):
    if isinstance(item, dict) and item.get("decision_status") == "human_required":
      count += 1
  return count


def _current_target_sha256(
  target_files: List[str],
  fallback: Dict[str, str],
  base_dir: Path,
) -> Dict[str, str]:
  """対象ファイルの現在 sha256 を返す。存在しない場合は fallback を使う。"""
  values: Dict[str, str] = {}
  for target in target_files:
    target_path = _resolve_path(target, base_dir)
    if target_path.is_file():
      values[target] = _sha256_file(target_path)
    elif target in fallback:
      values[target] = fallback[target]
  return values


def _verification_entries(models: List[str], target_files: List[str], target_sha256: Dict[str, str]) -> List[Dict[str, Any]]:
  """required verifier ごとの coverage matrix を作る。"""
  return [
    {
      "verifier": model,
      "target_files": list(target_files),
      "target_sha256": dict(target_sha256),
    }
    for model in models
  ]


def build_manifest_template(review_run_dir: str) -> Dict[str, Any]:
  """post-write-verification manifest 雛形を返す。"""
  run_dir = Path(review_run_dir)
  git_root = _find_git_root(run_dir)
  target_manifest = _load_yaml_dict(run_dir / "target-manifest.yaml")
  rounds = _load_yaml_dict(run_dir / "rounds.yaml")
  triage = _load_yaml_dict(run_dir / "triage.yaml")
  summary_path = run_dir / "model-result-summary.yaml"
  target_files = [
    item.get("path")
    for item in target_manifest.get("target_files", [])
    if isinstance(item, dict) and item.get("path")
  ]
  current_targets = _current_git_post_write_targets(git_root)
  if current_targets:
    target_files = sorted(set(target_files).union(current_targets))
  fallback_sha256 = {
    item.get("path"): item.get("sha256")
    for item in target_manifest.get("target_files", [])
    if isinstance(item, dict) and item.get("path") and item.get("sha256")
  }
  target_sha256 = _current_target_sha256(target_files, fallback_sha256, git_root)
  models = [
    item.get("model_id")
    for item in rounds.get("model_results", [])
    if isinstance(item, dict) and item.get("model_id")
  ]
  unresolved = unresolved_human_required_count(review_run_dir)

  status = "completed" if unresolved == 0 else "pending"
  return {
    "status": status,
    "target_files": target_files,
    "target_sha256": target_sha256,
    "required_verifiers": models,
    "completed_verifiers": models,
    "unresolved_substantive_findings": unresolved,
    "verifications": _verification_entries(models, target_files, target_sha256),
    "review_run": {
      "path": _path_string(run_dir),
      "summary_path": _path_string(summary_path),
    },
    "notes": "Generated template; verify target_files cover current post-write targets before use.",
  }


def assert_manifest_ready(
  review_run_dir: str,
  approval_record_path: Optional[str] = None,
) -> None:
  """manifest 生成可能か確認し、未判断があれば例外にする。"""
  run_dir = Path(review_run_dir)
  unresolved = unresolved_human_required_count(review_run_dir)
  if unresolved > 0:
    raise ValueError(f"human_required remains: {unresolved}")
  triage = _load_yaml_dict(_triage_path(run_dir))
  items = triage.get("items")
  if not isinstance(items, list):
    items = []
  important_ids = [
    item.get("finding_id")
    for item in items
    if isinstance(item, dict)
    and item.get("finding_id")
    and item.get("decision_status") == "decided"
    and _is_important_item(item)
  ]
  _require_review_run_approval(
    run_dir,
    approval_record_path,
    MANIFEST_APPROVAL_ACTIONS,
    sorted(set(important_ids)),
  )


def write_manifest(
  review_run_dir: str,
  out_path: str,
  approval_record_path: Optional[str] = None,
) -> Path:
  """完了 manifest をファイルへ書き、出力先 path を返す。"""
  assert_manifest_ready(review_run_dir, approval_record_path)
  manifest = build_manifest_template(review_run_dir)
  output = resolve_manifest_output_path(out_path)
  output.parent.mkdir(parents=True, exist_ok=True)
  _dump_yaml(output, manifest)
  return output


def resolve_manifest_output_path(out_path: str) -> Path:
  """manifest 出力先を解決する。auto は当日の次番号を返す。"""
  if out_path != "auto":
    return Path(out_path)
  manifest_dir = Path.cwd() / ".reviewcompass" / "post-write-verification"
  manifest_dir.mkdir(parents=True, exist_ok=True)
  prefix = f"post-write-{date.today().isoformat()}-"
  max_number = 0
  for path in manifest_dir.glob(f"{prefix}*.yaml"):
    suffix = path.stem.removeprefix(prefix)
    try:
      max_number = max(max_number, int(suffix))
    except ValueError:
      continue
  return manifest_dir / f"{prefix}{max_number + 1:03d}.yaml"


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
  decide_parser.add_argument("--approval-record")

  manifest_parser = subparsers.add_parser("manifest-template")
  manifest_parser.add_argument("--review-run-dir", required=True)
  manifest_parser.add_argument("--approval-record")

  write_manifest_parser = subparsers.add_parser("write-manifest")
  write_manifest_parser.add_argument("--review-run-dir", required=True)
  write_manifest_parser.add_argument("--out", required=True)
  write_manifest_parser.add_argument("--approval-record")

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
        args.approval_record,
      )
      if not found:
        sys.stderr.write(f"finding_id not found: {args.finding_id}\n")
        return 1
      return 0
    if args.command == "manifest-template":
      assert_manifest_ready(args.review_run_dir, args.approval_record)
      sys.stdout.write(
        yaml.safe_dump(
          build_manifest_template(args.review_run_dir),
          allow_unicode=True,
          sort_keys=False,
        )
      )
      return 0
    if args.command == "write-manifest":
      output = write_manifest(args.review_run_dir, args.out, args.approval_record)
      sys.stdout.write(f"{output}\n")
      return 0
  except Exception as exc:
    sys.stderr.write(f"エラー：{type(exc).__name__}: {exc}\n")
    return 1
  return 1


if __name__ == "__main__":
  sys.exit(main())
