"""T-010 のテスト：陳腐化伝播履行器。"""
import json

from staleness.handler_selection_logic import HandlerSelectionLogic
from staleness.propagation_executor import PropagationExecutor
from staleness.staleness_register_writer import StalenessRegisterWriter


def test_handler_selection_flags_small_standard_impact():
  """標準比較セットへの少数影響は陳腐化フラグ付け。"""
  decision = HandlerSelectionLogic().select(
    invalidated_run_count=1,
    standard_run_count=100,
    exploratory_only=False,
  )
  assert decision.action == "flag_stale"


def test_handler_selection_rederives_large_standard_impact():
  """標準比較セットへの多数影響は再導出。"""
  decision = HandlerSelectionLogic().select(
    invalidated_run_count=10,
    standard_run_count=100,
    exploratory_only=False,
  )
  assert decision.action == "rederive"


def test_handler_selection_flags_exploratory_only():
  """exploratory 集計のみへの影響は陳腐化フラグ付け。"""
  decision = HandlerSelectionLogic().select(
    invalidated_run_count=50,
    standard_run_count=100,
    exploratory_only=True,
  )
  assert decision.action == "flag_stale"


def test_propagation_executor_marks_artifacts_stale():
  """陳腐化フラグ付けの対象成果物を決定的に返す。"""
  result = PropagationExecutor().execute(
    invalidated_run_ids=["run-001"],
    affected_artifact_ids=["treatment_comparisons"],
    action="flag_stale",
  )
  assert result["status"] == "stale_flagged"
  assert result["invalidated_run_ids"] == ["run-001"]


def test_staleness_register_writer_records_history(tmp_path):
  """staleness_register.json に履歴を記録する。"""
  entry = {
    "invalidated_run_ids": ["run-001"],
    "affected_artifact_ids": ["treatment_comparisons"],
    "action": "flag_stale",
    "recorded_at": "2026-06-03T13:00:00+09:00",
  }
  path = StalenessRegisterWriter().append(tmp_path / "experiments" / "analysis", entry)
  register = json.loads(path.read_text(encoding="utf-8"))
  assert register["entries"] == [entry]
