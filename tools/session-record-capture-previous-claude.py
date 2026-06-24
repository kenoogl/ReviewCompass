#!/usr/bin/env python3
"""未記録の過去 Claude セッションを正式 2 層記録へ取り込む手動 CLI。

Codex 版 tools/session-record-capture-previous-codex.py の Claude 対応版。記録生成は
共通の tools/session-record-backfill.py --source claude へ委譲し、本ツールは Claude の
プロジェクトログ発見・状態判定（現在 / 記録済み / 未記録）・一覧・選択取り込みだけを担う。

Claude のログは $HOME/.claude/projects/<cwd の / を - に置換>/<session_id>.jsonl に
プロジェクトごとに分かれて置かれるため、Codex のような cwd 前方一致の絞り込みは不要で、
ファイル名 stem がそのまま session_id になる。Claude はサブエージェント会話を別 jsonl に
しない（本体 jsonl 内の sidechain 行として残す）ため、Codex のような派生セッション除外は
不要で、現在セッションをファイル名一致で除外すれば足りる。

使い方:
  python3 tools/session-record-capture-previous-claude.py \
    --current-session-id <現在の Claude session_id> \
    --repo-path /path/to/repo

確認だけなら --list を付ける（既定は全件、日時降順）。直近 N 件は --recent N、
機械処理用 JSONL は --format jsonl。記録はせず状態だけ見るなら --dry-run。
手動回収の既定上限は 5 件で、--max-count で変えられる。
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REPO_PATH = "/Users/Daily/Development/ReviewCompass"
DEFAULT_EVIDENCE_DIR = REPO_ROOT / ".reviewcompass" / "evidence" / "sessions"
DEFAULT_DOCS_DIR = REPO_ROOT / "docs" / "sessions"
BACKFILL = REPO_ROOT / "tools" / "session-record-backfill.py"
SESSION_ID_RE = re.compile(
  r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"
)


def _project_dir_from_repo(repo_path):
  """repo の cwd から Claude プロジェクト dir を求める（hook と同じ / → - 置換）。"""
  enc = str(repo_path or "").replace("/", "-")
  return Path.home() / ".claude" / "projects" / enc


def _first_timestamp(path):
  """転写先頭付近から最初の timestamp を読む（一覧の並び・表示用）。"""
  try:
    with Path(path).open(encoding="utf-8", errors="replace") as f:
      for index, line in enumerate(f):
        if index >= 8:
          break
        line = line.strip()
        if not line:
          continue
        try:
          obj = json.loads(line)
        except json.JSONDecodeError:
          continue
        ts = obj.get("timestamp")
        if ts:
          return str(ts)
  except OSError:
    return ""
  return ""


def _record_session_ids_from_path(path):
  """記録ファイルの来歴行とファイル名から session_id を取る（本文言及は拾わない）。"""
  session_ids = set(SESSION_ID_RE.findall(path.name))
  try:
    with Path(path).open(encoding="utf-8", errors="replace") as f:
      for index, line in enumerate(f):
        if index >= 32:
          break
        stripped = line.strip()
        if stripped.startswith(("session_label:", "source_path:", "<!-- id:")):
          session_ids.update(SESSION_ID_RE.findall(stripped))
  except OSError:
    pass
  return session_ids


def _recorded_session_ids(evidence_dir, docs_dir):
  """層1・層2 の両方に正式記録がある session_id だけを記録済みとみなす。"""
  ids_by_layer = []
  for root in (Path(evidence_dir), Path(docs_dir)):
    layer_ids = set()
    if not root.exists():
      ids_by_layer.append(layer_ids)
      continue
    for path in root.rglob("*.md"):
      layer_ids.update(_record_session_ids_from_path(path))
    ids_by_layer.append(layer_ids)
  return ids_by_layer[0] & ids_by_layer[1]


def _is_recorded(session_id, recorded_session_ids):
  return bool(session_id and session_id in recorded_session_ids)


def _discover(project_dir, current_session_id, recorded_session_ids):
  """プロジェクト dir 直下の <session_id>.jsonl を発見し、状態を付ける。"""
  rows = []
  root = Path(project_dir)
  if not root.exists():
    return rows
  for path in root.glob("*.jsonl"):
    session_id = path.stem
    if not session_id:
      continue
    try:
      mtime = path.stat().st_mtime
    except OSError:
      continue
    if session_id == current_session_id:
      state = "current"
    elif _is_recorded(session_id, recorded_session_ids):
      state = "recorded"
    else:
      state = "unrecorded"
    rows.append({
      "mtime": mtime,
      "timestamp": _first_timestamp(path),
      "session_id": session_id,
      "state": state,
      "session_path": str(path),
    })
  return sorted(rows, key=lambda row: (row["mtime"], row["session_path"]), reverse=True)


def _emit(event, **fields):
  row = {"event": event}
  row.update(fields)
  print(json.dumps(row, ensure_ascii=False, sort_keys=True))


def _status_label(state):
  return {
    "current": "現在",
    "recorded": "記録済み",
    "unrecorded": "未記録",
  }.get(state, state)


def _event_name(state):
  return {
    "current": "current_session",
    "recorded": "already_recorded",
    "unrecorded": "would_capture",
  }.get(state, state)


def _short_session_id(session_id):
  if len(session_id) <= 13:
    return session_id
  return f"{session_id[:8]}...{session_id[-4:]}"


def _display_timestamp(row):
  timestamp = str(row.get("timestamp") or "")
  if timestamp:
    return timestamp.replace("T", " ").replace("Z", "")
  return "-"


def _emit_list(rows, output_format):
  if output_format == "jsonl":
    for row in rows:
      _emit(
        _event_name(row["state"]),
        session_id=row["session_id"],
        session_path=row["session_path"],
      )
    return

  print("日時 | 短縮ID | 状態")
  for row in rows:
    print(
      f"{_display_timestamp(row)} | "
      f"{_short_session_id(row['session_id'])} | "
      f"{_status_label(row['state'])}"
    )


def _list_rows(rows, limit):
  def key(row):
    return (str(row.get("timestamp") or ""), row["mtime"], row["session_path"])

  latest_first = sorted(rows, key=key, reverse=True)
  return latest_first if limit is None else latest_first[:max(limit, 0)]


def _backfill(row, evidence_dir, docs_dir):
  return subprocess.run(
    [
      sys.executable,
      str(BACKFILL),
      "--session",
      row["session_path"],
      "--source",
      "claude",
      "--evidence-dir",
      str(evidence_dir),
      "--docs-dir",
      str(docs_dir),
    ],
    cwd=str(REPO_ROOT),
    capture_output=True,
    text=True,
    errors="replace",
    timeout=120,
  )


def main():
  parser = argparse.ArgumentParser(
    description="現在 session_id を除外し、未記録の過去 Claude セッションを取り込む",
    allow_abbrev=False,
  )
  parser.add_argument("--current-session-id", required=True,
                      help="現在実行中の Claude session_id。この session は取り込まない")
  parser.add_argument("--repo-path", default=DEFAULT_REPO_PATH,
                      help="対象リポジトリの cwd（Claude プロジェクト dir の算出に使う）")
  parser.add_argument("--claude-project-dir", default=None,
                      help="Claude プロジェクト dir を直接指定（既定は --repo-path から算出）")
  parser.add_argument("--evidence-dir", default=str(DEFAULT_EVIDENCE_DIR),
                      help="層1（整形済み転写）の出力先")
  parser.add_argument("--docs-dir", default=str(DEFAULT_DOCS_DIR),
                      help="層2（人間向け記録）の出力先")
  parser.add_argument("--dry-run", action="store_true",
                      help="状態を表示するだけで記録しない")
  parser.add_argument("--list", action="store_true",
                      help="確認用に対象セッションと記録状態を表示する。既定は全件")
  parser.add_argument("--format", choices=["table", "jsonl"], default="table",
                      help="--list / --dry-run の表示形式（既定 table）")
  parser.add_argument("--recent", type=int,
                      help="--list / --dry-run の表示を直近 N 件に制限する")
  parser.add_argument("--max-count", type=int, default=5,
                      help="記録する未記録過去セッションの上限（既定 5）")
  parser.add_argument("--list-limit", type=int,
                      help="互換用。--recent と同じく表示を直近 N 件に制限する")
  args = parser.parse_args()

  evidence_dir = Path(args.evidence_dir)
  docs_dir = Path(args.docs_dir)
  if args.claude_project_dir:
    project_dir = Path(args.claude_project_dir)
  else:
    project_dir = _project_dir_from_repo(args.repo_path)
  recorded_session_ids = _recorded_session_ids(evidence_dir, docs_dir)
  rows = _discover(project_dir, args.current_session_id, recorded_session_ids)

  if args.list or args.dry_run:
    limit = args.recent if args.recent is not None else args.list_limit
    listed_rows = _list_rows(rows, limit)
    _emit_list(listed_rows, args.format)
    return 0

  captured_count = 0
  max_count = max(args.max_count, 0)
  for row in rows:
    if captured_count >= max_count:
      _emit("max_count_reached", max_count=max_count)
      return 0
    if row["state"] == "current":
      _emit("current_session_skipped", session_id=row["session_id"], session_path=row["session_path"])
      continue
    if row["state"] == "recorded":
      _emit("already_recorded", session_id=row["session_id"], session_path=row["session_path"])
      continue
    _emit("selected", session_id=row["session_id"], session_path=row["session_path"])
    result = _backfill(row, evidence_dir, docs_dir)
    if result.returncode != 0:
      _emit(
        "capture_failed",
        session_id=row["session_id"],
        session_path=row["session_path"],
        returncode=result.returncode,
      )
      if result.stderr:
        print(result.stderr, file=sys.stderr)
      return result.returncode or 1
    _emit("captured", session_id=row["session_id"], session_path=row["session_path"])
    captured_count += 1

  _emit("no_unrecorded_previous_session")
  return 0


if __name__ == "__main__":
  sys.exit(main())
