"""実行分類器（evaluation tasks.md T-004）。"""
from dataclasses import asdict, dataclass
from pathlib import Path

import yaml

from classifier.foundation_ref import vocabulary
from classifier.step_omission_validator import StepOmissionValidator


@dataclass(frozen=True)
class RunClassification:
  """実行分類結果。"""

  run_id: str
  target_id: str
  classification: str
  evidence_class: str
  treatment: str
  review_mode: str
  included_in_standard_metrics: bool
  reason_codes: list
  step_failures: list

  def to_index_entry(self):
    return asdict(self)


class RunClassifier:
  """foundation evidence_class を主入力として評価側分類を決定する。"""

  def __init__(self, step_validator=None):
    self.step_validator = step_validator or StepOmissionValidator()

  def classify(self, run_dir, *, admission_status="admitted_standard"):
    run_dir = Path(run_dir)
    manifest = yaml.safe_load((run_dir / "run_manifest.yaml").read_text(encoding="utf-8"))
    evidence_class = manifest["evidence_class"]
    if evidence_class not in vocabulary("evidence_class"):
      raise ValueError(f"unknown evidence_class: {evidence_class}")

    classification = evidence_class
    reason_codes = []
    step_failures = []

    if admission_status == "rejected":
      classification = "analysis_blocked"
      reason_codes.append("admission_rejected")
    elif not (run_dir / "review_case.json").is_file():
      classification = "analysis_blocked"
      reason_codes.append("missing_required_input")
    else:
      step_result = self.step_validator.validate(run_dir)
      if not step_result.ok:
        classification = "analysis_blocked"
        reason_codes.append("step_outcome_mismatch")
        step_failures = step_result.failure_steps

    if classification in ("invalid", "exploratory", "analysis_blocked") and not reason_codes:
      reason_codes.append(f"evidence_class_{classification}")

    included_in_standard_metrics = classification == "valid"
    if classification == "valid" and admission_status != "admitted_standard":
      included_in_standard_metrics = False
      reason_codes.append("admission_not_standard")
    if classification == "valid" and manifest["review_mode"] != "runtime_mediated":
      included_in_standard_metrics = False
      reason_codes.append("review_mode_not_standard")

    return RunClassification(
      run_id=manifest["run_id"],
      target_id=manifest.get("target_id"),
      classification=classification,
      evidence_class=evidence_class,
      treatment=manifest["treatment"],
      review_mode=manifest["review_mode"],
      included_in_standard_metrics=included_in_standard_metrics,
      reason_codes=reason_codes,
      step_failures=step_failures,
    )
