"""T-003 のテスト：実行メタデータ契約（metadata_contract.yaml）。

対応タスク：foundation tasks.md T-003
対応設計節：design.md §3 実行メタデータ契約、§3.5 推定タスク用語彙
対応要件：Requirement 1 受入 5、Requirement 6 受入 1〜11

テスト要件（tasks.md T-003 より）：
- YAML 解析テスト
- 必須項目数テスト（20 項目）
- 語彙正本値テスト（6 種の語彙）
"""
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
METADATA_PATH = REPO_ROOT / "runtime/foundation/metadata_contract.yaml"

# design.md §3 の必須 20 項目
EXPECTED_REQUIRED_FIELDS = [
  "run_id",
  "target_id",
  "target_artifact_hash",
  "source_repository_id",
  "source_revision",
  "phase_profile",
  "treatment",
  "review_mode",
  "protocol_version",
  "runtime_version",
  "schema_set_version",
  "prompt_set_version",
  "config_version",
  "config_hash",
  "run_status",
  "validator_status",
  "human_signoff_status",
  "evidence_class",
  "started_at",
  "closed_at",
]

# design.md §3・§3.5 の 6 種の語彙正本値
EXPECTED_VOCABULARIES = {
  "run_status": ["created", "in_progress", "closed", "orchestration_failed"],
  "validator_status": ["not_run", "passed", "failed", "blocked"],
  "human_signoff_status": ["pending", "approved", "rejected", "deferred"],
  "evidence_class": ["valid", "invalid", "exploratory", "analysis_blocked"],
  "review_mode": ["manual_dogfooding", "runtime_mediated", "subagent_mediated", "api_mediated"],
  "confidence_label": ["high", "medium", "low"],
}


@pytest.fixture
def contract():
  """metadata_contract.yaml を読み込んで dict を返す。"""
  if not METADATA_PATH.is_file():
    pytest.fail(f"metadata_contract.yaml が存在しない：{METADATA_PATH}")
  with METADATA_PATH.open(encoding="utf-8") as f:
    return yaml.safe_load(f)


def test_yaml_parses():
  """YAML として解析可能で、トップが辞書である。"""
  if not METADATA_PATH.is_file():
    pytest.fail(f"metadata_contract.yaml が存在しない：{METADATA_PATH}")
  with METADATA_PATH.open(encoding="utf-8") as f:
    data = yaml.safe_load(f)
  assert isinstance(data, dict), "トップレベルが辞書でない"


def test_required_fields_count_is_20(contract):
  """必須項目が 20 件ちょうどである。"""
  fields = contract.get("required_fields", [])
  assert len(fields) == 20, f"必須項目数が 20 でない：{len(fields)} 件"


def test_required_fields_exact_set(contract):
  """必須項目が design.md §3 の 20 項目と一致する。"""
  fields = contract.get("required_fields", [])
  assert set(fields) == set(EXPECTED_REQUIRED_FIELDS), (
    "必須項目の集合が design.md §3 と一致しない"
  )


@pytest.mark.parametrize("vocab_name", list(EXPECTED_VOCABULARIES.keys()))
def test_vocabulary_exists(contract, vocab_name):
  """6 種の語彙がすべて宣言されている。"""
  vocabs = contract.get("vocabularies", {})
  assert vocab_name in vocabs, f"語彙が欠落：{vocab_name}"


@pytest.mark.parametrize(
  "vocab_name,expected_values", list(EXPECTED_VOCABULARIES.items())
)
def test_vocabulary_values(contract, vocab_name, expected_values):
  """各語彙の正本値が design.md §3・§3.5 と一致する。"""
  vocabs = contract.get("vocabularies", {})
  actual = vocabs.get(vocab_name)
  assert actual == expected_values, (
    f"語彙 {vocab_name} の正本値が一致しない：{actual}"
  )
