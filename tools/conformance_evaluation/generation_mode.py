"""Generation mode pipeline for human-collaborative onboarding."""
from pathlib import Path

from tools.conformance_evaluation.evaluation_record import EvaluationRecordModel


class GenerationPipeline:
  def __init__(self, root: Path):
    self.root = Path(root)

  def generate(self, *, app_root: Path, feature: str, run_date: str, code_refs: list) -> dict:
    app_root = Path(app_root)
    inferred_root = app_root / ".reviewcompass" / "conformance" / "inferred" / run_date
    docs = [
      inferred_root / "feature-partitioning-candidates.md",
      inferred_root / "intent-reference.md",
      inferred_root / "specs" / feature / "requirements.md",
      inferred_root / "specs" / feature / "design.md",
    ]
    for path in docs:
      path.parent.mkdir(parents=True, exist_ok=True)
      path.write_text(self._document_text(path.name, code_refs), encoding="utf-8")
    EvaluationRecordModel(app_root).write_record(
      feature=feature,
      mode_internal="generation",
      run_date=run_date,
      author="primary",
      reviewer="judgment",
      target_commit="unknown",
      materialization_commit_hash="independent",
      related_records=[],
      body="## 推定根拠\n" + "\n".join(f"- {ref}" for ref in code_refs) + "\n",
    )
    return {
      "layer_policy": {
        "feature-partitioning": "human_collaboration",
        "intent": "human_collaboration",
        "requirements": "automatic_estimation",
        "design": "automatic_estimation",
        "tasks": "excluded",
      },
      "documents": [str(path) for path in docs],
    }

  def _document_text(self, title: str, code_refs: list) -> str:
    refs = "\n".join(f"- {ref}" for ref in code_refs)
    return (
      "---\n"
      "human_review_required: true\n"
      "---\n\n"
      f"# {title}\n\n"
      "## Introduction\n\n"
      "Human review is required before adoption.\n\n"
      "## Boundary Context\n\n"
      "Generated as a first draft for conformance-evaluation.\n\n"
      "## Requirements\n\n"
      f"{refs}\n"
    )

