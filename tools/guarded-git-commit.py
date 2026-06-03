#!/usr/bin/env python3
"""ユーザ承認レコードを検査してから git commit を実行する薄いラッパー"""

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


DEFAULT_COMMIT_APPROVAL_PATH = ".reviewcompass/approvals/commit-approval.json"


def consume_commit_approval(cwd):
  """commit 成功後に承認レコードを消費済みにする"""
  approval_path = Path(cwd) / DEFAULT_COMMIT_APPROVAL_PATH
  try:
    approval = json.loads(approval_path.read_text(encoding="utf-8"))
  except (OSError, json.JSONDecodeError) as e:
    print(f"warning: 承認レコードの消費済み記録に失敗しました: {e}", file=sys.stderr)
    return

  if not isinstance(approval, dict):
    print("warning: 承認レコードが object ではないため消費済みにできません", file=sys.stderr)
    return

  if approval.get("expires_after_commit") is False:
    return

  approval["consumed"] = True
  approval["consumed_at"] = datetime.now(timezone.utc).isoformat()
  try:
    approval_path.write_text(
      json.dumps(approval, ensure_ascii=False, indent=2) + "\n",
      encoding="utf-8",
    )
  except OSError as e:
    print(f"warning: 承認レコードの消費済み記録に失敗しました: {e}", file=sys.stderr)


def run_precheck(cwd, rationale):
  """commit 事前検査を実行する"""
  script = Path(__file__).resolve().parent / "check-workflow-action.py"
  return subprocess.run(
    ["python3", str(script), "commit", "--rationale", rationale],
    cwd=str(cwd),
    capture_output=True,
    text=True,
  )


def run_git_commit(cwd, messages):
  """git commit を実行する"""
  cmd = ["git", "commit"]
  for message in messages:
    cmd.extend(["-m", message])
  return subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True)


def main(argv=None):
  """エントリポイント"""
  parser = argparse.ArgumentParser(
    description="check-workflow-action.py commit を通してから git commit する"
  )
  parser.add_argument(
    "-m",
    "--message",
    action="append",
    required=True,
    help="git commit に渡すメッセージ。複数指定可",
  )
  parser.add_argument(
    "--rationale",
    required=True,
    help="この commit を行う理由。ユーザ承認の出典を含めること",
  )
  parser.add_argument(
    "--allow-warn",
    action="store_true",
    help="事前検査が WARN の場合も commit を続行する",
  )
  args = parser.parse_args(argv)

  cwd = Path.cwd()
  precheck = run_precheck(cwd, args.rationale)
  if precheck.stdout:
    print(precheck.stdout, end="")
  if precheck.stderr:
    print(precheck.stderr, end="", file=sys.stderr)

  if precheck.returncode == 2:
    return 2
  if precheck.returncode == 1 and not args.allow_warn:
    print("error: 事前検査が WARN のため commit を停止しました", file=sys.stderr)
    return 1
  if precheck.returncode not in (0, 1):
    return precheck.returncode

  result = run_git_commit(cwd, args.message)
  if result.stdout:
    print(result.stdout, end="")
  if result.stderr:
    print(result.stderr, end="", file=sys.stderr)
  if result.returncode != 0:
    return result.returncode

  consume_commit_approval(cwd)
  return 0


if __name__ == "__main__":
  sys.exit(main())
