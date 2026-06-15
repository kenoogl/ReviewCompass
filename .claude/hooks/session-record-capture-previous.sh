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

EVIDENCE_DIR="${RC_SESSION_EVIDENCE_DIR:-$REPO_ROOT/.reviewcompass/evidence/sessions}"
DOCS_DIR="${RC_SESSION_DOCS_DIR:-$REPO_ROOT/docs/sessions}"

cd "$REPO_ROOT" || exit 0
python3 tools/session-record-backfill.py \
  --session "$PREV" --source claude \
  --evidence-dir "$EVIDENCE_DIR" --docs-dir "$DOCS_DIR" >/dev/null 2>&1 || true

exit 0
