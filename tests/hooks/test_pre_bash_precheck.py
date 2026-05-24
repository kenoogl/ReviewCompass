"""段階 3 フックスクリプト .claude/hooks/pre-bash-precheck.sh の単体テスト

対象仕様：docs/operations/WORKFLOW_PRECHECK.md §12
対象範囲：Bash の git commit／git push を検出して check-workflow-action.py を呼ぶ MVP

TDD 規律（CLAUDE.md 全体規律）に従い、本テストはフックスクリプト実装前に作成。
実行方法：
  cd /Users/Daily/Development/ReviewCompass
  python3 -m unittest tests.hooks.test_pre_bash_precheck -v
"""

import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
HOOK_SCRIPT = REPO_ROOT / ".claude" / "hooks" / "pre-bash-precheck.sh"


def run_hook(tool_input_dict, cwd):
  """フックスクリプトを subprocess で実行して結果を返す

  tool_input_dict: PreToolUse の tool_input 部分（例：{"command": "git commit"}）
  cwd: 実行ディレクトリ（temp git repo 等）
  """
  payload = {"tool_name": "Bash", "tool_input": tool_input_dict}
  return subprocess.run(
    ["bash", str(HOOK_SCRIPT)],
    input=json.dumps(payload),
    cwd=str(cwd),
    capture_output=True,
    text=True,
    timeout=15,
  )


def _assert_hook_invoked(testcase, result):
  """フックスクリプトが実際に起動したことを確認するヘルパー"""
  for marker in ("No such file or directory", "cannot find"):
    testcase.assertNotIn(
      marker, result.stderr,
      f"フックスクリプトが起動できていない（実装前の状態か）。stderr: {result.stderr}",
    )


def _setup_git_repo_with_script(tmpdir):
  """temp dir に git リポジトリと .reviewcompass 構造、段階 2 スクリプトを準備"""
  for cmd in [
    ["git", "init", "-q", "-b", "main"],
    ["git", "config", "user.email", "test@example.com"],
    ["git", "config", "user.name", "Test User"],
    ["git", "config", "commit.gpgsign", "false"],
  ]:
    subprocess.run(cmd, cwd=str(tmpdir), check=True, capture_output=True)
  Path(tmpdir, ".gitignore").write_text("")
  subprocess.run(
    ["git", "add", ".gitignore"], cwd=str(tmpdir), check=True, capture_output=True
  )
  subprocess.run(
    ["git", "commit", "-qm", "initial"],
    cwd=str(tmpdir), check=True, capture_output=True,
  )
  # .reviewcompass 構造
  pending_dir = Path(tmpdir) / ".reviewcompass"
  pending_dir.mkdir()
  pending_file = pending_dir / "pending-cross-feature-findings.md"
  pending_file.write_text("# 機能横断レビューで扱う所見の集約\n")
  subprocess.run(
    ["git", "add", ".reviewcompass/pending-cross-feature-findings.md"],
    cwd=str(tmpdir), check=True, capture_output=True,
  )
  subprocess.run(
    ["git", "commit", "-qm", "add pending"],
    cwd=str(tmpdir), check=True, capture_output=True,
  )
  # 段階 2 スクリプトを tools/ にコピー（フックが python3 tools/check-workflow-action.py
  # を相対パスで呼ぶため）
  tools_dir = Path(tmpdir) / "tools"
  tools_dir.mkdir()
  shutil.copy(REPO_ROOT / "tools" / "check-workflow-action.py", tools_dir)
  return pending_file


def _stage_file(tmpdir, relpath, content):
  """temp git repo にファイルを作成して staged にする"""
  full = Path(tmpdir) / relpath
  full.parent.mkdir(parents=True, exist_ok=True)
  full.write_text(content)
  subprocess.run(
    ["git", "add", relpath], cwd=str(tmpdir), check=True, capture_output=True
  )


class HookPassThroughTests(unittest.TestCase):
  """フックが非 git／読み取り専用 git コマンドを通過させる（仕様 §12.1）"""

  def setUp(self):
    self.tmpdir = tempfile.mkdtemp()
    self.addCleanup(shutil.rmtree, self.tmpdir)
    _setup_git_repo_with_script(self.tmpdir)

  def test_non_git_command_passes(self):
    """非 git コマンド（ls 等）は何もせず exit 0 で通過"""
    result = run_hook({"command": "ls -la"}, cwd=self.tmpdir)
    _assert_hook_invoked(self, result)
    self.assertEqual(
      result.returncode, 0,
      f"非 git コマンドは exit 0 で通過すべき。\n"
      f"stdout: {result.stdout}\nstderr: {result.stderr}",
    )

  def test_git_status_passes(self):
    """git status は読み取り専用のため通過"""
    result = run_hook({"command": "git status"}, cwd=self.tmpdir)
    _assert_hook_invoked(self, result)
    self.assertEqual(result.returncode, 0)

  def test_git_log_passes(self):
    """git log は読み取り専用のため通過"""
    result = run_hook({"command": "git log --oneline -5"}, cwd=self.tmpdir)
    _assert_hook_invoked(self, result)
    self.assertEqual(result.returncode, 0)


