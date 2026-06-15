#!/usr/bin/env python3
"""Codex TODO hook 用に現セッション記録を runtime 下書きへ保存する。"""
import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.session_record_extractor.merge import classify_update
from tools.session_record_extractor.provenance import PROVENANCE_MARKER, file_sha256
from tools.session_record_extractor.redact import find_residual_secrets, redact_text
from tools.session_record_extractor.sources import session_uid
from tools.session_record_extractor.transcript import parse_claude_session, parse_codex_session, render_transcript


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DRAFT_DIR = REPO_ROOT / ".reviewcompass" / "runtime" / "session-record-drafts"


def _tool_version():
  try:
    return subprocess.run(
      ["git", "rev-parse", "--short", "HEAD"],
      cwd=str(REPO_ROOT),
      capture_output=True,
      text=True,
    ).stdout.strip() or "unknown"
  except OSError:
    return "unknown"


def _detect_source(lines):
  for line in lines:
    line = line.strip()
    if not line:
      continue
    try:
      obj = json.loads(line)
    except json.JSONDecodeError:
      continue
    if obj.get("type") in ("session_meta", "response_item", "event_msg", "turn_context"):
      return "codex"
    if obj.get("type") in ("user", "assistant", "system", "summary"):
      return "claude"
  return "claude"


def _render_draft(path, source, lines, tool_version):
  if source == "codex":
    meta, events = parse_codex_session(lines)
  else:
    meta, events = {}, parse_claude_session(lines)
  uid = session_uid(source, path, meta)
  label = f"{source}-{uid}"
  front_matter = {
    "generated_by": PROVENANCE_MARKER,
    "tool_version": tool_version,
    "layer": "draft",
    "source_kind": source,
    "source_path": redact_text(str(path)),
    "source_sha256": file_sha256(path),
    "redaction_rules": "builtin",
    "session_label": label,
  }
  return uid, render_transcript(events, meta=meta, front_matter=front_matter)


def main():
  parser = argparse.ArgumentParser(description="現セッション記録を runtime 下書きへ保存する")
  parser.add_argument("--session", required=True, help="対象 rollout/jsonl パス")
  parser.add_argument("--source", choices=["auto", "claude", "codex"], default="auto")
  parser.add_argument("--draft-dir", default=str(DEFAULT_DRAFT_DIR))
  args = parser.parse_args()

  spath = Path(args.session)
  if not spath.exists():
    print(f"エラー: 入力が存在しません: {spath}", file=sys.stderr)
    return 1

  with spath.open(encoding="utf-8", errors="replace") as f:
    lines = f.readlines()
  source = args.source if args.source != "auto" else _detect_source(lines)
  uid, draft = _render_draft(spath, source, lines, _tool_version())
  findings = find_residual_secrets(draft)
  if findings:
    print(f"エラー: 機微情報候補が残っています: {findings[:3]}", file=sys.stderr)
    return 1

  draft_dir = Path(args.draft_dir)
  draft_dir.mkdir(parents=True, exist_ok=True)
  out = draft_dir / f"{source}-{uid}.md"
  if out.exists():
    existing = out.read_text(encoding="utf-8", errors="replace")
    cls = classify_update(existing, draft)
    if cls == "same":
      if existing == draft:
        print(f"更新なし: {out}")
        return 0
    elif cls == "shrink":
      print(f"保全（縮小検出）: {out}", file=sys.stderr)
      return 0
  out.write_text(draft, encoding="utf-8")
  print(f"drafted: {out}")
  return 0


if __name__ == "__main__":
  sys.exit(main())
