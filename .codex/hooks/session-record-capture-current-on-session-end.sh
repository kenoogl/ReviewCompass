#!/bin/bash
# SessionEnd フック：current session_id と cwd から現 Codex セッション rollout を
# 1 件だけ選び、正式な 2 層セッション記録へ取り込む。
#
# 設計：
#   - TODO_NEXT_SESSION.md の更新はトリガーにしない
#   - SessionEnd 以外では何もしない
#   - reason が clear 以外の非空値なら中間終了として取り込まない
#   - session_id が無い場合は並行セッション誤回収を避けるため推測しない
#   - 取り込めない場合も含め常に exit 0（セッション終了を妨げない）

set -u

SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
REPO_ROOT=$(cd "$SCRIPT_DIR/../.." && pwd)

INPUT=$(cat)

HOOK_EVENT_NAME=$(printf '%s' "$INPUT" | jq -r '.hook_event_name // empty')
SESSION_ID=$(printf '%s' "$INPUT" | jq -r '.session_id // empty')
CWD=$(printf '%s' "$INPUT" | jq -r '.cwd // empty')
REASON=$(printf '%s' "$INPUT" | jq -r '.reason // empty')
LOG_PATH="${RC_SESSION_CAPTURE_HOOK_LOG:-$REPO_ROOT/.reviewcompass/runtime/session-record-capture-current-on-session-end.jsonl}"
EVIDENCE_DIR="${RC_SESSION_EVIDENCE_DIR:-$REPO_ROOT/.reviewcompass/evidence/sessions}"
DOCS_DIR="${RC_SESSION_DOCS_DIR:-$REPO_ROOT/docs/sessions}"
CODEX_ROOT="${CODEX_SESSIONS_ROOT:-$HOME/.codex/sessions}"

log_event() {
  EVENT="$1"
  SELECTED_PATH="${2:-}"
  SELECTED_SESSION_ID="${3:-}"
  mkdir -p "$(dirname "$LOG_PATH")" 2>/dev/null || true
  EVENT="$EVENT" \
  HOOK_EVENT_NAME="$HOOK_EVENT_NAME" \
  SESSION_ID="$SESSION_ID" \
  CWD="$CWD" \
  SELECTED_PATH="$SELECTED_PATH" \
  SELECTED_SESSION_ID="$SELECTED_SESSION_ID" \
  python3 - <<'PY' >>"$LOG_PATH" 2>/dev/null || true
import json
import os
from datetime import datetime, timezone

row = {
  "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
  "hook": "codex_session_record_capture_current_on_session_end",
  "hook_event_name": os.environ.get("HOOK_EVENT_NAME", ""),
  "event": os.environ.get("EVENT", ""),
  "session_id": os.environ.get("SESSION_ID", ""),
  "cwd": os.environ.get("CWD", ""),
}
selected_path = os.environ.get("SELECTED_PATH", "")
selected_session_id = os.environ.get("SELECTED_SESSION_ID", "")
if selected_path:
  row["selected_path"] = selected_path
if selected_session_id:
  row["selected_session_id"] = selected_session_id
print(json.dumps(row, ensure_ascii=False, sort_keys=True))
PY
}

[ "$HOOK_EVENT_NAME" != "SessionEnd" ] && { log_event "ignored_event"; exit 0; }
[ -n "$REASON" ] && [ "$REASON" != "clear" ] && { log_event "non_final_session_end"; exit 0; }
[ -z "$SESSION_ID" ] && { log_event "no_current_session_id"; exit 0; }
[ -z "$CWD" ] && { log_event "no_cwd"; exit 0; }
[ ! -d "$CODEX_ROOT" ] && { log_event "no_codex_root"; exit 0; }

CURRENT_INFO=$(
  CODEX_ROOT="$CODEX_ROOT" SESSION_ID="$SESSION_ID" CWD="$CWD" python3 - <<'PY'
import json
import os
from pathlib import Path

root = Path(os.environ["CODEX_ROOT"])
current_id = os.environ["SESSION_ID"]
repo = os.environ["CWD"].rstrip("/")


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


best = None
for path in root.rglob("rollout-*.jsonl"):
  meta = read_meta(path)
  if meta.get("id") != current_id:
    continue
  cwd = str(meta.get("cwd") or "").rstrip("/")
  if cwd != repo and not cwd.startswith(repo + "/"):
    continue
  try:
    mtime = path.stat().st_mtime
  except OSError:
    continue
  if best is None or mtime > best[0]:
    best = (mtime, path, str(meta.get("id") or ""))

if best is not None:
  print(json.dumps({"path": str(best[1]), "session_id": best[2]}, ensure_ascii=False))
PY
)

[ -z "$CURRENT_INFO" ] && { log_event "no_current_session"; exit 0; }
CURRENT=$(printf '%s' "$CURRENT_INFO" | jq -r '.path // empty')
CURRENT_SESSION_ID=$(printf '%s' "$CURRENT_INFO" | jq -r '.session_id // empty')
[ -z "$CURRENT" ] && { log_event "no_current_session"; exit 0; }
[ ! -f "$CURRENT" ] && { log_event "selected_missing" "$CURRENT" "$CURRENT_SESSION_ID"; exit 0; }
log_event "selected" "$CURRENT" "$CURRENT_SESSION_ID"

cd "$REPO_ROOT" || exit 0
if python3 tools/session-record-backfill.py \
  --session "$CURRENT" --source codex \
  --evidence-dir "$EVIDENCE_DIR" --docs-dir "$DOCS_DIR" >/dev/null 2>&1; then
  log_event "captured" "$CURRENT" "$CURRENT_SESSION_ID"
else
  log_event "capture_failed" "$CURRENT" "$CURRENT_SESSION_ID"
fi

exit 0
