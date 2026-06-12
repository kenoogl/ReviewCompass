"""実行時生成物の旧配置に対する凍結違反検出（wm tasks T-004 観点 5）。

凍結集合の判定基準は git 追跡履歴を正本とする：P1 実装反映コミット時点で旧配置に
存在したファイルが凍結集合であり、それ以降の追加・変更・削除を違反として検出する。
判定規則は conformance-evaluation の凍結違反検出と同一
（正本は wm design §実行時生成物の凍結期（P3 まで）の扱い）。

注記：ReviewCompass 自身では旧 3 パスはいずれも gitignore 対象（未追跡）のため、
git 履歴で不変性を立証できるのは旧配置を追跡している構成（対象アプリ等）に限られる。
未追跡（ignore 対象）の旧成果物の凍結は、書き込み経路の凍結期挙動テスト（観点 1・2）で担保する。
このため未追跡の列挙には --exclude-standard を付け、ignore されたまま現存する凍結成果物を
誤検知しない（conformance-evaluation の検出器は旧記録が git 追跡済みのため ignored 込みで
検出するのが正しく、前提の違いによる意図的な規則差である）。
"""
import re
import subprocess
from pathlib import Path

# 凍結済み旧配置（P3 まで読み取り互換のみ。新規追加・変更・削除は凍結違反。
# 承認記録は契約どおり commit-approval.json 単体に限定する）
LEGACY_RUNTIME_PATTERNS = (
  re.compile(r"^docs/logs/workflow-precheck\.log$"),
  re.compile(r"^\.reviewcompass/effective-prompts/"),
  re.compile(r"^\.reviewcompass/approvals/commit-approval\.json$"),
)


def check_runtime_placement_freeze(cwd, freeze_commit):
  """旧 3 パスへの凍結違反（追加・変更・削除）を理由文字列のリストで返す"""
  violations = []
  for pattern in LEGACY_RUNTIME_PATTERNS:
    frozen = _matching(cwd, pattern, "ls-tree", "-r", "--name-only", freeze_commit)
    tracked = _matching(cwd, pattern, "ls-files")
    untracked = _matching(cwd, pattern, "ls-files", "--others", "--exclude-standard")
    changed = _matching(cwd, pattern, "diff", "--name-only", freeze_commit)
    current = tracked | untracked
    added = sorted(current - frozen)
    # 削除はステージ前だと索引（ls-files）に残るため、現存判定はファイル実体で行う
    deleted = sorted(
      path for path in (changed & frozen) if not (Path(cwd) / path).exists()
    )
    modified = sorted(
      path for path in (changed & frozen) if (Path(cwd) / path).exists()
    )
    violations.extend(f"added_after_freeze: {path}" for path in added)
    violations.extend(f"frozen_file_changed: {path}" for path in modified)
    violations.extend(f"deleted_after_freeze: {path}" for path in deleted)
  return violations


def _matching(cwd, pattern, *args):
  # git ls-tree はワイルドカードを解釈しないため、木全体を列挙して Python 側で絞り込む
  result = subprocess.run(
    ["git", "-C", str(Path(cwd)), *args],
    capture_output=True,
    text=True,
  )
  if result.returncode != 0:
    raise ValueError(
      "凍結検査の git 実行に失敗しました。freeze_commit が有効なコミットか、"
      f"対象が git リポジトリかを確認してください（git {args[0]}: {result.stderr.strip()[:200]}）"
    )
  return {line for line in result.stdout.splitlines() if line and pattern.match(line)}
