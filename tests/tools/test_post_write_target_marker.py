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


# (い) 機械が吐く捕捉物（ディレクトリ単位の対象外）

def test_review_run_captures_are_not_target():
  cwa = _load_cwa()
  assert cwa.is_post_write_verification_target(
    "docs/notes/review-runs/some-run/raw/gemini.round-1.txt") is False
  assert cwa.is_post_write_verification_target(
    "docs/experiments/review-runs/some-run/triage.yaml") is False


def test_autonomous_parallel_ledger_is_not_target():
  cwa = _load_cwa()
  assert cwa.is_post_write_verification_target(
    "docs/logs/autonomous-parallel/2026-06-04-trial.yaml") is False


def test_post_write_verification_review_results_are_not_target():
  cwa = _load_cwa()
  assert cwa.is_post_write_verification_target(
    "docs/notes/post-write-verification-review/result-google-gemini-r1.yaml") is False


def test_compliance_reports_remain_target():
  # G2 は監査記録として対象に残す（迷えば対象側）
  cwa = _load_cwa()
  assert cwa.is_post_write_verification_target(
    "docs/discipline-compliance-reports/options-precheck-log.md") is True


def test_design_notes_remain_target():
  cwa = _load_cwa()
  assert cwa.is_post_write_verification_target(
    "docs/notes/2026-06-12-document-placement-plan.md") is True


def test_working_notes_are_not_strict_post_write_targets():
  cwa = _load_cwa()
  assert cwa.is_post_write_verification_target(
    "docs/notes/working/2026-06-17-memo.md") is False
