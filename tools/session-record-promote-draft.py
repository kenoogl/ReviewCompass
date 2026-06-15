#!/usr/bin/env python3
"""runtime 下書きまたは元 rollout から終了済み Codex セッションを正式記録へ昇格する。"""
import argparse
import json
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CODEX_ROOT = Path.home() / ".codex" / "sessions"
DEFAULT_REPO_PATH = "/Users/Daily/Development/ReviewCompass"
DEFAULT_DRAFT_DIR = REPO_ROOT / ".reviewcompass" / "runtime" / "session-record-drafts"
DEFAULT_EVIDENCE_DIR = REPO_ROOT / ".reviewcompass" / "evidence" / "sessions"
DEFAULT_DOCS_DIR = REPO_ROOT / "docs" / "sessions"


def _read_meta(path):
  try:
    with Path(path).open(encoding="utf-8", errors="replace") as f:
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


def _find_codex_rollout(codex_root, session_id, repo_path):
  root = Path(codex_root)
  repo = str(repo_path).rstrip("/")
  best = None
  for path in root.rglob("rollout-*.jsonl"):
    meta = _read_meta(path)
    if meta.get("id") != session_id:
      continue
    cwd = str(meta.get("cwd") or "").rstrip("/")
    if cwd != repo and not cwd.startswith(repo + "/"):
      continue
    try:
      mtime = path.stat().st_mtime
    except OSError:
      continue
    if best is None or mtime > best[0]:
      best = (mtime, path)
  return best[1] if best else None


def main():
  parser = argparse.ArgumentParser(description="終了済みセッション下書きを正式記録へ昇格する")
  parser.add_argument("--session-id", required=True)
  parser.add_argument("--source", choices=["codex"], default="codex")
  parser.add_argument("--current-session-id", default="")
  parser.add_argument("--codex-root", default=str(DEFAULT_CODEX_ROOT))
  parser.add_argument("--repo-path", default=DEFAULT_REPO_PATH)
  parser.add_argument("--draft-dir", default=str(DEFAULT_DRAFT_DIR))
  parser.add_argument("--evidence-dir", default=str(DEFAULT_EVIDENCE_DIR))
  parser.add_argument("--docs-dir", default=str(DEFAULT_DOCS_DIR))
  args = parser.parse_args()

  if not args.current_session_id:
    print("エラー: current session id を確認できないため昇格しません", file=sys.stderr)
    return 2
  if args.session_id == args.current_session_id:
    print("エラー: current session はまだ進行中のため正式昇格しません", file=sys.stderr)
    return 2

  rollout = _find_codex_rollout(args.codex_root, args.session_id, args.repo_path)
  if rollout is None:
    draft = Path(args.draft_dir) / f"codex-{args.session_id}.md"
    hint = f" draft={draft}" if draft.exists() else ""
    print(f"エラー: 対象 rollout が見つかりません: {args.session_id}{hint}", file=sys.stderr)
    return 1

  result = subprocess.run(
    [
      sys.executable,
      str(REPO_ROOT / "tools" / "session-record-backfill.py"),
      "--session",
      str(rollout),
      "--source",
      args.source,
      "--evidence-dir",
      args.evidence_dir,
      "--docs-dir",
      args.docs_dir,
    ],
    cwd=str(REPO_ROOT),
    capture_output=True,
    text=True,
    errors="replace",
  )
  if result.stdout:
    print(result.stdout, end="")
  if result.stderr:
    print(result.stderr, end="", file=sys.stderr)
  return result.returncode


if __name__ == "__main__":
  sys.exit(main())
