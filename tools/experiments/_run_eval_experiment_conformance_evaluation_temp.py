"""tools/experiments/_run_eval_experiment_conformance_evaluation_temp.py

conformance-evaluation tasks の 7 モデル比較実験を 5 API モデル並列で実行する一時スクリプト。
セッション 39（2026-05-29）の conformance-evaluation tasks 7 モデル比較実験で使用、後で削除予定。

並列度 5（モデル単位）、各モデルが 10 件（topic-111〜topic-120）を順次実行。

起動方法（重要）：API キーは zsh ログインシェル経由でのみ読める。venv の python を使う。
  zsh -c 'source ~/.zshrc && .venv/bin/python3 tools/experiments/_run_eval_experiment_conformance_evaluation_temp.py'

出力：tools/experiments/results/topic-NN-MODEL.yaml（60 ファイル想定）
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

# topic-99〜topic-110（12 件）
TOPIC_NUMBERS = list(range(111, 121))

# 5 API モデル並列実行（Sonnet 4.6 CLI は Agent ツール経由で別途実施、Opus 4.7 は本人が直接判定）
MODELS = [
  ("anthropic-api", "claude-sonnet-4-6", "sonnet-4-6-api"),
  ("openai-api", "gpt-5.5", "gpt-5-5"),
  ("openai-api", "gpt-5.4", "gpt-5-4"),
  ("gemini-api", "gemini-3.5-flash", "gemini-3-5-flash"),
  ("gemini-api", "gemini-3.1-pro-preview", "gemini-3-1-pro-preview"),
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
  """1 model で 12 件を順次実行。"""
  results = []
  for topic_num in TOPIC_NUMBERS:
    r = run_one_topic_for_model(provider, model, output_suffix, topic_num)
    results.append(r)
    status = "OK" if r["status"] == "ok" else "NG"
    print(f"  [{output_suffix}] topic-{topic_num} {status} ({r['duration']:.1f}s)", flush=True)
  return results


def main() -> int:
  print(f"conformance-evaluation tasks 7 モデル比較実験：5 API モデル × 10 件 = 50 件")
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
