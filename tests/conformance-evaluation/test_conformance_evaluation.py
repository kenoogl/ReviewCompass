from pathlib import Path
import json
import re

import pytest
import yaml

from tools.conformance_evaluation.check_mode import CheckPipeline
from tools.conformance_evaluation.comparison_model import ComparisonModel
from tools.conformance_evaluation.criteria import CRITERIA, CriteriaError, criterion_by_id
from tools.conformance_evaluation.estimation_model import EstimationModel
from tools.conformance_evaluation.evaluation_record import EvaluationRecordModel, RecordError
from tools.conformance_evaluation.generation_mode import GenerationPipeline
from tools.conformance_evaluation.machine_verification import MachineVerification, VerificationStatus
from tools.conformance_evaluation.mode_switch import ModeSwitch, ModeSwitchError
from tools.conformance_evaluation.post_hoc_intent_diff import (
  ALLOWED_CLASSIFICATIONS,
  PostHocIntentDiff,
  PostHocIntentDiffError,
)
from tools.conformance_evaluation.triad_review import TriadReviewPolicy


ROOT = Path(__file__).resolve().parents[2]


def test_t001_layout_and_operation_docs_are_present():
  assert (ROOT / "tools" / "conformance_evaluation" / ".gitkeep").is_file()
  assert (ROOT / "tools" / "conformance_evaluation" / "schemas" / ".gitkeep").is_file()
  assert (ROOT / "tests" / "conformance-evaluation" / ".gitkeep").is_file()
  assert (ROOT / "schemas" / "review-criteria" / "README.md").is_file()
  text = (ROOT / "docs" / "operations" / "CONFORMANCE_EVALUATION.md").read_text(encoding="utf-8")
  assert "conformance/<日付>-<mode>.md" in text
  assert "reviews/ とは別" in text
  assert ".reviewcompass/conformance/inferred/<日付>/" in text
  tools_readme = (ROOT / "tools" / "README.md").read_text(encoding="utf-8")
  assert "tools/conformance_evaluation/" in tools_readme
  assert "tools/conformance-evaluation-check.py" in tools_readme


def test_t002_mode_switch_requires_explicit_mode():
  switch = ModeSwitch({"check": lambda payload: ("check", payload), "generation": lambda payload: ("generation", payload)})
  assert switch.dispatch("check", {"x": 1}) == ("check", {"x": 1})
  assert switch.dispatch("generation", {"x": 2}) == ("generation", {"x": 2})
  with pytest.raises(ModeSwitchError):
    switch.dispatch("auto", {})
  assert not switch.has_auto_detection()


def test_t003_generation_outputs_human_reviewable_documents(tmp_path):
  pipeline = GenerationPipeline(tmp_path)
  result = pipeline.generate(
    app_root=tmp_path,
    feature="billing",
    run_date="2026-06-04",
    code_refs=["src/billing.py:1-20"],
  )
  assert result["layer_policy"]["feature-partitioning"] == "human_collaboration"
  assert result["layer_policy"]["intent"] == "human_collaboration"
  assert result["layer_policy"]["requirements"] == "automatic_estimation"
  assert result["layer_policy"]["design"] == "automatic_estimation"
  assert result["layer_policy"]["tasks"] == "excluded"
  for path in result["documents"]:
    text = Path(path).read_text(encoding="utf-8")
    assert "Introduction" in text
    assert "Boundary Context" in text
    assert "Requirements" in text
    assert "src/billing.py:1-20" in text
    assert "human_review_required: true" in text
  assert (tmp_path / ".reviewcompass" / "specs" / "billing" / "conformance" / "2026-06-04-generation.md").is_file()


