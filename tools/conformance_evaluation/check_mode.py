"""Check mode pipeline with two-stage isolation."""
from pathlib import Path
import yaml

from tools.conformance_evaluation.comparison_model import ComparisonModel
from tools.conformance_evaluation.estimation_model import EstimationModel
from tools.conformance_evaluation.evaluation_record import EvaluationRecordModel
from tools.conformance_evaluation.machine_verification import MachineVerification, VerificationStatus


class CheckPipeline:
  def __init__(self, root: Path):
    self.root = Path(root)

  def run(
    self,
    *,
    feature: str,
    implementation_refs: list,
    feature_partitioning: str,
    prompt_text: str,
    run_date: str,
    check_partitioning: bool = False,
  ) -> dict:
    isolation = MachineVerification(self.root).check_prompt_isolation(
      prompt_text=prompt_text,
      forbidden_paths=["intent.md", "requirements.md", "design.md"],
      run_id=f"{feature}-{run_date}-check",
    )
    if isolation.status == VerificationStatus.DEVIATION:
      raise ValueError("; ".join(isolation.reasons))
    estimate = EstimationModel().estimate(implementation_refs)
    comparison = ComparisonModel().compare_one(
      criterion_id="criterion-1",
      existing={"section": "placeholder", "claim": "placeholder", "code_refs": implementation_refs},
      inferred={"section": "placeholder", "claim": "placeholder", "code_refs": implementation_refs},
    )
    comparison["severity"] = comparison.get("severity", "INFO")
    findings_yaml = yaml.safe_dump([comparison], allow_unicode=True, sort_keys=False)
    EvaluationRecordModel(self.root).write_record(
      feature=feature,
      mode_internal="check",
      run_date=run_date,
      author="primary",
      reviewer="judgment",
      target_commit="unknown",
      materialization_commit_hash="independent",
      related_records=[],
      body=(
        "## 機械検査結果\n"
        "MV-6 OK\n\n"
        "## 食い違い所見\n"
        "```yaml\n"
        f"{findings_yaml}"
        "```\n"
      ),
    )
    return {
      "stages": ["estimate", "compare"],
      "estimation": estimate,
      "estimation_input": {"feature_partitioning": feature_partitioning},
      "intent_policy": "reference_only",
      "partitioning_check": "enabled" if check_partitioning else "standard_disabled",
      "partitioning_input": feature_partitioning if check_partitioning else None,
      "findings": [comparison],
    }
