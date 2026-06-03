"""T-011 のテスト：分析機能の横断トレーサビリティ。"""
import importlib
import json
import re
from pathlib import Path

import yaml

from analysis.claim_mapping.claim_map_builder import ClaimMapBuilder
from analysis.common.reference_format import artifact_ref, resolve_artifact_ref
from analysis.destinations.destination_deriver import DestinationDeriver
from analysis.evidence_register.evidence_register_builder import (
  EvidenceRegisterBuilder,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
TASKS = REPO_ROOT / ".reviewcompass" / "specs" / "analysis" / "tasks.md"
DESIGN = REPO_ROOT / ".reviewcompass" / "specs" / "analysis" / "design.md"


def _guards():
  return importlib.import_module("analysis.traceability.completion_guards")


def _base_evidence(review_mode="runtime_mediated"):
  return {
    "evidence_id": "e1",
    "artifact_ref": artifact_ref(
      ref_type="evaluation_artifact",
      target_path="comparisons/treatment_comparisons.json",
      target_id="tc1",
    ),
    "source_analysis_manifest_ref": artifact_ref(
      ref_type="analysis_manifest",
      target_path="manifests/analysis_run_manifest.yaml",
      target_id="run1",
    ),
    "input_run_set_ref": artifact_ref(
      ref_type="run_set",
      target_path="manifests/run_set.json",
      target_id="rs1",
    ),
    "evidence_class": "valid",
    "review_mode": review_mode,
    "eligible_for_standard_comparison": True,
    "stale": False,
    "generated_at": "2026-05-01T00:00:00Z",
  }


def test_traceability_smoke_connects_claim_evidence_and_destination(tmp_path):
  """claim → evidence_register → destination manifest の追跡経路を通す。"""
  evidence_register = EvidenceRegisterBuilder().write(
    tmp_path,
    evidences=[_base_evidence()],
  )
  ClaimMapBuilder().write(
    tmp_path,
    claims=[
      {
        "claim_id": "c1",
        "claim_text": "ReviewCompass keeps claim evidence traceability.",
        "supporting_artifact_refs": [
          artifact_ref(
            ref_type="evidence_entry",
            target_path="shared/evidence_register.json",
            target_id="e1",
          )
        ],
        "maturity_label": "mature",
        "stale": False,
      }
    ],
  )
  DestinationDeriver().derive(
    tmp_path,
    analysis_logic_version="analysis-1",
    derivation_contract_version="1.0.0",
    evidences=[{"evidence_id": "e1", "review_mode": "runtime_mediated"}],
    caveats=[],
  )

  claim_map = json.loads((tmp_path / "shared" / "claim_map.json").read_text())
  evidence_ref = claim_map["claims"][0]["supporting_artifact_refs"][0]
  assert resolve_artifact_ref(evidence_ref, base_dir=tmp_path) == evidence_register

  manifest = yaml.safe_load(
    (tmp_path / "destinations" / "reports" / "manifest.yaml").read_text()
  )
  assert manifest["included_evidence_refs"] == [evidence_ref]


def test_completion_guard_confirms_analysis_owned_vocabularies():
  """analysis 所有 4 正本の値域を横断的に確認する。"""
  assert _guards().analysis_owned_vocabularies() == {
    "maturity_label": {"mature", "preliminary", "exploratory"},
    "limitation_type": {
      "invalid_data_exclusion",
      "partial_evidence",
      "methodological_limitation",
      "mixed_review_mode",
    },
    "fragment_type": {
      "claim_summary",
      "method_note",
      "limitation_note",
      "comparison_summary",
      "trend_summary",
    },
    "regeneration_status": {
      "pending",
      "in_progress",
      "completed",
      "failed",
    },
  }


def test_foundation_vocabularies_are_referenced_not_redefined():
  """foundation 7 語彙正本は analysis 側で参照のみを確認する。"""
  expected_names = {
    "counter_status",
    "validator_status",
    "evidence_class",
    "review_mode",
    "severity",
    "final_label",
    "confidence_label",
  }
  assert set(_guards().foundation_vocabularies(REPO_ROOT)) >= expected_names
  assert _guards().analysis_redefines_foundation_vocabularies(
    REPO_ROOT / "analysis",
    expected_names,
  ) == []


def test_requirements_traceability_covers_all_requirements_and_tasks():
  """要件追跡表が Requirement 1〜8 と T-001〜T-011 を双方向に含む。"""
  text = TASKS.read_text(encoding="utf-8")
  assert _guards().covered_requirements(text) == set(range(1, 9))
  assert _guards().covered_tasks(text) == {f"T-{index:03d}" for index in range(1, 12)}


def test_deferred_verification_table_has_deferral_reason_for_unresolved_items():
  """DVT の未解除項目は延期理由または解除トリガーを持つ。"""
  rows = _guards().deferred_verification_rows(TASKS.read_text(encoding="utf-8"))
  unresolved = [row for row in rows if "未解除" in row["status"]]
  assert unresolved
  assert all(row["has_deferral_reason"] for row in unresolved)


def test_design_completion_criteria_are_machine_checked_by_t011():
  """design.md 完成判定基準 8 項目を T-011 が明示的に受けている。"""
  design = DESIGN.read_text(encoding="utf-8")
  tasks = TASKS.read_text(encoding="utf-8")
  criteria = _guards().completion_criteria(design)
  assert len(criteria) == 8
  assert all(_guards().criteria_has_t011_gate(criterion, tasks) for criterion in criteria)


def test_test_file_responsibilities_are_declared():
  """テスト責務分担の明示が tasks.md に残っている。"""
  text = TASKS.read_text(encoding="utf-8")
  assert re.search(r"test_evidence_register\.py.*無声昇格", text)
  assert re.search(r"test_destinations\.py.*混在レビューモード", text)


def test_completion_guard_detects_evaluation_write_targets(tmp_path):
  """evaluation 成果物への書き込み経路は構造検査で検出する。"""
  source = tmp_path / "writer.py"
  source.write_text(
    "\n".join(
      [
        "from pathlib import Path",
        "",
        "def write_evaluation_result(root):",
        "  path = root / 'experiments' / 'conformance' / 'result.json'",
        "  path.write_text('{}')",
      ]
    )
    + "\n",
    encoding="utf-8",
  )

  violations = _guards().evaluation_write_violations(tmp_path)

  assert violations == [
    {
      "path": str(source),
      "line": 5,
      "target": "experiments/conformance/result.json",
      "operation": "write_text",
    }
  ]


def test_completion_guard_detects_experiments_analysis_write_targets(tmp_path):
  """experiments/analysis 配下への書き込み経路も検出する。"""
  source = tmp_path / "writer.py"
  source.write_text(
    "\n".join(
      [
        "from pathlib import Path",
        "",
        "def write_evaluation_analysis_result(root):",
        "  path = root / 'experiments' / 'analysis' / 'comparisons' / 'x.json'",
        "  path.write_text('{}')",
      ]
    )
    + "\n",
    encoding="utf-8",
  )

  violations = _guards().evaluation_write_violations(tmp_path)

  assert violations == [
    {
      "path": str(source),
      "line": 5,
      "target": "experiments/analysis/comparisons/x.json",
      "operation": "write_text",
    }
  ]


def test_analysis_implementation_does_not_write_evaluation_artifacts():
  """analysis 実装は evaluation 成果物へ書き込む経路を持たない。"""
  assert _guards().evaluation_write_violations(REPO_ROOT / "analysis") == []