def test_t004_check_mode_enforces_two_stage_isolation(tmp_path):
  pipeline = CheckPipeline(tmp_path)
  result = pipeline.run(
    feature="billing",
    implementation_refs=["src/billing.py:1-20"],
    feature_partitioning="billing boundary",
    prompt_text="Implementation only. Do not read existing upstream documents.",
    run_date="2026-06-04",
  )
  assert result["stages"] == ["estimate", "compare"]
  assert result["estimation_input"]["feature_partitioning"] == "billing boundary"
  assert result["intent_policy"] == "reference_only"
  assert result["partitioning_check"] == "standard_disabled"
  assert result["findings"][0]["severity"] == "INFO"
  record_path = tmp_path / ".reviewcompass" / "specs" / "billing" / "conformance" / "2026-06-04-check.md"
  assert record_path.is_file()
  record_text = record_path.read_text(encoding="utf-8")
  assert "## 食い違い所見" in record_text
  assert "finding_id: CF-001" in record_text
  assert "criterion_id: criterion-1" in record_text
  with pytest.raises(ValueError):
    pipeline.run(
      feature="billing",
      implementation_refs=["src/billing.py:1-20"],
      feature_partitioning="billing boundary",
      prompt_text="Please read requirements.md before estimating.",
      run_date="2026-06-04",
    )


def test_t004_check_partitioning_enabled_branch_is_explicit(tmp_path):
  pipeline = CheckPipeline(tmp_path)
  result = pipeline.run(
    feature="billing",
    implementation_refs=["src/billing.py:1-20"],
    feature_partitioning="billing boundary",
    prompt_text="Implementation only. Do not read existing upstream documents.",
    run_date="2026-06-04",
    check_partitioning=True,
  )
  assert result["partitioning_check"] == "enabled"
  assert result["partitioning_input"] == "billing boundary"


def test_t005_six_criteria_are_two_axis_only():
  assert len(CRITERIA) == 6
  assert {item.axis for item in CRITERIA} == {"requirements", "design"}
  assert {item.criterion_id for item in CRITERIA} == {f"criterion-{index}" for index in range(1, 7)}
  assert criterion_by_id("criterion-1").axis == "requirements"
  with pytest.raises(CriteriaError):
    criterion_by_id("intent")
  data = yaml.safe_load((ROOT / "schemas" / "review-criteria" / "conformance_evaluation.yaml").read_text(encoding="utf-8"))
  assert len(data["criteria"]) == 6
  for item in data["criteria"]:
    assert {"id", "axis", "criterion_short_name", "name", "sub_structure"} <= set(item)
    assert item["sub_structure"] == ["要点", "詳細抽出", "深掘り", "該当なし"]


def test_t006_estimation_runs_design_before_requirements():
  model = EstimationModel()
  result = model.estimate(["src/billing.py:1-20"])
  assert result["order"] == ["design", "requirements"]
  assert result["design"]["evidence_refs"] == ["src/billing.py:1-20"]
  assert result["requirements"]["derived_from"] == "design"
  assert result["confidence"] in {"high", "medium", "low"}
  assert result["excluded_layers"] == ["feature-partitioning", "tasks"]
  assert result["intent"]["reference_axis"] == "intent"


def test_t007_comparison_records_mismatches_and_ids():
  model = ComparisonModel()
  finding = model.compare_one(
    criterion_id="criterion-2",
    existing={"section": "API", "claim": "returns YAML", "code_refs": ["src/a.py:1-2"]},
    inferred={"section": "API", "claim": "returns JSON", "code_refs": ["src/a.py:1-2"]},
  )
  assert finding["finding_id"] == "CF-001"
  assert finding["judgment_id"] == "JD-001"
  assert finding["finding_type"] == "discrepancy"
  assert finding["correspondence_type"] == "claim_correspondence"
  assert finding["existing_text"] == "returns YAML"
  assert finding["estimated_text"] == "returns JSON"
  assert len(finding["discrepancy_description"]) >= 30
  assert finding["implementation_code_refs"] == [
    {"path": "src/a.py", "lines": "1-2"},
  ]
  assert finding["mismatch"] is True
  assert finding["mismatch_types"] == ["claim_mismatch"]
  intent = model.intent_difference("existing intent", "inferred intent")
  assert intent["reference_axis"] == "intent"
  assert intent["eligible_for_must_fix"] is False
  assert model.format_next_id("CF", 1000) == "CF-1000"
  boundary_model = ComparisonModel()
  boundary_model.finding_counter = 998
  assert boundary_model.compare_one(
    criterion_id="criterion-1",
    existing={"section": "A", "claim": "x", "code_refs": ["src/a.py:1"]},
    inferred={"section": "B", "claim": "x", "code_refs": ["src/a.py:1"]},
  )["finding_id"] == "CF-999"
  assert boundary_model.compare_one(
    criterion_id="criterion-1",
    existing={"section": "A", "claim": "x", "code_refs": ["src/a.py:1"]},
    inferred={"section": "B", "claim": "x", "code_refs": ["src/a.py:1"]},
  )["finding_id"] == "CF-1000"


