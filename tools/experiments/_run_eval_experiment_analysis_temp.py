"""tools/experiments/_run_eval_experiment_analysis_temp.py

analysis tasks の 7 モデル比較実験を 5 モデル並列で実行する一時スクリプト。
セッション 36（2026-05-28）の analysis tasks 7 モデル比較実験で使用、後で削除予定。

並列度 5（モデル単位）、各モデルが 23 件（topic-53〜topic-75）を順次実行。
API レート制限と OS リソース制限への配慮としてモデル単位並列を選択。

出力：tools/experiments/results/topic-NN-MODEL.yaml（115 ファイル想定）
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

# topic-53〜topic-75（23 件）
TOPIC_NUMBERS = list(range(53, 76))

# 5 API モデル並列実行（Sonnet 4.6 CLI は Agent ツール経由で別途実施）
# 本セッション 36：GPT 系のみリラン（Sonnet 4.6 API ／ Gemini 系は 1 回目で成功済み 69 件）
MODELS = [
  ("openai-api", "gpt-5.5", "gpt-5-5"),
  ("openai-api", "gpt-5.4", "gpt-5-4"),
]


def run_one_topic_for_model(provider: str, model: str, output_suffix: str, topic_num: int) -> dict:
  """1 topic × 1 model の実験を実行し、結果を保存。"""
  prompt_file = PROMPTS_DIR / f"topic-{topic_num}.txt"
  output_file = RESULTS_DIR / f"topic-{topic_num}-{output_suffix}.yaml"
  log_file = LOGS_DIR / f"topic-{topic_num}-{output_suffix}.log"

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
  """1 model で 23 件を順次実行。"""
  results = []
  for topic_num in TOPIC_NUMBERS:
    r = run_one_topic_for_model(provider, model, output_suffix, topic_num)
    results.append(r)
    status = "OK" if r["status"] == "ok" else "NG"
    print(f"  [{output_suffix}] topic-{topic_num} {status} ({r['duration']:.1f}s)", flush=True)
  return results


def main() -> int:
  print(f"analysis tasks 7 モデル比較実験：5 API モデル × 23 件 = 115 件")
  print(f"並列度 5（モデル単位）、各モデル順次実行")
  print()

  overall_start = time.time()
  all_results = []

  with ThreadPoolExecutor(max_workers=5) as ex:
    futures = {ex.submit(run_one_model_all_topics, p, m, s): s for p, m, s in MODELS}
    for f in as_completed(futures):
      suffix = futures[f]
      try:
        results = f.result()
        all_results.extend(results)
        ok_count = sum(1 for r in results if r["status"] == "ok")
        print(f"\n[{suffix}] 完了：{ok_count}/{len(results)} OK\n")
      except Exception as e:
        print(f"\n[{suffix}] エラー：{e}\n")

  overall_duration = time.time() - overall_start
  ok_total = sum(1 for r in all_results if r["status"] == "ok")
  print(f"\n===== 集計 =====")
  print(f"全体所要時間：{overall_duration:.1f} 秒（{overall_duration/60:.1f} 分）")
  print(f"成功：{ok_total}/{len(all_results)} 件")
  if ok_total < len(all_results):
    print("失敗件数：")
    for r in all_results:
      if r["status"] != "ok":
        print(f"  topic-{r['topic']} {r['model']}: returncode={r.get('returncode')}")
  return 0 if ok_total == len(all_results) else 1


if __name__ == "__main__":
  raise SystemExit(main())
