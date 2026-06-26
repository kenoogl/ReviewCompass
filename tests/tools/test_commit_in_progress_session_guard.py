"""commit 事前検査：セッション記録はスナップショットとしてコミット可能。

背景：会話ログの2層記録は、元の会話ログ（jsonl）から機械生成され、frontmatter に
source_path と source_sha256（生成時の元ログのハッシュ）を刻む。進行中セッションの
記録もスナップショットとしてコミット可能。後で会話が伸びた場合は再取り込みして
上書き更新する（backfill.py の classify_update で重複を防ぐ）。

TDD 規律（AGENTS.md 入口規律）に従う。
実行：
  cd /Users/Daily/Development/ReviewCompass
  python3 -m unittest tests.tools.test_commit_in_progress_session_guard -v
"""

import hashlib
import json
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

  def test_in_progress_record_is_allowed_as_snapshot(self):
    """元ログが生成後に変化（進行中）したセッション記録もスナップショットとしてコミット可能。"""
    self._stage_record()
    # 記録を作った後に元ログが伸びた（進行中）
    with open(self.src, "ab") as f:
      f.write(b'{"type":"assistant","content":"more"}\n')
    r = run_script(["commit", "--rationale", "進行中記録のスナップショットテスト"],
                   cwd=self.tmpdir)
    self.assertNotIn(GUARD_MSG, r.stdout,
                     f"進行中記録もコミット可能なはず。stdout={r.stdout}")

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

  def test_stage_command_includes_in_progress_record(self):
    """stage helper は進行中セッション記録もスナップショットとして stage 対象に含める。"""
    record_path = Path(self.tmpdir) / self.record_rel
    record_path.parent.mkdir(parents=True, exist_ok=True)
    record_path.write_text(_record_text(str(self.src), self.src_sha))
    with open(self.src, "ab") as f:
      f.write(b'{"type":"assistant","content":"more"}\n')
    normal_path = Path(self.tmpdir) / "notes.md"
    normal_path.write_text("# 通常ファイル\n")

    r = run_script(["stage", ".", "--json"], cwd=self.tmpdir)

    self.assertEqual(r.returncode, 0, f"stage helper should pass. stdout={r.stdout}")
    payload = json.loads(r.stdout)
    self.assertIn("notes.md", payload["staged"])
    self.assertNotIn(self.record_rel, payload.get("excluded_in_progress_records", []))


if __name__ == "__main__":
  unittest.main()
