# tools/api_providers/tests/test_post_write_prompt_audit.py
# PPWM-5: post-write 検証プロンプトの監査テスト。

import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
  sys.path.insert(0, str(_PROJECT_ROOT))

import pytest

from tools.api_providers.source_bundle import SourceBundle
from tools.api_providers.post_write_prompt_builder import PostWritePromptBuilder
from tools.api_providers.post_write_prompt_audit import audit_post_write_prompt


def _build_valid_prompt(tmp_path, target_content="規律本文\n", source_content="ガイダンス本文\n"):
  """テスト用の正常なプロンプトを生成する"""
  target = tmp_path / "docs" / "disciplines" / "policy.md"
  target.parent.mkdir(parents=True)
  target.write_text(target_content, encoding="utf-8")
  source = tmp_path / ".reviewcompass" / "guidance" / "WORKFLOW_NAVIGATION.md"
  source.parent.mkdir(parents=True)
  source.write_text(source_content, encoding="utf-8")
  bundle = SourceBundle.from_paths(
    target_paths=[str(target)],
    source_material_paths=[str(source)],
  )
  return PostWritePromptBuilder(
    bundle=bundle,
    judgment_item="規律文書が post-write 検証規約を満たすか",
    review_purpose="規律変更後の整合性確認",
  ).build()


class TestAuditPostWritePromptOK:
  """正常なプロンプトは PASS する"""

  def test_valid_prompt_passes_audit(self, tmp_path):
    """正常に構築されたプロンプトは監査を通過する"""
    prompt = _build_valid_prompt(tmp_path)

    result = audit_post_write_prompt(prompt)

    assert result["verdict"] == "OK"
    assert result["reasons"] == []

  def test_audit_result_has_required_keys(self, tmp_path):
    """監査結果には verdict / reasons / exit_code が含まれる"""
    prompt = _build_valid_prompt(tmp_path)

    result = audit_post_write_prompt(prompt)

    assert "verdict" in result
    assert "reasons" in result
    assert "exit_code" in result
    assert result["exit_code"] == 0


class TestAuditTargetBodyAbsent:
  """対象ファイル本文がないプロンプトを拒否する"""

  def test_rejects_prompt_without_target_file_body(self):
    """Target Materials にパス・SHA のみでコンテンツがないプロンプトは拒否"""
    prompt = "\n".join([
      "## Review Purpose",
      "",
      "目的",
      "",
      "## User Review Requirements",
      "",
      "要件",
      "",
      "## Target Materials",
      "",
      "### docs/disciplines/policy.md",
      "",
      "content_mode: full_text",
      "sha256: abc123",
      "",
      # コンテンツブロックなし（パスとSHAのみ）
      "## Source Materials",
      "",
      "（参照元なし）",
      "",
      "## Review Criteria",
      "",
      "基準",
      "",
      "## Non-goals / Out of Scope",
      "",
      "範囲外",
      "",
      "## Main Preanalysis",
      "",
      "事前分析",
      "",
      "## Required Checks",
      "",
      "チェック",
      "",
      "## Output Contract",
      "",
      "verdict: PASS | FAIL",
      "",
      "## Sensitive Information Check",
      "",
      "機微情報なし",
    ])

    result = audit_post_write_prompt(prompt)

    assert result["verdict"] == "DEVIATION"
    assert any("target" in r.lower() or "本文" in r for r in result["reasons"])

  def test_rejects_empty_target_materials_section(self):
    """Target Materials セクションが空のプロンプトは拒否"""
    prompt = "\n".join([
      "## Review Purpose",
      "",
      "目的",
      "",
      "## User Review Requirements", "",
      "## Target Materials",
      "",
      "## Source Materials", "",
      "## Review Criteria", "",
      "## Non-goals / Out of Scope", "",
      "## Main Preanalysis", "",
      "## Required Checks", "",
      "## Output Contract", "",
      "## Sensitive Information Check", "",
    ])

    result = audit_post_write_prompt(prompt)

    assert result["verdict"] == "DEVIATION"


