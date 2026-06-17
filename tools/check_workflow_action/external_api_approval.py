"""external API review approval nonce challenge helpers."""
import hashlib
import json
import secrets
from datetime import datetime, timedelta, timezone
from pathlib import Path

try:
  from session_record_extractor.redact import (
    find_residual_secrets,
    redact_text,
  )
except ModuleNotFoundError:  # run_review.py imports this module from project root.
  from tools.session_record_extractor.redact import (
    find_residual_secrets,
    redact_text,
  )


DEFAULT_EXTERNAL_API_APPROVAL_PATH = (
  ".reviewcompass/runtime/approvals/external-api-approval.json"
)
DEFAULT_EXTERNAL_API_APPROVAL_CHALLENGE_PATH = (
  ".reviewcompass/runtime/approvals/external-api-approval-challenge.json"
)
APPROVAL_TTL_SECONDS = 600
ATTESTATION_TYPE = "external_api_review_nonce_binding"
GUARANTEE_SCOPE = "target_provider_phase_criteria_binding"
SOURCE_OMISSION_REASONS = {
  "source_not_provided",
  "unsafe_source_omitted",
  "redaction_failed",
  "residual_secret_detected",
}


def utc_now():
  return datetime.now(timezone.utc)


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


def _sha256_file(path):
  return hashlib.sha256(path.read_bytes()).hexdigest()


def _redact_source(source_text):
  try:
    redacted = redact_text(source_text)
  except Exception as e:  # pragma: no cover - defensive fail-closed
    return None, "redaction_failed", [str(e)]
  findings = find_residual_secrets(redacted)
  if findings:
    return None, "residual_secret_detected", findings
  return redacted, None, []


def _load_json_object(path, label):
  try:
    data = json.loads(path.read_text(encoding="utf-8"))
  except (OSError, json.JSONDecodeError) as e:
    raise ValueError(f"{label} を読めません: {e}") from e
  if not isinstance(data, dict):
    raise ValueError(f"{label} の形式が不正です（object ではありません）")
  return data


