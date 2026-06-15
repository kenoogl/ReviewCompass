import json
import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_codex_hooks_template_registers_session_capture_fallback():
  template = json.loads(
    (REPO_ROOT / "templates/hooks/codex-hooks.json.template").read_text(encoding="utf-8")
  )
  hooks = template["hooks"]
  for event in ("SessionStart", "UserPromptSubmit"):
    commands = [
      hook["command"]
      for group in hooks.get(event, [])
      for hook in group.get("hooks", [])
    ]
    assert any(
      ".codex/hooks/session-record-capture-previous.sh" in command
      for command in commands
    ), f"{event} に前セッション取り込み hook を登録する必要がある"


def test_session_capture_template_is_deployable_without_local_user_paths():
  text = (
    REPO_ROOT / "templates/hooks/session-record-capture-previous.sh.template"
  ).read_text(encoding="utf-8")

  assert "{{REVIEWCOMPASS_PYTHON}}" in text
  assert "{{REVIEWCOMPASS_DIR}}" in text
  assert "/Users/keno" not in text
  assert "/Users/Daily/Development/ReviewCompass" not in text
  assert re.search(r"tools/session-record-backfill\.py", text)
  assert ".reviewcompass/runtime/session-record-capture-previous.jsonl" in text
  assert "already_checked" in text
