"""tools/guarded-git-commit.py の単体テスト"""

import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from tests.tools.test_check_workflow_action import (
  _init_git_repo,
  _stage_file,
  _write_commit_approval,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "tools" / "guarded-git-commit.py"


def run_guarded_commit(args, cwd):
  """guarded-git-commit.py をサブプロセスで実行する"""
  return subprocess.run(
    ["python3", str(SCRIPT)] + list(args),
    cwd=str(cwd),
    capture_output=True,
    text=True,
  )


def latest_commit_subject(cwd):
  """直近 commit の subject を返す"""
  result = subprocess.run(
    ["git", "log", "-1", "--pretty=%s"],
    cwd=str(cwd),
    check=True,
    capture_output=True,
    text=True,
  )
  return result.stdout.strip()


class GuardedGitCommitTests(unittest.TestCase):
  """ユーザ承認付き git commit ラッパーの判定"""

  def setUp(self):
    self.tmpdir = tempfile.mkdtemp()
    self.addCleanup(shutil.rmtree, self.tmpdir)
    self.pending_file = _init_git_repo(self.tmpdir)

  def test_guarded_commit_blocks_without_user_approval(self):
    """承認レコードなしなら commit しない"""
    _stage_file(self.tmpdir, "notes.md", "# テスト用ノート")
    result = run_guarded_commit(
      ["-m", "guarded commit", "--rationale", "承認なしの遮断テスト"],
      cwd=self.tmpdir,
    )
    self.assertEqual(result.returncode, 2)
    self.assertEqual(latest_commit_subject(self.tmpdir), "add carry-forward register")
    self.assertIn("ユーザ承認レコード", result.stdout)

  def test_guarded_commit_blocks_without_execution_delegation(self):
    """内容承認だけで実行代行承認がなければ commit しない"""
    _stage_file(self.tmpdir, "notes.md", "# テスト用ノート")
    _write_commit_approval(
      self.tmpdir,
      ["notes.md"],
      include_execution_delegation=False,
    )
    result = run_guarded_commit(
      ["-m", "guarded commit", "--rationale", "利用者がコミット内容を明示承認"],
      cwd=self.tmpdir,
    )
    self.assertEqual(result.returncode, 2)
    self.assertEqual(latest_commit_subject(self.tmpdir), "add carry-forward register")
    self.assertIn("コミット実行代行", result.stdout)

  def test_guarded_commit_commits_and_consumes_delegated_approval(self):
    """実行代行承認があれば commit し、承認を消費済みにする"""
    _stage_file(self.tmpdir, "notes.md", "# テスト用ノート")
    approval_path = _write_commit_approval(self.tmpdir, ["notes.md"])
    result = run_guarded_commit(
      [
        "-m", "guarded commit",
        "--rationale", "利用者が LLM によるコミット実行代行を明示承認",
      ],
      cwd=self.tmpdir,
    )
    self.assertEqual(
      result.returncode, 0,
      f"valid approval should allow commit.\nstdout: {result.stdout}\nstderr: {result.stderr}",
    )
    self.assertEqual(latest_commit_subject(self.tmpdir), "guarded commit")
    approval = json.loads(approval_path.read_text(encoding="utf-8"))
    self.assertTrue(approval["consumed"])


if __name__ == "__main__":
  unittest.main()
