"""Commit unit helpers for isolating staged commit candidates."""

import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import yaml


DEFAULT_COMMIT_UNIT_PATH = ".reviewcompass/runtime/work-units/commit-unit.json"
SCHEMA_VERSION = "commit-unit-v1"


def _json_digest(data):
  payload = json.dumps(
    data,
    ensure_ascii=False,
    sort_keys=True,
    separators=(",", ":"),
  ).encode("utf-8")
  return hashlib.sha256(payload).hexdigest()


def _git_cached_files(cwd):
  result = subprocess.run(
    ["git", "diff", "--cached", "--name-only", "-z"],
    cwd=str(cwd),
    capture_output=True,
    text=False,
  )
  if result.returncode != 0:
    raise RuntimeError(result.stderr.decode("utf-8", errors="replace"))
  return sorted(f.decode("utf-8") for f in result.stdout.split(b"\0") if f)


def _run_git(cwd, args):
  result = subprocess.run(
    ["git", *args],
    cwd=str(cwd),
    capture_output=True,
    text=True,
  )
  if result.returncode != 0:
    raise RuntimeError(result.stderr)
  return result.stdout.strip()


def _staged_file_hash(cwd, filepath):
  result = subprocess.run(
    ["git", "show", f":{filepath}"],
    cwd=str(cwd),
    capture_output=True,
  )
  if result.returncode != 0:
    return "DELETED"
  return hashlib.sha256(result.stdout).hexdigest()


def staged_digest(cwd, staged_files):
  canonical = {
    "algorithm": SCHEMA_VERSION,
    "entries": [
      {
        "path": path,
        "sha256": _staged_file_hash(cwd, path),
      }
      for path in sorted(staged_files)
    ],
  }
  return {
    "algorithm": SCHEMA_VERSION,
    "digest": _json_digest(canonical),
    "target": canonical,
  }


def _record_path(cwd, path=None):
  return Path(cwd) / (path or DEFAULT_COMMIT_UNIT_PATH)


