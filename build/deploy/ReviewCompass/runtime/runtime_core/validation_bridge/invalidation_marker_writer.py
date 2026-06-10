"""invalidation_marker_writer（無効化標識の追加書き込み）（runtime tasks.md T-009）。

無効化は生証拠の編集ではなく validation/invalidation_markers.json への追加で表現する
（要件 6 受入 3、foundation §8）。全部無効化と部分無効化を同じ成果物形式で扱う。
各標識は foundation invalidation_marker スキーマに準拠する。

対応設計節：design.md §無効化処理
対応要件：Requirement 6 受入 3
"""
import json
from pathlib import Path

from jsonschema import Draft202012Validator

_THIS_DIR = Path(__file__).resolve().parent
_REPO_ROOT = _THIS_DIR.parents[2]
_MARKER_SCHEMA_PATH = _REPO_ROOT / "runtime/validators/contracts/invalidation_marker.schema.json"


class InvalidationMarkerWriter:
  """validation/invalidation_markers.json へ無効化標識を追加する。"""

  def __init__(self):
    schema = json.loads(_MARKER_SCHEMA_PATH.read_text(encoding="utf-8"))
    self._validator = Draft202012Validator(schema)

  def add_marker(self, run_dir, marker):
    """無効化標識を検証して追加する（生証拠は改変しない）。"""
    self._validator.validate(marker)
    path = Path(run_dir) / "validation" / "invalidation_markers.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.is_file():
      data = json.loads(path.read_text(encoding="utf-8"))
    else:
      data = {"markers": []}
    data["markers"].append(marker)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return path
