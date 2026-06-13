"""セッション記録 機械抽出ツールの CLI（コマンド）テスト。

書き込み前スキャン（第 3 段）の fail-closed と、2 層出力の生成を検証する。
"""
import json
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "tools" / "session-record-extractor.py"


def _run(args, cwd=None):
  return subprocess.run(
    [sys.executable, str(SCRIPT)] + [str(a) for a in args],
    cwd=str(cwd or REPO_ROOT),
    capture_output=True,
    text=True,
  )


def _write_jsonl(path, objs):
  path.write_text(
    "\n".join(json.dumps(o, ensure_ascii=False) for o in objs) + "\n",
    encoding="utf-8",
  )


def _clean_claude_session(path):
  _write_jsonl(path, [
    {"type": "user", "timestamp": "2026-06-13T01:00:00Z",
     "message": {"role": "user", "content": "X を実装して"}},
    {"type": "assistant", "timestamp": "2026-06-13T01:01:00Z",
     "message": {"role": "assistant", "content": [
       {"type": "text", "text": "実装します"},
       {"type": "tool_use", "name": "Edit", "input": {"file_path": "tools/foo.py"}},
       {"type": "tool_use", "name": "Bash",
        "input": {"command": 'git commit -m "foo を追加"'}},
     ]}},
  ])


def test_writes_two_layers_on_clean_session(tmp_path):
  src = tmp_path / "session.jsonl"
  _clean_claude_session(src)
  tout = tmp_path / "out" / "transcript.md"
  rout = tmp_path / "out" / "record.md"
  res = _run([src, "--transcript-out", tout, "--record-out", rout, "--label", "s-test"])
  assert res.returncode == 0, res.stderr
  assert tout.exists() and rout.exists()
  t = tout.read_text(encoding="utf-8")
  r = rout.read_text(encoding="utf-8")
  assert "## 利用者" in t and "## アシスタント" in t
  assert "コミット一覧" in r and "触れたファイル" in r
  assert "foo を追加" in r


def test_fail_closed_when_residual_secret(tmp_path):
  src = tmp_path / "session.jsonl"
  token = "Ab3Cd9Ef2Gh5Ij8Kl1Mn4Op7Qr0St6Uv3Wx9Yz2Ab5Cd8Ef1Gh"  # 鍵らしい残存候補
  _write_jsonl(src, [
    {"type": "user", "timestamp": "2026-06-13T01:00:00Z",
     "message": {"role": "user", "content": f"値は {token} です"}},
  ])
  tout = tmp_path / "transcript.md"
  rout = tmp_path / "record.md"
  res = _run([src, "--transcript-out", tout, "--record-out", rout])
  assert res.returncode != 0
  assert not tout.exists() and not rout.exists()
  assert "残存" in res.stderr or "高エントロピー" in res.stderr


def test_allow_residual_overrides_fail_closed(tmp_path):
  src = tmp_path / "session.jsonl"
  token = "Ab3Cd9Ef2Gh5Ij8Kl1Mn4Op7Qr0St6Uv3Wx9Yz2Ab5Cd8Ef1Gh"
  _write_jsonl(src, [
    {"type": "user", "timestamp": "2026-06-13T01:00:00Z",
     "message": {"role": "user", "content": f"値は {token} です"}},
  ])
  tout = tmp_path / "transcript.md"
  res = _run([src, "--transcript-out", tout, "--allow-residual"])
  assert res.returncode == 0, res.stderr
  assert tout.exists()


def test_codex_source_autodetected(tmp_path):
  src = tmp_path / "rollout-x.jsonl"
  _write_jsonl(src, [
    {"type": "session_meta", "timestamp": "2026-05-28T07:14:47Z",
     "payload": {"cwd": "/Users/Daily/Development/ReviewCompass",
                 "id": "019e6b81-2872-77c1-87c6-4839143457b1"}},
    {"type": "response_item",
     "payload": {"type": "message", "role": "user",
                 "content": [{"type": "input_text", "text": "指示A"}]}},
    {"type": "response_item",
     "payload": {"type": "message", "role": "assistant",
                 "content": [{"type": "output_text", "text": "応答A"}]}},
  ])
  tout = tmp_path / "transcript.md"
  res = _run([src, "--transcript-out", tout])
  assert res.returncode == 0, res.stderr
  t = tout.read_text(encoding="utf-8")
  assert "指示A" in t and "応答A" in t