class HookCommitTests(unittest.TestCase):
  """git commit のフック検査（仕様 §12.1 ＋ §6.2）"""

  def setUp(self):
    self.tmpdir = tempfile.mkdtemp()
    self.addCleanup(shutil.rmtree, self.tmpdir)
    self.pending_file = _setup_git_repo_with_script(self.tmpdir)

  def test_clean_commit_allows(self):
    """通常変更のみの git commit は通過（exit 0 で permissionDecision 出力なし）"""
    _stage_file(self.tmpdir, "notes.md", "# テストノート")
    result = run_hook(
      {"command": "git commit -m 'add notes'"},
      cwd=self.tmpdir,
    )
    _assert_hook_invoked(self, result)
    self.assertEqual(
      result.returncode, 0,
      f"clean な commit は通過すべき。\n"
      f"stdout: {result.stdout}\nstderr: {result.stderr}",
    )
    # deny 判定ではないこと（permissionDecision が deny でない）
    if result.stdout.strip():
      try:
        data = json.loads(result.stdout)
        decision = data.get("hookSpecificOutput", {}).get("permissionDecision", "")
        self.assertNotEqual(decision, "deny", "clean な commit は deny されてはいけない")
      except json.JSONDecodeError:
        pass  # JSON 出力がなければ allow 扱い

  def test_dangerous_file_denies_commit(self):
    """credentials.json を含む commit は deny（仕様 §6.2 危険変更）"""
    _stage_file(self.tmpdir, "credentials.json", '{"key":"dummy"}')
    result = run_hook(
      {"command": "git commit -m 'add creds'"},
      cwd=self.tmpdir,
    )
    _assert_hook_invoked(self, result)
    # フックは exit 0 を返し、deny の JSON を stdout に出力する
    self.assertEqual(result.returncode, 0,
      f"フック自体は exit 0、deny は JSON で出力すべき。\n"
      f"stdout: {result.stdout}\nstderr: {result.stderr}")
    data = json.loads(result.stdout)
    decision = data["hookSpecificOutput"]["permissionDecision"]
    self.assertEqual(
      decision, "deny",
      f"危険変更（credentials）の commit は deny されるべき。stdout: {result.stdout}",
    )


class HookPushTests(unittest.TestCase):
  """git push のフック検査（仕様 §12.1 ＋ §6.3）"""

  def setUp(self):
    self.tmpdir = tempfile.mkdtemp()
    self.addCleanup(shutil.rmtree, self.tmpdir)
    _setup_git_repo_with_script(self.tmpdir)

  def test_clean_push_allows(self):
    """clean な状態の git push は通過"""
    result = run_hook(
      {"command": "git push origin main"},
      cwd=self.tmpdir,
    )
    _assert_hook_invoked(self, result)
    self.assertEqual(result.returncode, 0)
    if result.stdout.strip():
      try:
        data = json.loads(result.stdout)
        decision = data.get("hookSpecificOutput", {}).get("permissionDecision", "")
        self.assertNotEqual(decision, "deny", "clean な push は deny されてはいけない")
      except json.JSONDecodeError:
        pass

  def test_dirty_push_denies(self):
    """dirty な状態の git push は deny（仕様 §6.3）"""
    (Path(self.tmpdir) / "untracked.md").write_text("test")
    result = run_hook(
      {"command": "git push origin main"},
      cwd=self.tmpdir,
    )
    _assert_hook_invoked(self, result)
    self.assertEqual(result.returncode, 0,
      f"フック自体は exit 0、deny は JSON で出力すべき。\n"
      f"stdout: {result.stdout}\nstderr: {result.stderr}")
    data = json.loads(result.stdout)
    decision = data["hookSpecificOutput"]["permissionDecision"]
    self.assertEqual(
      decision, "deny",
      f"dirty tree での push は deny されるべき。stdout: {result.stdout}",
    )


if __name__ == "__main__":
  unittest.main()
