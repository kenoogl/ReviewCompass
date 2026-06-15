#!/usr/bin/env python3
"""proxy_model 裁定レコード（proxy-approval.yaml・decisions/*.yaml）を、正本が受け入れる
形で review-run と裁定入力から生成する。

「事例より正本」（候補7・生成ツールの横展開）：過去の review-run の yaml を手で写すのを
やめ、正本（tools/api_providers/review_triage.py の _approval_errors /
_proxy_decision_errors）が要求する形を組み立てる。生成後に正本の検証へ通し、合格しなければ
生成物を取り消して非ゼロで終了する（fail-closed）。

要件は事例でなく正本から導く:
  - 重要件＝severity が ERROR/CRITICAL、または final_label が must-fix（_is_important_item）
  - 重要件ごとに decisions/*.yaml（approved_by/proxy_model_id/decision_prompt_path/
    selected_option/final_label/rationale/raw_response_path/candidate_options/
    source_raw_paths/rejected_options を必須）
  - proxy-approval.yaml（approved_action/approved_by/review_run_id/各 presented フラグ/
    consumed/approved_finding_ids/approved_final_labels/proxy_model_id/proxy_decisions）
  - source_raw_paths は triage の source_raw_path（rounds.yaml の raw と sha256 一致）

裁定入力（--decisions の YAML）:
  proxy_model_id: gemini-3.1-pro-preview
  decision_prompt_path: proxy-adjudication-prompt.md     # review-run 直下（相対）
  raw_response_path: proxy-adjudication-response.txt      # review-run 直下（相対）
  decisions:
    - finding_id: <triage の finding_id>
      final_label: must-fix | should-fix | leave-as-is
      rationale: "決定理由"
      candidate_options: [must-fix, should-fix, leave-as-is]  # 任意、既定は 3 つ
      rejected_options:                                        # 重要件で必須
        should-fix: "却下理由"
        leave-as-is: "却下理由"

使い方:
  python3 tools/make-proxy-approval.py \\
      --review-run-dir .reviewcompass/evidence/review-runs/<run-id> \\
      --decisions <裁定入力.yaml>
"""
import argparse
import importlib.util
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CANDIDATE_OPTIONS = ["must-fix", "should-fix", "leave-as-is"]


def _load_review_triage():
  pkg_dir = str(REPO_ROOT / "tools")
  if pkg_dir not in sys.path:
    sys.path.insert(0, pkg_dir)
  spec = importlib.util.spec_from_file_location(
    "review_triage_for_make_proxy_approval",
    REPO_ROOT / "tools" / "api_providers" / "review_triage.py")
  m = importlib.util.module_from_spec(spec)
  spec.loader.exec_module(m)
  return m


def _load_yaml(path):
  try:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))
  except (OSError, yaml.YAMLError):
    return None


