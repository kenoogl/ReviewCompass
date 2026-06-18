"""SessionEnd フック .claude/hooks/session-record-capture.sh の単体テスト。

利用する LLM（ここでは Claude）が、利用時の会話ログを 2 層のセッション記録へ
自動取り込みする（PLC-DEC-007 候補5の going-forward 取り込み）。フックは
セッション終了時に発火し、当該セッションの jsonl を 1 件だけ取り込む。

TDD 規律（AGENTS.md 入口規律）に従い、本テストは実装前に作成する。
出力先はテスト汚染を避けるため環境変数で temp に差し替える
（RC_SESSION_EVIDENCE_DIR / RC_SESSION_DOCS_DIR）。復元経路の検証では
HOME も temp に差し替える。
実行：
  cd /Users/Daily/Development/ReviewCompass
  python3 -m unittest tests.hooks.test_session_record_capture -v
"""

import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
HOOK = REPO_ROOT / ".claude" / "hooks" / "session-record-capture.sh"


def _claude_fixture(path, objs):
  path.parent.mkdir(parents=True, exist_ok=True)
  body = "\n".join(json.dumps(o, ensure_ascii=False) for o in objs) + "\n"
  path.write_text(body, encoding="utf-8")


def _run_hook(payload, evidence_dir, docs_dir, home=None):
  env = dict(os.environ)
  env["RC_SESSION_EVIDENCE_DIR"] = str(evidence_dir)
  env["RC_SESSION_DOCS_DIR"] = str(docs_dir)
  if home is not None:
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


_SAMPLE = [
  {"type": "user", "timestamp": "2026-06-14T10:00:00.000Z",
   "message": {"role": "user", "content": "フックのテスト指示"}},
  {"type": "assistant", "timestamp": "2026-06-14T10:00:05.000Z",
   "message": {"role": "assistant", "content": [{"type": "text", "text": "了解"}]}},
]


def _assert_hook_invoked(testcase, result):
  for marker in ("No such file or directory", "command not found"):
    testcase.assertNotIn(
      marker, result.stderr,
      f"フックスクリプトが起動できていない（実装前の状態か）。stderr: {result.stderr}",
    )


class HookCaptureTests(unittest.TestCase):
  def setUp(self):
    self.tmp = Path(tempfile.mkdtemp())
    self.addCleanup(shutil.rmtree, self.tmp)
    self.evidence = self.tmp / "ev"
    self.docs = self.tmp / "dc"

  def test_capture_with_transcript_path(self):
    """transcript_path で渡された jsonl を 2 層記録へ取り込む。"""
    sess = self.tmp / "hooksess-0001.jsonl"
    _claude_fixture(sess, _SAMPLE)
    payload = {
      "hook_event_name": "SessionEnd",
      "session_id": "hooksess-0001",
      "transcript_path": str(sess),
      "cwd": str(REPO_ROOT),
      "reason": "clear",
    }
    r = _run_hook(payload, self.evidence, self.docs)
    _assert_hook_invoked(self, r)
    self.assertEqual(r.returncode, 0, f"stdout={r.stdout}\nstderr={r.stderr}")
    self.assertTrue(
      (self.evidence / "2026-06-14-claude-hooksess-0001.md").exists(),
      f"層1 が無い。stdout={r.stdout} stderr={r.stderr}",
    )
    self.assertTrue(
      (self.docs / "auto-2026-06-14-claude-hooksess-0001.md").exists(),
      f"層2 が無い。stdout={r.stdout} stderr={r.stderr}",
    )

  def test_reconstruct_path_from_session_id_and_cwd(self):
    """transcript_path が無くても session_id と cwd から jsonl を復元して取り込む。"""
    home = self.tmp / "home"
    cwd = "/Users/Daily/Development/ReviewCompass"
    enc = cwd.replace("/", "-")
    sess = home / ".claude" / "projects" / enc / "reconsess-0002.jsonl"
    _claude_fixture(sess, _SAMPLE)
    payload = {
      "hook_event_name": "SessionEnd",
      "session_id": "reconsess-0002",
      "cwd": cwd,
      "reason": "clear",
    }
    r = _run_hook(payload, self.evidence, self.docs, home=home)
    _assert_hook_invoked(self, r)
    self.assertEqual(r.returncode, 0, f"stdout={r.stdout}\nstderr={r.stderr}")
    self.assertTrue(
      (self.evidence / "2026-06-14-claude-reconsess-0002.md").exists(),
      f"復元パスから取り込めていない。stdout={r.stdout} stderr={r.stderr}",
    )

  def test_missing_transcript_exits_zero_without_records(self):
    """指定ログが存在しなくても exit 0（セッション終了を妨げない）。"""
    payload = {
      "hook_event_name": "SessionEnd",
      "session_id": "nope",
      "transcript_path": str(self.tmp / "absent.jsonl"),
      "cwd": str(REPO_ROOT),
    }
    r = _run_hook(payload, self.evidence, self.docs)
    _assert_hook_invoked(self, r)
    self.assertEqual(r.returncode, 0, f"フックは常に exit 0。stderr={r.stderr}")
    self.assertFalse(
      self.evidence.exists() and any(self.evidence.iterdir()),
      "ログが無いときに記録を書いてはいけない",
    )

  def test_no_identifiers_exits_zero(self):
    """transcript_path も session_id も無ければ何もせず exit 0。"""
    payload = {"hook_event_name": "SessionEnd", "cwd": str(REPO_ROOT)}
    r = _run_hook(payload, self.evidence, self.docs)
    _assert_hook_invoked(self, r)
    self.assertEqual(r.returncode, 0, f"stderr={r.stderr}")

  def test_auto_compact_reason_skips_capture(self):
    """reason が "auto_compact" のとき（コンテキスト圧縮中間 SessionEnd）は取り込まない。"""
    sess = self.tmp / "compact-sess-0001.jsonl"
    _claude_fixture(sess, _SAMPLE)
    payload = {
      "hook_event_name": "SessionEnd",
      "session_id": "compact-sess-0001",
      "transcript_path": str(sess),
      "cwd": str(REPO_ROOT),
      "reason": "auto_compact",
    }
    r = _run_hook(payload, self.evidence, self.docs)
    _assert_hook_invoked(self, r)
    self.assertEqual(r.returncode, 0, f"フックは常に exit 0。stderr={r.stderr}")
    self.assertFalse(
      self.evidence.exists() and any(self.evidence.iterdir()),
      "コンテキスト圧縮中間終了時に記録を書いてはいけない",
    )
    self.assertFalse(
      self.docs.exists() and any(self.docs.iterdir()),
      "コンテキスト圧縮中間終了時に記録を書いてはいけない（層2）",
    )

  def test_clear_reason_still_captures(self):
    """reason が "clear" のとき（通常終了）は取り込みを行う。（回帰テスト）"""
    sess = self.tmp / "clear-sess-0002.jsonl"
    _claude_fixture(sess, _SAMPLE)
    payload = {
      "hook_event_name": "SessionEnd",
      "session_id": "clear-sess-0002",
      "transcript_path": str(sess),
      "cwd": str(REPO_ROOT),
      "reason": "clear",
    }
    r = _run_hook(payload, self.evidence, self.docs)
    _assert_hook_invoked(self, r)
    self.assertEqual(r.returncode, 0, f"stdout={r.stdout}\nstderr={r.stderr}")
    self.assertTrue(
      (self.evidence / "2026-06-14-claude-clear-sess-0002.md").exists(),
      f"reason=clear のとき層1 を書くべき。stdout={r.stdout} stderr={r.stderr}",
    )


if __name__ == "__main__":
  unittest.main()
