"""tools/experiments/_rerun_longtimeout_temp.py

post-write-verification 検証用、3 系統対応のタイムアウト 300 秒ラッパー。
プロンプトが長くなり既定 60 秒では足りないため、3 系統すべてを 300 秒で実行する。
セッション 41（2026-05-31）の検証完了後に削除予定。

引数：
- --provider <anthropic-api|openai-api|gemini-api>：必須
- --model <モデル名>：必須
- --prompt-file <パス>：必須
"""
import argparse
import sys
import time
import yaml
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_PROJECT_ROOT))

from tools.api_providers.providers import get_provider

parser = argparse.ArgumentParser()
parser.add_argument("--provider", required=True)
parser.add_argument("--model", required=True)
parser.add_argument("--prompt-file", required=True)
args = parser.parse_args()

prompt = Path(args.prompt_file).read_text(encoding="utf-8")

provider_cls = get_provider(args.provider)
provider = provider_cls(
  model=args.model,
  timeout_seconds=300,
  max_retries=1,
)

start = time.monotonic()
response_text = provider.send_request(prompt)
duration = time.monotonic() - start

output = {
  "provider": args.provider,
  "model": args.model,
  "turn_number": 1,
  "duration_seconds": round(duration, 3),
  "sent_messages_count": 1,
  "response_text": response_text,
}

sys.stdout.write(yaml.dump(output, allow_unicode=True, sort_keys=False))
