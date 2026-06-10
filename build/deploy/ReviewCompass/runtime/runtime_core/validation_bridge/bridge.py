"""validation bridge（検証橋）（runtime tasks.md T-009）。

実行終了境界の順序（Step D 完了 → 人間署名 → 凍結 → 検証器呼び出し → validator_result 保存）を
強制する。前提条件違反や多重起動を検知した場合、検証器を起動せず run_status=orchestration_failed
として fail-closed し、無効化標識とトリアージ記録を残す。本モジュールは他 3 補助モジュール
（invalidation_marker_writer／evidence_class_transitioner／triage_note_writer）を統合する。

対応設計節：design.md §検証器連携 §実行終了境界、§無効化処理
対応要件：Requirement 6 受入 1〜5・7〜9
"""
import json
from pathlib import Path

import yaml

from ..evidence_writer.immutability_guard import ImmutabilityGuard
from ..evidence_writer.writer import EvidenceWriter
from ..foundation_ref import vocabulary
from .evidence_class_transitioner import EvidenceClassTransitioner
from .invalidation_marker_writer import InvalidationMarkerWriter
from .triage_note_writer import TriageNoteWriter

_VALIDATOR_STATUS_VOCAB = set(vocabulary("validator_status"))


class RunCloseOrderError(Exception):
  """実行終了境界の順序違反または多重起動を検出した違反。"""


