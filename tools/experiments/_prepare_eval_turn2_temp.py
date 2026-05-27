"""evaluation tasks の Gemini-flash 深掘り 3 件（topic-36／43／50）の turn-2 用 history-file を生成する一時スクリプト。"""
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent.parent
PROMPTS_DIR = ROOT / "tools" / "experiments" / "prompts"
RESULTS_DIR = ROOT / "tools" / "experiments" / "results"
HISTORY_DIR = ROOT / "tools" / "experiments" / "history"

# 深掘り発火した 3 件（topic-36 A-001、topic-43 F-008、topic-50 A-005）
DEEP_DIVE_TOPICS = [36, 43, 50]
MODEL_SUFFIX = "gemini-3-5-flash"


def build_history_file(topic_num: int) -> Path:
  """topic-NN.txt と 1 ターン目応答から history-file を生成。"""
  prompt_file = PROMPTS_DIR / f"topic-{topic_num:02d}.txt"
  result_file = RESULTS_DIR / f"topic-{topic_num:02d}-{MODEL_SUFFIX}.yaml"
  history_file = HISTORY_DIR / f"topic-{topic_num:02d}-{MODEL_SUFFIX}.yaml"

  user_content = prompt_file.read_text(encoding="utf-8")

  result_data = yaml.safe_load(result_file.read_text(encoding="utf-8"))
  assistant_content = result_data.get("response_text", "")

  messages = [
    {"role": "user", "content": user_content},
    {"role": "assistant", "content": assistant_content},
  ]

  HISTORY_DIR.mkdir(parents=True, exist_ok=True)
  history_file.write_text(
    yaml.safe_dump(messages, allow_unicode=True, sort_keys=False),
    encoding="utf-8",
  )
  return history_file


def main() -> int:
  for topic_num in DEEP_DIVE_TOPICS:
    history_file = build_history_file(topic_num)
    print(f"  生成: {history_file.relative_to(ROOT)}")
  print(f"\n合計 {len(DEEP_DIVE_TOPICS)} 件の history-file を生成完了")
  return 0


if __name__ == "__main__":
  raise SystemExit(main())
