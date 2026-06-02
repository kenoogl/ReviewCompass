"""T-009 のテスト：validation bridge（検証器連携と実行終了境界）。

対応タスク：runtime tasks.md T-009
対応設計節：design.md §検証器連携 §実行終了境界、§無効化処理、§セッションモデル §3
対応要件：Requirement 6（検証器連携と実行終了、受入 1〜5・7〜9）

テスト要件（tasks.md T-009 より）：
- 順序強制テスト（前提違反の拒否）
- validator_status 4 値の伝播テスト
- evidence_class 確定遷移の網羅性テスト（9 行マッピング全件）
- fail-closed 動作テスト
"""
import itertools
import json
from pathlib import Path

import pytest
import yaml

from runtime_core.validation_bridge.evidence_class_transitioner import EvidenceClassTransitioner
from runtime_core.validation_bridge.bridge import ValidationBridge, RunCloseOrderError
from runtime_core.validation_bridge.invalidation_marker_writer import InvalidationMarkerWriter

REPO_ROOT = Path(__file__).resolve().parents[2]
METADATA_CONTRACT = REPO_ROOT / "runtime/foundation/metadata_contract.yaml"
_VOCAB = yaml.safe_load(METADATA_CONTRACT.read_text(encoding="utf-8"))["vocabularies"]
VALIDATOR_STATUS_4 = set(_VOCAB["validator_status"])
SIGNOFF_4 = set(_VOCAB["human_signoff_status"])
EVIDENCE_CLASS_4 = set(_VOCAB["evidence_class"])

# design.md §セッションモデル §3 の 9 行マッピング表（代表 9 ケース）。
# (validator_status, signoff, exploratory, has_marker) -> evidence_class
NINE_ROWS = [
  ("passed", "approved", True, False, "exploratory"),   # 探索宣言が最優先
  ("passed", "approved", False, True, "invalid"),        # 無効化標識
  ("passed", "approved", False, False, "valid"),
  ("passed", "rejected", False, False, "invalid"),
  ("passed", "deferred", False, False, "analysis_blocked"),
  ("passed", "pending", False, False, "analysis_blocked"),
  ("failed", "approved", False, False, "invalid"),
  ("blocked", "approved", False, False, "analysis_blocked"),
  ("not_run", "approved", False, False, "analysis_blocked"),
]


# ---- evidence_class_transitioner ----

@pytest.mark.parametrize("validator_status,signoff,exploratory,marker,expected", NINE_ROWS)
def test_transitioner_nine_rows(validator_status, signoff, exploratory, marker, expected):
  """9 行マッピング表の各行が期待 evidence_class を返す（完了条件 3）。"""
  t = EvidenceClassTransitioner()
  assert t.transition(
    validator_status=validator_status, human_signoff_status=signoff,
    exploratory_declared=exploratory, has_invalidation_marker=marker,
  ) == expected


def test_transitioner_covers_all_combinations():
  """全組み合わせ（4×4×2×2＝64）が evidence_class 4 値のいずれかに必ず確定する。"""
  t = EvidenceClassTransitioner()
  for vs, so, ex, mk in itertools.product(VALIDATOR_STATUS_4, SIGNOFF_4, [True, False], [True, False]):
    result = t.transition(
      validator_status=vs, human_signoff_status=so,
      exploratory_declared=ex, has_invalidation_marker=mk,
    )
    assert result in EVIDENCE_CLASS_4, f"未確定の組み合わせ：{(vs, so, ex, mk)} -> {result}"


# ---- ValidationBridge ----

def _setup_run(tmp_path, *, with_signoff=True, signoff_status="approved", run_status="in_progress"):
  run_dir = tmp_path / "experiments" / "runs" / "run-1"
  (run_dir / "steps").mkdir(parents=True)
  (run_dir / "decisions").mkdir(parents=True)
  (run_dir / "run_manifest.yaml").write_text(
    yaml.safe_dump({"run_id": "run-1", "target_id": "doc-001", "run_status": run_status},
                   allow_unicode=True), encoding="utf-8")
  (run_dir / "steps" / "step_d_integration.json").write_text(json.dumps({
    "step_id": "step_d", "step_name": "integration", "step_outcome": "executed",
    "run_close_ready": True, "integration_summary": "統合",
  }), encoding="utf-8")
  if with_signoff:
    (run_dir / "decisions" / "human_signoff.json").write_text(json.dumps({
      "run_id": "run-1", "human_signoff_status": signoff_status,
      "signed_off_by": "op", "signed_off_at": "t", "covered_decision_unit_ids": [],
    }), encoding="utf-8")
  return run_dir


