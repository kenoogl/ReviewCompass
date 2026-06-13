"""セッション記録 機械抽出ツールの単体テスト（PLC-DEC-007 候補 5）。

正本：docs/notes/2026-06-12-document-placement-stage2-decisions.md の PLC-DEC-007。
方針：会話転写を一次ソースとし、2 層（整形済み発言全文転写＋人が読む記録）を生成する。
機微除去は 3 段防御（構造縮約・パターン除去・書き込み前スキャン）。ツール結果は案 B
（先頭 20 行＋末尾 20 行・上限つき）。内部思考は除外。
"""
import json

from tools.session_record_extractor.redact import (
  redact_text,
  find_residual_secrets,
)
from tools.session_record_extractor.transcript import (
  Event,
  truncate_tool_result,
  parse_claude_session,
  parse_codex_session,
  render_transcript,
)
from tools.session_record_extractor.record import (
  extract_record,
  render_record,
)
from tools.session_record_extractor.sources import (
  codex_cwd,
  discover_codex_sessions,
)


def _jsonl(objs):
  """dict のリストを jsonl 相当の文字列行リストへ。"""
  return [json.dumps(o, ensure_ascii=False) for o in objs]


# ---------------------------------------------------------------------------
# 第 2 段：パターン除去（redact_text）
# ---------------------------------------------------------------------------


class TestRedactText:
  def test_anthropic_key_removed(self):
    text = "鍵は sk-ant-api03-AbC123def456GHI789jklMNO_pqrstuvwxyz です"
    out = redact_text(text)
    assert "sk-ant-" not in out
    assert "[除去" in out

  def test_google_api_key_removed(self):
    text = "google: AIzaSyA1234567890abcdefghijklmnopqrstuvw"
    out = redact_text(text)
    assert "AIzaSy" not in out

  def test_key_eq_value_removed(self):
    text = "ANTHROPIC_API_KEY=sk-secretvalue1234567890abcde を設定"
    out = redact_text(text)
    assert "sk-secretvalue1234567890abcde" not in out

  def test_private_key_block_removed(self):
    text = (
      "前\n-----BEGIN OPENSSH PRIVATE KEY-----\n"
      "b3BlbnNzaC1rZXktdjEAAAABG\nAAAA\n"
      "-----END OPENSSH PRIVATE KEY-----\n後"
    )
    out = redact_text(text)
    assert "BEGIN OPENSSH PRIVATE KEY" not in out
    assert "前" in out and "後" in out

  def test_home_dir_normalized(self):
    text = "/Users/keno/.claude/x と /Users/Daily/Development/ReviewCompass"
    out = redact_text(text)
    assert "/Users/keno" not in out
    assert "/Users/Daily" not in out

  def test_email_removed(self):
    text = "連絡先 kenoogl@gmail.com まで"
    out = redact_text(text)
    assert "kenoogl@gmail.com" not in out
    assert "[除去:メール]" in out

  def test_plain_text_untouched(self):
    text = "テストは 921 件 pass、回帰なし。"
    assert redact_text(text) == text

  def test_masked_key_fingerprints_removed(self):
    # 元会話で既に伏せられた指紋（先頭＋...）も公開前に消す
    text = "ANTHROPIC: sk-ant-api03...\nOPENAI: sk-proj-r2YQ...\nGEMINI: AIzaSyALNNWQ..."
    out = redact_text(text)
    assert "sk-ant-api03" not in out
    assert "sk-proj-r2YQ" not in out
    assert "AIzaSyALNNWQ" not in out

  def test_bare_github_prefix_removed(self):
    assert "ghp_" not in redact_text("token は ghp_ で始まる")

  def test_hyphenated_words_not_corrupted(self):
    # sk- を含む普通の語（risk-based 等）を壊さない
    text = "risk-based な task-list を disk-usage と合わせて確認"
    assert redact_text(text) == text

  def test_sha256_hex_preserved(self):
    # sha256（64 桁 16 進）は正当な値であり除去しない
    sha = "a" * 8 + "b" * 8 + "c" * 8 + "d" * 8 + "e" * 8 + "f" * 8 + "0" * 8 + "1" * 8
    text = f"target_sha256 は {sha} である"
    assert sha in redact_text(text)


