"""T-008 のテスト：除外と注意点の報告。"""
import json

from reporting.caveat_register_writer import CaveatRegisterWriter
from reporting.exclusion_report_writer import ExclusionReportWriter


def test_exclusion_report_writer_outputs_invalid_and_blocked_runs(tmp_path):
  """除外報告は valid 以外の実行と理由を出力する。"""
  classifications = [
    {
      "run_id": "run-1",
      "classification": "valid",
      "reason_codes": [],
      "phase_profile": "design",
      "treatment": "primary",
      "review_mode": "runtime_mediated",
    },
    {
      "run_id": "run-2",
      "classification": "invalid",
      "reason_codes": ["evidence_class_invalid"],
      "phase_profile": "design",
      "treatment": "adversarial",
      "review_mode": "runtime_mediated",
    },
    {
      "run_id": "run-3",
      "classification": "analysis_blocked",
      "reason_codes": ["missing_required_input"],
      "phase_profile": "tasks",
      "treatment": "judgment",
      "review_mode": "api_mediated",
    },
  ]
  path = ExclusionReportWriter().write(tmp_path / "experiments" / "analysis", classifications)
  report = json.loads(path.read_text(encoding="utf-8"))
  assert [entry["run_id"] for entry in report["entries"]] == ["run-2", "run-3"]
  assert report["summary"]["excluded_count"] == 2
  assert set(report["entries"][0]) == {
    "run_id",
    "classification",
    "reason_codes",
    "reason_details",
    "phase_profile",
    "treatment",
    "review_mode",
  }


def test_caveat_register_writer_separates_data_and_runtime_quality(tmp_path):
  """注意点登録は data_quality と runtime_quality を区別する。"""
  caveats = [
    {
      "caveat_id": "C-001",
      "run_id": "run-1",
      "caveat_type": "data_quality",
      "reason_code": "low_sample_size",
    },
    {
      "caveat_id": "C-002",
      "run_id": "run-2",
      "caveat_type": "runtime_quality",
      "reason_code": "step_retry",
    },
  ]
  path = CaveatRegisterWriter().write(tmp_path / "experiments" / "analysis", caveats)
  register = json.loads(path.read_text(encoding="utf-8"))
  assert register["summary"]["by_caveat_type"] == {
    "data_quality": 1,
    "runtime_quality": 1,
  }
  assert register["entries"] == caveats
