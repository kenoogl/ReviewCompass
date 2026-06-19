"""tools/commit-from-current-staged.py の単体テスト"""

import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from tests.tools.test_check_workflow_action import (
  _init_git_repo,
  _prepare_commit_approval,
  _record_commit_approval,
  _stage_file,
)
from tests.tools.test_guarded_git_commit import latest_commit_subject


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "tools" / "commit-from-current-staged.py"


def run_wrapper(args, cwd, input_text=None):
  """commit-from-current-staged.py をサブプロセスで実行する"""
  return subprocess.run(
    ["python3", str(SCRIPT)] + list(args),
    cwd=str(cwd),
    input=input_text,
    capture_output=True,
    text=True,
    timeout=10,
  )


def runtime_record(tmpdir, name):
  """runtime approval record を読む"""
  path = (
    Path(tmpdir)
    / ".reviewcompass"
    / "runtime"
    / "approvals"
    / name
  )
  return json.loads(path.read_text(encoding="utf-8"))


class CommitFromCurrentStagedTests(unittest.TestCase):
  """現在の staged index から approval 作成と commit を一括実行する wrapper"""

  def setUp(self):
    self.tmpdir = tempfile.mkdtemp()
    self.addCleanup(shutil.rmtree, self.tmpdir)
    _init_git_repo(self.tmpdir)

  def test_commits_current_staged_even_when_stale_approval_exists(self):
    """古い approval があっても現在の index に束縛し直して即 commit する"""
    _stage_file(self.tmpdir, "old.md", "# old")
    stale_challenge = _prepare_commit_approval(self.tmpdir)
    stale_record = _record_commit_approval(
      self.tmpdir,
      stale_challenge["nonce"],
      source_text="コミット\n",
    )
    self.assertEqual(stale_record.returncode, 0, stale_record.stderr)
    _stage_file(self.tmpdir, "current.md", "# current")

    result = run_wrapper(
      [
        "-m", "commit current staged",
        "--rationale", "利用者が本ターンでコミットを明示指示",
      ],
      cwd=self.tmpdir,
      input_text="コミット\n",
    )

    self.assertEqual(result.returncode, 0, result.stderr)
    self.assertEqual(result.stdout.count("\n"), 2)
    self.assertIn("commit precheck: OK", result.stdout)
    self.assertIn("committed:", result.stdout)
    self.assertNotIn("[CURRENT STATE]", result.stdout)
    self.assertEqual(latest_commit_subject(self.tmpdir), "commit current staged")
    approval = runtime_record(self.tmpdir, "commit-approval.json")
    challenge = runtime_record(self.tmpdir, "commit-approval-challenge.json")
    delegation = runtime_record(self.tmpdir, "commit-execution-delegation.json")
    self.assertTrue(approval["consumed"])
    self.assertTrue(challenge["consumed"])
    self.assertTrue(delegation["consumed"])
    self.assertEqual(
      sorted(challenge["target_files"]),
      ["current.md", "old.md"],
    )

  def test_requires_stdin_approval_before_creating_challenge(self):
    """stdin 承認文がない場合は challenge を作らず停止する"""
    _stage_file(self.tmpdir, "notes.md", "# notes")

    result = run_wrapper(
      [
        "-m", "missing approval",
        "--rationale", "利用者が本ターンでコミットを明示指示",
      ],
      cwd=self.tmpdir,
      input_text="",
    )

    self.assertEqual(result.returncode, 2)
    self.assertIn("承認文が入力されていません", result.stderr)
    challenge_path = (
      Path(self.tmpdir)
      / ".reviewcompass"
      / "runtime"
      / "approvals"
      / "commit-approval-challenge.json"
    )
    self.assertFalse(challenge_path.exists())
    self.assertEqual(latest_commit_subject(self.tmpdir), "add carry-forward register")


if __name__ == "__main__":
  unittest.main()
