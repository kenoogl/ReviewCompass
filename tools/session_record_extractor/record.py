"""層 2：人が読むセッション記録の抽出と描画。

抽出するのは「日付・利用者発言の列挙・コミット一覧・触れたファイル」までに限る。
「決定」は機械が推測しない（LLM による決定の捏造は PLC-DEC-007 の誤記録で踏んだ失敗
であり、再発を避ける）。決定欄は人が後から注記する空欄として用意する。
"""
import re

from .redact import redact_text


# git commit -m "..." / '...' / 素のトークン からメッセージを取り出す
_COMMIT_MSG = re.compile(r"-m\s+(?:\"([^\"]*)\"|'([^']*)'|(\S+))")

# 変更（書き込み）を伴うツール。Read は「見た」であり「触れた」に含めない
_WRITE_TOOLS = {"Edit", "Write", "NotebookEdit"}


def _command_of(tool_input):
  c = (tool_input or {}).get("command")
  if isinstance(c, str):
    return c
  if isinstance(c, list):
    return " ".join(str(x) for x in c)
  return ""


def extract_record(events, meta=None):
  """Event 列から層 2 の素材を抽出する。"""
  user_statements = []
  touched = set()
  commits = []
  dates = []

  for e in events:
    if e.timestamp:
      dates.append(e.timestamp[:10])
    if e.kind == "user" and e.text:
      user_statements.append(e.text)
    elif e.kind == "tool_call":
      tin = e.tool_input or {}
      if e.tool_name in _WRITE_TOOLS:
        fp = tin.get("file_path") or tin.get("path")
        if fp:
          touched.add(fp)
      cmd = _command_of(tin)
      if cmd and ("git commit" in cmd or "guarded-git-commit" in cmd):
        m = _COMMIT_MSG.search(cmd)
        if m:
          msg = m.group(1) or m.group(2) or m.group(3) or ""
        else:
          msg = ""
        commits.append({"message": msg})

  sdates = sorted(d for d in dates if d)
  return {
    "date": sdates[0] if sdates else "",
    "date_range": (sdates[0], sdates[-1]) if sdates else ("", ""),
    "user_statements": user_statements,
    "commits": commits,
    "touched_files": sorted(touched),
  }


def _first_line(text):
  lines = (text or "").splitlines()
  return lines[0] if lines else ""


def render_record(record, session_label=None, rules=None, front_matter=None):
  """層 2 の素材を Markdown へ描画する（機微除去を適用）。

  front_matter を渡すと先頭に来歴ブロックを付す（本文は付さない場合と同一＝決定論）。
  """
  prefix = ""
  if front_matter:
    from .provenance import render_front_matter
    prefix = render_front_matter(front_matter)
  out = []
  out.append(f"# セッション記録（{record.get('date', '')}）")
  if session_label:
    out.append("")
    out.append(f"_セッション: {session_label}_")
  out.append("")

  out.append("## 利用者指示（発言の列挙）")
  out.append("")
  statements = record.get("user_statements", [])
  if statements:
    for s in statements:
      out.append(f"- {redact_text(_first_line(s), rules)}")
  else:
    out.append("（なし）")
  out.append("")

  out.append("## 決定")
  out.append("")
  out.append("（機械抽出では決定を推測しない。利用者発言と突き合わせて人が注記する）")
  out.append("")

  out.append("## コミット一覧")
  out.append("")
  commits = record.get("commits", [])
  if commits:
    for c in commits:
      out.append(f"- {redact_text(c.get('message', ''), rules)}")
  else:
    out.append("（なし）")
  out.append("")

  out.append("## 触れたファイル")
  out.append("")
  touched = record.get("touched_files", [])
  if touched:
    for f in touched:
      out.append(f"- {redact_text(f, rules)}")
  else:
    out.append("（なし）")
  out.append("")

  from .transcript import _normalize_newlines
  return _normalize_newlines(prefix + "\n".join(out).rstrip() + "\n")
