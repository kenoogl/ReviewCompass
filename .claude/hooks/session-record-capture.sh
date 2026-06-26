#!/bin/bash
# SessionEnd フック：Claude 利用時の会話ログを 2 層のセッション記録へ自動取り込みする。
#
# 背景：PLC-DEC-007 候補5（会話転写を一次ソースとし、機械抽出でセッション記録を生成）の
#       going-forward 取り込み。利用する LLM が、利用時の自分のログを残す方針。
#       Claude を使うときは Claude のセッション終了時に当該 jsonl を 1 件だけ取り込む。
#
# 設計：
#   - stdin から SessionEnd の JSON ペイロードを読む
#   - transcript_path があればそれを使う。無ければ session_id と cwd から
#     $HOME/.claude/projects/<cwd の / を - に置換>/<session_id>.jsonl を復元する
#   - 当該 jsonl が存在すれば tools/session-record-backfill.py --session で取り込む
#     （来歴刻印・再現性チェック・機微の fail-closed はツール側が担保）
#   - 取り込めない場合も含め常に exit 0（セッション終了を妨げない）
#
# 出力先はテスト用に環境変数で差し替え可能（既定は repo の正規置き場）：
#   RC_SESSION_EVIDENCE_DIR（層1）／ RC_SESSION_DOCS_DIR（層2）
#
# 入力 JSON 例：
#   {"hook_event_name":"SessionEnd","session_id":"<id>",
#    "transcript_path":"/.../<id>.jsonl","cwd":"/path/to/repo","reason":"clear"}
#
# 依存：bash、jq、python3、tools/session-record-backfill.py

set -u

SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
REPO_ROOT=$(cd "$SCRIPT_DIR/../.." && pwd)

INPUT=$(cat)

TRANSCRIPT=$(printf '%s' "$INPUT" | jq -r '.transcript_path // empty')
SESSION_ID=$(printf '%s' "$INPUT" | jq -r '.session_id // empty')
CWD=$(printf '%s' "$INPUT" | jq -r '.cwd // empty')
REASON=$(printf '%s' "$INPUT" | jq -r '.reason // empty')

# コンテキスト圧縮由来の中間 SessionEnd はスキップする。
# 圧縮後もセッションは同一 JSONL に追記を続けるため、ここで取り込むと
# source_sha256 が後続の追記で変化し commit guard が「進行中」と誤検知する。
# reason が "clear" 以外の非空文字列 = セッションがまだ継続中と判断してスキップ。
if [ -n "$REASON" ] && [ "$REASON" != "clear" ]; then
  exit 0
fi

# transcript_path が無ければ session_id と cwd からログのパスを復元する
if [ -z "$TRANSCRIPT" ] && [ -n "$SESSION_ID" ] && [ -n "$CWD" ]; then
  ENC=$(printf '%s' "$CWD" | sed 's#/#-#g')
  TRANSCRIPT="$HOME/.claude/projects/$ENC/$SESSION_ID.jsonl"
fi

# 取り込めるログが無ければ何もせず通過（セッション終了は妨げない）
[ -z "$TRANSCRIPT" ] && exit 0
[ ! -f "$TRANSCRIPT" ] && exit 0

EVIDENCE_DIR="${RC_SESSION_EVIDENCE_DIR:-$REPO_ROOT/.reviewcompass/evidence/sessions}"
DOCS_DIR="${RC_SESSION_DOCS_DIR:-$REPO_ROOT/docs/sessions}"

cd "$REPO_ROOT" || exit 0
python3 tools/session-record-backfill.py \
  --session "$TRANSCRIPT" --source claude \
  --evidence-dir "$EVIDENCE_DIR" --docs-dir "$DOCS_DIR" >/dev/null 2>&1 || true

# セッション ID を active-sessions.json から削除する
ACTIVE_SESSIONS_PATH="$REPO_ROOT/.reviewcompass/runtime/active-sessions.json"
if [ -n "$SESSION_ID" ] && [ -f "$ACTIVE_SESSIONS_PATH" ]; then
  python3 - "$ACTIVE_SESSIONS_PATH" "$SESSION_ID" <<'PYEOF'
import json, sys, pathlib
path, sid = pathlib.Path(sys.argv[1]), sys.argv[2]
try:
  data = json.loads(path.read_text(encoding="utf-8"))
except (json.JSONDecodeError, OSError):
  data = {}
active = [x for x in data.get("active", []) if x != sid]
data["active"] = active
path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
PYEOF
fi

exit 0
