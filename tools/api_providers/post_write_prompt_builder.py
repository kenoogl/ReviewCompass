"""PPWM-4: post-write 検証専用プロンプトビルダー。

SourceBundle を受け取り、必須セクション10個を持つ
post-write 検証プロンプトを生成する。

必須セクション（順序固定）:
  1. Review Purpose
  2. User Review Requirements
  3. Target Materials
  4. Source Materials
  5. Review Criteria
  6. Non-goals / Out of Scope
  7. Main Preanalysis
  8. Required Checks
  9. Output Contract
  10. Sensitive Information Check
"""

from typing import List, Union

from tools.api_providers.source_bundle import SourceBundle, BundleValidationError


class PromptBuildError(ValueError):
  """プロンプト構築の失敗を表す例外"""
  pass


class PostWritePromptBuilder:
  """post-write 検証専用プロンプトビルダー。

  1 prompt 1 primary judgment を強制し、SourceBundle の検証を
  build() 実行前に行う。
  """

  def __init__(
    self,
    *,
    bundle: SourceBundle,
    judgment_item: Union[str, List],
    review_purpose: str,
  ) -> None:
    if isinstance(judgment_item, list):
      raise PromptBuildError(
        "judgment_item はリストにできません。1 prompt 1 judgment を守ってください"
      )
    if not isinstance(judgment_item, str) or not judgment_item.strip():
      raise PromptBuildError("judgment_item が空です")
    if not review_purpose or not review_purpose.strip():
      raise PromptBuildError("review_purpose が空です")

    self._bundle = bundle
    self._judgment_item = judgment_item.strip()
    self._review_purpose = review_purpose.strip()

  def build(self) -> str:
    """プロンプト文字列を生成して返す。バンドル検証に失敗した場合は例外を送出する。"""
    try:
      self._bundle.validate()
    except BundleValidationError as e:
      raise PromptBuildError(f"ソース束の検証に失敗しました: {e}") from e

    target_entries = self._bundle.to_target_entries()
    source_entries = self._bundle.to_source_material_entries()

    lines: List[str] = []

    # 1. Review Purpose
    lines += [
      "## Review Purpose",
      "",
      self._review_purpose,
      "",
      f"Primary judgment: {self._judgment_item}",
      "",
    ]

    # 2. User Review Requirements
    lines += [
      "## User Review Requirements",
      "",
      "- post-write 対象ファイルがワークフロー規約を満たすかを確認する。",
      "- 関連する規律・ガイダンスとの間に矛盾がないかを確認する。",
      "- この判定項目に集中し、無関係な指摘を含めない。",
      "",
    ]

    # 3. Target Materials
    lines += [
      "## Target Materials",
      "",
    ]
    for entry in target_entries:
      lines += [
        f"### {entry['path']}",
        "",
        f"content_mode: {entry['content_mode']}",
        f"sha256: {entry['sha256']}",
        "",
        "```text",
        entry["content"].rstrip("\n"),
        "```",
        "",
      ]

    # 4. Source Materials
    lines += [
      "## Source Materials",
      "",
    ]
    if source_entries:
      for entry in source_entries:
        lines += [
          f"### {entry['path']}",
          "",
          f"content_mode: {entry['content_mode']}",
          f"sha256: {entry['sha256']}",
          "",
          "```text",
          entry["content"].rstrip("\n"),
          "```",
          "",
        ]
    else:
      lines += ["（参照元なし）", ""]

    # 5. Review Criteria
    lines += [
      "## Review Criteria",
      "",
      f"- {self._judgment_item}",
      "- 対象ファイルの本文に基づいて判定する（要約・推測不可）。",
      "- 参照元との矛盾を具体的な箇所で示す。",
      "",
    ]

    # 6. Non-goals / Out of Scope
    lines += [
      "## Non-goals / Out of Scope",
      "",
      "- 対象ファイルに列挙されていないファイルの判定は行わない。",
      "- スタイルのみの修正提案は含めない。",
      "- 実装の不足を文書の欠陥として扱わない（文書がそれを主張している場合を除く）。",
      "",
    ]

    # 7. Main Preanalysis
    lines += [
      "## Main Preanalysis",
      "",
      "対象ファイルと参照元を読み、以下を把握してから判定に進む。",
      "",
      "- 対象ファイルが記述している主な契約・手順・制約。",
      "- 参照元が定める期待との差異。",
      "- 矛盾・欠落・曖昧な記述の有無。",
      "",
    ]

    # 8. Required Checks
    lines += [
      "## Required Checks",
      "",
      f"1. {self._judgment_item} — 対象ファイルの本文で確認する。",
      "2. 参照元との整合性 — 矛盾する記述があれば箇所を示す。",
      "3. 手順の実行可能性 — 記述された手順が API レビュー前に実行可能か確認する。",
      "",
    ]

    # 9. Output Contract
    lines += [
      "## Output Contract",
      "",
      "次の形式で出力する。それ以外の形式は不可。",
      "",
      "```",
      "verdict: PASS | FAIL",
      "summary: <1〜2 文で判定理由を述べる>",
      "findings:",
      "  - <FAIL の場合、具体的な問題箇所と理由を列挙する>",
      "```",
      "",
      "- 1 回の出力で 1 つの verdict のみを返す。",
      "- verdict は PASS または FAIL の 2 値のみとする。",
      "",
    ]

    # 10. Sensitive Information Check
    lines += [
      "## Sensitive Information Check",
      "",
      "出力に以下を含めない。",
      "",
      "- API キー・シークレット・パスワードなどの認証情報。",
      "- 個人識別情報。",
      "- 対象ファイルおよび参照元に存在しない機密情報の推測。",
      "",
    ]

    return "\n".join(lines)
