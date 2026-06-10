"""immutability_guard（不変性の担保）（runtime tasks.md T-008）。

実行終了時に run_manifest.yaml へ凍結マーカー（closed_at）を記録し、これ以降の生段証拠
変更を構造的に禁止する。生証拠は不変とし、要約を後から更新しても生段証拠は変更しない
（design.md §不変性の担保）。

対応設計節：design.md §証拠出力モデル §不変性の担保
対応要件：Requirement 6 受入 3、Requirement 7 受入 5
"""
from pathlib import Path

import yaml


class FrozenEvidenceError(Exception):
  """凍結後の生段証拠変更を検出した違反。"""


class ImmutabilityGuard:
  """凍結マーカー（closed_at）による生段証拠の不変性ガード。"""

  def __init__(self, run_dir):
    self.run_dir = Path(run_dir)
    self.manifest_path = self.run_dir / "run_manifest.yaml"

  def _manifest(self):
    if not self.manifest_path.is_file():
      return {}
    return yaml.safe_load(self.manifest_path.read_text(encoding="utf-8")) or {}

  def is_frozen(self):
    """run_manifest.yaml に closed_at が記録されていれば凍結済み。"""
    return bool(self._manifest().get("closed_at"))

  def freeze(self, closed_at):
    """凍結マーカー closed_at を run_manifest.yaml に記録する。"""
    manifest = self._manifest()
    manifest["closed_at"] = closed_at
    self.manifest_path.write_text(
      yaml.safe_dump(manifest, allow_unicode=True, sort_keys=False), encoding="utf-8"
    )
    return closed_at

  def guarded_write_step(self, relpath, content):
    """凍結後は生段証拠の書き込みを拒否する。凍結前のみ書き込む。"""
    if self.is_frozen():
      raise FrozenEvidenceError(
        f"凍結済み実行の生段証拠は変更できない：{relpath}（closed_at 記録済み）"
      )
    path = self.run_dir / relpath
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path
