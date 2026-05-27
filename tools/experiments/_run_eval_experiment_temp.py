"""tools/experiments/_run_eval_experiment_temp.py

evaluation tasks の 7 モデル比較実験を 5 モデル並列で実行する一時スクリプト。
セッション 33（2026-05-27）の evaluation tasks 7 モデル比較実験で使用、後で削除予定。

並列度 5（モデル単位）、各モデルが 19 件（topic-34〜topic-52）を順次実行。
API レート制限と OS リソース制限への配慮として全件並列ではなくモデル単位並列を選択。

出力：tools/experiments/results/topic-NN-MODEL.yaml（95 ファイル想定）
ログ：tools/experiments/logs/topic-NN-MODEL.log
"""
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
EXPERIMENT_SCRIPT = ROOT / "tools" / "experiments" / "_experiment_n_model.py"
PROMPTS_DIR = ROOT / "tools" / "experiments" / "prompts"
RESULTS_DIR = ROOT / "tools" / "experiments" / "results"
LOGS_DIR = ROOT / "tools" / "experiments" / "logs"

# topic-34〜topic-52（19 件）
TOPIC_NUMBERS = list(range(34, 53))

# 5 モデル並列で実行（Sonnet 4.6 CLI は Agent ツール経由で別途、本スクリプトは API 経由のみ）
# モデル名は runtime セッション 32 実験で実証済の表記に揃える：
# - OpenAI もドット表記（gpt-5.5 / gpt-5.4）
# - Gemini もドット表記（gemini-3.5-flash / gemini-3.1-pro-preview）
# 出力ファイル名 suffix はハイフン表記で既存 results と統一
# 本セッション 33 では Gemini 系のみ再実行（Sonnet API / GPT-5.5 / GPT-5.4 は成功済のため除外）
MODELS = [
  ("gemini-api", "gemini-3.5-flash", "gemini-3-5-flash"),
  ("gemini-api", "gemini-3.1-pro-preview", "gemini-3-1-pro-preview"),
]


def run_one_topic_for_model(provider: str, model: str, output_suffix: str, topic_num: int) -> dict:
  """1 topic × 1 model の実験を実行し、結果を保存。"""
  prompt_file = PROMPTS_DIR / f"topic-{topic_num:02d}.txt"
  output_file = RESULTS_DIR / f"topic-{topic_num:02d}-{output_suffix}.yaml"
  log_file = LOGS_DIR / f"topic-{topic_num:02d}-{output_suffix}.log"

  start = time.time()
  result = subprocess.run(
    [
      sys.executable, str(EXPERIMENT_SCRIPT),
      "--provider", provider,
      "--model", model,
      "--prompt-file", str(prompt_file),
    ],
    capture_output=True,
    text=True,
    timeout=300,  # 5 分
  )
  duration = time.time() - start

  if result.returncode == 0:
    output_file.write_text(result.stdout, encoding="utf-8")
    if result.stderr:
      log_file.write_text(result.stderr, encoding="utf-8")
    return {"topic": topic_num, "model": output_suffix, "status": "ok", "duration": duration}
  else:
    log_file.write_text(f"STDERR:\n{result.stderr}\n\nSTDOUT:\n{result.stdout}", encoding="utf-8")
    return {"topic": topic_num, "model": output_suffix, "status": "error", "duration": duration, "returncode": result.returncode}


def run_one_model_all_topics(provider: str, model: str, output_suffix: str) -> list:
  """1 model で 19 件を順次実行。"""
  results = []
  for topic_num in TOPIC_NUMBERS:
    r = run_one_topic_for_model(provider, model, output_suffix, topic_num)
    results.append(r)
    status = "OK" if r["status"] == "ok" else "NG"
    print(f"  [{output_suffix}] topic-{topic_num:02d} {status} ({r['duration']:.1f}s)", flush=True)
  return results


def main() -> int:
  RESULTS_DIR.mkdir(parents=True, exist_ok=True)
  LOGS_DIR.mkdir(parents=True, exist_ok=True)

  start = time.time()
  print(f"=== evaluation tasks 7 モデル比較実験開始 ===")
  print(f"  対象: topic-34〜topic-52（{len(TOPIC_NUMBERS)} 件）")
  print(f"  モデル: {len(MODELS)} 経路（API 経由のみ、Sonnet CLI は別途 Agent 経由）")
  print(f"  並列度: モデル単位（5 並列、各モデル内は順次）")
  print()

  all_results = []
  with ThreadPoolExecutor(max_workers=len(MODELS)) as executor:
    futures = {executor.submit(run_one_model_all_topics, p, m, o): (p, m, o) for p, m, o in MODELS}
    for future in as_completed(futures):
      p, m, o = futures[future]
      try:
        results = future.result()
        all_results.extend(results)
      except Exception as e:
        print(f"  [{o}] FATAL: {e}", flush=True)

  duration = time.time() - start
  ok_count = sum(1 for r in all_results if r["status"] == "ok")
  ng_count = len(all_results) - ok_count
  print()
  print(f"=== 実験完了 ===")
  print(f"  合計: {len(all_results)} 件（OK {ok_count} 件 / NG {ng_count} 件）")
  print(f"  実時間: {duration:.1f}s（並列実行）")
  print(f"  API 経由合計時間（順次換算）: {sum(r['duration'] for r in all_results):.1f}s")

  if ng_count > 0:
    print()
    print("  NG 一覧:")
    for r in all_results:
      if r["status"] != "ok":
        print(f"    topic-{r['topic']:02d}-{r['model']}: returncode={r.get('returncode', '?')}")

  return 0 if ng_count == 0 else 1


if __name__ == "__main__":
  raise SystemExit(main())
