"""Codex の未記録過去セッション回収コマンドの単体テスト。"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
CAPTURE = REPO_ROOT / "tools" / "session-record-capture-previous-codex.py"


def _codex_fixture(path, session_id, cwd, text, mtime, extra_meta=None):
  path.parent.mkdir(parents=True, exist_ok=True)
  payload = {
    "id": session_id,
    "timestamp": "2026-06-24T10:00:00.000Z",
    "cwd": cwd,
  }
  if extra_meta:
    payload.update(extra_meta)
  rows = [
    {
      "timestamp": "2026-06-24T10:00:00.000Z",
      "type": "session_meta",
      "payload": payload,
    },
    {
      "timestamp": "2026-06-24T10:00:01.000Z",
      "type": "response_item",
      "payload": {
        "type": "message",
        "role": "user",
        "content": [{"type": "input_text", "text": text}],
      },
    },
  ]
  path.write_text(
    "\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n",
    encoding="utf-8",
  )
  os.utime(path, (mtime, mtime))


class CapturePreviousCodexSessionTests(unittest.TestCase):
  def setUp(self):
    self.tmp = Path(tempfile.mkdtemp())
    self.addCleanup(shutil.rmtree, self.tmp)
    self.codex_root = self.tmp / "codex"
    self.evidence = self.tmp / "evidence"
    self.docs = self.tmp / "docs"
    self.cwd = "/Users/Daily/Development/ReviewCompass"
    self.current_id = "bbbbbbbb-1111-2222-3333-444444444444"
    self.prev_id = "aaaaaaaa-1111-2222-3333-444444444444"
    self.old_id = "99999999-1111-2222-3333-444444444444"

  def _rollout(self, session_id, suffix):
    return (
      self.codex_root
      / "2026"
      / "06"
      / "24"
      / f"rollout-2026-06-24T{suffix}-{session_id}.jsonl"
    )

  def _run(self, extra=None):
    cmd = [
      sys.executable,
      str(CAPTURE),
      "--current-session-id",
      self.current_id,
      "--repo-path",
      self.cwd,
      "--codex-root",
      str(self.codex_root),
      "--evidence-dir",
      str(self.evidence),
      "--docs-dir",
      str(self.docs),
    ]
    if extra:
      cmd += extra
    return subprocess.run(
      cmd,
      cwd=str(REPO_ROOT),
      capture_output=True,
      text=True,
      errors="replace",
      timeout=60,
    )

  def test_captures_latest_unrecorded_previous_session_as_two_layers(self):
    """現在 session_id を除外し、最新の未記録過去セッションだけを 2 層記録する。"""
    _codex_fixture(
      self._rollout(self.old_id, "09-00-00"),
      self.old_id,
      self.cwd,
      "古い過去セッション",
      1000,
    )
    _codex_fixture(
      self._rollout(self.prev_id, "10-00-00"),
      self.prev_id,
      self.cwd,
      "未記録の前セッション",
      2000,
    )
    _codex_fixture(
      self._rollout(self.current_id, "11-00-00"),
      self.current_id,
      self.cwd,
      "現在セッション",
      3000,
    )

    result = self._run()

    self.assertEqual(result.returncode, 0, f"stdout={result.stdout}\nstderr={result.stderr}")
    self.assertTrue(
      (self.evidence / f"2026-06-24-codex-{self.prev_id}.md").exists(),
      "層1 の整形済み転写を作る必要がある",
    )
    self.assertTrue(
      (self.docs / f"auto-2026-06-24-codex-{self.prev_id}.md").exists(),
      "層2 の人間向け記録を作る必要がある",
    )
    self.assertFalse(
      (self.evidence / f"2026-06-24-codex-{self.current_id}.md").exists(),
      "現在セッションは正式記録してはいけない",
    )
    self.assertIn("\"captured\"", result.stdout)
    self.assertIn(self.prev_id, result.stdout)

  def test_skips_current_thread_subsession_and_captures_previous_session(self):
    """現在 thread から派生した subagent session は正式記録せず、過去候補へ進む。"""
    sub_id = "cccccccc-1111-2222-3333-444444444444"
    prev_id = "dddddddd-1111-2222-3333-444444444444"
    _codex_fixture(
      self._rollout(prev_id, "10-00-00"),
      prev_id,
      self.cwd,
      "現セッション配下ではない過去セッション",
      2000,
    )
    _codex_fixture(
      self._rollout(sub_id, "10-30-00"),
      sub_id,
      self.cwd,
      "現在 thread から派生したサブセッション",
      2500,
      extra_meta={
        "session_id": self.current_id,
        "parent_thread_id": self.current_id,
        "thread_source": "subagent",
        "source": {"subagent": {"other": "guardian"}},
      },
    )
    _codex_fixture(
      self._rollout(self.current_id, "11-00-00"),
      self.current_id,
      self.cwd,
      "現在セッション本体",
      3000,
    )

    result = self._run()

    self.assertEqual(result.returncode, 0, f"stdout={result.stdout}\nstderr={result.stderr}")
    self.assertFalse(
      (self.evidence / f"2026-06-24-codex-{sub_id}.md").exists(),
      "現在 thread 派生の subagent session は正式記録してはいけない",
    )
    self.assertTrue(
      (self.evidence / f"2026-06-24-codex-{prev_id}.md").exists(),
      "現在 thread 派生候補を飛ばして、過去セッションを層1 に記録する",
    )
    self.assertTrue(
      (self.docs / f"auto-2026-06-24-codex-{prev_id}.md").exists(),
      "現在 thread 派生候補を飛ばして、過去セッションを層2 に記録する",
    )
    self.assertFalse(
      (self.evidence / f"2026-06-24-codex-{self.current_id}.md").exists(),
      "現在セッション本体は正式記録してはいけない",
    )
    self.assertIn("\"current_session_skipped\"", result.stdout)
    self.assertIn("\"captured\"", result.stdout)
    self.assertIn(prev_id, result.stdout)

  def test_skips_already_recorded_and_captures_next_unrecorded(self):
    """最新候補が記録済みなら、次の未記録過去セッションを回収する。"""
    _codex_fixture(
      self._rollout(self.old_id, "09-00-00"),
      self.old_id,
      self.cwd,
      "未記録の古いセッション",
      1000,
    )
    _codex_fixture(
      self._rollout(self.prev_id, "10-00-00"),
      self.prev_id,
      self.cwd,
      "記録済みの前セッション",
      2000,
    )
    self.evidence.mkdir(parents=True, exist_ok=True)
    self.docs.mkdir(parents=True, exist_ok=True)
    (self.evidence / f"2026-06-24-codex-{self.prev_id}.md").write_text(
      f"session_label: codex-2026-06-24-{self.prev_id}\n",
      encoding="utf-8",
    )
    (self.docs / f"auto-2026-06-24-codex-{self.prev_id}.md").write_text(
      f"session_label: codex-2026-06-24-{self.prev_id}\n",
      encoding="utf-8",
    )

    result = self._run()

    self.assertEqual(result.returncode, 0, f"stdout={result.stdout}\nstderr={result.stderr}")
    self.assertTrue(
      (self.evidence / f"2026-06-24-codex-{self.old_id}.md").exists(),
      "記録済み候補を飛ばして次の未記録セッションを作る必要がある",
    )
    self.assertIn("\"already_recorded\"", result.stdout)
    self.assertIn("\"captured\"", result.stdout)

  def test_list_ignores_mentions_in_other_record_body(self):
    """別セッション本文の ID 言及を、対象 session_id の記録済み表示にしない。"""
    _codex_fixture(
      self._rollout(self.prev_id, "10-00-00"),
      self.prev_id,
      self.cwd,
      "一覧表示対象",
      2000,
    )
    self.evidence.mkdir(parents=True, exist_ok=True)
    self.docs.mkdir(parents=True, exist_ok=True)
    (self.evidence / f"2026-06-24-codex-{self.old_id}.md").write_text(
      "---\n"
      f"session_label: codex-2026-06-24-{self.old_id}\n"
      "layer: transcript\n"
      "---\n"
      f"本文中に {self.prev_id} が出るだけ。\n",
      encoding="utf-8",
    )
    (self.docs / f"auto-2026-06-24-codex-{self.old_id}.md").write_text(
      "---\n"
      f"session_label: codex-2026-06-24-{self.old_id}\n"
      "layer: record\n"
      "---\n"
      f"関連メモとして {self.prev_id} に触れる。\n",
      encoding="utf-8",
    )

    result = self._run(extra=["--list"])

    self.assertEqual(result.returncode, 0, f"stdout={result.stdout}\nstderr={result.stderr}")
    lines = [line for line in result.stdout.splitlines() if line.strip()]
    self.assertTrue(
      any(self.prev_id[:8] in line and "未記録" in line for line in lines),
      f"対象 session_id 自身の正式記録がないため未記録表示が必要。stdout={result.stdout}",
    )
    self.assertFalse(
      any(self.prev_id[:8] in line and "記録済み" in line for line in lines),
      f"本文言及だけで記録済み表示してはいけない。stdout={result.stdout}",
    )

  def test_capture_ignores_mentions_in_other_record_body(self):
    """別セッション本文の ID 言及を、対象 session_id の記録済み扱いにしない。"""
    _codex_fixture(
      self._rollout(self.prev_id, "10-00-00"),
      self.prev_id,
      self.cwd,
      "本文言及だけでは記録済みではない",
      2000,
    )
    self.evidence.mkdir(parents=True, exist_ok=True)
    self.docs.mkdir(parents=True, exist_ok=True)
    (self.evidence / f"2026-06-24-codex-{self.old_id}.md").write_text(
      "---\n"
      f"session_label: codex-2026-06-24-{self.old_id}\n"
      "layer: transcript\n"
      "---\n"
      f"会話本文で {self.prev_id} に言及しただけ。\n",
      encoding="utf-8",
    )
    (self.docs / f"auto-2026-06-24-codex-{self.old_id}.md").write_text(
      "---\n"
      f"session_label: codex-2026-06-24-{self.old_id}\n"
      "layer: record\n"
      "---\n"
      f"関連メモとして {self.prev_id} が登場する。\n",
      encoding="utf-8",
    )

    result = self._run()

    self.assertEqual(result.returncode, 0, f"stdout={result.stdout}\nstderr={result.stderr}")
    self.assertTrue(
      (self.evidence / f"2026-06-24-codex-{self.prev_id}.md").exists(),
      "本文中の偶然の ID 含有ではなく、対象セッション自身の正式記録だけで判定する",
    )
    self.assertNotIn("\"already_recorded\"", result.stdout)
    self.assertIn("\"captured\"", result.stdout)

  def test_dry_run_lists_without_writing(self):
    """dry-run は対象 session_id と記録状態を出し、ファイルは作らない。"""
    _codex_fixture(
      self._rollout(self.prev_id, "10-00-00"),
      self.prev_id,
      self.cwd,
      "dry-run 対象",
      2000,
    )

    result = self._run(extra=["--dry-run"])

    self.assertEqual(result.returncode, 0, f"stdout={result.stdout}\nstderr={result.stderr}")
    self.assertIn("未記録", result.stdout)
    self.assertIn(self.prev_id[:8], result.stdout)
    self.assertFalse(self.evidence.exists() and any(self.evidence.iterdir()))

  def test_list_defaults_to_all_sessions(self):
    """確認リストは既定で対象 repo の全 session_id を表示する。"""
    session_ids = [
      f"dddddddd-1111-2222-3333-44444444444{i}"
      for i in range(12)
    ]
    for index, session_id in enumerate(session_ids):
      _codex_fixture(
        self._rollout(session_id, f"1{index:02d}-00-00"),
        session_id,
        self.cwd,
        f"一覧対象 {index}",
        2000 + index,
      )
    _codex_fixture(
      self._rollout(self.current_id, "199-00-00"),
      self.current_id,
      self.cwd,
      "現在セッション",
      9999,
    )

    result = self._run(extra=["--list"])

    self.assertEqual(result.returncode, 0, f"stdout={result.stdout}\nstderr={result.stderr}")
    lines = [line for line in result.stdout.splitlines() if line.strip()]
    self.assertEqual(len(lines), 14, f"見出し + 全件を表示する。stdout={result.stdout}")
    self.assertIn("日時", lines[0])
    self.assertIn("短縮ID", lines[0])
    self.assertIn("状態", lines[0])
    self.assertTrue(
      any("現在" in line and self.current_id[:8] in line for line in lines[1:]),
      f"現在セッション行が必要。stdout={result.stdout}",
    )
    self.assertFalse(self.evidence.exists() and any(self.evidence.iterdir()))

  def test_list_orders_by_timestamp_descending(self):
    """確認リストは日時の降順で表示する。"""
    for index in [2, 0, 1]:
      session_id = f"ffffffff-1111-2222-3333-44444444444{index}"
      _codex_fixture(
        self._rollout(session_id, f"1{index}-00-00"),
        session_id,
        self.cwd,
        f"降順 {index}",
        2000 + index,
      )

    result = self._run(extra=["--list"])

    self.assertEqual(result.returncode, 0, f"stdout={result.stdout}\nstderr={result.stderr}")
    lines = [line for line in result.stdout.splitlines() if line.strip()]
    self.assertIn("4442", lines[1])
    self.assertIn("4441", lines[2])
    self.assertIn("4440", lines[3])

  def test_list_recent_limits_to_latest_n_sessions_in_descending_order(self):
    """--recent N は直近 N 件を日時降順で表示する。"""
    for index in range(5):
      session_id = f"eeeeeeee-1111-2222-3333-44444444444{index}"
      _codex_fixture(
        self._rollout(session_id, f"1{index}-00-00"),
        session_id,
        self.cwd,
        f"直近制限 {index}",
        2000 + index,
      )

    result = self._run(extra=["--list", "--recent", "2"])

    self.assertEqual(result.returncode, 0, f"stdout={result.stdout}\nstderr={result.stderr}")
    lines = [line for line in result.stdout.splitlines() if line.strip()]
    self.assertEqual(len(lines), 3, f"見出し + 2 件を表示する。stdout={result.stdout}")
    self.assertIn("eeeeeeee", lines[1])
    self.assertIn("4444", lines[1])
    self.assertIn("eeeeeeee", lines[2])
    self.assertIn("4443", lines[2])

  def test_jsonl_format_keeps_machine_readable_list(self):
    """--format jsonl なら従来どおり機械処理用 JSONL で一覧を出す。"""
    _codex_fixture(
      self._rollout(self.prev_id, "10-00-00"),
      self.prev_id,
      self.cwd,
      "jsonl 対象",
      2000,
    )

    result = self._run(extra=["--list", "--format", "jsonl"])

    self.assertEqual(result.returncode, 0, f"stdout={result.stdout}\nstderr={result.stderr}")
    rows = [json.loads(line) for line in result.stdout.splitlines() if line.strip()]
    self.assertEqual(rows[0]["event"], "would_capture")
    self.assertEqual(rows[0]["session_id"], self.prev_id)

  def test_manual_capture_defaults_to_at_most_five_unrecorded_sessions(self):
    """手動実行は未記録過去セッションを最大 5 件まで連続回収する。"""
    session_ids = [
      f"aaaaaaaa-1111-2222-3333-44444444444{i}"
      for i in range(6)
    ]
    for index, session_id in enumerate(session_ids):
      _codex_fixture(
        self._rollout(session_id, f"1{index}-00-00"),
        session_id,
        self.cwd,
        f"未記録セッション {index}",
        2000 + index,
      )

    result = self._run()

    self.assertEqual(result.returncode, 0, f"stdout={result.stdout}\nstderr={result.stderr}")
    captured = [
      json.loads(line)["session_id"]
      for line in result.stdout.splitlines()
      if line.strip() and json.loads(line).get("event") == "captured"
    ]
    self.assertEqual(len(captured), 5, f"既定上限は 5 件。stdout={result.stdout}")
    for session_id in captured:
      self.assertTrue(
        (self.evidence / f"2026-06-24-codex-{session_id}.md").exists(),
        f"{session_id} の層1 が必要",
      )

  def test_max_count_limits_capture_count(self):
    """--max-count で手動回収件数を制限できる。"""
    for index in range(3):
      session_id = f"cccccccc-1111-2222-3333-44444444444{index}"
      _codex_fixture(
        self._rollout(session_id, f"1{index}-00-00"),
        session_id,
        self.cwd,
        f"上限制御 {index}",
        2000 + index,
      )

    result = self._run(extra=["--max-count", "2"])

    self.assertEqual(result.returncode, 0, f"stdout={result.stdout}\nstderr={result.stderr}")
    self.assertEqual(
      sum(
        1
        for line in result.stdout.splitlines()
        if line.strip() and json.loads(line).get("event") == "captured"
      ),
      2,
      f"--max-count 2 なら 2 件だけ回収する。stdout={result.stdout}",
    )


if __name__ == "__main__":
  unittest.main()
