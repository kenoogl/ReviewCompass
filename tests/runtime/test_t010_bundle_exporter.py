"""T-010 のテスト：可搬証拠束輸出。

対応タスク：runtime tasks.md T-010
対応設計節：design.md §可搬証拠束輸出 §輸出境界 §束形状
対応要件：Requirement 9（可搬な証拠束の輸出）

テスト要件（tasks.md T-010 より）：
- 束生成テスト
- 必須項目存在テスト
- 生実行ディレクトリ不変性テスト
- 来歴同一性テスト
"""
import hashlib
import json
from pathlib import Path

import pytest
import yaml

from runtime_core.bundle_exporter.exporter import BundleExporter, MissingProvenanceError

REPO_ROOT = Path(__file__).resolve().parents[2]
BUNDLE_SCHEMA = REPO_ROOT / "runtime/runtime_core/bundle_exporter/bundle_manifest_schema.yaml"

REQUIRED_8 = {
  "bundle_id", "run_id", "source_repository_id", "source_revision",
  "review_mode", "exported_at", "export_runtime_version", "included_artifact_refs",
}


def _tree_hash(root):
  """ディレクトリツリーの内容ハッシュ（相対パス＋内容、ソート済み）。"""
  root = Path(root)
  h = hashlib.sha256()
  for path in sorted(p for p in root.rglob("*") if p.is_file()):
    h.update(str(path.relative_to(root)).encode("utf-8"))
    h.update(path.read_bytes())
  return h.hexdigest()


def _setup_run(tmp_path):
  run_dir = tmp_path / "experiments" / "runs" / "run-1"
  (run_dir / "steps").mkdir(parents=True)
  (run_dir / "run_manifest.yaml").write_text(yaml.safe_dump({
    "run_id": "run-1", "target_id": "doc-001",
    "source_repository_id": "repo-x", "source_revision": "rev-7",
    "review_mode": "runtime_mediated", "run_status": "closed",
  }, allow_unicode=True), encoding="utf-8")
  (run_dir / "review_case.json").write_text(json.dumps({"run_id": "run-1"}), encoding="utf-8")
  (run_dir / "steps" / "step_a_primary_detection.json").write_text(
    json.dumps({"step_id": "step_a"}), encoding="utf-8")
  return run_dir


def _export(tmp_path, run_dir):
  exporter = BundleExporter()
  return exporter.export(
    run_dir, bundle_id="bundle-001", exported_at="2026-06-02T13:00",
    export_runtime_version="r1", exports_base=tmp_path / "exports",
  )


def test_bundle_schema_declares_8_required():
  """bundle_manifest_schema.yaml が必須 8 項目を宣言する（完了条件 1）。"""
  spec = yaml.safe_load(BUNDLE_SCHEMA.read_text(encoding="utf-8"))
  assert set(spec["required_fields"]) == REQUIRED_8


def test_export_generates_bundle(tmp_path):
  """可搬束（bundle_manifest.yaml・run/・checksums/）が生成される（完了条件 1）。"""
  run_dir = _setup_run(tmp_path)
  bundle_dir = _export(tmp_path, run_dir)
  assert (bundle_dir / "bundle_manifest.yaml").is_file()
  assert (bundle_dir / "run" / "run-1").is_dir()
  assert (bundle_dir / "checksums" / "bundle_checksums.json").is_file()


def test_bundle_manifest_has_8_fields(tmp_path):
  """bundle_manifest.yaml に必須 8 項目が出力される（完了条件 1）。"""
  run_dir = _setup_run(tmp_path)
  bundle_dir = _export(tmp_path, run_dir)
  manifest = yaml.safe_load((bundle_dir / "bundle_manifest.yaml").read_text(encoding="utf-8"))
  for field in REQUIRED_8:
    assert field in manifest, f"bundle_manifest.yaml に {field} が欠落"


def test_source_run_dir_unchanged(tmp_path):
  """輸出後も生実行ディレクトリが不変（ハッシュ照合、完了条件 2）。"""
  run_dir = _setup_run(tmp_path)
  before = _tree_hash(run_dir)
  _export(tmp_path, run_dir)
  after = _tree_hash(run_dir)
  assert before == after, "輸出により生実行ディレクトリが変化した"


def test_provenance_identity_preserved(tmp_path):
  """来歴情報が run_manifest と bundle_manifest で一致する（完了条件 3）。"""
  run_dir = _setup_run(tmp_path)
  run_manifest = yaml.safe_load((run_dir / "run_manifest.yaml").read_text(encoding="utf-8"))
  bundle_dir = _export(tmp_path, run_dir)
  bundle_manifest = yaml.safe_load((bundle_dir / "bundle_manifest.yaml").read_text(encoding="utf-8"))
  for field in ("source_repository_id", "source_revision", "review_mode", "run_id"):
    assert bundle_manifest[field] == run_manifest[field], f"{field} の来歴同一性が崩れた"


def test_included_artifact_refs_listed(tmp_path):
  """included_artifact_refs に複製された成果物が列挙される。"""
  run_dir = _setup_run(tmp_path)
  bundle_dir = _export(tmp_path, run_dir)
  manifest = yaml.safe_load((bundle_dir / "bundle_manifest.yaml").read_text(encoding="utf-8"))
  refs = set(manifest["included_artifact_refs"])
  assert "run_manifest.yaml" in refs
  assert any("steps/" in r for r in refs)


def test_checksums_cover_included_artifacts(tmp_path):
  """checksums が複製成果物を網羅する。"""
  run_dir = _setup_run(tmp_path)
  bundle_dir = _export(tmp_path, run_dir)
  manifest = yaml.safe_load((bundle_dir / "bundle_manifest.yaml").read_text(encoding="utf-8"))
  checksums = json.loads((bundle_dir / "checksums" / "bundle_checksums.json").read_text(encoding="utf-8"))
  assert set(checksums.keys()) == set(manifest["included_artifact_refs"])


def test_missing_provenance_rejected(tmp_path):
  """来歴情報が欠落した実行の輸出を拒否する（欠落を暗黙補完しない）。"""
  run_dir = tmp_path / "experiments" / "runs" / "run-2"
  run_dir.mkdir(parents=True)
  (run_dir / "run_manifest.yaml").write_text(yaml.safe_dump({
    "run_id": "run-2", "target_id": "doc"}, allow_unicode=True), encoding="utf-8")
  exporter = BundleExporter()
  with pytest.raises(MissingProvenanceError):
    exporter.export(run_dir, bundle_id="b", exported_at="t",
                    export_runtime_version="r1", exports_base=tmp_path / "exports")
