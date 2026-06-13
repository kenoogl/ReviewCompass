"""会話転写の解析（第 1 段：構造縮約）と層 1（整形済み転写）の描画。

Claude（~/.claude/projects/<project>/*.jsonl）と Codex（~/.codex/sessions/.../rollout-*.jsonl）
の両形式を共通の Event 列へ正規化する。

第 1 段の方針:
  - 利用者発言・アシスタント本文のみ採る。内部思考（thinking / reasoning）は除外。
  - ツール呼び出しは「[ツール: 名前]」＋安全な引数（Bash は引数を出さない）に縮約。
    record 抽出のため raw 入力は Event.tool_input に保持する（描画には出さない）。
  - ツール結果は案 B（先頭 20 行＋末尾 20 行・上限つき）に縮約。
  - <system-reminder> など自動注入文脈は除去。
"""
import json
import re
from dataclasses import dataclass

from .redact import redact_text


@dataclass
class Event:
  kind: str  # "user" | "assistant" | "tool_call" | "tool_result"
  timestamp: str = ""
  text: str = ""
  tool_name: str = ""
  tool_input: dict = None


_SYSTEM_REMINDER = re.compile(r"<system-reminder>.*?</system-reminder>", re.DOTALL)

# 安全な引数（ファイルパス）を出してよいツール
_FILE_TOOLS = {"Edit", "Write", "Read", "NotebookEdit"}


def _normalize_newlines(text):
  """改行を \n に統一する（\r\n → \n、孤立 \r → \n）。"""
  return text.replace("\r\n", "\n").replace("\r", "\n")


def strip_system_reminders(text):
  """<system-reminder>...</system-reminder> ブロックを除去する。"""
  if not text:
    return ""
  return _SYSTEM_REMINDER.sub("", text).strip()


def truncate_tool_result(text, head=20, tail=20, keep_whole_if_le=40, char_cap=4000):
  """ツール結果を案 B（先頭 head 行＋末尾 tail 行）に縮約する。"""
  if text is None:
    return ""
  lines = text.split("\n")
  if len(lines) <= keep_whole_if_le:
    kept = text
  else:
    kept = "\n".join(lines[:head]) + "\n…（中略）…\n" + "\n".join(lines[-tail:])
  if len(kept) > char_cap:
    half = char_cap // 2
    kept = kept[:half] + "…（中略）…" + kept[-half:]
  return kept


def _tool_marker(name, tool_input):
  """ツール呼び出しの安全な 1 行マーカー。"""
  tin = tool_input or {}
  if name in _FILE_TOOLS:
    fp = tin.get("file_path") or tin.get("path") or ""
    return f"[ツール: {name}] {fp}".rstrip()
  # Bash・その他はコマンド全文を出さない（秘密混入の経路を断つ）
  return f"[ツール: {name}]"


def _tool_result_text(block):
  c = block.get("content", "")
  if isinstance(c, list):
    parts = []
    for b in c:
      if isinstance(b, dict) and b.get("type") == "text":
        parts.append(b.get("text", ""))
      elif isinstance(b, str):
        parts.append(b)
    return "\n".join(parts)
  if isinstance(c, str):
    return c
  return ""


# ---------------------------------------------------------------------------
# Claude
# ---------------------------------------------------------------------------


def parse_claude_session(lines):
  """Claude の jsonl 行列を Event 列へ正規化する。"""
  events = []
  for line in lines:
    try:
      obj = json.loads(line)
    except (json.JSONDecodeError, TypeError):
      continue
    rtype = obj.get("type")
    if rtype not in ("user", "assistant"):
      continue
    ts = obj.get("timestamp", "")
    msg = obj.get("message", {}) or {}
    role = msg.get("role")
    content = msg.get("content", "")

    if isinstance(content, str):
      txt = strip_system_reminders(content)
      if txt:
        events.append(Event(kind=role, timestamp=ts, text=txt))
      continue
    if not isinstance(content, list):
      continue

    text_parts = []

    def flush():
      if text_parts:
        t = strip_system_reminders("\n\n".join(text_parts))
        if t:
          events.append(Event(kind=role, timestamp=ts, text=t))
        text_parts.clear()

    for block in content:
      if not isinstance(block, dict):
        continue
      bt = block.get("type")
      if bt == "text":
        text_parts.append(block.get("text", ""))
      elif bt == "thinking":
        continue  # 内部思考は除外
      elif bt == "tool_use":
        flush()
        name = block.get("name", "?")
        tin = block.get("input", {}) or {}
        events.append(Event(kind="tool_call", timestamp=ts,
                            text=_tool_marker(name, tin),
                            tool_name=name, tool_input=tin))
      elif bt == "tool_result":
        flush()
        out = _tool_result_text(block)
        events.append(Event(kind="tool_result", timestamp=ts,
                            text=truncate_tool_result(out)))
    flush()
  return events


