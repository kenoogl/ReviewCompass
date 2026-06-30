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


def _remaining_work_by_id():
  data = yaml.safe_load(PLAN_PATH.read_text(encoding="utf-8"))
  return {item["id"]: item for item in data["remaining_work"]}


def test_mwp0_and_mwp1_are_marked_completed_with_evidence():
  remaining_work = _remaining_work_by_id()

  for item_id in ("MWP-0", "MWP-1"):
    item = remaining_work[item_id]
    assert item["status"] == "completed"
    assert item["completed_at"] == "2026-06-30"
    assert item["completion_evidence"]

  assert "d69c82e5" in remaining_work["MWP-0"]["completion_evidence"]
  assert "da8730c5" in remaining_work["MWP-1"]["completion_evidence"]
