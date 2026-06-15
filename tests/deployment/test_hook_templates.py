import json
import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_codex_hooks_template_registers_todo_capture_only_on_post_tool_use():
  template = json.loads(
    (REPO_ROOT / "templates/hooks/codex-hooks.json.template").read_text(encoding="utf-8")
  )
  hooks = template["hooks"]
  post_tool_commands = [
    hook["command"]
    for group in hooks.get("PostToolUse", [])
    for hook in group.get("hooks", [])
  ]
  session_start_commands = [
    hook["command"]
    for group in hooks.get("SessionStart", [])
    for hook in group.get("hooks", [])
  ]
  user_prompt_commands = [
    hook["command"]
    for group in hooks.get("UserPromptSubmit", [])
    for hook in group.get("hooks", [])
  ]

  assert any(
    ".codex/hooks/session-record-capture-current-on-todo.sh" in command
    for command in post_tool_commands
  ), "PostToolUse に TODO 更新後の現セッション取り込み hook を登録する必要がある"
  assert not any(
    ".codex/hooks/session-record-capture-current-on-todo.sh" in command
    for command in session_start_commands
  ), "現セッション取り込み hook は SessionStart へ登録しない"
  assert not any(
    ".codex/hooks/session-record-capture-current-on-todo.sh" in command
    for command in user_prompt_commands
  ), "UserPromptSubmit は発話ごとに誤発火し得るため登録しない"


def test_session_capture_template_is_deployable_without_local_user_paths():
  text = (
    REPO_ROOT / "templates/hooks/session-record-capture-current-on-todo.sh.template"
  ).read_text(encoding="utf-8")

  assert "{{REVIEWCOMPASS_PYTHON}}" in text
  assert "{{REVIEWCOMPASS_DIR}}" in text
  assert "/Users/keno" not in text
  assert "/Users/Daily/Development/ReviewCompass" not in text
  assert re.search(r"tools/session-record-draft\.py", text)
  assert ".reviewcompass/runtime/session-record-drafts" in text
  assert ".reviewcompass/runtime/session-record-capture-current-on-todo.jsonl" in text
  assert "hook_event_name" in text
  assert "ignored_event" in text
  assert "TODO_NEXT_SESSION.md" in text
  assert "todo_changed" in text
  assert "drafted" in text
  assert "baseline_recorded" in text
