"""Evaluation record writer for conformance-evaluation."""
from pathlib import Path


class RecordError(ValueError):
  """Raised when an evaluation record would violate the front-matter contract."""


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
    materialization_commit_hash: str,
    related_records: list,
    body: str,
  ) -> Path:
    if mode_internal not in {"generation", "check"}:
      raise RecordError(f"unknown_mode_internal: {mode_internal}")
    if author == reviewer:
      raise RecordError("author_reviewer_must_be_distinct")
    path = (
      self.root
      / ".reviewcompass"
      / "specs"
      / feature
      / "conformance"
      / f"{run_date}-{mode_internal}.md"
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    related = "\n".join(f"  - {item}" for item in related_records) or "  []"
    text = (
      "---\n"
      "type: conformance_evaluation\n"
      f"mode_internal: {mode_internal}\n"
      f"author: {author}\n"
      f"reviewer: {reviewer}\n"
      f"target_commit: {target_commit}\n"
      f"materialization_commit_hash: {materialization_commit_hash}\n"
      "related_records:\n"
      f"{related}\n"
      "---\n\n"
      f"{body}"
    )
    path.write_text(text, encoding="utf-8")
    return path

