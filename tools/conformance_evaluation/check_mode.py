"""Check mode pipeline with two-stage isolation."""
from pathlib import Path
import yaml

from tools.conformance_evaluation.comparison_model import ComparisonModel
from tools.conformance_evaluation.contract_ownership import (
  ContractOwnershipMap,
  SpecUpdateDraftWriter,
  load_contract_ownership_items,
)
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
    ownership_items=None,
    ownership_fixture=None,
    write_spec_update_drafts: bool = False,
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
    contract_ownership = None
    ownership_section = ""
    proposal_section = ""
    draft_section = ""
    if ownership_items is not None and ownership_fixture is not None:
      raise ValueError("ownership_items_and_fixture_are_mutually_exclusive")
    if ownership_fixture is not None:
      ownership_items = load_contract_ownership_items(ownership_fixture)
    if ownership_items is not None:
      ownership_map = ContractOwnershipMap.from_items(ownership_items)
      contract_ownership = {
        "items": ownership_map.items,
        "update_candidates": ownership_map.update_candidates(),
        "spec_update_proposals": ownership_map.spec_update_proposals(),
        "spec_update_drafts": ownership_map.spec_update_drafts(),
      }
      if write_spec_update_drafts:
        contract_ownership["spec_update_draft_files"] = SpecUpdateDraftWriter(self.root).write(
          feature=feature,
          run_date=run_date,
          drafts=contract_ownership["spec_update_drafts"],
        )
      ownership_yaml = yaml.safe_dump(contract_ownership, allow_unicode=True, sort_keys=False)
      proposal_yaml = yaml.safe_dump(
        contract_ownership["spec_update_proposals"],
        allow_unicode=True,
        sort_keys=False,
      )
      draft_yaml = yaml.safe_dump(
        contract_ownership["spec_update_drafts"],
        allow_unicode=True,
        sort_keys=False,
      )
      ownership_section = (
        "\n## Contract Ownership Candidates\n"
        "```yaml\n"
        f"{ownership_yaml}"
        "```\n"
      )
      proposal_section = (
        "\n## Spec Update Proposals\n"
        "```yaml\n"
        f"{proposal_yaml}"
        "```\n"
      )
      draft_section = (
        "\n## Spec Update Drafts\n"
        "```yaml\n"
        f"{draft_yaml}"
        "```\n"
      )
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
        f"{ownership_section}"
        f"{proposal_section}"
        f"{draft_section}"
      ),
    )
    result = {
      "stages": ["estimate", "compare"],
      "estimation": estimate,
      "estimation_input": {"feature_partitioning": feature_partitioning},
      "intent_policy": "reference_only",
      "partitioning_check": "enabled" if check_partitioning else "standard_disabled",
      "partitioning_input": feature_partitioning if check_partitioning else None,
      "findings": [comparison],
    }
    if contract_ownership is not None:
      result["contract_ownership"] = contract_ownership
    return result
