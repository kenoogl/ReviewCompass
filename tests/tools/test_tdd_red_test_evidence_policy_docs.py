"""TDD 赤テスト証跡と commit 境界の文書契約テスト。"""

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def read_doc(path):
  """文書を読む。"""
  return (REPO_ROOT / path).read_text(encoding="utf-8")


def test_agents_contract_allows_red_test_evidence_without_immediate_commit():
  """AGENTS は赤テスト失敗確認を証跡化し、実装完了 commit にまとめられる"""
  text = read_doc("AGENTS.md")

  assert "赤テスト失敗確認は証跡に残す" in text
  assert "赤テスト失敗確認だけでは commit しない" in text
  assert "実装完了後に赤テストと実装をまとめて commit する" in text
  assert "テストが正しいことを確認できた段階でコミットする" not in text


def test_autonomy_guidance_preserves_tdd_order_but_moves_commit_boundary():
  """自律実行規律は TDD 順序を維持しつつ commit 停止点を実装完了へ寄せる"""
  text = read_doc(".reviewcompass/guidance/discipline_implementation_autonomy.md")

  assert "赤テスト失敗確認は証跡に残す" in text
  assert "赤テスト失敗確認だけでは commit 停止点にしない" in text
  assert "実装完了時の 1 commit にまとめる" in text
  assert "post-write verification" in text
  assert "next --json が返す workflow 停止条件" in text
  assert "自律実行の適用外" in text


def test_commit_stop_point_plan_no_longer_requires_red_test_commit_stop():
  """自律実行計画は赤テスト commit 停止を前提にしない"""
  text = read_doc(
    ".reviewcompass/backlog/plans/plan-2026-06-23-commit-stop-point-and-approval-ux.yaml",
  )

  assert "赤テスト段階なら赤テスト commit で停止" not in text
  assert "赤テスト失敗確認は証跡に残し" in text
  assert "実装完了後の commit まで進める" in text
