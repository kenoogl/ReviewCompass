"""tools/session-record-backfill.py の単一セッション取り込み（--session）の単体テスト。

PLC-DEC-007 候補5の going-forward 取り込み（利用する LLM が、利用時の会話ログを
自分で残す）を支える部品。SessionEnd フックが 1 セッション分だけ取り込むために使う。

TDD 規律（AGENTS.md 入口規律）に従い、本テストは実装前に作成する。
実行：
  cd /Users/Daily/Development/ReviewCompass
  python3 -m unittest tests.tools.test_session_record_single_capture -v
"""

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
BACKFILL = REPO_ROOT / "tools" / "session-record-backfill.py"


def _write_claude_fixture(path, objs):
  """Claude jsonl 形式の最小フィクスチャを書く。"""
  path.parent.mkdir(parents=True, exist_ok=True)
  body = "\n".join(json.dumps(o, ensure_ascii=False) for o in objs) + "\n"
  path.write_text(body, encoding="utf-8")


def _write_codex_fixture(path, session_id, cwd, text, parent_session_id=None):
  path.parent.mkdir(parents=True, exist_ok=True)
  payload = {
    "id": session_id,
    "timestamp": "2026-06-14T10:00:00.000Z",
    "cwd": cwd,
  }
  if parent_session_id:
    payload["session_id"] = parent_session_id
  rows = [
    {
      "timestamp": "2026-06-14T10:00:00.000Z",
      "type": "session_meta",
      "payload": payload,
    },
    {
      "timestamp": "2026-06-14T10:00:01.000Z",
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


def _run_session(session_path, evidence_dir, docs_dir, source="claude", extra=None):
  cmd = [
      sys.executable, str(BACKFILL),
      "--session", str(session_path),
      "--source", source,
      "--evidence-dir", str(evidence_dir),
      "--docs-dir", str(docs_dir),
    ]
  if extra:
    cmd += extra
  return subprocess.run(
    cmd,
    cwd=str(REPO_ROOT),
    capture_output=True,
    text=True,
    errors="replace",
    timeout=60,
  )


_SAMPLE = [
  {"type": "user", "timestamp": "2026-06-14T10:00:00.000Z",
   "message": {"role": "user", "content": "テスト指示です"}},
  {"type": "assistant", "timestamp": "2026-06-14T10:00:05.000Z",
   "message": {"role": "assistant", "content": [{"type": "text", "text": "了解しました"}]}},
]


class SingleSessionCaptureTests(unittest.TestCase):
  def setUp(self):
    self.tmp = Path(tempfile.mkdtemp())
    self.addCleanup(shutil.rmtree, self.tmp)
    self.evidence = self.tmp / "evidence"
    self.docs = self.tmp / "docs"

  def test_writes_two_layers_with_provenance(self):
    """単一セッションから層1・層2を、来歴刻印つきで指定ディレクトリへ書く。"""
    sess = self.tmp / "testsess-0001.jsonl"
    _write_claude_fixture(sess, _SAMPLE)
    r = _run_session(sess, self.evidence, self.docs)
    self.assertEqual(r.returncode, 0, f"stdout={r.stdout}\nstderr={r.stderr}")
    tpath = self.evidence / "2026-06-14-claude-testsess-0001.md"
    rpath = self.docs / "auto-2026-06-14-claude-testsess-0001.md"
    self.assertTrue(tpath.exists(), f"層1 が無い。stdout={r.stdout}")
    self.assertTrue(rpath.exists(), f"層2 が無い。stdout={r.stdout}")
    self.assertIn(
      "generated_by: session-record-extractor", tpath.read_text(encoding="utf-8"),
      "層1 に来歴マーカーが必要",
    )
    self.assertIn(
      "テスト指示です", rpath.read_text(encoding="utf-8"),
      "層2 に利用者発言が必要",
    )

  def test_reproducible_ok(self):
    """書いた記録は引用元から再生成して 1 バイト一致する（再現性 ok）。"""
    sess = self.tmp / "testsess-0002.jsonl"
    _write_claude_fixture(sess, [
      {"type": "user", "timestamp": "2026-06-14T11:00:00.000Z",
       "message": {"role": "user", "content": "指示その2"}},
    ])
    r = _run_session(sess, self.evidence, self.docs)
    self.assertEqual(r.returncode, 0, f"stdout={r.stdout}\nstderr={r.stderr}")
    self.assertIn("再現性チェック: ok 2", r.stdout,
                  f"層1・層2 とも再現性 ok のはず。stdout={r.stdout}")

  def test_residual_secret_is_skipped(self):
    """残存検出（fail-closed）のセッションは書かずに飛ばす。"""
    sess = self.tmp / "testsess-0003.jsonl"
    token = "Abcd1234" * 6  # 48 文字・大小数字混在 = 高エントロピー候補
    _write_claude_fixture(sess, [
      {"type": "user", "timestamp": "2026-06-14T12:00:00.000Z",
       "message": {"role": "user", "content": f"鍵らしき値 {token}"}},
    ])
    r = _run_session(sess, self.evidence, self.docs)
    self.assertEqual(r.returncode, 0, f"stdout={r.stdout}\nstderr={r.stderr}")
    self.assertFalse(
      (self.evidence / "2026-06-14-claude-testsess-0003.md").exists(),
      "残存検出時は層1 を書かない",
    )
    self.assertIn("飛ばし", r.stdout, f"飛ばしを報告するはず。stdout={r.stdout}")

  def test_missing_input_returns_nonzero(self):
    """入力が存在しなければ非ゼロで終了する。"""
    r = _run_session(self.tmp / "does-not-exist.jsonl", self.evidence, self.docs)
    self.assertNotEqual(r.returncode, 0, f"stdout={r.stdout}\nstderr={r.stderr}")

  def test_codex_session_requires_current_session_id_guard(self):
    """Codex の直接 --session 取り込みは current-session guard 無しでは拒否する。"""
    session_id = "aaaaaaaa-1111-2222-3333-444444444444"
    sess = self.tmp / f"rollout-2026-06-14T10-00-00-{session_id}.jsonl"
    _write_codex_fixture(sess, session_id, "/Users/Daily/Development/ReviewCompass",
                         "Codex direct backfill")

    r = _run_session(sess, self.evidence, self.docs, source="codex")

    self.assertEqual(r.returncode, 2, f"stdout={r.stdout}\nstderr={r.stderr}")
    self.assertIn("--current-session-id", r.stderr)
    self.assertFalse(self.evidence.exists() and any(self.evidence.iterdir()))

  def test_codex_session_refuses_current_session_id(self):
    """対象 Codex session が current-session-id と同一なら正式記録しない。"""
    session_id = "aaaaaaaa-1111-2222-3333-444444444444"
    sess = self.tmp / f"rollout-2026-06-14T10-00-00-{session_id}.jsonl"
    _write_codex_fixture(sess, session_id, "/Users/Daily/Development/ReviewCompass",
                         "current session")

    r = _run_session(
      sess, self.evidence, self.docs, source="codex",
      extra=["--current-session-id", session_id],
    )

    self.assertEqual(r.returncode, 2, f"stdout={r.stdout}\nstderr={r.stderr}")
    self.assertIn("current session", r.stderr)
    self.assertFalse(self.evidence.exists() and any(self.evidence.iterdir()))

  def test_codex_session_refuses_current_parent_session_id(self):
    """現在 session 配下の派生 Codex log は正式記録しない。"""
    session_id = "aaaaaaaa-1111-2222-3333-444444444444"
    parent_id = "bbbbbbbb-1111-2222-3333-444444444444"
    sess = self.tmp / f"rollout-2026-06-14T10-00-00-{session_id}.jsonl"
    _write_codex_fixture(
      sess, session_id, "/Users/Daily/Development/ReviewCompass",
      "guardian subagent", parent_session_id=parent_id,
    )

    r = _run_session(
      sess, self.evidence, self.docs, source="codex",
      extra=["--current-session-id", parent_id],
    )

    self.assertEqual(r.returncode, 2, f"stdout={r.stdout}\nstderr={r.stderr}")
    self.assertIn("current session", r.stderr)
    self.assertFalse(self.evidence.exists() and any(self.evidence.iterdir()))

  def test_codex_session_allows_non_current_session(self):
    """current-session-id と異なる終了済み Codex session は直接回収できる。"""
    session_id = "aaaaaaaa-1111-2222-3333-444444444444"
    current_id = "bbbbbbbb-1111-2222-3333-444444444444"
    sess = self.tmp / f"rollout-2026-06-14T10-00-00-{session_id}.jsonl"
    _write_codex_fixture(sess, session_id, "/Users/Daily/Development/ReviewCompass",
                         "past session")

    r = _run_session(
      sess, self.evidence, self.docs, source="codex",
      extra=["--current-session-id", current_id],
    )

    self.assertEqual(r.returncode, 0, f"stdout={r.stdout}\nstderr={r.stderr}")
    self.assertTrue(
      (self.evidence / f"2026-06-14-codex-{session_id}.md").exists(),
      f"終了済み session は層1 を書く。stdout={r.stdout}",
    )


if __name__ == "__main__":
  unittest.main()
