#!/usr/bin/env python3
"""
Claude Code のセッション記録（jsonl 形式）を読みやすい Markdown に変換する。

Claude Code は ~/.claude/projects/<project>/<session-uuid>.jsonl にセッション全体を
自動保存する。本スクリプトはその jsonl を解析し、利用者と Claude の発言を
時系列に並べた Markdown を出力する。

使い方:
    python3 tools/session-log-converter.py <input.jsonl> <output.md>

または最新セッションを自動選択:
    python3 tools/session-log-converter.py --latest <project-dir> <output.md>

たとえば:
    python3 tools/session-log-converter.py --latest \\
        ~/.claude/projects/-Users-Daily-Development-Rwiki-v2-code-mod \\
        docs/sessions/session-18-2026-05-22.md

出力内容:
- 利用者発言と Claude 発言（テキストブロックのみ）
- 内部思考（thinking ブロック）は除外
- ツール呼び出しは「[ツール呼び出し: 道具名]」の 1 行に短縮
- ツール結果は省略
- system-reminder 由来の自動注入文は除去
"""

import argparse
import json
import sys
from pathlib import Path


def extract_text_content(content):
    """メッセージの content（文字列または content block の配列）からテキストを取り出す。"""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for block in content:
            if not isinstance(block, dict):
                continue
            btype = block.get("type")
            if btype == "text":
                parts.append(block.get("text", ""))
            elif btype == "tool_use":
                name = block.get("name", "?")
                parts.append(f"[ツール呼び出し: {name}]")
            elif btype == "tool_result":
                parts.append("[ツール結果省略]")
            # thinking ブロックは出力しない
        return "\n\n".join(parts).strip()
    return ""


def strip_system_reminders(text):
    """<system-reminder>...</system-reminder> ブロックを除去する。"""
    lines = text.split("\n")
    cleaned = []
    skip = False
    for ln in lines:
        if "<system-reminder>" in ln:
            skip = True
            continue
        if "</system-reminder>" in ln:
            skip = False
            continue
        if not skip:
            cleaned.append(ln)
    return "\n".join(cleaned).strip()


def convert_jsonl_to_markdown(input_path, output_path):
    out_lines = []
    out_lines.append("# セッション記録")
    out_lines.append("")
    out_lines.append(f"_自動変換元: {input_path}_")
    out_lines.append("")

    turn_count = 0
    with open(input_path) as f:
        for line in f:
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue

            rtype = obj.get("type")
            if rtype not in ("user", "assistant"):
                continue

            msg = obj.get("message", {})
            role = msg.get("role")
            content = msg.get("content", "")
            text = extract_text_content(content)

            if not text:
                continue

            text = strip_system_reminders(text)
            if not text:
                continue

            timestamp = obj.get("timestamp", "")
            label = "利用者" if role == "user" else "Claude"

            out_lines.append(f"## {label}（{timestamp}）")
            out_lines.append("")
            out_lines.append(text)
            out_lines.append("")

            turn_count += 1

    with open(output_path, "w") as f:
        f.write("\n".join(out_lines))

    return turn_count


def main():
    parser = argparse.ArgumentParser(
        description="Claude Code セッション記録を Markdown に変換する"
    )
    parser.add_argument(
        "input",
        help="入力 jsonl ファイル、または --latest 指定時はプロジェクトディレクトリ",
    )
    parser.add_argument("output", help="出力 Markdown ファイル")
    parser.add_argument(
        "--latest",
        action="store_true",
        help="input をプロジェクトディレクトリと見なし、最新の jsonl を変換対象とする",
    )
    args = parser.parse_args()

    if args.latest:
        project_dir = Path(args.input)
        if not project_dir.exists():
            print(f"エラー: ディレクトリが存在しません: {project_dir}", file=sys.stderr)
            sys.exit(1)
        jsonl_files = sorted(
            project_dir.glob("*.jsonl"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )
        if not jsonl_files:
            print(
                f"エラー: jsonl ファイルが見つかりません: {project_dir}",
                file=sys.stderr,
            )
            sys.exit(1)
        input_path = jsonl_files[0]
    else:
        input_path = Path(args.input)
        if not input_path.exists():
            print(f"エラー: ファイルが存在しません: {input_path}", file=sys.stderr)
            sys.exit(1)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    n = convert_jsonl_to_markdown(input_path, output_path)
    print(f"変換完了: {n} ターン → {output_path}")


if __name__ == "__main__":
    main()