# ---------------------------------------------------------------------------
# 第 3 段：書き込み前スキャン（find_residual_secrets / fail-closed）
# ---------------------------------------------------------------------------


class TestFindResidualSecrets:
  def test_clean_text_has_no_findings(self):
    assert find_residual_secrets("普通の文章。921 件 pass。") == []

  def test_surviving_secret_pattern_is_flagged(self):
    assert find_residual_secrets("sk-ant-api03-AbC123def456GHI789jklMNO_pqrstuvwxyz") != []

  def test_sha256_not_flagged(self):
    sha = "abcdef0123456789" * 4  # 64 桁 16 進・小文字のみ
    assert find_residual_secrets(f"sha {sha}") == []

  def test_uuid_not_flagged(self):
    assert find_residual_secrets("019e6b81-2872-77c1-87c6-4839143457b1") == []

  def test_mixed_case_high_entropy_token_flagged(self):
    # 大文字小文字＋数字混在の 50 文字（鍵らしい）→ 取りこぼしとして検出
    token = "Ab3Cd9Ef2Gh5Ij8Kl1Mn4Op7Qr0St6Uv3Wx9Yz2Ab5Cd8Ef1Gh"
    assert find_residual_secrets(f"残り {token}") != []

  def test_claude_project_dir_name_not_flagged(self):
    # ハイフン区切りの識別子（Claude プロジェクトフォルダ名）は鍵ではない
    name = "-Users-Daily-Development-ReviewCompass"
    assert find_residual_secrets(f"~/.claude/projects/{name}/x.jsonl") == []

  def test_codex_rollout_filename_not_flagged(self):
    # ハイフン区切りのファイル名（Codex rollout）は鍵ではない
    fn = "rollout-2026-06-10T18-18-12-019eb0d3-359e-7fc3-964b-4a21a64a40e3.jsonl"
    assert find_residual_secrets(fn) == []


# ---------------------------------------------------------------------------
# 第 1 段：ツール結果の縮約（案 B：先頭 20＋末尾 20 行）
# ---------------------------------------------------------------------------


class TestTruncateToolResult:
  def test_short_result_kept_whole(self):
    text = "\n".join(f"行{i}" for i in range(10))
    assert truncate_tool_result(text) == text

  def test_boundary_40_lines_kept_whole(self):
    text = "\n".join(f"行{i}" for i in range(40))
    assert truncate_tool_result(text) == text

  def test_long_result_keeps_head_and_tail(self):
    text = "\n".join(f"行{i}" for i in range(100))
    out = truncate_tool_result(text)
    assert "行0" in out and "行19" in out  # 先頭 20
    assert "行80" in out and "行99" in out  # 末尾 20
    assert "行50" not in out
    assert "中略" in out

  def test_char_cap_applied(self):
    text = "x" * 20000
    out = truncate_tool_result(text, char_cap=4000)
    assert len(out) <= 4000 + 50  # マーカー分の余裕


# ---------------------------------------------------------------------------
# Claude 転写の解析（parse_claude_session）
# ---------------------------------------------------------------------------


