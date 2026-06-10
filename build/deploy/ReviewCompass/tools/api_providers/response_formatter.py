"""tools/api_providers/response_formatter.py

API レスポンスの整形と所見抽出。
計画書 §5.9.7.1（run_role.py 出力契約）と §5.9.3（所見メタデータ）参照。

出力 YAML のトップレベルキー順：
  role → provider → model → attempts → duration_seconds → findings

日本語は UTF-8 のまま出力（allow_unicode=True）、キー順は固定（sort_keys=False）。
"""
from typing import List

import yaml


def format_response(
  role: str,
  provider: str,
  model: str,
  attempts: int,
  duration_seconds: float,
  findings: List[dict],
) -> str:
  """構造化データから整形済み YAML 文字列を返す。

  キー順は role → provider → model → attempts → duration_seconds → findings。
  日本語は UTF-8 のまま出力する（ASCII エスケープしない）。
  """
  data = {
    "role": role,
    "provider": provider,
    "model": model,
    "attempts": attempts,
    "duration_seconds": duration_seconds,
    "findings": findings,
  }
  return yaml.dump(data, allow_unicode=True, sort_keys=False)


def _strip_code_block(text: str) -> str:
  """```yaml ... ``` または ``` ... ``` のコードブロックマーカーを除去する。"""
  stripped = text.strip()
  if stripped.startswith("```"):
    lines = stripped.splitlines()
    # 先頭行（```yaml 等）と末尾行（```）を除く
    inner = lines[1:-1] if lines[-1].strip() == "```" else lines[1:]
    return "\n".join(inner)
  return text


def parse_response_text(response_text: str) -> List[dict]:
  """API レスポンスの YAML 文字列から findings リストを返す。

  - YAML パース失敗：yaml.YAMLError を投げる（fail-closed、§5.9.1 規律）
  - findings キー欠落：ValueError
  - findings の値がリストでない：ValueError
  """
  data = yaml.safe_load(_strip_code_block(response_text))
  if not isinstance(data, dict) or "findings" not in data:
    raise ValueError("response_text に findings キーが含まれていません")
  findings = data["findings"]
  if not isinstance(findings, list):
    raise ValueError(
      f"findings の値はリストである必要があります（実体：{type(findings).__name__}）"
    )
  return findings
