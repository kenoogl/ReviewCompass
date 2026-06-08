from pathlib import Path

import pytest

from tools.conformance_evaluation.check_mode import CheckPipeline
from tools.conformance_evaluation.contract_ownership import (
  ContractOwnershipMap,
  ContractOwnershipMapError,
  SpecUpdateDraftWriter,
  load_contract_ownership_items,
  workflow_management_seed_items,
)


ROOT = Path(__file__).resolve().parents[2]


def test_contract_ownership_map_records_provisional_owners_and_sources():
  ownership_map = ContractOwnershipMap()
  item = ownership_map.add_item(
    contract_id="XDI-WM-001",
    feature="workflow-management",
    classification="spec-missing",
    primary_owner_candidate="operations",
    secondary_owner_candidate="tool_contract",
    contract_refs=[
      ".reviewcompass/specs/workflow-management/requirements.md",
      ".reviewcompass/specs/workflow-management/design.md",
      "docs/operations/WORKFLOW_NAVIGATION.md",
    ],
    evidence_refs=[
      "tools/check-workflow-action.py",
      "tests/tools/test_check_workflow_action.py",
    ],
    related_clusters=["XDRIFT-001", "XDRIFT-002"],
  )

  assert item["contract_id"] == "XDI-WM-001"
  assert item["owner_status"] == "provisional"
  assert item["primary_owner_candidate"] == "operations"
  assert item["secondary_owner_candidate"] == "tool_contract"
  assert item["source_refs"] == [
    {
      "path": ".reviewcompass/specs/workflow-management/requirements.md",
      "source_kind": "requirements",
    },
    {
      "path": ".reviewcompass/specs/workflow-management/design.md",
      "source_kind": "design",
    },
    {
      "path": "docs/operations/WORKFLOW_NAVIGATION.md",
      "source_kind": "operations",
    },
    {
      "path": "tools/check-workflow-action.py",
      "source_kind": "implementation",
    },
    {
      "path": "tests/tools/test_check_workflow_action.py",
      "source_kind": "test",
    },
  ]


def test_contract_ownership_map_rejects_unknown_vocabularies():
  ownership_map = ContractOwnershipMap()

  with pytest.raises(ContractOwnershipMapError, match="unknown_owner_candidate"):
    ownership_map.add_item(
      contract_id="XDI-CE-001",
      feature="conformance-evaluation",
      classification="ownership-unclear",
      primary_owner_candidate="conformance-evaluation",
      secondary_owner_candidate="requirements",
      contract_refs=[],
      evidence_refs=[],
      related_clusters=[],
    )

  with pytest.raises(ContractOwnershipMapError, match="unknown_classification"):
    ownership_map.add_item(
      contract_id="XDI-META-001",
      feature="all",
      classification="boundary_violation",
      primary_owner_candidate="carry_forward",
      secondary_owner_candidate="requirements",
      contract_refs=[],
      evidence_refs=[],
      related_clusters=[],
    )


def test_contract_ownership_map_groups_update_candidates_by_spec_file():
  ownership_map = ContractOwnershipMap()
  ownership_map.add_item(
    contract_id="XDI-SI-001",
    feature="self-improvement",
    classification="spec-missing",
    primary_owner_candidate="requirements",
    secondary_owner_candidate="test_contract",
    contract_refs=[".reviewcompass/specs/self-improvement/requirements.md"],
    evidence_refs=["tools/self_improvement/approval_model.py"],
    related_clusters=["XDRIFT-004"],
  )
  ownership_map.add_item(
    contract_id="XDI-RUNTIME-001",
    feature="runtime",
    classification="spec-missing",
    primary_owner_candidate="design",
    secondary_owner_candidate="tool_contract",
    contract_refs=[".reviewcompass/specs/runtime/design.md"],
    evidence_refs=["tests/runtime/test_t009_validation_bridge.py"],
    related_clusters=["XDRIFT-006"],
  )
  ownership_map.add_item(
    contract_id="XDI-META-003",
    feature="conformance-evaluation",
    classification="ownership-unclear",
    primary_owner_candidate="carry_forward",
    secondary_owner_candidate="test_contract",
    contract_refs=[".reviewcompass/specs/conformance-evaluation/tasks.md"],
    evidence_refs=["docs/notes/2026-06-08-cross-feature-conformance-drift-audit.md"],
    related_clusters=["XDRIFT-007"],
    depends_on=["XDI-META-001", "XDI-META-002"],
  )

  candidates = ownership_map.update_candidates()

  assert candidates == {
    ".reviewcompass/specs/self-improvement/requirements.md": ["XDI-SI-001"],
    ".reviewcompass/specs/runtime/design.md": ["XDI-RUNTIME-001"],
    ".reviewcompass/specs/conformance-evaluation/tasks.md": ["XDI-META-003"],
  }
  assert ownership_map.item_by_id("XDI-META-003")["depends_on"] == [
    "XDI-META-001",
    "XDI-META-002",
  ]


