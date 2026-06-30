"""tools/guarded-git-commit.py の単体テスト"""

import io
import contextlib
import json
import importlib.util
import os
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
  run_script,
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


class TtyStdin:
  """テスト用の TTY 承認入力"""

  def __init__(self, text):
    self.buffer = io.BytesIO(text.encode("utf-8"))

  def isatty(self):
    return True


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

  def test_guarded_commit_clears_commit_unit_after_success(self):
    """commit 成功後は frozen commit-unit marker を自動削除する"""
    _stage_file(self.tmpdir, "notes.md", "# commit unit cleanup")
    freeze = run_script(
      [
        "commit-unit",
        "freeze",
        "--work-unit-id", "main-completed",
        "--allowed-file", "notes.md",
        "--json",
      ],
      cwd=self.tmpdir,
    )
    self.assertEqual(freeze.returncode, 0, freeze.stdout + freeze.stderr)
    marker = (
      Path(self.tmpdir)
      / ".reviewcompass"
      / "runtime"
      / "work-units"
      / "commit-unit.json"
    )
    self.assertTrue(marker.exists())
    _write_commit_approval(self.tmpdir, ["notes.md"])

    result = run_guarded_commit(
      [
        "-m", "commit unit cleanup",
        "--rationale", "利用者が LLM によるコミット実行代行を明示承認",
      ],
      cwd=self.tmpdir,
    )

    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
    self.assertEqual(latest_commit_subject(self.tmpdir), "commit unit cleanup")
    self.assertFalse(marker.exists())

  def test_guarded_commit_rejects_piped_line_approval(self):
    """pipe 経由の承認1行では approval record を作らず commit しない"""
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

    self.assertEqual(result.returncode, 2)
    self.assertIn("TTY", result.stderr)
    self.assertEqual(latest_commit_subject(self.tmpdir), "add carry-forward register")
    approval_path = (
      Path(self.tmpdir)
      / ".reviewcompass"
      / "runtime"
      / "approvals"
      / "commit-approval.json"
    )
    self.assertFalse(approval_path.exists())

  def test_guarded_commit_records_tty_line_approval_and_commits(self):
    """TTY 承認1行で内容承認・実行代行承認・commit まで進める"""
    _stage_file(self.tmpdir, "notes.md", "# deployable commit ux")
    challenge = _prepare_commit_approval(self.tmpdir)
    guarded = load_guarded_module()
    original_stdin = guarded.sys.stdin
    original_cwd = os.getcwd()

    try:
      os.chdir(self.tmpdir)
      guarded.sys.stdin = TtyStdin("承認\n")
      result = guarded.main([
        "-m", "guarded line approval commit",
        "--rationale", "利用者が提示済み nonce と staged 内容を承認",
        "--approval-nonce", challenge["nonce"],
        "--approval-source-text-line-stdin",
      ])
    finally:
      os.chdir(original_cwd)
      guarded.sys.stdin = original_stdin

    self.assertEqual(
      result, 0,
      "TTY line approval should allow commit.",
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

  def test_guarded_commit_success_output_is_minimal_by_default(self):
    """成功時の既定表示は precheck 詳細を流さず commit summary に絞る"""
    _stage_file(self.tmpdir, "notes.md", "# minimal output")
    challenge = _prepare_commit_approval(self.tmpdir)

    guarded = load_guarded_module()
    original_stdin = guarded.sys.stdin
    original_cwd = os.getcwd()
    stdout = io.StringIO()
    stderr = io.StringIO()

    try:
      os.chdir(self.tmpdir)
      guarded.sys.stdin = TtyStdin("承認\n")
      with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
        result = guarded.main([
          "-m", "minimal output commit",
          "--rationale", "利用者が提示済み nonce と staged 内容を承認",
          "--approval-nonce", challenge["nonce"],
          "--approval-source-text-line-stdin",
        ])
    finally:
      os.chdir(original_cwd)
      guarded.sys.stdin = original_stdin

    output = stdout.getvalue()
    self.assertEqual(result, 0, stderr.getvalue())
    self.assertNotIn("[CURRENT STATE]", output)
    self.assertNotIn("[ACTION]", output)
    self.assertIn("commit precheck: OK", output)
    self.assertRegex(output, r"committed: [0-9a-f]{7,40} minimal output commit")

  def test_guarded_commit_verbose_success_output_includes_precheck_details(self):
    """verbose 指定時は precheck 詳細を表示する"""
    _stage_file(self.tmpdir, "notes.md", "# verbose output")
    challenge = _prepare_commit_approval(self.tmpdir)

    guarded = load_guarded_module()
    original_stdin = guarded.sys.stdin
    original_cwd = os.getcwd()
    stdout = io.StringIO()
    stderr = io.StringIO()

    try:
      os.chdir(self.tmpdir)
      guarded.sys.stdin = TtyStdin("承認\n")
      with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
        result = guarded.main([
          "-m", "verbose output commit",
          "--rationale", "利用者が提示済み nonce と staged 内容を承認",
          "--approval-nonce", challenge["nonce"],
          "--approval-source-text-line-stdin",
          "--verbose",
        ])
    finally:
      os.chdir(original_cwd)
      guarded.sys.stdin = original_stdin

    output = stdout.getvalue()
    self.assertEqual(result, 0, stderr.getvalue())
    self.assertIn("[OK] commit", output)
    self.assertIn("1 file changed", output)
    self.assertIn("committed:", output)

  def test_guarded_commit_line_approval_retry_reuses_active_transaction(self):
    """commit 実行失敗後の同一 nonce 再実行は active transaction を再利用する"""
    _stage_file(self.tmpdir, "notes.md", "# retryable commit")
    challenge = _prepare_commit_approval(self.tmpdir)
    guarded = load_guarded_module()
    original_run_git_commit = guarded.run_git_commit
    original_stdin = guarded.sys.stdin
    original_cwd = os.getcwd()
    calls = {"count": 0}

    def fail_then_succeed(cwd, messages):
      calls["count"] += 1
      if calls["count"] == 1:
        return subprocess.CompletedProcess(
          ["git", "commit"],
          128,
          stdout="",
          stderr="fatal: Unable to create '.git/index.lock': Operation not permitted\n",
        )
      return original_run_git_commit(cwd, messages)

    guarded.run_git_commit = fail_then_succeed
    try:
      os.chdir(self.tmpdir)
      guarded.sys.stdin = TtyStdin("承認\n")
      first = guarded.main([
        "-m", "retryable guarded commit",
        "--rationale", "利用者が提示済み nonce と staged 内容を承認",
        "--approval-nonce", challenge["nonce"],
        "--approval-source-text-line-stdin",
      ])
      approval_path = (
        Path(self.tmpdir)
        / ".reviewcompass"
        / "runtime"
        / "approvals"
        / "commit-approval.json"
      )
      challenge_path = (
        Path(self.tmpdir)
        / ".reviewcompass"
        / "runtime"
        / "approvals"
        / "commit-approval-challenge.json"
      )
      approval_after_failure = json.loads(
        approval_path.read_text(encoding="utf-8")
      )
      challenge_after_failure = json.loads(
        challenge_path.read_text(encoding="utf-8")
      )
      delegation_after_failure = _read_commit_execution_delegation(self.tmpdir)

      guarded.sys.stdin = TtyStdin("承認\n")
      second = guarded.main([
        "-m", "retryable guarded commit",
        "--rationale", "利用者が提示済み nonce と staged 内容を承認",
        "--approval-nonce", challenge["nonce"],
        "--approval-source-text-line-stdin",
      ])
    finally:
      os.chdir(original_cwd)
      guarded.run_git_commit = original_run_git_commit
      guarded.sys.stdin = original_stdin

    self.assertEqual(first, 128)
    self.assertFalse(approval_after_failure["consumed"])
    self.assertFalse(approval_after_failure["invalidated"])
    self.assertFalse(challenge_after_failure["consumed"])
    self.assertFalse(challenge_after_failure["invalidated"])
    self.assertFalse(delegation_after_failure["consumed"])
    self.assertFalse(delegation_after_failure["invalidated"])
    self.assertEqual(second, 0)
    self.assertEqual(latest_commit_subject(self.tmpdir), "retryable guarded commit")

  def test_guarded_commit_preflight_denial_keeps_approval_and_skips_commit(self):
    """index.lock preflight で拒否されたら commit せず承認を保持する"""
    _stage_file(self.tmpdir, "notes.md", "# sandbox denied before commit")
    approval_path = _write_commit_approval(self.tmpdir, ["notes.md"])
    guarded = load_guarded_module()
    original_preflight = getattr(guarded, "preflight_git_index_lock", None)
    original_run_git_commit = guarded.run_git_commit
    original_cwd = os.getcwd()
    calls = {"commit": 0}

    def denied_preflight(cwd):
      return {
        "ok": False,
        "classification": "sandbox_git_write_denied",
        "message": "mock index.lock denied",
      }

    def fail_if_called(cwd, messages):
      calls["commit"] += 1
      return subprocess.CompletedProcess(
        ["git", "commit"],
        99,
        stdout="",
        stderr="git commit should not be called after denied preflight\n",
      )

    guarded.preflight_git_index_lock = denied_preflight
    guarded.run_git_commit = fail_if_called
    stdout = io.StringIO()
    stderr = io.StringIO()
    try:
      os.chdir(self.tmpdir)
      with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
        result = guarded.main([
          "-m", "guarded commit",
          "--rationale", "利用者が LLM によるコミット実行代行を明示承認",
        ])
    finally:
      os.chdir(original_cwd)
      guarded.run_git_commit = original_run_git_commit
      if original_preflight is None:
        del guarded.preflight_git_index_lock
      else:
        guarded.preflight_git_index_lock = original_preflight

    approval = json.loads(approval_path.read_text(encoding="utf-8"))
    combined_output = stdout.getvalue() + stderr.getvalue()
    self.assertEqual(result, 2)
    self.assertEqual(calls["commit"], 0)
    self.assertFalse(approval["consumed"])
    self.assertIn("sandbox_git_write_denied", combined_output)
    self.assertIn("required_action=rerun_commit_with_escalation", combined_output)

  def test_preflight_git_index_lock_reports_existing_lock(self):
    """既存 index.lock があれば commit 前に検査停止する"""
    guarded = load_guarded_module()
    lock_path = Path(self.tmpdir) / ".git" / "index.lock"
    lock_path.write_text("existing lock\n", encoding="utf-8")

    result = guarded.preflight_git_index_lock(self.tmpdir)

    self.assertFalse(result["ok"])
    self.assertEqual(result["classification"], "git_index_lock_exists")
    self.assertEqual(result["required_action"], "inspect_existing_git_index_lock")
    self.assertTrue(lock_path.exists())

  def test_preflight_git_index_lock_allows_writable_index_lock(self):
    """index.lock を作成削除できる場合は commit 実行へ進める"""
    guarded = load_guarded_module()
    lock_path = Path(self.tmpdir) / ".git" / "index.lock"

    result = guarded.preflight_git_index_lock(self.tmpdir)

    self.assertEqual(result, {"ok": True})
    self.assertFalse(lock_path.exists())

  def test_guarded_commit_classifies_index_lock_failure_after_commit_attempt(self):
    """commit 実行後の index.lock 失敗も sandbox_git_write_denied として表示する"""
    _stage_file(self.tmpdir, "notes.md", "# sandbox denied during commit")
    approval_path = _write_commit_approval(self.tmpdir, ["notes.md"])
    guarded = load_guarded_module()
    original_preflight = getattr(guarded, "preflight_git_index_lock", None)
    original_run_git_commit = guarded.run_git_commit
    original_cwd = os.getcwd()

    def allowed_preflight(cwd):
      return {"ok": True}

    def fail_with_index_lock(cwd, messages):
      return subprocess.CompletedProcess(
        ["git", "commit"],
        128,
        stdout="",
        stderr="fatal: Unable to create '.git/index.lock': Operation not permitted\n",
      )

    guarded.preflight_git_index_lock = allowed_preflight
    guarded.run_git_commit = fail_with_index_lock
    stdout = io.StringIO()
    stderr = io.StringIO()
    try:
      os.chdir(self.tmpdir)
      with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
        result = guarded.main([
          "-m", "guarded commit",
          "--rationale", "利用者が LLM によるコミット実行代行を明示承認",
        ])
    finally:
      os.chdir(original_cwd)
      guarded.run_git_commit = original_run_git_commit
      if original_preflight is None:
        del guarded.preflight_git_index_lock
      else:
        guarded.preflight_git_index_lock = original_preflight

    approval = json.loads(approval_path.read_text(encoding="utf-8"))
    combined_output = stdout.getvalue() + stderr.getvalue()
    self.assertEqual(result, 128)
    self.assertFalse(approval["consumed"])
    self.assertIn("sandbox_git_write_denied", combined_output)
    self.assertIn("required_action=rerun_commit_with_escalation", combined_output)

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
