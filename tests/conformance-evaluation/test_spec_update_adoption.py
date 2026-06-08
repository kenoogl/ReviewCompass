from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


XDI_SPEC_MATRIX = {
  "XDI-FOUND-001": "foundation",
  "XDI-RUNTIME-001": "runtime",
  "XDI-EVAL-001": "evaluation",
  "XDI-ANALYSIS-001": "analysis",
  "XDI-WM-001": "workflow-management",
  "XDI-SI-001": "self-improvement",
  "XDI-CE-001": "conformance-evaluation",
}


def _read(path):
  return (ROOT / path).read_text(encoding="utf-8")


def test_cross_feature_xdi_contracts_are_traceable_across_spec_triad():
  missing_refs = []

  for contract_id, feature in XDI_SPEC_MATRIX.items():
    for spec_name in ("requirements", "design", "tasks"):
      path = f".reviewcompass/specs/{feature}/{spec_name}.md"
      if contract_id not in _read(path):
        missing_refs.append(f"{path}: {contract_id}")

  assert missing_refs == []


def test_cross_feature_runtime_design_contract_is_adopted():
  text = _read(".reviewcompass/specs/runtime/design.md")

  assert "XDI-RUNTIME-001" in text
  assert "run_manifest.yaml" in text
  assert "state transition" in text
  assert "provenance" in text
  assert "immutable" in text


def test_cross_feature_foundation_contract_is_adopted():
  text = _read(".reviewcompass/specs/foundation/design.md")

  assert "XDI-FOUND-001" in text
  assert "completion validator" in text
  assert "encoding convention validator" in text
  assert "strategy coverage" in text


def test_cross_feature_evaluation_contract_is_adopted():
  text = _read(".reviewcompass/specs/evaluation/design.md")

  assert "XDI-EVAL-001" in text
  assert "bundle placement" in text
  assert "admission readiness" in text
  assert "staleness" in text
  assert "dogfooding metrics" in text


def test_cross_feature_analysis_design_contract_is_adopted():
  text = _read(".reviewcompass/specs/analysis/design.md")

  assert "XDI-ANALYSIS-001" in text
  assert "intake boundary guard" in text
  assert "destination boundary guard" in text
  assert "生実行ディレクトリ" in text


def test_cross_feature_workflow_management_contract_is_adopted():
  text = _read(".reviewcompass/specs/workflow-management/design.md")

  assert "XDI-WM-001" in text
  assert "post-write verification" in text
  assert "commit approval" in text
  assert "audit trail" in text
  assert "autonomous ledger" in text


def test_cross_feature_self_improvement_requirements_contract_is_adopted():
  text = _read(".reviewcompass/specs/self-improvement/requirements.md")

  assert "XDI-SI-001" in text
  assert "approval guard" in text
  assert "rejection guard" in text
  assert "proposal_id" in text
  assert "carry-forward guard" in text


def test_cross_feature_conformance_tasks_carry_forward_is_adopted():
  text = _read(".reviewcompass/specs/conformance-evaluation/tasks.md")

  assert "XDI-CE-001" in text
  assert "cross-feature drift clustering" in text
  assert "contract ownership outputs" in text
  assert "follow-up implementation decision" in text
