"""bundle exporter（可搬証拠束輸出）（runtime tasks.md T-010）。

実行終了・検証完了後の別工程として、生実行ディレクトリを置き換えずに可搬証拠束を生成する。
生実行成果物の意味を書き換えず、欠落した来歴を暗黙補完せず、中央側の取り込み判定を済ませた
ことにしない（要件 9 受入 1・4・5）。

対応設計節：design.md §可搬証拠束輸出 §輸出境界 §束形状
対応要件：Requirement 9（可搬な証拠束の輸出）
"""
import hashlib
import json
import shutil
from pathlib import Path

import yaml

# bundle_manifest.yaml に保持する来歴項目（run_manifest と同一性を保つ）。
_PROVENANCE_FIELDS = ["source_repository_id", "source_revision", "review_mode"]


class MissingProvenanceError(Exception):
  """来歴情報が欠落した実行の輸出を検出した違反（欠落を暗黙補完しない）。"""


class BundleExporter:
  """生実行ディレクトリから可搬証拠束を生成する（生証拠は不変）。"""

  def export(self, run_dir, *, bundle_id, exported_at, export_runtime_version, exports_base):
    run_dir = Path(run_dir)
    run_manifest = yaml.safe_load((run_dir / "run_manifest.yaml").read_text(encoding="utf-8"))

    # 来歴情報の欠落は暗黙補完せず拒否する（要件 9 受入 5）。
    missing = [f for f in _PROVENANCE_FIELDS if not run_manifest.get(f)]
    if missing:
      raise MissingProvenanceError(f"来歴情報が欠落しており輸出できない：{missing}")
    run_id = run_manifest["run_id"]

    bundle_dir = Path(exports_base) / bundle_id
    run_copy_root = bundle_dir / "run" / run_id
    run_copy_root.parent.mkdir(parents=True, exist_ok=True)

    # 生実行ディレクトリを複製する（元は変更しない）。
    shutil.copytree(run_dir, run_copy_root)

    # 複製成果物の参照一覧とチェックサムを作る。
    included_refs = []
    checksums = {}
    for path in sorted(p for p in run_copy_root.rglob("*") if p.is_file()):
      rel = str(path.relative_to(run_copy_root))
      included_refs.append(rel)
      checksums[rel] = "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()

    # bundle_manifest.yaml（必須 8 項目、来歴は run_manifest と同一）。
    bundle_manifest = {
      "bundle_id": bundle_id,
      "run_id": run_id,
      "source_repository_id": run_manifest["source_repository_id"],
      "source_revision": run_manifest["source_revision"],
      "review_mode": run_manifest["review_mode"],
      "exported_at": exported_at,
      "export_runtime_version": export_runtime_version,
      "included_artifact_refs": included_refs,
    }
    (bundle_dir / "bundle_manifest.yaml").write_text(
      yaml.safe_dump(bundle_manifest, allow_unicode=True, sort_keys=False), encoding="utf-8"
    )

    checksums_dir = bundle_dir / "checksums"
    checksums_dir.mkdir(parents=True, exist_ok=True)
    (checksums_dir / "bundle_checksums.json").write_text(
      json.dumps(checksums, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return bundle_dir
