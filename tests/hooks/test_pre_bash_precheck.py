"""段階 3 フックスクリプト .codex/hooks/pre-bash-precheck.sh の単体テスト

対象仕様：docs/operations/WORKFLOW_PRECHECK.md「段階 1・段階 3 との接続」
対象範囲：Bash の git commit／git push を検出して check-workflow-action.py を呼ぶ MVP

TDD 規律（AGENTS.md 入口規律）に従い、本テストはフックスクリプト実装前に作成。
実行方法：
  cd /Users/Daily/Development/ReviewCompass
  python3 -m unittest tests.hooks.test_pre_bash_precheck -v
"""

import json
import hashlib
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
HOOK_SCRIPT = REPO_ROOT / ".codex" / "hooks" / "pre-bash-precheck.sh"


def run_hook(tool_input_dict, cwd):
  """フックスクリプトを subprocess で実行して結果を返す

  tool_input_dict: PreToolUse の tool_input 部分（例：{"command": "git commit"}）
  cwd: 実行ディレクトリ（temp git repo 等）

  errors="replace" は git／locale 依存の stderr に非 UTF-8 バイトが含まれる
  可能性に対応する（macOS 等の環境差を吸収するための setup 設定、
  assertion は不変）。
  """
  payload = {"tool_name": "Bash", "tool_input": tool_input_dict}
  return subprocess.run(
    ["bash", str(HOOK_SCRIPT)],
    input=json.dumps(payload),
    cwd=str(cwd),
    capture_output=True,
    text=True,
    errors="replace",
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
  # carry-forward register 正本と履歴 source 構造
  register_dir = Path(tmpdir) / "learning" / "workflow" / "carry-forward-register"
  register_dir.mkdir(parents=True)
  register_file = register_dir / "reviewcompass-import.yaml"
  register_file.write_text(
    "items: []\n",
    encoding="utf-8",
  )
  pending_dir = register_dir / "sources"
  pending_dir.mkdir(parents=True)
  pending_file = pending_dir / "reviewcompass-pending-cross-feature-findings.md"
  pending_file.write_text(
    "# 機能横断レビューで扱う所見の集約\n",
    encoding="utf-8",
  )
  subprocess.run(
    [
      "git",
      "add",
      "learning/workflow/carry-forward-register/reviewcompass-import.yaml",
      "learning/workflow/carry-forward-register/sources/reviewcompass-pending-cross-feature-findings.md",
    ],
    cwd=str(tmpdir), check=True, capture_output=True,
  )
  subprocess.run(
    ["git", "commit", "-qm", "add pending"],
    cwd=str(tmpdir), check=True, capture_output=True,
  )
  # 段階 2 スクリプトを tools/ にコピー（フックが python3 tools/check-workflow-action.py
  # を相対パスで呼ぶため）。コピー後にコミットして作業ツリーを clean に保つ。
  tools_dir = Path(tmpdir) / "tools"
  tools_dir.mkdir()
  shutil.copy(REPO_ROOT / "tools" / "check-workflow-action.py", tools_dir)
  # check-workflow-action.py が同階層から import する lint 部品も併せてコピーする
  shutil.copy(REPO_ROOT / "tools" / "deployment_independence_lint.py", tools_dir)
  shutil.copy(REPO_ROOT / "tools" / "document_link_lint.py", tools_dir)
  # 実行時生成物パスの定数・読み取り解決（check_workflow_action パッケージ）も併せてコピーする
  package_dir = tools_dir / "check_workflow_action"
  package_dir.mkdir()
  shutil.copy(
    REPO_ROOT / "tools" / "check_workflow_action" / "runtime_paths.py", package_dir
  )
  subprocess.run(
    [
      "git",
      "add",
      "tools/check-workflow-action.py",
      "tools/deployment_independence_lint.py",
      "tools/document_link_lint.py",
      "tools/check_workflow_action/runtime_paths.py",
    ],
    cwd=str(tmpdir), check=True, capture_output=True,
  )
  subprocess.run(
    ["git", "commit", "-qm", "add stage-2 script"],
    cwd=str(tmpdir), check=True, capture_output=True,
  )
  return pending_file


def _stage_file(tmpdir, relpath, content):
  """temp git repo にファイルを作成して staged にする"""
  full = Path(tmpdir) / relpath
  full.parent.mkdir(parents=True, exist_ok=True)
  full.write_text(content)
  subprocess.run(
    ["git", "add", relpath], cwd=str(tmpdir), check=True, capture_output=True
  )


def _write_commit_approval(tmpdir, target_files, consumed=False):
  """temp git repo に commit 承認レコードを書く"""
  target_sha256 = {}
  for target_file in target_files:
    if target_file == "*":
      continue
    result = subprocess.run(
      ["git", "show", f":{target_file}"],
      cwd=str(tmpdir),
      capture_output=True,
      check=True,
    )
    target_sha256[target_file] = hashlib.sha256(result.stdout).hexdigest()

  approval_dir = Path(tmpdir) / ".reviewcompass" / "approvals"
  approval_dir.mkdir(parents=True, exist_ok=True)
  approval_path = approval_dir / "commit-approval.json"
  approval_path.write_text(
    json.dumps(
      {
        "approved_action": "commit",
        "approved_by": "user",
        "approved_at": "2026-06-03T00:00:00+09:00",
        "rationale": "人がコミットを明示承認",
        "target_files": target_files,
        "target_sha256": target_sha256,
        # 段階 2 は execution_actor=llm のとき実行代行の明示承認を要求する
        "execution_delegation": {
          "delegated_to": "llm",
          "approved_by": "user",
          "approved_at": "2026-06-03T00:00:00+09:00",
          "explicit_instruction": "コミット",
          "rationale": "人が単発 commit 実行を明示承認",
        },
        "expires_after_commit": True,
        "consumed": consumed,
      },
      ensure_ascii=False,
      indent=2,
    ),
    encoding="utf-8",
  )


class HookPassThroughTests(unittest.TestCase):
  """フックが非 git／読み取り専用 git コマンドを通過させる"""

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
  """git commit のフック検査"""

  def setUp(self):
    self.tmpdir = tempfile.mkdtemp()
    self.addCleanup(shutil.rmtree, self.tmpdir)
    self.pending_file = _setup_git_repo_with_script(self.tmpdir)

  def test_approved_clean_commit_allows(self):
    """承認済み通常変更の git commit は通過（permissionDecision 出力なし）"""
    _stage_file(self.tmpdir, "notes.md", "# テストノート")
    _write_commit_approval(self.tmpdir, ["notes.md"])
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

  def test_commit_without_user_approval_denies(self):
    """承認レコードなしの git commit は deny"""
    _stage_file(self.tmpdir, "notes.md", "# テストノート")
    result = run_hook(
      {"command": "git commit -m 'add notes'"},
      cwd=self.tmpdir,
    )
    _assert_hook_invoked(self, result)
    self.assertEqual(result.returncode, 0)
    data = json.loads(result.stdout)
    decision = data["hookSpecificOutput"]["permissionDecision"]
    self.assertEqual(decision, "deny")

  def test_dangerous_file_denies_commit(self):
    """credentials.json を含む commit は承認済みでも deny"""
    _stage_file(self.tmpdir, "credentials.json", '{"key":"dummy"}')
    _write_commit_approval(self.tmpdir, ["credentials.json"])
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
  """git push のフック検査"""

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
    """dirty な状態の git push は deny"""
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
