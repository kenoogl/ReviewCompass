"""axis_selector（軸選択ロジック）（runtime tasks.md T-003）。

treatment（処理方式）と phase_profile（フェーズ・プロファイル）を独立軸として扱う。
両者を実行メタデータの第一級属性として記録し、選択軸の混同を構造的に防ぐ
（design.md §判断 4）。

軸の独立性（完了条件 2 の操作的定義）：一方の軸の値を変更しても他方の軸選択
ロジック出力は変化しない。これは select_treatment／select_phase_profile が
互いの値を引数に取らず、select() がそれぞれを独立に解決することで保証する。

対応設計節：design.md §セッションモデル §4 phase／profile と treatment の軸
対応要件：Requirement 2、Requirement 8 受入 5（処理方式選択とフェーズプロファイル選択を区別）
"""
from pathlib import Path

import yaml

_THIS_DIR = Path(__file__).resolve().parent
_DEFAULT_TREATMENT_VOCAB = _THIS_DIR / "treatment_vocab.yaml"
_DEFAULT_PHASE_PROFILE_VOCAB = _THIS_DIR / "phase_profile_vocab.yaml"


class InvalidAxisValue(Exception):
  """軸の語彙正本に存在しない値を選択しようとした違反。"""


class AxisSelector:
  """treatment／phase_profile の 2 軸を独立に解決するセレクタ。"""

  def __init__(self, treatment_vocab_path=None, phase_profile_vocab_path=None):
    treatment_vocab_path = treatment_vocab_path or _DEFAULT_TREATMENT_VOCAB
    phase_profile_vocab_path = phase_profile_vocab_path or _DEFAULT_PHASE_PROFILE_VOCAB
    self._treatments = yaml.safe_load(Path(treatment_vocab_path).read_text(encoding="utf-8"))["treatments"]
    self._phase_profiles = yaml.safe_load(Path(phase_profile_vocab_path).read_text(encoding="utf-8"))["phase_profiles"]

  def valid_treatments(self):
    return list(self._treatments.keys())

  def valid_phase_profiles(self):
    return list(self._phase_profiles.keys())

  def select_treatment(self, treatment):
    """treatment 軸のみを解決する（phase_profile を引数に取らない＝独立）。"""
    if treatment not in self._treatments:
      raise InvalidAxisValue(
        f"無効な treatment 値：{treatment!r}（正本：{self.valid_treatments()}）"
      )
    spec = self._treatments[treatment]
    return {
      "treatment": treatment,
      "included_steps": list(spec["included_steps"]),
    }

  def select_phase_profile(self, phase_profile):
    """phase_profile 軸のみを解決する（treatment を引数に取らない＝独立）。"""
    if phase_profile not in self._phase_profiles:
      raise InvalidAxisValue(
        f"無効な phase_profile 値：{phase_profile!r}（正本：{self.valid_phase_profiles()}）"
      )
    spec = self._phase_profiles[phase_profile]
    return {
      "phase_profile": phase_profile,
      "emphasis": list(spec["emphasis"]),
    }

  def select(self, treatment, phase_profile):
    """両軸を独立に解決して合成する。

    treatment_axis は treatment のみに、phase_axis は phase_profile のみに依存する。
    """
    return {
      "treatment_axis": self.select_treatment(treatment),
      "phase_axis": self.select_phase_profile(phase_profile),
    }
