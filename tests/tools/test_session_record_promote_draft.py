"""tools/session-record-promote-draft.py の単体テスト。

Codex TODO hook が runtime 下書きへ保存した現セッション記録は、後続セッションで
終了済みになってから正式 2 層記録へ昇格する。current session_id と同じ対象は
進行中なので拒否する。
"""

import json
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
PROMOTE = REPO_ROOT / "tools" / "session-record-promote-draft.py"


def _codex_fixture(path, session_id, cwd, text):
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
  path.write_text(
    "\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n",
    encoding="utf-8",
  )


def _run_promote(*args):
  return subprocess.run(
    [str(PROMOTE), *args],
    cwd=str(REPO_ROOT),
    capture_output=True,
    text=True,
    errors="replace",
    timeout=60,
  )


class SessionRecordPromoteDraftTests(unittest.TestCase):
  def setUp(self):
    self.tmpdir = tempfile.TemporaryDirectory()
    self.addCleanup(self.tmpdir.cleanup)
    self.tmp = Path(self.tmpdir.name)
    self.repo = self.tmp / "repo"
    self.repo.mkdir()
    self.codex_root = self.tmp / "codex"
    self.evidence = self.tmp / "evidence"
    self.docs = self.tmp / "docs"
    self.drafts = self.tmp / "drafts"
    self.session_id = "aaaaaaaa-1111-2222-3333-444444444444"
    self.rollout = (
      self.codex_root
      / "2026"
      / "06"
      / "15"
      / "rollout-2026-06-15T10-00-00-aaaaaaaa-1111-2222-3333-444444444444.jsonl"
    )
    _codex_fixture(self.rollout, self.session_id, str(self.repo), "昇格対象セッション")

  def _base_args(self):
    return [
      "--session-id", self.session_id,
      "--source", "codex",
      "--codex-root", str(self.codex_root),
      "--repo-path", str(self.repo),
      "--evidence-dir", str(self.evidence),
      "--docs-dir", str(self.docs),
      "--draft-dir", str(self.drafts),
    ]

  def test_rejects_current_session_id(self):
    """現在実行中の session_id と同じ対象は正式昇格しない。"""
    result = _run_promote(*self._base_args(), "--current-session-id", self.session_id)

    self.assertEqual(result.returncode, 2, result.stderr)
    self.assertIn("current session", result.stderr)
    self.assertFalse(self.evidence.exists() and any(self.evidence.iterdir()))
    self.assertFalse(self.docs.exists() and any(self.docs.iterdir()))

  def test_promotes_ended_session_from_rollout(self):
    """終了済み session_id は元 rollout から正式 2 層記録へ昇格できる。"""
    result = _run_promote(
      *self._base_args(),
      "--current-session-id", "bbbbbbbb-1111-2222-3333-444444444444",
    )

    self.assertEqual(result.returncode, 0, result.stderr)
    self.assertTrue(
      (self.evidence / "2026-06-15-codex-aaaaaaaa-1111-2222-3333-444444444444.md").exists()
    )
    self.assertTrue(
      (self.docs / "auto-2026-06-15-codex-aaaaaaaa-1111-2222-3333-444444444444.md").exists()
    )


if __name__ == "__main__":
  unittest.main()
