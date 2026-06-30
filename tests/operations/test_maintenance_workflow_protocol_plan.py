from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
PLAN_PATH = (
  ROOT
  / ".reviewcompass"
  / "backlog"
  / "plans"
  / "plan-2026-06-23-maintenance-workflow-protocol.yaml"
)
INDEX_PATH = ROOT / ".reviewcompass" / "backlog" / "index.yaml"


def _remaining_work_by_id():
  data = yaml.safe_load(PLAN_PATH.read_text(encoding="utf-8"))
  return {item["id"]: item for item in data["remaining_work"]}


def _index_item_by_id():
  data = yaml.safe_load(INDEX_PATH.read_text(encoding="utf-8"))
  return {item["id"]: item for item in data["items"]}


def test_mwp0_through_mwp3_are_marked_completed_with_evidence():
  remaining_work = _remaining_work_by_id()

  for item_id in ("MWP-0", "MWP-1", "MWP-2", "MWP-3"):
    item = remaining_work[item_id]
    assert item["status"] == "completed"
    assert item["completed_at"] == "2026-06-30"
    assert item["completion_evidence"]

  assert "d69c82e5" in remaining_work["MWP-0"]["completion_evidence"]
  assert "da8730c5" in remaining_work["MWP-1"]["completion_evidence"]
  assert "73f88db8" in remaining_work["MWP-2"]["completion_evidence"]
  assert "8fe89efc" in remaining_work["MWP-2"]["completion_evidence"]
  assert "6eebe013" in remaining_work["MWP-3"]["completion_evidence"]
  assert "d583949b" in remaining_work["MWP-3"]["completion_evidence"]
  assert "0b0fbd5d" in remaining_work["MWP-3"]["completion_evidence"]


def test_maintenance_workflow_protocol_plan_and_index_are_completed():
  plan = yaml.safe_load(PLAN_PATH.read_text(encoding="utf-8"))
  index_item = _index_item_by_id()["plan-2026-06-23-maintenance-workflow-protocol"]

  assert plan["status"] == "completed"
  assert index_item["status"] == "completed"
