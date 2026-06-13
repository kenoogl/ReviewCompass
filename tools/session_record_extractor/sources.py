"""入力源（転写ファイル）の発見と Codex の対象アプリ絞り込み。

Claude はプロジェクトごとにディレクトリが分かれるため絞り込み不要。
Codex は全プロジェクト混在のため、先頭 session_meta の cwd で前方一致絞り込みする。
cwd が欠落・破損した記録は対象外とする（ベストエフォート）。
"""
import json
from pathlib import Path


def codex_cwd(path):
  """Codex 転写の先頭付近から session_meta.cwd を読む。読めなければ None。"""
  p = Path(path)
  try:
    with p.open(encoding="utf-8", errors="replace") as f:
      for i, line in enumerate(f):
        if i >= 5:
          break
        line = line.strip()
        if not line:
          continue
        try:
          obj = json.loads(line)
        except json.JSONDecodeError:
          return None
        if obj.get("type") == "session_meta":
          payload = obj.get("payload") or {}
          return payload.get("cwd")
  except OSError:
    return None
  return None


def discover_codex_sessions(codex_root, repo_path):
  """codex_root 配下の rollout-*.jsonl を、cwd が repo_path に前方一致するものに絞る。"""
  root = Path(codex_root)
  repo = str(repo_path).rstrip("/")
  found = []
  for p in sorted(root.rglob("rollout-*.jsonl")):
    cwd = codex_cwd(p)
    if not cwd:
      continue
    c = cwd.rstrip("/")
    if c == repo or c.startswith(repo + "/"):
      found.append(p)
  return found


def discover_claude_sessions(claude_project_dir):
  """Claude プロジェクトディレクトリ配下の *.jsonl を列挙する（絞り込み不要）。"""
  root = Path(claude_project_dir)
  return sorted(root.glob("*.jsonl"))
