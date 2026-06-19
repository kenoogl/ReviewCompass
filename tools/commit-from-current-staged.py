#!/usr/bin/env python3
"""現在の staged index に束縛した approval を作り、即 guarded commit する。"""

import argparse
import subprocess
import sys
from pathlib import Path


_TOOLS_DIR = Path(__file__).resolve().parent
if str(_TOOLS_DIR) not in sys.path:
  sys.path.insert(0, str(_TOOLS_DIR))

from check_workflow_action import commit_approval  # noqa: E402


def _read_required_approval_line():
  """stdin から承認文 1 行を読み、challenge 作成前に妥当性を確認する。"""
  if not sys.stdin.isatty():
    raise ValueError("承認文は TTY からの対話入力である必要があります")
  source_bytes = sys.stdin.buffer.readline()
  if not source_bytes:
    raise ValueError("承認文が入力されていません")
  commit_approval.normalize_execution_delegation_instruction(source_bytes)
  return source_bytes


def _record_approval_pair(cwd, nonce, source_bytes):
  """TTY で読んだ承認文から内容承認と実行代行承認を作る。"""
  try:
    source_text = source_bytes.decode("utf-8")
  except UnicodeDecodeError as e:
    raise ValueError(f"承認文は UTF-8 である必要があります: {e}") from e
  commit_approval.record(cwd, nonce, source_text=source_text)
  commit_approval.delegate_execution(cwd, nonce, source_bytes)


def _run_guarded_commit(cwd, args):
  """生成済み approval record を使って guarded-git-commit.py を実行する。"""
  cmd = [
    sys.executable,
    str(_TOOLS_DIR / "guarded-git-commit.py"),
  ]
  for message in args.message:
    cmd.extend(["-m", message])
  cmd.extend(["--rationale", args.rationale])
  if args.allow_warn:
    cmd.append("--allow-warn")
  if args.verbose:
    cmd.append("--verbose")
  return subprocess.run(
    cmd,
    cwd=str(cwd),
    capture_output=True,
  )


def _relay(result):
  """子プロセスの出力をそのまま返す。"""
  if result.stdout:
    if hasattr(sys.stdout, "buffer"):
      sys.stdout.buffer.write(result.stdout)
    else:
      sys.stdout.write(result.stdout.decode("utf-8", errors="replace"))
  if result.stderr:
    if hasattr(sys.stderr, "buffer"):
      sys.stderr.buffer.write(result.stderr)
    else:
      sys.stderr.write(result.stderr.decode("utf-8", errors="replace"))


def main(argv=None):
  """エントリポイント"""
  parser = argparse.ArgumentParser(
    description="現在の staged index に対する approval を作成し、そのまま guarded commit する",
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
    "--verbose",
    action="store_true",
    help="commit precheck と git commit の詳細出力を表示する",
  )
  args = parser.parse_args(argv)

  try:
    source_bytes = _read_required_approval_line()
    challenge = commit_approval.prepare(Path.cwd())
    _record_approval_pair(Path.cwd(), challenge["nonce"], source_bytes)
  except (OSError, RuntimeError, ValueError) as e:
    print(f"error: commit-from-current-staged: {e}", file=sys.stderr)
    return 2

  result = _run_guarded_commit(
    Path.cwd(),
    args,
  )
  _relay(result)
  return result.returncode


if __name__ == "__main__":
  sys.exit(main())