def test_t008_triad_review_policy_applies_stage_and_intensity():
  policy = TriadReviewPolicy()
  assert policy.intensity_for("requirements_estimation") == "full"
  assert policy.intensity_for("design_estimation") == "lightweight"
  assert policy.intensity_for("comparison") == "full"
  metadata = policy.metadata_template()
  assert {"severity", "judgment", "depth", "evidence_type", "verifying_commands"} <= set(metadata)
  assert policy.handle_api_result({"status": "timeout"})["retry"] is True
  assert policy.handle_api_result({"status": "partial_failure"})["partial_failure"] is True


def test_t009_evaluation_record_front_matter_and_placement(tmp_path):
  model = EvaluationRecordModel(tmp_path)
  path = model.write_record(
    feature="billing",
    mode_internal="check",
    run_date="2026-06-04",
    author="primary",
    reviewer="judgment",
    target_commit="abc123",
    materialization_commit_hash="def456",
    related_records=["runtime/run.yaml"],
    body="## 機械検査結果\nOK\n",
  )
  assert "conformance" in path.parts
  text = path.read_text(encoding="utf-8")
  assert "type: conformance_evaluation" in text
  assert "mode_internal: check" in text
  assert "target_commit: abc123" in text
  assert "materialization_commit_hash:" not in text
  assert "related_artifacts:" in text
  assert "self_improvement: def456" in text
  assert (ROOT / "tools" / "conformance_evaluation" / "schemas" / "evaluation_record.schema.json").is_file()
  with pytest.raises(RecordError):
    model.write_record(
      feature="billing",
      mode_internal="check",
      run_date="2026-06-04",
      author="same",
      reviewer="same",
      target_commit="abc123",
      materialization_commit_hash="def456",
      related_records=[],
      body="",
    )


def test_t010_dependency_shape_matches_feature_dependency():
  import yaml

  data = yaml.safe_load((ROOT / "stages" / "feature-dependency.yaml").read_text(encoding="utf-8"))
  deps = data["features"]["conformance-evaluation"]["depends_on"]
  assert deps == {
    "foundation": "hard",
    "runtime": "review",
    "evaluation": "review",
    "workflow-management": "review",
  }


def test_t011_interfaces_do_not_reverse_self_improvement_direction():
  from tools.conformance_evaluation.interfaces import Interfaces

  interfaces = Interfaces()
  assert interfaces.self_improvement_direction() == "conformance-evaluation -> self-improvement"
  assert interfaces.foundation_reference_only(["foundation_vocab_ref"])
  assert not interfaces.foundation_reference_only(["not_foundation_but_contains_foundation_word"])
  assert interfaces.commit_hashes_are_independent("target-a", "materialized-b")
  assert not interfaces.commit_hashes_are_independent("abc", "abc")


def test_t012_machine_verification_mv6_is_blocking(tmp_path):
  verifier = MachineVerification(tmp_path)
  ok = verifier.check_prompt_isolation(
    prompt_text="Implementation only. 自律探索禁止: existing upstream docs must not be read.",
    forbidden_paths=["requirements.md", "design.md", "intent.md"],
    run_id="run-001",
  )
  assert ok.status == VerificationStatus.OK
  prompt_log = tmp_path / "logs" / "estimation" / "run-001" / "prompt.log"
  assert prompt_log.is_file()
  log_text = prompt_log.read_text(encoding="utf-8")
  assert "run_id: run-001" in log_text
  assert "prompt_text:" in log_text
  assert "Implementation only." in log_text
  bad = verifier.check_prompt_isolation(
    prompt_text="Read requirements.md before estimating.",
    forbidden_paths=["requirements.md", "design.md", "intent.md"],
    run_id="run-002",
  )
  assert bad.status == VerificationStatus.DEVIATION
  assert bad.fail_closed == "blocking"


