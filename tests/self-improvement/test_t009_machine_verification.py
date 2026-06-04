"""T-009 のテスト：機械検査の具体手段。

対応タスク：self-improvement tasks.md T-009
対応設計節：design.md §17.1〜§17.4
対応要件：Requirement 1 受入 4
"""
import json
import subprocess
import sys
from pathlib import Path

import yaml

from tools.self_improvement.machine_verification import (
  MachineVerification,
  VerificationStatus,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "tools" / "self-improvement-check.py"


def _write_yaml(path, data):
  path.parent.mkdir(parents=True, exist_ok=True)
  path.write_text(
    yaml.safe_dump(data, allow_unicode=True, sort_keys=False),
    encoding="utf-8",
  )


def _proposal(**overrides):
  data = {
    "proposal_id": "WP-001",
    "proposal_type": "update",
    "target_discipline_path": "docs/disciplines/discipline_update.md",
    "motivating_evidence": [
      {
        "source": "review_record",
        "location": "reviews/2026-06-04.yaml",
        "observation": "機械検査のために十分な長さを持つ観察記録",
      }
    ],
    "proposed_change": {"change_diff": "- old\n+ new"},
    "expected_effect": "規律更新の効果",
    "status": "approved",
    "materialization_commit_hash": None,
  }
  data.update(overrides)
  return data


def test_t009_mv1_detects_direct_discipline_write_fail_closed():
  result = MachineVerification().check_direct_discipline_writes(
    changed_files=[
      "docs/disciplines/discipline_update.md",
      "learning/workflow/proposals/WP-001.yaml",
    ],
    actor_feature="self-improvement",
  )

  assert result.status == VerificationStatus.DEVIATION
  assert result.check_id == "MV-1"
  assert "docs/disciplines/discipline_update.md" in result.reasons[0]


def test_t009_mv1_allows_non_discipline_files():
  result = MachineVerification().check_direct_discipline_writes(
    changed_files=["learning/workflow/proposals/WP-001.yaml"],
    actor_feature="self-improvement",
  )

  assert result.status == VerificationStatus.OK


def test_t009_mv2_detects_missing_required_proposal_field(tmp_path):
  proposal_path = tmp_path / "learning" / "workflow" / "approved-updates" / "WP-001.yaml"
  proposal = _proposal()
  del proposal["expected_effect"]
  _write_yaml(proposal_path, proposal)

  result = MachineVerification(tmp_path).check_proposal_required_fields([proposal_path])

  assert result.status == VerificationStatus.DEVIATION
  assert result.check_id == "MV-2"
  assert "missing_required_fields" in result.reasons[0]


def test_t009_mv3_skips_null_materialization_commit_hash(tmp_path):
  proposal_path = tmp_path / "learning" / "workflow" / "approved-updates" / "WP-001.yaml"
  _write_yaml(proposal_path, _proposal(materialization_commit_hash=None))

  result = MachineVerification(tmp_path).check_materialization_commit_hashes(
    [proposal_path],
    commit_exists=lambda commit: False,
  )

  assert result.status == VerificationStatus.OK
  assert result.details["skipped_null_count"] == 1


def test_t009_mv3_detects_missing_non_null_commit_hash(tmp_path):
  proposal_path = tmp_path / "learning" / "workflow" / "approved-updates" / "WP-001.yaml"
  _write_yaml(proposal_path, _proposal(materialization_commit_hash="deadbeef"))

  result = MachineVerification(tmp_path).check_materialization_commit_hashes(
    [proposal_path],
    commit_exists=lambda commit: False,
  )

  assert result.status == VerificationStatus.DEVIATION
  assert "deadbeef" in result.reasons[0]


def test_t009_mv4_requires_superseded_three_fields(tmp_path):
  proposal_path = tmp_path / "learning" / "workflow" / "approved-updates" / "WP-001.yaml"
  _write_yaml(proposal_path, _proposal(status="superseded", superseded_by="WP-002"))

  result = MachineVerification(tmp_path).check_superseded_fields([proposal_path])

  assert result.status == VerificationStatus.DEVIATION
  assert result.check_id == "MV-4"
  assert "superseded_at" in result.reasons[0]
  assert "reopen_reason" in result.reasons[0]


def test_t009_fail_closed_summary_and_metrics_append(tmp_path):
  proposal_path = tmp_path / "learning" / "workflow" / "approved-updates" / "WP-001.yaml"
  proposal = _proposal()
  del proposal["expected_effect"]
  _write_yaml(proposal_path, proposal)

  summary = MachineVerification(tmp_path).run_all(
    changed_files=["learning/workflow/approved-updates/WP-001.yaml"],
    actor_feature="self-improvement",
    proposal_paths=[proposal_path],
    metric_date="2026-06-04",
    commit_exists=lambda commit: True,
  )

  metrics = yaml.safe_load(
    (tmp_path / "learning" / "workflow" / "metrics" / "2026-06-04-machine-verification.yaml")
    .read_text(encoding="utf-8")
  )
  assert summary["verdict"] == "DEVIATION"
  assert metrics["verdict"] == "DEVIATION"
  assert metrics["checks"][1]["check_id"] == "MV-2"


def test_t009_cli_returns_json_and_exit_two_for_deviation(tmp_path):
  result = subprocess.run(
    [
      sys.executable,
      str(SCRIPT),
      "mv1",
      "--actor-feature",
      "self-improvement",
      "--changed-file",
      "docs/disciplines/discipline_update.md",
      "--json",
    ],
    cwd=tmp_path,
    capture_output=True,
    text=True,
    timeout=10,
  )

  assert result.returncode == 2
  data = json.loads(result.stdout)
  assert data["verdict"] == "DEVIATION"
  assert data["checks"][0]["check_id"] == "MV-1"


def test_t009_responsibility_document_exists():
  doc = REPO_ROOT / "docs" / "operations" / "SELF_IMPROVEMENT_MACHINE_VERIFICATION.md"

  text = doc.read_text(encoding="utf-8")
  assert "MV-1" in text
  assert "MV-2" in text
  assert "MV-3" in text
  assert "MV-4" in text
  assert "check-workflow-action.py" in text
  assert "self-improvement-check.py" in text
