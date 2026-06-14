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
import json
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
from tools.session_record_extractor.merge import classify_update

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


def _detect_source(lines):
  """先頭の解析可能な行から claude / codex を判定する（--session の auto 用）。"""
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
  parser.add_argument("--session",
                      help="単一セッションのみ取り込む（jsonl パス）。"
                           "利用時フックからの going-forward 取り込みに使う")
  parser.add_argument("--source", choices=["auto", "claude", "codex"], default="auto",
                      help="--session のソース種別（既定 auto で自動判定）")
  parser.add_argument("--evidence-dir", default=str(EVIDENCE_SESSIONS),
                      help="層1（整形済み転写）の出力先ディレクトリ")
  parser.add_argument("--docs-dir", default=str(DOCS_SESSIONS),
                      help="層2（人が読む記録）の出力先ディレクトリ")
  parser.add_argument("--dry-run", action="store_true",
                      help="生成せず対象と件数だけ表示する")
  parser.add_argument("--historical-import", action="store_true",
                      help="一括スキャン（--session なし）を明示的に許可する。通常は使わない。"
                           "going-forward は SessionEnd フックの単一取り込み（--session）が担い、"
                           "過去ログの一括取り込みは完了済み。進行中セッションを掴み churn を生む"
                           "恐れがあるため、一度きりの過去ログ取り込み専用。")
  args = parser.parse_args()

  evidence_dir = Path(args.evidence_dir)
  docs_dir = Path(args.docs_dir)

  if args.session:
    spath = Path(args.session)
    if not spath.exists():
      print(f"エラー: 入力が存在しません: {spath}", file=sys.stderr)
      return 1
    with open(spath, encoding="utf-8", errors="replace") as f:
      head = f.readlines()
    source = args.source if args.source != "auto" else _detect_source(head)
    targets = [(source, spath)]
    # 再現性チェックは当該セッションが置かれたディレクトリを引用元として探す
    src_dirs = [str(spath.parent)]
    print(f"対象: 単一セッション 1 件（source={source}）")
  else:
    if not args.historical_import:
      print(
        "エラー: 一括 backfill（--session なし）は既定で無効です。\n"
        "  これからの会話ログ取り込みは SessionEnd フックの単一取り込み（--session）が担います。\n"
        "  過去ログの一括取り込みは完了済みです。\n"
        "  終了済みセッション 1 件を回収するときは --session <jsonl> を使ってください。\n"
        "  どうしても一括が必要なときだけ --historical-import を付けてください"
        "（進行中セッションを掴み churn を生む恐れがあります）。",
        file=sys.stderr)
      return 2
    claude = [("claude", p) for p in discover_claude_sessions(args.claude_dir)]
    codex = [("codex", p) for p in discover_codex_sessions(args.codex_root, args.repo_path)]
    targets = claude + codex
    src_dirs = [args.claude_dir, args.codex_root]
    print(f"対象: Claude {len(claude)} 件・Codex {len(codex)} 件・計 {len(targets)} 件")

  if args.dry_run:
    return 0

  evidence_dir.mkdir(parents=True, exist_ok=True)
  docs_dir.mkdir(parents=True, exist_ok=True)
  tool_version = _tool_version()

  written = 0       # 新規生成
  updated = 0       # 既存を拡張更新（増えた分を反映）
  unchanged = 0     # 既存と同一で書き込みなし
  preserved = []    # 縮小検出で保全（既存を残し上書きしない）
  skipped = []      # 残存検出で飛ばし
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
    tpath = evidence_dir / f"{base}.md"
    rpath = docs_dir / f"auto-{base}.md"
    # 追記専用マージ：既存があれば層1（転写）の包含で判定し、層1・層2を一括で
    # 書く／保全する／スキップする（消さずに足す。元ログが縮んでも既存を失わない）
    existed = tpath.exists() and rpath.exists()
    if existed:
      cls = classify_update(
        tpath.read_text(encoding="utf-8", errors="replace"), transcript)
      if cls == "same":
        unchanged += 1
        continue
      if cls == "shrink":
        preserved.append(Path(path).name)
        continue
    tpath.write_text(transcript, encoding="utf-8")
    rpath.write_text(record, encoding="utf-8")
    written_files += [tpath, rpath]
    if existed:
      updated += 1
    else:
      written += 1

  print(f"生成: {written} 件 / 更新: {updated} 件 / 更新なし: {unchanged} 件 / "
        f"保全（縮小検出）: {len(preserved)} 件 / 飛ばし（残存検出）: {len(skipped)} 件")
  for name in preserved:
    print(f"  保全（縮小検出）: {name}（既存記録を残し上書きしない）")
  for name, fs in skipped:
    print(f"  飛ばし: {name} :: {fs}")

  # 再現性チェック：引用元から再生成して 1 バイト一致を確認する
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
