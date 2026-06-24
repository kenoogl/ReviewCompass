"""commit の単発利用者指示運用を文書で固定するテスト"""

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def read_doc(path):
  """文書を読む"""
  return (REPO_ROOT / path).read_text(encoding="utf-8")


def test_codex_adapter_uses_single_turn_commit_instruction_policy():
  """Codex adapter は commit / 承認の二段階を要求しない"""
  text = read_doc(".reviewcompass/guidance/WORKFLOW_NAVIGATION_FOR_CODEX.md")

  assert "1 回目" not in text
  assert "2 回目" not in text
  assert "1回目" not in text
  assert "2回目" not in text
  assert "利用者の単発 commit 指示" in text
  assert "直近の利用者発話で明示された commit 指示" in text
  assert "利用者発話なしに Codex が承認文を生成してはならない" in text


def test_commit_operation_card_allows_user_commit_instruction_transfer_only():
  """操作カードは直近の commit 指示の転送だけを許可する"""
  text = read_doc(".reviewcompass/guidance/COMMIT_OPERATION_CARD.md")

  assert "直近の利用者発話で明示された commit 指示" in text
  assert "staged 内容承認と LLM commit 実行代行承認" in text
  assert "利用者発話なしに Codex / Claude / LLM が承認文を生成してはならない" in text
  assert "LLM が `printf` 等で承認文を生成" in text


def test_commit_operation_card_keeps_stale_approval_reprepare_internal():
  """古い承認レコードの再準備は利用者向け途中報告に出さない"""
  text = read_doc(".reviewcompass/guidance/COMMIT_OPERATION_CARD.md")

  assert "古い承認レコード" in text
  assert "消費済み" in text
  assert "現在の staged 内容と一致しない" in text
  assert "利用者向け途中報告に出してはならない" in text


def test_precheck_docs_describe_single_turn_commit_source():
  """precheck 文書は単発 commit 指示を approval source として説明する"""
  short = read_doc(".reviewcompass/guidance/WORKFLOW_PRECHECK.md")
  details = read_doc(".reviewcompass/guidance/WORKFLOW_PRECHECK_DETAILS.md")
  combined = short + "\n" + details

  assert "利用者の単発 commit 指示" in combined
  assert "staged 内容承認と LLM commit 実行代行承認" in combined
  assert "LLM が利用者発話なしに承認文を生成してはならない" in combined
