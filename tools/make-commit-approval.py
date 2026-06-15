#!/usr/bin/env python3
"""commit 用ユーザ承認レコードを、正本が受け入れる形で生成する。

「事例より正本」（案2・2026-06-14）：過去の承認レコードを手で写すのをやめ、正本
（check-workflow-action.py の validate_commit_approval /
validate_commit_execution_delegation）が要求する形をこのツールで組み立てる。生成後に
正本の検証関数へ通し、合格しなければ書き込まない（fail-closed）。

要件は事例でなく正本から導く:
  - approved_action=commit / approved_by=user / consumed=False
  - target_files が staged を網羅し、target_sha256 が staged 内容と一致
  - execution_actor=llm のとき execution_delegation（delegated_to=llm・approved_by=user・
    explicit_instruction が正本の実行代行述語を通る）

使い方:
  python3 tools/make-commit-approval.py \\
      --explicit-instruction コミット \\
      --rationale "利用者『コミット』（発言全文）" \\
      [--instruction-source "..."] [--execution-actor llm|human]
"""
import argparse
import importlib.util
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools"))

from check_workflow_action.runtime_paths import DEFAULT_COMMIT_APPROVAL_PATH


def _load_cwa():
  """正本 check-workflow-action.py を読み込む（ハイフン名のため importlib）。"""
  spec = importlib.util.spec_from_file_location(
    "cwa_for_make_commit_approval",
    REPO_ROOT / "tools" / "check-workflow-action.py")
  m = importlib.util.module_from_spec(spec)
  spec.loader.exec_module(m)
  return m


def _staged_files(cwd):
  out = subprocess.run(
    ["git", "diff", "--cached", "--name-only"],
    cwd=str(cwd), capture_output=True, text=True, check=True).stdout
  return [line for line in out.splitlines() if line.strip()]


def _deleted_staged_files(cwd):
  """git diff --cached --name-status から削除ファイルのセットを返す"""
  out = subprocess.run(
    ["git", "diff", "--cached", "--name-status"],
    cwd=str(cwd), capture_output=True, text=True, check=True).stdout
  deleted = set()
  for line in out.splitlines():
    if line.startswith("D\t"):
      deleted.add(line[2:].strip())
  return deleted


def main():
  parser = argparse.ArgumentParser(
    description="commit 承認レコードを正本準拠で生成する")
  parser.add_argument("--explicit-instruction", required=True,
                      help="利用者の commit 実行指示の機械判定用文字列（例：コミット）")
  parser.add_argument("--rationale", required=True,
                      help="承認の理由。利用者発言の出典を含めること")
  parser.add_argument("--instruction-source",
                      help="指示の出典（任意。発言の文脈など）")
  parser.add_argument("--execution-actor", choices=["llm", "human"], default="llm")
  args = parser.parse_args()

  cwd = Path.cwd()
  cwa = _load_cwa()

  # 正本: 実行代行の指示述語（llm 実行のときのみ要求される）
  if args.execution_actor == "llm":
    if not cwa._is_commit_execution_delegation_instruction(args.explicit_instruction):
      print("エラー: explicit_instruction が正本の実行代行述語を通りません: "
            f"{args.explicit_instruction!r}", file=sys.stderr)
      return 2

  staged = _staged_files(cwd)
  if not staged:
    print("エラー: staged ファイルがありません（git add 後に実行してください）",
          file=sys.stderr)
    return 1

  deleted = _deleted_staged_files(cwd)
  target_sha256 = {}
  for f in staged:
    if f in deleted:
      target_sha256[f] = "DELETED"
    else:
      h = cwa.staged_file_sha256(str(cwd), f)
      if not h:
        print(f"エラー: staged 内容のハッシュ取得に失敗しました: {f}", file=sys.stderr)
        return 1
      target_sha256[f] = h

  approval = {
    "approved_action": "commit",
    "approved_by": "user",
    "consumed": False,
    "expires_after_commit": True,
    "approved_at": datetime.now(timezone.utc).astimezone().isoformat(),
    "rationale": args.rationale,
    "target_files": staged,
    "target_sha256": target_sha256,
  }
  if args.execution_actor == "llm":
    delegation = {
      "delegated_to": "llm",
      "approved_by": "user",
      "explicit_instruction": args.explicit_instruction,
    }
    if args.instruction_source:
      delegation["instruction_source"] = args.instruction_source
    approval["execution_delegation"] = delegation

  out = cwd / DEFAULT_COMMIT_APPROVAL_PATH
  out.parent.mkdir(parents=True, exist_ok=True)
  out.write_text(json.dumps(approval, ensure_ascii=False, indent=2) + "\n",
                 encoding="utf-8")

  # 正本で自己検証（fail-closed）：生成物が正本検証を通らなければ書き込みを取り消す
  state, errors = cwa.validate_commit_approval(str(cwd), staged)
  if args.execution_actor == "llm":
    errors = list(errors) + cwa.validate_commit_execution_delegation(state, "llm")
  if errors:
    out.unlink(missing_ok=True)
    print("エラー: 生成物が正本検証を通りませんでした（書き込みを取り消し）:",
          file=sys.stderr)
    for e in errors:
      print("  -", e, file=sys.stderr)
    return 3

  print(f"承認レコード生成: {out}（target_files {len(staged)} 件、正本検証 OK）")
  return 0


if __name__ == "__main__":
  sys.exit(main())
