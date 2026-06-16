"""Codex SessionStart hook の前セッション正式昇格テスト。

Codex の TODO hook は現セッションを runtime 下書きへ保存する。
新しい Codex セッション開始時には、現 session_id と異なる最新下書きを
正式 2 層記録へ昇格する。
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
HOOK = REPO_ROOT / ".codex" / "hooks" / "session-record-promote-previous-draft.sh"
DRAFT_TOOL = REPO_ROOT / "tools" / "session-record-draft.py"


def _codex_fixture(path, session_id, cwd, text, mtime):
  path.parent.mkdir(parents=True, exist_ok=True)
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
    {
      "timestamp": "2026-06-15T10:00:01.000Z",
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


def _sha256(path):
  import hashlib

  return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _draft_fixture(path, session_id, mtime, source_sha256="draft-sha"):
  path.parent.mkdir(parents=True, exist_ok=True)
  path.write_text(
    "---\n"
    "source: codex\n"
    f"session_id: {session_id}\n"
    "layer: draft\n"
    f"source_sha256: {source_sha256}\n"
    "---\n"
    "\n"
    "draft\n",
    encoding="utf-8",
  )
  os.utime(path, (mtime, mtime))


def _run_hook(payload, evidence_dir, docs_dir, draft_dir, codex_root, log_path, extra_env=None):
  env = dict(os.environ)
  env["RC_SESSION_EVIDENCE_DIR"] = str(evidence_dir)
  env["RC_SESSION_DOCS_DIR"] = str(docs_dir)
  env["RC_SESSION_DRAFT_DIR"] = str(draft_dir)
  env["CODEX_SESSIONS_ROOT"] = str(codex_root)
  env["RC_SESSION_PROMOTE_HOOK_LOG"] = str(log_path)
  env["REVIEWCOMPASS_PYTHON"] = sys.executable
  if extra_env:
    env.update(extra_env)
  return subprocess.run(
    ["/bin/bash", str(HOOK)],
    input=json.dumps(payload),
    cwd=str(REPO_ROOT),
    capture_output=True,
    text=True,
    errors="replace",
    timeout=60,
    env=env,
  )


def _run_draft_tool(session_path, draft_dir):
  return subprocess.run(
    [
      sys.executable,
      str(DRAFT_TOOL),
      "--session",
      str(session_path),
      "--source",
      "codex",
      "--draft-dir",
      str(draft_dir),
    ],
    cwd=str(REPO_ROOT),
    capture_output=True,
    text=True,
    errors="replace",
    timeout=60,
  )


def _events(path):
  if not path.exists():
    return []
  return [
    json.loads(line)["event"]
    for line in path.read_text(encoding="utf-8").splitlines()
    if line.strip()
  ]


class CodexPromotePreviousDraftHookTests(unittest.TestCase):
  def setUp(self):
    self.tmp = Path(tempfile.mkdtemp())
    self.addCleanup(shutil.rmtree, self.tmp)
    self.evidence = self.tmp / "evidence"
    self.docs = self.tmp / "docs"
    self.drafts = self.tmp / "drafts"
    self.codex_root = self.tmp / "codex"
    self.log_path = self.tmp / "promote.jsonl"
    self.cwd = "/Users/Daily/Development/ReviewCompass"
    self.prev_id = "aaaaaaaa-1111-2222-3333-444444444444"
    self.current_id = "bbbbbbbb-1111-2222-3333-444444444444"
    self.old_id = "cccccccc-1111-2222-3333-444444444444"

  def _rollout(self, session_id, suffix="10-00-00"):
    return (
      self.codex_root
      / "2026"
      / "06"
      / "15"
      / f"rollout-2026-06-15T{suffix}-{session_id}.jsonl"
    )

  def _payload(self, session_id=None):
    return {
      "hook_event_name": "SessionStart",
      "session_id": session_id or self.current_id,
      "cwd": self.cwd,
      "source": "startup",
    }

  def test_promotes_latest_non_current_draft_on_session_start(self):
    """SessionStart で現セッション以外の最新下書きだけを正式化する。"""
    _codex_fixture(self._rollout(self.old_id), self.old_id, self.cwd, "古い下書き", 1000)
    _codex_fixture(self._rollout(self.prev_id), self.prev_id, self.cwd, "前セッション", 2000)
    _codex_fixture(self._rollout(self.current_id), self.current_id, self.cwd, "現セッション", 3000)
    _draft_fixture(
      self.drafts / f"codex-{self.old_id}.md",
      self.old_id,
      1000,
      _sha256(self._rollout(self.old_id)),
    )
    _draft_fixture(
      self.drafts / f"codex-{self.prev_id}.md",
      self.prev_id,
      2000,
      _sha256(self._rollout(self.prev_id)),
    )
    _draft_fixture(
      self.drafts / f"codex-{self.current_id}.md",
      self.current_id,
      3000,
      _sha256(self._rollout(self.current_id)),
    )

    result = _run_hook(
      self._payload(),
      self.evidence,
      self.docs,
      self.drafts,
      self.codex_root,
      self.log_path,
    )

    self.assertEqual(result.returncode, 0, f"stdout={result.stdout}\nstderr={result.stderr}")
    self.assertTrue(
      (self.evidence / f"2026-06-15-codex-{self.prev_id}.md").exists(),
      "前セッション下書きを正式層1へ昇格する必要がある",
    )
    self.assertTrue(
      (self.docs / f"auto-2026-06-15-codex-{self.prev_id}.md").exists(),
      "前セッション下書きを正式層2へ昇格する必要がある",
    )
    self.assertFalse(
      (self.evidence / f"2026-06-15-codex-{self.current_id}.md").exists(),
      "現セッションは正式化してはいけない",
    )
    self.assertFalse(
      (self.evidence / f"2026-06-15-codex-{self.old_id}.md").exists(),
      "最新より古い下書きはこの hook では正式化しない",
    )
    self.assertEqual(_events(self.log_path), ["selected", "promoted"])

  def test_promotes_draft_written_by_current_draft_tool(self):
    """実際の下書き生成 tool の source_sha256 と hook の検証範囲を固定する。"""
    rollout = self._rollout(self.prev_id)
    _codex_fixture(rollout, self.prev_id, self.cwd, "前セッション", 2000)

    draft_result = _run_draft_tool(rollout, self.drafts)
    self.assertEqual(
      draft_result.returncode,
      0,
      f"stdout={draft_result.stdout}\nstderr={draft_result.stderr}",
    )

    result = _run_hook(
      self._payload(),
      self.evidence,
      self.docs,
      self.drafts,
      self.codex_root,
      self.log_path,
    )

    self.assertEqual(result.returncode, 0, f"stdout={result.stdout}\nstderr={result.stderr}")
    self.assertTrue(
      (self.evidence / f"2026-06-15-codex-{self.prev_id}.md").exists(),
      "session-record-draft.py が書いた source_sha256 を hook が一致判定できる必要がある",
    )
    self.assertTrue(
      (self.docs / f"auto-2026-06-15-codex-{self.prev_id}.md").exists(),
      "実 tool 生成下書きも正式層2へ昇格する必要がある",
    )
    self.assertEqual(_events(self.log_path), ["selected", "promoted"])

  def test_only_current_draft_is_noop(self):
    """現セッション下書きしか無い場合は何もせず exit 0。"""
    _codex_fixture(self._rollout(self.current_id), self.current_id, self.cwd, "現セッション", 3000)
    _draft_fixture(
      self.drafts / f"codex-{self.current_id}.md",
      self.current_id,
      3000,
      _sha256(self._rollout(self.current_id)),
    )

    result = _run_hook(
      self._payload(),
      self.evidence,
      self.docs,
      self.drafts,
      self.codex_root,
      self.log_path,
    )

    self.assertEqual(result.returncode, 0, result.stderr)
    self.assertFalse(self.evidence.exists() and any(self.evidence.iterdir()))
    self.assertEqual(_events(self.log_path), ["no_previous_draft"])

  def test_non_session_start_is_ignored(self):
    """SessionStart 以外に誤登録されても正式化しない。"""
    _codex_fixture(self._rollout(self.prev_id), self.prev_id, self.cwd, "前セッション", 2000)
    _draft_fixture(
      self.drafts / f"codex-{self.prev_id}.md",
      self.prev_id,
      2000,
      _sha256(self._rollout(self.prev_id)),
    )
    payload = self._payload()
    payload["hook_event_name"] = "PostToolUse"

    result = _run_hook(payload, self.evidence, self.docs, self.drafts, self.codex_root, self.log_path)

    self.assertEqual(result.returncode, 0, result.stderr)
    self.assertFalse(self.evidence.exists() and any(self.evidence.iterdir()))
    self.assertEqual(_events(self.log_path), ["ignored_event"])

  def test_missing_current_session_id_is_diagnostic_noop(self):
    """current session_id が無い場合は推測せず no-op。"""
    payload = self._payload()
    payload.pop("session_id")

    result = _run_hook(payload, self.evidence, self.docs, self.drafts, self.codex_root, self.log_path)

    self.assertEqual(result.returncode, 0, result.stderr)
    self.assertFalse(self.evidence.exists() and any(self.evidence.iterdir()))
    self.assertEqual(_events(self.log_path), ["no_current_session_id"])

  def test_missing_cwd_is_diagnostic_noop(self):
    """cwd が無い場合は対象 repo を推測せず no-op。"""
    payload = self._payload()
    payload.pop("cwd")

    result = _run_hook(payload, self.evidence, self.docs, self.drafts, self.codex_root, self.log_path)

    self.assertEqual(result.returncode, 0, result.stderr)
    self.assertFalse(self.evidence.exists() and any(self.evidence.iterdir()))
    self.assertEqual(_events(self.log_path), ["no_cwd"])

  def test_missing_draft_dir_is_diagnostic_noop(self):
    """下書きディレクトリが無ければ no-op。"""
    result = _run_hook(
      self._payload(),
      self.evidence,
      self.docs,
      self.drafts,
      self.codex_root,
      self.log_path,
    )

    self.assertEqual(result.returncode, 0, result.stderr)
    self.assertFalse(self.evidence.exists() and any(self.evidence.iterdir()))
    self.assertEqual(_events(self.log_path), ["no_draft_dir"])

  def test_missing_jq_is_diagnostic_noop(self):
    """jq が無い場合は原因を診断ログに残して安全側 no-op にする。"""
    result = _run_hook(
      self._payload(),
      self.evidence,
      self.docs,
      self.drafts,
      self.codex_root,
      self.log_path,
      extra_env={"REVIEWCOMPASS_JQ": str(self.tmp / "missing-jq")},
    )

    self.assertEqual(result.returncode, 0, result.stderr)
    self.assertFalse(self.evidence.exists() and any(self.evidence.iterdir()))
    self.assertEqual(_events(self.log_path), ["missing_jq"])

  def test_missing_promote_tool_is_diagnostic_noop(self):
    """昇格 helper が無い場合は no_promote_tool で no-op。"""
    _codex_fixture(self._rollout(self.prev_id), self.prev_id, self.cwd, "前セッション", 2000)
    _draft_fixture(
      self.drafts / f"codex-{self.prev_id}.md",
      self.prev_id,
      2000,
      _sha256(self._rollout(self.prev_id)),
    )

    result = _run_hook(
      self._payload(),
      self.evidence,
      self.docs,
      self.drafts,
      self.codex_root,
      self.log_path,
      extra_env={"REVIEWCOMPASS_PROMOTE_TOOL": str(self.tmp / "missing-promote.py")},
    )

    self.assertEqual(result.returncode, 0, result.stderr)
    self.assertFalse(self.evidence.exists() and any(self.evidence.iterdir()))
    self.assertEqual(_events(self.log_path), ["no_promote_tool"])

  def test_promote_failure_is_diagnostic_noop(self):
    """昇格 helper が失敗しても SessionStart は止めず promote_failed を記録する。"""
    _codex_fixture(self._rollout(self.prev_id), self.prev_id, self.cwd, "前セッション", 2000)
    _draft_fixture(
      self.drafts / f"codex-{self.prev_id}.md",
      self.prev_id,
      2000,
      _sha256(self._rollout(self.prev_id)),
    )
    failing_tool = self.tmp / "failing-promote.py"
    failing_tool.write_text("import sys\nsys.exit(1)\n", encoding="utf-8")

    result = _run_hook(
      self._payload(),
      self.evidence,
      self.docs,
      self.drafts,
      self.codex_root,
      self.log_path,
      extra_env={"REVIEWCOMPASS_PROMOTE_TOOL": str(failing_tool)},
    )

    self.assertEqual(result.returncode, 0, result.stderr)
    self.assertFalse(self.evidence.exists() and any(self.evidence.iterdir()))
    self.assertEqual(_events(self.log_path), ["selected", "promote_failed"])

  def test_skips_latest_previous_draft_when_rollout_hash_changed(self):
    """最新候補の rollout が下書き作成後に伸びた場合は正式化しない。"""
    _codex_fixture(self._rollout(self.old_id), self.old_id, self.cwd, "古い終了済み", 1000)
    _codex_fixture(self._rollout(self.prev_id), self.prev_id, self.cwd, "前セッション v1", 2000)
    _draft_fixture(
      self.drafts / f"codex-{self.old_id}.md",
      self.old_id,
      1000,
      _sha256(self._rollout(self.old_id)),
    )
    _draft_fixture(
      self.drafts / f"codex-{self.prev_id}.md",
      self.prev_id,
      2000,
      _sha256(self._rollout(self.prev_id)),
    )
    _codex_fixture(self._rollout(self.prev_id), self.prev_id, self.cwd, "前セッション v2", 3000)

    result = _run_hook(
      self._payload(),
      self.evidence,
      self.docs,
      self.drafts,
      self.codex_root,
      self.log_path,
    )

    self.assertEqual(result.returncode, 0, result.stderr)
    self.assertFalse(
      (self.evidence / f"2026-06-15-codex-{self.prev_id}.md").exists(),
      "hash 不一致の最新候補は正式化してはいけない",
    )
    self.assertFalse(
      (self.evidence / f"2026-06-15-codex-{self.old_id}.md").exists(),
      "最新候補が進行中なら古い候補へフォールバックしない",
    )
    self.assertEqual(_events(self.log_path), ["selected", "previous_draft_in_progress"])

  def test_duplicate_session_rollouts_prefer_hash_matching_source(self):
    """同一 session_id の候補が複数ある場合は下書き source_sha256 一致を優先する。"""
    original_rollout = self._rollout(self.prev_id, "10-00-00")
    later_rollout = self._rollout(self.prev_id, "11-00-00")
    _codex_fixture(original_rollout, self.prev_id, self.cwd, "前セッション original", 2000)
    _draft_fixture(
      self.drafts / f"codex-{self.prev_id}.md",
      self.prev_id,
      2000,
      _sha256(original_rollout),
    )
    _codex_fixture(later_rollout, self.prev_id, self.cwd, "前セッション duplicate", 3000)

    result = _run_hook(
      self._payload(),
      self.evidence,
      self.docs,
      self.drafts,
      self.codex_root,
      self.log_path,
    )

    self.assertEqual(result.returncode, 0, result.stderr)
    self.assertTrue(
      (self.evidence / f"2026-06-15-codex-{self.prev_id}.md").exists(),
      "同一 session_id の別 rollout があっても source_sha256 一致候補を正式化する必要がある",
    )
    self.assertEqual(_events(self.log_path), ["selected", "promoted"])

  def test_duplicate_session_rollouts_without_hash_match_stay_in_progress(self):
    """同一 session_id 候補が複数あっても hash 一致が無ければ安全側で止まる。"""
    _codex_fixture(
      self._rollout(self.prev_id, "10-00-00"),
      self.prev_id,
      self.cwd,
      "前セッション mismatch old",
      2000,
    )
    _codex_fixture(
      self._rollout(self.prev_id, "11-00-00"),
      self.prev_id,
      self.cwd,
      "前セッション mismatch new",
      3000,
    )
    _draft_fixture(
      self.drafts / f"codex-{self.prev_id}.md",
      self.prev_id,
      3000,
      "0" * 64,
    )

    result = _run_hook(
      self._payload(),
      self.evidence,
      self.docs,
      self.drafts,
      self.codex_root,
      self.log_path,
    )

    self.assertEqual(result.returncode, 0, result.stderr)
    self.assertFalse(
      (self.evidence / f"2026-06-15-codex-{self.prev_id}.md").exists(),
      "同一 session_id 候補に hash 一致が無ければ正式化してはいけない",
    )
    self.assertEqual(_events(self.log_path), ["selected", "previous_draft_in_progress"])

  def test_resume_session_start_uses_same_safety_checks(self):
    """resume 起動でも startup と同じ安全確認で前セッションを昇格する。"""
    _codex_fixture(self._rollout(self.prev_id), self.prev_id, self.cwd, "前セッション", 2000)
    _draft_fixture(
      self.drafts / f"codex-{self.prev_id}.md",
      self.prev_id,
      2000,
      _sha256(self._rollout(self.prev_id)),
    )
    payload = self._payload()
    payload["source"] = "resume"

    result = _run_hook(payload, self.evidence, self.docs, self.drafts, self.codex_root, self.log_path)

    self.assertEqual(result.returncode, 0, result.stderr)
    self.assertTrue(
      (self.evidence / f"2026-06-15-codex-{self.prev_id}.md").exists(),
      "resume でも hash 一致した前セッション下書きは正式化する",
    )
    self.assertEqual(_events(self.log_path), ["selected", "promoted"])

  def test_missing_draft_hash_is_unverifiable_and_not_promoted(self):
    """source_sha256 の無い下書きは検証不能として正式化しない。"""
    _codex_fixture(self._rollout(self.prev_id), self.prev_id, self.cwd, "前セッション", 2000)
    _draft_fixture(
      self.drafts / f"codex-{self.prev_id}.md",
      self.prev_id,
      2000,
      "",
    )

    result = _run_hook(
      self._payload(),
      self.evidence,
      self.docs,
      self.drafts,
      self.codex_root,
      self.log_path,
    )

    self.assertEqual(result.returncode, 0, result.stderr)
    self.assertFalse(
      (self.evidence / f"2026-06-15-codex-{self.prev_id}.md").exists(),
      "hash 検証不能な下書きは正式化してはいけない",
    )
    self.assertEqual(_events(self.log_path), ["selected", "previous_draft_unverifiable"])

  def test_missing_draft_hash_line_is_unverifiable_and_not_promoted(self):
    """source_sha256 行そのものが無い下書きも検証不能として正式化しない。"""
    _codex_fixture(self._rollout(self.prev_id), self.prev_id, self.cwd, "前セッション", 2000)
    draft = self.drafts / f"codex-{self.prev_id}.md"
    draft.parent.mkdir(parents=True, exist_ok=True)
    draft.write_text(
      "---\n"
      "source: codex\n"
      f"session_id: {self.prev_id}\n"
      "layer: draft\n"
      "---\n"
      "\n"
      "draft\n",
      encoding="utf-8",
    )
    os.utime(draft, (2000, 2000))

    result = _run_hook(
      self._payload(),
      self.evidence,
      self.docs,
      self.drafts,
      self.codex_root,
      self.log_path,
    )

    self.assertEqual(result.returncode, 0, result.stderr)
    self.assertFalse(
      (self.evidence / f"2026-06-15-codex-{self.prev_id}.md").exists(),
      "source_sha256 行の無い下書きは正式化してはいけない",
    )
    self.assertEqual(_events(self.log_path), ["selected", "previous_draft_unverifiable"])

  def test_missing_rollout_is_unverifiable_and_not_promoted(self):
    """下書きに hash があっても元 rollout が見つからなければ正式化しない。"""
    _draft_fixture(
      self.drafts / f"codex-{self.prev_id}.md",
      self.prev_id,
      2000,
      "0" * 64,
    )

    result = _run_hook(
      self._payload(),
      self.evidence,
      self.docs,
      self.drafts,
      self.codex_root,
      self.log_path,
    )

    self.assertEqual(result.returncode, 0, result.stderr)
    self.assertFalse(
      (self.evidence / f"2026-06-15-codex-{self.prev_id}.md").exists(),
      "元 rollout が見つからない下書きは正式化してはいけない",
    )
    self.assertEqual(_events(self.log_path), ["selected", "previous_draft_unverifiable"])

  def test_rollout_for_other_cwd_is_unverifiable_and_not_promoted(self):
    """同じ session_id でも別 cwd の rollout は元記録として扱わない。"""
    _codex_fixture(
      self._rollout(self.prev_id),
      self.prev_id,
      "/Users/Daily/OtherProject",
      "別 repo の同一 session_id",
      2000,
    )
    _draft_fixture(
      self.drafts / f"codex-{self.prev_id}.md",
      self.prev_id,
      2000,
      "0" * 64,
    )

    result = _run_hook(
      self._payload(),
      self.evidence,
      self.docs,
      self.drafts,
      self.codex_root,
      self.log_path,
    )

    self.assertEqual(result.returncode, 0, result.stderr)
    self.assertFalse(
      (self.evidence / f"2026-06-15-codex-{self.prev_id}.md").exists(),
      "別 cwd の rollout を根拠に正式化してはいけない",
    )
    self.assertEqual(_events(self.log_path), ["selected", "previous_draft_unverifiable"])


if __name__ == "__main__":
  unittest.main()