class TestAuditSourceMaterialBodyAbsent:
  """参照元本文がないプロンプトを拒否する"""

  def test_rejects_path_only_source_material(self):
    """Source Materials にパスのみ（本文なし）のプロンプトは拒否"""
    prompt = "\n".join([
      "## Review Purpose", "", "目的", "",
      "## User Review Requirements", "", "要件", "",
      "## Target Materials",
      "",
      "### docs/disciplines/policy.md",
      "",
      "content_mode: full_text",
      "sha256: abc123",
      "",
      "```text",
      "規律本文",
      "```",
      "",
      "## Source Materials",
      "",
      "### .reviewcompass/guidance/WORKFLOW_NAVIGATION.md",
      "",
      "content_mode: full_text",
      "sha256: def456",
      "",
      # コンテンツブロックなし
      "## Review Criteria", "", "基準", "",
      "## Non-goals / Out of Scope", "", "範囲外", "",
      "## Main Preanalysis", "", "事前分析", "",
      "## Required Checks", "", "チェック", "",
      "## Output Contract", "", "verdict: PASS | FAIL", "",
      "## Sensitive Information Check", "", "機微情報なし", "",
    ])

    result = audit_post_write_prompt(prompt)

    assert result["verdict"] == "DEVIATION"
    assert any("source" in r.lower() or "参照元" in r for r in result["reasons"])


class TestAuditRequiredSections:
  """必須セクションが欠けているプロンプトを拒否する"""

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

  def test_rejects_prompt_missing_output_contract(self, tmp_path):
    """Output Contract セクションがないプロンプトは拒否"""
    prompt = _build_valid_prompt(tmp_path)
    prompt_without_contract = prompt.replace("## Output Contract", "## 出力仕様")

    result = audit_post_write_prompt(prompt_without_contract)

    assert result["verdict"] == "DEVIATION"
    assert any("Output Contract" in r for r in result["reasons"])

  def test_rejects_prompt_missing_required_section(self, tmp_path):
    """必須セクションが1つでも欠けると拒否"""
    for section in self.REQUIRED_SECTIONS:
      prompt = _build_valid_prompt(tmp_path)
      broken = prompt.replace(section, "## 削除済みセクション")

      result = audit_post_write_prompt(broken)

      assert result["verdict"] == "DEVIATION", f"セクション '{section}' が欠けても通過してしまいました"


class TestAuditOutputContract:
  """Output Contract の形式チェック"""

  def test_rejects_prompt_without_pass_fail_verdict(self, tmp_path):
    """Output Contract に PASS/FAIL が含まれないプロンプトは拒否"""
    prompt = _build_valid_prompt(tmp_path)
    # PASS/FAIL を削除
    broken = prompt.replace("verdict: PASS | FAIL", "verdict: 要確認")

    result = audit_post_write_prompt(broken)

    assert result["verdict"] == "DEVIATION"
    assert any("Output Contract" in r or "PASS" in r or "FAIL" in r for r in result["reasons"])


class TestAuditSensitiveInformation:
  """機微情報パターンの検出"""

  def test_rejects_prompt_with_api_key_pattern(self, tmp_path):
    """API キーらしきパターンが含まれるプロンプトは拒否"""
    base_prompt = _build_valid_prompt(tmp_path)
    prompt_with_secret = base_prompt + "\nsk-abcdefghijklmnop1234567890\n"

    result = audit_post_write_prompt(prompt_with_secret)

    assert result["verdict"] == "DEVIATION"
    assert any("sensitive" in r.lower() or "機微" in r for r in result["reasons"])

  def test_valid_prompt_without_secrets_passes(self, tmp_path):
    """機微情報のないプロンプトは機微情報チェックを通過する"""
    prompt = _build_valid_prompt(tmp_path)

    result = audit_post_write_prompt(prompt)

    assert result["verdict"] == "OK"