def _dump_yaml(path, data):
  Path(path).parent.mkdir(parents=True, exist_ok=True)
  Path(path).write_text(
    yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")


def _finding_suffix(finding_id, run_id):
  prefix = f"{run_id}-"
  return finding_id[len(prefix):] if finding_id.startswith(prefix) else finding_id


def main():
  parser = argparse.ArgumentParser(
    description="proxy_model 裁定レコードを review-run から正本準拠で生成する")
  parser.add_argument("--review-run-dir", required=True, help="対象 review-run（cwd 相対）")
  parser.add_argument("--decisions", required=True, help="裁定入力 YAML のパス")
  args = parser.parse_args()

  cwd = Path.cwd()
  run_dir = cwd / args.review_run_dir
  if not run_dir.is_dir():
    print(f"エラー: review-run ディレクトリがありません: {args.review_run_dir}", file=sys.stderr)
    return 1
  run_id = run_dir.name

  triage = _load_yaml(run_dir / "triage.yaml")
  if not isinstance(triage, dict) or not isinstance(triage.get("items"), list):
    print("エラー: triage.yaml を読めません（items が配列でない）", file=sys.stderr)
    return 1
  items_by_id = {it.get("finding_id"): it for it in triage["items"]
                 if isinstance(it, dict)}

  spec_in = _load_yaml(args.decisions)
  if not isinstance(spec_in, dict) or not isinstance(spec_in.get("decisions"), list):
    print("エラー: 裁定入力を読めません（decisions が配列でない）", file=sys.stderr)
    return 1
  proxy_model_id = spec_in.get("proxy_model_id")
  decision_prompt_path = spec_in.get("decision_prompt_path")
  raw_response_path = spec_in.get("raw_response_path")
  for key, val in (("proxy_model_id", proxy_model_id),
                   ("decision_prompt_path", decision_prompt_path),
                   ("raw_response_path", raw_response_path)):
    if not isinstance(val, str) or not val.strip():
      print(f"エラー: 裁定入力に {key} がありません", file=sys.stderr)
      return 1

  rt = _load_review_triage()

  important_labels = {}
  proxy_decisions = {}
  written = []  # 失敗時に取り消すために記録
  decisions_dir = run_dir / "decisions"

  for dec in spec_in["decisions"]:
    if not isinstance(dec, dict):
      continue
    fid = dec.get("finding_id")
    final_label = dec.get("final_label")
    item = items_by_id.get(fid)
    if item is None:
      print(f"エラー: finding_id が triage に存在しません: {fid}", file=sys.stderr)
      return 1
    if not isinstance(final_label, str) or not final_label.strip():
      print(f"エラー: {fid} に final_label がありません", file=sys.stderr)
      return 1

    # 重要件かは正本の判定に委ねる（severity ERROR/CRITICAL または must-fix）
    if not rt._is_important_item(item, final_label):
      continue

    suffix = _finding_suffix(fid, run_id)
    decision_ref = f"decisions/{suffix}.yaml"
    decision = {
      "approved_by": "proxy_model",
      "finding_id": fid,
      "proxy_model_id": proxy_model_id,
      "decision_prompt_path": decision_prompt_path,
      "selected_option": final_label,
      "final_label": final_label,
      "rationale": dec.get("rationale"),
      "raw_response_path": raw_response_path,
      "candidate_options": dec.get("candidate_options") or list(DEFAULT_CANDIDATE_OPTIONS),
      "rejected_options": dec.get("rejected_options"),
      "source_raw_paths": [item.get("source_raw_path")],
    }
    _dump_yaml(decisions_dir / f"{suffix}.yaml", decision)
    written.append(decisions_dir / f"{suffix}.yaml")
    important_labels[fid] = final_label
    proxy_decisions[fid] = decision_ref

  approval = {
    "approved_action": "review_triage_decide",
    "approved_by": "proxy_model",
    "review_run_id": run_id,
    "summary_presented_to_user": True,
    "triage_presented_to_user": True,
    "consumed": False,
    "approved_finding_ids": list(important_labels.keys()),
    "approved_final_labels": dict(important_labels),
    "proxy_model_id": proxy_model_id,
    "proxy_decisions": proxy_decisions,
  }
  approval_path = run_dir / "proxy-approval.yaml"
  _dump_yaml(approval_path, approval)
  written.append(approval_path)

  # 正本で自己検証（fail-closed）
  errors = rt._approval_errors(
    approval,
    run_dir,
    approval_path,
    rt.TRIAGE_DECIDE_APPROVAL_ACTIONS,
    list(important_labels.keys()),
    dict(important_labels),
  )
  if errors:
    for path in written:
      try:
        path.unlink()
      except OSError:
        pass
    print("エラー: 生成物が正本検証（_approval_errors）を通りませんでした（書き込みを取り消し）:",
          file=sys.stderr)
    for e in errors:
      print("  -", e, file=sys.stderr)
    return 3

  print(f"proxy 裁定レコード生成: {approval_path}"
        f"（重要件 {len(important_labels)} 件、正本検証 OK）")
  return 0


if __name__ == "__main__":
  sys.exit(main())
