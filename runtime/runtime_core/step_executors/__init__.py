"""step_executors：Step A／B／C／D 実行器（runtime tasks.md T-004／T-005）。

各段実行器が共有する定数・補助関数を本パッケージ初期化に置く。

- RUNTIME_REVIEW_MODE：runtime が生成する証拠に付与するレビューモード（要件 6 受入 6）
- STEP_OUTCOMES：step_outcome 3 値正本（step_outcome_vocab.yaml から読み込み）
- foundation_enum：foundation スキーマの enum を参照のみで取得（再定義しない、§判断 6）
- complete_finding：素の所見を foundation finding スキーマ準拠の 11 項目に整える
- skip_marker：treatment による段省略マーカーを作る
- write_step_json：steps/ への JSON 書き出し
"""
import json
from pathlib import Path

import yaml

from ..axis_selector import AxisSelector

RUNTIME_REVIEW_MODE = "runtime_mediated"

_THIS_DIR = Path(__file__).resolve().parent
_REPO_ROOT = _THIS_DIR.parents[2]
_STEP_OUTCOME_VOCAB = _THIS_DIR / "step_outcome_vocab.yaml"
_FOUNDATION_SCHEMA_DIR = _REPO_ROOT / "runtime/schemas"

STEP_OUTCOMES = set(
  yaml.safe_load(_STEP_OUTCOME_VOCAB.read_text(encoding="utf-8"))["step_outcome"]
)


def foundation_enum(schema_filename, field):
  """foundation スキーマの enum を参照のみで取得する（再定義禁止、§判断 6）。"""
  schema = json.loads((_FOUNDATION_SCHEMA_DIR / schema_filename).read_text(encoding="utf-8"))
  return set(schema["properties"][field]["enum"])


def included_steps_for(treatment):
  """treatment が実行する段の一覧を treatment_vocab 正本から得る（T-003 連動）。"""
  return AxisSelector().select_treatment(treatment)["included_steps"]


def complete_finding(raw, *, finding_id, step_id, source_role, counter_status):
  """素の所見を foundation finding スキーマ準拠の 11 項目に整える。

  Step A／B 時点で未確定の参照（judgment_ref／decision_unit_id／human_decision_ref）は
  空文字で埋め、後段（Step D／T-007／T-008）で確定させる。
  """
  return {
    "finding_id": finding_id,
    "step_id": step_id,
    "source_role": source_role,
    "severity": raw["severity"],
    "summary": raw["summary"],
    "source_refs": list(raw.get("source_refs", [])),
    "counter_evidence_refs": list(raw.get("counter_evidence_refs", [])),
    "judgment_ref": raw.get("judgment_ref", ""),
    "decision_unit_id": raw.get("decision_unit_id", ""),
    "human_decision_ref": raw.get("human_decision_ref", ""),
    "counter_status": counter_status,
  }


def skip_marker(*, step_id, step_name, treatment):
  """treatment による段省略マーカー（design.md §treatment × 段実行マトリクス）。"""
  return {
    "step_id": step_id,
    "step_name": step_name,
    "step_outcome": "skipped_by_treatment",
    "reason": f"treatment={treatment} の選択により本段を実行しない",
    "treatment": treatment,
    "review_mode": RUNTIME_REVIEW_MODE,
  }


def write_step_json(run_dir, filename, output):
  path = Path(run_dir) / "steps" / filename
  path.parent.mkdir(parents=True, exist_ok=True)
  path.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
  return path
