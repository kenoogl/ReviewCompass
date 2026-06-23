"""tools/session-record-backfill.py の一括スキャン抑止（歯止め）の単体テスト。

背景：一括 backfill（--session なし）は、まだ終わっていないセッション（実行中の
自分自身を含む）を掴むことがあり、後で取り込み直し＝差分のたまり（churn）を生む。
going-forward 取り込みは session-record-capture-previous-codex.py が担い、過去
ログの一括取り込みは完了済みのため、一括スキャンは既定で無効にする。どうしても
必要な一度きりの過去ログ取り込みは明示フラグ --historical-import で許可する。

TDD 規律（AGENTS.md 入口規律）に従い、本テストは実装前に作成する。
実行：
  cd /Users/Daily/Development/ReviewCompass
  python3 -m unittest tests.tools.test_session_record_bulk_guard -v
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
  path.parent.mkdir(parents=True, exist_ok=True)
  body = "\n".join(json.dumps(o, ensure_ascii=False) for o in objs) + "\n"
  path.write_text(body, encoding="utf-8")


_SAMPLE = [
  {"type": "user", "timestamp": "2026-06-14T10:00:00.000Z",
   "message": {"role": "user", "content": "一括歯止めテスト指示"}},
  {"type": "assistant", "timestamp": "2026-06-14T10:00:05.000Z",
   "message": {"role": "assistant", "content": [{"type": "text", "text": "了解"}]}},
]


class BulkBackfillGuardTests(unittest.TestCase):
  def setUp(self):
    self.tmp = Path(tempfile.mkdtemp())
    self.addCleanup(shutil.rmtree, self.tmp)
    self.claude_dir = self.tmp / "claude"
    self.codex_root = self.tmp / "codex"
    self.codex_root.mkdir(parents=True, exist_ok=True)
    self.evidence = self.tmp / "evidence"
    self.docs = self.tmp / "docs"
    # 一括スキャンが拾えるフィクスチャを 1 件置く
    _write_claude_fixture(self.claude_dir / "bulksess-0001.jsonl", _SAMPLE)

  def _run_bulk(self, extra=None):
    cmd = [
      sys.executable, str(BACKFILL),
      "--claude-dir", str(self.claude_dir),
      "--codex-root", str(self.codex_root),
      "--evidence-dir", str(self.evidence),
      "--docs-dir", str(self.docs),
    ]
    if extra:
      cmd += extra
    return subprocess.run(
      cmd, cwd=str(REPO_ROOT), capture_output=True, text=True,
      errors="replace", timeout=60)

  def test_bulk_without_flag_refuses(self):
    """一括スキャン（--session なし）は、明示フラグ無しでは止まり、何も書かない。"""
    r = self._run_bulk()
    self.assertNotEqual(r.returncode, 0,
                        f"一括は既定で止まるはず。stdout={r.stdout}\nstderr={r.stderr}")
    self.assertFalse(self.evidence.exists() and any(self.evidence.iterdir()),
                     "止まったときは層1 を書かない")
    msg = r.stdout + r.stderr
    self.assertIn("--session", msg, "単一取り込みへの案内が必要")
    self.assertIn(
      "session-record-capture-previous-codex.py",
      msg,
      "going-forward を担う CLI への案内が必要",
    )

  def test_bulk_with_flag_runs(self):
    """明示フラグ --historical-import を付けたときだけ一括スキャンを実行する。"""
    r = self._run_bulk(extra=["--historical-import"])
    self.assertEqual(r.returncode, 0,
                     f"フラグ付きなら実行するはず。stdout={r.stdout}\nstderr={r.stderr}")
    self.assertTrue(
      (self.evidence / "2026-06-14-claude-bulksess-0001.md").exists(),
      f"フラグ付き一括は層1 を書く。stdout={r.stdout}")

  def test_bulk_dry_run_also_refuses_without_flag(self):
    """--dry-run でも、明示フラグ無しの一括スキャンは止める（誤用の入口を塞ぐ）。"""
    r = self._run_bulk(extra=["--dry-run"])
    self.assertNotEqual(r.returncode, 0,
                        f"dry-run でも一括は既定で止まるはず。stdout={r.stdout}\nstderr={r.stderr}")

  def test_single_session_unaffected_by_guard(self):
    """歯止めは一括だけに効き、単一取り込み（--session）はフラグ無しで通る。"""
    sess = self.claude_dir / "bulksess-0001.jsonl"
    r = subprocess.run(
      [
        sys.executable, str(BACKFILL),
        "--session", str(sess), "--source", "claude",
        "--evidence-dir", str(self.evidence), "--docs-dir", str(self.docs),
      ],
      cwd=str(REPO_ROOT), capture_output=True, text=True,
      errors="replace", timeout=60)
    self.assertEqual(r.returncode, 0,
                     f"単一取り込みは歯止めの影響を受けない。stdout={r.stdout}\nstderr={r.stderr}")
    self.assertTrue(
      (self.evidence / "2026-06-14-claude-bulksess-0001.md").exists(),
      f"単一取り込みは層1 を書く。stdout={r.stdout}")


if __name__ == "__main__":
  unittest.main()
