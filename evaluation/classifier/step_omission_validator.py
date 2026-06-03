"""設計上の段省略と障害欠損の弁別。"""
from dataclasses import dataclass
import json
from pathlib import Path

import yaml

_THIS_DIR = Path(__file__).resolve().parent
_REPO_ROOT = _THIS_DIR.parents[1]
_TREATMENT_VOCAB = _REPO_ROOT / "runtime/runtime_core/treatment_vocab.yaml"
_ALL_STEPS = ["primary_detection", "adversarial_review", "judgment", "integration"]


@dataclass(frozen=True)
class StepOmissionResult:
  """段省略整合チェック結果。"""

  ok: bool
  failure_steps: list
  expected_outcomes: dict
  actual_outcomes: dict


class StepOmissionValidator:
  """runtime treatment 正本に基づき step_outcome の整合性を検査する。"""

  def validate(self, run_dir):
    run_dir = Path(run_dir)
    manifest = yaml.safe_load((run_dir / "run_manifest.yaml").read_text(encoding="utf-8"))
    review_case = json.loads((run_dir / "review_case.json").read_text(encoding="utf-8"))
    expected = self._expected_outcomes(manifest["treatment"])
    actual = {
      record["step"]: record["step_outcome"]
      for record in review_case.get("step_records", [])
    }
    failure_steps = []
    for step, expected_outcome in expected.items():
      actual_outcome = actual.get(step)
      if actual_outcome != expected_outcome:
        failure_steps.append(step)
    return StepOmissionResult(
      ok=not failure_steps,
      failure_steps=failure_steps,
      expected_outcomes=expected,
      actual_outcomes=actual,
    )

  def _expected_outcomes(self, treatment):
    spec = yaml.safe_load(_TREATMENT_VOCAB.read_text(encoding="utf-8"))
    included = set(spec["treatments"][treatment]["included_steps"])
    return {
      step: "executed" if step in included else "skipped_by_treatment"
      for step in _ALL_STEPS
    }
