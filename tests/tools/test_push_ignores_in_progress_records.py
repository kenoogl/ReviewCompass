"""push 事前検査：セッション記録（進行中・終了済み問わず）は未コミットなら汚れとして扱う。

背景：セッション記録はスナップショットとしてコミット可能になったため、未追跡の記録は
「コミットすべき変更」として扱う。進行中セッションの記録も例外ではない。

TDD 規律（AGENTS.md 入口規律）に従う。
実行：
  cd /Users/Daily/Development/ReviewCompass
  python3 -m unittest tests.tools.test_push_ignores_in_progress_records -v
"""

import hashlib
import shutil
import tempfile
import unittest
from pathlib import Path

from tests.tools.test_check_workflow_action import (
  _init_git_repo,
  run_script,
)


DIRTY_MSG = "作業ツリーに未コミット変更があります"


def _record_text(source_path, source_sha256):
  return (
    "---\n"
    "generated_by: session-record-extractor\n"
    "tool_version: testver\n"
    "layer: record\n"
    "source_kind: claude\n"
    f"source_path: {source_path}\n"
    f"source_sha256: {source_sha256}\n"
    "redaction_rules: builtin\n"
    "session_label: claude-2026-06-14-testsess\n"
    "---\n"
    "# セッション記録（テスト）\n"
  )


class PushIgnoresInProgressRecordTests(unittest.TestCase):
  def setUp(self):
    self.tmpdir = tempfile.mkdtemp()
    self.addCleanup(shutil.rmtree, self.tmpdir)
    _init_git_repo(self.tmpdir)
    # 元の会話ログ（jsonl）は repo の外に置く（repo 内だと未追跡として汚れに数えられるため）
    self.srcdir = Path(tempfile.mkdtemp())
    self.addCleanup(shutil.rmtree, self.srcdir)
    self.src = self.srcdir / "testsess.jsonl"
    self.src.write_bytes(b'{"type":"user","content":"hi"}\n')
    self.src_sha = hashlib.sha256(self.src.read_bytes()).hexdigest()
    self.record = (
      Path(self.tmpdir)
      / ".reviewcompass" / "evidence" / "sessions"
      / "2026-06-14-claude-testsess.md"
    )
    self.record.parent.mkdir(parents=True, exist_ok=True)

  def test_push_blocked_by_in_progress_record(self):
    """進行中（元ログが生成後に変化）の未追跡記録もスナップショットとしてコミット可能な
    ため、未追跡のまま残っていれば汚れとして push を止める。"""
    self.record.write_text(_record_text(str(self.src), self.src_sha))
    # 記録生成後に元ログが伸びた＝まだ進行中
    with open(self.src, "ab") as f:
      f.write(b'{"type":"assistant","content":"more"}\n')
    r = run_script(["push", "--rationale", "進行中記録も汚れとして弾く"],
                   cwd=self.tmpdir)
    self.assertEqual(r.returncode, 2,
                     f"進行中記録も未コミットなら push を止める。stdout={r.stdout}")
    self.assertIn(DIRTY_MSG, r.stdout,
                  f"汚れ理由が必要。stdout={r.stdout}")

  def test_push_still_blocked_by_finished_record(self):
    """終了済み（元ログが生成時から不変）の未追跡記録は、従来どおり汚れとして弾く。"""
    self.record.write_text(_record_text(str(self.src), self.src_sha))  # 元ログ変えない
    r = run_script(["push", "--rationale", "終了済み未追跡記録は弾く"],
                   cwd=self.tmpdir)
    self.assertEqual(r.returncode, 2,
                     f"終了済み記録は委ねずコミットすべき＝弾く。stdout={r.stdout}")
    self.assertIn(DIRTY_MSG, r.stdout, f"汚れ理由が必要。stdout={r.stdout}")

  def test_push_still_blocked_by_normal_untracked(self):
    """セッション記録でない通常の未追跡ファイルは、従来どおり弾く。"""
    (Path(self.tmpdir) / "untracked.md").write_text("# 未追跡")
    r = run_script(["push", "--rationale", "通常の未追跡は弾く"],
                   cwd=self.tmpdir)
    self.assertEqual(r.returncode, 2, f"通常の未追跡は弾く。stdout={r.stdout}")
    self.assertIn(DIRTY_MSG, r.stdout, f"汚れ理由が必要。stdout={r.stdout}")


if __name__ == "__main__":
  unittest.main()
