from pathlib import Path

from tools.conformance_evaluation.check_mode import CheckPipeline
from tools.conformance_evaluation.spec_triad_traceability import (
  SpecTriadTraceabilityChecker,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DEFAULT_CONTRACT_FEATURE_MAP = {
  "XDI-FOUND-001": "foundation",
  "XDI-RUNTIME-001": "runtime",
  "XDI-EVAL-001": "evaluation",
  "XDI-ANALYSIS-001": "analysis",
  "XDI-WM-001": "workflow-management",
  "XDI-SI-001": "self-improvement",
  "XDI-CE-001": "conformance-evaluation",
}

DEFAULT_IMPLEMENTATION_REFS = [
  "tests/runtime/test_t009_validation_bridge.py",
  "tests/analysis/test_analysis_t008_conformance_intake.py",
  "tests/self-improvement/test_t004_proposal_model.py",
  "tests/conformance-evaluation/test_conformance_evaluation.py",
]


class CrossFeatureDriftWorkflow:
  def __init__(self, root):
    self.root = Path(root)

  def default_fixture_path(self):
    return (
      PROJECT_ROOT
      / "tests"
      / "fixtures"
      / "conformance-evaluation"
      / "cross-feature-contract-ownership.yaml"
    )

  def run(
    self,
    *,
    run_date,
    ownership_fixture=None,
    implementation_refs=None,
    contract_feature_map=None,
  ):
    ownership_fixture = Path(ownership_fixture) if ownership_fixture else self.default_fixture_path()
    implementation_refs = implementation_refs or DEFAULT_IMPLEMENTATION_REFS
    contract_feature_map = contract_feature_map or DEFAULT_CONTRACT_FEATURE_MAP

    pipeline_result = CheckPipeline(self.root).run(
      feature="_cross_feature",
      implementation_refs=implementation_refs,
      feature_partitioning="cross-feature representative drift items",
      prompt_text="Implementation only. Do not read existing upstream documents.",
      run_date=run_date,
      ownership_fixture=ownership_fixture,
      write_spec_update_drafts=True,
    )

    draft_result = pipeline_result["contract_ownership"]["spec_update_draft_files"]
    check_record = (
      self.root
      / ".reviewcompass"
      / "specs"
      / "_cross_feature"
      / "conformance"
      / f"{run_date}-check.md"
    )

    return {
      "feature": "_cross_feature",
      "check_record": str(check_record),
      "draft_dir": draft_result["draft_dir"],
      "draft_files": draft_result["draft_files"],
      "traceability": SpecTriadTraceabilityChecker(self.root).check(contract_feature_map),
      "pipeline": pipeline_result,
    }
