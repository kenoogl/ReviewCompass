"""SessionStart フック .claude/hooks/session-record-capture-previous.sh の単体テスト。

履歴確認のため前スレッドを開いたまま新セッションを始める運用では、前セッションの
SessionEnd フックが発火せず自動記録が漏れる。これを補うため、新セッション開始時に
**現セッション以外で最新の会話ログ（＝前セッション）を 1 件だけ**単一取り込みする。

TDD 規律（AGENTS.md 入口規律）に従い、本テストは実装前に作成する。
出力先・HOME は temp に差し替えてテスト汚染を避ける。
実行：
  cd /Users/Daily/Development/ReviewCompass
  python3 -m unittest tests.hooks.test_session_record_capture_previous -v
"""

import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
HOOK = REPO_ROOT / ".claude" / "hooks" / "session-record-capture-previous.sh"

_SAMPLE = [
  {"type": "user", "timestamp": "2026-06-14T10:00:00.000Z",
   "message": {"role": "user", "content": "前セッション取り込みテスト"}},
  {"type": "assistant", "timestamp": "2026-06-14T10:00:05.000Z",
   "message": {"role": "assistant", "content": [{"type": "text", "text": "了解"}]}},
]


def _claude_fixture(path, mtime):
  path.parent.mkdir(parents=True, exist_ok=True)
  body = "\n".join(json.dumps(o, ensure_ascii=False) for o in _SAMPLE) + "\n"
  path.write_text(body, encoding="utf-8")
  os.utime(path, (mtime, mtime))


def _run_hook(payload, evidence_dir, docs_dir, home, done_dir):
  env = dict(os.environ)
  env["RC_SESSION_EVIDENCE_DIR"] = str(evidence_dir)
  env["RC_SESSION_DOCS_DIR"] = str(docs_dir)
  env["RC_SESSION_BACKFILL_DONE_DIR"] = str(done_dir)
  env["HOME"] = str(home)
  return subprocess.run(
    ["bash", str(HOOK)],
    input=json.dumps(payload),
    cwd=str(REPO_ROOT), capture_output=True, text=True,
    errors="replace", timeout=60, env=env)


def _assert_invoked(testcase, result):
  for marker in ("No such file or directory", "command not found"):
    testcase.assertNotIn(marker, result.stderr,
                         f"フック未起動（実装前か）。stderr={result.stderr}")


