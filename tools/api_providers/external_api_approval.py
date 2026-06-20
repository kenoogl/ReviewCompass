"""External API approval record validation for API/proxy runs."""
import fnmatch
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml


ALLOWED_ACTIONS = {
  "external_api_proxy_model",
  "external_api_review",
}

_SECRET_PATTERNS = [
  re.compile(r"\b(?:OPENAI|ANTHROPIC|GEMINI|GOOGLE)_[A-Z0-9_]*KEY\s*=", re.I),
  re.compile(r"\bapi[_-]?key\s*[:=]\s*\S+", re.I),
  re.compile(r"\b(?:token|password|passwd|secret)\s*[:=]\s*\S+", re.I),
  re.compile(r"\bBearer\s+[A-Za-z0-9._~+/=-]{16,}", re.I),
  re.compile(r"\bsk-[A-Za-z0-9_-]{8,}"),
  re.compile(r"\bnonce\s*[:=]\s*[A-Fa-f0-9]{16,}"),
]

_PERSONAL_IDENTIFIER_PATTERNS = [
  re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
]

_PHONE_LIKE_PATTERN = re.compile(r"\b(?:\+?\d[\d ()-]{8,}\d)\b")


def _load_yaml(path: Path) -> Dict[str, Any]:
  data = yaml.safe_load(path.read_text(encoding="utf-8"))
  return data if isinstance(data, dict) else {}


def _parse_datetime(value: Any) -> Optional[datetime]:
  if isinstance(value, datetime):
    if value.tzinfo is None:
      return None
    return value.astimezone(timezone.utc)
  if not isinstance(value, str) or not value.strip():
    return None
  try:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
  except ValueError:
    return None
  if parsed.tzinfo is None:
    return None
  return parsed.astimezone(timezone.utc)


def _list_value(record: Dict[str, Any], key: str) -> List[str]:
  value = record.get(key)
  if isinstance(value, list):
    return [str(item) for item in value]
  if isinstance(value, str):
    return [value]
  return []


def _matches_prompt_scope(prompt_path: str, patterns: List[str]) -> bool:
  return any(
    fnmatch.fnmatch(prompt_path, pattern) or fnmatch.fnmatch(Path(prompt_path).name, pattern)
    for pattern in patterns
  )


def prompt_material_findings(prompt_text: str) -> List[str]:
  """Return external-send blocking findings detected in prompt text."""
  findings = []
  for pattern in _SECRET_PATTERNS:
    if pattern.search(prompt_text):
      findings.append("prompt contains possible credential or secret material")
      break
  for pattern in _PERSONAL_IDENTIFIER_PATTERNS:
    if pattern.search(prompt_text):
      findings.append("prompt contains possible personal identifier")
      break
  else:
    for match in _PHONE_LIKE_PATTERN.finditer(prompt_text):
      digits = re.sub(r"\D", "", match.group(0))
      if len(digits) >= 10:
        findings.append("prompt contains possible personal identifier")
        break
  return findings


def validate_external_api_approval(
  approval_record_path: str,
  *,
  prompt_path: str,
  provider: str,
  model: str,
  purpose: str,
  prompt_text: Optional[str] = None,
) -> Dict[str, Any]:
  """Validate an external API approval record and return loaded record.

  Raises ValueError with a semicolon-separated reason list when validation fails.
  """
  path = Path(approval_record_path)
  record = _load_yaml(path)
  errors = []

  if record.get("schema_version") != "external-api-approval-v1":
    errors.append("schema_version must be external-api-approval-v1")
  if record.get("approved_action") not in ALLOWED_ACTIONS:
    errors.append("approved_action does not allow external API execution")
  if record.get("approved_by") != "user":
    errors.append("approved_by must be user")
  if record.get("provider") != provider:
    errors.append("provider mismatch")
  if record.get("model") != model:
    errors.append("model mismatch")
  if record.get("consumed") is True:
    errors.append("approval record is already consumed")

  expires_at = _parse_datetime(record.get("expires_at"))
  if expires_at is None:
    errors.append("expires_at must be timezone-aware ISO datetime")
  elif expires_at <= datetime.now(timezone.utc):
    errors.append("approval record is expired")

  purposes = _list_value(record, "purpose")
  if purpose not in purposes:
    errors.append("purpose is not approved")

  prompt_patterns = _list_value(record, "allowed_prompt_globs")
  if not prompt_patterns:
    errors.append("allowed_prompt_globs is required")
  elif not _matches_prompt_scope(prompt_path, prompt_patterns):
    errors.append("prompt path is not approved")

  material_policy = record.get("material_policy")
  if not isinstance(material_policy, dict):
    errors.append("material_policy is required")
    material_policy = {}
  if material_policy.get("require_secret_scan") is not True:
    errors.append("material_policy.require_secret_scan must be true")
  if material_policy.get("forbid_credentials") is not True:
    errors.append("material_policy.forbid_credentials must be true")
  if material_policy.get("forbid_personal_identifiers") is not True:
    errors.append("material_policy.forbid_personal_identifiers must be true")

  if prompt_text is not None:
    errors.extend(prompt_material_findings(prompt_text))

  if errors:
    raise ValueError("external API approval failed: " + "; ".join(errors))
  return record
