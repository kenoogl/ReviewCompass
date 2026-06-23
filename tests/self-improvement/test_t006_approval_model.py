"""T-006 のテスト：承認モデル。

対応タスク：self-improvement tasks.md T-006
対応設計節：design.md §10.1〜§10.5
対応要件：Requirement 6 受入 1〜5
"""
from pathlib import Path

import pytest
import yaml

from tools.self_improvement.approval_model import ApprovalError, ApprovalModel


def _write_proposal(path, proposal):
  path.parent.mkdir(parents=True, exist_ok=True)
  path.write_text(
    yaml.safe_dump(proposal, allow_unicode=True, sort_keys=False),
    encoding="utf-8",
  )


def _read_yaml(path):
  return yaml.safe_load(Path(path).read_text(encoding="utf-8"))


def _base_proposal(proposal_id="WP-001", status="pending"):
  return {
    "proposal_id": proposal_id,
    "proposal_type": "update",
    "target_discipline_path": ".reviewcompass/guidance/discipline_update.md",
    "motivating_evidence": [
      {
        "source": "review_record",
        "location": "reviews/2026-06-04.yaml",
        "observation": "承認モデルの状態遷移を検証するための十分な長さの観察記録",
      }
    ],
    "proposed_change": {"change_diff": "- old\n+ new"},
    "expected_effect": "規律を更新する",
    "status": status,
  }


def test_t006_approves_pending_proposal_with_explicit_user_approval(tmp_path):
  source = tmp_path / "learning" / "workflow" / "proposals" / "WP-001.yaml"
  _write_proposal(source, _base_proposal())

  result = ApprovalModel(tmp_path).approve(source, approval_text="承認します")

  target = tmp_path / "learning" / "workflow" / "approved-updates" / "WP-001.yaml"
  assert result == {
    "proposal_id": "WP-001",
    "from_status": "pending",
    "to_status": "approved",
    "source_path": "learning/workflow/proposals/WP-001.yaml",
    "target_path": "learning/workflow/approved-updates/WP-001.yaml",
    "move_operation": "git_mv_required",
  }
  assert not source.exists()
  assert _read_yaml(target)["status"] == "approved"


def test_t006_rejects_pending_proposal_with_explicit_user_rejection(tmp_path):
  source = tmp_path / "learning" / "workflow" / "proposals" / "WP-002.yaml"
  _write_proposal(source, _base_proposal("WP-002"))

  result = ApprovalModel(tmp_path).reject(source, approval_text="却下します")

  target = tmp_path / "learning" / "workflow" / "rejected-updates" / "WP-002.yaml"
  assert result["to_status"] == "rejected"
  assert result["target_path"] == "learning/workflow/rejected-updates/WP-002.yaml"
  assert _read_yaml(target)["status"] == "rejected"


def test_t006_rejects_pending_proposal_with_declined_adoption_phrase(tmp_path):
  source = tmp_path / "learning" / "workflow" / "proposals" / "WP-007.yaml"
  _write_proposal(source, _base_proposal("WP-007"))

  result = ApprovalModel(tmp_path).reject(source, approval_text="今回は採用しません")

  target = tmp_path / "learning" / "workflow" / "rejected-updates" / "WP-007.yaml"
  assert result["to_status"] == "rejected"
  assert _read_yaml(target)["status"] == "rejected"


def test_t006_does_not_approve_with_declined_adoption_phrase(tmp_path):
  source = tmp_path / "learning" / "workflow" / "proposals" / "WP-008.yaml"
  _write_proposal(source, _base_proposal("WP-008"))

  with pytest.raises(ApprovalError, match="explicit_user_approval_required"):
    ApprovalModel(tmp_path).approve(source, approval_text="今回は採用しません")


def test_t006_blocks_status_change_to_enforced_without_explicit_approval(tmp_path):
  source = tmp_path / "learning" / "workflow" / "proposals" / "WP-003.yaml"
  proposal = _base_proposal("WP-003")
  proposal["proposal_type"] = "status_change"
  proposal["proposed_change"] = {"from": "aspirational", "to": "enforced"}
  proposal["statistical_evidence"] = {"compliance_rate": 0.9}
  _write_proposal(source, proposal)

  with pytest.raises(ApprovalError, match="explicit_user_approval_required"):
    ApprovalModel(tmp_path).approve(source, approval_text="よさそう")


def test_t006_status_change_to_enforced_requires_formalization_approval(tmp_path):
  source = tmp_path / "learning" / "workflow" / "proposals" / "WP-003.yaml"
  proposal = _base_proposal("WP-003")
  proposal["proposal_type"] = "status_change"
  proposal["proposed_change"] = {"from": "aspirational", "to": "enforced"}
  proposal["statistical_evidence"] = {"compliance_rate": 0.9}
  _write_proposal(source, proposal)

  with pytest.raises(ApprovalError, match="explicit_enforcement_approval_required"):
    ApprovalModel(tmp_path).approve(source, approval_text="承認します")

  result = ApprovalModel(tmp_path).approve(source, approval_text="正式化を承認します")

  assert result["to_status"] == "approved"


def test_t006_superseded_transition_requires_reopen_five_step_fields(tmp_path):
  source = tmp_path / "learning" / "workflow" / "approved-updates" / "WP-004.yaml"
  _write_proposal(source, _base_proposal("WP-004", status="approved"))

  with pytest.raises(ApprovalError, match="missing_reopen_fields"):
    ApprovalModel(tmp_path).supersede(
      source,
      superseded_by="WP-005",
      superseded_at="2026-06-04T12:00:00+09:00",
      reopen_reason="後続提案で上書きする必要がある",
      approval_text="承認します",
      declaration=False,
      new_conclusion=True,
    )


def test_t006_superseded_transition_records_required_three_fields(tmp_path):
  source = tmp_path / "learning" / "workflow" / "approved-updates" / "WP-004.yaml"
  _write_proposal(source, _base_proposal("WP-004", status="approved"))

  result = ApprovalModel(tmp_path).supersede(
    source,
    superseded_by="WP-005",
    superseded_at="2026-06-04T12:00:00+09:00",
    reopen_reason="後続提案で上書きする必要がある",
    approval_text="承認します",
    declaration=True,
    new_conclusion=True,
  )

  proposal = _read_yaml(source)
  assert result["to_status"] == "superseded"
  assert result["target_path"] == "learning/workflow/approved-updates/WP-004.yaml"
  assert proposal["status"] == "superseded"
  assert proposal["superseded_by"] == "WP-005"
  assert proposal["superseded_at"] == "2026-06-04T12:00:00+09:00"
  assert proposal["reopen_reason"] == "後続提案で上書きする必要がある"


def test_t006_rejects_invalid_state_transition(tmp_path):
  source = tmp_path / "learning" / "workflow" / "rejected-updates" / "WP-006.yaml"
  _write_proposal(source, _base_proposal("WP-006", status="rejected"))

  with pytest.raises(ApprovalError, match="invalid_transition"):
    ApprovalModel(tmp_path).approve(source, approval_text="承認します")
