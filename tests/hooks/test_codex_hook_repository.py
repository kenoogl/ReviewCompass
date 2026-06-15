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
  ".codex/hooks/session-record-capture-current-on-todo.sh",
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

  def test_codex_post_tool_todo_capture_hook_is_registered(self):
    hooks_config = json.loads((REPO_ROOT / ".codex/hooks.json").read_text())
    commands = [
      hook["command"]
      for group in hooks_config["hooks"].get("PostToolUse", [])
      for hook in group.get("hooks", [])
    ]
    self.assertTrue(
      any(".codex/hooks/session-record-capture-current-on-todo.sh" in c for c in commands),
      "Codex PostToolUse で TODO 更新後の現セッション取り込み hook を登録する必要がある",
    )

  def test_codex_session_start_capture_hook_is_not_registered(self):
    hooks_config = json.loads((REPO_ROOT / ".codex/hooks.json").read_text())
    commands = [
      hook["command"]
      for group in hooks_config["hooks"].get("SessionStart", [])
      for hook in group.get("hooks", [])
    ]
    self.assertFalse(
      any(".codex/hooks/session-record-capture-current-on-todo.sh" in c for c in commands),
      "Codex の現セッション取り込み hook は SessionStart へ登録しない",
    )

  def test_codex_user_prompt_capture_fallback_hook_is_not_registered(self):
    hooks_config = json.loads((REPO_ROOT / ".codex/hooks.json").read_text())
    commands = [
      hook["command"]
      for group in hooks_config["hooks"].get("UserPromptSubmit", [])
      for hook in group.get("hooks", [])
    ]
    self.assertFalse(
      any(".codex/hooks/session-record-capture-current-on-todo.sh" in c for c in commands),
      "UserPromptSubmit は発話ごとに誤発火し得るため、現セッション取り込み hook を登録してはいけない",
    )


if __name__ == "__main__":
  unittest.main()
