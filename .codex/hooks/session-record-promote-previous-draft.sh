#!/bin/bash
# SessionStart フック：新しい Codex セッション開始時に、現セッション以外で
# 最新の runtime 下書きを正式 2 層記録へ昇格する。
#
# 設計：
#   - SessionStart 以外では何もしない
#   - current session_id と同じ下書きは昇格しない
#   - 最新の別 session_id の下書き 1 件だけを対象にする
#   - 昇格できない場合も常に exit 0（セッション開始を妨げない）

set -u

SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
REPO_ROOT=$(cd "$SCRIPT_DIR/../.." && pwd)

INPUT=$(cat)

HOOK_EVENT_NAME=""
SESSION_ID=""
CWD=""
LOG_PATH="${RC_SESSION_PROMOTE_HOOK_LOG:-$REPO_ROOT/.reviewcompass/runtime/session-record-promote-previous-draft.jsonl}"
DRAFT_DIR="${RC_SESSION_DRAFT_DIR:-$REPO_ROOT/.reviewcompass/runtime/session-record-drafts}"
EVIDENCE_DIR="${RC_SESSION_EVIDENCE_DIR:-$REPO_ROOT/.reviewcompass/evidence/sessions}"
DOCS_DIR="${RC_SESSION_DOCS_DIR:-$REPO_ROOT/docs/sessions}"
CODEX_ROOT="${CODEX_SESSIONS_ROOT:-$HOME/.codex/sessions}"
REVIEWCOMPASS_PYTHON="${REVIEWCOMPASS_PYTHON:-python3}"
REVIEWCOMPASS_JQ="${REVIEWCOMPASS_JQ:-jq}"
PROMOTE_TOOL="${REVIEWCOMPASS_PROMOTE_TOOL:-$REPO_ROOT/tools/session-record-promote-draft.py}"

log_event() {
  local EVENT="$1"
  local TARGET_SESSION_ID="${2:-}"
  local TARGET_DRAFT="${3:-}"
  mkdir -p "$(dirname "$LOG_PATH")" 2>/dev/null || true
  EVENT="$EVENT" \
  HOOK_EVENT_NAME="$HOOK_EVENT_NAME" \
  SESSION_ID="$SESSION_ID" \
  CWD="$CWD" \
  TARGET_SESSION_ID="$TARGET_SESSION_ID" \
  TARGET_DRAFT="$TARGET_DRAFT" \
  "$REVIEWCOMPASS_PYTHON" - <<'PY' >>"$LOG_PATH" 2>/dev/null || true
import json
import os
from datetime import datetime, timezone

row = {
  "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
  "hook": "codex_session_record_promote_previous_draft",
  "hook_event_name": os.environ.get("HOOK_EVENT_NAME", ""),
  "event": os.environ.get("EVENT", ""),
  "session_id": os.environ.get("SESSION_ID", ""),
  "cwd": os.environ.get("CWD", ""),
}
target_session_id = os.environ.get("TARGET_SESSION_ID", "")
target_draft = os.environ.get("TARGET_DRAFT", "")
if target_session_id:
  row["target_session_id"] = target_session_id
if target_draft:
  row["target_draft"] = target_draft
print(json.dumps(row, ensure_ascii=False, sort_keys=True))
PY
}

if ! command -v "$REVIEWCOMPASS_JQ" >/dev/null 2>&1; then
  log_event "missing_jq"
  exit 0
fi

HOOK_EVENT_NAME=$(printf '%s' "$INPUT" | "$REVIEWCOMPASS_JQ" -r '.hook_event_name // empty')
SESSION_ID=$(printf '%s' "$INPUT" | "$REVIEWCOMPASS_JQ" -r '.session_id // empty')
CWD=$(printf '%s' "$INPUT" | "$REVIEWCOMPASS_JQ" -r '.cwd // empty')

[ "$HOOK_EVENT_NAME" != "SessionStart" ] && { log_event "ignored_event"; exit 0; }
[ -z "$SESSION_ID" ] && { log_event "no_current_session_id"; exit 0; }
[ -z "$CWD" ] && { log_event "no_cwd"; exit 0; }
[ ! -d "$DRAFT_DIR" ] && { log_event "no_draft_dir"; exit 0; }
[ ! -f "$PROMOTE_TOOL" ] && { log_event "no_promote_tool"; exit 0; }

TARGET_INFO=$(
  DRAFT_DIR="$DRAFT_DIR" SESSION_ID="$SESSION_ID" "$REVIEWCOMPASS_PYTHON" - <<'PY'
import json
import os
from pathlib import Path

draft_dir = Path(os.environ["DRAFT_DIR"])
current_id = os.environ["SESSION_ID"]

best = None
for path in draft_dir.glob("codex-*.md"):
  session_id = path.name.removeprefix("codex-").removesuffix(".md")
  if not session_id or session_id == current_id:
    continue
  try:
    mtime = path.stat().st_mtime
  except OSError:
    continue
  candidate = (mtime, session_id, path)
  if best is None or candidate > best:
    best = candidate

if best is not None:
  print(json.dumps({"session_id": best[1], "draft": str(best[2])}, ensure_ascii=False))
PY
)

