import json
import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_codex_hooks_template_registers_session_capture_only_on_session_end():
  template = json.loads(
    (REPO_ROOT / "templates/hooks/codex-hooks.json.template").read_text(encoding="utf-8")
  )
  hooks = template["hooks"]
  session_end_commands = [
    hook["command"]
    for group in hooks.get("SessionEnd", [])
    for hook in group.get("hooks", [])
  ]
  post_tool_commands = [
    hook["command"]
    for group in hooks.get("PostToolUse", [])
    for hook in group.get("hooks", [])
  ]
  user_prompt_commands = [
    hook["command"]
    for group in hooks.get("UserPromptSubmit", [])
    for hook in group.get("hooks", [])
  ]

  assert any(
    ".codex/hooks/session-record-capture-current-on-session-end.sh" in command
    for command in session_end_commands
  ), "SessionEnd に現セッション取り込み hook を登録する必要がある"
  assert not any(
    "session-record-capture-current" in command
    for command in post_tool_commands
  ), "TODO 更新を観測する PostToolUse でセッション記録を取り込んではいけない"
  assert not any(
    "session-record-capture-current" in command
    for command in user_prompt_commands
  ), "UserPromptSubmit は発話ごとに誤発火し得るため登録しない"


def test_session_capture_template_is_deployable_without_local_user_paths():
  text = (
    REPO_ROOT / "templates/hooks/session-record-capture-current-on-session-end.sh.template"
  ).read_text(encoding="utf-8")

  assert "{{REVIEWCOMPASS_PYTHON}}" in text
  assert "{{REVIEWCOMPASS_DIR}}" in text
  assert "/Users/keno" not in text
  assert "/Users/Daily/Development/ReviewCompass" not in text
  assert re.search(r"tools/session-record-backfill\.py", text)
  assert ".reviewcompass/evidence/sessions" in text
  assert ".reviewcompass/runtime/session-record-capture-current-on-session-end.jsonl" in text
  assert "hook_event_name" in text
  assert "ignored_event" in text
  assert "SessionEnd" in text
  assert "session_id" in text
  assert "captured" in text
