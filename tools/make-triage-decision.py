#!/usr/bin/env python3
"""トリアージ（所見の仕分け）決定を review-run に記録し、関係ファイルを正本どおり整合させる。

「事例より正本」（§4-7 拡大・2026-06-14）：トリアージ決定を手で記録すると、triage.yaml と
model-result-summary.yaml を 2 か所そろえる必要があり、ラベル表記（leave-as-is を
leave_as_is と書く等）や件数の同期ミスが起きやすい。本ツールは決定を triage.yaml に書き、
model-result-summary.yaml の triage_status と件数を triage から再計算し、全件 decided なら
正本（check-workflow-action.py の review_run_traceability_satisfied）へ通して fail-closed する。

使い方:
  python3 tools/make-triage-decision.py \\
      --review-run-dir .reviewcompass/evidence/review-runs/<run-id> \\
      --finding-id <id> \\
      --label {must-fix|should-fix|leave-as-is} \\
      --reason "決定理由" \\
      [--actor user] [--decided-at 2026-06-14T23:50:00+00:00]
"""
import argparse
import importlib.util
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
VALID_LABELS = ("must-fix", "should-fix", "leave-as-is")


def _load_cwa():
  tools_dir = str(REPO_ROOT / "tools")
  if tools_dir not in sys.path:
    sys.path.insert(0, tools_dir)
  spec = importlib.util.spec_from_file_location(
    "cwa_for_make_triage_decision",
    REPO_ROOT / "tools" / "check-workflow-action.py")
  m = importlib.util.module_from_spec(spec)
  spec.loader.exec_module(m)
  return m


def _load_yaml(path):
  try:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))
  except (OSError, yaml.YAMLError):
    return None


def _dump_yaml(path, data):
  Path(path).write_text(
    yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")


def _recompute_summary(summary, triage_items):
  """model-result-summary の各モデルの triage_status と件数を triage から再計算する。"""
  by_model = {}
  for it in triage_items:
    if isinstance(it, dict):
      by_model.setdefault(it.get("source_model"), []).append(it)
  for model in summary.get("models") or []:
    if not isinstance(model, dict):
      continue
    items = by_model.get(model.get("model_id"))
    if not items:
      continue  # 所見の無いモデル（findings_count 0 → no_findings）はそのまま
    decided = [it for it in items if it.get("decision_status") == "decided"]
    model["must_fix_count"] = sum(1 for it in decided if it.get("final_label") == "must-fix")
    model["should_fix_count"] = sum(1 for it in decided if it.get("final_label") == "should-fix")
    model["leave_as_is_count"] = sum(1 for it in decided if it.get("final_label") == "leave-as-is")
    model["human_required_count"] = sum(
      1 for it in items if it.get("decision_status") == "human_required")
    all_decided = all(it.get("decision_status") == "decided" for it in items)
    model["triage_status"] = "triaged" if all_decided else "triage_pending"
  return summary


def main():
  parser = argparse.ArgumentParser(
    description="トリアージ決定を review-run へ記録し関係ファイルを正本どおり整合させる")
  parser.add_argument("--review-run-dir", required=True, help="対象 review-run（cwd 相対）")
  parser.add_argument("--finding-id", required=True, help="決定する所見の finding_id")
  parser.add_argument("--label", required=True,
                      help="三段階ラベル：must-fix / should-fix / leave-as-is")
  parser.add_argument("--reason", required=True, help="決定理由（出典を含めること）")
  parser.add_argument("--actor", default="user", help="決定者（既定 user）")
  parser.add_argument("--decided-at", help="決定時刻（既定は現在 UTC）。テスト用に注入可")
  args = parser.parse_args()

  if args.label not in VALID_LABELS:
    print(f"エラー: --label は {' / '.join(VALID_LABELS)} のいずれかです（受領: {args.label}）",
          file=sys.stderr)
    return 2

  cwd = Path.cwd()
  run_dir = cwd / args.review_run_dir
  if not run_dir.is_dir():
    print(f"エラー: review-run ディレクトリがありません: {args.review_run_dir}", file=sys.stderr)
    return 1

  triage = _load_yaml(run_dir / "triage.yaml")
  summary = _load_yaml(run_dir / "model-result-summary.yaml")
  rounds = _load_yaml(run_dir / "rounds.yaml")
  if not isinstance(triage, dict) or not isinstance(summary, dict) or not isinstance(rounds, dict):
    print("エラー: triage.yaml / model-result-summary.yaml / rounds.yaml を読めません",
          file=sys.stderr)
    return 1

  items = triage.get("items")
  if not isinstance(items, list):
    print("エラー: triage.yaml の items が配列ではありません", file=sys.stderr)
    return 1
  target = next((it for it in items
                 if isinstance(it, dict) and it.get("finding_id") == args.finding_id), None)
  if target is None:
    print(f"エラー: finding_id が見つかりません: {args.finding_id}", file=sys.stderr)
    return 1

  decided_at = args.decided_at or datetime.now(timezone.utc).isoformat()

  # 決定を記録（書き換えはここから。ラベル・存在検査を通過した後）
  target["final_label"] = args.label
  target["decision_status"] = "decided"
  target["decision_actor"] = args.actor
  target["decision_actor_type"] = "human"
  target["decision_at"] = decided_at
  target["decision_reason"] = args.reason

  all_decided = all(it.get("decision_status") == "decided" for it in items)
  triage["triage_status"] = "decided" if all_decided else "draft"
  triage["decision_actor"] = args.actor
  triage["decision_actor_type"] = "human"
  _dump_yaml(run_dir / "triage.yaml", triage)

  _recompute_summary(summary, items)
  _dump_yaml(run_dir / "model-result-summary.yaml", summary)

  pending = sum(1 for it in items if it.get("decision_status") != "decided")
  if pending > 0:
    print(f"記録: {args.finding_id} を {args.label} に決定。未決定 {pending} 件が残ります"
          "（残りも決定後に正本判定が通ります）。")
    return 0

  # 全件 decided：正本（review_run_traceability_satisfied）へ通して fail-closed
  cwa = _load_cwa()
  model_ids = sorted({r.get("model_id")
                      for r in (rounds.get("model_results") or [])
                      if isinstance(r, dict) and r.get("model_id")})
  manifest = {
    "review_run": {
      "path": args.review_run_dir,
      "summary_path": str(Path(args.review_run_dir) / "model-result-summary.yaml"),
    },
    "required_verifiers": model_ids,
  }
  if not cwa.review_run_traceability_satisfied(str(cwd), manifest):
    print("エラー: 決定後の review-run が正本判定（review_run_traceability_satisfied）を満たしません。"
          "raw/rounds/summary/triage の整合を確認してください。", file=sys.stderr)
    return 3

  print(f"記録: {args.finding_id} を {args.label} に決定。全件 decided・正本判定 OK。")
  return 0


if __name__ == "__main__":
  sys.exit(main())
