"""commit approval nonce challenge helpers.

This module owns the runtime approval/challenge files used by
tools/check-workflow-action.py and guarded-git-commit.py.
"""
import hashlib
import json
import secrets
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path

from session_record_extractor.redact import (
  find_residual_secrets,
  redact_text,
)

from .runtime_paths import DEFAULT_COMMIT_APPROVAL_PATH


DEFAULT_COMMIT_APPROVAL_CHALLENGE_PATH = (
  ".reviewcompass/runtime/approvals/commit-approval-challenge.json"
)
CANONICAL_DIGEST_ALGORITHM = "commit-approval-v1"
APPROVAL_TTL_SECONDS = 600
FORBIDDEN_APPROVAL_FIELDS = {
  "llm",
  "provider",
  "model",
  "model_id",
  "proxy_model_id",
}
ATTESTATION_TYPE = "staged_content_nonce_binding"
GUARANTEE_SCOPE = "staged_content_binding_not_ui_utterance_proof"
SOURCE_OMISSION_REASONS = {
  "source_not_provided",
  "unsafe_source_omitted",
  "redaction_failed",
  "residual_secret_detected",
}


def utc_now():
  """現在 UTC を timezone-aware で返す。"""
  return datetime.now(timezone.utc)


def _run_git(cwd, args, text=True):
  return subprocess.run(
    ["git"] + args,
    cwd=str(cwd),
    capture_output=True,
    text=text,
  )


def _isoformat(value):
  return value.astimezone(timezone.utc).isoformat()


def _parse_datetime(value):
  if not isinstance(value, str) or not value:
    return None
  try:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
  except ValueError:
    return None
  if parsed.tzinfo is None:
    return None
  return parsed.astimezone(timezone.utc)


def _json_digest(data):
  payload = json.dumps(
    data,
    ensure_ascii=False,
    sort_keys=True,
    separators=(",", ":"),
  ).encode("utf-8")
  return hashlib.sha256(payload).hexdigest()


def staged_files(cwd):
  """staged ファイル一覧を git index から取得する。"""
  result = _run_git(cwd, ["diff", "--cached", "--name-only", "-z"], text=False)
  if result.returncode != 0:
    raise RuntimeError(result.stderr.decode("utf-8", errors="replace"))
  return [
    item.decode("utf-8")
    for item in result.stdout.split(b"\0")
    if item
  ]


def _staged_status_map(cwd):
  result = _run_git(cwd, ["diff", "--cached", "--name-status", "-z"], text=False)
  if result.returncode != 0:
    raise RuntimeError(result.stderr.decode("utf-8", errors="replace"))
  parts = [part.decode("utf-8") for part in result.stdout.split(b"\0") if part]
  status = {}
  i = 0
  while i < len(parts):
    code = parts[i]
    if code.startswith(("R", "C")) and i + 2 < len(parts):
      old_path = parts[i + 1]
      new_path = parts[i + 2]
      status[old_path] = "D"
      status[new_path] = code[0]
      i += 3
    elif i + 1 < len(parts):
      status[parts[i + 1]] = code[0]
      i += 2
    else:
      i += 1
  return status


def staged_blob_sha256(cwd, path):
  result = _run_git(cwd, ["show", f":{path}"], text=False)
  if result.returncode != 0:
    return None
  return hashlib.sha256(result.stdout).hexdigest()


def _staged_index_entry(cwd, path):
  result = _run_git(cwd, ["ls-files", "-s", "--", path])
  if result.returncode != 0:
    return None
  line = result.stdout.strip().splitlines()
  if not line:
    return None
  parts = line[0].split()
  if len(parts) < 2:
    return None
  return {
    "mode": parts[0],
    "object_id": parts[1],
  }


def canonical_target(cwd, paths=None):
  """staged exact index を versioned canonical form にする。"""
  selected = staged_files(cwd) if paths is None else list(paths)
  statuses = _staged_status_map(cwd)
  entries = []
  for path in sorted(selected):
    status = statuses.get(path, "M")
    index_entry = _staged_index_entry(cwd, path)
    blob_sha = staged_blob_sha256(cwd, path)
    deleted = status == "D" or index_entry is None or blob_sha is None
    entries.append({
      "path": path,
      "status": "D" if deleted else status,
      "mode": None if deleted else index_entry["mode"],
      "object_id": "DELETED" if deleted else index_entry["object_id"],
      "sha256": "DELETED" if deleted else blob_sha,
    })
  target = {
    "algorithm": CANONICAL_DIGEST_ALGORITHM,
    "entries": entries,
  }
  return {
    "algorithm": CANONICAL_DIGEST_ALGORITHM,
    "digest": _json_digest(target),
    "target": target,
  }


def target_sha256_from_canonical(canonical):
  """旧互換 target_sha256 を canonical target から作る。"""
  return {
    entry["path"]: entry["sha256"]
    for entry in canonical["target"]["entries"]
  }


def challenge_path(cwd):
  return Path(cwd) / DEFAULT_COMMIT_APPROVAL_CHALLENGE_PATH