def test_contract_ownership_map_builds_spec_update_proposals():
  ownership_map = ContractOwnershipMap()
  ownership_map.add_item(
    contract_id="XDI-REQ-001",
    feature="workflow-management",
    classification="spec-missing",
    primary_owner_candidate="requirements",
    secondary_owner_candidate="design",
    contract_refs=[
      ".reviewcompass/specs/workflow-management/requirements.md",
      ".reviewcompass/specs/workflow-management/design.md",
    ],
    evidence_refs=["tests/tools/test_check_workflow_action.py"],
    related_clusters=["XDRIFT-001"],
    claim="next action is a user-visible workflow contract",
  )
  ownership_map.add_item(
    contract_id="XDI-DES-001",
    feature="runtime",
    classification="spec-missing",
    primary_owner_candidate="design",
    secondary_owner_candidate="tool_contract",
    contract_refs=[".reviewcompass/specs/runtime/design.md"],
    evidence_refs=["tests/runtime/test_t009_validation_bridge.py"],
    related_clusters=["XDRIFT-006"],
    claim="validation bridge state transitions are design contracts",
  )
  ownership_map.add_item(
    contract_id="XDI-TASK-001",
    feature="conformance-evaluation",
    classification="ownership-unclear",
    primary_owner_candidate="carry_forward",
    secondary_owner_candidate="test_contract",
    contract_refs=[".reviewcompass/specs/conformance-evaluation/tasks.md"],
    evidence_refs=["docs/notes/2026-06-08-cross-feature-conformance-drift-audit.md"],
    related_clusters=["XDRIFT-007"],
    claim="line-level traceability needs a follow-up decision",
    depends_on=["XDI-META-001"],
  )

  assert ownership_map.spec_update_proposals() == [
    {
      "target_file": ".reviewcompass/specs/workflow-management/requirements.md",
      "target_kind": "requirements",
      "contract_ids": ["XDI-REQ-001"],
      "claims": ["next action is a user-visible workflow contract"],
      "needs_human_decision": False,
    },
    {
      "target_file": ".reviewcompass/specs/runtime/design.md",
      "target_kind": "design",
      "contract_ids": ["XDI-DES-001"],
      "claims": ["validation bridge state transitions are design contracts"],
      "needs_human_decision": False,
    },
    {
      "target_file": ".reviewcompass/specs/conformance-evaluation/tasks.md",
      "target_kind": "tasks",
      "contract_ids": ["XDI-TASK-001"],
      "claims": ["line-level traceability needs a follow-up decision"],
      "needs_human_decision": True,
    },
  ]


