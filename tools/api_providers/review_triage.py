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
APPLY_FIXES_APPROVAL_ACTIONS = ("review_run_apply_fixes", "review_run_triage")
FIX_LABELS = ("must-fix", "should-fix")
POST_WRITE_VERIFICATION_DIR_PREFIXES = (
  "docs/plan/",
  "docs/disciplines/",
  "docs/operations/",
  "docs/notes/",
  "docs/experiments/",
)
POST_WRITE_VERIFICATION_MD_DIR_PREFIXES = (
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
POST_WRITE_VERIFICATION_SPEC_FILENAMES = (
  "requirements.md",
  "design.md",
  "tasks.md",
  "implementation.md",
)
LIGHTWEIGHT_SELF_CHECK_DIR_PREFIXES = (
  "docs/notes/",
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
  if path.startswith("docs/notes/review-runs/"):
    return False
  if path.startswith(".reviewcompass/evidence/review-runs/"):
    return False
  if any(path.startswith(prefix) for prefix in LIGHTWEIGHT_SELF_CHECK_DIR_PREFIXES):
    return False
  if path.startswith("docs/sessions/auto-"):
    return False
  if path in POST_WRITE_VERIFICATION_FILE_PATHS:
    return True
  if path.startswith("docs/reviews/"):
    name = Path(path).name
    return (
      name.startswith("reopen-classification-")
      or "-audit-" in name
    ) and name.endswith(".md")
  if path.startswith("docs/"):
    return True
  if any(path.startswith(prefix) for prefix in POST_WRITE_VERIFICATION_DIR_PREFIXES):
    return True
  if not path.endswith(".md"):
    return False
  if any(path.startswith(prefix) for prefix in POST_WRITE_VERIFICATION_FILE_PREFIXES):
    return True
  if path.startswith(".reviewcompass/specs/"):
    return Path(path).name in POST_WRITE_VERIFICATION_SPEC_FILENAMES
  if any(path.startswith(prefix) for prefix in POST_WRITE_VERIFICATION_MD_DIR_PREFIXES):
    return True
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


def _review_run_target_files(run_dir: Path) -> List[str]:
  """review-run の target-manifest.yaml から対象ファイル一覧を返す。"""
  target_manifest = _load_yaml_dict(run_dir / "target-manifest.yaml")
  return [
    item.get("path")
    for item in target_manifest.get("target_files", [])
    if isinstance(item, dict) and item.get("path")
  ]


def _find_git_root(start: Path) -> Path:
  """start から上位へ .git を探し、見つからなければ現在ディレクトリを返す。"""
  found = _find_git_root_or_none(start)
  return found if found is not None else Path.cwd()


def _find_git_root_or_none(start: Path) -> Optional[Path]:
  """start から上位へ .git を探し、見つからなければ None を返す。"""
  current = start.resolve()
  if current.is_file():
    current = current.parent
  for candidate in [current] + list(current.parents):
    if (candidate / ".git").exists():
      return candidate
  return None


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


def _resolve_record_path(path_value: str, run_dir: Path, base_dir: Path) -> Path:
  path = Path(path_value)
  if path.is_absolute():
    return path
  base_candidate = base_dir / path
  if base_candidate.exists():
    return base_candidate
  return run_dir / path


def _rounds_raw_sha256_by_path(run_dir: Path) -> Dict[str, str]:
  """rounds.yaml の raw_path -> raw_sha256 対応を返す。"""
  rounds = _load_yaml_dict(run_dir / "rounds.yaml")
  model_results = rounds.get("model_results")
  if not isinstance(model_results, list):
    return {}
  raw_sha256 = {}
  for result in model_results:
    if not isinstance(result, dict):
      continue
    raw_path = result.get("raw_path")
    raw_hash = result.get("raw_sha256")
    if isinstance(raw_path, str) and raw_path and isinstance(raw_hash, str) and raw_hash:
      raw_sha256[raw_path] = raw_hash
  return raw_sha256


def _proxy_decision_errors(
  approval: Dict[str, Any],
  run_dir: Path,
  approval_path: Optional[Path],
  required_finding_ids: List[str],
  final_labels: Optional[Dict[str, str]],
) -> List[str]:
  errors = []
  proxy_model_id = approval.get("proxy_model_id")
  if not isinstance(proxy_model_id, str) or not proxy_model_id.strip():
    errors.append("proxy_model_id is required")

  proxy_decisions = approval.get("proxy_decisions")
  if not isinstance(proxy_decisions, dict):
    return errors + ["proxy_decisions must be a mapping"]

  base_dir = approval_path.parent if approval_path else run_dir
  expected_raw_sha256 = _rounds_raw_sha256_by_path(run_dir)
  for finding_id in sorted(set(required_finding_ids)):
    decision_ref = proxy_decisions.get(finding_id)
    if not isinstance(decision_ref, str) or not decision_ref:
      errors.append(f"proxy_decisions missing: {finding_id}")
      continue

    decision_path = _resolve_record_path(decision_ref, run_dir, base_dir)
    if not decision_path.is_file():
      errors.append(f"proxy decision file missing: {decision_ref}")
      continue

    decision = _load_yaml_dict(decision_path)
    if decision.get("approved_by") != "proxy_model":
      errors.append(f"{finding_id}: decision approved_by must be proxy_model")
    if decision.get("finding_id") != finding_id:
      errors.append(f"{finding_id}: decision finding_id mismatch")
    if decision.get("proxy_model_id") != proxy_model_id:
      errors.append(f"{finding_id}: proxy_model_id mismatch")

    for key in (
      "decision_prompt_path",
      "selected_option",
      "final_label",
      "rationale",
      "raw_response_path",
    ):
      value = decision.get(key)
      if not isinstance(value, str) or not value.strip():
        errors.append(f"{finding_id}: {key} is required")

    candidate_options = decision.get("candidate_options")
    if not isinstance(candidate_options, list) or not candidate_options:
      errors.append(f"{finding_id}: candidate_options is required")

    source_raw_paths = decision.get("source_raw_paths")
    if not isinstance(source_raw_paths, list) or not source_raw_paths:
      errors.append(f"{finding_id}: source_raw_paths is required")
    elif not all(isinstance(item, str) and item.strip() for item in source_raw_paths):
      errors.append(f"{finding_id}: source_raw_paths must contain paths")

    rejected_options = decision.get("rejected_options")
    if not isinstance(rejected_options, dict) or not rejected_options:
      errors.append(f"{finding_id}: rejected_options is required")

    expected_label = final_labels.get(finding_id) if final_labels else None
    if expected_label and decision.get("final_label") != expected_label:
      errors.append(f"{finding_id}: final_label mismatch")

    raw_response_path = decision.get("raw_response_path")
    if isinstance(raw_response_path, str) and raw_response_path.strip():
      raw_path = _resolve_record_path(raw_response_path, run_dir, decision_path.parent)
      if not raw_path.is_file():
        errors.append(f"{finding_id}: raw_response_path missing")
      elif raw_path.stat().st_size == 0:
        errors.append(f"{finding_id}: raw_response_path empty")

    decision_prompt_path = decision.get("decision_prompt_path")
    if isinstance(decision_prompt_path, str) and decision_prompt_path.strip():
      prompt_path = _resolve_record_path(decision_prompt_path, run_dir, decision_path.parent)
      if not prompt_path.is_file():
        errors.append(f"{finding_id}: decision_prompt_path missing")

    if isinstance(source_raw_paths, list):
      for source_raw_path in source_raw_paths:
        if not isinstance(source_raw_path, str) or not source_raw_path.strip():
          continue
        source_path = _resolve_record_path(source_raw_path, run_dir, decision_path.parent)
        if not source_path.is_file():
          errors.append(f"{finding_id}: source_raw_paths missing: {source_raw_path}")
          continue
        expected_hash = expected_raw_sha256.get(source_raw_path)
        if expected_hash and _sha256_file(source_path) != expected_hash:
          errors.append(
            f"{finding_id}: source_raw_paths sha256 mismatch: {source_raw_path}"
          )
  return errors


def _approval_errors(
  approval: Dict[str, Any],
  run_dir: Path,
  approval_path: Optional[Path],
  allowed_actions: tuple,
  required_finding_ids: List[str],
  final_labels: Optional[Dict[str, str]] = None,
) -> List[str]:
  errors = []
  if not approval:
    return ["approval record is required"]
  if approval.get("approved_action") not in allowed_actions:
    errors.append("approved_action does not allow this review-run action")
  approved_by = approval.get("approved_by")
  if approved_by not in ("user", "proxy_model"):
    errors.append("approved_by must be user or proxy_model")
  if approval.get("review_run_id") != run_dir.name:
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
  if approved_by == "proxy_model":
    errors.extend(
      _proxy_decision_errors(
        approval,
        run_dir,
        approval_path,
        required_finding_ids,
        final_labels,
      )
    )
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
  approval_path = Path(approval_record_path) if approval_record_path else None
  errors = _approval_errors(
    approval,
    run_dir,
    approval_path,
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


def _is_unresolved_triage_item(item: Dict[str, Any]) -> bool:
  """decided 以外の item は triage 未完了として扱う。"""
  return item.get("decision_status") != "decided"


def list_pending(review_run_dir: str) -> str:
  """未完了の triage item を Markdown 表で返す。"""
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
    if not _is_unresolved_triage_item(item):
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
    if _is_unresolved_triage_item(item):
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
    unresolved_for_model = [
      item for item in items
      if isinstance(item, dict)
      and item.get("source_model") == model_id
      and _is_unresolved_triage_item(item)
    ]
    if unresolved_for_model:
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
    if isinstance(item, dict) and _is_unresolved_triage_item(item)
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


def unresolved_triage_count(review_run_dir: str) -> int:
  """decided 以外の triage item が残る件数を返す。"""
  triage = _load_yaml_dict(_triage_path(Path(review_run_dir)))
  count = 0
  for item in triage.get("items", []):
    if isinstance(item, dict) and _is_unresolved_triage_item(item):
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
  target_files = _review_run_target_files(run_dir)
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
  unresolved = unresolved_triage_count(review_run_dir)

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
  git_root = _find_git_root_or_none(run_dir)
  if git_root is not None:
    review_targets = sorted(set(_review_run_target_files(run_dir)))
    current_targets = _current_git_post_write_targets(git_root)
    unreviewed_targets = sorted(set(current_targets) - set(review_targets))
    if unreviewed_targets:
      raise ValueError(
        "unreviewed post-write target changes remain: "
        + ", ".join(unreviewed_targets)
      )
  unresolved = unresolved_triage_count(review_run_dir)
  if unresolved > 0:
    raise ValueError(f"unresolved triage remains (human_required/draft): {unresolved}")
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


def assert_apply_fixes_ready(
  review_run_dir: str,
  approval_record_path: Optional[str] = None,
) -> None:
  """API review 所見への修正適用を始めてよいか機械判定する。"""
  run_dir = Path(review_run_dir)
  unresolved = unresolved_triage_count(review_run_dir)
  if unresolved > 0:
    raise ValueError(f"unresolved triage remains (human_required/draft): {unresolved}")

  triage = _load_yaml_dict(_triage_path(run_dir))
  items = triage.get("items")
  if not isinstance(items, list):
    items = []
  final_labels = {}
  required_ids = []
  for item in items:
    if not isinstance(item, dict):
      continue
    finding_id = item.get("finding_id")
    final_label = item.get("final_label")
    if (
      finding_id
      and item.get("decision_status") == "decided"
      and final_label in FIX_LABELS
    ):
      required_ids.append(finding_id)
      final_labels[finding_id] = final_label

  _require_review_run_approval(
    run_dir,
    approval_record_path,
    APPLY_FIXES_APPROVAL_ACTIONS,
    sorted(set(required_ids)),
    final_labels,
  )


def assert_review_report_ready(
  review_run_dir: str,
  report_path: str,
  ledger_path: str,
) -> None:
  """自動実行テスト報告に必要な成果物が揃っているか確認する。"""
  run_dir = Path(review_run_dir)
  required_run_files = [
    "target-manifest.yaml",
    "rounds.yaml",
    "triage.yaml",
    "model-result-summary.yaml",
    "must-fix-clusters.md",
    "must-fix-clusters.yaml",
    "proxy-decision-summary.md",
  ]
  errors = []
  for relpath in required_run_files:
    if not (run_dir / relpath).is_file():
      errors.append(f"required artifact missing: {relpath}")

  triage = _load_yaml_dict(run_dir / "triage.yaml")
  cluster_ids = []
  clusters_path = run_dir / "must-fix-clusters.yaml"
  proxy_summary_path = run_dir / "proxy-decision-summary.md"
  if clusters_path.is_file():
    clusters_data = _load_yaml_dict(clusters_path)
    clusters = clusters_data.get("clusters")
    if not isinstance(clusters, list) or not clusters:
      errors.append("must-fix-clusters.yaml clusters is required")
    else:
      for index, cluster in enumerate(clusters, start=1):
        if not isinstance(cluster, dict):
          errors.append(f"must-fix-clusters.yaml clusters[{index}] must be a mapping")
          continue
        cluster_id = cluster.get("cluster_id")
        cluster_label = cluster_id if isinstance(cluster_id, str) else f"#{index}"
        if not isinstance(cluster_id, str) or not cluster_id.strip():
          errors.append(f"must-fix-clusters.yaml cluster {cluster_label}: cluster_id is required")
        else:
          cluster_ids.append(cluster_id)
        if not isinstance(cluster.get("plain_explanation"), str) or not cluster.get("plain_explanation").strip():
          errors.append(
            f"must-fix-clusters.yaml cluster {cluster_label}: plain_explanation is required"
          )
        candidate_options = cluster.get("candidate_options")
        if not isinstance(candidate_options, list) or len(candidate_options) < 2:
          errors.append(
            f"must-fix-clusters.yaml cluster {cluster_label}: candidate_options "
            "requires at least two options"
          )
        else:
          option_ids = []
          for option_index, option in enumerate(candidate_options, start=1):
            if not isinstance(option, dict):
              errors.append(
                f"must-fix-clusters.yaml cluster {cluster_label}: "
                f"candidate_options[{option_index}] must be a mapping"
              )
              continue
            option_id = option.get("option_id", option.get("id"))
            if not isinstance(option_id, str) or not option_id.strip():
              errors.append(
                f"must-fix-clusters.yaml cluster {cluster_label}: "
                f"candidate_options[{option_index}].option_id is required"
              )
            else:
              option_ids.append(option_id)
            for key in ("summary", "tradeoff"):
              if not isinstance(option.get(key), str) or not option.get(key).strip():
                errors.append(
                  f"must-fix-clusters.yaml cluster {cluster_label}: "
                  f"candidate_options[{option_index}].{key} is required"
                )
          recommended_option = cluster.get("recommended_option")
          if not isinstance(recommended_option, str) or not recommended_option.strip():
            errors.append(
              f"must-fix-clusters.yaml cluster {cluster_label}: recommended_option is required"
            )
          elif option_ids and recommended_option not in option_ids:
            errors.append(
              f"must-fix-clusters.yaml cluster {cluster_label}: "
              "recommended_option must match candidate_options"
            )
        if not isinstance(cluster.get("recommended_reason"), str) or not cluster.get("recommended_reason").strip():
          errors.append(
            f"must-fix-clusters.yaml cluster {cluster_label}: recommended_reason is required"
          )
        final_label = cluster.get("proposed_final_label", cluster.get("final_label"))
        if final_label not in FINAL_LABELS:
          errors.append(
            f"must-fix-clusters.yaml cluster {cluster_label}: "
            "proposed_final_label/final_label is required"
          )

  if proxy_summary_path.is_file() and cluster_ids:
    proxy_summary = proxy_summary_path.read_text(encoding="utf-8")
    for cluster_id in cluster_ids:
      if cluster_id not in proxy_summary:
        errors.append(
          f"proxy-decision-summary.md missing cluster: {cluster_id}"
        )

  report = Path(report_path)
  if not report.is_file():
    errors.append(f"required artifact missing: {report.name}")
  else:
    report_text = report.read_text(encoding="utf-8")
    for heading in ("生じた問題", "対応したこと", "残った課題"):
      if heading not in report_text:
        errors.append(f"report section missing: {heading}")

  ledger = _load_yaml_dict(Path(ledger_path)) if Path(ledger_path).is_file() else {}
  if not ledger:
    errors.append(f"required artifact missing: {Path(ledger_path).name}")
  else:
    errors.extend(_autonomous_ledger_errors(ledger))
    errors.extend(_finding_fix_traceability_errors(triage, ledger))

  if errors:
    raise ValueError("; ".join(errors))


def _autonomous_ledger_errors(ledger: Dict[str, Any]) -> List[str]:
  """plan なしで監査できる自律実行 ledger か検査する。"""
  errors = []
  if ledger.get("mode") != "autonomous_parallel":
    errors.append("ledger.mode must be autonomous_parallel")
  if ledger.get("verdict") != "OK" or ledger.get("exit_code") != 0:
    errors.append("ledger verdict/exit_code must be OK/0")

  snapshot = ledger.get("execution_evidence_snapshot")
  if not isinstance(snapshot, dict):
    errors.append("ledger.execution_evidence_snapshot is required")
    snapshot = {}
  completed_tasks = snapshot.get("completed_tasks")
  if not isinstance(completed_tasks, list) or not completed_tasks:
    errors.append("ledger.execution_evidence_snapshot.completed_tasks is required")
  if not isinstance(snapshot.get("parallelized_operations"), list):
    errors.append("ledger.execution_evidence_snapshot.parallelized_operations is required")
  human_required_count = snapshot.get("human_required_count")
  if not isinstance(human_required_count, int):
    errors.append("ledger.execution_evidence_snapshot.human_required_count is required")
  elif human_required_count:
    errors.append("ledger.execution_evidence_snapshot.human_required_count must be 0")

  integration_result = ledger.get("integration_result")
  if not isinstance(integration_result, dict):
    errors.append("ledger.integration_result is required")
    integration_result = {}
  if integration_result.get("status") != "completed":
    errors.append("ledger.integration_result.status must be completed")
  if not integration_result.get("tests"):
    errors.append("ledger.integration_result.tests is required")
  if not integration_result.get("decision"):
    errors.append("ledger.integration_result.decision is required")
  return errors


def _accepted_finding_ids(triage: Dict[str, Any]) -> List[str]:
  """修正追跡が必要な accepted finding ids を返す。"""
  items = triage.get("items")
  if not isinstance(items, list):
    return []
  finding_ids = []
  for item in items:
    if not isinstance(item, dict):
      continue
    finding_id = item.get("finding_id")
    if (
      isinstance(finding_id, str)
      and finding_id
      and item.get("decision_status") == "decided"
      and item.get("final_label") in FIX_LABELS
    ):
      finding_ids.append(finding_id)
  return sorted(set(finding_ids))


def _finding_fix_traceability_errors(
  triage: Dict[str, Any],
  ledger: Dict[str, Any],
) -> List[str]:
  """accepted finding と fix/test/commit trace の対応を検査する。"""
  accepted_ids = _accepted_finding_ids(triage)
  if not accepted_ids:
    return []

  traces = ledger.get("finding_fix_traceability")
  if not isinstance(traces, list):
    return ["ledger.finding_fix_traceability is required"]

  by_finding = {}
  errors = []
  for index, trace in enumerate(traces, start=1):
    if not isinstance(trace, dict):
      errors.append(f"finding_fix_traceability[{index}] must be a mapping")
      continue
    finding_id = trace.get("finding_id")
    if not isinstance(finding_id, str) or not finding_id:
      errors.append(f"finding_fix_traceability[{index}].finding_id is required")
      continue
    by_finding[finding_id] = trace

  for finding_id in accepted_ids:
    trace = by_finding.get(finding_id)
    if not isinstance(trace, dict):
      errors.append(f"finding_fix_traceability missing finding: {finding_id}")
      continue
    resolution_commit = trace.get("resolution_commit")
    if not isinstance(resolution_commit, str) or not resolution_commit.strip():
      errors.append(f"{finding_id}: resolution_commit is required")
    changed_files = trace.get("changed_files")
    if not isinstance(changed_files, list) or not changed_files:
      errors.append(f"{finding_id}: changed_files is required")
    elif not all(isinstance(path, str) and path.strip() for path in changed_files):
      errors.append(f"{finding_id}: changed_files must contain paths")
    test_refs = trace.get("test_refs")
    if not isinstance(test_refs, list) or not test_refs:
      errors.append(f"{finding_id}: test_refs is required")
    elif not all(isinstance(path, str) and path.strip() for path in test_refs):
      errors.append(f"{finding_id}: test_refs must contain paths")
  return errors


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


def _count_by_label(items: List[Dict[str, Any]]) -> Dict[str, int]:
  """triage items を final_label ごとに数える。"""
  counts = {label: 0 for label in FINAL_LABELS}
  for item in items:
    label = item.get("final_label")
    if label in counts:
      counts[label] += 1
  return counts


def _markdown_table(headers: List[str], rows: List[List[Any]]) -> List[str]:
  """単純な Markdown table を返す。"""
  lines = [
    "| " + " | ".join(headers) + " |",
    "| " + " | ".join("---" for _ in headers) + " |",
  ]
  for row in rows:
    lines.append("| " + " | ".join(str(value) for value in row) + " |")
  return lines


def _joined_list(value: Any) -> str:
  """Markdown table 向けに list 値を改行なし文字列へ変換する。"""
  if isinstance(value, list):
    return "<br>".join(str(item) for item in value)
  return "" if value is None else str(value)


def build_review_traceability_report(review_run_dir: str, ledger_path: str) -> str:
  """review-run の主要証跡を 1 枚の Markdown report にまとめる。"""
  run_dir = Path(review_run_dir)
  summary = _load_yaml_dict(run_dir / "model-result-summary.yaml")
  triage = _load_yaml_dict(run_dir / "triage.yaml")
  clusters_data = _load_yaml_dict(run_dir / "must-fix-clusters.yaml")
  ledger = _load_yaml_dict(Path(ledger_path))
  proxy_summary_path = run_dir / "proxy-decision-summary.md"

  models = summary.get("models") if isinstance(summary.get("models"), list) else []
  items = triage.get("items") if isinstance(triage.get("items"), list) else []
  clusters = (
    clusters_data.get("clusters")
    if isinstance(clusters_data.get("clusters"), list)
    else []
  )
  label_counts = _count_by_label([
    item for item in items if isinstance(item, dict)
  ])
  integration_result = ledger.get("integration_result", {})
  if not isinstance(integration_result, dict):
    integration_result = {}
  fix_traces = (
    ledger.get("finding_fix_traceability")
    if isinstance(ledger.get("finding_fix_traceability"), list)
    else []
  )

  lines = [
    f"# Review Run Traceability Report: {run_dir.name}",
    "",
    "## Raw Responses",
  ]
  raw_rows = []
  for model in models:
    if not isinstance(model, dict):
      continue
    raw_rows.append([
      model.get("model_id", ""),
      model.get("raw_path", ""),
      model.get("parse_status", ""),
      model.get("triage_status", ""),
    ])
  lines.extend(_markdown_table(
    ["model", "raw_path", "parse_status", "triage_status"],
    raw_rows,
  ))

  lines.extend(["", "## Model Findings"])
  finding_rows = []
  for model in models:
    if not isinstance(model, dict):
      continue
    finding_rows.append([
      model.get("model_id", ""),
      model.get("findings_count", 0),
      model.get("must_fix_count", 0),
      model.get("should_fix_count", 0),
      model.get("leave_as_is_count", 0),
      model.get("human_required_count", 0),
    ])
  lines.extend(_markdown_table(
    [
      "model",
      "findings_count",
      "must_fix_count",
      "should_fix_count",
      "leave_as_is_count",
      "human_required_count",
    ],
    finding_rows,
  ))

  lines.extend([
    "",
    "## Three-Level Triage",
    "",
    f"- must-fix: {label_counts['must-fix']}",
    f"- should-fix: {label_counts['should-fix']}",
    f"- leave-as-is: {label_counts['leave-as-is']}",
    f"- decision_actor: {triage.get('decision_actor', '')}",
    f"- decision_actor_type: {triage.get('decision_actor_type', '')}",
    "",
    "## Important Findings",
  ])
  important_rows = []
  for cluster in clusters:
    if not isinstance(cluster, dict):
      continue
    important_rows.append([
      cluster.get("cluster_id", ""),
      cluster.get("severity_max", ""),
      cluster.get("proposed_final_label", cluster.get("final_label", "")),
      cluster.get("title", ""),
      cluster.get("plain_explanation", ""),
    ])
  lines.extend(_markdown_table(
    ["cluster", "severity", "label", "title", "plain_explanation"],
    important_rows,
  ))

  lines.extend(["", "## Adopted Options"])
  option_rows = []
  for cluster in clusters:
    if not isinstance(cluster, dict):
      continue
    option_rows.append([
      cluster.get("cluster_id", ""),
      f"option {cluster.get('recommended_option', '')}",
      cluster.get("recommended_reason", ""),
    ])
  lines.extend(_markdown_table(
    ["cluster", "selected", "reason"],
    option_rows,
  ))
  if proxy_summary_path.is_file():
    lines.extend([
      "",
      "Proxy decision summary: proxy-decision-summary.md",
    ])

  lines.extend(["", "## Finding-to-Fix Matrix"])
  fix_rows = []
  for trace in fix_traces:
    if not isinstance(trace, dict):
      continue
    fix_rows.append([
      trace.get("finding_id", ""),
      trace.get("resolution_commit", ""),
      _joined_list(trace.get("changed_files", [])),
      _joined_list(trace.get("test_refs", [])),
    ])
  lines.extend(_markdown_table(
    ["finding_id", "resolution_commit", "changed_files", "test_refs"],
    fix_rows,
  ))

  lines.extend([
    "",
    "## Implementation Result",
    "",
    f"- status: {integration_result.get('status', '')}",
    f"- tests: {integration_result.get('tests', '')}",
    f"- decision: {integration_result.get('decision', '')}",
    "",
  ])
  return "\n".join(lines)


def generate_review_traceability_report(
  review_run_dir: str,
  ledger_path: str,
  out_path: str,
) -> Path:
  """ready 検査後に review-run traceability report を書き出す。"""
  assert_review_report_ready(
    review_run_dir,
    str(Path(review_run_dir) / "autonomous-execution-report.md"),
    ledger_path,
  )
  output = Path(out_path)
  output.parent.mkdir(parents=True, exist_ok=True)
  output.write_text(
    build_review_traceability_report(review_run_dir, ledger_path),
    encoding="utf-8",
  )
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

  apply_fixes_parser = subparsers.add_parser("assert-apply-fixes-ready")
  apply_fixes_parser.add_argument("--review-run-dir", required=True)
  apply_fixes_parser.add_argument("--approval-record")

  report_parser = subparsers.add_parser("assert-review-report-ready")
  report_parser.add_argument("--review-run-dir", required=True)
  report_parser.add_argument("--report-path", required=True)
  report_parser.add_argument("--ledger-path", required=True)

  generate_report_parser = subparsers.add_parser("generate-review-report")
  generate_report_parser.add_argument("--review-run-dir", required=True)
  generate_report_parser.add_argument("--ledger-path", required=True)
  generate_report_parser.add_argument("--out", required=True)

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
    if args.command == "assert-apply-fixes-ready":
      assert_apply_fixes_ready(args.review_run_dir, args.approval_record)
      sys.stdout.write("apply_fixes_ready: true\n")
      return 0
    if args.command == "assert-review-report-ready":
      assert_review_report_ready(args.review_run_dir, args.report_path, args.ledger_path)
      sys.stdout.write("review_report_ready: true\n")
      return 0
    if args.command == "generate-review-report":
      output = generate_review_traceability_report(
        args.review_run_dir,
        args.ledger_path,
        args.out,
      )
      sys.stdout.write(f"{output}\n")
      return 0
  except Exception as exc:
    sys.stderr.write(f"エラー：{type(exc).__name__}: {exc}\n")
    return 1
  return 1


if __name__ == "__main__":
  sys.exit(main())
