# tools/api_providers/tests/test_ppwm7_integration.py
# PPWM-7: post-write prompt 機械化の統合テスト。
#
# PPWM-2〜6 の各部品が連携して動くことを確認する。
# 実際のプロジェクトファイルと config/api-settings.yaml を使う。

import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
  sys.path.insert(0, str(_PROJECT_ROOT))

import pytest

from tools.api_providers.source_bundle import SourceBundle, BundleValidationError
from tools.api_providers.post_write_prompt_builder import PostWritePromptBuilder, PromptBuildError
from tools.api_providers.post_write_prompt_audit import audit_post_write_prompt
from tools.api_providers.runner_gate import check_runner_gate
from tools.api_providers.config_loader import (
  load_config,
  resolve_default_variant_name,
  resolve_variant,
)


CONFIG_PATH = _PROJECT_ROOT / "config" / "api-settings.yaml"


class TestFullPipelineIntegration:
  """PPWM-3〜6 の部品を組み合わせた全体フローのテスト"""

  def test_pipeline_passes_with_real_project_files(self):
    """実際のプロジェクトファイルで bundle→prompt→audit→gate が一貫して通過する"""
    target_path = _PROJECT_ROOT / ".reviewcompass" / "guidance" / "discipline_post_write_verification.md"
    source_path = _PROJECT_ROOT / ".reviewcompass" / "guidance" / "WORKFLOW_NAVIGATION.md"

    if not target_path.is_file():
      pytest.skip(f"テスト用ファイルが存在しません: {target_path}")
    if not source_path.is_file():
      pytest.skip(f"テスト用ファイルが存在しません: {source_path}")

    # PPWM-3: ソース束の構築
    bundle = SourceBundle.from_paths(
      target_paths=[str(target_path)],
      source_material_paths=[str(source_path)],
    )
    bundle.validate()

    # PPWM-4: プロンプトの生成
    builder = PostWritePromptBuilder(
      bundle=bundle,
      judgment_item="post-write 検証規律が手順として実行可能か",
      review_purpose="規律文書改定後の整合性確認",
    )
    prompt = builder.build()

    # PPWM-5: プロンプトの監査
    audit_result = audit_post_write_prompt(prompt)
    assert audit_result["verdict"] == "OK", (
      f"監査が失敗しました: {audit_result['reasons']}"
    )

    # PPWM-6: 関門の確認
    gate_result = check_runner_gate(
      next_action={"kind": "post_write_verification", "target_files": [str(target_path)]},
      prompt=prompt,
      audit_result=audit_result,
      variant="post_write_verification_independent_3way",
    )
    assert gate_result["allowed"] is True, (
      f"関門が拒否しました: {gate_result['reasons']}"
    )

  def test_generated_prompt_contains_required_content(self):
    """生成プロンプトにターゲット本文・参照元・範囲外・必須確認・出力契約が含まれる"""
    target_path = _PROJECT_ROOT / ".reviewcompass" / "guidance" / "discipline_post_write_verification.md"
    source_path = _PROJECT_ROOT / ".reviewcompass" / "guidance" / "WORKFLOW_NAVIGATION.md"

    if not target_path.is_file() or not source_path.is_file():
      pytest.skip("テスト用ファイルが存在しません")

    bundle = SourceBundle.from_paths(
      target_paths=[str(target_path)],
      source_material_paths=[str(source_path)],
    )
    prompt = PostWritePromptBuilder(
      bundle=bundle,
      judgment_item="整合性確認",
      review_purpose="統合テスト",
    ).build()

    # 必須コンテンツの確認
    assert "## Target Materials" in prompt
    assert "## Source Materials" in prompt
    assert "## Non-goals / Out of Scope" in prompt
    assert "## Required Checks" in prompt
    assert "## Output Contract" in prompt
    assert "```text" in prompt  # 本文が含まれている
    # ターゲットファイルの本文が含まれていることを間接確認
    target_content = target_path.read_text(encoding="utf-8")
    assert target_content[:50].strip() in prompt


