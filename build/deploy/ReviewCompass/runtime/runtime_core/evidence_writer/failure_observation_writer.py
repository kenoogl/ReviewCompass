"""failure_observation_writer（失敗観察の書き出し）（runtime tasks.md T-008）。

レビュー実行が失敗様式（review miss／disagreement など）に遭遇した場合、foundation の
failure_observation スキーマに準拠した記録を failures/failure_observations/<observation_id>.json に
書き出す。failure_observation は独立成果物として保管し、review_case.json に埋め込まない
（review_case の不変性を保つ、foundation §4 配置方針）。

対応設計節：design.md §証拠出力モデル（行 454）、§判断 5
対応要件：Requirement 4 受入 7
"""
import json
from pathlib import Path

from jsonschema import Draft202012Validator

_THIS_DIR = Path(__file__).resolve().parent
_REPO_ROOT = _THIS_DIR.parents[2]
_FAILURE_OBS_SCHEMA_PATH = _REPO_ROOT / "runtime/schemas/failure_observation.schema.json"


class FailureObservationWriter:
  """foundation failure_observation スキーマに準拠した失敗観察を書き出す。"""

  def __init__(self):
    schema = json.loads(_FAILURE_OBS_SCHEMA_PATH.read_text(encoding="utf-8"))
    self._validator = Draft202012Validator(schema)

  def write(self, run_dir, observation):
    """failure_observation を検証し、独立成果物として書き出す。"""
    # foundation スキーマ準拠を強制（必須項目欠落などは例外を送出）。
    self._validator.validate(observation)
    path = (
      Path(run_dir) / "failures" / "failure_observations"
      / f"{observation['observation_id']}.json"
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(observation, ensure_ascii=False, indent=2), encoding="utf-8")
    return path
