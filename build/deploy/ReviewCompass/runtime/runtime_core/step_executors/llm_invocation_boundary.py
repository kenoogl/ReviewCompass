"""言語モデル呼び出しの差し替え点（runtime tasks.md T-004）。

各段実行器の言語モデル呼び出しを差し替え可能な境界に集約する。本番では実モデルを
呼ぶ実装を差し込み、テストでは固定応答に差し替えて段実行器を決定的に検証できる
（design.md §テスト戦略 言語モデル差し替え点）。

対応設計節：design.md §ステップ実行モデル、§テスト戦略
対応要件：Requirement 1 受入 1〜3、Requirement 10 受入 2（実モデル呼び出しによる動的判定）
"""


class LLMInvocationBoundary:
  """言語モデル呼び出しの抽象境界。実装はこの invoke を上書きする。"""

  def invoke(self, *, role, prompt=None, target_artifact=None, context=None):
    raise NotImplementedError("LLMInvocationBoundary.invoke を実装すること")


class FixedResponseBoundary(LLMInvocationBoundary):
  """役ごとの固定応答を返す差し替え実装（決定的テスト用）。"""

  def __init__(self, responses_by_role):
    self._responses = dict(responses_by_role)

  def invoke(self, *, role, prompt=None, target_artifact=None, context=None):
    if role not in self._responses:
      raise KeyError(f"固定応答に役 {role!r} の応答がない")
    return self._responses[role]
