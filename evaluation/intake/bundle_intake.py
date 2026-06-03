"""可搬証拠束の取り込み器（evaluation tasks.md T-002）。"""
from dataclasses import dataclass
from pathlib import Path

import yaml

from intake.ingestion_register_writer import IngestionRegisterWriter
from intake.physical_placement import PhysicalPlacement

_INGESTION_FIELDS = [
  "bundle_id",
  "run_id",
  "source_repository_id",
  "source_revision",
  "review_mode",
]
_PROVENANCE_FIELDS = ["source_repository_id", "source_revision", "review_mode"]


@dataclass(frozen=True)
class IntakeResult:
  """取り込み結果。"""

  bundle_id: str
  run_id: str
  bundle_path: Path
  register_path: Path


class BundleIntake:
  """runtime 輸出束を中央側 analysis imports 配下へ取り込む。"""

  def __init__(self, placement=None, register_writer=None):
    self.placement = placement or PhysicalPlacement()
    self.register_writer = register_writer or IngestionRegisterWriter()

  def ingest(self, bundle_dir, *, analysis_root, ingested_at):
    bundle_dir = Path(bundle_dir)
    analysis_root = Path(analysis_root)
    manifest = yaml.safe_load((bundle_dir / "bundle_manifest.yaml").read_text(encoding="utf-8"))

    bundle_id = manifest["bundle_id"]
    run_id = manifest["run_id"]
    missing_fields = [field for field in _PROVENANCE_FIELDS if not manifest.get(field)]
    destination_bundle = analysis_root / "imports" / "bundles" / bundle_id
    already_present = destination_bundle.exists()

    bundle_path = self.placement.place(
      bundle_dir,
      analysis_root=analysis_root,
      bundle_id=bundle_id,
      run_id=run_id,
    )
    if already_present:
      ingestion_status = "already_present"
    elif missing_fields:
      ingestion_status = "incomplete"
    else:
      ingestion_status = "ingested"

    entry = {
      "bundle_id": bundle_id,
      "run_id": run_id,
      "source_repository_id": manifest.get("source_repository_id"),
      "source_revision": manifest.get("source_revision"),
      "review_mode": manifest.get("review_mode"),
      "ingested_at": ingested_at,
      "ingestion_status": ingestion_status,
      "missing_fields": missing_fields,
    }
    register_path = self.register_writer.append(analysis_root, entry)
    return IntakeResult(
      bundle_id=bundle_id,
      run_id=run_id,
      bundle_path=bundle_path,
      register_path=register_path,
    )
