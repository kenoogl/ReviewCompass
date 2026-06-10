"""human_signoff_writer（人間署名記録の生成）（runtime tasks.md T-007）。

実行全体の人間終了判断を表す実行レベル正本 decisions/human_signoff.json を出力する。
human_signoff_status は foundation 4 値正本（pending／approved／rejected／deferred）を
再定義せず参照する。本記録は実行終了境界の順序の起点で、検証器呼び出しより前に書き込む
（要件 6 受入 9、順序強制は T-009）。

対応設計節：design.md §人間署名記録
対応要件：Requirement 5（人間決定の組み込み）、Requirement 6 受入 9
"""
import json
from pathlib import Path

from ..foundation_ref import vocabulary

# foundation human_signoff_status 4 値正本を参照のみで取得（再定義禁止）。
_SIGNOFF_STATUS_VOCAB = set(vocabulary("human_signoff_status"))


class InvalidSignoffStatus(Exception):
  """foundation 4 値正本に基づかない signoff 状態を検出した違反（再定義禁止）。"""


class HumanSignoffWriter:
  """decisions/human_signoff.json を書き出す。"""

  def write(self, run_dir, *, run_id, human_signoff_status, signed_off_by,
            signed_off_at, covered_decision_unit_ids, signoff_note=""):
    if human_signoff_status not in _SIGNOFF_STATUS_VOCAB:
      raise InvalidSignoffStatus(
        f"human_signoff_status は foundation 4 値正本 {sorted(_SIGNOFF_STATUS_VOCAB)} から："
        f"{human_signoff_status!r}"
      )
    record = {
      "run_id": run_id,
      "human_signoff_status": human_signoff_status,
      "signed_off_by": signed_off_by,
      "signed_off_at": signed_off_at,
      "covered_decision_unit_ids": list(covered_decision_unit_ids),
      "signoff_note": signoff_note,
    }
    path = Path(run_dir) / "decisions" / "human_signoff.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
    return path
