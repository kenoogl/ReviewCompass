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

# 現セッション以外で mtime 最新の jsonl を 1 件選ぶ（＝前セッション）
PREV=""
while IFS= read -r f; do
  [ -z "$f" ] && continue
  base=$(basename "$f" .jsonl)
  [ "$base" = "$SESSION_ID" ] && continue
  PREV="$f"
  break
done < <(ls -t "$PROJ"/*.jsonl 2>/dev/null)

# 前セッションが無ければ通過
[ -z "$PREV" ] && exit 0
[ ! -f "$PREV" ] && exit 0

PREV_ID=$(basename "$PREV" .jsonl)
DONE_DIR="${RC_SESSION_BACKFILL_DONE_DIR:-$REPO_ROOT/.reviewcompass/runtime/session-backfill-done}"
DONE_MARKER="$DONE_DIR/$PREV_ID"

EVIDENCE_DIR="${RC_SESSION_EVIDENCE_DIR:-$REPO_ROOT/.reviewcompass/evidence/sessions}"
DOCS_DIR="${RC_SESSION_DOCS_DIR:-$REPO_ROOT/docs/sessions}"

# 取り込み済みマーカーがある場合でも、source_sha256 が現在の jsonl と一致しなければ再取り込みする。
# Claude Code アプリはセッション終了後も last-prompt / mode 行を jsonl に追記するため、
# 初回取り込み後に sha256 が変化し、コミット前検査で「進行中セッション」と誤判定される。
if [ -f "$DONE_MARKER" ]; then
  # 対応する md ファイルを探す（層1 の evidence ディレクトリ）
  MD_FILE=$(ls "$EVIDENCE_DIR"/*-claude-"$PREV_ID".md 2>/dev/null | head -1)
  if [ -n "$MD_FILE" ] && [ -f "$MD_FILE" ]; then
    STORED_SHA=$(grep "^source_sha256:" "$MD_FILE" 2>/dev/null | awk '{print $2}')
    if [ -n "$STORED_SHA" ]; then
      if command -v shasum >/dev/null 2>&1; then
        CURRENT_SHA=$(shasum -a 256 "$PREV" 2>/dev/null | awk '{print $1}')
      else
        CURRENT_SHA=$(sha256sum "$PREV" 2>/dev/null | awk '{print $1}')
      fi
      # sha256 が一致していれば再取り込み不要
      [ "$STORED_SHA" = "$CURRENT_SHA" ] && exit 0
      # 不一致（stale）の場合は再取り込みへ続く
    else
      # sha256 が読めない場合は安全のためスキップ
      exit 0
    fi
  else
    # md がない（取り込み済みでない）場合は通常取り込みへ続く
    :
  fi
fi

cd "$REPO_ROOT" || exit 0
python3 tools/session-record-backfill.py \
  --session "$PREV" --source claude \
  --evidence-dir "$EVIDENCE_DIR" --docs-dir "$DOCS_DIR" >/dev/null 2>&1 || true

# 取り込み完了マーカーを記録
mkdir -p "$DONE_DIR"
touch "$DONE_MARKER"

exit 0
