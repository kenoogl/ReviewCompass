"""Codex TODO 更新 hook .codex/hooks/session-record-capture-current-on-todo.sh の単体テスト。

Codex では UserPromptSubmit を使わず、TODO_NEXT_SESSION.md の更新を合図に
現セッション rollout を runtime 下書きへ保存する。TODO は 1 セッション内で複数回更新
されるため、内容 hash が変わるたびに同じ下書きを更新し、伸びた分だけ反映する。
"""

import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
HOOK = REPO_ROOT / ".codex" / "hooks" / "session-record-capture-current-on-todo.sh"


def _codex_fixture(path, session_id, cwd, text, mtime):
  path.parent.mkdir(parents=True, exist_ok=True)
  texts = text if isinstance(text, list) else [text]
  rows = [
    {
      "timestamp": "2026-06-15T10:00:00.000Z",
      "type": "session_meta",
      "payload": {
        "id": session_id,
        "timestamp": "2026-06-15T10:00:00.000Z",
        "cwd": cwd,
      },
    },
  ]
  for index, item in enumerate(texts, start=1):
    rows.append({
      "timestamp": "2026-06-15T10:00:01.000Z",
      "type": "response_item",
      "payload": {
        "type": "message",
        "role": "user",
        "content": [{"type": "input_text", "text": item}],
      },
    })
  body = "\n".join(json.dumps(o, ensure_ascii=False) for o in rows) + "\n"
  path.write_text(body, encoding="utf-8")
  os.utime(path, (mtime, mtime))


def _run_hook(payload, evidence_dir, docs_dir, draft_dir, home):
  env = dict(os.environ)
  env["RC_SESSION_EVIDENCE_DIR"] = str(evidence_dir)
  env["RC_SESSION_DOCS_DIR"] = str(docs_dir)
  env["RC_SESSION_DRAFT_DIR"] = str(draft_dir)
  env["RC_SESSION_HOOK_LOG"] = str(evidence_dir.parent / "hook.log.jsonl")
  env["RC_SESSION_HOOK_STATE_DIR"] = str(evidence_dir.parent / "state")
  env["HOME"] = str(home)
  return subprocess.run(
    ["bash", str(HOOK)],
    input=json.dumps(payload),
    cwd=str(REPO_ROOT),
    capture_output=True,
    text=True,
    errors="replace",
    timeout=60,
    env=env,
  )


def _events(path):
  return [
    json.loads(line)
    for line in path.read_text(encoding="utf-8").splitlines()
    if line.strip()
  ]


def _assert_invoked(testcase, result):
  for marker in ("No such file or directory", "command not found"):
    testcase.assertNotIn(
      marker,
      result.stderr,
      f"フック未起動（実装前か）。stderr={result.stderr}",
    )


