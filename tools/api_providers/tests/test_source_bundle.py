# tools/api_providers/tests/test_source_bundle.py
# PPWM-3: ソース束（source bundle）の構築・検証テスト。

import hashlib
import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
  sys.path.insert(0, str(_PROJECT_ROOT))

import pytest

from tools.api_providers.source_bundle import SourceBundle, BundleValidationError


def _sha256(text: str) -> str:
  return hashlib.sha256(text.encode("utf-8")).hexdigest()


class TestSourceBundleBuild:
  """SourceBundle.from_paths() による束の構築テスト"""

  def test_build_reads_file_content(self, tmp_path):
    """構築時にファイル本文を読み込む"""
    target = tmp_path / "docs" / "disciplines" / "policy.md"
    target.parent.mkdir(parents=True)
    target.write_text("規律本文\n", encoding="utf-8")

    bundle = SourceBundle.from_paths(
      target_paths=[str(target)],
      source_material_paths=[],
    )

    entries = bundle.to_target_entries()
    assert len(entries) == 1
    assert entries[0]["content"] == "規律本文\n"

  def test_build_computes_sha256_from_content(self, tmp_path):
    """SHA256 はファイル本文から計算される"""
    target = tmp_path / "docs" / "disciplines" / "policy.md"
    target.parent.mkdir(parents=True)
    body = "規律本文\n"
    target.write_text(body, encoding="utf-8")
    expected_sha = _sha256(body)

    bundle = SourceBundle.from_paths(
      target_paths=[str(target)],
      source_material_paths=[],
    )

    entries = bundle.to_target_entries()
    assert entries[0]["sha256"] == expected_sha

  def test_build_distinguishes_target_from_source_material(self, tmp_path):
    """target と source_material は別の役割として区別される"""
    target = tmp_path / "docs" / "disciplines" / "policy.md"
    target.parent.mkdir(parents=True)
    target.write_text("規律本文\n", encoding="utf-8")
    source = tmp_path / ".reviewcompass" / "guidance" / "WORKFLOW_NAVIGATION.md"
    source.parent.mkdir(parents=True)
    source.write_text("ガイダンス本文\n", encoding="utf-8")

    bundle = SourceBundle.from_paths(
      target_paths=[str(target)],
      source_material_paths=[str(source)],
    )

    target_entries = bundle.to_target_entries()
    source_entries = bundle.to_source_material_entries()
    assert len(target_entries) == 1
    assert len(source_entries) == 1
    assert target_entries[0]["role"] == "target"
    assert source_entries[0]["role"] == "source_material"

  def test_build_content_mode_is_full_text(self, tmp_path):
    """content_mode は full_text として設定される"""
    target = tmp_path / "docs" / "disciplines" / "policy.md"
    target.parent.mkdir(parents=True)
    target.write_text("規律本文\n", encoding="utf-8")

    bundle = SourceBundle.from_paths(
      target_paths=[str(target)],
      source_material_paths=[],
    )

    entries = bundle.to_target_entries()
    assert entries[0]["content_mode"] == "full_text"


class TestSourceBundleValidation:
  """SourceBundle.validate() による検証テスト"""

  def test_validate_passes_when_content_is_present(self, tmp_path):
    """本文が含まれる束は検証を通過する"""
    target = tmp_path / "docs" / "disciplines" / "policy.md"
    target.parent.mkdir(parents=True)
    target.write_text("規律本文\n", encoding="utf-8")

    bundle = SourceBundle.from_paths(
      target_paths=[str(target)],
      source_material_paths=[],
    )

    bundle.validate()  # 例外なしで通過すること

  def test_validate_rejects_path_only_entry(self):
    """コンテンツなし（パスのみ）の束は拒否される"""
    bundle = SourceBundle.from_raw_entries([
      {
        "path": "docs/disciplines/policy.md",
        "role": "target",
        "content": "",
        "sha256": _sha256(""),
        "content_mode": "full_text",
      }
    ])

    with pytest.raises(BundleValidationError, match="content"):
      bundle.validate()

  def test_validate_rejects_sha_only_without_content(self):
    """SHA はあるが本文が空の束は拒否される"""
    bundle = SourceBundle.from_raw_entries([
      {
        "path": "docs/disciplines/policy.md",
        "role": "target",
        "content": "",
        "sha256": "abc123",
        "content_mode": "full_text",
      }
    ])

    with pytest.raises(BundleValidationError, match="content"):
      bundle.validate()

  def test_validate_rejects_sha_mismatch(self):
    """SHA と本文が一致しない束は拒否される"""
    bundle = SourceBundle.from_raw_entries([
      {
        "path": "docs/disciplines/policy.md",
        "role": "target",
        "content": "規律本文\n",
        "sha256": "deadbeef" * 8,  # 意図的に間違ったSHA
        "content_mode": "full_text",
      }
    ])

    with pytest.raises(BundleValidationError, match="sha256"):
      bundle.validate()

  def test_validate_rejects_bundle_with_no_target(self, tmp_path):
    """target が一つもない束は拒否される"""
    source = tmp_path / ".reviewcompass" / "guidance" / "guide.md"
    source.parent.mkdir(parents=True)
    source.write_text("ガイダンス\n", encoding="utf-8")

    bundle = SourceBundle.from_paths(
      target_paths=[],
      source_material_paths=[str(source)],
    )

    with pytest.raises(BundleValidationError, match="target"):
      bundle.validate()

  def test_validate_sha_matches_content(self, tmp_path):
    """from_paths で構築した束は SHA と本文が常に一致する"""
    target = tmp_path / "docs" / "disciplines" / "policy.md"
    target.parent.mkdir(parents=True)
    body = "正確な規律本文\n"
    target.write_text(body, encoding="utf-8")

    bundle = SourceBundle.from_paths(
      target_paths=[str(target)],
      source_material_paths=[],
    )

    # validate() が通れば SHA と本文が一致している
    bundle.validate()
    entries = bundle.to_target_entries()
    assert entries[0]["sha256"] == _sha256(body)


class TestSourceBundleEntryFormat:
  """to_target_entries() / to_source_material_entries() の出力形式テスト"""

  def test_entries_include_required_fields(self, tmp_path):
    """エントリには path / role / content / sha256 / content_mode が含まれる"""
    target = tmp_path / "docs" / "disciplines" / "policy.md"
    target.parent.mkdir(parents=True)
    target.write_text("規律本文\n", encoding="utf-8")

    bundle = SourceBundle.from_paths(
      target_paths=[str(target)],
      source_material_paths=[],
    )

    entries = bundle.to_target_entries()
    entry = entries[0]
    assert "path" in entry
    assert "role" in entry
    assert "content" in entry
    assert "sha256" in entry
    assert "content_mode" in entry

  def test_source_material_entries_have_correct_role(self, tmp_path):
    """source_material エントリの role は source_material"""
    target = tmp_path / "docs" / "disciplines" / "policy.md"
    target.parent.mkdir(parents=True)
    target.write_text("規律本文\n", encoding="utf-8")
    source = tmp_path / ".reviewcompass" / "guidance" / "guide.md"
    source.parent.mkdir(parents=True)
    source.write_text("参照元本文\n", encoding="utf-8")

    bundle = SourceBundle.from_paths(
      target_paths=[str(target)],
      source_material_paths=[str(source)],
    )

    for entry in bundle.to_source_material_entries():
      assert entry["role"] == "source_material"
