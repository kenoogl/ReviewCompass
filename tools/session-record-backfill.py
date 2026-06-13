#!/usr/bin/env python3
"""現存する会話転写から 2 層のセッション記録を一括生成する（PLC-DEC-007 候補 5）。

入力（一次ソース・ローカルのみ）:
  Claude : ~/.claude/projects/<project>/*.jsonl（プロジェクト固定・絞り込み不要）
  Codex  : ~/.codex/sessions/.../rollout-*.jsonl（cwd 前方一致で本プロジェクト分のみ）

出力（既定の置き場。PLC-DEC-007・配置規約）:
  層 1（整形済み転写）: .reviewcompass/evidence/sessions/<date>-<source>-<shortid>.md
  層 2（人が読む記録） : docs/sessions/auto-<date>-<source>-<shortid>.md

第 3 段スキャンで秘密の残存が見つかったセッションは書き込まずに飛ばし、最後に一覧する
（fail-closed）。過去分のバックフィルは現存転写のみのベストエフォート。

使い方:
  python3 tools/session-record-backfill.py            # 既定の入出力で実行
  python3 tools/session-record-backfill.py --dry-run  # 生成せず対象と件数だけ表示
"""
import argparse
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.session_record_extractor.record import extract_record, render_record
from tools.session_record_extractor.redact import find_residual_secrets, redact_text
from tools.session_record_extractor.provenance import (
  PROVENANCE_MARKER,
  file_sha256,
  verify_reproducible,
)
from tools.session_record_extractor.sources import (
  discover_claude_sessions,
  discover_codex_sessions,
  session_uid,
)
from tools.session_record_extractor.transcript import (
  parse_claude_session,
  parse_codex_session,
  render_transcript,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CLAUDE_DIR = os.path.expanduser(
  "~/.claude/projects/-Users-Daily-Development-ReviewCompass"
)
DEFAULT_CODEX_ROOT = os.path.expanduser("~/.codex/sessions")
DEFAULT_REPO_PATH = "/Users/Daily/Development/ReviewCompass"
EVIDENCE_SESSIONS = REPO_ROOT / ".reviewcompass" / "evidence" / "sessions"
DOCS_SESSIONS = REPO_ROOT / "docs" / "sessions"


def _tool_version():
  try:
    return subprocess.run(
      ["git", "rev-parse", "--short", "HEAD"],
      cwd=str(REPO_ROOT), capture_output=True, text=True,
    ).stdout.strip() or "unknown"
  except OSError:
    return "unknown"


def _process(path, source, lines, tool_version):
  if source == "codex":
    meta, events = parse_codex_session(lines)
  else:
    meta, events = {}, parse_claude_session(lines)
  record_data = extract_record(events, meta=meta)
  uid = session_uid(source, path, meta)
  date = record_data["date"] or "0000-00-00"
  label = f"{source}-{date}-{uid}"
  base_fm = {
    "generated_by": PROVENANCE_MARKER,
    "tool_version": tool_version,
    "source_kind": source,
    # 利用者名を残さないようホーム正規化した出所パス（特定は source_sha256 で行う）
    "source_path": redact_text(str(path)),
    "source_sha256": file_sha256(path),
    "redaction_rules": "builtin",
    "session_label": label,
  }
  transcript = render_transcript(
    events, meta=meta, front_matter=dict(base_fm, layer="transcript"))
  record = render_record(
    record_data, session_label=label, front_matter=dict(base_fm, layer="record"))
  findings = find_residual_secrets(transcript) + find_residual_secrets(record)
  return record_data, uid, date, transcript, record, findings


def main():
  parser = argparse.ArgumentParser(description="現存転写から 2 層記録を一括生成する")
  parser.add_argument("--claude-dir", default=DEFAULT_CLAUDE_DIR)
  parser.add_argument("--codex-root", default=DEFAULT_CODEX_ROOT)
  parser.add_argument("--repo-path", default=DEFAULT_REPO_PATH)
  parser.add_argument("--dry-run", action="store_true",
                      help="生成せず対象と件数だけ表示する")
  args = parser.parse_args()

  claude = [("claude", p) for p in discover_claude_sessions(args.claude_dir)]
  codex = [("codex", p) for p in discover_codex_sessions(args.codex_root, args.repo_path)]
  targets = claude + codex
  print(f"対象: Claude {len(claude)} 件・Codex {len(codex)} 件・計 {len(targets)} 件")

  if args.dry_run:
    return 0

  EVIDENCE_SESSIONS.mkdir(parents=True, exist_ok=True)
  DOCS_SESSIONS.mkdir(parents=True, exist_ok=True)
  tool_version = _tool_version()

  written = 0
  skipped = []
  written_files = []
  for source, path in targets:
    with open(path, encoding="utf-8", errors="replace") as f:
      lines = f.readlines()
    record_data, uid, date, transcript, record, findings = _process(
      path, source, lines, tool_version)
    if findings:
      skipped.append((Path(path).name, findings[:3]))
      continue
    base = f"{date}-{source}-{uid}"
    tpath = EVIDENCE_SESSIONS / f"{base}.md"
    rpath = DOCS_SESSIONS / f"auto-{base}.md"
    tpath.write_text(transcript, encoding="utf-8")
    rpath.write_text(record, encoding="utf-8")
    written_files += [tpath, rpath]
    written += 1

  print(f"生成: {written} 件 / 飛ばし（残存検出）: {len(skipped)} 件")
  for name, fs in skipped:
    print(f"  飛ばし: {name} :: {fs}")

  # 再現性チェック：引用元から再生成して 1 バイト一致を確認する
  src_dirs = [args.claude_dir, args.codex_root]
  counts = {"ok": 0, "mismatch": 0, "source_unavailable": 0, "no_provenance": 0}
  bad = []
  for fp in written_files:
    res = verify_reproducible(fp, src_dirs)
    counts[res["status"]] = counts.get(res["status"], 0) + 1
    if res["status"] == "mismatch":
      bad.append((fp.name, res["detail"]))
  print(f"再現性チェック: ok {counts['ok']} / mismatch {counts['mismatch']} / "
        f"source_unavailable {counts['source_unavailable']}")
  for name, detail in bad[:10]:
    print(f"  不一致: {name} :: {detail}")
  return 0


if __name__ == "__main__":
  sys.exit(main())
