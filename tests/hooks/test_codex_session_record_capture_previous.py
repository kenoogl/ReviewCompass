"""Codex SessionStart フック .codex/hooks/session-record-capture-previous.sh の単体テスト。

Codex には Claude の SessionEnd 相当イベントが無いため、SessionStart 時に
**現セッション以外で最新の Codex rollout（cwd が repo に一致するもの）を 1 件だけ**
単一取り込みする。

TDD 規律（AGENTS.md 入口規律）に従い、本テストは実装前に作成する。
出力先・HOME は temp に差し替えてテスト汚染を避ける。
実行：
  cd /Users/Daily/Development/ReviewCompass
  python3 -m unittest tests.hooks.test_codex_session_record_capture_previous -v
"""

import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
HOOK = REPO_ROOT / ".codex" / "hooks" / "session-record-capture-previous.sh"


def _codex_fixture(path, session_id, cwd, text, mtime):
  path.parent.mkdir(parents=True, exist_ok=True)
  rows = [
    {
      "timestamp": "2026-06-15T10:00:00.000Z",
      "type": "session_meta",
      "payload": {
        "id": session_id,
        "timestamp": "2026-06-15T10:00:00.000Z",
        "cwd": cwd,
      },
    },
    {
      "timestamp": "2026-06-15T10:00:01.000Z",
      "type": "response_item",
      "payload": {
        "type": "message",
        "role": "user",
        "content": [{"type": "input_text", "text": text}],
      },
    },
  ]
  body = "\n".join(json.dumps(o, ensure_ascii=False) for o in rows) + "\n"
  path.write_text(body, encoding="utf-8")
  os.utime(path, (mtime, mtime))


def _run_hook(payload, evidence_dir, docs_dir, home):
  env = dict(os.environ)
  env["RC_SESSION_EVIDENCE_DIR"] = str(evidence_dir)
  env["RC_SESSION_DOCS_DIR"] = str(docs_dir)
  env["HOME"] = str(home)
  return subprocess.run(
    ["bash", str(HOOK)],
    input=json.dumps(payload),
    cwd=str(REPO_ROOT),
    capture_output=True,
    text=True,
    errors="replace",
    timeout=60,
    env=env,
  )


def _assert_invoked(testcase, result):
  for marker in ("No such file or directory", "command not found"):
    testcase.assertNotIn(
      marker, result.stderr,
      f"フック未起動（実装前か）。stderr={result.stderr}",
    )


class CodexCapturePreviousTests(unittest.TestCase):
  def setUp(self):
    self.tmp = Path(tempfile.mkdtemp())
    self.addCleanup(shutil.rmtree, self.tmp)
    self.evidence = self.tmp / "ev"
    self.docs = self.tmp / "dc"
    self.home = self.tmp / "home"
    self.cwd = "/Users/Daily/Development/ReviewCompass"
    self.sessions = self.home / ".codex" / "sessions" / "2026" / "06" / "15"

  def test_captures_latest_previous_for_same_repo_only(self):
    """現セッション以外で、同じ repo の最新 Codex rollout だけを取り込む。"""
    _codex_fixture(
      self.sessions / "rollout-2026-06-15T10-00-00-aaaaaaaa-1111-2222-3333-444444444444.jsonl",
      "aaaaaaaa-1111-2222-3333-444444444444",
      self.cwd,
      "古い Codex セッション",
      mtime=1000,
    )
    _codex_fixture(
      self.sessions / "rollout-2026-06-15T11-00-00-bbbbbbbb-1111-2222-3333-444444444444.jsonl",
      "bbbbbbbb-1111-2222-3333-444444444444",
      self.cwd,
      "前 Codex セッション",
      mtime=2000,
    )
    _codex_fixture(
      self.sessions / "rollout-2026-06-15T12-00-00-cccccccc-1111-2222-3333-444444444444.jsonl",
      "cccccccc-1111-2222-3333-444444444444",
      self.cwd,
      "現 Codex セッション",
      mtime=3000,
    )
    _codex_fixture(
      self.sessions / "rollout-2026-06-15T13-00-00-dddddddd-1111-2222-3333-444444444444.jsonl",
      "dddddddd-1111-2222-3333-444444444444",
      "/Users/Daily/Development/OtherRepo",
      "別 repo の Codex セッション",
      mtime=4000,
    )

    payload = {
      "hook_event_name": "SessionStart",
      "session_id": "cccccccc-1111-2222-3333-444444444444",
      "cwd": self.cwd,
      "source": "startup",
    }
    r = _run_hook(payload, self.evidence, self.docs, self.home)
    _assert_invoked(self, r)
    self.assertEqual(r.returncode, 0, f"stdout={r.stdout}\nstderr={r.stderr}")
    self.assertTrue(
      (self.evidence / "2026-06-15-codex-bbbbbbbb-1111-2222-3333-444444444444.md").exists(),
      f"同じ repo の前 Codex セッションを取り込むべき。stdout={r.stdout} stderr={r.stderr}",
    )
    self.assertFalse(
      (self.evidence / "2026-06-15-codex-aaaaaaaa-1111-2222-3333-444444444444.md").exists(),
      "前より古い Codex セッションは取り込まない",
    )
    self.assertFalse(
      (self.evidence / "2026-06-15-codex-cccccccc-1111-2222-3333-444444444444.md").exists(),
      "現 Codex セッションは取り込まない",
    )
    self.assertFalse(
      (self.evidence / "2026-06-15-codex-dddddddd-1111-2222-3333-444444444444.md").exists(),
      "別 repo の Codex セッションは取り込まない",
    )

  def test_only_current_no_capture(self):
    """現セッションしか無ければ何も取り込まず exit 0。"""
    _codex_fixture(
      self.sessions / "rollout-2026-06-15T12-00-00-eeeeeeee-1111-2222-3333-444444444444.jsonl",
      "eeeeeeee-1111-2222-3333-444444444444",
      self.cwd,
      "現 Codex セッションのみ",
      mtime=3000,
    )
    payload = {
      "hook_event_name": "SessionStart",
      "session_id": "eeeeeeee-1111-2222-3333-444444444444",
      "cwd": self.cwd,
    }
    r = _run_hook(payload, self.evidence, self.docs, self.home)
    _assert_invoked(self, r)
    self.assertEqual(r.returncode, 0, f"stderr={r.stderr}")
    self.assertFalse(
      self.evidence.exists() and any(self.evidence.iterdir()),
      "前セッションが無いときは何も書かない",
    )

  def test_no_cwd_exits_zero(self):
    """cwd が無ければ何もせず exit 0（起動を妨げない）。"""
    payload = {"hook_event_name": "SessionStart", "session_id": "x"}
    r = _run_hook(payload, self.evidence, self.docs, self.home)
    _assert_invoked(self, r)
    self.assertEqual(r.returncode, 0, f"stderr={r.stderr}")


if __name__ == "__main__":
  unittest.main()
