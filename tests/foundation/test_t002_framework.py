"""T-002 のテスト：レイヤ1フレームワーク（layer1_framework.yaml）。

対応タスク：foundation tasks.md T-002
対応設計節：design.md §1 レビュー段の論理契約、§2 役の抽象化
対応要件：Requirement 1（レビュー状態機械の契約）、Requirement 2 受入 1（役の抽象名）

テスト要件（tasks.md T-002 より）：
- YAML 解析テスト
- 必須最上位区画 7 件の存在テスト
- Step 名・役名の固定値テスト
"""
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
FRAMEWORK_PATH = REPO_ROOT / "runtime/foundation/layer1_framework.yaml"

# design.md §1 で定める最上位 7 区画
EXPECTED_TOP_SECTIONS = [
  "version",
  "roles",
  "step_pipeline",
  "step_intents",
  "required_metadata_refs",
  "asset_locations",
  "override_extension_point",
]

# design.md §1 の Step A/B/C/D 正本名称
EXPECTED_STEP_NAMES = [
  "primary_detection",
  "adversarial_review",
  "judgment",
  "integration",
]

# design.md §2 の役抽象名
EXPECTED_ROLE_NAMES = [
  "primary_reviewer",
  "adversarial_reviewer",
  "judgment_reviewer",
]


@pytest.fixture
def framework():
  """layer1_framework.yaml を読み込んで dict を返す。"""
  if not FRAMEWORK_PATH.is_file():
    pytest.fail(f"layer1_framework.yaml が存在しない：{FRAMEWORK_PATH}")
  with FRAMEWORK_PATH.open(encoding="utf-8") as f:
    return yaml.safe_load(f)


def test_yaml_parses():
  """YAML として解析可能で、トップが辞書である。"""
  if not FRAMEWORK_PATH.is_file():
    pytest.fail(f"layer1_framework.yaml が存在しない：{FRAMEWORK_PATH}")
  with FRAMEWORK_PATH.open(encoding="utf-8") as f:
    data = yaml.safe_load(f)
  assert isinstance(data, dict), "トップレベルが辞書でない"


@pytest.mark.parametrize("section", EXPECTED_TOP_SECTIONS)
def test_top_section_exists(framework, section):
  """必須最上位区画 7 件がすべて存在する。"""
  assert section in framework, f"最上位区画が欠落：{section}"


def test_step_pipeline_fixed_names(framework):
  """step_pipeline が Step A/B/C/D の正本名称 4 つを順序どおり持つ。"""
  pipeline = framework.get("step_pipeline")
  assert pipeline == EXPECTED_STEP_NAMES, (
    f"step_pipeline の正本名称が一致しない：{pipeline}"
  )


def test_roles_fixed_names(framework):
  """roles が 3 役の抽象名をすべて持つ。"""
  roles = framework.get("roles", {})
  role_keys = set(roles.keys()) if isinstance(roles, dict) else set(roles)
  for name in EXPECTED_ROLE_NAMES:
    assert name in role_keys, f"役抽象名が欠落：{name}"
