#!/usr/bin/env python3
"""書き込み後検証 manifest を、正本が「completed」と判定する形で review-run から生成する。

「事例より正本」（案2・2026-06-14）：過去の manifest を手で写すのをやめ、正本
（check-workflow-action.py の evaluate_post_write_manifest_state /
review_run_traceability_satisfied）が要求する形を review-run から組み立てる。生成後に
正本の判定へ通し、completed にならなければ非ゼロで終了する（fail-closed）。

要件は事例でなく正本から導く:
  - review_run の rounds.yaml の model_results から検証者（model_id）を取る
  - triage.yaml の未解決（decision_status != decided）件数を unresolved_substantive_findings に
  - target_files が対象を網羅し、target_sha256 が現在のファイル内容と一致
  - status=completed は未解決0かつ正本判定が completed のときだけ

使い方:
  python3 tools/make-post-write-manifest.py \\
      --review-run-dir .reviewcompass/evidence/review-runs/<run-id> \\
      --target TODO_NEXT_SESSION.md [--target 別ファイル ...] \\
      --out .reviewcompass/post-write-verification/post-write-YYYY-MM-DD-NNN.yaml \\
      [--notes "..."]
"""
import argparse
import importlib.util
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent


def _load_cwa():
  tools_dir = str(REPO_ROOT / "tools")
  if tools_dir not in sys.path:
    sys.path.insert(0, tools_dir)
  spec = importlib.util.spec_from_file_location(
    "cwa_for_make_post_write_manifest",
    REPO_ROOT / "tools" / "check-workflow-action.py")
  m = importlib.util.module_from_spec(spec)
  spec.loader.exec_module(m)
  return m


def _load_yaml(path):
  try:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))
  except (OSError, yaml.YAMLError):
    return None


def main():
  parser = argparse.ArgumentParser(
    description="書き込み後検証 manifest を review-run から正本準拠で生成する")
  parser.add_argument("--review-run-dir", required=True,
                      help="検証 review-run ディレクトリ（cwd 相対）")
  parser.add_argument("--target", action="append", required=True,
                      help="検証対象ファイル（複数指定可、cwd 相対）")
  parser.add_argument("--out", required=True,
                      help="manifest 出力先。正本が読む "
                           ".reviewcompass/post-write-verification/ 配下を指定すること")
  parser.add_argument("--notes", help="manifest の notes（任意）")
  args = parser.parse_args()

  cwd = Path.cwd()
  cwa = _load_cwa()

  run_dir = cwd / args.review_run_dir
  if not run_dir.is_dir():
    print(f"エラー: review-run ディレクトリがありません: {args.review_run_dir}",
          file=sys.stderr)
    return 1

  rounds = _load_yaml(run_dir / "rounds.yaml")
  triage = _load_yaml(run_dir / "triage.yaml")
  if not isinstance(rounds, dict) or not isinstance(triage, dict):
    print("エラー: rounds.yaml / triage.yaml を読めません", file=sys.stderr)
    return 1

  model_results = rounds.get("model_results")
  if not isinstance(model_results, list) or not model_results:
    print("エラー: rounds.yaml に model_results がありません", file=sys.stderr)
    return 1
  verifiers = sorted({r.get("model_id") for r in model_results if r.get("model_id")})
  if not verifiers:
    print("エラー: 検証者（model_id）を特定できません", file=sys.stderr)
    return 1

  # 未解決の本質的指摘＝triage の decided 以外（human_required・未判定を含む）
  items = triage.get("items")
  if not isinstance(items, list):
    print("エラー: triage.yaml の items が配列ではありません", file=sys.stderr)
    return 1
  unresolved = sum(1 for it in items
                   if isinstance(it, dict) and it.get("decision_status") != "decided")

  # 対象ファイルのハッシュ（現在の内容。正本は commit 時に現ファイルと突き合わせる）
  target_sha256 = {}
  for t in args.target:
    h = cwa.file_sha256(cwd / t)
    if not h:
      print(f"エラー: 対象ファイルを読めません: {t}", file=sys.stderr)
      return 1
    target_sha256[t] = h

  manifest = {
    "status": "completed" if unresolved == 0 else "human_required",
    "target_files": list(args.target),
    "target_sha256": target_sha256,
    "required_verifiers": verifiers,
    "completed_verifiers": verifiers,
    "unresolved_substantive_findings": unresolved,
    "verifications": [
      {
        "verifier": v,
        "target_files": list(args.target),
        "target_sha256": dict(target_sha256),
      }
      for v in verifiers
    ],
    "review_run": {
      "path": args.review_run_dir,
      "summary_path": str(Path(args.review_run_dir) / "model-result-summary.yaml"),
    },
  }
  if args.notes:
    manifest["notes"] = args.notes

  out = cwd / args.out
  out.parent.mkdir(parents=True, exist_ok=True)
  out.write_text(
    yaml.safe_dump(manifest, allow_unicode=True, sort_keys=False), encoding="utf-8")

  # 正本で自己検証（fail-closed）
  status, _ = cwa.evaluate_post_write_manifest_state(str(cwd), list(args.target))
  if unresolved > 0:
    print(f"未解決の本質的指摘が {unresolved} 件あります（正本判定: {status}）。"
          "人へ上げて解消するまで commit できません。", file=sys.stderr)
    print(f"manifest 生成: {out}（status={manifest['status']}）")
    return 3
  if status != "completed":
    print(f"エラー: 生成 manifest が正本で completed になりません（判定: {status}）。"
          "review-run の整合を確認してください。", file=sys.stderr)
    return 3

  print(f"manifest 生成: {out}（検証者 {len(verifiers)} 体、正本判定 completed）")
  return 0


if __name__ == "__main__":
  sys.exit(main())
