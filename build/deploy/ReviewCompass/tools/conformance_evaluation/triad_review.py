"""Triad review application policy for conformance-evaluation."""


class TriadReviewPolicy:
  FULL_STAGES = {"feature_partitioning_estimation", "requirements_estimation", "comparison"}
  LIGHTWEIGHT_STAGES = {"design_estimation", "intent_inference"}

  def intensity_for(self, stage: str) -> str:
    if stage in self.FULL_STAGES:
      return "full"
    if stage in self.LIGHTWEIGHT_STAGES:
      return "lightweight"
    raise ValueError(f"unknown_triad_stage: {stage}")

  def metadata_template(self) -> dict:
    return {
      "severity": None,
      "judgment": None,
      "depth": None,
      "evidence_type": None,
      "verifying_commands": [],
      "findings_by_method": {},
    }

  def handle_api_result(self, result: dict) -> dict:
    status = result.get("status")
    return {
      "retry": status == "timeout",
      "partial_failure": status == "partial_failure",
      "status": status,
    }