def test_t013_traceability_smoke():
  tasks_text = (ROOT / ".reviewcompass" / "specs" / "conformance-evaluation" / "tasks.md").read_text(encoding="utf-8")
  for index in range(1, 17):
    assert f"T-{index:03d}" in tasks_text
    task_block = re.search(rf"### T-{index:03d}：.*?(?=^### T-|\Z)", tasks_text, re.S | re.M)
    assert task_block is not None
    assert "対応要件" in task_block.group(0)
    assert "テスト要件" in task_block.group(0)
  assert "DVT" in tasks_text


def test_t016_post_hoc_intent_diff_outputs_candidates_and_record(tmp_path):
  tasks_path = tmp_path / ".reviewcompass" / "specs" / "workflow-management" / "tasks.md"
  tasks_path.parent.mkdir(parents=True)
  original_tasks = "既存 tasks 本文\n"
  tasks_path.write_text(original_tasks, encoding="utf-8")
  reopen_path = tmp_path / "stages" / "in-progress" / "reopen-procedure-2026-06-09.yaml"
  reopen_path.parent.mkdir(parents=True)
  original_reopen = (
    "process_id: reopen-procedure\n"
    "pending_gates:\n"
    "  - stages/implementation.yaml#triad-review\n"
  )
  reopen_path.write_text(original_reopen, encoding="utf-8")

  extractor = PostHocIntentDiff(tmp_path)
  result = extractor.extract(
    added_intent="既存システムに intent を後から追加した場合も仕様駆動開発で下流工程へ進める。",
    feature_partitioning="conformance-evaluation は差分候補抽出、workflow-management は reopen 伝播を担当する。",
    existing_specs={
      "conformance-evaluation": {
        "requirements": "Requirement 10: 既存システム差分抽出",
        "design": "post-hoc intent diff model",
        "tasks": "T-016",
      },
      "workflow-management": {
        "requirements": "Requirement 9: 後追い intent の下流再展開",
        "design": "downstream_impact_decisions",
        "tasks": str(tasks_path),
      },
    },
    implementation_refs=[
      {
        "path": "tools/conformance_evaluation/post_hoc_intent_diff.py",
        "symbol": "PostHocIntentDiff.extract",
      },
      {
        "path": "tools/check-workflow-action.py",
        "symbol": "build_in_progress_next_action",
      },
    ],
    run_date="2026-06-09",
  )

  assert result["mode_internal"] == "post_hoc_intent_diff"
  assert result["added_intent"] == "既存システムに intent を後から追加した場合も仕様駆動開発で下流工程へ進める。"
  assert {candidate["feature"] for candidate in result["candidates"]} == {
    "conformance-evaluation",
    "workflow-management",
  }
  allowed = {
    "existing_sufficient",
    "spec_update_candidate",
    "design_conflict_candidate",
    "downstream_impact_candidate",
    "implementation_change_candidate",
  }
  for candidate in result["candidates"]:
    assert {
      "feature",
      "phase",
      "classification",
      "code_refs",
      "existing_spec_refs",
      "reasoning_summary",
      "needs_human_decision",
    } <= set(candidate)
    assert candidate["classification"] in allowed

  wm_candidates = [
    candidate for candidate in result["candidates"]
    if candidate["feature"] == "workflow-management"
  ]
  assert wm_candidates[0]["classification"] == "downstream_impact_candidate"
  assert wm_candidates[0]["handoff_target"] == "workflow-management"
  assert tasks_path.read_text(encoding="utf-8") == original_tasks
  assert reopen_path.read_text(encoding="utf-8") == original_reopen

  record_path = Path(result["record_path"])
  assert record_path.is_file()
  record_text = record_path.read_text(encoding="utf-8")
  assert "type: conformance_evaluation" in record_text
  assert "mode_internal: post_hoc_intent_diff" in record_text
  assert "post_hoc_intent_diff" in record_text
  assert "workflow-management" in record_text


