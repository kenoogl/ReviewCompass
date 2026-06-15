#!/bin/bash
# SessionStart フック：新セッション開始時に、前回の Codex セッション（現セッション以外で
# 最新の同一 repo rollout）を 2 層のセッション記録へ単一取り込みする。
#
# 背景：Codex には Claude の SessionEnd 相当イベントが無いため、SessionStart で
#       「現セッション以外の最新 1 件」を取り込む。Stop hook は turn scope のため、
#       進行中セッションを毎ターン取り込む経路にはしない。
#
# 設計：
#   - stdin から SessionStart の JSON ペイロード（session_id・cwd）を読む
#   - $HOME/.codex/sessions 配下の rollout-*.jsonl を探索する
#   - 先頭 session_meta.payload.cwd が cwd と一致または cwd 配下のものだけを対象にする
#   - session_meta.payload.id が session_id のものは現セッションとして除外する
#   - mtime 最新の 1 件だけを tools/session-record-backfill.py --session --source codex で取り込む
#   - 取り込めない場合も含め常に exit 0（起動を妨げない）
#
# 出力先はテスト用に環境変数で差し替え可能（既定は repo の正規置き場）：
#   RC_SESSION_EVIDENCE_DIR（層1）／ RC_SESSION_DOCS_DIR（層2）
#
# 依存：bash、jq、python3、tools/session-record-backfill.py

set -u

SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
REPO_ROOT=$(cd "$SCRIPT_DIR/../.." && pwd)

INPUT=$(cat)

SESSION_ID=$(printf '%s' "$INPUT" | jq -r '.session_id // empty')
CWD=$(printf '%s' "$INPUT" | jq -r '.cwd // empty')

# cwd が無ければ repo を特定できないので通過
[ -z "$CWD" ] && exit 0

CODEX_ROOT="$HOME/.codex/sessions"
[ ! -d "$CODEX_ROOT" ] && exit 0

PREV=$(
  CODEX_ROOT="$CODEX_ROOT" SESSION_ID="$SESSION_ID" CWD="$CWD" python3 - <<'PY'
import json
import os
from pathlib import Path

root = Path(os.environ["CODEX_ROOT"])
current_id = os.environ.get("SESSION_ID", "")
repo = os.environ["CWD"].rstrip("/")


def read_meta(path):
  try:
    with path.open(encoding="utf-8", errors="replace") as f:
      for i, line in enumerate(f):
        if i >= 5:
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
  cwd = str(meta.get("cwd") or "").rstrip("/")
  if not cwd:
    continue
  if cwd != repo and not cwd.startswith(repo + "/"):
    continue
  if current_id and meta.get("id") == current_id:
    continue
  try:
    mtime = path.stat().st_mtime
  except OSError:
    continue
  if best is None or mtime > best[0]:
    best = (mtime, path)

if best is not None:
  print(best[1])
PY
)

# 前セッションが無ければ通過
[ -z "$PREV" ] && exit 0
[ ! -f "$PREV" ] && exit 0

EVIDENCE_DIR="${RC_SESSION_EVIDENCE_DIR:-$REPO_ROOT/.reviewcompass/evidence/sessions}"
DOCS_DIR="${RC_SESSION_DOCS_DIR:-$REPO_ROOT/docs/sessions}"

cd "$REPO_ROOT" || exit 0
python3 tools/session-record-backfill.py \
  --session "$PREV" --source codex \
  --evidence-dir "$EVIDENCE_DIR" --docs-dir "$DOCS_DIR" >/dev/null 2>&1 || true

exit 0
