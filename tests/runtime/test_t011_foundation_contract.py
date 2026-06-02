"""T-011 のテスト：foundation 契約の consumer 検証。

対応タスク：runtime tasks.md T-011
対応設計節：design.md §判断 6（contract consumer 原則）、§完成判定基準
対応要件：foundation 6 語彙正本の参照のみ使用、runtime 所有 3 語彙の正本確定

完了条件（tasks.md T-011）：
- foundation 6 語彙正本（counter_status／validator_status／evidence_class／
  review_mode／severity／final_label）を runtime が再定義せず参照のみで使用
- runtime 所有 3 語彙（phase_profile 4 値／treatment 3 値／step_outcome 3 値）が
  T-003／T-004 の成果物で正本確定
"""
from pathlib import Path

import pytest
import yaml

from runtime_core import foundation_ref

REPO_ROOT = Path(__file__).resolve().parents[2]
RUNTIME_CORE = REPO_ROOT / "runtime/runtime_core"

# foundation が所有する 6 語彙（design.md §責務境界、§判断 6）。
FOUNDATION_6 = {"counter_status", "validator_status", "evidence_class", "review_mode", "severity", "final_label"}

# runtime が所有する 3 語彙とその正本ファイル・件数。
RUNTIME_OWNED = {
  "treatment": (RUNTIME_CORE / "treatment_vocab.yaml", "treatments", 3),
  "phase_profile": (RUNTIME_CORE / "phase_profile_vocab.yaml", "phase_profiles", 4),
  "step_outcome": (RUNTIME_CORE / "step_executors/step_outcome_vocab.yaml", "step_outcome", 3),
}


def test_foundation_6_vocab_reachable():
  """foundation 6 語彙正本がすべて foundation 側から取得できる（参照可能）。"""
  assert set(foundation_ref.vocabulary("validator_status")) == {"not_run", "passed", "failed", "blocked"}
  assert set(foundation_ref.vocabulary("evidence_class")) == {"valid", "invalid", "exploratory", "analysis_blocked"}
  assert "api_mediated" in set(foundation_ref.vocabulary("review_mode"))
  assert set(foundation_ref.schema_enum("finding.schema.json", "counter_status")) == {
    "counter_evidence_raised", "no_counter_evidence_after_challenge", "not_assessed"}
  assert set(foundation_ref.schema_enum("finding.schema.json", "severity")) == {
    "CRITICAL", "ERROR", "WARN", "INFO"}
  assert set(foundation_ref.schema_enum("necessity_judgment.schema.json", "final_label")) == {
    "must-fix", "should-fix", "leave-as-is"}


def test_runtime_yaml_do_not_redefine_foundation_vocab():
  """runtime_core の YAML が foundation 6 語彙を再定義しない（キー名＋値集合の両面、P-009）。"""
  # foundation 6 語彙の値集合を参照のみで取得（再定義しない）。
  foundation_value_sets = {
    "validator_status": set(foundation_ref.vocabulary("validator_status")),
    "evidence_class": set(foundation_ref.vocabulary("evidence_class")),
    "review_mode": set(foundation_ref.vocabulary("review_mode")),
    "counter_status": set(foundation_ref.schema_enum("finding.schema.json", "counter_status")),
    "severity": set(foundation_ref.schema_enum("finding.schema.json", "severity")),
    "final_label": set(foundation_ref.schema_enum("necessity_judgment.schema.json", "final_label")),
  }
  offenders = []
  for path in RUNTIME_CORE.rglob("*.yaml"):
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
      continue
    rel = path.relative_to(REPO_ROOT)
    # キー名での再定義
    for name in FOUNDATION_6:
      if name in data:
        offenders.append(f"{rel} がトップレベルキー {name} を定義")
    # 値集合での再定義（いずれかのリスト値が foundation 値集合と完全一致）
    for key, value in data.items():
      if isinstance(value, list):
        vset = {v for v in value if isinstance(v, str)}
        for name, fset in foundation_value_sets.items():
          if fset and vset == fset:
            offenders.append(f"{rel} のキー {key} が foundation {name} の値集合を再掲")
  assert offenders == [], "foundation 語彙の再定義の疑い：\n" + "\n".join(offenders)


@pytest.mark.parametrize("name", sorted(RUNTIME_OWNED))
def test_runtime_owned_vocab_declared(name):
  """runtime 所有 3 語彙が正本ファイルで宣言され件数が一致する（T-003／T-004）。"""
  path, key, count = RUNTIME_OWNED[name]
  spec = yaml.safe_load(path.read_text(encoding="utf-8"))
  values = spec[key]
  assert len(values) == count, f"{name} の正本件数が {count} でない：{values}"


def test_step_d_action_map_matches_foundation_final_label():
  """Step D の final_label 写像のキーが foundation final_label 正本と一致する（再定義防止）。"""
  from runtime_core.step_executors.step_d_integration import FINAL_LABEL_TO_ACTION
  foundation_labels = set(foundation_ref.schema_enum("necessity_judgment.schema.json", "final_label"))
  assert set(FINAL_LABEL_TO_ACTION) == foundation_labels


def test_evidence_class_transitioner_uses_foundation_vocab():
  """evidence_class 確定遷移が foundation 4 値だけを返す（再定義しない）。"""
  from runtime_core.validation_bridge.evidence_class_transitioner import EvidenceClassTransitioner
  ec = set(foundation_ref.vocabulary("evidence_class"))
  t = EvidenceClassTransitioner()
  result = t.transition(validator_status="passed", human_signoff_status="approved",
                        exploratory_declared=False, has_invalidation_marker=False)
  assert result in ec
