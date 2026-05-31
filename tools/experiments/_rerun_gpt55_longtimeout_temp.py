"""tools/experiments/_rerun_gpt55_longtimeout_temp.py

post-write-verification 検証で GPT-5.5 が既定 60 秒タイムアウトで失敗したため、
タイムアウトを 300 秒に延長して再実行する一時スクリプト。
本検証完了後に削除予定（セッション 41、2026-05-31）。
"""
import sys
import time
import yaml
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_PROJECT_ROOT))

from tools.api_providers.providers import OpenAIProvider

PROMPT_PATH = _PROJECT_ROOT / "docs/notes/post-write-verification-review/prompt.md"
prompt = PROMPT_PATH.read_text(encoding="utf-8")

provider = OpenAIProvider(
  model="gpt-5.5",
  timeout_seconds=300,
  max_retries=1,
)

start = time.monotonic()
response_text = provider.send_request(prompt)
duration = time.monotonic() - start

output = {
  "provider": "openai-api",
  "model": "gpt-5.5",
  "turn_number": 1,
  "duration_seconds": round(duration, 3),
  "sent_messages_count": 1,
  "response_text": response_text,
}

sys.stdout.write(yaml.dump(output, allow_unicode=True, sort_keys=False))
