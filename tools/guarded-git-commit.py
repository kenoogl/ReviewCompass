#!/usr/bin/env python3
"""ユーザ承認レコードを検査してから git commit を実行する薄いラッパー"""

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


# 実行時生成物の runtime 区画集約（2026-06-12 配置規約 P1）。旧配置は凍結・読み取り互換のみ P3 まで。
# 定数と読み取り解決の正本は check_workflow_action/runtime_paths.py
from check_workflow_action.runtime_paths import (
  DEFAULT_COMMIT_APPROVAL_PATH,
  resolve_commit_approval_path,
)

DEFAULT_LAST_COMMIT_PRECHECK_PATH = ".git/reviewcompass/last-commit-precheck.json"


def _mark_consumed(path, consumed_at):
  """JSON object record を consumed として永続化する。"""
  try:
    record = json.loads(path.read_text(encoding="utf-8"))
  except (OSError, json.JSONDecodeError) as e:
    return False, f"{path}: {e}"

  if not isinstance(record, dict):
    return False, f"{path}: record is not an object"

  record["consumed"] = True
  record["consumed_at"] = consumed_at
  try:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
      json.dumps(record, ensure_ascii=False, indent=2) + "\n",
      encoding="utf-8",
    )
  except OSError as e:
    return False, f"{path}: {e}"
  return True, record


def consume_commit_approval(cwd):
  """commit 成功後に承認レコードと nonce challenge を消費済みにする。

  読み取りは新→旧の順のフォールバック。承認レコードの書き込みは常に新配置へ行い、
  凍結済み旧記録は変更しない（wm design §実行時生成物の凍結期（P3 まで）の扱い）。
  """
  read_path = Path(cwd) / resolve_commit_approval_path(cwd)
  try:
    approval = json.loads(read_path.read_text(encoding="utf-8"))
  except (OSError, json.JSONDecodeError) as e:
    print(f"error: 承認レコードの消費済み記録に失敗しました: {e}", file=sys.stderr)
    return False
  if not isinstance(approval, dict):
    print("error: 承認レコードが object ではないため消費済みにできません", file=sys.stderr)
    return False

  if approval.get("expires_after_commit") is False:
    return True

  consumed_at = datetime.now(timezone.utc).isoformat()
  if approval.get("nonce"):
    challenge_ref = approval.get("challenge_path")
    if not isinstance(challenge_ref, str) or not challenge_ref:
      print("error: nonce 承認の challenge_path がありません", file=sys.stderr)
      return False
    challenge_path = Path(cwd) / challenge_ref
    ok, result = _mark_consumed(challenge_path, consumed_at)
    if not ok:
      print(f"error: challenge の消費済み記録に失敗しました: {result}", file=sys.stderr)
      return False

  write_path = Path(cwd) / DEFAULT_COMMIT_APPROVAL_PATH
  approval["consumed"] = True
  approval["consumed_at"] = consumed_at
  try:
    write_path.parent.mkdir(parents=True, exist_ok=True)
    write_path.write_text(
      json.dumps(approval, ensure_ascii=False, indent=2) + "\n",
      encoding="utf-8",
    )
  except OSError as e:
    print(f"error: 承認レコードの消費済み記録に失敗しました: {e}", file=sys.stderr)
    return False

  return True


def run_precheck(cwd, rationale):
  """commit 事前検査を実行する"""
  script = Path(__file__).resolve().parent / "check-workflow-action.py"
  return subprocess.run(
    [
      "python3",
      str(script),
      "commit",
      "--rationale",
      rationale,
      "--execution-actor",
      "llm",
    ],
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


def current_head_commit(cwd):
  """現在の HEAD commit を返す"""
  result = subprocess.run(
    ["git", "rev-parse", "HEAD"],
    cwd=str(cwd),
    capture_output=True,
    text=True,
  )
  if result.returncode != 0:
    return None
  return result.stdout.strip()


def record_last_commit_precheck(cwd, precheck):
  """commit 成功後に push 用の事前検査通過記録を repo 外へ残す"""
  head_commit = current_head_commit(cwd)
  if not head_commit:
    print("warning: HEAD commit を取得できず commit 事前検査記録を残せません", file=sys.stderr)
    return

  precheck_path = Path(cwd) / DEFAULT_LAST_COMMIT_PRECHECK_PATH
  precheck_path.parent.mkdir(parents=True, exist_ok=True)
  record = {
    "head_commit": head_commit,
    "precheck_command": "tools/check-workflow-action.py commit",
    "precheck_exit_code": precheck.returncode,
    "recorded_at": datetime.now(timezone.utc).isoformat(),
  }
  try:
    precheck_path.write_text(
      json.dumps(record, ensure_ascii=False, indent=2) + "\n",
      encoding="utf-8",
    )
  except OSError as e:
    print(f"warning: commit 事前検査記録の保存に失敗しました: {e}", file=sys.stderr)


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

  record_last_commit_precheck(cwd, precheck)
  if not consume_commit_approval(cwd):
    return 2
  return 0


if __name__ == "__main__":
  sys.exit(main())
