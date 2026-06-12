"""Evaluation record writer for conformance-evaluation."""
from pathlib import Path
from typing import Optional


class RecordError(ValueError):
  """Raised when an evaluation record would violate the front-matter contract."""


def conformance_dir(root: Path, feature: str) -> Path:
  """書き込み正本の配置ルート（Req 6 受入 2、2026-06-12 配置規約）。

  `_cross_feature` は実 feature ではない横断名前空間で、配置は specs 配下のまま（tasks T-015）。
  """
  if feature == "_cross_feature":
    return Path(root) / ".reviewcompass" / "specs" / feature / "conformance"
  return Path(root) / ".reviewcompass" / "evidence" / "features" / feature / "conformance"


def legacy_conformance_dir(root: Path, feature: str) -> Path:
  """凍結済み旧配置。読み取り互換（P3 まで）専用で、新規書き込みは禁止。"""
  return Path(root) / ".reviewcompass" / "specs" / feature / "conformance"


class EvaluationRecordModel:
  def __init__(self, root: Path):
    self.root = Path(root)

  def write_record(
    self,
    *,
    feature: str,
    mode_internal: str,
    run_date: str,
    author: str,
    reviewer: str,
    target_commit: str,
    materialization_commit_hash: Optional[str],
    related_records: list,
    body: str,
  ) -> Path:
    if mode_internal not in {"generation", "check"}:
      raise RecordError(f"unknown_mode_internal: {mode_internal}")
    if author == reviewer:
      raise RecordError("author_reviewer_must_be_distinct")
    path = conformance_dir(self.root, feature) / f"{run_date}-{mode_internal}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    runtime_records = "\n".join(f"    - {item}" for item in related_records) or "    []"
    self_improvement = materialization_commit_hash or ""
    text = (
      "---\n"
      "type: conformance_evaluation\n"
      f"mode_internal: {mode_internal}\n"
      f"author: {author}\n"
      f"reviewer: {reviewer}\n"
      f"target_commit: {target_commit}\n"
      "related_artifacts:\n"
      "  runtime:\n"
      f"{runtime_records}\n"
      "  evaluation: []\n"
      "  workflow_management: []\n"
      f"  self_improvement: {self_improvement}\n"
      "---\n\n"
      f"{body}"
    )
    path.write_text(text, encoding="utf-8")
    return path

  def read_record(self, *, feature: str, file_name: str) -> dict:
    """新配置優先・旧配置フォールバックの読み取り（design §12.2、P3 まで）。"""
    new_path = conformance_dir(self.root, feature) / file_name
    legacy_path = legacy_conformance_dir(self.root, feature) / file_name
    if new_path.is_file():
      warnings = []
      if legacy_path != new_path and legacy_path.is_file():
        warnings.append(
          f"duplicate_record_in_frozen_legacy_placement: {legacy_path}（新配置を正とする）"
        )
      return {
        "path": new_path,
        "text": new_path.read_text(encoding="utf-8"),
        "source": "cross_feature_namespace" if feature == "_cross_feature" else "evidence",
        "warnings": warnings,
      }
    if legacy_path.is_file():
      return {
        "path": legacy_path,
        "text": legacy_path.read_text(encoding="utf-8"),
        "source": "legacy_frozen",
        "warnings": [],
      }
    raise RecordError(f"record_not_found: {feature}/{file_name}")