def approval_path(cwd):
  return Path(cwd) / DEFAULT_COMMIT_APPROVAL_PATH


def prepare(cwd):
  """nonce challenge を作成する。"""
  now = utc_now()
  canonical = canonical_target(cwd)
  nonce = secrets.token_hex(24)
  challenge = {
    "schema_version": 1,
    "challenge_type": "commit_approval",
    "nonce": nonce,
    "created_at": _isoformat(now),
    "expires_at": _isoformat(now + timedelta(seconds=APPROVAL_TTL_SECONDS)),
    "ttl_seconds": APPROVAL_TTL_SECONDS,
    "target_files": [
      entry["path"]
      for entry in canonical["target"]["entries"]
    ],
    "target_digest": {
      "algorithm": CANONICAL_DIGEST_ALGORITHM,
      "digest": canonical["digest"],
    },
    "target": canonical["target"],
    "consumed": False,
    "invalidated": False,
  }
  path = challenge_path(cwd)
  path.parent.mkdir(parents=True, exist_ok=True)
  path.write_text(
    json.dumps(challenge, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8",
  )
  return {
    "status": "prepared",
    "challenge_path": DEFAULT_COMMIT_APPROVAL_CHALLENGE_PATH,
    "nonce": nonce,
    "created_at": challenge["created_at"],
    "expires_at": challenge["expires_at"],
    "ttl_seconds": APPROVAL_TTL_SECONDS,
    "target_files": challenge["target_files"],
    "target_digest": challenge["target_digest"],
  }


def _load_json_object(path, label):
  try:
    data = json.loads(path.read_text(encoding="utf-8"))
  except (OSError, json.JSONDecodeError) as e:
    raise ValueError(f"{label} を読めません: {e}") from e
  if not isinstance(data, dict):
    raise ValueError(f"{label} の形式が不正です（object ではありません）")
  return data


def _redact_source(source_text):
  try:
    redacted = redact_text(source_text)
  except Exception as e:  # pragma: no cover - defensive fail-closed
    return None, "redaction_failed", [str(e)]
  findings = find_residual_secrets(redacted)
  if findings:
    return None, "residual_secret_detected", findings
  return redacted, None, []


def record(cwd, nonce, source_text=None, no_source_text=False):
  """challenge nonce に対応する承認レコードを保存する。"""
  challenge = _load_json_object(challenge_path(cwd), "commit approval challenge")
  if challenge.get("nonce") != nonce:
    raise ValueError("nonce が challenge と一致しません")
  if challenge.get("invalidated") is True:
    raise ValueError("challenge は invalidated です")
  if challenge.get("consumed") is True:
    raise ValueError("challenge は consumed です")

  now = utc_now()
  created_at = _parse_datetime(challenge.get("created_at"))
  expires_at = _parse_datetime(challenge.get("expires_at"))
  if created_at is None or expires_at is None:
    raise ValueError("challenge の UTC ISO-8601 timestamp が不正です")
  if created_at > now:
    raise ValueError("clock rollback を検出したため commit approval を拒否します")
  if expires_at <= now:
    raise ValueError("challenge は期限切れです")

  current = canonical_target(cwd)
  challenge_digest = challenge.get("target_digest")
  if not isinstance(challenge_digest, dict):
    raise ValueError("challenge target_digest が不正です")
  if challenge_digest.get("algorithm") != CANONICAL_DIGEST_ALGORITHM:
    raise ValueError("challenge target_digest algorithm が不正です")
  if challenge_digest.get("digest") != current["digest"]:
    raise ValueError("staged 内容が challenge と一致しません")

  redacted_source = None
  source_omission_reason = None
  residual_findings = []
  if no_source_text:
    source_omission_reason = "source_not_provided"
  elif source_text is None:
    raise ValueError("source text は stdin または no-store mode で指定してください")
  else:
    source_bytes = source_text.encode("utf-8")
    if len(source_bytes) > 4096:
      source_omission_reason = "unsafe_source_omitted"
    else:
      redacted_source, source_omission_reason, residual_findings = _redact_source(
        source_text
      )

  approval = {
    "schema_version": 1,
    "approved_action": "commit",
    "approved_by": "user",
    "approved_at": _isoformat(now),
    "created_at": challenge["created_at"],
    "expires_at": challenge["expires_at"],
    "ttl_seconds": APPROVAL_TTL_SECONDS,
    "nonce": nonce,
    "challenge_path": DEFAULT_COMMIT_APPROVAL_CHALLENGE_PATH,
    "target_files": challenge["target_files"],
    "target_sha256": target_sha256_from_canonical(current),
    "target_digest": {
      "algorithm": CANONICAL_DIGEST_ALGORITHM,
      "digest": current["digest"],
    },
    "attestation_type": ATTESTATION_TYPE,
    "guarantee_scope": GUARANTEE_SCOPE,
    "source_omission_reason": source_omission_reason,
    "expires_after_commit": True,
    "consumed": False,
    "invalidated": False,
    "execution_delegation": {
      "delegated_to": "llm",
      "approved_by": "user",
      "approved_at": _isoformat(now),
      "explicit_instruction": "コミット代行も含めて自律実行",
      "rationale": "利用者が LLM によるコミット実行代行を明示承認",
    },
  }
  if redacted_source is not None:
    approval["source_text_redacted"] = redacted_source
  if residual_findings:
    approval["redaction_findings"] = residual_findings

  path = approval_path(cwd)
  path.parent.mkdir(parents=True, exist_ok=True)
  path.write_text(
    json.dumps(approval, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8",
  )
  return {
    "status": "recorded",
    "approval_path": DEFAULT_COMMIT_APPROVAL_PATH,
    "target_files": approval["target_files"],
    "target_digest": approval["target_digest"],
    "source_omission_reason": source_omission_reason,
  }


def invalidate(cwd):
  """challenge と approval を invalidated として保存する。"""
  changed = []
  for path in (challenge_path(cwd), approval_path(cwd)):
    if not path.exists():
      continue
    try:
      data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
      continue
    if not isinstance(data, dict):
      continue
    data["invalidated"] = True
    data["invalidated_at"] = _isoformat(utc_now())
    path.write_text(
      json.dumps(data, ensure_ascii=False, indent=2) + "\n",
      encoding="utf-8",
    )
    changed.append(str(path))
  return {
    "status": "invalidated",
    "invalidated_paths": changed,
  }


def _invalidate_runtime_records(cwd):
  try:
    invalidate(cwd)
  except OSError:
    pass


def validate(cwd, approval):
  """nonce approval record を現在の exact index に対して検証する。"""
  errors = []
  for field in sorted(FORBIDDEN_APPROVAL_FIELDS):
    if field in approval:
      errors.append(f"commit-approval record に禁止フィールド {field} があります")

  if approval.get("invalidated") is True:
    errors.append("commit-approval record は invalidated です")
  if approval.get("consumed") is True:
    errors.append("commit-approval record は consumed です")
  if approval.get("attestation_type") != ATTESTATION_TYPE:
    errors.append("commit-approval attestation_type が不正です")
  if approval.get("guarantee_scope") != GUARANTEE_SCOPE:
    errors.append("commit-approval guarantee_scope が不正です")
  source_omission_reason = approval.get("source_omission_reason")
  has_saved_source = isinstance(approval.get("source_text_redacted"), str)
  if source_omission_reason is None:
    if not has_saved_source:
      errors.append("commit-approval source_omission_reason が不正です")
  elif source_omission_reason not in SOURCE_OMISSION_REASONS:
    errors.append("commit-approval source_omission_reason が不正です")

  created_at = _parse_datetime(approval.get("created_at"))
  expires_at = _parse_datetime(approval.get("expires_at"))
  now = utc_now()
  if created_at is None or expires_at is None:
    errors.append("commit-approval timestamp が UTC ISO-8601 ではありません")
  else:
    ttl_seconds = int((expires_at - created_at).total_seconds())
    if ttl_seconds != APPROVAL_TTL_SECONDS or approval.get("ttl_seconds") != APPROVAL_TTL_SECONDS:
      errors.append("commit-approval TTL が 10 分ではありません")
    if created_at > now:
      errors.append("commit-approval clock rollback を検出しました")
    if expires_at <= now:
      errors.append("commit-approval は期限切れです")

  challenge_file = challenge_path(cwd)
  if not challenge_file.exists():
    errors.append("commit-approval challenge がありません")
    challenge = None
  else:
    try:
      challenge = _load_json_object(challenge_file, "commit approval challenge")
    except ValueError as e:
      errors.append(str(e))
      challenge = None

  if challenge is not None:
    if challenge.get("invalidated") is True:
      errors.append("commit-approval challenge は invalidated です")
    if challenge.get("consumed") is True:
      errors.append("commit-approval challenge は consumed です")
    if challenge.get("nonce") != approval.get("nonce"):
      errors.append("commit-approval nonce が challenge と一致しません")

  current = canonical_target(cwd)
  approval_digest = approval.get("target_digest")
  if not isinstance(approval_digest, dict):
    errors.append("commit-approval target_digest が不正です")
  elif approval_digest.get("algorithm") != CANONICAL_DIGEST_ALGORITHM:
    errors.append("commit-approval target_digest algorithm が不正です")
  elif approval_digest.get("digest") != current["digest"]:
    errors.append("commit-approval target_digest が staged exact index と一致しません")

  if challenge is not None:
    challenge_digest = challenge.get("target_digest")
    if not isinstance(challenge_digest, dict):
      errors.append("commit-approval challenge target_digest が不正です")
    elif challenge_digest.get("digest") != current["digest"]:
      errors.append("commit-approval challenge target_digest が staged exact index と一致しません")
    elif isinstance(approval_digest, dict) and challenge_digest.get("digest") != approval_digest.get("digest"):
      errors.append("commit-approval approval/challenge target_digest が一致しません")

  if errors:
    _invalidate_runtime_records(cwd)
  return errors
