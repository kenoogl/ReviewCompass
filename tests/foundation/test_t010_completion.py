"""T-010 のテスト：完成判定基準の自動実行。

対応タスク：foundation tasks.md T-010
対応設計節：design.md §完成判定基準（6 項目）、完成判定レポートの YAML スキーマ
対応要件：foundation 全要件の機械的合否判定

テスト要件（tasks.md T-010 より）：
- 統合スクリプトの正常系テスト
- 不完全状態での fail テスト
- 双方向整合チェック（要件追跡表 ⇔ 各タスク本文の対応要件欄）
"""
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "tools" / "foundation_validators"))

import check_completion as cc  # noqa: E402


def test_report_has_required_top_keys():
  """レポートが design.md のスキーマの必須トップキーを持つ。"""
  report = cc.run_completion_check(REPO_ROOT)
  for key in ["overall_pass", "target_commit", "timestamp", "criteria_results"]:
    assert key in report, f"レポートに必須キーが欠落：{key}"


def test_report_has_exactly_6_criteria():
  """criteria_results が 6 項目ちょうどである。"""
  report = cc.run_completion_check(REPO_ROOT)
  assert len(report["criteria_results"]) == 6


def test_each_criterion_has_required_fields():
  """各 criterion が criterion_id／name／status／details を持ち、id は 1〜6 で一意。"""
  report = cc.run_completion_check(REPO_ROOT)
  ids = []
  for c in report["criteria_results"]:
    for key in ["criterion_id", "name", "status", "details"]:
      assert key in c, f"criterion に必須フィールド欠落：{key}"
    assert c["status"] in ["pass", "fail", "error"], f"status が不正：{c['status']}"
    assert 1 <= c["criterion_id"] <= 6
    ids.append(c["criterion_id"])
  assert sorted(ids) == [1, 2, 3, 4, 5, 6], f"criterion_id が 1〜6 で一意でない：{ids}"


def test_overall_pass_is_bool():
  """overall_pass が真偽値である。"""
  report = cc.run_completion_check(REPO_ROOT)
  assert isinstance(report["overall_pass"], bool)


def test_real_repo_completion_passes():
  """実リポジトリで完成判定が pass する（全 6 項目が pass）。"""
  report = cc.run_completion_check(REPO_ROOT)
  assert report["overall_pass"] is True, (
    f"完成判定が pass しない：{[c for c in report['criteria_results'] if c['status'] != 'pass']}"
  )


# --- 双方向整合チェック ---

def test_bidirectional_consistent_text_passes():
  """要件追跡表とタスク本文の対応要件が双方向で整合するテキストはエラー 0。"""
  text = """
### T-001
- **対応要件**：Requirement 5、Requirement 7

## 要件追跡（Requirements Traceability）

| 要件 | 対応タスク |
|------|-----------|
| Requirement 5：x | T-001 |
| Requirement 7：y | T-001 |
"""
  errors = cc.check_bidirectional_traceability(text)
  assert errors == [], f"整合テキストでエラー：{errors}"


def test_bidirectional_inconsistent_text_fails():
  """タスク本文が参照する要件が追跡表にないと不整合として検出される。"""
  text = """
### T-001
- **対応要件**：Requirement 5、Requirement 99

## 要件追跡（Requirements Traceability）

| 要件 | 対応タスク |
|------|-----------|
| Requirement 5：x | T-001 |
"""
  errors = cc.check_bidirectional_traceability(text)
  assert errors, "片方向の不整合（Requirement 99）が検出されない"


def test_real_tasks_md_bidirectional_consistent():
  """実 tasks.md が双方向整合している。"""
  tasks_md = REPO_ROOT / ".reviewcompass/specs/foundation/tasks.md"
  text = tasks_md.read_text(encoding="utf-8")
  errors = cc.check_bidirectional_traceability(text)
  assert errors == [], f"実 tasks.md が双方向整合しない：{errors}"


def test_main_returns_int():
  """main は整数の終了コードを返す。"""
  rc = cc.main([str(REPO_ROOT)])
  assert isinstance(rc, int)
