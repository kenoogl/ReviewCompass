"""T-004 のテスト：提案モデル。

対応タスク：self-improvement tasks.md T-004
対応設計節：design.md §8.1〜§8.9
対応要件：Requirement 3 受入 1〜5、Requirement 4 受入 1〜5
"""
import json

import pytest
import yaml

from tools.self_improvement.proposal_model import (
  ProposalError,
  ProposalModel,
  validate_proposal,
)


EVIDENCE = [
  {
    "source": "review_record",
    "location": "reviews/2026-06-04.yaml",
    "observation": "提案の根拠として十分な長さの観察記録があり、後から追跡できる",
  }
]


BASE_SIGNAL = {
  "signal_id": "SE-001",
  "signal_type": "discipline_absence",
  "observed_pattern": "実体運用に定常的なパターンがある",
  "related_disciplines": [],
  "motivating_evidence_seed": EVIDENCE,
}


def _write_yaml(path, data):
  path.parent.mkdir(parents=True, exist_ok=True)
  path.write_text(
    yaml.safe_dump(data, allow_unicode=True, sort_keys=False),
    encoding="utf-8",
  )


def test_t004_generates_all_five_proposal_types(tmp_path):
  model = ProposalModel(tmp_path)

  proposals = [
    model.create_proposal(
      proposal_type="new_discipline",
      target_discipline_path="docs/disciplines/discipline_new.md",
      signal=BASE_SIGNAL,
      proposed_change={
        "draft_discipline": "新規規律本文",
        "relationship_notes": "既存規律 [[discipline_existing]] との関係",
        "related_disciplines": ["docs/disciplines/discipline_existing.md"],
      },
      expected_effect="規律不在を解消する",
    ),
    model.create_proposal(
      proposal_type="update",
      target_discipline_path="docs/disciplines/discipline_update.md",
      signal=BASE_SIGNAL,
      proposed_change={"change_diff": "- old\n+ new"},
      expected_effect="既存規律を実体に合わせる",
    ),
    model.create_proposal(
      proposal_type="status_change",
      target_discipline_path="docs/disciplines/discipline_status.md",
      signal=BASE_SIGNAL,
      proposed_change={"from": "aspirational", "to": "enforced"},
      expected_effect="正式化判断を記録する",
      statistical_evidence={"compliance_rate": 0.9},
    ),
    model.create_proposal(
      proposal_type="archive",
      target_discipline_path="docs/disciplines/discipline_old.md",
      signal=BASE_SIGNAL,
      proposed_change={"archive_readme_path": "docs/disciplines/archive/README.md"},
      expected_effect="撤廃済み規律を分離する",
    ),
    model.create_proposal(
      proposal_type="consolidation",
      target_discipline_path="docs/disciplines/discipline_merged.md",
      signal=BASE_SIGNAL,
      proposed_change={"mapping_table": "old -> merged"},
      expected_effect="重複規律を統合する",
      source_discipline_paths=[
        "docs/disciplines/discipline_a.md",
        "docs/disciplines/discipline_b.md",
      ],
    ),
  ]

  assert [proposal["proposal_type"] for proposal in proposals] == [
    "new_discipline",
    "update",
    "status_change",
    "archive",
    "consolidation",
  ]
  assert all(proposal["status"] == "pending" for proposal in proposals)
  assert all(proposal["proposal_id"].startswith("WP-") for proposal in proposals)


def test_t004_rejects_unknown_proposal_type_fail_closed(tmp_path):
  model = ProposalModel(tmp_path)

  with pytest.raises(ProposalError, match="unknown_proposal_type"):
    model.create_proposal(
      proposal_type="runtime_prompt",
      target_discipline_path="docs/disciplines/discipline_prompt.md",
      signal=BASE_SIGNAL,
      proposed_change={},
      expected_effect="範囲外の変更",
    )


def test_t004_validates_required_fields_and_target_pattern():
  proposal = {
    "proposal_id": "WP-001",
    "proposal_type": "update",
    "target_discipline_path": "runtime/prompts/main.md",
    "motivating_evidence": EVIDENCE,
    "proposed_change": {"change_diff": "- old\n+ new"},
    "expected_effect": "改善する",
    "status": "pending",
  }

  with pytest.raises(ProposalError, match="invalid_target_discipline_path"):
    validate_proposal(proposal)

  del proposal["expected_effect"]
  with pytest.raises(ProposalError, match="missing_required_fields"):
    validate_proposal(proposal)


