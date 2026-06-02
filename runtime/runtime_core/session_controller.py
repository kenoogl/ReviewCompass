"""session controller（セッション制御器）（runtime tasks.md T-002）。

実行開始時のセッション入力固定、run_manifest.yaml 生成、run_status 4 値の遷移制御を担う。
実行入口を明示入力群に限定し、特定事例の暗黙既定値を排除する
（Reference-Free Runtime Entry Principle）。

対応設計節：design.md §全体構造（session controller 役）、§セッションモデル §1〜§3、
          §Reference-Free Runtime Entry Principle
対応要件：Requirement 1 受入 1〜3・5、Requirement 5（決定単位提示の起点）、
          Requirement 6 受入 6（review_mode 付与の起点）、Requirement 7（再生対応の実行時記録）
"""
from pathlib import Path

import yaml

# design.md §2 セッション入力の 14 項目（value 語彙の所有は別途：
# phase_profile／treatment は runtime 所有、review_mode は foundation 正本参照）。
SESSION_INPUT_FIELDS = [
  "target_id",
  "target_artifact_hash",
  "source_repository_id",
  "source_revision",
  "phase_profile",
  "treatment",
  "review_mode",
  "protocol_version",
  "runtime_version",
  "prompt_set_version",
  "schema_set_version",
  "config_version",
  "config_hash",
  "operator_id",
]

# controller が開始時に固定する 2 項目。
CONTROLLER_FIXED_FIELDS = ["run_id", "started_at"]

# 開始時固定フィールド 16 件（tasks.md T-002 完了条件 1）。
START_FIXED_FIELDS = SESSION_INPUT_FIELDS + CONTROLLER_FIXED_FIELDS

# run_status の許可遷移（design.md §セッションモデル §1、foundation run_status 4 値正本）。
# created → in_progress → closed（または orchestration_failed）の 1 方向に制限する。
VALID_TRANSITIONS = {
  "created": {"in_progress", "orchestration_failed"},
  "in_progress": {"closed", "orchestration_failed"},
  "closed": set(),
  "orchestration_failed": set(),
}


class InvalidStatusTransition(Exception):
  """run_status の不正遷移（1 方向性の違反）。"""


class ReferenceFreeEntryViolation(Exception):
  """必須セッション入力の欠落を暗黙既定値で補わずに検出した違反。"""


class SessionController:
  """1 実行のライフサイクルを制御するセッション制御器。"""

  def __init__(self, run_root_base):
    # run_root_base/experiments/runs/<run_id>/ を実行ディレクトリとする。
    self.run_root_base = Path(run_root_base)

  def start_session(self, session_inputs, run_id, started_at):
    """セッション入力を固定し run_manifest.yaml を生成する。

    Reference-Free：必須セッション入力が明示提供されることを要求し、
    欠落・空値を暗黙既定値で補わない。特定事例名の既定値はコードに持たない。
    """
    missing = [
      field
      for field in SESSION_INPUT_FIELDS
      if field not in session_inputs or session_inputs[field] in (None, "")
    ]
    if missing:
      raise ReferenceFreeEntryViolation(
        f"必須セッション入力が欠落（暗黙既定値で補わない）：{missing}"
      )

    manifest = {field: session_inputs[field] for field in SESSION_INPUT_FIELDS}
    manifest["run_id"] = run_id
    manifest["started_at"] = started_at
    manifest["run_status"] = "created"

    run_dir = self.run_root_base / "experiments" / "runs" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    # 必須サブディレクトリを開始時に作成する（A-001、tasks T-001／T-002、layout_spec 準拠）。
    # design.md §実行成果物配置の 5 サブディレクトリ（＋ルート）を session controller が確立する。
    for sub in ("steps", "decisions", "failures/failure_observations", "validation", "derived"):
      (run_dir / sub).mkdir(parents=True, exist_ok=True)
    self._write_manifest(run_dir, manifest)
    return run_dir

  def transition_status(self, run_dir, new_status):
    """run_status を 1 方向の許可遷移に限って更新する。"""
    run_dir = Path(run_dir)
    manifest = self._read_manifest(run_dir)
    current = manifest.get("run_status")
    if new_status not in VALID_TRANSITIONS.get(current, set()):
      raise InvalidStatusTransition(
        f"不正な run_status 遷移：{current} → {new_status}"
      )
    manifest["run_status"] = new_status
    self._write_manifest(run_dir, manifest)
    return new_status

  @staticmethod
  def _manifest_path(run_dir):
    return Path(run_dir) / "run_manifest.yaml"

  def _read_manifest(self, run_dir):
    with self._manifest_path(run_dir).open(encoding="utf-8") as f:
      return yaml.safe_load(f)

  def _write_manifest(self, run_dir, manifest):
    with self._manifest_path(run_dir).open("w", encoding="utf-8") as f:
      yaml.safe_dump(manifest, f, allow_unicode=True, sort_keys=False)
