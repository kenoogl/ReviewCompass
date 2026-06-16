"""tools/guarded-git-commit.py の単体テスト"""

import json
import importlib.util
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from tests.tools.test_check_workflow_action import (
  _delegate_commit_execution,
  _init_git_repo,
  _prepare_commit_approval,
  _read_commit_execution_delegation,
  _record_commit_approval,
  _stage_file,
  _write_commit_approval,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "tools" / "guarded-git-commit.py"


def load_guarded_module():
  """guarded-git-commit.py を直接呼び出せる形で読み込む"""
  spec = importlib.util.spec_from_file_location("guarded_git_commit_under_test", SCRIPT)
  module = importlib.util.module_from_spec(spec)
  sys.path.insert(0, str(REPO_ROOT / "tools"))
  spec.loader.exec_module(module)
  return module


def run_guarded_commit(args, cwd, input_text=None):
  """guarded-git-commit.py をサブプロセスで実行する"""
  return subprocess.run(
    ["python3", str(SCRIPT)] + list(args),
    cwd=str(cwd),
    input=input_text,
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

  def test_guarded_commit_consumes_nonce_challenge_after_success(self):
    """nonce 承認 commit 成功後は approval/challenge/delegation を消費済みにする"""
    _stage_file(self.tmpdir, "notes.md", "# nonce commit")
    challenge = _prepare_commit_approval(self.tmpdir)
    record_result = _record_commit_approval(self.tmpdir, challenge["nonce"])
    self.assertEqual(record_result.returncode, 0, record_result.stderr)
    delegate_result = _delegate_commit_execution(
      self.tmpdir,
      challenge["nonce"],
    )
    self.assertEqual(delegate_result.returncode, 0, delegate_result.stderr)

    result = run_guarded_commit(
      [
        "-m", "guarded nonce commit",
        "--rationale", "利用者が LLM によるコミット実行代行を明示承認",
      ],
      cwd=self.tmpdir,
    )

    self.assertEqual(result.returncode, 0, result.stderr)
    approval_path = (
      Path(self.tmpdir)
      / ".reviewcompass"
      / "runtime"
      / "approvals"
      / "commit-approval.json"
    )
    approval = json.loads(approval_path.read_text(encoding="utf-8"))
    challenge_path = (
      Path(self.tmpdir)
      / ".reviewcompass"
      / "runtime"
      / "approvals"
      / "commit-approval-challenge.json"
    )
    consumed_challenge = json.loads(challenge_path.read_text(encoding="utf-8"))
    delegation = _read_commit_execution_delegation(self.tmpdir)
    self.assertTrue(approval["consumed"])
    self.assertTrue(consumed_challenge["consumed"])
    self.assertTrue(delegation["consumed"])

  def test_guarded_commit_records_line_approval_and_commits(self):
    """承認1行で内容承認・実行代行承認・commit まで進める"""
    _stage_file(self.tmpdir, "notes.md", "# deployable commit ux")
    challenge = _prepare_commit_approval(self.tmpdir)

    result = run_guarded_commit(
      [
        "-m", "guarded line approval commit",
        "--rationale", "利用者が提示済み nonce と staged 内容を承認",
        "--approval-nonce", challenge["nonce"],
        "--approval-source-text-line-stdin",
      ],
      cwd=self.tmpdir,
      input_text="承認\n",
    )

    self.assertEqual(
      result.returncode, 0,
      f"line approval should allow commit.\nstdout: {result.stdout}\nstderr: {result.stderr}",
    )
    self.assertEqual(latest_commit_subject(self.tmpdir), "guarded line approval commit")
    approval_path = (
      Path(self.tmpdir)
      / ".reviewcompass"
      / "runtime"
      / "approvals"
      / "commit-approval.json"
    )
    approval = json.loads(approval_path.read_text(encoding="utf-8"))
    delegation = _read_commit_execution_delegation(self.tmpdir)
    self.assertTrue(approval["consumed"])
    self.assertTrue(delegation["consumed"])
    self.assertEqual(delegation["explicit_instruction"], "承認")

  def test_guarded_commit_consumes_nonce_challenge_before_approval(self):
    """nonce 承認は challenge を先に消費し、再利用可能な challenge を残さない"""
    _stage_file(self.tmpdir, "notes.md", "# nonce consumption order")
    challenge = _prepare_commit_approval(self.tmpdir)
    record_result = _record_commit_approval(self.tmpdir, challenge["nonce"])
    self.assertEqual(record_result.returncode, 0, record_result.stderr)
    delegate_result = _delegate_commit_execution(self.tmpdir, challenge["nonce"])
    self.assertEqual(delegate_result.returncode, 0, delegate_result.stderr)

    approval_path = (
      Path(self.tmpdir)
      / ".reviewcompass"
      / "runtime"
      / "approvals"
      / "commit-approval.json"
    )
    guarded = load_guarded_module()
    original_mark_consumed = guarded._mark_consumed
    observed = {}

    def spy_mark_consumed(path, consumed_at):
      approval = json.loads(approval_path.read_text(encoding="utf-8"))
      observed["approval_consumed_before_challenge"] = approval.get("consumed") is True
      return original_mark_consumed(path, consumed_at)

    guarded._mark_consumed = spy_mark_consumed
    try:
      self.assertTrue(guarded.consume_commit_approval(self.tmpdir))
    finally:
      guarded._mark_consumed = original_mark_consumed

    self.assertFalse(observed["approval_consumed_before_challenge"])


if __name__ == "__main__":
  unittest.main()
