"""来歴刻印・再現性チェック・決定論のテスト（PLC-DEC-007 候補5・書き込み後検証ポリシー）。

機械記録は独立検証ではなく「来歴の刻印＋引用元からの再生成突き合わせ（再現性）」で担保する。
"""
import hashlib
import json

from tools.session_record_extractor.provenance import (
  PROVENANCE_MARKER,
  render_front_matter,
  split_front_matter,
  has_provenance_marker,
  verify_reproducible,
)
from tools.session_record_extractor.transcript import (
  parse_claude_session,
  render_transcript,
)
from tools.session_record_extractor.record import extract_record, render_record


def _jsonl(objs):
  return [json.dumps(o, ensure_ascii=False) for o in objs]


def _sample_claude():
  return _jsonl([
    {"type": "user", "timestamp": "2026-06-13T01:00:00Z",
     "message": {"role": "user", "content": "X を実装して"}},
    {"type": "assistant", "timestamp": "2026-06-13T01:01:00Z",
     "message": {"role": "assistant", "content": [
       {"type": "text", "text": "実装します"},
       {"type": "tool_use", "name": "Edit", "input": {"file_path": "tools/foo.py"}},
     ]}},
  ])


class TestFrontMatter:
  def test_render_and_split_roundtrip(self):
    fm = {"generated_by": PROVENANCE_MARKER, "tool_version": "abc1234",
          "source_sha256": "deadbeef", "layer": "transcript"}
    text = render_front_matter(fm) + "本文ここ\n"
    parsed, body = split_front_matter(text)
    assert parsed["generated_by"] == PROVENANCE_MARKER
    assert parsed["tool_version"] == "abc1234"
    assert body == "本文ここ\n"

  def test_has_marker_true_and_false(self):
    fm = {"generated_by": PROVENANCE_MARKER}
    assert has_provenance_marker(render_front_matter(fm) + "x")
    assert not has_provenance_marker("---\ngenerated_by: 別物\n---\nx")
    assert not has_provenance_marker("front-matter なしの普通の文書")

  def test_split_returns_none_when_no_front_matter(self):
    parsed, body = split_front_matter("front-matter なし\n本文")
    assert parsed is None
    assert body == "front-matter なし\n本文"


class TestRenderersEmitFrontMatter:
  def test_transcript_emits_front_matter(self):
    events = parse_claude_session(_sample_claude())
    fm = {"generated_by": PROVENANCE_MARKER, "layer": "transcript"}
    out = render_transcript(events, front_matter=fm)
    assert out.startswith("---\n")
    assert "generated_by: session-record-extractor" in out

  def test_record_emits_front_matter(self):
    events = parse_claude_session(_sample_claude())
    rec = extract_record(events)
    fm = {"generated_by": PROVENANCE_MARKER, "layer": "record"}
    out = render_record(rec, session_label="s-1", front_matter=fm)
    assert out.startswith("---\n")
    assert "## 利用者指示" in out


class TestDeterminism:
  def test_transcript_body_is_identical_on_reruns(self):
    a = render_transcript(parse_claude_session(_sample_claude()))
    b = render_transcript(parse_claude_session(_sample_claude()))
    assert a == b

  def test_record_body_is_identical_on_reruns(self):
    a = render_record(extract_record(parse_claude_session(_sample_claude())), session_label="s")
    b = render_record(extract_record(parse_claude_session(_sample_claude())), session_label="s")
    assert a == b


