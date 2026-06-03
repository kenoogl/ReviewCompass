"""T-007 のテスト：比較器（comparison builder）。"""
import json

from comparison.mode_population_rule import ModePopulationRule
from comparison.phase_comparison_builder import PhaseComparisonBuilder
from comparison.treatment_comparison_builder import TreatmentComparisonBuilder
from comparison.valid_population_rule import ValidPopulationRule
from comparison.version_consistency_validator import VersionConsistencyValidator


RUNS = [
  {
    "run_id": "run-1",
    "target_id": "target-1",
    "classification": "valid",
    "treatment": "primary",
    "phase_profile": "design",
    "review_mode": "runtime_mediated",
    "protocol_version": "p1",
    "prompt_set_version": "q1",
    "finding_count": 2,
  },
  {
    "run_id": "run-2",
    "target_id": "target-1",
    "classification": "valid",
    "treatment": "adversarial",
    "phase_profile": "design",
    "review_mode": "runtime_mediated",
    "protocol_version": "p1",
    "prompt_set_version": "q1",
    "finding_count": 3,
  },
  {
    "run_id": "run-3",
    "target_id": "target-2",
    "classification": "invalid",
    "treatment": "judgment",
    "phase_profile": "tasks",
    "review_mode": "runtime_mediated",
    "protocol_version": "p1",
    "prompt_set_version": "q1",
    "finding_count": 9,
  },
  {
    "run_id": "run-4",
    "target_id": "target-3",
    "classification": "valid",
    "treatment": "judgment",
    "phase_profile": "tasks",
    "review_mode": "api_mediated",
    "protocol_version": "p1",
    "prompt_set_version": "q1",
    "finding_count": 4,
  },
]


def test_valid_population_rule_includes_only_valid_runs():
  """有効母集団規則は valid のみを含める。"""
  included = ValidPopulationRule().apply(RUNS)
  assert [run["run_id"] for run in included] == ["run-1", "run-2", "run-4"]


def test_mode_population_rule_separates_runtime_standard_from_other_modes():
  """runtime_mediated を標準集団、それ以外を別集団として分離する。"""
  result = ModePopulationRule().slice(RUNS)
  assert [run["run_id"] for run in result["standard_runtime_mediated"]] == ["run-1", "run-2", "run-3"]
  assert [run["run_id"] for run in result["by_review_mode"]["api_mediated"]] == ["run-4"]


def test_version_consistency_validator_detects_mixed_protocol():
  """比較セット内の規約版混在を検出する。"""
  runs = [dict(RUNS[0]), dict(RUNS[1], protocol_version="p2")]
  result = VersionConsistencyValidator().validate(runs)
  assert result.ok is False
  assert result.reason_codes == ["mixed_protocol_version"]


def test_treatment_comparison_builder_outputs_included_valid_runtime_runs(tmp_path):
  """treatment 比較は valid かつ runtime_mediated の実行だけを含める。"""
  path = TreatmentComparisonBuilder().write(tmp_path / "experiments" / "analysis", RUNS)
  payload = json.loads(path.read_text(encoding="utf-8"))
  assert payload["comparison_type"] == "treatment"
  assert payload["included_runs"] == ["run-1", "run-2"]
  assert set(payload["by_treatment"]) == {"primary", "adversarial"}


def test_phase_comparison_builder_keeps_phase_slices(tmp_path):
  """phase 比較はフェーズ別 slice を未分化に潰さない。"""
  path = PhaseComparisonBuilder().write(tmp_path / "experiments" / "analysis", RUNS)
  payload = json.loads(path.read_text(encoding="utf-8"))
  assert payload["comparison_type"] == "phase"
  assert payload["by_phase"]["design"]["included_runs"] == ["run-1", "run-2"]
  assert "tasks" not in payload["by_phase"]
