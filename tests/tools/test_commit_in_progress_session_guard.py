"""commit 事前検査の歯止め：進行中セッションの記録はコミットさせない（強制コード）。

背景：会話ログの2層記録は、元の会話ログ（jsonl）から機械生成され、frontmatter に
source_path と source_sha256（生成時の元ログのハッシュ）を刻む。まだ終わっていない
セッションを途中で記録すると、後で会話が伸びて取り込み直し＝差分のたまり（churn）に
なる。これを「コミット時に手で除外する」のは守り忘れの温床なので、コミット前検査で
機械的に弾く。判定は「staged のセッション記録の source_sha256 が、いまの元ログの
ハッシュと一致するか」。一致しなければ元ログは生成後に変化＝まだ進行中とみなす。

TDD 規律（AGENTS.md 入口規律）に従い、本テストは実装前に作成する。
実行：
  cd /Users/Daily/Development/ReviewCompass
  python3 -m unittest tests.tools.test_commit_in_progress_session_guard -v
"""

import hashlib
import shutil
import tempfile
import unittest
from pathlib import Path

from tests.tools.test_check_workflow_action import (
  _init_git_repo,
  _set_pending_findings,
  _stage_file,
  _write_commit_approval,
  run_script,
)


GUARD_MSG = "進行中セッションの記録はコミットできません"


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


class CommitInProgressSessionGuardTests(unittest.TestCase):
  def setUp(self):
    self.tmpdir = tempfile.mkdtemp()
    self.addCleanup(shutil.rmtree, self.tmpdir)
    self.pending_file = _init_git_repo(self.tmpdir)
    _set_pending_findings(self.pending_file, unresolved_count=0, resolved_count=2)
    # 元の会話ログ（jsonl）を repo 外相当の絶対パスに用意
    self.src = Path(self.tmpdir) / "src-logs" / "testsess.jsonl"
    self.src.parent.mkdir(parents=True, exist_ok=True)
    self.src.write_bytes(b'{"type":"user","content":"hi"}\n')
    self.src_sha = hashlib.sha256(self.src.read_bytes()).hexdigest()
    self.record_rel = (
      ".reviewcompass/evidence/sessions/2026-06-14-claude-testsess.md"
    )

  def _stage_record(self):
    _stage_file(
      self.tmpdir, self.record_rel,
      _record_text(str(self.src), self.src_sha))
    _write_commit_approval(self.tmpdir, [self.record_rel])

  def test_in_progress_record_is_blocked(self):
    """元ログが生成後に変化（進行中）したセッション記録は exit 2 で弾く。"""
    self._stage_record()
    # 記録を作った後に元ログが伸びた＝まだ進行中
    with open(self.src, "ab") as f:
      f.write(b'{"type":"assistant","content":"more"}\n')
    r = run_script(["commit", "--rationale", "進行中記録の遮断テスト"],
                   cwd=self.tmpdir)
    self.assertEqual(r.returncode, 2,
                     f"進行中記録は遮断すべき。\nstdout={r.stdout}\nstderr={r.stderr}")
    self.assertIn(GUARD_MSG, r.stdout, f"遮断理由が必要。stdout={r.stdout}")
    self.assertIn(self.record_rel, r.stdout, "対象ファイル名を示すべき")

  def test_finished_record_is_allowed(self):
    """元ログが生成時から不変（終了済み）なら、この歯止めは作動しない。"""
    self._stage_record()  # 元ログは変えない
    r = run_script(["commit", "--rationale", "終了済み記録の通過テスト"],
                   cwd=self.tmpdir)
    self.assertNotIn(GUARD_MSG, r.stdout,
                     f"終了済みは歯止めの対象外。stdout={r.stdout}")

  def test_missing_source_is_not_blocked(self):
    """元ログが見つからない（判定不能）は弾かない（過剰遮断しない）。"""
    _stage_file(
      self.tmpdir, self.record_rel,
      _record_text(str(self.src) + ".does-not-exist", self.src_sha))
    _write_commit_approval(self.tmpdir, [self.record_rel])
    r = run_script(["commit", "--rationale", "判定不能は通すテスト"],
                   cwd=self.tmpdir)
    self.assertNotIn(GUARD_MSG, r.stdout,
                     f"判定不能は弾かない。stdout={r.stdout}")


if __name__ == "__main__":
  unittest.main()
