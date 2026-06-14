"""push 事前検査：進行中セッションの記録は『作業ツリーの汚れ』に数えない（強制コード）。

背景：会話ログの記録は「進行中セッションはコミットしない」のが正（コミット側の歯止め
＝test_commit_in_progress_session_guard）。ところが push 前検査は作業ツリーを完全に
clean に保つよう求めるため、進行中の記録が未追跡で残っていると永遠に push できない。
両者の矛盾を解くため、push 前検査でも「進行中セッションの記録（元ログが生成後に変化）」
は汚れに数えず無視する。終了済みの記録や通常ファイルは従来どおり汚れとして弾く。

TDD 規律（AGENTS.md 入口規律）に従い、本テストは実装前に作成する。
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

  def test_push_not_blocked_by_in_progress_record(self):
    """進行中（元ログが生成後に変化）の未追跡記録は汚れに数えず、push を止めない。"""
    self.record.write_text(_record_text(str(self.src), self.src_sha))
    # 記録生成後に元ログが伸びた＝まだ進行中
    with open(self.src, "ab") as f:
      f.write(b'{"type":"assistant","content":"more"}\n')
    r = run_script(["push", "--rationale", "進行中記録は無視して push"],
                   cwd=self.tmpdir)
    self.assertNotIn(DIRTY_MSG, r.stdout,
                     f"進行中記録は汚れに数えない。stdout={r.stdout}")
    self.assertEqual(r.returncode, 0,
                     f"他に汚れが無ければ push 通過。stdout={r.stdout}\nstderr={r.stderr}")

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
