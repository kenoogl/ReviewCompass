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


if __name__ == "__main__":
  unittest.main()
