"""T-003 のテスト：treatment × phase/profile 選択軸。

対応タスク：runtime tasks.md T-003
対応設計節：design.md §セッションモデル §4 phase／profile と treatment の軸
対応要件：Requirement 2（処理方式対応の実行）、Requirement 8（フェーズ対応のレビュープロファイル）

テスト要件（tasks.md T-003 より）：
- 語彙 YAML の値テスト
- 軸選択の独立性テスト（一方の変更が他方に影響しないこと）
- 無効値の拒否テスト
"""
from pathlib import Path

import pytest
import yaml

from runtime_core.axis_selector import AxisSelector, InvalidAxisValue

REPO_ROOT = Path(__file__).resolve().parents[2]
TREATMENT_VOCAB = REPO_ROOT / "runtime/runtime_core/treatment_vocab.yaml"
PHASE_PROFILE_VOCAB = REPO_ROOT / "runtime/runtime_core/phase_profile_vocab.yaml"

# design.md §セッションモデル §4 の正本値
EXPECTED_TREATMENTS = {"primary", "adversarial", "judgment"}
EXPECTED_PHASE_PROFILES = {"intent", "requirements", "design", "tasks"}


def test_treatment_vocab_exists():
  assert TREATMENT_VOCAB.is_file(), f"存在しない：{TREATMENT_VOCAB}"


def test_phase_profile_vocab_exists():
  assert PHASE_PROFILE_VOCAB.is_file(), f"存在しない：{PHASE_PROFILE_VOCAB}"


def test_treatment_vocab_declares_3_values():
  """treatment 語彙 YAML が 3 値を宣言する（完了条件 1）。"""
  spec = yaml.safe_load(TREATMENT_VOCAB.read_text(encoding="utf-8"))
  assert set(spec["treatments"].keys()) == EXPECTED_TREATMENTS


def test_phase_profile_vocab_declares_4_values():
  """phase_profile 語彙 YAML が 4 値を宣言する（完了条件 1）。"""
  spec = yaml.safe_load(PHASE_PROFILE_VOCAB.read_text(encoding="utf-8"))
  assert set(spec["phase_profiles"].keys()) == EXPECTED_PHASE_PROFILES


def test_selector_valid_values():
  """AxisSelector が正本値を返す（語彙テスト）。"""
  selector = AxisSelector()
  assert set(selector.valid_treatments()) == EXPECTED_TREATMENTS
  assert set(selector.valid_phase_profiles()) == EXPECTED_PHASE_PROFILES


def test_select_treatment_returns_included_steps():
  """treatment 軸選択が included_steps を返す。"""
  selector = AxisSelector()
  primary = selector.select_treatment("primary")
  judgment = selector.select_treatment("judgment")
  assert "adversarial_review" not in primary["included_steps"]
  assert "adversarial_review" in judgment["included_steps"]
  assert "judgment" in judgment["included_steps"]


def test_select_phase_profile_returns_emphasis():
  """phase_profile 軸選択が emphasis を返す。"""
  selector = AxisSelector()
  design = selector.select_phase_profile("design")
  assert isinstance(design["emphasis"], list) and design["emphasis"]


def test_axes_are_independent_treatment_invariant_to_phase():
  """treatment を固定し phase_profile を変えても treatment 軸出力が不変（完了条件 2）。"""
  selector = AxisSelector()
  out1 = selector.select("judgment", "intent")
  out2 = selector.select("judgment", "tasks")
  assert out1["treatment_axis"] == out2["treatment_axis"], (
    "phase_profile の変更が treatment 軸出力に影響している"
  )


def test_axes_are_independent_phase_invariant_to_treatment():
  """phase_profile を固定し treatment を変えても phase 軸出力が不変（完了条件 2）。"""
  selector = AxisSelector()
  out1 = selector.select("primary", "design")
  out2 = selector.select("judgment", "design")
  assert out1["phase_axis"] == out2["phase_axis"], (
    "treatment の変更が phase 軸出力に影響している"
  )


def test_invalid_treatment_rejected():
  """無効な treatment 値を拒否する（テスト要件）。"""
  selector = AxisSelector()
  with pytest.raises(InvalidAxisValue):
    selector.select_treatment("dual")  # 旧命名、無効


def test_invalid_phase_profile_rejected():
  """無効な phase_profile 値を拒否する（テスト要件）。"""
  selector = AxisSelector()
  with pytest.raises(InvalidAxisValue):
    selector.select_phase_profile("implementation")  # 4 値に含まれない


def test_select_rejects_invalid_combination():
  """select() が無効値を拒否する。"""
  selector = AxisSelector()
  with pytest.raises(InvalidAxisValue):
    selector.select("bogus", "design")
  with pytest.raises(InvalidAxisValue):
    selector.select("judgment", "bogus")
