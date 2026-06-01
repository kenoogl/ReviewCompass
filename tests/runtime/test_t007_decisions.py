"""T-007 のテスト：決定単位と人間署名記録。

対応タスク：runtime tasks.md T-007
対応設計節：design.md §決定単位モデル、§人間署名記録
対応要件：Requirement 5（人間決定の組み込み）、Requirement 6 受入 9

テスト要件（tasks.md T-007 より）：
- 人間決定付加テスト（決定単位生成は T-005 側に集約）
- 人間署名 4 値の整合テスト
- 不在と保留の区別テスト
"""
import json
from pathlib import Path

import pytest
import yaml

from runtime_core.decisions.decision_unit_updater import DecisionUnitUpdater, InvalidHumanDecision
from runtime_core.decisions.human_signoff_writer import HumanSignoffWriter, InvalidSignoffStatus

REPO_ROOT = Path(__file__).resolve().parents[2]
METADATA_CONTRACT = REPO_ROOT / "runtime/foundation/metadata_contract.yaml"

FOUNDATION_SIGNOFF_4 = set(
  yaml.safe_load(METADATA_CONTRACT.read_text(encoding="utf-8"))["vocabularies"]["human_signoff_status"]
)


def _run_dir_with_units(tmp_path):
  run_dir = tmp_path / "experiments" / "runs" / "run-1"
  (run_dir / "decisions").mkdir(parents=True)
  units = {
    "decision_units": [
      {"decision_unit_id": "du-001", "finding_refs": ["step_a-f0"], "judgment_refs": ["judgment-0"],
       "proposed_action": "fix_required", "human_decision": None,
       "human_decision_timestamp": None, "human_decision_note": ""},
      {"decision_unit_id": "du-002", "finding_refs": ["step_a-f1"], "judgment_refs": [],
       "proposed_action": "human_review_required", "human_decision": None,
       "human_decision_timestamp": None, "human_decision_note": ""},
    ]
  }
  (run_dir / "decisions" / "decision_units.json").write_text(
    json.dumps(units, ensure_ascii=False, indent=2), encoding="utf-8"
  )
  return run_dir


def _load_units(run_dir):
  return json.loads((Path(run_dir) / "decisions" / "decision_units.json").read_text(encoding="utf-8"))


def test_foundation_signoff_has_4_values():
  """前提：foundation human_signoff_status が 4 値（pending/approved/rejected/deferred）。"""
  assert FOUNDATION_SIGNOFF_4 == {"pending", "approved", "rejected", "deferred"}


def test_apply_human_decision(tmp_path):
  """T-005 生成の決定単位に人間決定を付加する（完了条件 1）。"""
  run_dir = _run_dir_with_units(tmp_path)
  updater = DecisionUnitUpdater(run_dir)
  updater.apply_decision("du-001", human_decision="approved", timestamp="2026-06-02T10:00", note="承認")
  units = _load_units(run_dir)
  du1 = next(u for u in units["decision_units"] if u["decision_unit_id"] == "du-001")
  assert du1["human_decision"] == "approved"
  assert du1["human_decision_timestamp"] == "2026-06-02T10:00"
  assert du1["human_decision_note"] == "承認"


def test_apply_decision_unknown_unit_fails(tmp_path):
  """存在しない決定単位 ID は失敗する。"""
  run_dir = _run_dir_with_units(tmp_path)
  updater = DecisionUnitUpdater(run_dir)
  with pytest.raises(KeyError):
    updater.apply_decision("du-999", human_decision="approved", timestamp="t")


def test_invalid_human_decision_rejected(tmp_path):
  """foundation 4 値に基づかない人間決定値を拒否する（再定義禁止）。"""
  run_dir = _run_dir_with_units(tmp_path)
  updater = DecisionUnitUpdater(run_dir)
  with pytest.raises(InvalidHumanDecision):
    updater.apply_decision("du-001", human_decision="maybe", timestamp="t")


def test_absent_vs_explicit_deferral_distinguishable(tmp_path):
  """不在（None）と明示保留（deferred）／却下（rejected）を機械区別できる（完了条件 3）。"""
  run_dir = _run_dir_with_units(tmp_path)
  updater = DecisionUnitUpdater(run_dir)
  updater.apply_decision("du-001", human_decision="deferred", timestamp="t", note="保留")
  units = _load_units(run_dir)
  du1 = next(u for u in units["decision_units"] if u["decision_unit_id"] == "du-001")
  du2 = next(u for u in units["decision_units"] if u["decision_unit_id"] == "du-002")
  assert du1["human_decision"] == "deferred"   # 明示保留
  assert du2["human_decision"] is None          # 不在
  assert du1["human_decision"] != du2["human_decision"]


def test_explicit_decision_values_reference_foundation(tmp_path):
  """明示決定値は foundation 4 値（pending を除く 3 値）を参照する。"""
  run_dir = _run_dir_with_units(tmp_path)
  updater = DecisionUnitUpdater(run_dir)
  for decision in ("approved", "rejected", "deferred"):
    updater.apply_decision("du-001", human_decision=decision, timestamp="t")
    units = _load_units(run_dir)
    du1 = next(u for u in units["decision_units"] if u["decision_unit_id"] == "du-001")
    assert du1["human_decision"] == decision


def test_human_signoff_writer_writes_record(tmp_path):
  """human_signoff.json を 6 項目で出力する（design.md §人間署名記録）。"""
  run_dir = tmp_path / "experiments" / "runs" / "run-1"
  (run_dir / "decisions").mkdir(parents=True)
  writer = HumanSignoffWriter()
  writer.write(
    run_dir, run_id="run-1", human_signoff_status="approved",
    signed_off_by="operator-1", signed_off_at="2026-06-02T10:00",
    covered_decision_unit_ids=["du-001", "du-002"], signoff_note="全件確認",
  )
  data = json.loads((run_dir / "decisions" / "human_signoff.json").read_text(encoding="utf-8"))
  for key in ("run_id", "human_signoff_status", "signed_off_by", "signed_off_at",
              "covered_decision_unit_ids", "signoff_note"):
    assert key in data, f"human_signoff.json に {key} が欠落"
  assert data["human_signoff_status"] == "approved"


def test_human_signoff_accepts_all_4_foundation_values(tmp_path):
  """human_signoff_status は foundation 4 値すべてを受理する（整合テスト）。"""
  writer = HumanSignoffWriter()
  for status in FOUNDATION_SIGNOFF_4:
    run_dir = tmp_path / status
    (run_dir / "decisions").mkdir(parents=True)
    writer.write(
      run_dir, run_id="r", human_signoff_status=status,
      signed_off_by="op", signed_off_at="t", covered_decision_unit_ids=[],
    )
    data = json.loads((run_dir / "decisions" / "human_signoff.json").read_text(encoding="utf-8"))
    assert data["human_signoff_status"] == status


def test_human_signoff_rejects_invalid_status(tmp_path):
  """foundation 4 値外の signoff 状態を拒否する（再定義禁止）。"""
  run_dir = tmp_path / "experiments" / "runs" / "run-1"
  (run_dir / "decisions").mkdir(parents=True)
  writer = HumanSignoffWriter()
  with pytest.raises(InvalidSignoffStatus):
    writer.write(
      run_dir, run_id="r", human_signoff_status="signed",  # 無効
      signed_off_by="op", signed_off_at="t", covered_decision_unit_ids=[],
    )