class ValidationBridge:
  """実行終了境界の順序を強制し、検証器を呼び、evidence_class を確定する。"""

  def __init__(self, run_dir, validator_callable):
    self.run_dir = Path(run_dir)
    self.validator = validator_callable
    self.manifest_path = self.run_dir / "run_manifest.yaml"
    self.guard = ImmutabilityGuard(run_dir)
    self.transitioner = EvidenceClassTransitioner()
    self.marker_writer = InvalidationMarkerWriter()
    self.triage_writer = TriageNoteWriter()

  def _manifest(self):
    return yaml.safe_load(self.manifest_path.read_text(encoding="utf-8")) or {}

  def _save_manifest(self, manifest):
    self.manifest_path.write_text(
      yaml.safe_dump(manifest, allow_unicode=True, sort_keys=False), encoding="utf-8"
    )

  def close_run(self, exploratory_declared=False):
    """実行終了境界を順序どおりに進め、evidence_class を確定する。"""
    manifest = self._manifest()
    run_status = manifest.get("run_status")

    # 多重起動の検知（既に終了した実行への再呼び出し）。
    if run_status in ("closed", "orchestration_failed"):
      raise RunCloseOrderError(f"既に終了した実行への二重起動：run_status={run_status!r}")
    if run_status != "in_progress":
      self._fail_closed(code="invalid_run_status", detail=f"run_status={run_status!r}")
      raise RunCloseOrderError(f"実行終了の前提を満たさない run_status：{run_status!r}")

    # 前提 1：Step D 完了かつ実行終了準備が整っている（P-002：run_close_ready を消費）。
    step_d_path = self.run_dir / "steps" / "step_d_integration.json"
    if not step_d_path.is_file():
      self._fail_closed(code="step_d_not_complete", detail="Step D が完了していない")
      raise RunCloseOrderError("Step D 完了前の実行終了は禁止")
    step_d = json.loads(step_d_path.read_text(encoding="utf-8"))
    if step_d.get("step_outcome") != "executed":
      self._fail_closed(code="step_d_not_complete", detail="Step D が完了していない")
      raise RunCloseOrderError("Step D 完了前の実行終了は禁止")
    if step_d.get("run_close_ready") is not True:
      self._fail_closed(code="run_close_not_ready",
                        detail="Step D が実行終了準備未完了（run_close_ready が True でない）")
      raise RunCloseOrderError("実行終了準備が整っていない（run_close_ready が True でない）")

    # 前提 2：人間署名（検証器呼び出しより前、要件 6 受入 9）。
    signoff_path = self.run_dir / "decisions" / "human_signoff.json"
    if not signoff_path.is_file():
      self._fail_closed(code="run_close_without_signoff", detail="人間署名なしの実行終了")
      raise RunCloseOrderError("人間署名前の検証器呼び出し・実行終了は禁止")
    signoff = json.loads(signoff_path.read_text(encoding="utf-8"))

    # 順序 3：生証拠の凍結。
    self.guard.freeze(closed_at=signoff.get("signed_off_at") or "closed")

    # 順序 4：検証器呼び出し。
    result = self.validator(self.run_dir)
    validator_status = result.get("validator_status")
    if validator_status not in _VALIDATOR_STATUS_VOCAB:
      # A-002：検証器が 4 値正本外を返したら fail-closed（中間状態を残さない）。
      self._fail_closed(
        code="invalid_validator_status",
        detail=f"検証器が foundation 4 値正本外の validator_status を返した：{validator_status!r}",
      )
      raise RunCloseOrderError(
        f"検証器が foundation 4 値正本外の validator_status を返した：{validator_status!r}"
      )

    # 順序 5：validator_result.json の保存。
    self._save_validator_result(result)

    # 無効化標識の有無を確認。
    has_marker = self._has_invalidation_marker()

    # evidence_class 確定遷移（9 行マッピング）。
    evidence_class = self.transitioner.transition(
      validator_status=validator_status,
      human_signoff_status=signoff["human_signoff_status"],
      exploratory_declared=exploratory_declared,
      has_invalidation_marker=has_marker,
    )

    # メタデータ更新（run_status=closed、validator_status、evidence_class の確定）。
    manifest = self._manifest()
    manifest["run_status"] = "closed"
    manifest["validator_status"] = validator_status
    manifest["human_signoff_status"] = signoff["human_signoff_status"]
    manifest["evidence_class"] = evidence_class
    self._save_manifest(manifest)

    # A-003：無効実行（invalid）ならトリアージ記録を生成する（design.md §無効化処理）。
    if evidence_class == "invalid":
      self.triage_writer.write(
        self.run_dir,
        primary_failure_code=f"validator_status={validator_status}",
        failed_validator_check_ids=result.get("error_list", []),
        invalidation_marker_linkage=(
          ["validation/invalidation_markers.json"] if has_marker else []
        ),
        operator_action_hint="検証結果と人間署名を確認し、無効原因を是正してから再実行する",
      )

    # A-006：唯一の横断正本 review_case.json に終了メタデータを反映する
    # （design.md §実行終了境界 手順 3）。
    EvidenceWriter(self.run_dir).project_to_review_case()

    return {
      "run_status": "closed",
      "validator_status": validator_status,
      "evidence_class": evidence_class,
    }

  def _save_validator_result(self, result):
    path = self.run_dir / "validation" / "validator_result.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

  def _has_invalidation_marker(self):
    path = self.run_dir / "validation" / "invalidation_markers.json"
    if not path.is_file():
      return False
    return bool(json.loads(path.read_text(encoding="utf-8")).get("markers"))

  def _fail_closed(self, *, code, detail):
    """検証器を起動せず orchestration_failed とし、無効化標識とトリアージ記録を残す。"""
    manifest = self._manifest()
    self.marker_writer.add_marker(self.run_dir, {
      "run_id": manifest.get("run_id", "unknown"),
      "reason_code": code,
      "reason_detail": detail,
      "scope": "run",
      "issued_by": "validation_bridge",
      "issued_at": "fail-closed",
    })
    self.triage_writer.write(
      self.run_dir,
      primary_failure_code=code,
      failed_validator_check_ids=[],
      invalidation_marker_linkage=[code],
      operator_action_hint="実行終了境界の前提条件（Step D 完了・人間署名）を満たしてから再実行する",
    )
    manifest = self._manifest()
    manifest["run_status"] = "orchestration_failed"
    # P-010：無効化標識を付与した実行は evidence_class=invalid に確定する
    # （design.md §セッションモデル §3：無効化標識ありは invalid）。
    manifest["evidence_class"] = "invalid"
    self._save_manifest(manifest)