def test_contract_ownership_map_builds_spec_update_drafts_without_applying():
  ownership_map = ContractOwnershipMap()
  ownership_map.add_item(
    contract_id="XDI-REQ-001",
    feature="workflow-management",
    classification="spec-missing",
    primary_owner_candidate="requirements",
    secondary_owner_candidate="design",
    contract_refs=[".reviewcompass/specs/workflow-management/requirements.md"],
    evidence_refs=["tests/tools/test_check_workflow_action.py"],
    related_clusters=["XDRIFT-001"],
    claim="next action is a user-visible workflow contract",
  )
  ownership_map.add_item(
    contract_id="XDI-TASK-001",
    feature="conformance-evaluation",
    classification="ownership-unclear",
    primary_owner_candidate="carry_forward",
    secondary_owner_candidate="test_contract",
    contract_refs=[".reviewcompass/specs/conformance-evaluation/tasks.md"],
    evidence_refs=["docs/notes/2026-06-08-cross-feature-conformance-drift-audit.md"],
    related_clusters=["XDRIFT-007"],
    claim="line-level traceability needs a follow-up decision",
    depends_on=["XDI-META-001"],
  )

  assert ownership_map.spec_update_drafts() == [
    {
      "target_file": ".reviewcompass/specs/workflow-management/requirements.md",
      "target_kind": "requirements",
      "apply_status": "draft_only",
      "draft_heading": "Implementation-derived requirements candidates",
      "draft_bullets": [
        "- XDI-REQ-001: next action is a user-visible workflow contract",
      ],
      "needs_human_decision": False,
    },
    {
      "target_file": ".reviewcompass/specs/conformance-evaluation/tasks.md",
      "target_kind": "tasks",
      "apply_status": "draft_only",
      "draft_heading": "Carry-forward implementation drift tasks",
      "draft_bullets": [
        "- XDI-TASK-001: line-level traceability needs a follow-up decision",
      ],
      "needs_human_decision": True,
    },
  ]


def test_spec_update_draft_writer_materializes_markdown_without_applying(tmp_path):
  ownership_map = ContractOwnershipMap()
  ownership_map.add_item(
    contract_id="XDI-REQ-001",
    feature="workflow-management",
    classification="spec-missing",
    primary_owner_candidate="requirements",
    secondary_owner_candidate="design",
    contract_refs=[".reviewcompass/specs/workflow-management/requirements.md"],
    evidence_refs=["tests/tools/test_check_workflow_action.py"],
    related_clusters=["XDRIFT-001"],
    claim="next action is a user-visible workflow contract",
  )

  writer = SpecUpdateDraftWriter(tmp_path)
  result = writer.write(
    feature="workflow-management",
    run_date="2026-06-08",
    drafts=ownership_map.spec_update_drafts(),
  )

  expected_path = (
    tmp_path
    / ".reviewcompass"
    / "specs"
    / "workflow-management"
    / "conformance"
    / "2026-06-08-spec-update-drafts"
    / "reviewcompass-specs-workflow-management-requirements.md"
  )
  assert result == {
    "draft_dir": str(expected_path.parent),
    "draft_files": [str(expected_path)],
  }
  assert expected_path.is_file()
  text = expected_path.read_text(encoding="utf-8")
  assert "apply_status: draft_only" in text
  assert "target_file: .reviewcompass/specs/workflow-management/requirements.md" in text
  assert "# Implementation-derived requirements candidates" in text
  assert "- XDI-REQ-001: next action is a user-visible workflow contract" in text
  assert not (tmp_path / ".reviewcompass" / "specs" / "workflow-management" / "requirements.md").exists()


def test_mixed_contract_ownership_fixture_builds_spec_update_proposals():
  fixture_path = (
    ROOT
    / "tests"
    / "fixtures"
    / "conformance-evaluation"
    / "mixed-contract-ownership.yaml"
  )
  ownership_map = ContractOwnershipMap.from_items(load_contract_ownership_items(fixture_path))

  assert ownership_map.spec_update_proposals() == [
    {
      "target_file": ".reviewcompass/specs/workflow-management/requirements.md",
      "target_kind": "requirements",
      "contract_ids": ["XDI-REQ-001"],
      "claims": ["next action is a user-visible workflow contract"],
      "needs_human_decision": False,
    },
    {
      "target_file": ".reviewcompass/specs/runtime/design.md",
      "target_kind": "design",
      "contract_ids": ["XDI-DES-001"],
      "claims": ["validation bridge state transitions are design contracts"],
      "needs_human_decision": False,
    },
    {
      "target_file": ".reviewcompass/specs/conformance-evaluation/tasks.md",
      "target_kind": "tasks",
      "contract_ids": ["XDI-TASK-001"],
      "claims": ["line-level traceability needs a follow-up decision"],
      "needs_human_decision": True,
    },
  ]


