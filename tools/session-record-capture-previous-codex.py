#!/usr/bin/env python3
"""未記録の過去 Codex セッションを正式 2 層記録へ取り込む。"""

import argparse
import json
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CODEX_ROOT = Path.home() / ".codex" / "sessions"
DEFAULT_REPO_PATH = "/Users/Daily/Development/ReviewCompass"
DEFAULT_EVIDENCE_DIR = REPO_ROOT / ".reviewcompass" / "evidence" / "sessions"
DEFAULT_DOCS_DIR = REPO_ROOT / "docs" / "sessions"
BACKFILL = REPO_ROOT / "tools" / "session-record-backfill.py"


def _read_meta(path):
  try:
    with Path(path).open(encoding="utf-8", errors="replace") as f:
      for index, line in enumerate(f):
        if index >= 8:
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


def _repo_matches(cwd, repo_path):
  cwd = str(cwd or "").rstrip("/")
  repo = str(repo_path or "").rstrip("/")
  return bool(cwd and repo and (cwd == repo or cwd.startswith(repo + "/")))


def _record_texts(evidence_dir, docs_dir):
  texts = []
  for root in (Path(evidence_dir), Path(docs_dir)):
    if not root.exists():
      continue
    for path in root.rglob("*.md"):
      try:
        texts.append(path.name)
        texts.append(path.read_text(encoding="utf-8", errors="replace"))
      except OSError:
        texts.append(path.name)
  return "\n".join(texts)


def _is_recorded(session_id, record_text):
  return bool(session_id and session_id in record_text)


def _discover(codex_root, repo_path, current_session_id, record_text):
  rows = []
  root = Path(codex_root)
  if not root.exists():
    return rows
  for path in root.rglob("rollout-*.jsonl"):
    meta = _read_meta(path)
    session_id = str(meta.get("id") or "")
    if not session_id:
      continue
    if not _repo_matches(meta.get("cwd"), repo_path):
      continue
    try:
      mtime = path.stat().st_mtime
    except OSError:
      continue
    if session_id == current_session_id:
      state = "current"
    elif _is_recorded(session_id, record_text):
      state = "recorded"
    else:
      state = "unrecorded"
    rows.append({
      "mtime": mtime,
      "timestamp": meta.get("timestamp") or "",
      "session_id": session_id,
      "state": state,
      "rollout": str(path),
    })
  return sorted(rows, key=lambda row: (row["mtime"], row["rollout"]), reverse=True)


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
      _emit(_event_name(row["state"]), session_id=row["session_id"], rollout=row["rollout"])
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
    return (str(row.get("timestamp") or ""), row["mtime"], row["rollout"])

  latest_first = sorted(rows, key=key, reverse=True)
  return latest_first if limit is None else latest_first[:max(limit, 0)]


def _backfill(row, evidence_dir, docs_dir):
  return subprocess.run(
    [
      sys.executable,
      str(BACKFILL),
      "--session",
      row["rollout"],
      "--source",
      "codex",
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
    description="現在 session_id を除外し、未記録の過去 Codex セッションを取り込む",
    allow_abbrev=False,
  )
  parser.add_argument("--current-session-id", required=True,
                      help="現在実行中の Codex session_id。この session は取り込まない")
  parser.add_argument("--repo-path", default=DEFAULT_REPO_PATH,
                      help="対象リポジトリの cwd")
  parser.add_argument("--codex-root", default=str(DEFAULT_CODEX_ROOT),
                      help="Codex rollout root")
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
  record_text = _record_texts(evidence_dir, docs_dir)
  rows = _discover(args.codex_root, args.repo_path, args.current_session_id, record_text)

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
      _emit("current_session_skipped", session_id=row["session_id"], rollout=row["rollout"])
      continue
    if row["state"] == "recorded":
      _emit("already_recorded", session_id=row["session_id"], rollout=row["rollout"])
      continue
    _emit("selected", session_id=row["session_id"], rollout=row["rollout"])
    result = _backfill(row, evidence_dir, docs_dir)
    if result.returncode != 0:
      _emit(
        "capture_failed",
        session_id=row["session_id"],
        rollout=row["rollout"],
        returncode=result.returncode,
      )
      if result.stderr:
        print(result.stderr, file=sys.stderr)
      return result.returncode or 1
    _emit("captured", session_id=row["session_id"], rollout=row["rollout"])
    captured_count += 1

  _emit("no_unrecorded_previous_session")
  return 0


if __name__ == "__main__":
  sys.exit(main())
