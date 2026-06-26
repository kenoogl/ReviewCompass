"""PPWM-3: ソース束（source bundle）の構築と検証。

post-write review prompt に渡す材料を「パスのみ」ではなく本文込みで構築し、
SHA と本文の一致を保証する。
"""
import hashlib
from pathlib import Path
from typing import Dict, List, Optional


class BundleValidationError(ValueError):
  """ソース束の検証失敗を表す例外"""
  pass


def _sha256_text(text: str) -> str:
  return hashlib.sha256(text.encode("utf-8")).hexdigest()


class SourceBundle:
  """本文込みのソース束。

  構築方法:
    - from_paths(): ファイルパスから本文を読み込んで構築する（通常用途）
    - from_raw_entries(): 既存のエントリ辞書から構築する（テスト・変換用途）

  validate() で以下を確認する:
    - target が 1 件以上ある
    - すべてのエントリに本文（content）がある（パス/SHA のみ拒否）
    - SHA と本文が一致する
  """

  def __init__(self, entries: List[Dict]) -> None:
    self._entries = entries

  @classmethod
  def from_paths(
    cls,
    target_paths: List[str],
    source_material_paths: List[str],
    cwd: Optional[str] = None,
  ) -> "SourceBundle":
    """ファイルパスから本文を読み込んで束を構築する。"""
    base = Path(cwd) if cwd else Path.cwd()
    entries: List[Dict] = []
    for path_str in target_paths:
      p = Path(path_str)
      if not p.is_absolute():
        p = base / p
      content = p.read_text(encoding="utf-8")
      sha = _sha256_text(content)
      entries.append({
        "path": path_str,
        "role": "target",
        "content": content,
        "sha256": sha,
        "content_mode": "full_text",
      })
    for path_str in source_material_paths:
      p = Path(path_str)
      if not p.is_absolute():
        p = base / p
      content = p.read_text(encoding="utf-8")
      sha = _sha256_text(content)
      entries.append({
        "path": path_str,
        "role": "source_material",
        "content": content,
        "sha256": sha,
        "content_mode": "full_text",
      })
    return cls(entries)

  @classmethod
  def from_raw_entries(cls, entries: List[Dict]) -> "SourceBundle":
    """既存のエントリ辞書から束を構築する（テスト・変換用途）。"""
    return cls(list(entries))

  def validate(self) -> None:
    """束の整合性を確認する。問題があれば BundleValidationError を送出する。"""
    target_entries = [e for e in self._entries if e.get("role") == "target"]
    if not target_entries:
      raise BundleValidationError("束に target が含まれていません")
    for entry in self._entries:
      content = entry.get("content", "")
      if not content:
        path = entry.get("path", "(不明)")
        raise BundleValidationError(
          f"{path}: content が空です。パス/SHA のみの束は受け付けません"
        )
      expected_sha = _sha256_text(content)
      actual_sha = entry.get("sha256", "")
      if actual_sha != expected_sha:
        path = entry.get("path", "(不明)")
        raise BundleValidationError(
          f"{path}: sha256 が本文と一致しません"
          f"（期待: {expected_sha[:16]}…, 実際: {actual_sha[:16]}…）"
        )

  def to_target_entries(self) -> List[Dict]:
    """target ロールのエントリ一覧を返す。"""
    return [e for e in self._entries if e.get("role") == "target"]

  def to_source_material_entries(self) -> List[Dict]:
    """source_material ロールのエントリ一覧を返す。"""
    return [e for e in self._entries if e.get("role") == "source_material"]
