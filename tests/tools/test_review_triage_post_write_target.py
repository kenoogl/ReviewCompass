"""review_triage.py の _is_post_write_target が docs/sessions/auto-*.md を除外するテスト。

バグ：check-workflow-action.py は docs/sessions/auto-*.md（機械生成記録）を
post-write 対象から除外するが、review_triage.py は docs/ 以下全体を対象と
判定するため docs/sessions/auto-*.md を誤って引っかける。
write-manifest が「unreviewed post-write target changes remain」と失敗する原因。
"""
import importlib.util
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def _load_review_triage():
  module_dir = str(REPO_ROOT / "tools" / "api_providers")
  if module_dir not in sys.path:
    sys.path.insert(0, module_dir)
  spec = importlib.util.spec_from_file_location(
    "review_triage", REPO_ROOT / "tools" / "api_providers" / "review_triage.py")
  m = importlib.util.module_from_spec(spec)
  spec.loader.exec_module(m)
  return m


def test_auto_session_record_is_not_post_write_target():
  rt = _load_review_triage()
  assert rt._is_post_write_target(
    "docs/sessions/auto-2026-06-24-claude-09102360-d115-4f84-b5ef-150ec9febb52.md"
  ) is False


def test_multiple_auto_session_records_excluded():
  rt = _load_review_triage()
  for name in [
    "docs/sessions/auto-2026-06-24-claude-e70d1957-b24b-4877-a084-0916a637c3e0.md",
    "docs/sessions/auto-2026-06-25-claude-cb72ffc3-115d-48b9-b9f8-c3bd2284fcd4.md",
  ]:
    assert rt._is_post_write_target(name) is False, f"{name} should not be a target"


def test_manual_session_doc_is_still_target():
  rt = _load_review_triage()
  assert rt._is_post_write_target(
    "docs/sessions/session-49.md"
  ) is True


def test_docs_discipline_file_is_still_target():
  rt = _load_review_triage()
  assert rt._is_post_write_target(
    "docs/disciplines/some-discipline.md"
  ) is True


def test_workflow_stage_specs_are_not_post_write_targets():
  rt = _load_review_triage()
  for name in [
    ".reviewcompass/specs/workflow-management/spec.json",
    ".reviewcompass/specs/workflow-management/requirements.md",
    ".reviewcompass/specs/workflow-management/design.md",
    ".reviewcompass/specs/workflow-management/tasks.md",
    ".reviewcompass/specs/workflow-management/reviews/2026-06-27-run/triage.yaml",
  ]:
    assert rt._is_post_write_target(name) is False, f"{name} should not be a target"