def test_cross_feature_contract_ownership_fixture_covers_representative_drift_items():
  fixture_path = (
    ROOT
    / "tests"
    / "fixtures"
    / "conformance-evaluation"
    / "cross-feature-contract-ownership.yaml"
  )
  ownership_map = ContractOwnershipMap.from_items(
    load_contract_ownership_items(fixture_path)
  )

  assert {item["feature"] for item in ownership_map.items} == {
    "foundation",
    "runtime",
    "evaluation",
    "analysis",
    "workflow-management",
    "self-improvement",
    "conformance-evaluation",
  }
  assert [item["contract_id"] for item in ownership_map.items] == [
    "XDI-FOUND-001",
    "XDI-RUNTIME-001",
    "XDI-EVAL-001",
    "XDI-ANALYSIS-001",
    "XDI-WM-001",
    "XDI-SI-001",
    "XDI-CE-001",
  ]
  assert ownership_map.item_by_id("XDI-FOUND-001")["source_refs"][0] == {
    "path": ".reviewcompass/specs/foundation/requirements.md",
    "source_kind": "requirements",
  }
  assert ownership_map.item_by_id("XDI-EVAL-001")[
    "primary_owner_candidate"
  ] == "operations"
  assert ownership_map.item_by_id("XDI-CE-001")["depends_on"] == [
    "XDI-META-001",
    "XDI-META-002",
  ]


def test_cross_feature_contract_ownership_fixture_builds_spec_update_drafts():
  fixture_path = (
    ROOT
    / "tests"
    / "fixtures"
    / "conformance-evaluation"
    / "cross-feature-contract-ownership.yaml"
  )
  ownership_map = ContractOwnershipMap.from_items(
    load_contract_ownership_items(fixture_path)
  )

  proposals = ownership_map.spec_update_proposals()
  assert proposals == [
    {
      "target_file": ".reviewcompass/specs/runtime/design.md",
      "target_kind": "design",
      "contract_ids": ["XDI-RUNTIME-001"],
      "claims": [
        "runtime manifest, state transition, provenance, and immutability contracts are more precise in tests than in prose specs",
      ],
      "needs_human_decision": False,
    },
    {
      "target_file": ".reviewcompass/specs/analysis/design.md",
      "target_kind": "design",
      "contract_ids": ["XDI-ANALYSIS-001"],
      "claims": [
        "analysis intake and destination boundary guards are implementation-derived design contracts",
      ],
      "needs_human_decision": False,
    },
    {
      "target_file": ".reviewcompass/specs/self-improvement/requirements.md",
      "target_kind": "requirements",
      "contract_ids": ["XDI-SI-001"],
      "claims": [
        "self-improvement approval, rejection, proposal id, and carry-forward guards are externally visible requirements candidates",
      ],
      "needs_human_decision": False,
    },
    {
      "target_file": ".reviewcompass/specs/conformance-evaluation/tasks.md",
      "target_kind": "tasks",
      "contract_ids": ["XDI-CE-001"],
      "claims": [
        "cross-feature drift clustering and contract ownership outputs need a follow-up implementation decision",
      ],
      "needs_human_decision": True,
    },
  ]


def test_workflow_management_seed_items_capture_representative_drift():
  ownership_map = ContractOwnershipMap.from_items(workflow_management_seed_items())

  assert [item["contract_id"] for item in ownership_map.items] == [
    "WM-DRIFT-001",
    "WM-DRIFT-002",
    "WM-DRIFT-005",
    "WM-DRIFT-008",
  ]
  assert ownership_map.item_by_id("WM-DRIFT-001")["claim"] == (
    "next subcommand is the canonical workflow navigation entry point"
  )
  assert ownership_map.item_by_id("WM-DRIFT-002")["related_clusters"] == [
    "XDRIFT-002",
    "XDRIFT-003",
    "XDRIFT-005",
  ]
  assert ownership_map.item_by_id("WM-DRIFT-005")["primary_owner_candidate"] == "requirements"
  assert ownership_map.item_by_id("WM-DRIFT-008")["secondary_owner_candidate"] == "design"

  assert ownership_map.update_candidates() == {
    ".reviewcompass/specs/workflow-management/requirements.md": [
      "WM-DRIFT-001",
      "WM-DRIFT-002",
      "WM-DRIFT-005",
      "WM-DRIFT-008",
    ],
  }