# ---------------------------------------------------------------------------
# Codex
# ---------------------------------------------------------------------------


def _codex_message_text(content):
  if isinstance(content, str):
    return content
  parts = []
  if isinstance(content, list):
    for b in content:
      if isinstance(b, dict) and b.get("type") in ("input_text", "output_text", "text"):
        parts.append(b.get("text", ""))
      elif isinstance(b, str):
        parts.append(b)
  return "\n".join(parts)


def _codex_args(args):
  if isinstance(args, dict):
    return args
  if isinstance(args, str):
    try:
      parsed = json.loads(args)
      if isinstance(parsed, dict):
        return parsed
      return {"raw": parsed}
    except json.JSONDecodeError:
      return {"raw": args}
  return {}


def parse_codex_session(lines):
  """Codex の jsonl 行列を (meta, Event 列) へ正規化する。

  response_item を正本とし、event_msg のエコーは採らない。
  """
  meta = {}
  events = []
  for line in lines:
    try:
      obj = json.loads(line)
    except (json.JSONDecodeError, TypeError):
      continue
    t = obj.get("type")
    p = obj.get("payload", {}) or {}
    if t == "session_meta":
      if isinstance(p, dict):
        meta = dict(p)
      continue
    if t != "response_item":
      continue
    ts = obj.get("timestamp", "")
    pt = p.get("type")
    if pt == "message":
      role = p.get("role")
      if role not in ("user", "assistant"):
        continue  # developer 等の注入は除外
      txt = strip_system_reminders(_codex_message_text(p.get("content", [])))
      if txt:
        events.append(Event(kind=role, timestamp=ts, text=txt))
    elif pt == "reasoning":
      continue  # 内部思考は除外
    elif pt in ("function_call", "custom_tool_call"):
      name = p.get("name", "?")
      args = p.get("arguments", None)
      if args is None:
        args = p.get("input", "")
      events.append(Event(kind="tool_call", timestamp=ts,
                          text=f"[ツール: {name}]",
                          tool_name=name, tool_input=_codex_args(args)))
    elif pt in ("function_call_output", "custom_tool_call_output"):
      out = p.get("output", "")
      if isinstance(out, dict):
        out = out.get("content") or json.dumps(out, ensure_ascii=False)
      if not isinstance(out, str):
        out = str(out)
      events.append(Event(kind="tool_result", timestamp=ts,
                          text=truncate_tool_result(out)))
  return meta, events


# ---------------------------------------------------------------------------
# 層 1：整形済み転写の描画
# ---------------------------------------------------------------------------


_LABELS = {
  "user": "利用者",
  "assistant": "アシスタント",
  "tool_call": "ツール",
  "tool_result": "ツール結果",
}


def render_transcript(events, meta=None, rules=None, front_matter=None):
  """Event 列を整形済み Markdown 転写へ描画する（機微除去を適用）。

  front_matter を渡すと先頭に来歴ブロックを付す（本文は付さない場合と同一＝決定論）。
  """
  prefix = ""
  if front_matter:
    from .provenance import render_front_matter
    prefix = render_front_matter(front_matter)
  out = []
  if meta:
    out.append("<!-- session meta -->")
    for k in ("cwd", "id"):
      if meta.get(k):
        out.append(f"<!-- {k}: {redact_text(str(meta[k]), rules)} -->")
    out.append("")
  for e in events:
    label = _LABELS.get(e.kind, e.kind)
    body = redact_text(e.text or "", rules)
    header = f"## {label}（{e.timestamp}）" if e.timestamp else f"## {label}"
    out.append(header)
    out.append("")
    out.append(body)
    out.append("")
  # テキスト文書として改行を \n に統一する（CR が混じると書き戻し時に正規化され
  # 再生成と食い違うため。決定論・再現性のために必須）
  return _normalize_newlines(prefix + "\n".join(out).rstrip() + "\n")