def test_t016_post_hoc_intent_diff_rejects_unknown_classification(tmp_path):
  extractor = PostHocIntentDiff(tmp_path)
  with pytest.raises(PostHocIntentDiffError):
    extractor.validate_candidate(
      {
        "feature": "conformance-evaluation",
        "phase": "requirements",
        "classification": "fixed_checklist_match",
        "code_refs": [],
        "existing_spec_refs": [],
        "reasoning_summary": "固定チェックリストだけの分類は許可しない。",
        "needs_human_decision": False,
      }
    )


def test_t016_post_hoc_intent_diff_schema_tracks_classification_contract():
  schema_path = ROOT / "tools" / "conformance_evaluation" / "schemas" / "post_hoc_intent_diff.schema.json"
  schema = json.loads(schema_path.read_text(encoding="utf-8"))

  assert set(schema["properties"]["classification"]["enum"]) == ALLOWED_CLASSIFICATIONS
  assert "tasks" in schema["properties"]["phase"]["enum"]
  assert "needs_human_decision" in schema["required"]


def test_conformance_evaluation_specs_track_contract_ownership_and_spec_update_drafts():
  requirements = (ROOT / ".reviewcompass" / "specs" / "conformance-evaluation" / "requirements.md").read_text(encoding="utf-8")
  design = (ROOT / ".reviewcompass" / "specs" / "conformance-evaluation" / "design.md").read_text(encoding="utf-8")
  tasks = (ROOT / ".reviewcompass" / "specs" / "conformance-evaluation" / "tasks.md").read_text(encoding="utf-8")

  for text in (requirements, design, tasks):
    assert "contract ownership map" in text
    assert "spec update proposals" in text
    assert "draft-only spec update artifacts" in text
    assert "requirements.md, design.md, tasks.md" in text


def test_conformance_evaluation_specs_route_formal_spec_updates_through_reopen():
  requirements = (ROOT / ".reviewcompass" / "specs" / "conformance-evaluation" / "requirements.md").read_text(encoding="utf-8")
  design = (ROOT / ".reviewcompass" / "specs" / "conformance-evaluation" / "design.md").read_text(encoding="utf-8")
  tasks = (ROOT / ".reviewcompass" / "specs" / "conformance-evaluation" / "tasks.md").read_text(encoding="utf-8")

  for text in (requirements, design, tasks):
    assert "workflow-management の reopen 手続き" in text
    assert "triad-review / review-wave / alignment / approval" in text
    assert "requirements.md, design.md, tasks.md を直接書き換えない" in text
    assert "phase: tasks" in text
    assert "tasks.md 本体の推定・再作成やタスク分解の確定は行わない" in text

  assert "resolved 扱いにしてはならない" in requirements
  assert "reopen handoff package" in design
  assert "T-017" in tasks


def test_cross_feature_conformance_workflow_is_operationalized():
  operations = (ROOT / "docs" / "operations" / "CONFORMANCE_EVALUATION.md").read_text(encoding="utf-8")
  tasks = (ROOT / ".reviewcompass" / "specs" / "conformance-evaluation" / "tasks.md").read_text(encoding="utf-8")

  for phrase in (
    "cross-feature drift workflow",
    "code → ownership fixture",
    "check record",
    "spec update drafts",
    "spec adoption",
    "tools/conformance_evaluation/cross_feature_workflow.py",
    "tools/conformance-evaluation-cross-feature.py",
    "spec triad traceability test",
    "commit",
  ):
    assert phrase in operations

  t015 = re.search(r"### T-015：.*?(?=^## |\Z)", tasks, re.S | re.M)
  assert t015 is not None
  t015_text = t015.group(0)
  for phrase in (
    "cross-feature drift workflow",
    "tools/conformance_evaluation/cross_feature_workflow.py",
    "tools/conformance-evaluation-cross-feature.py",
    "tests/conformance-evaluation/test_spec_update_adoption.py",
    "tools/conformance_evaluation/spec_triad_traceability.py",
    "spec triad traceability test",
    "docs/operations/CONFORMANCE_EVALUATION.md",
  ):
    assert phrase in t015_text
