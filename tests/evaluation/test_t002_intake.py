"""T-002 のテスト：取り込み器（intake）と物理配置。

対応タスク：evaluation tasks.md T-002
対応設計節：design.md §取り込みモデル、§可搬証拠束の取り込み、§取り込み時の物理配置
対応要件：Requirement 10 受入 1、5

テスト要件（tasks.md T-002 より）：
- 固定 exports/<bundle_id>/ 入力に対する物理配置の決定的テスト
- ingestion_register.json 追記テスト
- 構造対称性検証テスト
"""
import json
from pathlib import Path

import yaml

from intake.bundle_intake import BundleIntake
from intake.physical_placement import relative_file_paths

REQUIRED_INGESTION_FIELDS = {
  "bundle_id",
  "run_id",
  "source_repository_id",
  "source_revision",
  "review_mode",
  "ingested_at",
  "ingestion_status",
  "missing_fields",
}


def _setup_export_bundle(tmp_path):
  bundle_dir = tmp_path / "exports" / "bundle-001"
  run_dir = bundle_dir / "run" / "run-001"
  (run_dir / "decisions").mkdir(parents=True)
  (run_dir / "validation").mkdir()
  (run_dir / "derived").mkdir()
  (bundle_dir / "checksums").mkdir()

  run_manifest = {
    "run_id": "run-001",
    "target_id": "target-001",
    "source_repository_id": "repo-001",
    "source_revision": "rev-001",
    "review_mode": "runtime_mediated",
    "run_status": "closed",
  }
  bundle_manifest = {
    "bundle_id": "bundle-001",
    "run_id": "run-001",
    "source_repository_id": "repo-001",
    "source_revision": "rev-001",
    "review_mode": "runtime_mediated",
    "exported_at": "2026-06-03T10:00:00+09:00",
    "export_runtime_version": "runtime-1",
    "included_artifact_refs": [
      "run_manifest.yaml",
      "review_case.json",
      "decisions/decision_units.json",
      "validation/validator_result.json",
      "validation/invalidation_markers.json",
      "derived/comparison_eligibility_note.json",
    ],
  }
  (bundle_dir / "bundle_manifest.yaml").write_text(
    yaml.safe_dump(bundle_manifest, allow_unicode=True, sort_keys=False),
    encoding="utf-8",
  )
  (run_dir / "run_manifest.yaml").write_text(
    yaml.safe_dump(run_manifest, allow_unicode=True, sort_keys=False),
    encoding="utf-8",
  )
  (run_dir / "review_case.json").write_text(
    json.dumps({"run_id": "run-001", "target_id": "target-001"}, ensure_ascii=False),
    encoding="utf-8",
  )
  (run_dir / "decisions" / "decision_units.json").write_text(
    json.dumps({"decision_units": []}, ensure_ascii=False),
    encoding="utf-8",
  )
  (run_dir / "validation" / "validator_result.json").write_text(
    json.dumps({"validator_status": "passed"}, ensure_ascii=False),
    encoding="utf-8",
  )
  (run_dir / "validation" / "invalidation_markers.json").write_text(
    json.dumps({"markers": []}, ensure_ascii=False),
    encoding="utf-8",
  )
  (run_dir / "derived" / "comparison_eligibility_note.json").write_text(
    json.dumps({"eligible": True}, ensure_ascii=False),
    encoding="utf-8",
  )
  (bundle_dir / "checksums" / "bundle_checksums.json").write_text(
    json.dumps({}, ensure_ascii=False),
    encoding="utf-8",
  )
  return bundle_dir


def test_bundle_intake_physically_places_run_bundle(tmp_path):
  """可搬証拠束が中央側 imports/bundles/<bundle_id>/run/<run_id>/ に配置される。"""
  bundle_dir = _setup_export_bundle(tmp_path)
  analysis_root = tmp_path / "experiments" / "analysis"

  result = BundleIntake().ingest(
    bundle_dir,
    analysis_root=analysis_root,
    ingested_at="2026-06-03T11:00:00+09:00",
  )

  placed_run = analysis_root / "imports" / "bundles" / "bundle-001" / "run" / "run-001"
  assert result.bundle_path == analysis_root / "imports" / "bundles" / "bundle-001"
  assert placed_run.is_dir()
  assert (placed_run / "run_manifest.yaml").is_file()
  assert (placed_run / "validation" / "validator_result.json").is_file()


