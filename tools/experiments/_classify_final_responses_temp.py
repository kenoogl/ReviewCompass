"""tools/experiments/_classify_final_responses_temp.py

質問返し 15 件への 2 ターン目実行結果（topic-NN-MODEL-final.yaml）を分類する一時スクリプト。
セッション 36（2026-05-28）作成、後で削除予定。
"""
import re
import yaml
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
RESULTS_DIR = ROOT / "tools" / "experiments" / "results"

TARGETS = [
  (77, "sonnet-4-6-api", "Sonnet 4.6 API"),
  (79, "sonnet-4-6-api", "Sonnet 4.6 API"),
  (85, "sonnet-4-6-api", "Sonnet 4.6 API"),
  (87, "sonnet-4-6-api", "Sonnet 4.6 API"),
  (77, "gemini-3-5-flash", "Gemini-3.5-flash"),
  (78, "gemini-3-5-flash", "Gemini-3.5-flash"),
  (79, "gemini-3-5-flash", "Gemini-3.5-flash"),
  (81, "gemini-3-5-flash", "Gemini-3.5-flash"),
  (84, "gemini-3-5-flash", "Gemini-3.5-flash"),
  (87, "gemini-3-5-flash", "Gemini-3.5-flash"),
  (89, "gemini-3-5-flash", "Gemini-3.5-flash"),
  (91, "gemini-3-5-flash", "Gemini-3.5-flash"),
  (98, "gemini-3-5-flash", "Gemini-3.5-flash"),
]


def classify(response_text: str) -> str:
  m = re.search(r'decision:\s*["\']?(採用[：:]?\s*案\s*[12]|別案を提示|深掘り要求)', response_text)
  if not m:
    return "質問返し継続"
  v = m.group(1)
  if re.match(r'採用', v):
    return v.replace(" ", "").replace(":", "：")
  return v


def main() -> int:
  print("| topic | finding_id | モデル | 1 ターン目 | 2 ターン目（最終）|")
  print("|---|---|---|---|---|")
  for topic, suffix, label in TARGETS:
    final_path = RESULTS_DIR / f"topic-{topic}-{suffix}-final.yaml"
    turn1_path = RESULTS_DIR / f"topic-{topic}-{suffix}.yaml"

    if not final_path.exists():
      print(f"| topic-{topic} | - | {label} | - | (file 不在) |")
      continue

    final_data = yaml.safe_load(final_path.read_text(encoding="utf-8"))
    turn1_data = yaml.safe_load(turn1_path.read_text(encoding="utf-8"))

    final_decision = classify(final_data.get("response_text", ""))
    turn1_decision = classify(turn1_data.get("response_text", ""))

    print(f"| topic-{topic} | - | {label} | {turn1_decision} | **{final_decision}** |")

  # 最終判定の分布
  print("\n## 最終判定の分布")
  counts = {}
  for topic, suffix, _ in TARGETS:
    final_path = RESULTS_DIR / f"topic-{topic}-{suffix}-final.yaml"
    if final_path.exists():
      data = yaml.safe_load(final_path.read_text(encoding="utf-8"))
      cls = classify(data.get("response_text", ""))
      counts[cls] = counts.get(cls, 0) + 1
  for k, v in sorted(counts.items(), key=lambda x: -x[1]):
    print(f"  {k}: {v} 件")
  return 0


if __name__ == "__main__":
  raise SystemExit(main())