def _now_id():
  return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _write_record(cwd, record, path=None):
  record_path = _record_path(cwd, path)
  record_path.parent.mkdir(parents=True, exist_ok=True)
  record_path.write_text(
    json.dumps(record, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8",
  )
  return record_path


def _new_record(cwd, work_unit_id, allowed_files, staged_files, message=None, rationale=None):
  digest = staged_digest(cwd, staged_files)
  record = {
    "schema_version": SCHEMA_VERSION,
    "commit_unit_id": f"commit-unit-{_now_id()}",
    "work_unit_id": work_unit_id,
    "status": "frozen",
    "created_at": datetime.now(timezone.utc).isoformat(),
    "allowed_files": sorted(set(allowed_files or [])),
    "target_files": sorted(set(allowed_files or [])),
    "staged_files": staged_files,
    "staged_digest": {
      "algorithm": digest["algorithm"],
      "digest": digest["digest"],
    },
    "target": digest["target"],
  }
  if message is not None:
    record["message"] = message
  if rationale is not None:
    record["rationale"] = rationale
  return record


def freeze(cwd, work_unit_id, allowed_files, path=None):
  cwd = Path(cwd)
  staged_files = _git_cached_files(cwd)
  allowed = sorted(set(allowed_files or []))
  extra = [filepath for filepath in staged_files if filepath not in set(allowed)]
  if not staged_files:
    return {
      "status": "error",
      "verdict": "DEVIATION",
      "codes": ["NO_STAGED_FILES"],
      "reasons": ["commit unit として freeze する staged file がありません"],
    }
  if extra:
    return {
      "status": "error",
      "verdict": "DEVIATION",
      "codes": ["COMMIT_MIXING_RISK"],
      "reasons": ["staged files が allowed files を超えています"],
      "current_state": {
        "staged_files": staged_files,
        "extra_staged_files": extra,
      },
    }
  record = _new_record(cwd, work_unit_id, allowed, staged_files)
  record_path = _write_record(cwd, record, path)
  return {
    "status": "frozen",
    "verdict": "OK",
    "path": str(record_path.relative_to(cwd)),
    "record": record,
  }


def stage(cwd, work_unit_id, target_files, message, rationale, path=None):
  """target_files だけを stage し、その staged index を commit unit に固定する。"""
  cwd = Path(cwd)
  targets = sorted(set(target_files or []))
  if not targets:
    return {
      "status": "error",
      "verdict": "DEVIATION",
      "codes": ["NO_TARGET_FILES"],
      "reasons": ["commit unit target_files が指定されていません"],
    }
  missing = [target for target in targets if not (cwd / target).exists()]
  if missing:
    return {
      "status": "error",
      "verdict": "DEVIATION",
      "codes": ["TARGET_FILE_NOT_FOUND"],
      "reasons": ["commit unit target_files に存在しないファイルがあります"],
      "current_state": {"missing_target_files": missing},
    }

  _run_git(cwd, ["reset", "--quiet"])
  _run_git(cwd, ["add", "--", *targets])
  staged_files = _git_cached_files(cwd)
  extra = [filepath for filepath in staged_files if filepath not in set(targets)]
  if extra:
    return {
      "status": "error",
      "verdict": "DEVIATION",
      "codes": ["COMMIT_MIXING_RISK"],
      "reasons": ["target_files 外の staged file があります"],
      "current_state": {
        "staged_files": staged_files,
        "extra_staged_files": extra,
      },
    }
  record = _new_record(
    cwd,
    work_unit_id,
    targets,
    staged_files,
    message=message,
    rationale=rationale,
  )
  record_path = _write_record(cwd, record, path)
  return {
    "status": "staged",
    "verdict": "OK",
    "path": str(record_path.relative_to(cwd)),
    "record": record,
  }


def suggest(cwd, backlog_id, checklist_path):
  """backlog/checklist から commit message / rationale 候補を定型生成する。"""
  cwd = Path(cwd)
  path = cwd / checklist_path
  if not path.exists():
    return {
      "verdict": "DEVIATION",
      "codes": ["CHECKLIST_NOT_FOUND"],
      "reasons": [f"checklist が見つかりません: {checklist_path}"],
    }
  data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
  checklist_id = data.get("checklist_id") or Path(checklist_path).stem
  summary = data.get("completion_summary") or ""
  message = f"Implement {backlog_id}"
  rationale_parts = [
    f"backlog TODO {backlog_id} の作業結果",
    f"checklist {checklist_id}",
  ]
  if summary:
    rationale_parts.append(summary)
  return {
    "verdict": "OK",
    "message": message,
    "rationale": " / ".join(rationale_parts),
    "source": {
      "backlog_id": backlog_id,
      "checklist_path": checklist_path,
      "checklist_id": checklist_id,
    },
  }


def postcondition(cwd):
  """commit 後の状態を定型出力する。"""
  cwd = Path(cwd)
  status = _run_git(cwd, ["status", "--porcelain", "-uall"])
  head_commit = _run_git(cwd, ["rev-parse", "HEAD"])
  ahead_count = None
  try:
    ahead_count = int(_run_git(cwd, ["rev-list", "--count", "origin/main..HEAD"]))
  except RuntimeError:
    ahead_count = None
  is_dirty = bool(status.strip())
  push_candidate = bool(not is_dirty and ahead_count is not None and ahead_count > 0)
  return {
    "verdict": "OK",
    "is_dirty": is_dirty,
    "head_commit": head_commit,
    "ahead_count": ahead_count,
    "push_candidate": push_candidate,
  }


def load(cwd, path=None):
  record_path = _record_path(cwd, path)
  if not record_path.exists():
    return None, [f"commit unit record がありません: {record_path}"]
  try:
    data = json.loads(record_path.read_text(encoding="utf-8"))
  except (OSError, json.JSONDecodeError) as exc:
    return None, [f"commit unit record を読めません: {exc}"]
  if not isinstance(data, dict):
    return None, ["commit unit record は object である必要があります"]
  return data, []


def check(cwd, path=None):
  cwd = Path(cwd)
  record, errors = load(cwd, path)
  if errors:
    return {
      "verdict": "DEVIATION",
      "codes": ["NO_COMMIT_UNIT_RECORD"],
      "reasons": errors,
      "current_state": {},
    }

  staged_files = _git_cached_files(cwd)
  allowed = set(record.get("allowed_files") or [])
  extra = [filepath for filepath in staged_files if filepath not in allowed]
  current_digest = staged_digest(cwd, staged_files)
  recorded_digest = record.get("staged_digest", {}).get("digest")

  codes = []
  reasons = []
  if extra:
    codes.append("COMMIT_MIXING_RISK")
    reasons.append("staged files が commit unit の allowed files を超えています")
  if recorded_digest != current_digest["digest"]:
    codes.append("STALE_COMMIT_UNIT")
    reasons.append("staged digest が frozen commit unit と一致しません")

  return {
    "verdict": "DEVIATION" if codes else "OK",
    "codes": codes,
    "reasons": reasons,
    "record": record,
    "current_state": {
      "staged_files": staged_files,
      "extra_staged_files": extra,
      "staged_digest": {
        "algorithm": current_digest["algorithm"],
        "digest": current_digest["digest"],
      },
    },
  }