class _CountingValidator:
  """呼び出し回数を数える検証器。fail-closed 検証用。"""

  def __init__(self, status="passed"):
    self.calls = 0
    self.status = status

  def __call__(self, run_dir):
    self.calls += 1
    return {
      "run_id": "run-1", "validator_status": self.status, "checked_contract": "review_case",
      "error_list": [], "validated_by": "validator", "validated_at": "t",
    }


def _manifest(run_dir):
  return yaml.safe_load((Path(run_dir) / "run_manifest.yaml").read_text(encoding="utf-8"))


def test_close_run_success_valid(tmp_path):
  """正常系：検証合格＋人間承認で evidence_class=valid、run_status=closed。"""
  run_dir = _setup_run(tmp_path, signoff_status="approved")
  validator = _CountingValidator("passed")
  bridge = ValidationBridge(run_dir, validator_callable=validator)
  result = bridge.close_run()
  assert result["evidence_class"] == "valid"
  m = _manifest(run_dir)
  assert m["run_status"] == "closed"
  assert (run_dir / "validation" / "validator_result.json").is_file()


def test_validator_status_propagated(tmp_path):
  """validator_status 4 値が run_manifest にそのまま伝播される（再定義禁止、完了条件 2）。"""
  for status in VALIDATOR_STATUS_4:
    run_dir = _setup_run(tmp_path / status, signoff_status="approved")
    bridge = ValidationBridge(run_dir, validator_callable=_CountingValidator(status))
    bridge.close_run()
    assert _manifest(run_dir)["validator_status"] == status


def test_order_violation_missing_signoff_rejected(tmp_path):
  """人間署名が無い実行終了は順序違反として拒否される（完了条件 1）。"""
  run_dir = _setup_run(tmp_path, with_signoff=False)
  validator = _CountingValidator("passed")
  bridge = ValidationBridge(run_dir, validator_callable=validator)
  with pytest.raises(RunCloseOrderError):
    bridge.close_run()


def test_fail_closed_does_not_call_validator(tmp_path):
  """順序違反時は検証器を起動せず fail-closed（orchestration_failed、完了条件 1・テスト要件）。"""
  run_dir = _setup_run(tmp_path, with_signoff=False)
  validator = _CountingValidator("passed")
  bridge = ValidationBridge(run_dir, validator_callable=validator)
  with pytest.raises(RunCloseOrderError):
    bridge.close_run()
  assert validator.calls == 0, "順序違反なのに検証器が起動された"
  m = _manifest(run_dir)
  assert m["run_status"] == "orchestration_failed"
  # 無効化標識が付与される
  assert (run_dir / "validation" / "invalidation_markers.json").is_file()


def test_fail_closed_generates_triage_note(tmp_path):
  """無効実行時に derived/invalid_run_triage_note.json を生成する（design.md §無効化処理）。"""
  run_dir = _setup_run(tmp_path, with_signoff=False)
  bridge = ValidationBridge(run_dir, validator_callable=_CountingValidator("passed"))
  with pytest.raises(RunCloseOrderError):
    bridge.close_run()
  triage = run_dir / "derived" / "invalid_run_triage_note.json"
  assert triage.is_file()
  data = json.loads(triage.read_text(encoding="utf-8"))
  for key in ("primary_failure_code", "failed_validator_check_ids",
              "invalidation_marker_linkage", "operator_action_hint"):
    assert key in data, f"triage note に {key} が欠落"


def test_multiple_invocation_rejected(tmp_path):
  """既に終了した実行への二重起動を拒否する（完了条件 1）。"""
  run_dir = _setup_run(tmp_path, run_status="closed")
  bridge = ValidationBridge(run_dir, validator_callable=_CountingValidator("passed"))
  with pytest.raises(RunCloseOrderError):
    bridge.close_run()


