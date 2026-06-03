"""可搬証拠束のチェックサム照合。"""
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path


@dataclass(frozen=True)
class ChecksumResult:
  """チェックサム照合結果。"""

  ok: bool
  mismatches: list
  missing_files: list


class ChecksumVerifier:
  """checksums/bundle_checksums.json と run/<run_id>/ 配下の実体を照合する。"""

  def verify(self, bundle_dir):
    bundle_dir = Path(bundle_dir)
    checksums_path = bundle_dir / "checksums" / "bundle_checksums.json"
    if not checksums_path.is_file():
      return ChecksumResult(ok=False, mismatches=["bundle_checksums.json"], missing_files=[])

    checksums = json.loads(checksums_path.read_text(encoding="utf-8"))
    run_root = self._single_run_root(bundle_dir)
    mismatches = []
    missing_files = []
    for rel, expected in checksums.items():
      path = run_root / rel
      if not path.is_file():
        missing_files.append(rel)
        continue
      actual = "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()
      if actual != expected:
        mismatches.append(rel)
    return ChecksumResult(
      ok=not mismatches and not missing_files,
      mismatches=mismatches,
      missing_files=missing_files,
    )

  def _single_run_root(self, bundle_dir):
    run_parent = Path(bundle_dir) / "run"
    run_dirs = [path for path in run_parent.iterdir() if path.is_dir()]
    if len(run_dirs) != 1:
      return run_parent
    return run_dirs[0]
