from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _read(path):
  return (ROOT / path).read_text(encoding="utf-8")


def test_cross_feature_runtime_design_contract_is_adopted():
  text = _read(".reviewcompass/specs/runtime/design.md")

  assert "XDI-RUNTIME-001" in text
  assert "run_manifest.yaml" in text
  assert "state transition" in text
  assert "provenance" in text
  assert "immutable" in text


def test_cross_feature_analysis_design_contract_is_adopted():
  text = _read(".reviewcompass/specs/analysis/design.md")

  assert "XDI-ANALYSIS-001" in text
  assert "intake boundary guard" in text
  assert "destination boundary guard" in text
  assert "生実行ディレクトリ" in text


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
