from pathlib import Path
import json
import subprocess
import sys

from tools.conformance_evaluation.cross_feature_workflow import (
  CrossFeatureDriftWorkflow,
)


ROOT = Path(__file__).resolve().parents[2]


def test_cross_feature_workflow_generates_check_record_drafts_and_traceability(tmp_path):
  fixture_path = (
    ROOT
    / "tests"
    / "fixtures"
    / "conformance-evaluation"
    / "cross-feature-contract-ownership.yaml"
  )
  workflow = CrossFeatureDriftWorkflow(tmp_path)

  result = workflow.run(
    run_date="2026-06-08",
    ownership_fixture=fixture_path,
    implementation_refs=[
      "tests/runtime/test_t009_validation_bridge.py",
      "tests/analysis/test_analysis_t008_conformance_intake.py",
      "tests/self-improvement/test_t004_proposal_model.py",
      "tests/conformance-evaluation/test_conformance_evaluation.py",
    ],
    contract_feature_map={
      "XDI-RUNTIME-001": "runtime",
      "XDI-ANALYSIS-001": "analysis",
    },
  )

  assert result["feature"] == "_cross_feature"
  assert result["check_record"].endswith(
    ".reviewcompass/specs/_cross_feature/conformance/2026-06-08-check.md"
  )
  assert Path(result["check_record"]).is_file()
  assert result["draft_dir"].endswith(
    ".reviewcompass/specs/_cross_feature/conformance/2026-06-08-spec-update-drafts"
  )
  assert [Path(path).name for path in result["draft_files"]] == [
    "reviewcompass-specs-runtime-design.md",
    "reviewcompass-specs-analysis-design.md",
    "reviewcompass-specs-self-improvement-requirements.md",
    "reviewcompass-specs-conformance-evaluation-tasks.md",
  ]
  assert result["traceability"] == {
    "ok": False,
    "checked_refs": 6,
    "missing_refs": [
      ".reviewcompass/specs/runtime/requirements.md: XDI-RUNTIME-001",
      ".reviewcompass/specs/runtime/design.md: XDI-RUNTIME-001",
      ".reviewcompass/specs/runtime/tasks.md: XDI-RUNTIME-001",
      ".reviewcompass/specs/analysis/requirements.md: XDI-ANALYSIS-001",
      ".reviewcompass/specs/analysis/design.md: XDI-ANALYSIS-001",
      ".reviewcompass/specs/analysis/tasks.md: XDI-ANALYSIS-001",
    ],
  }


def test_cross_feature_workflow_uses_default_fixture_and_refs(tmp_path):
  workflow = CrossFeatureDriftWorkflow(tmp_path)
  result = workflow.run(run_date="2026-06-08")

  assert result["feature"] == "_cross_feature"
  assert len(result["draft_files"]) == 4
  assert result["traceability"]["checked_refs"] == 21


def test_cross_feature_workflow_cli_outputs_json(tmp_path):
  fixture_path = (
    ROOT
    / "tests"
    / "fixtures"
    / "conformance-evaluation"
    / "cross-feature-contract-ownership.yaml"
  )

  result = subprocess.run(
    [
      sys.executable,
      str(ROOT / "tools" / "conformance-evaluation-cross-feature.py"),
      "--root",
      str(tmp_path),
      "--run-date",
      "2026-06-08",
      "--ownership-fixture",
      str(fixture_path),
      "--json",
    ],
    cwd=ROOT,
    check=False,
    capture_output=True,
    text=True,
  )

  assert result.returncode == 0, result.stderr
  payload = json.loads(result.stdout)
  assert payload["feature"] == "_cross_feature"
  assert payload["check_record"].endswith(
    ".reviewcompass/specs/_cross_feature/conformance/2026-06-08-check.md"
  )
  assert len(payload["draft_files"]) == 4
  assert payload["traceability"]["checked_refs"] == 21


def test_cross_feature_workflow_cli_fails_closed_for_missing_fixture(tmp_path):
  result = subprocess.run(
    [
      sys.executable,
      str(ROOT / "tools" / "conformance-evaluation-cross-feature.py"),
      "--root",
      str(tmp_path),
      "--run-date",
      "2026-06-08",
      "--ownership-fixture",
      str(tmp_path / "missing.yaml"),
      "--json",
    ],
    cwd=ROOT,
    check=False,
    capture_output=True,
    text=True,
  )

  assert result.returncode == 2
  payload = json.loads(result.stdout)
  assert payload["ok"] is False
  assert payload["error"] == "ownership_fixture_not_found"
