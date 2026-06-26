"""PPWM-6: API 実行前の関門（runner gate）。

API 実行ツール（runner）を起動する前に、以下の条件をすべて確認する。

1. next_action.kind == post_write_verification
2. プロンプトが空でない
3. プロンプト監査結果が OK（None または DEVIATION は拒否）
4. バリアント（実行設定キー）が明示指定されている（空文字・None は拒否）

監査 DEVIATION は user_approval_override があっても上書きできない。
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional


def check_runner_gate(
  *,
  next_action: Optional[Dict[str, Any]],
  prompt: Optional[str],
  audit_result: Optional[Dict[str, Any]],
  variant: Optional[str],
  user_approval_override: bool = False,
) -> Dict[str, Any]:
  """API 実行を許可するかを判定して結果を返す。

  Args:
    next_action: check-workflow-action.py next --json の next_action 辞書。
    prompt: PostWritePromptBuilder で生成したプロンプト文字列。
    audit_result: audit_post_write_prompt() の戻り値。None は「監査未実施」。
    variant: 設定キーから解決したバリアント名（CLI デフォルト fallback 禁止）。
    user_approval_override: True でも DEVIATION は上書きできない（意図的制約）。

  Returns:
    dict: allowed (bool), verdict ("OK" | "DEVIATION"), reasons (list[str])
  """
  reasons: List[str] = []

  _check_next_action_kind(next_action, reasons)
  _check_prompt(prompt, reasons)
  _check_audit_result(audit_result, reasons)
  _check_variant(variant, reasons)

  verdict = "OK" if not reasons else "DEVIATION"
  allowed = verdict == "OK"
  return {
    "allowed": allowed,
    "verdict": verdict,
    "reasons": reasons,
  }


def _check_next_action_kind(
  next_action: Optional[Dict[str, Any]],
  reasons: List[str],
) -> None:
  if not isinstance(next_action, dict):
    reasons.append(
      "next_action が指定されていません。"
      "post_write_verification 地点からのみ API 実行を許可します"
    )
    return
  kind = next_action.get("kind")
  if kind != "post_write_verification":
    reasons.append(
      f"next_action.kind が post_write_verification ではありません: {kind!r}。"
      "API 実行は post_write_verification 地点でのみ許可されます"
    )


def _check_prompt(prompt: Optional[str], reasons: List[str]) -> None:
  if not prompt:
    reasons.append(
      "prompt が空または未指定です。"
      "PostWritePromptBuilder で生成したプロンプトを渡してください"
    )


def _check_audit_result(
  audit_result: Optional[Dict[str, Any]],
  reasons: List[str],
) -> None:
  if audit_result is None:
    reasons.append(
      "プロンプト監査（audit）が実施されていません。"
      "audit_post_write_prompt() を実行して OK を確認してから API 実行に進んでください"
    )
    return
  verdict = audit_result.get("verdict")
  if verdict != "OK":
    audit_reasons = audit_result.get("reasons") or []
    reasons.append(
      f"プロンプト監査の結果が {verdict!r} です。監査 DEVIATION は上書きできません。"
      "プロンプトを修正して再度監査を通過してください"
    )
    reasons.extend(f"  監査指摘: {r}" for r in audit_reasons)


def _check_variant(variant: Optional[str], reasons: List[str]) -> None:
  if not variant or not variant.strip():
    reasons.append(
      "variant が指定されていません。"
      "post-write verification 用のバリアントを設定キーから明示指定してください。"
      "CLI デフォルトへの暗黙 fallback は禁止されています"
    )
