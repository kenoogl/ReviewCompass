#!/usr/bin/env python3
"""セッション記録 機械抽出ツール（PLC-DEC-007 候補 5）の CLI。

会話転写（Claude / Codex の jsonl）を一次ソースとして、2 層の出力を生成する。

  層 1（--transcript-out）：整形・機微除去済みの発言全文転写
  層 2（--record-out）   ：人が読むセッション記録（日付・利用者指示・コミット・触れたファイル）

機微除去は 3 段防御。書き込み前スキャン（第 3 段）で秘密の残存が見つかった場合は、
既定では書き込まずに停止する（fail-closed）。意図的に上書きする場合のみ --allow-residual。

使い方:
  python3 tools/session-record-extractor.py <input.jsonl> \\
      [--source {auto,claude,codex}] \\
      [--transcript-out PATH] [--record-out PATH] \\
      [--label LABEL] [--rules PATH] [--allow-residual]
"""
import argparse
import json
import sys
from pathlib import Path

# スクリプト実行時もパッケージを tools.* で import できるようリポジトリルートを通す
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.session_record_extractor.record import extract_record, render_record
from tools.session_record_extractor.redact import find_residual_secrets, load_rules
from tools.session_record_extractor.transcript import (
  parse_claude_session,
  parse_codex_session,
  render_transcript,
)


def detect_source(lines):
  """先頭の解析可能な行から claude / codex を判定する。"""
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


def main():
  parser = argparse.ArgumentParser(
    description="会話転写から 2 層のセッション記録を機械抽出する"
  )
  parser.add_argument("input", help="入力 jsonl ファイル")
  parser.add_argument("--source", choices=["auto", "claude", "codex"], default="auto")
  parser.add_argument("--transcript-out", help="層 1（整形済み転写）の出力先")
  parser.add_argument("--record-out", help="層 2（人が読む記録）の出力先")
  parser.add_argument("--label", help="出力に付すセッション名")
  parser.add_argument("--rules", help="機微除去ルール yaml（任意。既定規則へ重ねる）")
  parser.add_argument("--allow-residual", action="store_true",
                      help="第 3 段スキャンで残存があっても書き込む（既定は停止）")
  args = parser.parse_args()

  input_path = Path(args.input)
  if not input_path.exists():
    print(f"エラー: 入力が存在しません: {input_path}", file=sys.stderr)
    return 1

  rules = load_rules(args.rules) if args.rules else None

  with input_path.open(encoding="utf-8", errors="replace") as f:
    lines = f.readlines()

  source = args.source
  if source == "auto":
    source = detect_source(lines)

  if source == "codex":
    meta, events = parse_codex_session(lines)
  else:
    meta, events = {}, parse_claude_session(lines)

  label = args.label or input_path.stem

  transcript = render_transcript(events, meta=meta, rules=rules)
  record_data = extract_record(events, meta=meta)
  record = render_record(record_data, session_label=label, rules=rules)

  # 第 3 段：書き込み前スキャン（fail-closed）
  findings = find_residual_secrets(transcript, rules) + find_residual_secrets(record, rules)
  if findings and not args.allow_residual:
    print(f"中止: 機微の残存候補が {len(findings)} 件見つかったため書き込みません "
          f"（--allow-residual で上書き可）:", file=sys.stderr)
    for f in findings[:20]:
      print(f"  - {f}", file=sys.stderr)
    return 2

  wrote = []
  if args.transcript_out:
    p = Path(args.transcript_out)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(transcript, encoding="utf-8")
    wrote.append(str(p))
  if args.record_out:
    p = Path(args.record_out)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(record, encoding="utf-8")
    wrote.append(str(p))

  print(f"source={source} events={len(events)} "
        f"commits={len(record_data['commits'])} "
        f"touched={len(record_data['touched_files'])} "
        f"residual={len(findings)}")
  if wrote:
    print("書き込み: " + ", ".join(wrote))
  else:
    print("（出力先未指定のため書き込みなし。--transcript-out / --record-out を指定）")
  return 0


if __name__ == "__main__":
  sys.exit(main())
