"""tools/make-commit-approval.py の単体テスト。

「事例より正本」改善（案2）：commit 承認レコードを過去事例から手で写すのをやめ、
正本（check-workflow-action.py の validate_commit_approval /
validate_commit_execution_delegation）が受け入れる形をツールで生成する。

テストは生成物を**正本の検証関数**に通して合格することを確認する（固定の期待文字列でなく、
正本の判定に対する検証）。TDD 規律に従い実装前に作成。
実行：
  cd /Users/Daily/Development/ReviewCompass
  python3 -m unittest tests.tools.test_make_commit_approval -v
"""

import importlib.util
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
TOOL = REPO_ROOT / "tools" / "make-commit-approval.py"


def _load_cwa():
  """正本 check-workflow-action.py を読み込む（importlib・既存テストと同手口）。"""
  tools_dir = str(REPO_ROOT / "tools")
  if tools_dir not in sys.path:
    sys.path.insert(0, tools_dir)
  spec = importlib.util.spec_from_file_location(
    "cwa_under_test_make_commit_approval",
    REPO_ROOT / "tools" / "check-workflow-action.py")
  m = importlib.util.module_from_spec(spec)
  spec.loader.exec_module(m)
  return m


def _init_repo(tmp):
  for cmd in [
    ["git", "init", "-q", "-b", "main"],
    ["git", "config", "user.email", "t@example.com"],
    ["git", "config", "user.name", "T"],
  ]:
    subprocess.run(cmd, cwd=tmp, check=True, capture_output=True)


def _stage(tmp, rel, content):
  p = Path(tmp) / rel
  p.parent.mkdir(parents=True, exist_ok=True)
  p.write_text(content, encoding="utf-8")
  subprocess.run(["git", "add", rel], cwd=tmp, check=True, capture_output=True)


def _run_tool(tmp, *args):
  return subprocess.run(
    [sys.executable, str(TOOL), *args],
    cwd=tmp, capture_output=True, text=True, errors="replace", timeout=30)


class MakeCommitApprovalTests(unittest.TestCase):
  def setUp(self):
    self.tmp = tempfile.mkdtemp()
    self.addCleanup(shutil.rmtree, self.tmp)
    _init_repo(self.tmp)
    self.cwa = _load_cwa()

  def test_generated_record_passes_canonical_validators(self):
    """生成した承認レコードが正本の検証関数を所見0で通る。"""
    _stage(self.tmp, "notes.md", "# メモ")
    r = _run_tool(self.tmp, "--explicit-instruction", "コミット",
                  "--rationale", "利用者『コミット』")
    self.assertEqual(r.returncode, 0, f"stdout={r.stdout}\nstderr={r.stderr}")
    state, errors = self.cwa.validate_commit_approval(self.tmp, ["notes.md"])
    self.assertEqual(errors, [], f"正本 validate_commit_approval が不合格: {errors}")
    deleg_errors = self.cwa.validate_commit_execution_delegation(state, "llm")
    self.assertEqual(deleg_errors, [], f"正本 execution_delegation 検証が不合格: {deleg_errors}")

  def test_covers_all_staged_files(self):
    """複数 staged ファイルを全て target_files に含め、正本検証を通る。"""
    _stage(self.tmp, "a.md", "a")
    _stage(self.tmp, "b.md", "b")
    r = _run_tool(self.tmp, "--explicit-instruction", "コミット", "--rationale", "x")
    self.assertEqual(r.returncode, 0, f"stdout={r.stdout}\nstderr={r.stderr}")
    _state, errors = self.cwa.validate_commit_approval(self.tmp, ["a.md", "b.md"])
    self.assertEqual(errors, [], f"正本検証が不合格: {errors}")

  def test_bad_instruction_is_refused(self):
    """正本の実行代行述語を通らない指示は拒否する（fail-closed）。"""
    _stage(self.tmp, "notes.md", "# メモ")
    r = _run_tool(self.tmp, "--explicit-instruction", "やめて", "--rationale", "x")
    self.assertNotEqual(r.returncode, 0,
                        "正本述語を通らない指示は拒否すべき")
    approval = Path(self.tmp) / ".reviewcompass/runtime/approvals/commit-approval.json"
    self.assertFalse(approval.exists(), "拒否時は承認レコードを残さない")

  def test_no_staged_files_is_error(self):
    """staged ファイルが無ければエラー（非ゼロ）。"""
    r = _run_tool(self.tmp, "--explicit-instruction", "コミット", "--rationale", "x")
    self.assertNotEqual(r.returncode, 0, f"stdout={r.stdout}\nstderr={r.stderr}")

  def test_deleted_file_passes_canonical_validators(self):
    """削除ファイルを含む staged で正本検証を通る。"""
    # ファイルを作成してコミット済みにする
    _stage(self.tmp, "delete_me.md", "# 削除予定")
    subprocess.run(
      ["git", "commit", "-qm", "add", "--allow-empty-message"],
      cwd=self.tmp, check=True, capture_output=True,
    )
    # ファイルを削除してステージ
    subprocess.run(
      ["git", "rm", "-q", "delete_me.md"],
      cwd=self.tmp, check=True, capture_output=True,
    )
    r = _run_tool(self.tmp, "--explicit-instruction", "コミット", "--rationale", "削除テスト")
    self.assertEqual(r.returncode, 0,
                     f"削除ファイルがある staged でも承認レコードを生成できるはず\n"
                     f"stdout={r.stdout}\nstderr={r.stderr}")
    state, errors = self.cwa.validate_commit_approval(self.tmp, ["delete_me.md"])
    self.assertEqual(errors, [],
                     f"正本 validate_commit_approval が不合格: {errors}\n{r.stdout}")


if __name__ == "__main__":
  unittest.main()
