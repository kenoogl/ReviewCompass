"""post_hoc_intent_diff の実データ試行（2026-06-09）を fixture として再生する回帰テスト。

fixture は実記録 2 件（r1=後追い intent の下流展開、r2=LLM 判断に基づくレビュー収集）の
入力と期待記録本文を固定したもの。ツールは LLM を呼ばない決定的処理のため、
生成記録が期待記録とバイト一致することを検証する（2026-06-12 利用者決定「案 a」）。
"""
from pathlib import Path

import pytest
import yaml

from tools.conformance_evaluation.post_hoc_intent_diff import PostHocIntentDiff


ROOT = Path(__file__).resolve().parents[2]
FIXTURE_ROOT = ROOT / "tests" / "fixtures" / "conformance-evaluation" / "post-hoc-intent-diff"


@pytest.mark.parametrize("case", ["real-data-r1", "real-data-r2"])
def test_post_hoc_intent_diff_replays_real_data_fixture(tmp_path, case):
  fixture = FIXTURE_ROOT / case
  inputs = yaml.safe_load((fixture / "input.yaml").read_text(encoding="utf-8"))
  expected_record = (fixture / "expected-record.md").read_text(encoding="utf-8")

  result = PostHocIntentDiff(tmp_path).extract(
    added_intent=inputs["added_intent"],
    feature_partitioning=inputs["feature_partitioning"],
    existing_specs=inputs["existing_specs"],
    implementation_refs=inputs["implementation_refs"],
    run_date=inputs["run_date"],
  )

  record_path = Path(result["record_path"])
  assert record_path.is_file()
  assert record_path.name == f"{inputs['run_date']}-post-hoc-intent-diff.md"
  assert record_path.read_text(encoding="utf-8") == expected_record

  assert result["mode_internal"] == "post_hoc_intent_diff"
  assert [c["candidate_id"] for c in result["candidates"]] == [
    "PHID-CE-001",
    "PHID-WM-001",
  ]
  wm = result["candidates"][1]
  assert wm["handoff_target"] == "workflow-management"
  assert wm["write_policy"] == "handoff_only"
  for candidate in result["candidates"]:
    assert candidate["existing_spec_refs"], "実仕様への参照が空であってはならない"
    assert candidate["code_refs"], "実装参照が空であってはならない"


@pytest.mark.parametrize("case", ["real-data-r1", "real-data-r2"])
def test_real_data_fixture_expected_record_matches_canonical_record(case):
  """fixture の期待記録が、正本記録（リポジトリ内の実記録）から逸脱していないことの自己検査。"""
  canonical_names = {
    "real-data-r1": "2026-06-09-post-hoc-intent-diff.md",
    "real-data-r2": "2026-06-09-real-data-r2-post-hoc-intent-diff.md",
  }
  canonical = (
    ROOT
    / ".reviewcompass"
    / "specs"
    / "conformance-evaluation"
    / "conformance"
    / canonical_names[case]
  )
  expected = FIXTURE_ROOT / case / "expected-record.md"
  assert expected.read_text(encoding="utf-8") == canonical.read_text(encoding="utf-8")