def test_bundle_intake_rejects_bundle_without_expected_run_path(tmp_path):
  """bundle_manifest の run_id と実体の run/<run_id> が一致しなければ配置しない。"""
  bundle_dir = _setup_export_bundle(tmp_path)
  (bundle_dir / "run" / "run-001").rename(bundle_dir / "run" / "run-other")

  try:
    BundleIntake().ingest(
      bundle_dir,
      analysis_root=tmp_path / "experiments" / "analysis",
      ingested_at="2026-06-03T11:00:00+09:00",
    )
  except ValueError as exc:
    assert "missing_run_path" in str(exc)
  else:
    raise AssertionError("run_id 不一致の bundle が配置された")


def test_bundle_intake_preserves_export_run_structure(tmp_path):
  """輸出前後の run/<run_id>/ 配下の相対パス構造が一致する。"""
  bundle_dir = _setup_export_bundle(tmp_path)
  analysis_root = tmp_path / "experiments" / "analysis"

  BundleIntake().ingest(
    bundle_dir,
    analysis_root=analysis_root,
    ingested_at="2026-06-03T11:00:00+09:00",
  )

  source_run = bundle_dir / "run" / "run-001"
  placed_run = analysis_root / "imports" / "bundles" / "bundle-001" / "run" / "run-001"
  assert relative_file_paths(placed_run) == relative_file_paths(source_run)


def test_ingestion_register_is_created_with_required_8_fields(tmp_path):
  """ingestion_register.json に取り込み履歴 8 必須項目が追記される。"""
  bundle_dir = _setup_export_bundle(tmp_path)
  analysis_root = tmp_path / "experiments" / "analysis"

  BundleIntake().ingest(
    bundle_dir,
    analysis_root=analysis_root,
    ingested_at="2026-06-03T11:00:00+09:00",
  )

  register = json.loads(
    (analysis_root / "imports" / "ingestion_register.json").read_text(encoding="utf-8")
  )
  assert isinstance(register["entries"], list)
  entry = register["entries"][0]
  assert set(entry) == REQUIRED_INGESTION_FIELDS
  assert entry["bundle_id"] == "bundle-001"
  assert entry["run_id"] == "run-001"
  assert entry["ingestion_status"] == "ingested"
  assert entry["missing_fields"] == []


def test_ingestion_register_appends_entries(tmp_path):
  """既存 bundle は無言上書きせず、履歴だけを追記する。"""
  bundle_dir = _setup_export_bundle(tmp_path)
  analysis_root = tmp_path / "experiments" / "analysis"

  intake = BundleIntake()
  intake.ingest(
    bundle_dir,
    analysis_root=analysis_root,
    ingested_at="2026-06-03T11:00:00+09:00",
  )
  placed_marker = (
    analysis_root / "imports" / "bundles" / "bundle-001" / "run" / "run-001" / "marker.txt"
  )
  placed_marker.write_text("keep\n", encoding="utf-8")
  intake.ingest(
    bundle_dir,
    analysis_root=analysis_root,
    ingested_at="2026-06-03T11:05:00+09:00",
  )

  register = json.loads(
    (analysis_root / "imports" / "ingestion_register.json").read_text(encoding="utf-8")
  )
  assert [entry["ingested_at"] for entry in register["entries"]] == [
    "2026-06-03T11:00:00+09:00",
    "2026-06-03T11:05:00+09:00",
  ]
  assert placed_marker.read_text(encoding="utf-8") == "keep\n"
  assert register["entries"][1]["ingestion_status"] == "already_present"


def test_missing_provenance_is_recorded_without_invention(tmp_path):
  """来歴欠落は暗黙補完せず missing_fields に記録する。"""
  bundle_dir = _setup_export_bundle(tmp_path)
  manifest_path = bundle_dir / "bundle_manifest.yaml"
  manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
  del manifest["source_revision"]
  manifest_path.write_text(
    yaml.safe_dump(manifest, allow_unicode=True, sort_keys=False),
    encoding="utf-8",
  )
  analysis_root = tmp_path / "experiments" / "analysis"

  BundleIntake().ingest(
    bundle_dir,
    analysis_root=analysis_root,
    ingested_at="2026-06-03T11:00:00+09:00",
  )

  register = json.loads(
    (analysis_root / "imports" / "ingestion_register.json").read_text(encoding="utf-8")
  )
  entry = register["entries"][0]
  assert entry["source_revision"] is None
  assert entry["missing_fields"] == ["source_revision"]
  assert entry["ingestion_status"] == "incomplete"
