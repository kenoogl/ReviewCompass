#!/bin/bash
# SessionStart フック：新セッション開始時に、前セッション（現セッション以外で最新の
# 会話ログ）を 2 層のセッション記録へ単一取り込みする。
#
# 背景：履歴確認のため前スレッドを開いたまま新セッションを始める運用では、前セッションの
#       SessionEnd フック（session-record-capture.sh）が発火せず自動記録が漏れる。
#       一括 backfill は churn（取り込み直しの差分たまり）回避のため無効化済みなので、
#       起動側で「現セッション以外で最新の 1 件」を単一取り込みして取りこぼしを補う。
#
# 設計：
#   - stdin から SessionStart の JSON ペイロード（session_id・cwd）を読む
#   - cwd から $HOME/.claude/projects/<cwd の / を - に置換> のプロジェクト dir を求める
#   - その dir の *.jsonl のうち、session_id（現セッション）以外で mtime 最新の 1 件を選ぶ
#   - 当該 jsonl を tools/session-record-backfill.py --session で取り込む（単一・安全）
#   - 進行中の現セッションは選ばない。仮に取り込んでもコミット側の歯止めが弾く
#   - 取り込み済みのセッションは .reviewcompass/runtime/session-backfill-done/ にマーカーを
#     残し、コンテキスト圧縮による SessionStart 再発火でも二重取り込みしない
#   - 取り込めない場合も含め常に exit 0（起動を妨げない）
#
# 出力先はテスト用に環境変数で差し替え可能（既定は repo の正規置き場）：
#   RC_SESSION_EVIDENCE_DIR（層1）／ RC_SESSION_DOCS_DIR（層2）
#   RC_SESSION_BACKFILL_DONE_DIR（二重取り込み防止マーカー）
#
# 依存：bash、jq、python3、tools/session-record-backfill.py

set -u

SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
REPO_ROOT=$(cd "$SCRIPT_DIR/../.." && pwd)

INPUT=$(cat)

SESSION_ID=$(printf '%s' "$INPUT" | jq -r '.session_id // empty')
CWD=$(printf '%s' "$INPUT" | jq -r '.cwd // empty')

# cwd が無ければプロジェクト dir を特定できないので通過
[ -z "$CWD" ] && exit 0

ENC=$(printf '%s' "$CWD" | sed 's#/#-#g')
PROJ="$HOME/.claude/projects/$ENC"
[ ! -d "$PROJ" ] && exit 0

DONE_DIR="${RC_SESSION_BACKFILL_DONE_DIR:-$REPO_ROOT/.reviewcompass/runtime/session-backfill-done}"
EVIDENCE_DIR="${RC_SESSION_EVIDENCE_DIR:-$REPO_ROOT/.reviewcompass/evidence/sessions}"
DOCS_DIR="${RC_SESSION_DOCS_DIR:-$REPO_ROOT/docs/sessions}"

# 現セッション以外の jsonl を全件取り込む（mtime 降順）
cd "$REPO_ROOT" || exit 0
while IFS= read -r f; do
  [ -z "$f" ] && continue
  [ ! -f "$f" ] && continue
  PREV_ID=$(basename "$f" .jsonl)
  [ "$PREV_ID" = "$SESSION_ID" ] && continue

  DONE_MARKER="$DONE_DIR/$PREV_ID"

  # 取り込み済みマーカーがある場合でも、source_sha256 が stale なら再取り込みする。
  # Claude Code はセッション終了後も jsonl に追記するため sha256 が変化する。
  if [ -f "$DONE_MARKER" ]; then
    MD_FILE=$(ls "$EVIDENCE_DIR"/*-claude-"$PREV_ID".md 2>/dev/null | head -1)
    if [ -n "$MD_FILE" ] && [ -f "$MD_FILE" ]; then
      STORED_SHA=$(grep "^source_sha256:" "$MD_FILE" 2>/dev/null | awk '{print $2}')
      if [ -n "$STORED_SHA" ]; then
        if command -v shasum >/dev/null 2>&1; then
          CURRENT_SHA=$(shasum -a 256 "$f" 2>/dev/null | awk '{print $1}')
        else
          CURRENT_SHA=$(sha256sum "$f" 2>/dev/null | awk '{print $1}')
        fi
        [ "$STORED_SHA" = "$CURRENT_SHA" ] && continue
      else
        continue
      fi
    fi
  fi

  python3 tools/session-record-backfill.py \
    --session "$f" --source claude \
    --evidence-dir "$EVIDENCE_DIR" --docs-dir "$DOCS_DIR" >/dev/null 2>&1 || true

  mkdir -p "$DONE_DIR"
  touch "$DONE_MARKER"
done < <(ls -t "$PROJ"/*.jsonl 2>/dev/null)

exit 0
