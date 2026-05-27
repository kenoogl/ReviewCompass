"""evaluation 7 モデル比較実験の結果を集計する一時スクリプト。"""
import re
from pathlib import Path

import yaml

results_dir = Path(__file__).resolve().parent / "results"
MODELS = [
  ("sonnet-4-6-api", "sonnet-api"),
  ("sonnet-4-6-cli", "sonnet-cli"),
  ("gpt-5-5", "gpt-5.5"),
  ("gpt-5-4", "gpt-5.4"),
  ("gemini-3-5-flash", "g-flash"),
  ("gemini-3-1-pro-preview", "g-pro"),
]
TOPIC_RANGE = list(range(34, 53))
TOPIC_TO_ID = {
  34: ("F-001", "must"),
  35: ("F-002", "must"),
  36: ("A-001", "must"),
  37: ("F-003", "must"),
  38: ("F-006", "must"),
  39: ("F-011", "must"),
  40: ("A-003", "must"),
  41: ("A-002", "must"),
  42: ("F-007", "should"),
  43: ("F-008", "should"),
  44: ("F-009", "should"),
  45: ("F-012", "should"),
  46: ("F-013", "should"),
  47: ("F-014", "should"),
  48: ("F-015", "should"),
  49: ("A-004", "should"),
  50: ("A-005", "should"),
  51: ("A-006", "should"),
  52: ("A-007", "should"),
}


def extract_decision(yaml_path: Path, turn2_path: Path = None) -> str:
  # turn-2 が存在すればそれを優先（深掘り発火後の最終判定）
  if turn2_path and turn2_path.exists():
    yaml_path = turn2_path
  if not yaml_path.exists():
    return "—"
  try:
    data = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
    rt = data.get("response_text", "")
    m = re.search(r'decision:\s*["\']([^"\']+)["\']', rt)
    if m:
      return m.group(1)
    m = re.search(r'decision:\s*([^\n]+)', rt)
    if m:
      return m.group(1).strip().strip('"').strip("'")
    return "(no_decision)"
  except Exception as e:
    return f"err:{e}"


def short(d: str) -> str:
  if "案 1" in d or "案1" in d:
    return "案1"
  if "案 2" in d or "案2" in d:
    return "案2"
  if "別案" in d:
    return "別案"
  if "深掘り" in d:
    return "深掘"
  if d == "—":
    return "—"
  return d[:6]


# 表ヘッダ
print(f"{'topic':<8} {'ID':<6} {'判定':<6} | " + " ".join(f"{n:<10}" for _, n in MODELS) + " | 一致度")
print("-" * 110)

stats = {"案1": 0, "案2": 0, "別案": 0, "深掘": 0, "?": 0}
agreement_stats = {}

for t in TOPIC_RANGE:
  fid, jclass = TOPIC_TO_ID[t]
  decisions = []
  for mfile, mname in MODELS:
    d = extract_decision(results_dir / f"topic-{t}-{mfile}.yaml", results_dir / f"topic-{t}-{mfile}-turn2.yaml")
    decisions.append(short(d))

  # 一致度
  has_question = "深掘" in decisions
  counts = {}
  for d in decisions:
    if d != "深掘":
      counts[d] = counts.get(d, 0) + 1
  if counts:
    top_count = max(counts.values())
  else:
    top_count = 0

  if has_question:
    agree = "深掘り発火"
  elif top_count == len(MODELS):
    agree = "完全一致"
  elif top_count == len(MODELS) - 1:
    agree = f"準一致({len(MODELS)-1}/{len(MODELS)})"
  else:
    agree = f"分岐({len(MODELS)-2}/{len(MODELS)}以下)"

  agreement_stats.setdefault(agree, 0)
  agreement_stats[agree] += 1

  dec_str = " ".join(f"{d:<10}" for d in decisions)
  print(f"topic-{t:<3} {fid:<6} {jclass:<6} | {dec_str} | {agree}")

print()
print("=== 一致度分布 ===")
for k, v in agreement_stats.items():
  print(f"  {k}: {v} 件")

print()
print("=== モデル別判定分布 ===")
for mfile, mname in MODELS:
  cnt = {"案1": 0, "案2": 0, "別案": 0, "深掘": 0, "?": 0}
  for t in TOPIC_RANGE:
    d = short(extract_decision(results_dir / f"topic-{t}-{mfile}.yaml", results_dir / f"topic-{t}-{mfile}-turn2.yaml"))
    if d in cnt:
      cnt[d] += 1
    else:
      cnt["?"] += 1
  print(f"  {mname:<14}: 案1={cnt['案1']:>2} 案2={cnt['案2']:>2} 別案={cnt['別案']:>2} 深掘={cnt['深掘']:>2} ?={cnt['?']:>2}")
