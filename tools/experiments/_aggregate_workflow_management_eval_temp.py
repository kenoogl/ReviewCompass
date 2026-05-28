"""tools/experiments/_aggregate_workflow_management_eval_temp.py

workflow-management tasks の 7 モデル比較実験結果（topic-76〜topic-98、23 件 × 7 モデル ＝ 161 件）
を集計する一時スクリプト。セッション 38（2026-05-28）で使用、後で削除予定。

各 topic で 7 モデルの判定（decision）を抽出し、一致状況をまとめる。
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
RESULTS_DIR = ROOT / "tools" / "experiments" / "results"

TOPIC_NUMBERS = list(range(76, 99))

MODELS = [
  ("opus-4-7", "Opus 4.7"),
  ("sonnet-4-6-cli", "Sonnet 4.6 CLI"),
  ("sonnet-4-6-api", "Sonnet 4.6 API"),
  ("gpt-5-5", "GPT-5.5"),
  ("gpt-5-4", "GPT-5.4"),
  ("gemini-3-5-flash", "Gemini-3.5-flash"),
  ("gemini-3-1-pro-preview", "Gemini-3.1-pro"),
]

# 各トピックの finding_id（参考用）
FINDING_IDS = {
  76: ("F-006", "must"), 77: ("F-008", "must"), 78: ("F-009", "must"),
  79: ("F-012", "must"), 80: ("F-015", "must"), 81: ("A-004", "must"),
  82: ("F-001", "should"), 83: ("F-003", "should"), 84: ("F-004", "should"),
  85: ("F-007", "should"), 86: ("F-010", "should"), 87: ("F-011", "should"),
  88: ("F-013", "should"), 89: ("F-016", "should"), 90: ("F-017", "should"),
  91: ("F-018", "should"), 92: ("F-019", "should"), 93: ("F-020", "should"),
  94: ("A-005", "should"), 95: ("A-006", "should"), 96: ("A-007", "should"),
  97: ("A-008", "should"), 98: ("A-010", "should"),
}


def extract_decision(yaml_text: str) -> str:
  """YAML テキストから decision フィールドの値を抽出（response_text 内含む）。"""
  m = re.search(
    r'decision:\s*\\?["\']?\s*(採用[：:]?\s*案\s*[12]|別案を提示|深掘り要求)',
    yaml_text,
  )
  if m:
    return m.group(1).replace(" ", "").replace(":", "：")
  return "?"


def short(decision: str) -> str:
  """decision を短い記号に変換。"""
  mapping = {
    "採用：案1": "案1", "採用:案1": "案1",
    "採用：案2": "案2", "採用:案2": "案2",
    "別案を提示": "別案", "深掘り要求": "深掘",
    "?": "?",
  }
  return mapping.get(decision, decision)


def build_rows(use_final: bool) -> list:
  """各トピック × モデルの判定を集計。use_final=True なら -final.yaml を優先。"""
  rows = []
  for topic in TOPIC_NUMBERS:
    fid, kind = FINDING_IDS[topic]
    row = {"topic": topic, "finding_id": fid, "kind": kind, "decisions": {}}
    for suffix, label in MODELS:
      final_path = RESULTS_DIR / f"topic-{topic}-{suffix}-final.yaml"
      turn1_path = RESULTS_DIR / f"topic-{topic}-{suffix}.yaml"

      if use_final and final_path.exists():
        text = final_path.read_text(encoding="utf-8")
      elif turn1_path.exists():
        text = turn1_path.read_text(encoding="utf-8")
      else:
        row["decisions"][label] = "欠"
        continue
      row["decisions"][label] = short(extract_decision(text))
    rows.append(row)
  return rows


def print_table(rows, title) -> None:
  print(f"\n## {title}\n")
  header = "| topic | 所見 | 種別 | " + " | ".join(label for _, label in MODELS) + " | 一致 |"
  separator = "|---|---|---|" + "|".join(["---"] * (len(MODELS) + 1)) + "|"
  print(header)
  print(separator)

  for row in rows:
    decisions = [row["decisions"][label] for _, label in MODELS]
    unique = set(d for d in decisions if d not in ("?", "欠"))
    if len(unique) == 1:
      agreement = f"完全一致（{list(unique)[0]}）"
    elif len(unique) == 2:
      from collections import Counter
      c = Counter(decisions)
      most = c.most_common(2)
      agreement = f"分割（{most[0][0]} {most[0][1]} ／ {most[1][0]} {most[1][1]}）"
    else:
      agreement = f"分散（{len(unique)} 案）"
    cols = [f"topic-{row['topic']}", row["finding_id"], row["kind"]] + decisions + [agreement]
    print("| " + " | ".join(cols) + " |")

  total = len(rows)
  full_agreement = sum(1 for r in rows if len(set(r["decisions"][l] for _, l in MODELS) - {"?", "欠"}) == 1)
  print(f"\n集計：{total} topic 中、完全一致 {full_agreement} 件、割れ {total - full_agreement} 件")


def main() -> int:
  # 表 1：1 ターン目応答（質問返しを含む）
  rows_turn1 = build_rows(use_final=False)
  print_table(rows_turn1, "表 1：1 ターン目応答の分布（モデルの自信度・質問能力の代理指標）")

  # 表 2：最終判定（-final.yaml 優先）
  rows_final = build_rows(use_final=True)
  print_table(rows_final, "表 2：最終判定の分布（マルチターン続行後）")
  return 0


if __name__ == "__main__":
  raise SystemExit(main())