class CapturePreviousTests(unittest.TestCase):
  def setUp(self):
    self.tmp = Path(tempfile.mkdtemp())
    self.addCleanup(shutil.rmtree, self.tmp)
    self.evidence = self.tmp / "ev"
    self.docs = self.tmp / "dc"
    self.done = self.tmp / "done"
    self.home = self.tmp / "home"
    self.cwd = "/Users/Daily/Development/ReviewCompass"
    enc = self.cwd.replace("/", "-")
    self.proj = self.home / ".claude" / "projects" / enc

  def test_captures_previous_not_current_not_older(self):
    """前セッション（現セッション以外で最新）だけを取り込む。現セッションと
    それより古いセッションは取り込まない。"""
    _claude_fixture(self.proj / "sessC.jsonl", mtime=1000)   # 古い別セッション
    _claude_fixture(self.proj / "sessA.jsonl", mtime=2000)   # 前セッション（最新の別）
    _claude_fixture(self.proj / "sessB.jsonl", mtime=3000)   # 現セッション
    payload = {"hook_event_name": "SessionStart",
               "session_id": "sessB", "cwd": self.cwd, "source": "startup"}
    r = _run_hook(payload, self.evidence, self.docs, self.home, self.done)
    _assert_invoked(self, r)
    self.assertEqual(r.returncode, 0, f"stdout={r.stdout}\nstderr={r.stderr}")
    self.assertTrue((self.evidence / "2026-06-14-claude-sessA.md").exists(),
                    f"前セッション sessA を取り込むべき。stdout={r.stdout} stderr={r.stderr}")
    self.assertFalse((self.evidence / "2026-06-14-claude-sessB.md").exists(),
                     "現セッション sessB は取り込まない")
    self.assertFalse((self.evidence / "2026-06-14-claude-sessC.md").exists(),
                     "前より古い sessC は取り込まない（最新の別 1 件のみ）")

  def test_only_current_no_capture(self):
    """現セッションしか無ければ何も取り込まず exit 0。"""
    _claude_fixture(self.proj / "soloB.jsonl", mtime=3000)
    payload = {"hook_event_name": "SessionStart",
               "session_id": "soloB", "cwd": self.cwd, "source": "startup"}
    r = _run_hook(payload, self.evidence, self.docs, self.home, self.done)
    _assert_invoked(self, r)
    self.assertEqual(r.returncode, 0, f"stderr={r.stderr}")
    self.assertFalse(self.evidence.exists() and any(self.evidence.iterdir()),
                     "前セッションが無いときは何も書かない")

  def test_no_cwd_exits_zero(self):
    """cwd が無ければ何もせず exit 0（起動を妨げない）。"""
    payload = {"hook_event_name": "SessionStart", "session_id": "x"}
    r = _run_hook(payload, self.evidence, self.docs, self.home, self.done)
    _assert_invoked(self, r)
    self.assertEqual(r.returncode, 0, f"stderr={r.stderr}")

  def test_rebackfills_stale_record_even_when_marker_exists(self):
    """DONE_MARKER があっても source_sha256 が古ければ再取り込みして sha256 を更新する。

    Claude Code アプリはセッション終了後も last-prompt / mode 行を jsonl に追記する。
    これにより取り込み済みの md の source_sha256 が変化し、コミット前検査で
    「進行中セッション」として誤ってブロックされる。

    再発火時に sha256 が stale であれば再取り込みし、md の source_sha256 を
    最新の jsonl に合わせる。
    """
    import hashlib

    _claude_fixture(self.proj / "sessA.jsonl", mtime=2000)
    _claude_fixture(self.proj / "sessB.jsonl", mtime=3000)
    payload = {"hook_event_name": "SessionStart",
               "session_id": "sessB", "cwd": self.cwd, "source": "startup"}

    # 1回目: 初回取り込み（DONE_MARKER を作成）
    r1 = _run_hook(payload, self.evidence, self.docs, self.home, self.done)
    _assert_invoked(self, r1)
    self.assertEqual(r1.returncode, 0, f"1回目取り込み失敗。stderr={r1.stderr}")
    md_path = self.evidence / "2026-06-14-claude-sessA.md"
    self.assertTrue(md_path.exists(), "初回取り込みで md が作られるはず")

    # jsonl に Claude Code アプリ模擬のメタデータ行を追記して sha256 を変化させる
    jsonl_path = self.proj / "sessA.jsonl"
    with open(jsonl_path, "a", encoding="utf-8") as f:
      f.write(json.dumps({"type": "last-prompt", "lastPrompt": "test",
                          "sessionId": "sessA"}) + "\n")
      f.write(json.dumps({"type": "mode", "mode": "normal",
                          "sessionId": "sessA"}) + "\n")

    # sha256 が stale になっていることを確認
    stored = None
    for line in md_path.read_text(encoding="utf-8").splitlines():
      if line.startswith("source_sha256:"):
        stored = line.split(":", 1)[1].strip()
        break
    current_hash = hashlib.sha256(jsonl_path.read_bytes()).hexdigest()
    self.assertNotEqual(stored, current_hash, "前提: jsonl 追記後は sha256 が stale なはず")

    # 2回目: DONE_MARKER があるが sha256 が stale → 再取り込みすべき
    r2 = _run_hook(payload, self.evidence, self.docs, self.home, self.done)
    _assert_invoked(self, r2)
    self.assertEqual(r2.returncode, 0, f"2回目取り込み失敗。stderr={r2.stderr}")

    # md の source_sha256 が最新 jsonl のハッシュに更新されているはず
    updated_stored = None
    for line in md_path.read_text(encoding="utf-8").splitlines():
      if line.startswith("source_sha256:"):
        updated_stored = line.split(":", 1)[1].strip()
        break
    self.assertEqual(
      updated_stored,
      current_hash,
      f"再取り込み後の source_sha256 は最新 jsonl のハッシュに一致すべき。"
      f"stored={updated_stored}, current={current_hash}",
    )


if __name__ == "__main__":
  unittest.main()
