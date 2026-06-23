"""Codex SessionEnd hook .codex/hooks/session-record-capture-current-on-session-end.sh の単体テスト。

セッション会話記録は TODO 更新をトリガーにせず、セッション境界で渡される
current session_id と cwd から当該 rollout を 1 件だけ機械選択して正式記録へ取り込む。
"""

import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
HOOK = REPO_ROOT / ".codex" / "hooks" / "session-record-capture-current-on-session-end.sh"


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
  for item in texts:
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


def _run_hook(payload, evidence_dir, docs_dir, codex_root, log_path):
  env = dict(os.environ)
  env["RC_SESSION_EVIDENCE_DIR"] = str(evidence_dir)
  env["RC_SESSION_DOCS_DIR"] = str(docs_dir)
  env["RC_SESSION_CAPTURE_HOOK_LOG"] = str(log_path)
  env["CODEX_SESSIONS_ROOT"] = str(codex_root)
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
  if not path.exists():
    return []
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


class CodexCaptureCurrentOnSessionEndTests(unittest.TestCase):
  def setUp(self):
    self.tmp = Path(tempfile.mkdtemp())
    self.addCleanup(shutil.rmtree, self.tmp)
    self.evidence = self.tmp / "ev"
    self.docs = self.tmp / "dc"
    self.log = self.tmp / "hook.log.jsonl"
    self.codex_root = self.tmp / "codex"
    self.cwd = str(self.tmp / "repo")
    self.repo = Path(self.cwd)
    self.repo.mkdir()
    self.todo = self.repo / "TODO_NEXT_SESSION.md"
    self.session_id = "cccccccc-1111-2222-3333-444444444444"
    self.other_id = "bbbbbbbb-1111-2222-3333-444444444444"
    self.rollout = (
      self.codex_root
      / "2026"
      / "06"
      / "15"
      / "rollout-2026-06-15T12-00-00-cccccccc-1111-2222-3333-444444444444.jsonl"
    )

  def _payload(self, event="SessionEnd", session_id=None, reason="clear"):
    return {
      "hook_event_name": event,
      "session_id": session_id if session_id is not None else self.session_id,
      "cwd": self.cwd,
      "reason": reason,
    }

  def test_session_end_captures_current_session_by_session_id_and_cwd(self):
    """SessionEnd で current session_id/cwd に一致する rollout だけを正式記録へ取り込む。"""
    _codex_fixture(
      self.rollout,
      self.session_id,
      self.cwd,
      "現 Codex セッション",
      mtime=3000,
    )
    _codex_fixture(
      self.codex_root
      / "2026"
      / "06"
      / "15"
      / "rollout-2026-06-15T11-00-00-bbbbbbbb-1111-2222-3333-444444444444.jsonl",
      self.other_id,
      self.cwd,
      "別 Codex セッション",
      mtime=4000,
    )

    result = _run_hook(
      self._payload(),
      self.evidence,
      self.docs,
      self.codex_root,
      self.log,
    )

    _assert_invoked(self, result)
    self.assertEqual(result.returncode, 0, f"stdout={result.stdout}\nstderr={result.stderr}")
    self.assertTrue(
      (self.evidence / f"2026-06-15-codex-{self.session_id}.md").exists(),
      "current session_id に一致する正式 evidence を作る必要がある",
    )
    self.assertTrue(
      (self.docs / f"auto-2026-06-15-codex-{self.session_id}.md").exists(),
      "current session_id に一致する docs/sessions 記録を作る必要がある",
    )
    self.assertFalse(
      (self.evidence / f"2026-06-15-codex-{self.other_id}.md").exists(),
      "別 session_id を誤回収してはいけない",
    )
    self.assertEqual(
      ["selected", "captured"],
      [event["event"] for event in _events(self.log)],
    )

  def test_todo_post_tool_use_is_not_a_capture_trigger(self):
    """TODO 更新はセッション記録の取り込みトリガーではない。"""
    self.todo.write_text("handoff v1\n", encoding="utf-8")
    _codex_fixture(self.rollout, self.session_id, self.cwd, "現 Codex セッション", 3000)
    payload = {
      "hook_event_name": "PostToolUse",
      "tool_name": "Edit",
      "tool_input": {"file_path": str(self.todo)},
      "session_id": self.session_id,
      "cwd": self.cwd,
    }

    result = _run_hook(payload, self.evidence, self.docs, self.codex_root, self.log)

    _assert_invoked(self, result)
    self.assertEqual(result.returncode, 0, f"stderr={result.stderr}")
    self.assertFalse(self.evidence.exists() and any(self.evidence.iterdir()))
    self.assertFalse(self.docs.exists() and any(self.docs.iterdir()))
    self.assertEqual(["ignored_event"], [event["event"] for event in _events(self.log)])

  def test_missing_session_id_does_not_guess_current_session(self):
    """並行セッション誤回収を避けるため、session_id 無しでは最新 rollout を推測しない。"""
    _codex_fixture(self.rollout, self.session_id, self.cwd, "現 Codex セッション", 3000)

    result = _run_hook(
      self._payload(session_id=""),
      self.evidence,
      self.docs,
      self.codex_root,
      self.log,
    )

    _assert_invoked(self, result)
    self.assertEqual(result.returncode, 0, f"stderr={result.stderr}")
    self.assertFalse(self.evidence.exists() and any(self.evidence.iterdir()))
    self.assertEqual(["no_current_session_id"], [event["event"] for event in _events(self.log)])

  def test_auto_compact_session_end_is_not_captured(self):
    """中間的な SessionEnd はセッション境界として扱わない。"""
    _codex_fixture(self.rollout, self.session_id, self.cwd, "現 Codex セッション", 3000)

    result = _run_hook(
      self._payload(reason="auto_compact"),
      self.evidence,
      self.docs,
      self.codex_root,
      self.log,
    )

    _assert_invoked(self, result)
    self.assertEqual(result.returncode, 0, f"stderr={result.stderr}")
    self.assertFalse(self.evidence.exists() and any(self.evidence.iterdir()))
    self.assertEqual(["non_final_session_end"], [event["event"] for event in _events(self.log)])


if __name__ == "__main__":
  unittest.main()