class TestVerifyReproducible:
  def _write_source(self, tmp_path):
    src = tmp_path / "src.jsonl"
    src.write_text("\n".join(_sample_claude()) + "\n", encoding="utf-8")
    return src

  def _make_generated(self, src, layer="transcript", tamper=False, bad_sha=False):
    raw = src.read_bytes()
    sha = hashlib.sha256(raw).hexdigest()
    lines = raw.decode().splitlines()
    events = parse_claude_session(lines)
    fm = {
      "generated_by": PROVENANCE_MARKER, "tool_version": "test",
      "layer": layer, "source_kind": "claude",
      "source_path": str(src),
      "source_sha256": "0" * 64 if bad_sha else sha,
      "session_label": "s-1",
    }
    if layer == "transcript":
      body = render_transcript(events)
    else:
      body = render_record(extract_record(events), session_label="s-1")
    if tamper:
      body = body + "\n改ざん追記\n"
    return render_front_matter(fm) + body

  def test_ok_when_body_matches_source(self, tmp_path):
    src = self._write_source(tmp_path)
    f = tmp_path / "gen.md"
    f.write_text(self._make_generated(src), encoding="utf-8")
    res = verify_reproducible(f, [tmp_path])
    assert res["status"] == "ok"

  def test_mismatch_when_body_tampered(self, tmp_path):
    src = self._write_source(tmp_path)
    f = tmp_path / "gen.md"
    f.write_text(self._make_generated(src, tamper=True), encoding="utf-8")
    res = verify_reproducible(f, [tmp_path])
    assert res["status"] == "mismatch"

  def test_source_unavailable_when_no_matching_sha(self, tmp_path):
    src = self._write_source(tmp_path)
    f = tmp_path / "gen.md"
    f.write_text(self._make_generated(src, bad_sha=True), encoding="utf-8")
    res = verify_reproducible(f, [tmp_path])
    assert res["status"] == "source_unavailable"

  def test_record_layer_roundtrip_ok(self, tmp_path):
    src = self._write_source(tmp_path)
    f = tmp_path / "rec.md"
    f.write_text(self._make_generated(src, layer="record"), encoding="utf-8")
    res = verify_reproducible(f, [tmp_path])
    assert res["status"] == "ok"

  def test_carriage_return_in_output_is_reproducible(self, tmp_path):
    # コマンド出力由来の CRLF（\r\n）が本文に入ると、書き込み→読み戻しで \r が
    # 正規化されて消え、再生成と食い違う回帰。出力を \n 改行に統一して防ぐ。
    import hashlib
    src = tmp_path / "cr.jsonl"
    obj = {"type": "user", "timestamp": "2026-06-13T01:00:00Z",
           "message": {"role": "user", "content": [
             {"type": "tool_result", "content": [
               {"type": "text", "text": "line1\r\nPermission denied (publickey).\r\n"}]}]}}
    src.write_text(json.dumps(obj, ensure_ascii=False) + "\n", encoding="utf-8")
    with open(src, encoding="utf-8", errors="replace") as fh:
      lines = fh.readlines()
    events = parse_claude_session(lines)
    sha = hashlib.sha256(src.read_bytes()).hexdigest()
    fm = {
      "generated_by": PROVENANCE_MARKER, "tool_version": "t", "layer": "transcript",
      "source_kind": "claude", "source_path": str(src), "source_sha256": sha,
      "session_label": "s",
    }
    f = tmp_path / "gen.md"
    f.write_text(render_front_matter(fm) + render_transcript(events), encoding="utf-8")
    assert verify_reproducible(f, [tmp_path])["status"] == "ok"

  def test_unicode_line_separator_is_reproducible(self, tmp_path):
    # 本文に U+2028（行区切り）が混ざると readlines と splitlines が食い違う回帰。
    # 生成は backfill と同じ readlines、検証も同一の行分割でなければ再現性が崩れる。
    import hashlib
    src = tmp_path / "u.jsonl"
    obj = {"type": "user", "timestamp": "2026-06-13T01:00:00Z",
           "message": {"role": "user", "content": "前 後の指示"}}
    src.write_text(json.dumps(obj, ensure_ascii=False) + "\n", encoding="utf-8")
    with open(src, encoding="utf-8", errors="replace") as fh:
      lines = fh.readlines()
    events = parse_claude_session(lines)
    sha = hashlib.sha256(src.read_bytes()).hexdigest()
    fm = {
      "generated_by": PROVENANCE_MARKER, "tool_version": "t", "layer": "transcript",
      "source_kind": "claude", "source_path": str(src), "source_sha256": sha,
      "session_label": "s",
    }
    f = tmp_path / "gen.md"
    f.write_text(render_front_matter(fm) + render_transcript(events), encoding="utf-8")
    assert verify_reproducible(f, [tmp_path])["status"] == "ok"