class TestParseClaudeSession:
  def test_user_text_strips_system_reminder(self):
    lines = _jsonl([
      {
        "type": "user",
        "timestamp": "2026-06-13T01:00:00Z",
        "message": {
          "role": "user",
          "content": "本題の指示\n<system-reminder>\n注入された文脈\n</system-reminder>",
        },
      },
    ])
    events = parse_claude_session(lines)
    assert len(events) == 1
    assert events[0].kind == "user"
    assert "本題の指示" in events[0].text
    assert "注入された文脈" not in events[0].text

  def test_assistant_text_and_tool_use_thinking_excluded(self):
    lines = _jsonl([
      {
        "type": "assistant",
        "timestamp": "2026-06-13T01:01:00Z",
        "message": {
          "role": "assistant",
          "content": [
            {"type": "thinking", "thinking": "内部の検討メモ"},
            {"type": "text", "text": "これを実行します"},
            {"type": "tool_use", "name": "Bash", "input": {"command": "git status"}},
          ],
        },
      },
    ])
    events = parse_claude_session(lines)
    kinds = [e.kind for e in events]
    assert kinds == ["assistant", "tool_call"]
    assert "これを実行します" in events[0].text
    assert "内部の検討メモ" not in events[0].text
    assert events[1].tool_name == "Bash"

  def test_tool_result_event_is_not_labeled_user(self):
    long_output = "\n".join(f"line{i}" for i in range(100))
    lines = _jsonl([
      {
        "type": "user",
        "timestamp": "2026-06-13T01:02:00Z",
        "message": {
          "role": "user",
          "content": [
            {"type": "tool_result", "content": [{"type": "text", "text": long_output}]},
          ],
        },
      },
    ])
    events = parse_claude_session(lines)
    assert len(events) == 1
    assert events[0].kind == "tool_result"
    assert "line50" not in events[0].text  # 縮約済み
    assert "line0" in events[0].text and "line99" in events[0].text

  def test_bash_command_not_exposed_in_tool_input_text_marker(self):
    # 安全な引数方針：Bash の command 全文はマーカーへ出さない
    lines = _jsonl([
      {
        "type": "assistant",
        "timestamp": "2026-06-13T01:03:00Z",
        "message": {
          "role": "assistant",
          "content": [
            {"type": "tool_use", "name": "Bash",
             "input": {"command": "export SECRET=sk-zzz; echo done"}},
          ],
        },
      },
    ])
    events = parse_claude_session(lines)
    assert events[0].kind == "tool_call"
    assert "SECRET" not in events[0].text
    # ただし record 抽出用に raw 入力は保持される
    assert events[0].tool_input.get("command", "").startswith("export SECRET")


# ---------------------------------------------------------------------------
# Codex 転写の解析（parse_codex_session）
# ---------------------------------------------------------------------------


class TestParseCodexSession:
  def test_meta_cwd_and_canonical_messages(self):
    lines = _jsonl([
      {"type": "session_meta", "timestamp": "2026-05-28T07:14:47Z",
       "payload": {"cwd": "/Users/Daily/Development/ReviewCompass"}},
      {"type": "response_item",
       "payload": {"type": "message", "role": "user",
                   "content": [{"type": "input_text", "text": "指示A"}]}},
      {"type": "event_msg",
       "payload": {"type": "user_message", "message": "指示A"}},  # 重複エコー
      {"type": "response_item",
       "payload": {"type": "message", "role": "assistant",
                   "content": [{"type": "output_text", "text": "応答A"}]}},
      {"type": "response_item",
       "payload": {"type": "reasoning", "content": [{"type": "text", "text": "思考"}]}},
    ])
    meta, events = parse_codex_session(lines)
    assert meta["cwd"] == "/Users/Daily/Development/ReviewCompass"
    kinds = [e.kind for e in events]
    # event_msg の重複エコーと reasoning は採らない
    assert kinds == ["user", "assistant"]
    assert events[0].text == "指示A"
    assert events[1].text == "応答A"

  def test_function_call_and_output(self):
    lines = _jsonl([
      {"type": "session_meta", "payload": {"cwd": "/x"}},
      {"type": "response_item",
       "payload": {"type": "function_call", "name": "shell",
                   "arguments": json.dumps({"command": ["bash", "-lc", "git status"]})}},
      {"type": "response_item",
       "payload": {"type": "function_call_output",
                   "output": "\n".join(f"l{i}" for i in range(60))}},
    ])
    _, events = parse_codex_session(lines)
    kinds = [e.kind for e in events]
    assert kinds == ["tool_call", "tool_result"]
    assert "l30" not in events[1].text  # 縮約


# ---------------------------------------------------------------------------
# 層 1：整形済み転写の描画（render_transcript）
# ---------------------------------------------------------------------------


