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
from check_workflow_action.commit_approval import (
  DEFAULT_COMMIT_EXECUTION_DELEGATION_PATH,
  delegate_execution,
  record,
)
from check_workflow_action import commit_unit

DEFAULT_LAST_COMMIT_PRECHECK_PATH = ".git/reviewcompass/last-commit-precheck.json"
SANDBOX_GIT_WRITE_DENIED = "sandbox_git_write_denied"
RERUN_COMMIT_WITH_ESCALATION = "rerun_commit_with_escalation"


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
    delegation_path = Path(cwd) / DEFAULT_COMMIT_EXECUTION_DELEGATION_PATH
    ok, result = _mark_consumed(delegation_path, consumed_at)
    if not ok:
      print(f"error: commit 実行代行承認の消費済み記録に失敗しました: {result}", file=sys.stderr)
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


def git_index_lock_path(cwd):
  """現在の git index.lock パスを返す。"""
  result = subprocess.run(
    ["git", "rev-parse", "--git-path", "index.lock"],
    cwd=str(cwd),
    capture_output=True,
    text=True,
  )
  if result.returncode == 0 and result.stdout.strip():
    return Path(cwd) / result.stdout.strip()
  return Path(cwd) / ".git" / "index.lock"


def preflight_git_index_lock(cwd):
  """git commit 直前に index.lock の作成可否を確認する。"""
  lock_path = git_index_lock_path(cwd)
  if lock_path.exists():
    return {
      "ok": False,
      "classification": "git_index_lock_exists",
      "required_action": "inspect_existing_git_index_lock",
      "message": f"{lock_path} が既に存在します",
    }

  try:
    with lock_path.open("x", encoding="utf-8"):
      pass
    lock_path.unlink()
  except PermissionError as e:
    return {
      "ok": False,
      "classification": SANDBOX_GIT_WRITE_DENIED,
      "required_action": RERUN_COMMIT_WITH_ESCALATION,
      "message": str(e),
    }
  except OSError as e:
    return {
      "ok": False,
      "classification": SANDBOX_GIT_WRITE_DENIED,
      "required_action": RERUN_COMMIT_WITH_ESCALATION,
      "message": str(e),
    }

  return {"ok": True}


def is_index_lock_permission_failure(result):
  """git commit 結果が sandbox の index.lock 書き込み拒否かを判定する。"""
  output = f"{result.stdout}\n{result.stderr}".lower()
  return (
    "index.lock" in output
    and (
      "operation not permitted" in output
      or "permission denied" in output
      or "unable to create" in output
    )
  )


def print_commit_escalation_required(preflight):
  """sandbox 外 guarded commit 再実行が必要なことを表示する。"""
  classification = preflight.get("classification", SANDBOX_GIT_WRITE_DENIED)
  required_action = preflight.get("required_action", RERUN_COMMIT_WITH_ESCALATION)
  message = preflight.get("message")
  print(f"error: {classification}", file=sys.stderr)
  print(f"required_action={required_action}", file=sys.stderr)
  print("承認は保持されました", file=sys.stderr)
  if required_action == RERUN_COMMIT_WITH_ESCALATION:
    print("staged 内容が変わらなければ再承認不要です", file=sys.stderr)
    print("sandbox 外で guarded commit を再実行してください", file=sys.stderr)
  else:
    print("既存の git index lock を確認してください", file=sys.stderr)
  if message:
    print(f"detail: {message}", file=sys.stderr)


def record_line_approval(cwd, nonce):
  """承認1行から内容承認と実行代行承認を連続作成する。"""
  if not sys.stdin.isatty():
    raise ValueError("承認文は TTY からの対話入力である必要があります")
  source_bytes = sys.stdin.buffer.readline()
  if not source_bytes:
    raise ValueError("承認文が入力されていません")
  try:
    source_text = source_bytes.decode("utf-8")
  except UnicodeDecodeError as e:
    raise ValueError(f"承認文は UTF-8 である必要があります: {e}") from e
  record(cwd, nonce, source_text=source_text)
  delegate_execution(cwd, nonce, source_bytes)


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


def current_head_subject(cwd):
  """現在の HEAD commit subject を返す。"""
  result = subprocess.run(
    ["git", "log", "-1", "--pretty=%s"],
    cwd=str(cwd),
    capture_output=True,
    text=True,
  )
  if result.returncode != 0:
    return None
  return result.stdout.strip()


def print_precheck_output(precheck):
  """commit precheck の詳細出力をそのまま表示する。"""
  if precheck.stdout:
    print(precheck.stdout, end="")
  if precheck.stderr:
    print(precheck.stderr, end="", file=sys.stderr)


def print_success_summary(cwd, precheck):
  """成功時の最小 summary を表示する。"""
  status = "OK" if precheck.returncode == 0 else "WARN"
  print(f"commit precheck: {status}")
  head_commit = current_head_commit(cwd)
  head_subject = current_head_subject(cwd)
  if head_commit and head_subject:
    print(f"committed: {head_commit} {head_subject}")
  elif head_commit:
    print(f"committed: {head_commit}")


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
  parser.add_argument(
    "--approval-nonce",
    help="prepare 済み nonce。指定時は承認1行から approval/delegation を作成してから commit する",
  )
  parser.add_argument(
    "--approval-source-text-line-stdin",
    action="store_true",
    help="承認文を TTY stdin から1行だけ読む。EOF を待たない",
  )
  parser.add_argument(
    "--verbose",
    action="store_true",
    help="commit precheck と git commit の詳細出力を表示する",
  )
  args = parser.parse_args(argv)

  cwd = Path.cwd()
  if bool(args.approval_nonce) != bool(args.approval_source_text_line_stdin):
    print(
      "error: --approval-nonce と --approval-source-text-line-stdin は同時に指定してください",
      file=sys.stderr,
    )
    return 2
  if args.approval_nonce:
    try:
      record_line_approval(cwd, args.approval_nonce)
    except (OSError, RuntimeError, ValueError) as e:
      print(f"error: commit 承認の記録に失敗しました: {e}", file=sys.stderr)
      return 2

  precheck = run_precheck(cwd, args.rationale)
  if args.verbose or precheck.returncode != 0:
    print_precheck_output(precheck)

  if precheck.returncode == 2:
    return 2
  if precheck.returncode == 1 and not args.allow_warn:
    print("error: 事前検査が WARN のため commit を停止しました", file=sys.stderr)
    return 1
  if precheck.returncode not in (0, 1):
    return precheck.returncode

  preflight = preflight_git_index_lock(cwd)
  if not preflight.get("ok"):
    print_commit_escalation_required(preflight)
    return 2

  result = run_git_commit(cwd, args.message)
  if args.verbose or result.returncode != 0:
    if result.stdout:
      print(result.stdout, end="")
    if result.stderr:
      print(result.stderr, end="", file=sys.stderr)
  if result.returncode != 0:
    if is_index_lock_permission_failure(result):
      print_commit_escalation_required({
        "classification": SANDBOX_GIT_WRITE_DENIED,
        "required_action": RERUN_COMMIT_WITH_ESCALATION,
        "message": result.stderr.strip(),
      })
    return result.returncode

  record_last_commit_precheck(cwd, precheck)
  if not consume_commit_approval(cwd):
    return 2
  cleanup = commit_unit.clear(cwd)
  if cleanup.get("verdict") != "OK":
    for reason in cleanup.get("reasons", []):
      print(f"error: {reason}", file=sys.stderr)
    return 2
  print_success_summary(cwd, precheck)
  return 0


if __name__ == "__main__":
  sys.exit(main())
