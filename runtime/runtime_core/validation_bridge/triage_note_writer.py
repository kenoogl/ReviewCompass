"""triage_note_writer（無効実行トリアージ記録の生成）（runtime tasks.md T-009）。

無効実行が発生した場合、runtime は derived/invalid_run_triage_note.json を生成する
（design.md §無効化処理）。失敗検査・無効化標識・運用者向け修復ヒントの連結を保持する
（要件 6 受入 7・8）。

対応設計節：design.md §無効化処理
対応要件：Requirement 6 受入 7・8
"""
import json
from pathlib import Path


class TriageNoteWriter:
  """derived/invalid_run_triage_note.json を書き出す。"""

  def write(self, run_dir, *, primary_failure_code, failed_validator_check_ids,
            invalidation_marker_linkage, operator_action_hint):
    note = {
      "primary_failure_code": primary_failure_code,
      "failed_validator_check_ids": list(failed_validator_check_ids),
      "invalidation_marker_linkage": list(invalidation_marker_linkage),
      "operator_action_hint": operator_action_hint,
    }
    path = Path(run_dir) / "derived" / "invalid_run_triage_note.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(note, ensure_ascii=False, indent=2), encoding="utf-8")
    return path