def test_rejected_signoff_yields_invalid(tmp_path):
  """検証合格でも人間却下なら evidence_class=invalid（9 行マッピング）。"""
  run_dir = _setup_run(tmp_path, signoff_status="rejected")
  bridge = ValidationBridge(run_dir, validator_callable=_CountingValidator("passed"))
  result = bridge.close_run()
  assert result["evidence_class"] == "invalid"


def test_invalidation_marker_writer_appends(tmp_path):
  """無効化標識を生証拠を改変せず追加する（要件 6 受入 3）。"""
  run_dir = tmp_path / "experiments" / "runs" / "run-1"
  (run_dir / "validation").mkdir(parents=True)
  writer = InvalidationMarkerWriter()
  writer.add_marker(run_dir, {
    "run_id": "run-1", "reason_code": "run_close_without_signoff",
    "reason_detail": "署名なし終了", "scope": "run", "issued_by": "validator", "issued_at": "t",
  })
  data = json.loads((run_dir / "validation" / "invalidation_markers.json").read_text(encoding="utf-8"))
  assert len(data["markers"]) == 1
  assert data["markers"][0]["scope"] == "run"


# ---- triad-review 機能内対処（2026-06-02、論点A）----

def test_close_run_updates_review_case(tmp_path):
  """A-006：実行終了で review_case.json に終了メタデータを確定反映する。"""
  run_dir = _setup_run(tmp_path, signoff_status="approved")
  bridge = ValidationBridge(run_dir, validator_callable=_CountingValidator("passed"))
  bridge.close_run()
  rc_path = run_dir / "review_case.json"
  assert rc_path.is_file(), "review_case.json が更新されていない"
  rc = json.loads(rc_path.read_text(encoding="utf-8"))
  assert rc["run_status"] == "closed"
  assert rc["validator_status"] == "passed"
  assert rc["evidence_class"] == "valid"


def test_close_run_rejects_when_not_ready(tmp_path):
  """P-002：Step D の run_close_ready が False なら実行終了を拒否する。"""
  run_dir = _setup_run(tmp_path, signoff_status="approved")
  step_d_path = run_dir / "steps" / "step_d_integration.json"
  data = json.loads(step_d_path.read_text(encoding="utf-8"))
  data["run_close_ready"] = False
  step_d_path.write_text(json.dumps(data), encoding="utf-8")
  bridge = ValidationBridge(run_dir, validator_callable=_CountingValidator("passed"))
  with pytest.raises(RunCloseOrderError):
    bridge.close_run()


def test_fail_closed_sets_evidence_class_invalid(tmp_path):
  """P-010：fail-closed 経路でも evidence_class を invalid に確定する。"""
  run_dir = _setup_run(tmp_path, with_signoff=False)
  bridge = ValidationBridge(run_dir, validator_callable=_CountingValidator("passed"))
  with pytest.raises(RunCloseOrderError):
    bridge.close_run()
  assert _manifest(run_dir)["evidence_class"] == "invalid"


def test_invalid_validator_status_fails_closed(tmp_path):
  """A-002：検証器が 4 値外を返したら fail-closed（中間状態を残さない）。"""
  run_dir = _setup_run(tmp_path, signoff_status="approved")
  bridge = ValidationBridge(run_dir, validator_callable=_CountingValidator("bogus"))
  with pytest.raises(RunCloseOrderError):
    bridge.close_run()
  m = _manifest(run_dir)
  assert m["run_status"] == "orchestration_failed"
  assert (run_dir / "validation" / "invalidation_markers.json").is_file()


def test_validator_failure_generates_triage(tmp_path):
  """A-003：検証器 failed のとき invalid 確定＋トリアージ記録を生成する。"""
  run_dir = _setup_run(tmp_path, signoff_status="approved")
  bridge = ValidationBridge(run_dir, validator_callable=_CountingValidator("failed"))
  result = bridge.close_run()
  assert result["evidence_class"] == "invalid"
  assert (run_dir / "derived" / "invalid_run_triage_note.json").is_file()
