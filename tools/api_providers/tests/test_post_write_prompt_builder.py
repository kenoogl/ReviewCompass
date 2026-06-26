# tools/api_providers/tests/test_post_write_prompt_builder.py
# PPWM-4: post-write 検証専用プロンプトビルダーのテスト。

import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
  sys.path.insert(0, str(_PROJECT_ROOT))

import pytest

from tools.api_providers.source_bundle import SourceBundle
from tools.api_providers.post_write_prompt_builder import (
  PostWritePromptBuilder,
  PromptBuildError,
)


def _make_bundle(tmp_path, target_content="規律本文\n", source_content="ガイダンス本文\n"):
  target = tmp_path / "docs" / "disciplines" / "policy.md"
  target.parent.mkdir(parents=True)
  target.write_text(target_content, encoding="utf-8")
  source = tmp_path / ".reviewcompass" / "guidance" / "WORKFLOW_NAVIGATION.md"
  source.parent.mkdir(parents=True)
  source.write_text(source_content, encoding="utf-8")
  return SourceBundle.from_paths(
    target_paths=[str(target)],
    source_material_paths=[str(source)],
  )


REQUIRED_SECTIONS = [
  "## Review Purpose",
  "## User Review Requirements",
  "## Target Materials",
  "## Source Materials",
  "## Review Criteria",
  "## Non-goals / Out of Scope",
  "## Main Preanalysis",
  "## Required Checks",
  "## Output Contract",
  "## Sensitive Information Check",
]


class TestPostWritePromptBuilderRequiredSections:
  """必須セクション10個がすべて含まれることを確認するテスト"""

  def test_build_includes_all_required_sections(self, tmp_path):
    """生成プロンプトに必須セクションが10個すべて含まれる"""
    bundle = _make_bundle(tmp_path)
    builder = PostWritePromptBuilder(
      bundle=bundle,
      judgment_item="規律文書が post-write 検証規約を満たすか",
      review_purpose="規律変更後の整合性確認",
    )

    prompt = builder.build()

    for section in REQUIRED_SECTIONS:
      assert section in prompt, f"必須セクション '{section}' が見つかりません"

  def test_build_sections_appear_in_order(self, tmp_path):
    """必須セクションは定められた順序で現れる"""
    bundle = _make_bundle(tmp_path)
    builder = PostWritePromptBuilder(
      bundle=bundle,
      judgment_item="規律文書が post-write 検証規約を満たすか",
      review_purpose="規律変更後の整合性確認",
    )

    prompt = builder.build()

    positions = [prompt.index(s) for s in REQUIRED_SECTIONS]
    assert positions == sorted(positions), "必須セクションの順序が正しくありません"


class TestPostWritePromptBuilderContent:
  """プロンプト本文の内容テスト"""

  def test_target_materials_includes_file_content(self, tmp_path):
    """Target Materials セクションにターゲットファイルの本文が含まれる"""
    bundle = _make_bundle(tmp_path, target_content="重要な規律本文\n")
    builder = PostWritePromptBuilder(
      bundle=bundle,
      judgment_item="規律文書の整合性",
      review_purpose="post-write 確認",
    )

    prompt = builder.build()

    assert "重要な規律本文" in prompt

  def test_source_materials_includes_file_content(self, tmp_path):
    """Source Materials セクションに参照元ファイルの本文が含まれる"""
    bundle = _make_bundle(tmp_path, source_content="参照元ガイダンス本文\n")
    builder = PostWritePromptBuilder(
      bundle=bundle,
      judgment_item="規律文書の整合性",
      review_purpose="post-write 確認",
    )

    prompt = builder.build()

    assert "参照元ガイダンス本文" in prompt

  def test_review_purpose_appears_in_prompt(self, tmp_path):
    """review_purpose の文言がプロンプトに含まれる"""
    bundle = _make_bundle(tmp_path)
    purpose = "規律変更後に手順の矛盾がないか確認する"
    builder = PostWritePromptBuilder(
      bundle=bundle,
      judgment_item="整合性確認",
      review_purpose=purpose,
    )

    prompt = builder.build()

    assert purpose in prompt

  def test_judgment_item_appears_in_prompt(self, tmp_path):
    """judgment_item の文言がプロンプトに含まれる"""
    bundle = _make_bundle(tmp_path)
    item = "post-write 検証規約を文書が明示しているか"
    builder = PostWritePromptBuilder(
      bundle=bundle,
      judgment_item=item,
      review_purpose="整合性確認",
    )

    prompt = builder.build()

    assert item in prompt

  def test_output_contract_specifies_single_verdict(self, tmp_path):
    """Output Contract は単一の判定（PASS/FAIL）を要求する"""
    bundle = _make_bundle(tmp_path)
    builder = PostWritePromptBuilder(
      bundle=bundle,
      judgment_item="整合性確認",
      review_purpose="post-write 確認",
    )

    prompt = builder.build()

    output_contract_start = prompt.index("## Output Contract")
    output_contract_section = prompt[output_contract_start:]
    # 判定語が含まれる
    assert "PASS" in output_contract_section or "FAIL" in output_contract_section


class TestPostWritePromptBuilderSingleJudgment:
  """1 prompt 1 primary judgment の強制テスト"""

  def test_build_rejects_multiple_judgment_items(self, tmp_path):
    """複数の独立した判定項目はビルドエラーになる"""
    bundle = _make_bundle(tmp_path)

    with pytest.raises(PromptBuildError, match="judgment"):
      PostWritePromptBuilder(
        bundle=bundle,
        judgment_item=["整合性確認", "完全性確認"],  # リストは禁止
        review_purpose="post-write 確認",
      )

  def test_build_allows_single_judgment_item(self, tmp_path):
    """単一の判定項目は許可される"""
    bundle = _make_bundle(tmp_path)

    builder = PostWritePromptBuilder(
      bundle=bundle,
      judgment_item="整合性確認",
      review_purpose="post-write 確認",
    )
    prompt = builder.build()

    assert isinstance(prompt, str)
    assert len(prompt) > 0


class TestPostWritePromptBuilderValidation:
  """バンドルと入力の検証テスト"""

  def test_build_validates_bundle_before_building(self, tmp_path):
    """build() 前にバンドルの validate() を実行する"""
    from tools.api_providers.source_bundle import BundleValidationError

    invalid_bundle = SourceBundle.from_raw_entries([
      {
        "path": "docs/disciplines/policy.md",
        "role": "target",
        "content": "",  # 空コンテンツ → 無効
        "sha256": "abc",
        "content_mode": "full_text",
      }
    ])

    builder = PostWritePromptBuilder(
      bundle=invalid_bundle,
      judgment_item="整合性確認",
      review_purpose="post-write 確認",
    )

    with pytest.raises((PromptBuildError, BundleValidationError)):
      builder.build()

  def test_build_requires_non_empty_judgment_item(self, tmp_path):
    """judgment_item が空文字はエラー"""
    bundle = _make_bundle(tmp_path)

    with pytest.raises(PromptBuildError, match="judgment"):
      PostWritePromptBuilder(
        bundle=bundle,
        judgment_item="",
        review_purpose="post-write 確認",
      )

  def test_build_requires_non_empty_review_purpose(self, tmp_path):
    """review_purpose が空文字はエラー"""
    bundle = _make_bundle(tmp_path)

    with pytest.raises(PromptBuildError, match="review_purpose"):
      PostWritePromptBuilder(
        bundle=bundle,
        judgment_item="整合性確認",
        review_purpose="",
      )