class TestPipelineRejectsEdgeCases:
  """パイプラインのエッジケース拒否テスト"""

  def test_path_only_bundle_is_rejected(self):
    """パスのみのバンドル（本文なし）は validate() で拒否される"""
    bundle = SourceBundle.from_raw_entries([
      {
        "path": "docs/disciplines/policy.md",
        "role": "target",
        "content": "",  # 本文なし
        "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        "content_mode": "full_text",
      }
    ])

    with pytest.raises(BundleValidationError):
      bundle.validate()

  def test_multiple_judgment_items_are_rejected(self):
    """複数の判定項目をリストで渡すと PromptBuildError になる"""
    bundle = SourceBundle.from_raw_entries([
      {
        "path": "docs/disciplines/policy.md",
        "role": "target",
        "content": "規律本文\n",
        "sha256": "ignored_sha",  # validate() を呼ばなければ検査されない
        "content_mode": "full_text",
      }
    ])

    with pytest.raises(PromptBuildError, match="judgment"):
      PostWritePromptBuilder(
        bundle=bundle,
        judgment_item=["判定A", "判定B"],  # リストは禁止
        review_purpose="統合テスト",
      )

  def test_deviation_audit_blocks_runner_gate(self):
    """プロンプト監査が DEVIATION のとき関門は拒否する"""
    deviation_audit = {"verdict": "DEVIATION", "exit_code": 2, "reasons": ["本文が空です"]}

    gate_result = check_runner_gate(
      next_action={"kind": "post_write_verification", "target_files": ["docs/disciplines/policy.md"]},
      prompt="## Review Purpose\n...",
      audit_result=deviation_audit,
      variant="post_write_verification_independent_3way",
    )

    assert gate_result["allowed"] is False
    assert gate_result["verdict"] == "DEVIATION"

  def test_wrong_next_action_kind_blocks_runner_gate(self):
    """next_action.kind が post_write_verification でなければ関門は拒否する"""
    ok_audit = {"verdict": "OK", "exit_code": 0, "reasons": []}

    for kind in ("post_write_policy_violation", "stage", "completed", "lightweight_self_check"):
      gate_result = check_runner_gate(
        next_action={"kind": kind},
        prompt="## Review Purpose\n...",
        audit_result=ok_audit,
        variant="post_write_verification_independent_3way",
      )
      assert gate_result["allowed"] is False, f"kind={kind!r} で関門が通過してしまいました"


class TestVariantResolutionFromConfig:
  """設定ファイルからのバリアント解決テスト"""

  def test_api_review_prompt_quality_resolves_to_expected_variant(self):
    """api_review_prompt_quality の既定バリアントが api_review_prompt_quality_2way に解決される"""
    config = load_config(CONFIG_PATH)

    variant_name = resolve_default_variant_name(config, "api_review_prompt_quality")

    assert variant_name == "api_review_prompt_quality_2way"

  def test_api_review_prompt_quality_variant_uses_claude_sonnet_and_gemini(self):
    """api_review_prompt_quality_2way バリアントに claude-sonnet-4-6 と gemini-3.1-pro-preview が含まれる"""
    config = load_config(CONFIG_PATH)
    variant_name = resolve_default_variant_name(config, "api_review_prompt_quality")
    variant = resolve_variant(config, variant_name)

    adversarial_model = variant["adversarial"]["model"]
    judgment_model = variant["judgment"]["model"]

    assert adversarial_model == "claude-sonnet-4-6"
    assert judgment_model == "gemini-3.1-pro-preview"

  def test_post_write_verification_resolves_to_independent_3way(self):
    """post_write_verification の既定バリアットが post_write_verification_independent_3way に解決される"""
    config = load_config(CONFIG_PATH)

    variant_name = resolve_default_variant_name(config, "post_write_verification")

    assert variant_name == "post_write_verification_independent_3way"

  def test_post_write_verification_variant_includes_claude_sonnet(self):
    """post_write_verification_independent_3way バリアントに claude-sonnet-4-6 が含まれる"""
    config = load_config(CONFIG_PATH)
    variant_name = resolve_default_variant_name(config, "post_write_verification")
    variant = resolve_variant(config, variant_name)

    primary_model = variant["primary"]["model"]

    assert primary_model == "claude-sonnet-4-6"

  def test_variant_not_resolved_from_cli_default(self):
    """resolve_default_variant_name は CLI デフォルトへ fallback せず config から解決する"""
    config = load_config(CONFIG_PATH)

    # operation_defaults に存在しないキーを渡すと KeyError になる（CLI default fallback なし）
    with pytest.raises(KeyError):
      resolve_default_variant_name(config, "nonexistent_operation")

  def test_runner_gate_requires_explicit_variant_not_default(self):
    """関門はバリアント未指定を拒否する（設定ファイルからの明示解決が必要）"""
    ok_audit = {"verdict": "OK", "exit_code": 0, "reasons": []}

    # 明示バリアットなしは拒否
    result_none = check_runner_gate(
      next_action={"kind": "post_write_verification", "target_files": []},
      prompt="## Review Purpose\n...",
      audit_result=ok_audit,
      variant=None,
    )
    assert result_none["allowed"] is False

    # config から解決したバリアットを渡せば通過
    config = load_config(CONFIG_PATH)
    resolved_variant = resolve_default_variant_name(config, "post_write_verification")
    result_explicit = check_runner_gate(
      next_action={"kind": "post_write_verification", "target_files": []},
      prompt="## Review Purpose\n...",
      audit_result=ok_audit,
      variant=resolved_variant,
    )
    assert result_explicit["allowed"] is True