class CodexCaptureCurrentOnTodoTests(unittest.TestCase):
  def setUp(self):
    self.tmp = Path(tempfile.mkdtemp())
    self.addCleanup(shutil.rmtree, self.tmp)
    self.evidence = self.tmp / "ev"
    self.docs = self.tmp / "dc"
    self.drafts = self.tmp / "drafts"
    self.log = self.tmp / "hook.log.jsonl"
    self.home = self.tmp / "home"
    self.cwd = str(self.tmp / "repo")
    self.repo = Path(self.cwd)
    self.repo.mkdir()
    self.todo = self.repo / "TODO_NEXT_SESSION.md"
    self.sessions = self.home / ".codex" / "sessions" / "2026" / "06" / "15"
    self.session_id = "cccccccc-1111-2222-3333-444444444444"
    self.rollout = (
      self.sessions
      / "rollout-2026-06-15T12-00-00-cccccccc-1111-2222-3333-444444444444.jsonl"
    )

  def _payload(self, tool_name="Edit", file_path="TODO_NEXT_SESSION.md", session_id=None):
    return {
      "hook_event_name": "PostToolUse",
      "tool_name": tool_name,
      "tool_input": {"file_path": str(self.repo / file_path)},
      "session_id": session_id or self.session_id,
      "cwd": self.cwd,
    }

  def test_drafts_current_session_when_todo_update_is_observed(self):
    """TODO 更新を合図に、前セッションではなく現セッションを下書き保存する。"""
    self.todo.write_text("handoff v1\n", encoding="utf-8")
    _codex_fixture(
      self.rollout,
      self.session_id,
      self.cwd,
      "現 Codex セッション",
      mtime=3000,
    )
    _codex_fixture(
      self.sessions / "rollout-2026-06-15T11-00-00-bbbbbbbb-1111-2222-3333-444444444444.jsonl",
      "bbbbbbbb-1111-2222-3333-444444444444",
      self.cwd,
      "前 Codex セッション",
      mtime=2000,
    )

    result = _run_hook(self._payload(), self.evidence, self.docs, self.drafts, self.home)

    _assert_invoked(self, result)
    self.assertEqual(result.returncode, 0, f"stdout={result.stdout}\nstderr={result.stderr}")
    self.assertTrue(
      (self.drafts / "codex-cccccccc-1111-2222-3333-444444444444.md").exists(),
      "現セッションを runtime 下書きへ保存する必要がある",
    )
    self.assertFalse(
      self.evidence.exists() and any(self.evidence.iterdir()),
      "TODO 更新 hook は正式 evidence を直接生成しない",
    )
    self.assertFalse(
      self.docs.exists() and any(self.docs.iterdir()),
      "TODO 更新 hook は docs/sessions を直接生成しない",
    )
    self.assertEqual(
      ["todo_changed", "selected", "drafted"],
      [event["event"] for event in _events(self.log)],
    )

  def test_todo_changes_are_captured_each_time(self):
    """TODO が複数回更新されたら、そのたび現セッションを再取り込みする。"""
    self.todo.write_text("handoff v1\n", encoding="utf-8")
    _codex_fixture(self.rollout, self.session_id, self.cwd, "現 Codex セッション v1", 3000)

    first = _run_hook(self._payload(), self.evidence, self.docs, self.drafts, self.home)
    self.todo.write_text("handoff v2\n", encoding="utf-8")
    _codex_fixture(
      self.rollout,
      self.session_id,
      self.cwd,
      ["現 Codex セッション v1", "現 Codex セッション v2"],
      4000,
    )
    second = _run_hook(self._payload(), self.evidence, self.docs, self.drafts, self.home)

    _assert_invoked(self, first)
    _assert_invoked(self, second)
    self.assertEqual(first.returncode, 0, f"stderr={first.stderr}")
    self.assertEqual(second.returncode, 0, f"stderr={second.stderr}")
    transcript = (
      self.drafts / "codex-cccccccc-1111-2222-3333-444444444444.md"
    ).read_text(encoding="utf-8")
    self.assertIn("現 Codex セッション v2", transcript)
    self.assertEqual(
      ["todo_changed", "selected", "drafted", "todo_changed", "selected", "drafted"],
      [event["event"] for event in _events(self.log)],
    )

  def test_first_non_todo_tool_only_records_baseline(self):
    """初回に TODO 更新の痕跡が無い場合、dirty な TODO を誤回収せず baseline だけ残す。"""
    self.todo.write_text("already dirty before hook\n", encoding="utf-8")
    _codex_fixture(self.rollout, self.session_id, self.cwd, "現 Codex セッション", 3000)

    first = _run_hook(
      self._payload(tool_name="Bash", file_path="README.md"),
      self.evidence,
      self.docs,
      self.drafts,
      self.home,
    )
    second = _run_hook(
      self._payload(tool_name="Bash", file_path="README.md"),
      self.evidence,
      self.docs,
      self.drafts,
      self.home,
    )

    _assert_invoked(self, first)
    _assert_invoked(self, second)
    self.assertFalse(
      self.evidence.exists() and any(self.evidence.iterdir()),
      "既に dirty な TODO を初回の無関係 tool で誤回収しない",
    )
    self.assertEqual(
      ["baseline_recorded", "todo_unchanged"],
      [event["event"] for event in _events(self.log)],
    )

  def test_user_prompt_submit_is_ignored_even_if_todo_is_dirty(self):
    """UserPromptSubmit は使用禁止。TODO が dirty でも回収しない。"""
    self.todo.write_text("handoff v1\n", encoding="utf-8")
    _codex_fixture(self.rollout, self.session_id, self.cwd, "現 Codex セッション", 3000)
    payload = {
      "hook_event_name": "UserPromptSubmit",
      "session_id": self.session_id,
      "cwd": self.cwd,
    }

    result = _run_hook(payload, self.evidence, self.docs, self.drafts, self.home)

    _assert_invoked(self, result)
    self.assertEqual(result.returncode, 0, f"stderr={result.stderr}")
    self.assertFalse(self.evidence.exists() and any(self.evidence.iterdir()))
    self.assertEqual(["ignored_event"], [event["event"] for event in _events(self.log)])

  def test_missing_session_id_does_not_guess_current_session(self):
    """並行セッション誤回収を避けるため、session_id 無しでは最新 rollout を推測しない。"""
    self.todo.write_text("handoff v1\n", encoding="utf-8")
    _codex_fixture(self.rollout, self.session_id, self.cwd, "現 Codex セッション", 3000)
    payload = self._payload(session_id="")
    payload["session_id"] = ""

    result = _run_hook(payload, self.evidence, self.docs, self.drafts, self.home)

    _assert_invoked(self, result)
    self.assertEqual(result.returncode, 0, f"stderr={result.stderr}")
    self.assertFalse(self.evidence.exists() and any(self.evidence.iterdir()))
    self.assertEqual(["todo_changed", "no_session_id"], [event["event"] for event in _events(self.log)])


if __name__ == "__main__":
  unittest.main()