def test_contract_ownership_items_can_load_from_structured_fixture():
  fixture_path = (
    ROOT
    / "tests"
    / "fixtures"
    / "conformance-evaluation"
    / "workflow-management-contract-ownership.yaml"
  )

  items = load_contract_ownership_items(fixture_path)
  ownership_map = ContractOwnershipMap.from_items(items)

  assert items == workflow_management_seed_items()
  assert ownership_map.item_by_id("WM-DRIFT-002")["claim"] == (
    "post-write target detection and manifest verification are implementation contracts"
  )
  assert ownership_map.update_candidates() == {
    ".reviewcompass/specs/workflow-management/requirements.md": [
      "WM-DRIFT-001",
      "WM-DRIFT-002",
      "WM-DRIFT-005",
      "WM-DRIFT-008",
    ],
  }


def test_check_pipeline_can_emit_contract_ownership_candidates(tmp_path):
  pipeline = CheckPipeline(tmp_path)
  result = pipeline.run(
    feature="workflow-management",
    implementation_refs=["tools/check-workflow-action.py"],
    feature_partitioning="workflow-management boundary",
    prompt_text="Implementation only. Do not read existing upstream documents.",
    run_date="2026-06-08",
    ownership_items=workflow_management_seed_items(),
  )

  assert result["contract_ownership"]["items"][0]["contract_id"] == "WM-DRIFT-001"
  assert result["contract_ownership"]["update_candidates"] == {
    ".reviewcompass/specs/workflow-management/requirements.md": [
      "WM-DRIFT-001",
      "WM-DRIFT-002",
      "WM-DRIFT-005",
      "WM-DRIFT-008",
    ],
  }

  record_path = (
    tmp_path
    / ".reviewcompass"
    / "specs"
    / "workflow-management"
    / "conformance"
    / "2026-06-08-check.md"
  )
  record_text = record_path.read_text(encoding="utf-8")
  assert "## Contract Ownership Candidates" in record_text
  assert "WM-DRIFT-001" in record_text


def test_check_pipeline_can_load_contract_ownership_fixture(tmp_path):
  fixture_path = (
    ROOT
    / "tests"
    / "fixtures"
    / "conformance-evaluation"
    / "workflow-management-contract-ownership.yaml"
  )
  pipeline = CheckPipeline(tmp_path)
  result = pipeline.run(
    feature="workflow-management",
    implementation_refs=["tools/check-workflow-action.py"],
    feature_partitioning="workflow-management boundary",
    prompt_text="Implementation only. Do not read existing upstream documents.",
    run_date="2026-06-08",
    ownership_fixture=fixture_path,
  )

  assert result["contract_ownership"]["items"][1]["contract_id"] == "WM-DRIFT-002"
  assert result["contract_ownership"]["items"][1]["source_refs"][0] == {
    "path": ".reviewcompass/specs/workflow-management/requirements.md",
    "source_kind": "requirements",
  }


def test_check_pipeline_includes_spec_update_proposals(tmp_path):
  fixture_path = (
    ROOT
    / "tests"
    / "fixtures"
    / "conformance-evaluation"
    / "workflow-management-contract-ownership.yaml"
  )
  pipeline = CheckPipeline(tmp_path)
  result = pipeline.run(
    feature="workflow-management",
    implementation_refs=["tools/check-workflow-action.py"],
    feature_partitioning="workflow-management boundary",
    prompt_text="Implementation only. Do not read existing upstream documents.",
    run_date="2026-06-08",
    ownership_fixture=fixture_path,
  )

  assert result["contract_ownership"]["spec_update_proposals"] == [
    {
      "target_file": ".reviewcompass/specs/workflow-management/requirements.md",
      "target_kind": "requirements",
      "contract_ids": [
        "WM-DRIFT-001",
        "WM-DRIFT-002",
        "WM-DRIFT-005",
        "WM-DRIFT-008",
      ],
      "claims": [
        "next subcommand is the canonical workflow navigation entry point",
        "post-write target detection and manifest verification are implementation contracts",
        "commit approval records require target_sha256 coverage for staged content",
        "autonomous plan and ledger contracts are implemented as workflow-management safety contracts",
      ],
      "needs_human_decision": False,
    },
  ]
  assert result["contract_ownership"]["spec_update_drafts"][0] == {
    "target_file": ".reviewcompass/specs/workflow-management/requirements.md",
    "target_kind": "requirements",
    "apply_status": "draft_only",
    "draft_heading": "Implementation-derived requirements candidates",
    "draft_bullets": [
      "- WM-DRIFT-001: next subcommand is the canonical workflow navigation entry point",
      "- WM-DRIFT-002: post-write target detection and manifest verification are implementation contracts",
      "- WM-DRIFT-005: commit approval records require target_sha256 coverage for staged content",
      "- WM-DRIFT-008: autonomous plan and ledger contracts are implemented as workflow-management safety contracts",
    ],
    "needs_human_decision": False,
  }

  record_path = (
    tmp_path
    / ".reviewcompass"
    / "specs"
    / "workflow-management"
    / "conformance"
    / "2026-06-08-check.md"
  )
  record_text = record_path.read_text(encoding="utf-8")
  assert "## Spec Update Proposals" in record_text
  assert "## Spec Update Drafts" in record_text
  assert "target_file: .reviewcompass/specs/workflow-management/requirements.md" in record_text
  assert "WM-DRIFT-008" in record_text