def test_t004_requires_motivating_evidence_three_fields():
  proposal = {
    "proposal_id": "WP-001",
    "proposal_type": "update",
    "target_discipline_path": "docs/disciplines/discipline_update.md",
    "motivating_evidence": [{"source": "review_record", "location": "reviews/x.yaml"}],
    "proposed_change": {"change_diff": "- old\n+ new"},
    "expected_effect": "改善する",
    "status": "pending",
  }

  with pytest.raises(ProposalError, match="invalid_motivating_evidence"):
    validate_proposal(proposal)


def test_t004_accepts_exact_motivating_evidence_three_fields():
  proposal = {
    "proposal_id": "WP-001",
    "proposal_type": "update",
    "target_discipline_path": "docs/disciplines/discipline_update.md",
    "motivating_evidence": EVIDENCE,
    "proposed_change": {"change_diff": "- old\n+ new"},
    "expected_effect": "改善する",
    "status": "pending",
  }

  validate_proposal(proposal)


def test_t004_allocates_next_id_across_four_workflow_directories(tmp_path):
  for directory, proposal_id in [
    ("proposals", "WP-001"),
    ("approved-updates", "WP-099"),
    ("rejected-updates", "WP-100"),
    ("rollback", "RB-002"),
  ]:
    _write_yaml(
      tmp_path / "learning" / "workflow" / directory / f"{proposal_id}.yaml",
      {"proposal_id": proposal_id},
    )

  assert ProposalModel(tmp_path).next_proposal_id("WP") == "WP-101"
  assert ProposalModel(tmp_path).next_proposal_id("RB") == "RB-003"


def test_t004_extends_id_width_after_999(tmp_path):
  _write_yaml(
    tmp_path / "learning" / "workflow" / "approved-updates" / "WP-999.yaml",
    {"proposal_id": "WP-999"},
  )

  assert ProposalModel(tmp_path).next_proposal_id("WP") == "WP-1000"


def test_t004_enforces_type_specific_requirements(tmp_path):
  model = ProposalModel(tmp_path)

  with pytest.raises(ProposalError, match="missing_change_diff"):
    model.create_proposal(
      proposal_type="update",
      target_discipline_path="docs/disciplines/discipline_update.md",
      signal=BASE_SIGNAL,
      proposed_change={},
      expected_effect="改善する",
    )
  with pytest.raises(ProposalError, match="missing_source_discipline_paths"):
    model.create_proposal(
      proposal_type="consolidation",
      target_discipline_path="docs/disciplines/discipline_merged.md",
      signal=BASE_SIGNAL,
      proposed_change={"mapping_table": "old -> merged"},
      expected_effect="統合する",
    )


def test_t004_new_discipline_requires_machine_checkable_relationship(tmp_path):
  model = ProposalModel(tmp_path)

  with pytest.raises(ProposalError, match="missing_related_disciplines"):
    model.create_proposal(
      proposal_type="new_discipline",
      target_discipline_path="docs/disciplines/discipline_new.md",
      signal=BASE_SIGNAL,
      proposed_change={
        "draft_discipline": "新規規律本文",
        "relationship_notes": "既存規律との関係",
      },
      expected_effect="規律不在を解消する",
    )

  proposal = model.create_proposal(
    proposal_type="new_discipline",
    target_discipline_path="docs/disciplines/discipline_new.md",
    signal=BASE_SIGNAL,
    proposed_change={
      "draft_discipline": "新規規律本文",
      "relationship_notes": "既存規律 [[discipline_existing]] との関係",
      "related_disciplines": ["docs/disciplines/discipline_existing.md"],
    },
    expected_effect="規律不在を解消する",
  )

  assert proposal["proposed_change"]["related_disciplines"] == [
    "docs/disciplines/discipline_existing.md"
  ]


def test_t004_proposal_schema_documents_owned_constraints():
  schema = json.loads(
    (ProposalModel.project_root() / "learning" / "workflow" / "schemas" / "proposal.schema.json")
    .read_text(encoding="utf-8")
  )

  assert schema["properties"]["proposal_type"]["enum"] == [
    "new_discipline",
    "update",
    "status_change",
    "archive",
    "consolidation",
  ]
  assert schema["properties"]["status"]["enum"] == [
    "pending",
    "approved",
    "rejected",
    "superseded",
  ]
  assert schema["properties"]["target_discipline_path"]["pattern"] == "^docs/disciplines/discipline_.*\\.md$"
  assert "allOf" in schema
  assert schema["required"] == [
    "proposal_id",
    "proposal_type",
    "target_discipline_path",
    "motivating_evidence",
    "proposed_change",
    "expected_effect",
    "status",
  ]