def _atomic_write_json(path, data):
  path.parent.mkdir(parents=True, exist_ok=True)
  tmp_path = path.with_name(path.name + ".tmp")
  tmp_path.write_text(
    json.dumps(data, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8",
  )
  tmp_path.replace(path)


def _normalize_target_path(cwd, target):
  path = Path(target)
  if not path.is_absolute():
    path = Path(cwd) / path
  return path


def _target_sha256(cwd, target_files):
  result = {}
  for target in target_files:
    path = _normalize_target_path(cwd, target)
    if not path.is_file():
      raise ValueError(f"target file が存在しません: {target}")
    result[target] = _sha256_file(path)
  return result


def challenge_path(cwd):
  return Path(cwd) / DEFAULT_EXTERNAL_API_APPROVAL_CHALLENGE_PATH


def approval_path(cwd):
  return Path(cwd) / DEFAULT_EXTERNAL_API_APPROVAL_PATH


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


def prepare(
  cwd,
  target_files,
  phase,
  criteria,
  variant,
  review_run_dir,
  providers,
  models,
):
  """外部 API 送信承認の nonce challenge を作成する。"""
  if not target_files:
    raise ValueError("target_files が空です")
  if not providers:
    raise ValueError("providers が空です")
  if not models:
    raise ValueError("models が空です")
  now = utc_now()
  invalidated_at = _isoformat(now)
  _invalidate_existing_runtime_record(approval_path(cwd), invalidated_at)
  target_sha256 = _target_sha256(cwd, target_files)
  nonce = secrets.token_hex(24)
  challenge = {
    "schema_version": 1,
    "challenge_type": "external_api_approval",
    "approved_action": "external_api_review",
    "nonce": nonce,
    "created_at": _isoformat(now),
    "expires_at": _isoformat(now + timedelta(seconds=APPROVAL_TTL_SECONDS)),
    "ttl_seconds": APPROVAL_TTL_SECONDS,
    "target_files": list(target_files),
    "target_sha256": target_sha256,
    "phase": phase,
    "criteria": criteria,
    "variant": variant,
    "review_run_dir": review_run_dir,
    "providers": list(providers),
    "models": list(models),
    "consumed": False,
    "invalidated": False,
  }
  _atomic_write_json(challenge_path(cwd), challenge)
  return {
    "status": "prepared",
    "approved_action": "external_api_review",
    "challenge_path": DEFAULT_EXTERNAL_API_APPROVAL_CHALLENGE_PATH,
    "nonce": nonce,
    "created_at": challenge["created_at"],
    "expires_at": challenge["expires_at"],
    "ttl_seconds": APPROVAL_TTL_SECONDS,
    "target_files": challenge["target_files"],
    "target_sha256": target_sha256,
    "phase": phase,
    "criteria": criteria,
    "variant": variant,
    "review_run_dir": review_run_dir,
    "providers": list(providers),
    "models": list(models),
  }


def record(cwd, nonce, source_text=None, no_source_text=False):
  """challenge nonce に対応する外部 API 送信承認 record を保存する。"""
  challenge = _load_json_object(
    challenge_path(cwd),
    "external API approval challenge",
  )
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
    raise ValueError("clock rollback を検出したため external API approval を拒否します")
  if expires_at <= now:
    raise ValueError("challenge は期限切れです")

  current_sha256 = _target_sha256(cwd, challenge.get("target_files") or [])
  if current_sha256 != challenge.get("target_sha256"):
    raise ValueError("target 内容が challenge と一致しません")

  redacted_source = None
  source_omission_reason = None
  residual_findings = []
  if no_source_text:
    source_omission_reason = "source_not_provided"
  elif source_text is None:
    raise ValueError("source text は stdin または no-store mode で指定してください")
  else:
    if not source_text.strip():
      raise ValueError("source text が空です")
    source_bytes = source_text.encode("utf-8")
    if len(source_bytes) > 4096:
      source_omission_reason = "unsafe_source_omitted"
    else:
      redacted_source, source_omission_reason, residual_findings = _redact_source(
        source_text
      )

  approval = {
    "schema_version": 1,
    "approved_action": "external_api_review",
    "approved_by": "user",
    "approved_at": _isoformat(now),
    "created_at": challenge["created_at"],
    "expires_at": challenge["expires_at"],
    "ttl_seconds": APPROVAL_TTL_SECONDS,
    "nonce": nonce,
    "challenge_path": DEFAULT_EXTERNAL_API_APPROVAL_CHALLENGE_PATH,
    "target_files": challenge["target_files"],
    "target_sha256": current_sha256,
    "phase": challenge["phase"],
    "criteria": challenge["criteria"],
    "variant": challenge["variant"],
    "review_run_dir": challenge["review_run_dir"],
    "providers": challenge["providers"],
    "models": challenge["models"],
    "attestation_type": ATTESTATION_TYPE,
    "guarantee_scope": GUARANTEE_SCOPE,
    "consumed": False,
    "invalidated": False,
  }
  if source_omission_reason is not None:
    approval["source_omission_reason"] = source_omission_reason
  if redacted_source is not None:
    approval["source_text_redacted"] = redacted_source
  if residual_findings:
    approval["redaction_findings"] = residual_findings

  _atomic_write_json(approval_path(cwd), approval)
  return {
    "status": "recorded",
    "approval_path": DEFAULT_EXTERNAL_API_APPROVAL_PATH,
    "target_files": approval["target_files"],
    "providers": approval["providers"],
    "models": approval["models"],
  }


def _as_sorted_strings(value):
  if not isinstance(value, list):
    return None
  if not all(isinstance(item, str) for item in value):
    return None
  return sorted(value)


def validate(cwd, approval, expected):
  """外部 API 送信承認 record を実行引数に対して検証する。"""
  errors = []
  if approval.get("approved_action") != "external_api_review":
    errors.append("external-api-approval approved_action が不正です")
  if approval.get("approved_by") != "user":
    errors.append("external-api-approval approved_by が user ではありません")
  if approval.get("invalidated") is True:
    errors.append("external-api-approval record は invalidated です")
  if approval.get("consumed") is True:
    errors.append("external-api-approval record は consumed です")
  if approval.get("attestation_type") != ATTESTATION_TYPE:
    errors.append("external-api-approval attestation_type が不正です")
  if approval.get("guarantee_scope") != GUARANTEE_SCOPE:
    errors.append("external-api-approval guarantee_scope が不正です")

  created_at = _parse_datetime(approval.get("created_at"))
  expires_at = _parse_datetime(approval.get("expires_at"))
  now = utc_now()
  if created_at is None or expires_at is None:
    errors.append("external-api-approval timestamp が UTC ISO-8601 ではありません")
  else:
    ttl_seconds = int((expires_at - created_at).total_seconds())
    if ttl_seconds != APPROVAL_TTL_SECONDS or approval.get("ttl_seconds") != APPROVAL_TTL_SECONDS:
      errors.append("external-api-approval TTL が 10 分ではありません")
    if created_at > now:
      errors.append("external-api-approval clock rollback を検出しました")
    if expires_at <= now:
      errors.append("external-api-approval は期限切れです")

  challenge_file = challenge_path(cwd)
  if not challenge_file.exists():
    errors.append("external-api-approval challenge がありません")
    challenge = None
  else:
    try:
      challenge = _load_json_object(challenge_file, "external API approval challenge")
    except ValueError as e:
      errors.append(str(e))
      challenge = None

  if challenge is not None:
    if challenge.get("invalidated") is True:
      errors.append("external-api-approval challenge は invalidated です")
    if challenge.get("consumed") is True:
      errors.append("external-api-approval challenge は consumed です")
    if challenge.get("nonce") != approval.get("nonce"):
      errors.append("external-api-approval nonce が challenge と一致しません")

  scalar_fields = ("phase", "criteria", "variant", "review_run_dir")
  for field in scalar_fields:
    if approval.get(field) != expected.get(field):
      errors.append(f"external-api-approval {field} が実行引数と一致しません")

  for field in ("target_files", "providers", "models"):
    if _as_sorted_strings(approval.get(field)) != _as_sorted_strings(expected.get(field)):
      errors.append(f"external-api-approval {field} が実行引数と一致しません")

  try:
    current_sha256 = _target_sha256(cwd, expected.get("target_files") or [])
  except ValueError as e:
    errors.append(str(e))
    current_sha256 = None
  if current_sha256 is not None and approval.get("target_sha256") != current_sha256:
    errors.append("external-api-approval target_sha256 が現在の対象内容と一致しません")

  return errors


def load_approval_record(path):
  return _load_json_object(Path(path), "external API approval record")