def test_check_pipeline_can_materialize_spec_update_draft_files(tmp_path):
  fixture_path = (
    ROOT
    / "tests"
    / "fixtures"
    / "conformance-evaluation"
    / "workflow-management-contract-ownership.yaml"
  )
  pipeline = CheckPipeline(tmp_path)
  result = pipeline.run(
    feature="workflow-management",
    implementation_refs=["tools/check-workflow-action.py"],
    feature_partitioning="workflow-management boundary",
    prompt_text="Implementation only. Do not read existing upstream documents.",
    run_date="2026-06-08",
    ownership_fixture=fixture_path,
    write_spec_update_drafts=True,
  )

  draft_result = result["contract_ownership"]["spec_update_draft_files"]
  assert draft_result["draft_dir"].endswith(
    ".reviewcompass/specs/workflow-management/conformance/2026-06-08-spec-update-drafts"
  )
  assert len(draft_result["draft_files"]) == 1
  draft_path = Path(draft_result["draft_files"][0])
  assert draft_path.is_file()
  text = draft_path.read_text(encoding="utf-8")
  assert "apply_status: draft_only" in text
  assert "# Implementation-derived requirements candidates" in text
  assert "WM-DRIFT-001" in text
  assert not (tmp_path / ".reviewcompass" / "specs" / "workflow-management" / "requirements.md").exists()


def test_check_pipeline_can_materialize_cross_feature_spec_update_drafts(tmp_path):
  fixture_path = (
    ROOT
    / "tests"
    / "fixtures"
    / "conformance-evaluation"
    / "cross-feature-contract-ownership.yaml"
  )
  pipeline = CheckPipeline(tmp_path)
  result = pipeline.run(
    feature="_cross_feature",
    implementation_refs=[
      "tests/runtime/test_t009_validation_bridge.py",
      "tests/analysis/test_analysis_t008_conformance_intake.py",
      "tests/self-improvement/test_t004_proposal_model.py",
      "tests/conformance-evaluation/test_conformance_evaluation.py",
    ],
    feature_partitioning="cross-feature representative drift items",
    prompt_text="Implementation only. Do not read existing upstream documents.",
    run_date="2026-06-08",
    ownership_fixture=fixture_path,
    write_spec_update_drafts=True,
  )

  draft_result = result["contract_ownership"]["spec_update_draft_files"]
  assert draft_result["draft_dir"].endswith(
    ".reviewcompass/specs/_cross_feature/conformance/2026-06-08-spec-update-drafts"
  )
  draft_files = [Path(path) for path in draft_result["draft_files"]]
  assert [path.name for path in draft_files] == [
    "reviewcompass-specs-runtime-design.md",
    "reviewcompass-specs-analysis-design.md",
    "reviewcompass-specs-self-improvement-requirements.md",
    "reviewcompass-specs-conformance-evaluation-tasks.md",
  ]
  for path in draft_files:
    assert path.is_file()
    text = path.read_text(encoding="utf-8")
    assert "apply_status: draft_only" in text
    assert "target_file: .reviewcompass/specs/" in text
  assert "XDI-RUNTIME-001" in draft_files[0].read_text(encoding="utf-8")
  assert "needs_human_decision: true" in draft_files[-1].read_text(encoding="utf-8")
  assert not (tmp_path / ".reviewcompass" / "specs" / "runtime" / "design.md").exists()
