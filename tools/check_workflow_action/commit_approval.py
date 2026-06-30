"""commit approval nonce challenge helpers.

This module owns the runtime approval/challenge files used by
tools/check-workflow-action.py and guarded-git-commit.py.
"""
import hashlib
import json
import re
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
DEFAULT_COMMIT_EXECUTION_DELEGATION_PATH = (
  ".reviewcompass/runtime/approvals/commit-execution-delegation.json"
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
EXECUTION_DELEGATION_ATTESTATION_TYPE = "commit_execution_delegation_nonce_binding"
EXECUTION_DELEGATION_GUARANTEE_SCOPE = (
  "stdin_text_instruction_bound_to_commit_approval_not_ui_utterance_proof"
)
ALLOWED_EXECUTION_DELEGATION_INSTRUCTIONS = {
  "コミット",
  "コミットして",
  "コミットを実行",
  "承認",
  "承諾",
  "commit",
  "commitして",
  "ok",
}
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
  return sorted(_staged_status_map(cwd))


def _staged_status_map(cwd):
  result = _run_git(cwd, ["diff", "--cached", "--name-status", "-z"], text=False)
  if result.returncode != 0:
    raise RuntimeError(result.stderr.decode("utf-8", errors="replace"))
  parts = [part.decode("utf-8") for part in result.stdout.split(b"\0") if part]
  status = {}
  i = 0
  while i < len(parts):
    code = parts[i]
    if code.startswith("R") and i + 2 < len(parts):
      old_path = parts[i + 1]
      new_path = parts[i + 2]
      status[old_path] = "D"
      status[new_path] = "R"
      i += 3
    elif code.startswith("C") and i + 2 < len(parts):
      new_path = parts[i + 2]
      status[new_path] = "C"
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


def delegation_path(cwd):
  return Path(cwd) / DEFAULT_COMMIT_EXECUTION_DELEGATION_PATH


def staged_file_set_digest_from_canonical(canonical):
  """staged ファイル集合（path/status/mode）だけの digest を返す。"""
  file_set = {
    "algorithm": CANONICAL_DIGEST_ALGORITHM,
    "entries": [
      {
        "path": entry["path"],
        "status": entry["status"],
        "mode": entry["mode"],
      }
      for entry in canonical["target"]["entries"]
    ],
  }
  return {
    "algorithm": CANONICAL_DIGEST_ALGORITHM,
    "digest": _json_digest(file_set),
  }


def approval_record_digest(approval):
  """commit-approval.json の canonical digest を返す。"""
  return {
    "algorithm": CANONICAL_DIGEST_ALGORITHM,
    "digest": _json_digest(approval),
  }


def prepare(cwd):
  """nonce challenge を作成する。"""
  now = utc_now()
  invalidate_runtime_records_for_new_prepare(cwd)
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


def _require_string_list(value, label):
  if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
    raise ValueError(f"{label} は文字列配列である必要があります")
  if len(value) != len(set(value)):
    raise ValueError(f"{label} に重複があります")
  return value


def _is_canonical_digest_text(value):
  return (
    isinstance(value, str)
    and len(value) == 64
    and all(char in "0123456789abcdef" for char in value)
  )


def _require_target_digest(value, label):
  if not isinstance(value, dict):
    raise ValueError(f"{label} target_digest が不正です")
  if value.get("algorithm") != CANONICAL_DIGEST_ALGORITHM:
    raise ValueError(f"{label} target_digest algorithm が不正です")
  digest = value.get("digest")
  if not _is_canonical_digest_text(digest):
    raise ValueError(f"{label} target_digest digest が不正です")
  return value


def approval_source_relay(cwd, source_text, target_digest=None):
  """ユーザ発話を TTY 入力として relay した証跡を作る。"""
  normalized = normalize_execution_delegation_instruction(source_text)
  current = canonical_target(cwd)
  digest = target_digest or {
    "algorithm": CANONICAL_DIGEST_ALGORITHM,
    "digest": current["digest"],
  }
  source_record = {
    "schema_version": 1,
    "source_kind": "user_turn_relay",
    "source_text_redacted": normalized,
    "relay_from_user_turn": True,
    "relayed_by": "llm",
    "target_digest": digest,
    "target_files": [
      entry["path"]
      for entry in current["target"]["entries"]
    ],
  }
  autonomous_approval = _candidate_selector_autonomous_approval(normalized)
  if autonomous_approval is not None:
    source_record["autonomous_execution_approval"] = autonomous_approval
  return source_record


def _atomic_write_json(path, data):
  path.parent.mkdir(parents=True, exist_ok=True)
  tmp_path = path.with_name(path.name + ".tmp")
  tmp_path.write_text(
    json.dumps(data, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8",
  )
  tmp_path.replace(path)


def _invalidate_existing_runtime_record(path, invalidated_at):
  if not path.exists():
    return False
  try:
    data = json.loads(path.read_text(encoding="utf-8"))
  except (OSError, json.JSONDecodeError):
    data = {}
  if not isinstance(data, dict):
    data = {}
  if data.get("invalidated") is True:
    return False
  data["invalidated"] = True
  data["invalidated_at"] = invalidated_at
  _atomic_write_json(path, data)
  return True


def invalidate_runtime_records_for_new_prepare(cwd):
  """新しい prepare 前に古い runtime 承認レコードを無効化する。"""
  invalidated_at = _isoformat(utc_now())
  changed = []
  for path in (approval_path(cwd), delegation_path(cwd)):
    if _invalidate_existing_runtime_record(path, invalidated_at):
      changed.append(str(path))
  return changed


def _lower_ascii(text):
  return "".join(
    chr(ord(char) + 32) if "A" <= char <= "Z" else char
    for char in text
  )


def _candidate_selector_autonomous_approval(normalized):
  match = re.fullmatch(r"([1-9][0-9]*)を(pushまで)?自律実行", normalized)
  if not match:
    return None
  raw_index = match.group(1)
  through_push = match.group(2) == "pushまで"
  return {
    "raw_instruction": normalized,
    "candidate_selector": {
      "type": "ordinal",
      "index": int(raw_index),
      "raw": raw_index,
    },
    "operation_id": (
      "autonomous-through-push" if through_push else "autonomous-through-commit"
    ),
    "commit_execution_delegation": "included",
    "push_execution_delegation": "included" if through_push else "excluded",
  }


def normalize_execution_delegation_instruction(source_text):
  """commit 実行代行承認の stdin を厳密に正規化する。"""
  if isinstance(source_text, bytes):
    source_bytes = source_text
    try:
      text = source_bytes.decode("utf-8")
    except UnicodeDecodeError as e:
      raise ValueError(f"source text は UTF-8 である必要があります: {e}") from e
  elif isinstance(source_text, str):
    text = source_text
    source_bytes = text.encode("utf-8")
  else:
    raise ValueError("source text は bytes または str である必要があります")

  if len(source_bytes) > 256:
    raise ValueError("source text は 256 bytes 以下である必要があります")
  if "\x00" in text:
    raise ValueError("source text に NUL は使えません")
  if "\r" in text:
    raise ValueError("source text に CR/CRLF は使えません")
  if text.endswith("\n\n"):
    raise ValueError("source text の末尾 LF は 1 個までです")
  if text.endswith("\n"):
    text = text[:-1]
  if "\n" in text:
    raise ValueError("source text に内部改行は使えません")

  normalized = _lower_ascii(text.strip(" \t\f\v\u3000"))
  if normalized.endswith("。"):
    normalized = normalized[:-1]
  normalized = normalized.strip(" \t\f\v\u3000")
  if not normalized:
    raise ValueError("source text が空です")
  if (
    normalized not in ALLOWED_EXECUTION_DELEGATION_INSTRUCTIONS
    and _candidate_selector_autonomous_approval(normalized) is None
  ):
    raise ValueError("source text が commit 実行代行承認の許可文言ではありません")
  return normalized


def _validate_ready_for_delegation(cwd, nonce):
  challenge = _load_json_object(challenge_path(cwd), "commit approval challenge")
  approval = _load_json_object(approval_path(cwd), "commit approval record")
  if challenge.get("nonce") != nonce:
    raise ValueError("nonce が challenge と一致しません")
  if approval.get("nonce") != nonce:
    raise ValueError("nonce が commit approval record と一致しません")
  errors = validate(cwd, approval)
  if errors:
    raise ValueError("; ".join(errors))
  return challenge, approval


def delegate_execution(cwd, nonce, source_text, approval_source=None):
  """commit 実行代行承認を commit-approval とは別レコードに保存する。"""
  normalized_instruction = normalize_execution_delegation_instruction(source_text)
  redacted, source_omission_reason, findings = _redact_source(normalized_instruction)
  if source_omission_reason is not None or findings:
    raise ValueError("source text の redaction に失敗したため実行代行承認を保存しません")

  _, approval = _validate_ready_for_delegation(cwd, nonce)
  existing_path = delegation_path(cwd)
  if existing_path.exists():
    existing = _load_json_object(existing_path, "commit execution delegation")
    expires_at = _parse_datetime(existing.get("expires_at"))
    if (
      existing.get("consumed") is not True
      and existing.get("invalidated") is not True
      and (expires_at is None or expires_at > utc_now())
    ):
      existing_errors = validate_execution_delegation(cwd, approval)
      if not existing_errors and existing.get("explicit_instruction") == redacted:
        return {
          "status": "delegated",
          "delegation_path": DEFAULT_COMMIT_EXECUTION_DELEGATION_PATH,
          "target_digest": existing["target_digest"],
          "staged_file_set_digest": existing["staged_file_set_digest"],
        }
      raise ValueError("未消費の commit-execution-delegation record が既にあります")

  current = canonical_target(cwd)
  now = utc_now()
  source_record = approval_source or approval_source_relay(
    cwd,
    source_text,
    {
      "algorithm": CANONICAL_DIGEST_ALGORITHM,
      "digest": current["digest"],
    },
  )
  record_data = {
    "schema_version": 1,
    "approved_action": "commit_execution_delegation",
    "delegated_action": "commit",
    "delegated_to": "llm",
    "approved_by": "user",
    "nonce": nonce,
    "target_digest": {
      "algorithm": CANONICAL_DIGEST_ALGORITHM,
      "digest": current["digest"],
    },
    "staged_file_set_digest": staged_file_set_digest_from_canonical(current),
    "staged_content_approval_digest": approval_record_digest(approval),
    "challenge_path": DEFAULT_COMMIT_APPROVAL_CHALLENGE_PATH,
    "approval_record_path": DEFAULT_COMMIT_APPROVAL_PATH,
    "created_at": _isoformat(now),
    "expires_at": approval["expires_at"],
    "explicit_instruction": redacted,
    "instruction_sha256": hashlib.sha256(
      redacted.encode("utf-8")
    ).hexdigest(),
    "approval_source": source_record,
    "attestation_type": EXECUTION_DELEGATION_ATTESTATION_TYPE,
    "guarantee_scope": EXECUTION_DELEGATION_GUARANTEE_SCOPE,
    "consumed": False,
    "invalidated": False,
  }

  _, approval_before_write = _validate_ready_for_delegation(cwd, nonce)
  if approval_record_digest(approval_before_write) != record_data["staged_content_approval_digest"]:
    raise ValueError("commit approval record が実行代行承認の保存直前に変化しました")
  fresh_current = canonical_target(cwd)
  if fresh_current["digest"] != current["digest"]:
    raise ValueError("staged 内容が実行代行承認の保存直前に変化しました")
  record_data["target_digest"] = {
    "algorithm": CANONICAL_DIGEST_ALGORITHM,
    "digest": fresh_current["digest"],
  }
  record_data["staged_file_set_digest"] = staged_file_set_digest_from_canonical(
    fresh_current
  )

  _atomic_write_json(existing_path, record_data)
  return {
    "status": "delegated",
    "delegation_path": DEFAULT_COMMIT_EXECUTION_DELEGATION_PATH,
    "target_digest": record_data["target_digest"],
    "staged_file_set_digest": record_data["staged_file_set_digest"],
  }


def record(cwd, nonce, source_text=None, no_source_text=False, approval_source=None):
  """challenge nonce に対応する承認レコードを保存する。"""
  challenge = _load_json_object(challenge_path(cwd), "commit approval challenge")
  if challenge.get("nonce") != nonce:
    raise ValueError("nonce が challenge と一致しません")
  if challenge.get("invalidated") is True:
    raise ValueError("challenge は invalidated です")
  if challenge.get("consumed") is True:
    raise ValueError("challenge は consumed です")
  challenge_target_files = _require_string_list(
    challenge.get("target_files"),
    "challenge target_files",
  )

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
  challenge_digest = _require_target_digest(
    challenge.get("target_digest"),
    "challenge",
  )
  if challenge_digest.get("digest") != current["digest"]:
    raise ValueError("staged 内容が challenge と一致しません")
  if challenge_target_files != [
    entry["path"]
    for entry in current["target"]["entries"]
  ]:
    raise ValueError("challenge target_files が staged exact index と一致しません")

  path = approval_path(cwd)
  if path.exists():
    existing = _load_json_object(path, "commit approval record")
    if existing.get("nonce") == nonce and not validate(cwd, existing):
      return {
        "status": "recorded",
        "approval_path": DEFAULT_COMMIT_APPROVAL_PATH,
        "target_files": existing["target_files"],
        "target_digest": existing["target_digest"],
        "source_omission_reason": existing.get("source_omission_reason"),
      }

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
    "expires_after_commit": True,
    "consumed": False,
    "invalidated": False,
  }
  if approval_source is not None:
    approval["approval_source"] = approval_source
  elif source_text is not None:
    try:
      normalized_source = normalize_execution_delegation_instruction(source_text)
    except ValueError:
      normalized_source = None
    if (
      normalized_source is not None
      and _candidate_selector_autonomous_approval(normalized_source) is not None
    ):
      approval["approval_source"] = approval_source_relay(
        cwd,
        source_text,
        approval["target_digest"],
      )
  if source_omission_reason is not None:
    approval["source_omission_reason"] = source_omission_reason
  if redacted_source is not None:
    approval["source_text_redacted"] = redacted_source
  if residual_findings:
    approval["redaction_findings"] = residual_findings

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
  for path in (challenge_path(cwd), approval_path(cwd), delegation_path(cwd)):
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


def _write_runtime_invalidated_approval(cwd, approval, invalidated_at):
  if not isinstance(approval, dict) or not approval.get("nonce"):
    return
  path = approval_path(cwd)
  if path.exists():
    return
  data = dict(approval)
  data["invalidated"] = True
  data["invalidated_at"] = invalidated_at
  path.parent.mkdir(parents=True, exist_ok=True)
  path.write_text(
    json.dumps(data, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8",
  )


def _invalidate_runtime_records(cwd, approval=None):
  try:
    invalidated_at = _isoformat(utc_now())
    invalidate(cwd)
    _write_runtime_invalidated_approval(cwd, approval, invalidated_at)
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
  elif not _is_canonical_digest_text(approval_digest.get("digest")):
    errors.append("commit-approval target_digest digest が不正です")
  elif approval_digest.get("digest") != current["digest"]:
    errors.append("commit-approval target_digest が staged exact index と一致しません")

  if challenge is not None:
    challenge_digest = challenge.get("target_digest")
    if not isinstance(challenge_digest, dict):
      errors.append("commit-approval challenge target_digest が不正です")
    elif not _is_canonical_digest_text(challenge_digest.get("digest")):
      errors.append("commit-approval challenge target_digest digest が不正です")
    elif challenge_digest.get("digest") != current["digest"]:
      errors.append("commit-approval challenge target_digest が staged exact index と一致しません")
    elif isinstance(approval_digest, dict) and challenge_digest.get("digest") != approval_digest.get("digest"):
      errors.append("commit-approval approval/challenge target_digest が一致しません")

  if errors:
    _invalidate_runtime_records(cwd, approval)
  return errors


def validate_execution_delegation(cwd, approval):
  """commit 実行代行承認レコードを現在の exact index に対して検証する。"""
  path = delegation_path(cwd)
  if not path.exists():
    return [
      "LLM によるコミット実行代行の明示承認がありません"
      f"（{DEFAULT_COMMIT_EXECUTION_DELEGATION_PATH} が必要）"
    ]

  try:
    delegation = _load_json_object(path, "commit execution delegation")
  except ValueError as e:
    return [str(e)]

  errors = []
  allowed_fields = {
    "schema_version",
    "approved_action",
    "delegated_action",
    "delegated_to",
    "approved_by",
    "nonce",
    "target_digest",
    "staged_file_set_digest",
    "staged_content_approval_digest",
    "challenge_path",
    "approval_record_path",
    "created_at",
    "expires_at",
    "explicit_instruction",
    "instruction_sha256",
    "approval_source",
    "attestation_type",
    "guarantee_scope",
    "consumed",
    "invalidated",
  }
  missing = sorted(allowed_fields - set(delegation))
  extra = sorted(set(delegation) - allowed_fields)
  if missing:
    errors.append("commit-execution-delegation 必須フィールド不足: " + ", ".join(missing))
  if extra:
    errors.append("commit-execution-delegation 不明フィールド: " + ", ".join(extra))
  for field in sorted(FORBIDDEN_APPROVAL_FIELDS):
    if field in delegation:
      errors.append(f"commit-execution-delegation record に禁止フィールド {field} があります")

  expected_values = {
    "approved_action": "commit_execution_delegation",
    "delegated_action": "commit",
    "delegated_to": "llm",
    "approved_by": "user",
    "challenge_path": DEFAULT_COMMIT_APPROVAL_CHALLENGE_PATH,
    "approval_record_path": DEFAULT_COMMIT_APPROVAL_PATH,
    "attestation_type": EXECUTION_DELEGATION_ATTESTATION_TYPE,
    "guarantee_scope": EXECUTION_DELEGATION_GUARANTEE_SCOPE,
    "consumed": False,
    "invalidated": False,
  }
  for field, expected in expected_values.items():
    if delegation.get(field) != expected:
      errors.append(f"commit-execution-delegation {field} が不正です")

  if delegation.get("nonce") != approval.get("nonce"):
    errors.append("commit-execution-delegation nonce が commit-approval と一致しません")

  created_at = _parse_datetime(delegation.get("created_at"))
  expires_at = _parse_datetime(delegation.get("expires_at"))
  now = utc_now()
  if created_at is None or expires_at is None:
    errors.append("commit-execution-delegation timestamp が UTC ISO-8601 ではありません")
  else:
    if created_at > now:
      errors.append("commit-execution-delegation clock rollback を検出しました")
    if expires_at <= now:
      errors.append("commit-execution-delegation は期限切れです")
  if delegation.get("expires_at") != approval.get("expires_at"):
    errors.append("commit-execution-delegation expires_at が commit-approval と一致しません")

  instruction = delegation.get("explicit_instruction")
  if instruction not in ALLOWED_EXECUTION_DELEGATION_INSTRUCTIONS:
    errors.append("commit-execution-delegation explicit_instruction が不正です")
  elif delegation.get("instruction_sha256") != hashlib.sha256(
    instruction.encode("utf-8")
  ).hexdigest():
    errors.append("commit-execution-delegation instruction_sha256 が不正です")

  current = canonical_target(cwd)
  target_digest = delegation.get("target_digest")
  if not isinstance(target_digest, dict):
    errors.append("commit-execution-delegation target_digest が不正です")
  elif target_digest.get("algorithm") != CANONICAL_DIGEST_ALGORITHM:
    errors.append("commit-execution-delegation target_digest algorithm が不正です")
  elif not _is_canonical_digest_text(target_digest.get("digest")):
    errors.append("commit-execution-delegation target_digest digest が不正です")
  elif target_digest.get("digest") != current["digest"]:
    errors.append("commit-execution-delegation target_digest が staged exact index と一致しません")

  staged_file_set_digest = delegation.get("staged_file_set_digest")
  expected_file_set_digest = staged_file_set_digest_from_canonical(current)
  if staged_file_set_digest != expected_file_set_digest:
    errors.append("commit-execution-delegation staged_file_set_digest が一致しません")

  staged_content_approval_digest = delegation.get("staged_content_approval_digest")
  expected_approval_digest = approval_record_digest(approval)
  if staged_content_approval_digest != expected_approval_digest:
    errors.append("commit-execution-delegation staged_content_approval_digest が一致しません")

  if errors:
    _invalidate_runtime_records(cwd, approval)
  return errors
