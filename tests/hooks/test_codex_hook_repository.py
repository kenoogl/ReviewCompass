"""Codex hook adapter のリポジトリ管理状態を確認するテスト"""

import json
import subprocess
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]

CODEX_HOOK_FILES = [
  ".codex/hooks.json",
  ".codex/hooks/README.md",
  ".codex/hooks/pre-bash-precheck.sh",
  ".codex/hooks/review-prompt-guide-inject.sh",
  ".codex/hooks/session-record-capture-current-on-session-end.sh",
  ".codex/hooks/session-record-promote-previous-draft.sh",
]


class CodexHookRepositoryTests(unittest.TestCase):
  """Codex 稼働に必要な hook adapter ファイルが追跡可能であることを確認する"""

  def test_codex_hook_files_are_not_ignored(self):
    for relpath in CODEX_HOOK_FILES:
      result = subprocess.run(
        ["git", "check-ignore", "-q", relpath],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
      )
      self.assertNotEqual(
        result.returncode,
        0,
        f"{relpath} は gitignore で無視されてはいけない",
      )

  def test_codex_hook_files_exist(self):
    for relpath in CODEX_HOOK_FILES:
      self.assertTrue(
        (REPO_ROOT / relpath).exists(),
        f"{relpath} が存在する必要がある",
      )

  def test_codex_hook_command_is_repository_relative(self):
    hooks_config = json.loads((REPO_ROOT / ".codex/hooks.json").read_text())
    command = hooks_config["hooks"]["PreToolUse"][0]["hooks"][0]["command"]

    self.assertNotIn(
      str(REPO_ROOT),
      command,
      "hooks.json は環境固有の絶対パスを含んではいけない",
    )
    self.assertIn(
      ".codex/hooks/pre-bash-precheck.sh",
      command,
      "hooks.json は repo 相対の Codex hook を呼び出す必要がある",
    )

  def test_codex_session_end_capture_hook_is_registered(self):
    hooks_config = json.loads((REPO_ROOT / ".codex/hooks.json").read_text())
    commands = [
      hook["command"]
      for group in hooks_config["hooks"].get("SessionEnd", [])
      for hook in group.get("hooks", [])
    ]
    self.assertTrue(
      any(".codex/hooks/session-record-capture-current-on-session-end.sh" in c for c in commands),
      "Codex SessionEnd で現セッション取り込み hook を登録する必要がある",
    )

  def test_codex_post_tool_todo_capture_hook_is_not_registered(self):
    hooks_config = json.loads((REPO_ROOT / ".codex/hooks.json").read_text())
    commands = [
      hook["command"]
      for group in hooks_config["hooks"].get("PostToolUse", [])
      for hook in group.get("hooks", [])
    ]
    self.assertFalse(
      any("session-record-capture-current" in c for c in commands),
      "TODO 更新を観測する PostToolUse でセッション記録を取り込んではいけない",
    )

  def test_codex_session_start_promote_previous_draft_hook_is_registered(self):
    hooks_config = json.loads((REPO_ROOT / ".codex/hooks.json").read_text())
    commands = [
      hook["command"]
      for group in hooks_config["hooks"].get("SessionStart", [])
      for hook in group.get("hooks", [])
    ]
    self.assertTrue(
      any(".codex/hooks/session-record-promote-previous-draft.sh" in c for c in commands),
      "Codex SessionStart で前セッション下書きの正式昇格 hook を登録する必要がある",
    )
    matchers = [
      group.get("matcher", "")
      for group in hooks_config["hooks"].get("SessionStart", [])
      for hook in group.get("hooks", [])
      if ".codex/hooks/session-record-promote-previous-draft.sh" in hook.get("command", "")
    ]
    self.assertTrue(
      any("startup" in matcher and "resume" in matcher for matcher in matchers),
      "SessionStart hook は startup/resume の開始契機で前セッション昇格を試みる必要がある",
    )

  def test_codex_session_start_promote_previous_draft_hook_template_is_registered(self):
    hooks_config = json.loads(
      (REPO_ROOT / "templates" / "hooks" / "codex-hooks.json.template").read_text()
    )
    commands = [
      hook["command"]
      for group in hooks_config["hooks"].get("SessionStart", [])
      for hook in group.get("hooks", [])
    ]
    self.assertTrue(
      any(".codex/hooks/session-record-promote-previous-draft.sh" in c for c in commands),
      "Codex hook 雛形も SessionStart の前セッション昇格 hook を登録する必要がある",
    )
    matchers = [
      group.get("matcher", "")
      for group in hooks_config["hooks"].get("SessionStart", [])
      for hook in group.get("hooks", [])
      if ".codex/hooks/session-record-promote-previous-draft.sh" in hook.get("command", "")
    ]
    self.assertTrue(
      any("startup" in matcher and "resume" in matcher for matcher in matchers),
      "Codex hook 雛形の SessionStart hook も startup/resume を対象にする必要がある",
    )

  def test_codex_user_prompt_capture_fallback_hook_is_not_registered(self):
    hooks_config = json.loads((REPO_ROOT / ".codex/hooks.json").read_text())
    commands = [
      hook["command"]
      for group in hooks_config["hooks"].get("UserPromptSubmit", [])
      for hook in group.get("hooks", [])
    ]
    self.assertFalse(
      any("session-record-capture-current" in c for c in commands),
      "UserPromptSubmit は発話ごとに誤発火し得るため、現セッション取り込み hook を登録してはいけない",
    )

  def test_codex_user_prompt_review_guide_hook_is_registered(self):
    hooks_config = json.loads((REPO_ROOT / ".codex/hooks.json").read_text())
    commands = [
      hook["command"]
      for group in hooks_config["hooks"].get("UserPromptSubmit", [])
      for hook in group.get("hooks", [])
    ]
    self.assertTrue(
      any(".codex/hooks/review-prompt-guide-inject.sh" in c for c in commands),
      "Codex UserPromptSubmit で LLM-as-judge prompt guide hook を登録する必要がある",
    )

  def test_codex_user_prompt_review_guide_hook_template_is_registered(self):
    hooks_config = json.loads(
      (REPO_ROOT / "templates" / "hooks" / "codex-hooks.json.template").read_text()
    )
    commands = [
      hook["command"]
      for group in hooks_config["hooks"].get("UserPromptSubmit", [])
      for hook in group.get("hooks", [])
    ]
    self.assertTrue(
      any(".codex/hooks/review-prompt-guide-inject.sh" in c for c in commands),
      "Codex hook 雛形も UserPromptSubmit の LLM-as-judge prompt guide hook を登録する必要がある",
    )

  def test_codex_review_prompt_guide_hook_injects_context_for_review_prompt(self):
    payload = json.dumps({
      "hook_event_name": "UserPromptSubmit",
      "prompt": "3者レビューで確認してはどうか",
      "cwd": str(REPO_ROOT),
    })
    result = subprocess.run(
      ["bash", ".codex/hooks/review-prompt-guide-inject.sh"],
      cwd=str(REPO_ROOT),
      input=payload,
      capture_output=True,
      text=True,
    )

    self.assertEqual(result.returncode, 0, result.stderr)
    parsed = json.loads(result.stdout)
    additional_context = parsed["hookSpecificOutput"]["additionalContext"]
    self.assertIn("LLM as a Judge", additional_context)
    self.assertIn("llm-as-judge-prompting", additional_context)

  def test_codex_review_prompt_guide_hook_is_silent_for_unrelated_prompt(self):
    payload = json.dumps({
      "hook_event_name": "UserPromptSubmit",
      "prompt": "TODO_NEXT_SESSION.mdを読む",
      "cwd": str(REPO_ROOT),
    })
    result = subprocess.run(
      ["bash", ".codex/hooks/review-prompt-guide-inject.sh"],
      cwd=str(REPO_ROOT),
      input=payload,
      capture_output=True,
      text=True,
    )

    self.assertEqual(result.returncode, 0, result.stderr)
    self.assertEqual(result.stdout, "")


if __name__ == "__main__":
  unittest.main()