[ -z "$TARGET_INFO" ] && { log_event "no_previous_draft"; exit 0; }
TARGET_SESSION_ID=$(printf '%s' "$TARGET_INFO" | "$REVIEWCOMPASS_JQ" -r '.session_id // empty')
TARGET_DRAFT=$(printf '%s' "$TARGET_INFO" | "$REVIEWCOMPASS_JQ" -r '.draft // empty')
[ -z "$TARGET_SESSION_ID" ] && { log_event "no_previous_draft"; exit 0; }

log_event "selected" "$TARGET_SESSION_ID" "$TARGET_DRAFT"

HASH_INFO=$(
  TARGET_DRAFT="$TARGET_DRAFT" \
  TARGET_SESSION_ID="$TARGET_SESSION_ID" \
  CODEX_ROOT="$CODEX_ROOT" \
  CWD="$CWD" \
  "$REVIEWCOMPASS_PYTHON" - <<'PY'
import hashlib
import json
import os
from pathlib import Path

draft = Path(os.environ["TARGET_DRAFT"])
target_session_id = os.environ["TARGET_SESSION_ID"]
root = Path(os.environ["CODEX_ROOT"])
repo = os.environ["CWD"].rstrip("/")


def read_draft_sha(path):
  try:
    text = path.read_text(encoding="utf-8", errors="replace")
  except OSError:
    return ""
  if not text.startswith("---\n"):
    return ""
  end = text.find("\n---\n", 4)
  block = text[4:end] if end != -1 else text[4:]
  for line in block.splitlines():
    if line.startswith("source_sha256:"):
      return line.split(":", 1)[1].strip().strip("'\"")
  return ""


def read_meta(path):
  try:
    with path.open(encoding="utf-8", errors="replace") as f:
      for index, line in enumerate(f):
        if index >= 5:
          break
        line = line.strip()
        if not line:
          continue
        obj = json.loads(line)
        if obj.get("type") == "session_meta":
          payload = obj.get("payload") or {}
          return payload if isinstance(payload, dict) else {}
  except (OSError, json.JSONDecodeError):
    return {}
  return {}


def find_rollout(expected_sha):
  best_match = None
  best = None
  for path in root.rglob(f"*{target_session_id}*.jsonl"):
    if not path.name.startswith("rollout-"):
      continue
    meta = read_meta(path)
    if meta.get("id") != target_session_id:
      continue
    cwd = str(meta.get("cwd") or "").rstrip("/")
    if cwd != repo and not cwd.startswith(repo + "/"):
      continue
    try:
      mtime = path.stat().st_mtime
      actual_sha = hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
      continue
    candidate = (mtime, str(path), path, actual_sha)
    if expected_sha and actual_sha == expected_sha:
      if best_match is None or candidate > best_match:
        best_match = candidate
      continue
    if best is None or candidate > best:
      best = candidate
  if best_match:
    return best_match[2], best_match[3]
  if best:
    return best[2], best[3]
  return None, ""


expected = read_draft_sha(draft)
if not expected:
  print(json.dumps({"status": "unverifiable", "reason": "missing_draft_source_sha256"}))
  raise SystemExit
rollout, actual = find_rollout(expected)
if rollout is None:
  print(json.dumps({"status": "unverifiable", "reason": "missing_rollout"}))
elif actual == expected:
  print(json.dumps({"status": "match", "rollout": str(rollout)}))
else:
  print(json.dumps({"status": "mismatch", "rollout": str(rollout)}))
PY
)

HASH_STATUS=$(printf '%s' "$HASH_INFO" | "$REVIEWCOMPASS_JQ" -r '.status // empty')
if [ "$HASH_STATUS" = "mismatch" ]; then
  log_event "previous_draft_in_progress" "$TARGET_SESSION_ID" "$TARGET_DRAFT"
  exit 0
fi
if [ "$HASH_STATUS" != "match" ]; then
  log_event "previous_draft_unverifiable" "$TARGET_SESSION_ID" "$TARGET_DRAFT"
  exit 0
fi

cd "$REPO_ROOT" || exit 0
if "$REVIEWCOMPASS_PYTHON" "$PROMOTE_TOOL" \
  --session-id "$TARGET_SESSION_ID" \
  --source codex \
  --current-session-id "$SESSION_ID" \
  --codex-root "$CODEX_ROOT" \
  --repo-path "$CWD" \
  --draft-dir "$DRAFT_DIR" \
  --evidence-dir "$EVIDENCE_DIR" \
  --docs-dir "$DOCS_DIR" >/dev/null 2>&1; then
  log_event "promoted" "$TARGET_SESSION_ID" "$TARGET_DRAFT"
else
  log_event "promote_failed" "$TARGET_SESSION_ID" "$TARGET_DRAFT"
fi

exit 0
