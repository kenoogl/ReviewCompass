#!/bin/bash
# SessionStart フック：現在 session_id を除外し、未記録の過去 Codex rollout を
# 1 件だけ正式な 2 層セッション記録へ取り込む。

set -u

SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
REPO_ROOT=$(cd "$SCRIPT_DIR/../.." && pwd)

INPUT=$(cat)

HOOK_EVENT_NAME=""
SESSION_ID=""
CWD=""
LOG_PATH="${RC_SESSION_CAPTURE_PREVIOUS_HOOK_LOG:-$REPO_ROOT/.reviewcompass/runtime/session-record-capture-previous-codex.jsonl}"
EVIDENCE_DIR="${RC_SESSION_EVIDENCE_DIR:-$REPO_ROOT/.reviewcompass/evidence/sessions}"
DOCS_DIR="${RC_SESSION_DOCS_DIR:-$REPO_ROOT/docs/sessions}"
CODEX_ROOT="${CODEX_SESSIONS_ROOT:-$HOME/.codex/sessions}"
REVIEWCOMPASS_PYTHON="${REVIEWCOMPASS_PYTHON:-python3}"
REVIEWCOMPASS_JQ="${REVIEWCOMPASS_JQ:-jq}"
CAPTURE_TOOL="${REVIEWCOMPASS_CAPTURE_PREVIOUS_CODEX_TOOL:-$REPO_ROOT/tools/session-record-capture-previous-codex.py}"

log_event() {
  local EVENT="$1"
  mkdir -p "$(dirname "$LOG_PATH")" 2>/dev/null || true
  EVENT="$EVENT" \
  HOOK_EVENT_NAME="$HOOK_EVENT_NAME" \
  SESSION_ID="$SESSION_ID" \
  CWD="$CWD" \
  "$REVIEWCOMPASS_PYTHON" - <<'PY' >>"$LOG_PATH" 2>/dev/null || true
import json
import os
from datetime import datetime, timezone

print(json.dumps({
  "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
  "hook": "codex_session_record_capture_previous",
  "hook_event_name": os.environ.get("HOOK_EVENT_NAME", ""),
  "event": os.environ.get("EVENT", ""),
  "session_id": os.environ.get("SESSION_ID", ""),
  "cwd": os.environ.get("CWD", ""),
}, ensure_ascii=False, sort_keys=True))
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
[ ! -f "$CAPTURE_TOOL" ] && { log_event "no_capture_tool"; exit 0; }

cd "$REPO_ROOT" || exit 0
if "$REVIEWCOMPASS_PYTHON" "$CAPTURE_TOOL" \
  --current-session-id "$SESSION_ID" \
  --repo-path "$CWD" \
  --codex-root "$CODEX_ROOT" \
  --evidence-dir "$EVIDENCE_DIR" \
  --docs-dir "$DOCS_DIR" \
  --max-count 1 >>"$LOG_PATH" 2>&1; then
  log_event "capture_checked"
else
  log_event "capture_failed"
fi

exit 0
