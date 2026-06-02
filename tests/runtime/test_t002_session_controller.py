"""T-002 のテスト：session controller（セッション制御器）。

対応タスク：runtime tasks.md T-002
対応設計節：design.md §全体構造（session controller 役）、§セッションモデル §1〜§3、
          §Reference-Free Runtime Entry Principle
対応要件：Requirement 1 受入 1〜3・5、Requirement 5、Requirement 6 受入 6、Requirement 7

テスト要件（tasks.md T-002 より）：
- セッション開始時の run_manifest.yaml 生成テスト
- run_status 不正遷移の拒否テスト（例：created → closed 直接遷移を拒否）
- Reference-Free 入口の境界テスト
"""
from pathlib import Path

import pytest
import yaml

from runtime_core.session_controller import (
  SessionController,
  InvalidStatusTransition,
  ReferenceFreeEntryViolation,
  START_FIXED_FIELDS,
  SESSION_INPUT_FIELDS,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
SESSION_INPUTS_SCHEMA = REPO_ROOT / "runtime/runtime_core/session_inputs_schema.yaml"

# design.md §2 セッション入力の 14 項目
EXPECTED_SESSION_INPUTS = {
  "target_id", "target_artifact_hash", "source_repository_id", "source_revision",
  "phase_profile", "treatment", "review_mode", "protocol_version", "runtime_version",
  "prompt_set_version", "schema_set_version", "config_version", "config_hash", "operator_id",
}

# tasks.md T-002 完了条件 1 の 16 項目（= 14 セッション入力 ＋ run_id ＋ started_at）
EXPECTED_16_FIELDS = {
  "run_id", "target_id", "target_artifact_hash", "source_repository_id",
  "source_revision", "phase_profile", "treatment", "review_mode",
  "protocol_version", "runtime_version", "prompt_set_version",
  "schema_set_version", "config_version", "config_hash", "operator_id",
  "started_at",
}


def _valid_inputs():
  """特定事例に依存しない汎用のセッション入力（14 項目）。"""
  return {
    "target_id": "doc-001",
    "target_artifact_hash": "sha256:abc",
    "source_repository_id": "repo-x",
    "source_revision": "rev-1",
    "phase_profile": "design",
    "treatment": "judgment",
    "review_mode": "runtime_mediated",
    "protocol_version": "p1",
    "runtime_version": "r1",
    "prompt_set_version": "ps1",
    "schema_set_version": "ss1",
    "config_version": "c1",
    "config_hash": "sha256:cfg",
    "operator_id": "operator-1",
  }


def _start(tmp_path, inputs=None, run_id="run-0001", started_at="2026-06-02T00:00:00+09:00"):
  controller = SessionController(run_root_base=tmp_path)
  return controller, controller.start_session(
    session_inputs=inputs if inputs is not None else _valid_inputs(),
    run_id=run_id,
    started_at=started_at,
  )


def test_session_inputs_schema_exists():
  """session_inputs_schema.yaml が存在する（成果物）。"""
  assert SESSION_INPUTS_SCHEMA.is_file(), f"存在しない：{SESSION_INPUTS_SCHEMA}"


def test_session_inputs_schema_declares_14_inputs():
  """session_inputs_schema.yaml が 14 セッション入力を宣言する（design.md §2）。"""
  spec = yaml.safe_load(SESSION_INPUTS_SCHEMA.read_text(encoding="utf-8"))
  declared = set(spec["required_inputs"])
  assert declared == EXPECTED_SESSION_INPUTS, (
    f"セッション入力の宣言が design.md §2 と一致しない：{declared}"
  )


def test_session_input_fields_match_schema():
  """コード側 SESSION_INPUT_FIELDS が 14 項目で schema と一致する。"""
  assert set(SESSION_INPUT_FIELDS) == EXPECTED_SESSION_INPUTS
  assert len(SESSION_INPUT_FIELDS) == 14


def test_start_fixed_fields_count_is_16():
  """開始時固定フィールドが 16 件（完了条件 1）。"""
  assert len(START_FIXED_FIELDS) == 16
  assert set(START_FIXED_FIELDS) == EXPECTED_16_FIELDS


def test_start_session_creates_manifest(tmp_path):
  """セッション開始時に run_manifest.yaml が生成される（テスト要件）。"""
  _, run_dir = _start(tmp_path)
  manifest_path = Path(run_dir) / "run_manifest.yaml"
  assert manifest_path.is_file(), "run_manifest.yaml が生成されていない"


def test_manifest_contains_16_fields(tmp_path):
  """run_manifest.yaml に 16 項目すべてが書き込まれる（完了条件 1）。"""
  _, run_dir = _start(tmp_path)
  manifest = yaml.safe_load((Path(run_dir) / "run_manifest.yaml").read_text(encoding="utf-8"))
  for field in EXPECTED_16_FIELDS:
    assert field in manifest, f"run_manifest.yaml に {field} が欠落"


def test_manifest_initial_run_status_is_created(tmp_path):
  """開始時の run_status は created（design.md §1 ライフサイクル）。"""
  _, run_dir = _start(tmp_path)
  manifest = yaml.safe_load((Path(run_dir) / "run_manifest.yaml").read_text(encoding="utf-8"))
  assert manifest["run_status"] == "created"


def test_manifest_values_are_not_overwritten_with_defaults(tmp_path):
  """書き込まれた値が入力どおりで、暗黙既定値で上書きされない（完了条件 3）。"""
  inputs = _valid_inputs()
  _, run_dir = _start(tmp_path, inputs=inputs)
  manifest = yaml.safe_load((Path(run_dir) / "run_manifest.yaml").read_text(encoding="utf-8"))
  for field, value in inputs.items():
    assert manifest[field] == value, f"{field} が入力値と異なる：{manifest[field]}"


def test_transition_created_to_in_progress(tmp_path):
  """created → in_progress は許可される。"""
  controller, run_dir = _start(tmp_path)
  controller.transition_status(run_dir, "in_progress")
  manifest = yaml.safe_load((Path(run_dir) / "run_manifest.yaml").read_text(encoding="utf-8"))
  assert manifest["run_status"] == "in_progress"


def test_transition_in_progress_to_closed(tmp_path):
  """in_progress → closed は許可される。"""
  controller, run_dir = _start(tmp_path)
  controller.transition_status(run_dir, "in_progress")
  controller.transition_status(run_dir, "closed")
  manifest = yaml.safe_load((Path(run_dir) / "run_manifest.yaml").read_text(encoding="utf-8"))
  assert manifest["run_status"] == "closed"


def test_transition_created_to_closed_rejected(tmp_path):
  """created → closed 直接遷移は拒否される（完了条件 2、テスト要件）。"""
  controller, run_dir = _start(tmp_path)
  with pytest.raises(InvalidStatusTransition):
    controller.transition_status(run_dir, "closed")


def test_transition_closed_is_terminal(tmp_path):
  """closed からの遷移は拒否される（1 方向性、完了条件 2）。"""
  controller, run_dir = _start(tmp_path)
  controller.transition_status(run_dir, "in_progress")
  controller.transition_status(run_dir, "closed")
  with pytest.raises(InvalidStatusTransition):
    controller.transition_status(run_dir, "in_progress")


def test_transition_to_orchestration_failed_allowed(tmp_path):
  """in_progress → orchestration_failed は許可される（実行制御の失敗）。"""
  controller, run_dir = _start(tmp_path)
  controller.transition_status(run_dir, "in_progress")
  controller.transition_status(run_dir, "orchestration_failed")
  manifest = yaml.safe_load((Path(run_dir) / "run_manifest.yaml").read_text(encoding="utf-8"))
  assert manifest["run_status"] == "orchestration_failed"


def test_reference_free_rejects_missing_input(tmp_path):
  """必須セッション入力の欠落を暗黙既定値で補わず拒否する（完了条件 3）。"""
  inputs = _valid_inputs()
  del inputs["target_id"]
  controller = SessionController(run_root_base=tmp_path)
  with pytest.raises(ReferenceFreeEntryViolation):
    controller.start_session(session_inputs=inputs, run_id="run-x", started_at="2026-06-02T00:00:00+09:00")


def test_reference_free_rejects_empty_input(tmp_path):
  """必須セッション入力が空値の場合も拒否する（完了条件 3）。"""
  inputs = _valid_inputs()
  inputs["source_repository_id"] = ""
  controller = SessionController(run_root_base=tmp_path)
  with pytest.raises(ReferenceFreeEntryViolation):
    controller.start_session(session_inputs=inputs, run_id="run-x", started_at="2026-06-02T00:00:00+09:00")


# ---- triad-review 機能内対処（2026-06-02、A-001）----

def test_start_session_creates_required_subdirectories(tmp_path):
  """セッション開始時に必須サブディレクトリを作成する（A-001、tasks T-001／T-002）。"""
  _, run_dir = _start(tmp_path)
  run_dir = Path(run_dir)
  for sub in ("steps", "decisions", "failures/failure_observations", "validation", "derived"):
    assert (run_dir / sub).is_dir(), f"必須サブディレクトリが未作成：{sub}"
