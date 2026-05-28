"""tools/experiments/_classify_api_responses_temp.py

analysis tasks の API 経路 5 モデル × 23 件 ＝ 115 件の 1 ターン目応答を
「判定（decision: ... を出した）」と「質問返し（決断保留、追加情報要求）」に分類する一時スクリプト。
セッション 36（2026-05-28）のマルチターン対話プロトコル設計の調査に使用、後で削除予定。

判定基準：
- response_text 内に decision: ... の文字列がある → 「判定」
- ない、または「質問」「確認」「教えて」等の語が含まれる → 「質問返し」
"""
import re
import yaml as yaml_lib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
RESULTS_DIR = ROOT / "tools" / "experiments" / "results"

TOPIC_NUMBERS = list(range(53, 76))

MODELS = [
  ("sonnet-4-6-api", "Sonnet 4.6 API"),
  ("gpt-5-5", "GPT-5.5"),
  ("gpt-5-4", "GPT-5.4"),
  ("gemini-3-5-flash", "Gemini-3.5-flash"),
  ("gemini-3-1-pro-preview", "Gemini-3.1-pro"),
]


def classify(yaml_text: str, response_text: str) -> str:
  """1 ターン目応答を分類。

  判定方針（2026-05-28 セッション 36 改修）：
  - 第 1 段階：`decision:` フィールドの有無で「判定」と「質問返し」を二分。
    これにより質問語（「質問」「ご教示」「ご確認」「お聞かせ」等の丁寧表現を含む）
    の検出漏れによる誤分類を構造的に防ぐ。
  - 第 2 段階：判定の場合、その値で「案 1／案 2」「別案」「深掘り要求」に細分類。
  """
  # 第 1 段階：decision フィールドの有無
  decision_match = re.search(r'decision:\s*["\']?(採用[：:]?\s*案\s*[12]|別案を提示|深掘り要求)', response_text)
  if not decision_match:
    return "質問返し（マルチターン続行可）"

  # 第 2 段階：判定値の細分類
  decision_value = decision_match.group(1)
  if re.match(r'採用', decision_value):
    return "判定（案 1 or 案 2）"
  if "別案" in decision_value:
    return "判定（別案）"
  if "深掘り" in decision_value:
    return "深掘り要求"
  return "判定（その他）"


def main() -> int:
  classification = {}  # {(topic, model_label): 分類結果}

  for topic in TOPIC_NUMBERS:
    for suffix, label in MODELS:
      path = RESULTS_DIR / f"topic-{topic}-{suffix}.yaml"
      if not path.exists():
        classification[(topic, label)] = "ファイル無"
        continue
      try:
        data = yaml_lib.safe_load(path.read_text(encoding="utf-8"))
        response = data.get("response_text", "") if isinstance(data, dict) else ""
      except Exception as e:
        classification[(topic, label)] = f"YAML 解析失敗: {e}"
        continue
      classification[(topic, label)] = classify(path.read_text(encoding="utf-8"), response)

  # 表形式で出力（topic × モデル）
  print("| topic |", " | ".join(label for _, label in MODELS), "|")
  print("|---|" + "---|" * len(MODELS))
  for topic in TOPIC_NUMBERS:
    row = [f"topic-{topic}"]
    for _, label in MODELS:
      row.append(classification[(topic, label)])
    print("| " + " | ".join(row) + " |")

  # モデル別集計
  print("\n## モデル別集計")
  for _, label in MODELS:
    counts = {}
    for topic in TOPIC_NUMBERS:
      cls = classification[(topic, label)]
      counts[cls] = counts.get(cls, 0) + 1
    print(f"\n**{label}**：", ", ".join(f"{k} {v}件" for k, v in counts.items()))

  # 全体集計
  print("\n## 全体集計（5 モデル × 23 件 ＝ 115 件）")
  all_counts = {}
  for (_, _), cls in classification.items():
    all_counts[cls] = all_counts.get(cls, 0) + 1
  for k, v in sorted(all_counts.items(), key=lambda x: -x[1]):
    print(f"  {k}: {v} 件")

  return 0


if __name__ == "__main__":
  raise SystemExit(main())
