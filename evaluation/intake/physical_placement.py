"""可搬証拠束の中央側物理配置。

runtime が生成した `exports/<bundle_id>/run/<run_id>/...` の構造を、
`experiments/analysis/imports/bundles/<bundle_id>/run/<run_id>/...` に
対称配置する。
"""
import shutil
from pathlib import Path


def relative_file_paths(root):
  """root 配下のファイル相対パス集合を返す。"""
  root = Path(root)
  return {str(path.relative_to(root)) for path in root.rglob("*") if path.is_file()}


class PhysicalPlacement:
  """可搬証拠束を analysis imports 配下へ配置する。"""

  def place(self, bundle_dir, *, analysis_root, bundle_id, run_id):
    bundle_dir = Path(bundle_dir)
    analysis_root = Path(analysis_root)
    destination_bundle = analysis_root / "imports" / "bundles" / bundle_id
    source_run = bundle_dir / "run" / run_id
    if not source_run.is_dir():
      raise ValueError(f"missing_run_path: run/{run_id}")

    destination_bundle.parent.mkdir(parents=True, exist_ok=True)
    if destination_bundle.exists():
      return destination_bundle
    shutil.copytree(bundle_dir, destination_bundle)
    return destination_bundle