class TestRenderTranscript:
  def test_headers_and_redaction_applied(self):
    events = [
      Event(kind="user", timestamp="2026-06-13T01:00:00Z",
            text="鍵 sk-ant-api03-AbC123def456GHI789jklMNO_pqrstuvwxyz を使う"),
      Event(kind="assistant", timestamp="2026-06-13T01:01:00Z", text="了解"),
    ]
    out = render_transcript(events)
    assert "## 利用者" in out
    assert "## アシスタント" in out
    assert "sk-ant-" not in out  # 描画時に機微除去がかかる


# ---------------------------------------------------------------------------
# 層 2：人が読む記録（extract_record / render_record）
# ---------------------------------------------------------------------------


class TestExtractRecord:
  def _sample_events(self):
    return [
      Event(kind="user", timestamp="2026-06-13T01:00:00Z", text="X を実装して"),
      Event(kind="assistant", timestamp="2026-06-13T01:01:00Z", text="実装します"),
      Event(kind="tool_call", timestamp="2026-06-13T01:02:00Z", tool_name="Edit",
            tool_input={"file_path": "tools/foo.py"}),
      Event(kind="tool_call", timestamp="2026-06-13T01:03:00Z", tool_name="Write",
            tool_input={"file_path": "tests/test_foo.py"}),
      Event(kind="tool_call", timestamp="2026-06-13T01:04:00Z", tool_name="Bash",
            tool_input={"command": 'git commit -m "foo を追加"'}),
    ]

  def test_collects_user_statements(self):
    rec = extract_record(self._sample_events())
    assert "X を実装して" in rec["user_statements"]

  def test_collects_touched_files(self):
    rec = extract_record(self._sample_events())
    assert "tools/foo.py" in rec["touched_files"]
    assert "tests/test_foo.py" in rec["touched_files"]

  def test_collects_commit_messages(self):
    rec = extract_record(self._sample_events())
    msgs = [c["message"] for c in rec["commits"]]
    assert "foo を追加" in msgs

  def test_date_range_from_timestamps(self):
    rec = extract_record(self._sample_events())
    assert rec["date"] == "2026-06-13"

  def test_render_record_has_sections(self):
    rec = extract_record(self._sample_events())
    out = render_record(rec, session_label="codex-2026-06-13")
    assert "利用者指示" in out
    assert "コミット一覧" in out
    assert "触れたファイル" in out


# ---------------------------------------------------------------------------
# 入力源の発見・Codex 絞り込み（前方一致）
# ---------------------------------------------------------------------------


class TestCodexSources:
  def _write_session(self, path, cwd):
    path.parent.mkdir(parents=True, exist_ok=True)
    obj = {"type": "session_meta", "payload": {"cwd": cwd}}
    path.write_text(json.dumps(obj, ensure_ascii=False) + "\n", encoding="utf-8")

  def test_codex_cwd_reads_meta(self, tmp_path):
    p = tmp_path / "rollout-1.jsonl"
    self._write_session(p, "/Users/Daily/Development/ReviewCompass")
    assert codex_cwd(p) == "/Users/Daily/Development/ReviewCompass"

  def test_discover_filters_by_prefix(self, tmp_path):
    repo = "/Users/Daily/Development/ReviewCompass"
    self._write_session(tmp_path / "a/rollout-a.jsonl", repo)
    self._write_session(tmp_path / "b/rollout-b.jsonl", repo + "/sub")  # 前方一致で拾う
    self._write_session(tmp_path / "c/rollout-c.jsonl", "/Users/Daily/Development/Other")
    found = discover_codex_sessions(tmp_path, repo)
    names = sorted(p.name for p in found)
    assert names == ["rollout-a.jsonl", "rollout-b.jsonl"]

  def test_broken_cwd_excluded(self, tmp_path):
    p = tmp_path / "rollout-broken.jsonl"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("壊れた行\n", encoding="utf-8")
    found = discover_codex_sessions(tmp_path, "/Users/Daily/Development/ReviewCompass")
    assert found == []
