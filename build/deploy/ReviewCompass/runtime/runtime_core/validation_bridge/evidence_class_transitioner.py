"""evidence_class_transitioner（証拠区分の確定遷移）（runtime tasks.md T-009）。

design.md §セッションモデル §3 の 9 行マッピング表を実装する。foundation の
validator_status（4 値）と human_signoff_status（4 値）、探索宣言、無効化標識の組み合わせを
すべてカバーして evidence_class（foundation 4 値正本）を確定する。runtime は語彙を再定義しない。

確定遷移は実行終了時の単一トランザクションで完了し、過渡値は持たせない。

対応設計節：design.md §セッションモデル §3（9 行マッピング表）
対応要件：Requirement 6 受入 8
"""
from ..foundation_ref import vocabulary

# foundation 4 値正本を参照のみで取得（再定義禁止）。
_VALIDATOR_STATUS = set(vocabulary("validator_status"))
_SIGNOFF_STATUS = set(vocabulary("human_signoff_status"))
_EVIDENCE_CLASS = set(vocabulary("evidence_class"))


class EvidenceClassTransitioner:
  """9 行マッピング表に従って evidence_class を確定する。"""

  def transition(self, *, validator_status, human_signoff_status,
                 exploratory_declared, has_invalidation_marker):
    """組み合わせから evidence_class を一意確定する（9 行マッピング、優先順位適用）。"""
    if validator_status not in _VALIDATOR_STATUS:
      raise ValueError(f"未知の validator_status：{validator_status!r}")
    if human_signoff_status not in _SIGNOFF_STATUS:
      raise ValueError(f"未知の human_signoff_status：{human_signoff_status!r}")

    # 行 1：探索宣言が他の判定より最優先（運用者の意図的決定）。
    if exploratory_declared:
      return "exploratory"
    # 行 2：無効化標識が付与された実行は無効。
    if has_invalidation_marker:
      return "invalid"
    # 行 3〜6：検証合格時は人間署名状態で分岐。
    if validator_status == "passed":
      return {
        "approved": "valid",
        "rejected": "invalid",
        "deferred": "analysis_blocked",
        "pending": "analysis_blocked",
      }[human_signoff_status]
    # 行 7：検証失敗。
    if validator_status == "failed":
      return "invalid"
    # 行 8：前提条件未充足で結論不能。
    if validator_status == "blocked":
      return "analysis_blocked"
    # 行 9：検証未実行で確定不能。
    if validator_status == "not_run":
      return "analysis_blocked"
    # ここには到達しない（validator_status は 4 値に限られる）。
    raise ValueError(f"evidence_class を確定できない組み合わせ：{validator_status}")
