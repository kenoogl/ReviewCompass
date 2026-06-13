"""書き込み後検証ガードが機械生成記録（来歴マーカー）を対象外にすることのテスト。

PLC-DEC-007 候補5・書き込み後検証ポリシー：機械生成・出所明記の派生記録は独立検証では
なく再現性で担保するため、is_post_write_verification_target は対象外（False）を返す。
"""
import importlib.util
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def _load_cwa():
  tools_dir = str(REPO_ROOT / "tools")
  if tools_dir not in sys.path:
    sys.path.insert(0, tools_dir)
  spec = importlib.util.spec_from_file_location(
    "cwa_under_test", REPO_ROOT / "tools" / "check-workflow-action.py")
  m = importlib.util.module_from_spec(spec)
  spec.loader.exec_module(m)
  return m


_MARKER = (
  "---\n"
  "generated_by: session-record-extractor\n"
  "tool_version: abc1234\n"
  "layer: record\n"
  "---\n"
  "# セッション記録\n本文\n"
)


def test_machine_generated_record_is_not_target(tmp_path):
  cwa = _load_cwa()
  d = tmp_path / "docs" / "sessions"
  d.mkdir(parents=True)
  (d / "auto-2026-06-13-claude-x.md").write_text(_MARKER, encoding="utf-8")
  assert cwa.is_post_write_verification_target(
    "docs/sessions/auto-2026-06-13-claude-x.md", str(tmp_path)) is False


def test_manual_doc_in_sessions_is_still_target(tmp_path):
  cwa = _load_cwa()
  d = tmp_path / "docs" / "sessions"
  d.mkdir(parents=True)
  (d / "session-49.md").write_text("# 手書き記録\n本文", encoding="utf-8")
  assert cwa.is_post_write_verification_target(
    "docs/sessions/session-49.md", str(tmp_path)) is True


def test_marker_exempts_regardless_of_directory(tmp_path):
  # 位置に依存せず、来歴マーカーがあれば対象外（性質ベース）
  cwa = _load_cwa()
  d = tmp_path / "docs" / "notes"
  d.mkdir(parents=True)
  (d / "weird-machine-record.md").write_text(_MARKER, encoding="utf-8")
  assert cwa.is_post_write_verification_target(
    "docs/notes/weird-machine-record.md", str(tmp_path)) is False


def test_non_marker_front_matter_is_still_target(tmp_path):
  cwa = _load_cwa()
  d = tmp_path / "docs" / "notes"
  d.mkdir(parents=True)
  (d / "normal.md").write_text(
    "---\ntitle: 普通のノート\n---\n本文", encoding="utf-8")
  assert cwa.is_post_write_verification_target(
    "docs/notes/normal.md", str(tmp_path)) is True


def test_default_cwd_keeps_backward_compatible_signature(tmp_path):
  # cwd 省略時も従来どおり path だけで判定できる（存在しないファイルは内容判定しない）
  cwa = _load_cwa()
  assert cwa.is_post_write_verification_target("docs/notes/nonexistent.md") is True
  assert cwa.is_post_write_verification_target("README.md") is False
