"""実行時生成物 3 パスの配置定数と読み取り解決（2026-06-12 配置規約 P1）。

正本は workflow-management design §実行時生成物の凍結期（P3 まで）の扱い。
書き込みは常に新配置（runtime 区画）、読み取りは新→旧の順のフォールバック（P3 まで）、
新旧競合時は新配置を採用する。check-workflow-action.py・guarded-git-commit.py・
run_role.py が本モジュールを参照し、定数の二重定義を持たない。
"""
from pathlib import Path

DEFAULT_LOG_PATH = ".reviewcompass/runtime/logs/workflow-precheck.log"
LEGACY_LOG_PATH = "docs/logs/workflow-precheck.log"
DEFAULT_COMMIT_APPROVAL_PATH = ".reviewcompass/runtime/approvals/commit-approval.json"
LEGACY_COMMIT_APPROVAL_PATH = ".reviewcompass/approvals/commit-approval.json"
DEFAULT_EFFECTIVE_PROMPT_DIR = ".reviewcompass/runtime/effective-prompts"
LEGACY_EFFECTIVE_PROMPT_DIR = ".reviewcompass/effective-prompts"


def resolve_precheck_log_read_path(cwd):
  """検査ログの読み取りパスを新→旧の順で解決する（凍結期の読み取り互換、P3 まで）

  ツール自身は新配置へ追記するのみで、本関数は過去ログを読む利用者・外部ツール向けの解決を提供する。
  """
  if (Path(cwd) / DEFAULT_LOG_PATH).exists():
    return DEFAULT_LOG_PATH
  if (Path(cwd) / LEGACY_LOG_PATH).exists():
    return LEGACY_LOG_PATH
  return DEFAULT_LOG_PATH


def resolve_commit_approval_path(cwd):
  """承認レコードの読み取りパスを新→旧の順で解決する（凍結期の読み取り互換、P3 まで）"""
  if (Path(cwd) / DEFAULT_COMMIT_APPROVAL_PATH).exists():
    return DEFAULT_COMMIT_APPROVAL_PATH
  if (Path(cwd) / LEGACY_COMMIT_APPROVAL_PATH).exists():
    return LEGACY_COMMIT_APPROVAL_PATH
  return DEFAULT_COMMIT_APPROVAL_PATH


def resolve_effective_prompt_read_path(cwd, relative_path):
  """effective prompt の読み取りパスを新→旧の順で解決する（凍結期の読み取り互換、P3 まで）

  入力前提：relative_path は cwd 相対の新配置形式または旧配置形式のパスを想定する。
  str と Path のどちらも受け入れ、内部で str 化して扱う。
  どちらの形式で渡されても新配置を先に確認し、無ければ旧配置を確認する
  （新旧競合時は新配置を正とする。P1 前の記録が保持する旧形式パスにも適用）。
  どちらにも実体が無い場合と、新旧いずれの形式でもないパス（絶対パス等）は入力をそのまま返す
  （変換しない）。戻り値は常に str。
  """
  path_text = str(relative_path)
  if path_text.startswith(DEFAULT_EFFECTIVE_PROMPT_DIR + "/"):
    suffix = path_text[len(DEFAULT_EFFECTIVE_PROMPT_DIR):]
  elif path_text.startswith(LEGACY_EFFECTIVE_PROMPT_DIR + "/"):
    suffix = path_text[len(LEGACY_EFFECTIVE_PROMPT_DIR):]
  else:
    return path_text
  runtime_relative = DEFAULT_EFFECTIVE_PROMPT_DIR + suffix
  legacy_relative = LEGACY_EFFECTIVE_PROMPT_DIR + suffix
  if (Path(cwd) / runtime_relative).exists():
    return runtime_relative
  if (Path(cwd) / legacy_relative).exists():
    return legacy_relative
  return path_text
