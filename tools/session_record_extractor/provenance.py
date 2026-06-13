"""来歴（provenance）の刻印と、再現性チェック。

機械記録は独立検証ではなく「来歴の刻印＋引用元からの再生成突き合わせ」で担保する
（PLC-DEC-007 候補5・書き込み後検証ポリシー）。front-matter に出所（引用元の転写・
そのハッシュ・ツール版・機微除去ルール版）を刻み、verify_reproducible で引用元から
本文を再生成して 1 バイト一致を確認する。
"""
import hashlib
from pathlib import Path

from .record import extract_record, render_record
from .transcript import parse_claude_session, parse_codex_session, render_transcript

PROVENANCE_MARKER = "session-record-extractor"

_FM_KEYS_ORDER = [
  "generated_by", "tool_version", "layer", "source_kind",
  "source_path", "source_sha256", "redaction_rules", "session_label",
]


def render_front_matter(meta):
  """dict を YAML 風の front-matter ブロック（--- 区切り）に描画する。"""
  lines = ["---"]
  keys = [k for k in _FM_KEYS_ORDER if k in meta]
  keys += [k for k in meta if k not in _FM_KEYS_ORDER]
  for k in keys:
    lines.append(f"{k}: {meta[k]}")
  lines.append("---")
  return "\n".join(lines) + "\n"


def split_front_matter(text):
  """先頭の front-matter を (dict, body) に分ける。無ければ (None, text)。"""
  if not text.startswith("---\n"):
    return None, text
  rest = text[4:]
  end = rest.find("\n---\n")
  if end == -1:
    return None, text
  block = rest[:end]
  body = rest[end + 5:]
  meta = {}
  for line in block.split("\n"):
    if not line.strip():
      continue
    if ":" not in line:
      continue
    k, _, v = line.partition(":")
    meta[k.strip()] = v.strip()
  return meta, body


def has_provenance_marker(text):
  """機械生成記録の来歴マーカーを持つか。"""
  meta, _ = split_front_matter(text)
  return bool(meta) and meta.get("generated_by") == PROVENANCE_MARKER


def file_sha256(path):
  return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _find_source(source_sha256, source_dirs):
  """source_dirs 配下から sha256 が一致する転写を探す。"""
  for d in source_dirs:
    root = Path(d)
    if not root.exists():
      continue
    for p in root.rglob("*.jsonl"):
      try:
        if file_sha256(p) == source_sha256:
          return p
      except OSError:
        continue
  return None


def _regenerate_body(source_path, source_kind, layer, session_label):
  # 生成（backfill / CLI）と同じく改行 \n のみで分割する。splitlines() は U+2028 等の
  # Unicode 行区切りでも割れてしまい、本文にそれを含むセッションで再生成が食い違う。
  with open(source_path, encoding="utf-8", errors="replace") as f:
    lines = f.readlines()
  if source_kind == "codex":
    meta, events = parse_codex_session(lines)
  else:
    meta, events = {}, parse_claude_session(lines)
  if layer == "transcript":
    return render_transcript(events, meta=meta)
  return render_record(extract_record(events, meta=meta), session_label=session_label)


def verify_reproducible(path, source_dirs):
  """記録 path を引用元から再生成して本文一致を確認する。

  返り値の status:
    ok                : 引用元から再生成した本文と一致（再現性 OK）
    mismatch          : 来歴はあるが本文が再生成と食い違う（バグ・破損・手編集）
    source_unavailable: 引用元（sha 一致）が見つからない（消去済み等）
    no_provenance     : 来歴マーカーが無い（機械記録ではない）
  """
  text = Path(path).read_text(encoding="utf-8", errors="replace")
  meta, body = split_front_matter(text)
  if not meta or meta.get("generated_by") != PROVENANCE_MARKER:
    return {"status": "no_provenance", "detail": "来歴マーカーなし"}
  sha = meta.get("source_sha256", "")
  src = _find_source(sha, source_dirs)
  if src is None:
    return {"status": "source_unavailable", "detail": f"sha {sha[:8]} の引用元が見つからない"}
  regen = _regenerate_body(
    src, meta.get("source_kind", "claude"), meta.get("layer", "transcript"),
    meta.get("session_label"),
  )
  if regen == body:
    return {"status": "ok", "detail": str(src)}
  return {"status": "mismatch", "detail": f"再生成と不一致: {src}"}
