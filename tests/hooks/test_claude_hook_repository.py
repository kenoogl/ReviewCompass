"""Claude hook adapter のリポジトリ管理状態を確認するテスト"""

import json
import subprocess
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]

CLAUDE_HOOK_FILES = [
  ".claude/settings.json",
  ".claude/hooks/README.md",
  ".claude/hooks/pre-bash-precheck.sh",
]


class ClaudeHookRepositoryTests(unittest.TestCase):
  """Claude Code 稼働に必要な hook adapter ファイルが追跡可能であることを確認する"""

  def test_claude_hook_files_are_not_ignored(self):
    for relpath in CLAUDE_HOOK_FILES:
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

  def test_claude_hook_files_exist(self):
    for relpath in CLAUDE_HOOK_FILES:
      self.assertTrue(
        (REPO_ROOT / relpath).exists(),
        f"{relpath} が存在する必要がある",
      )

  def test_claude_hook_command_is_repository_relative(self):
    settings = json.loads((REPO_ROOT / ".claude/settings.json").read_text())
    command = settings["hooks"]["PreToolUse"][0]["hooks"][0]["command"]

    self.assertNotIn(
      str(REPO_ROOT),
      command,
      "settings.json の hook は環境固有の絶対パスを含んではいけない",
    )
    self.assertIn(
      ".claude/hooks/pre-bash-precheck.sh",
      command,
      "settings.json は repo 相対の Claude hook を呼び出す必要がある",
    )

  def test_claude_settings_have_no_absolute_paths(self):
    raw = (REPO_ROOT / ".claude/settings.json").read_text()
    self.assertNotIn(
      str(REPO_ROOT),
      raw,
      "settings.json は環境固有の絶対パスを含んではいけない",
    )

  def test_claude_entry_file_imports_agents_md(self):
    claude_md = REPO_ROOT / "CLAUDE.md"
    self.assertTrue(
      claude_md.exists(),
      "リポジトリ直下に Claude 用入口 CLAUDE.md が存在する必要がある",
    )
    self.assertIn(
      "@AGENTS.md",
      claude_md.read_text(),
      "CLAUDE.md は AGENTS.md を取り込む入口である必要がある",
    )


class ClaudeCodexHookParityTests(unittest.TestCase):
  """Claude と Codex のフック本体が漂流していないことを確認する"""

  def test_hook_scripts_are_identical(self):
    claude_script = (REPO_ROOT / ".claude/hooks/pre-bash-precheck.sh").read_text()
    codex_script = (REPO_ROOT / ".codex/hooks/pre-bash-precheck.sh").read_text()
    self.assertEqual(
      claude_script,
      codex_script,
      ".claude と .codex の pre-bash-precheck.sh は同一内容でなければならない",
    )


if __name__ == "__main__":
  unittest.main()
