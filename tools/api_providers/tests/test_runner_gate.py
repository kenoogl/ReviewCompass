# tools/api_providers/tests/test_runner_gate.py
# PPWM-6: API 実行前の関門（runner gate）テスト。

import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
  sys.path.insert(0, str(_PROJECT_ROOT))

import pytest

from tools.api_providers.runner_gate import check_runner_gate


def _ok_audit():
  return {"verdict": "OK", "exit_code": 0, "reasons": []}


def _deviation_audit(reason="プロンプトに問題があります"):
  return {"verdict": "DEVIATION", "exit_code": 2, "reasons": [reason]}


def _post_write_next_action():
  return {"kind": "post_write_verification", "target_files": ["docs/disciplines/policy.md"]}


class TestRunnerGateAllowed:
  """すべての条件が揃ったとき API 実行を許可する"""

  def test_gate_allows_when_all_conditions_met(self):
    """next_action.kind が正しく、監査OK、バリアント指定ありで許可される"""
    result = check_runner_gate(
      next_action=_post_write_next_action(),
      prompt="## Review Purpose\n...",
      audit_result=_ok_audit(),
      variant="post-write-verification-v1",
    )

    assert result["allowed"] is True
    assert result["verdict"] == "OK"
    assert result["reasons"] == []

  def test_gate_result_has_required_keys(self):
    """関門の結果には allowed / verdict / reasons が含まれる"""
    result = check_runner_gate(
      next_action=_post_write_next_action(),
      prompt="## Review Purpose\n...",
      audit_result=_ok_audit(),
      variant="post-write-verification-v1",
    )

    assert "allowed" in result
    assert "verdict" in result
    assert "reasons" in result


class TestRunnerGateNextActionKind:
  """next_action.kind の確認"""

  def test_gate_rejects_wrong_next_action_kind(self):
    """next_action.kind が post_write_verification でない場合は拒否"""
    result = check_runner_gate(
      next_action={"kind": "post_write_policy_violation", "target_files": []},
      prompt="## Review Purpose\n...",
      audit_result=_ok_audit(),
      variant="post-write-verification-v1",
    )

    assert result["allowed"] is False
    assert result["verdict"] == "DEVIATION"
    assert any("post_write_verification" in r for r in result["reasons"])

  def test_gate_rejects_stage_kind(self):
    """next_action.kind が stage のときも拒否"""
    result = check_runner_gate(
      next_action={"kind": "stage", "feature": "wm", "phase": "impl", "stage": "triad-review"},
      prompt="## Review Purpose\n...",
      audit_result=_ok_audit(),
      variant="post-write-verification-v1",
    )

    assert result["allowed"] is False

  def test_gate_rejects_missing_next_action(self):
    """next_action が None のときは拒否"""
    result = check_runner_gate(
      next_action=None,
      prompt="## Review Purpose\n...",
      audit_result=_ok_audit(),
      variant="post-write-verification-v1",
    )

    assert result["allowed"] is False


class TestRunnerGateAuditResult:
  """プロンプト監査結果の確認"""

  def test_gate_rejects_when_audit_is_deviation(self):
    """監査結果が DEVIATION のときは拒否"""
    result = check_runner_gate(
      next_action=_post_write_next_action(),
      prompt="## Review Purpose\n...",
      audit_result=_deviation_audit(),
      variant="post-write-verification-v1",
    )

    assert result["allowed"] is False
    assert result["verdict"] == "DEVIATION"

  def test_gate_rejects_when_no_audit_provided(self):
    """監査結果が None（未実施）のときは拒否"""
    result = check_runner_gate(
      next_action=_post_write_next_action(),
      prompt="## Review Purpose\n...",
      audit_result=None,
      variant="post-write-verification-v1",
    )

    assert result["allowed"] is False
    assert any("audit" in r.lower() or "監査" in r for r in result["reasons"])

  def test_deviation_cannot_be_overridden(self):
    """監査 DEVIATION は user_approval_override を渡しても上書きできない"""
    result = check_runner_gate(
      next_action=_post_write_next_action(),
      prompt="## Review Purpose\n...",
      audit_result=_deviation_audit(),
      variant="post-write-verification-v1",
      user_approval_override=True,
    )

    assert result["allowed"] is False
    assert result["verdict"] == "DEVIATION"


class TestRunnerGateVariant:
  """バリアント（実行設定キー）の確認"""

  def test_gate_rejects_when_variant_not_specified(self):
    """バリアントが指定されていない（None）ときは拒否"""
    result = check_runner_gate(
      next_action=_post_write_next_action(),
      prompt="## Review Purpose\n...",
      audit_result=_ok_audit(),
      variant=None,
    )

    assert result["allowed"] is False
    assert any("variant" in r.lower() for r in result["reasons"])

  def test_gate_rejects_when_variant_is_empty_string(self):
    """バリアントが空文字のときは拒否（CLI デフォルト暗黙 fallback 防止）"""
    result = check_runner_gate(
      next_action=_post_write_next_action(),
      prompt="## Review Purpose\n...",
      audit_result=_ok_audit(),
      variant="",
    )

    assert result["allowed"] is False
    assert any("variant" in r.lower() for r in result["reasons"])

  def test_gate_allows_with_explicit_variant(self):
    """バリアントが明示指定されていれば通過する"""
    result = check_runner_gate(
      next_action=_post_write_next_action(),
      prompt="## Review Purpose\n...",
      audit_result=_ok_audit(),
      variant="claude-sonnet-4-6-post-write",
    )

    assert result["allowed"] is True


class TestRunnerGatePrompt:
  """プロンプト文字列の確認"""

  def test_gate_rejects_empty_prompt(self):
    """プロンプトが空のときは拒否"""
    result = check_runner_gate(
      next_action=_post_write_next_action(),
      prompt="",
      audit_result=_ok_audit(),
      variant="post-write-verification-v1",
    )

    assert result["allowed"] is False
    assert any("prompt" in r.lower() for r in result["reasons"])

  def test_gate_rejects_none_prompt(self):
    """プロンプトが None のときは拒否"""
    result = check_runner_gate(
      next_action=_post_write_next_action(),
      prompt=None,
      audit_result=_ok_audit(),
      variant="post-write-verification-v1",
    )

    assert result["allowed"] is False
