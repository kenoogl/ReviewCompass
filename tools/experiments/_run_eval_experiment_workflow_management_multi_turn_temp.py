"""tools/experiments/_run_eval_experiment_workflow_management_multi_turn_temp.py

workflow-management tasks 7 モデル比較実験：質問返し 13 件への 2 ターン目実行。
proxy_responses_workflow_management_temp.yaml の代理回答を history-file に組み込み、
_experiment_n_model.py を呼び出して最終判定を取得する。

セッション 38（2026-05-28）作成、後で削除予定。

起動方法：zsh -c 'source ~/.zshrc && .venv/bin/python3 tools/experiments/_run_eval_experiment_workflow_management_multi_turn_temp.py'

出力：tools/experiments/results/topic-NN-MODEL-final.yaml（13 ファイル）
"""
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent.parent
EXPERIMENT_SCRIPT = ROOT / "tools" / "experiments" / "_experiment_n_model.py"
PROMPTS_DIR = ROOT / "tools" / "experiments" / "prompts"
RESULTS_DIR = ROOT / "tools" / "experiments" / "results"
PROXY_FILE = ROOT / "tools" / "experiments" / "proxy_responses_workflow_management_temp.yaml"

# 質問返し 13 件：(topic, model_suffix, provider, model_name)
TARGETS = [
  (77, "sonnet-4-6-api", "anthropic-api", "claude-sonnet-4-6"),
  (79, "sonnet-4-6-api", "anthropic-api", "claude-sonnet-4-6"),
  (85, "sonnet-4-6-api", "anthropic-api", "claude-sonnet-4-6"),
  (87, "sonnet-4-6-api", "anthropic-api", "claude-sonnet-4-6"),
  (77, "gemini-3-5-flash", "gemini-api", "gemini-3.5-flash"),
  (78, "gemini-3-5-flash", "gemini-api", "gemini-3.5-flash"),
  (79, "gemini-3-5-flash", "gemini-api", "gemini-3.5-flash"),
  (81, "gemini-3-5-flash", "gemini-api", "gemini-3.5-flash"),
  (84, "gemini-3-5-flash", "gemini-api", "gemini-3.5-flash"),
  (87, "gemini-3-5-flash", "gemini-api", "gemini-3.5-flash"),
  (89, "gemini-3-5-flash", "gemini-api", "gemini-3.5-flash"),
  (91, "gemini-3-5-flash", "gemini-api", "gemini-3.5-flash"),
  (98, "gemini-3-5-flash", "gemini-api", "gemini-3.5-flash"),
]

PROXY_DATA = yaml.safe_load(PROXY_FILE.read_text(encoding="utf-8"))


def get_proxy_response(topic: int, model_suffix: str) -> str:
  """proxy_responses_workflow_management_temp.yaml から該当する代理回答を取得。"""
  for entry in PROXY_DATA["proxy_responses"]:
    if entry["topic"] == topic and entry["model"] == model_suffix:
      return entry["response"]
  raise ValueError(f"proxy response not found: topic={topic} model={model_suffix}")


def run_one(topic: int, model_suffix: str, provider: str, model_name: str) -> dict:
  """1 件の 2 ターン目実行。"""
  start = time.time()
  try:
    proxy_response = get_proxy_response(topic, model_suffix)
    turn1_prompt = (PROMPTS_DIR / f"topic-{topic}.txt").read_text(encoding="utf-8")
    turn1_response_data = yaml.safe_load(
      (RESULTS_DIR / f"topic-{topic}-{model_suffix}.yaml").read_text(encoding="utf-8")
    )
    turn1_response = turn1_response_data["response_text"]

    history = [
      {"role": "user", "content": turn1_prompt},
      {"role": "assistant", "content": turn1_response},
    ]

    turn2_prompt = (
      proxy_response
      + "\n\n上記の追加情報を踏まえて、改めて当初の所見について判定をお願いします。"
      + "プロンプトで指定された YAML 形式（decision／rationale／confidence／"
      + "case_scores 等）で回答してください。"
    )

    with tempfile.NamedTemporaryFile(
      mode="w", suffix=".yaml", delete=False, encoding="utf-8"
    ) as hf:
      yaml.dump(history, hf, allow_unicode=True)
      history_path = hf.name

    with tempfile.NamedTemporaryFile(
      mode="w", suffix=".txt", delete=False, encoding="utf-8"
    ) as pf:
      pf.write(turn2_prompt)
      prompt_path = pf.name

    result = subprocess.run(
      [
        sys.executable, str(EXPERIMENT_SCRIPT),
        "--provider", provider,
        "--model", model_name,
        "--prompt-file", prompt_path,
        "--history-file", history_path,
        "--turn-number", "2",
      ],
      capture_output=True,
      text=True,
      timeout=300,
    )
    duration = time.time() - start

    output_file = RESULTS_DIR / f"topic-{topic}-{model_suffix}-final.yaml"
    if result.returncode == 0:
      output_file.write_text(result.stdout, encoding="utf-8")

    Path(history_path).unlink(missing_ok=True)
    Path(prompt_path).unlink(missing_ok=True)

    return {
      "topic": topic, "model": model_suffix,
      "status": "ok" if result.returncode == 0 else "error",
      "duration": duration,
      "stderr": result.stderr if result.returncode != 0 else "",
    }
  except Exception as e:
    return {
      "topic": topic, "model": model_suffix,
      "status": "exception",
      "duration": time.time() - start,
      "error": str(e),
    }


def main() -> int:
  print(f"質問返し {len(TARGETS)} 件への 2 ターン目実行（並列度 5）")
  print()

  overall_start = time.time()
  results = []

  with ThreadPoolExecutor(max_workers=5) as ex:
    futures = {
      ex.submit(run_one, t, m, p, mn): (t, m)
      for t, m, p, mn in TARGETS
    }
    for f in as_completed(futures):
      t, m = futures[f]
      try:
        r = f.result()
        results.append(r)
        status = "OK" if r["status"] == "ok" else "NG"
        print(f"  topic-{t} {m}: {status} ({r['duration']:.1f}s)", flush=True)
      except Exception as e:
        print(f"  topic-{t} {m}: EXCEPTION {e}")

  ok_count = sum(1 for r in results if r["status"] == "ok")
  print(f"\n===== 集計 =====")
  print(f"全体所要時間：{time.time()-overall_start:.1f} 秒")
  print(f"成功：{ok_count}/{len(results)} 件")
  for r in results:
    if r["status"] != "ok":
      print(f"  失敗 topic-{r['topic']} {r['model']}: {r.get('error', r.get('stderr', ''))[:200]}")
  return 0 if ok_count == len(results) else 1


if __name__ == "__main__":
  raise SystemExit(main())
