"""PPWM-5: post-write 検証プロンプトの監査。

生成されたプロンプト文字列を検査し、以下を確認する。
- 必須セクション10個がすべて存在する
- Target Materials セクションにコンテンツブロックがある（パスのみ不可）
- Source Materials セクションにコンテンツブロックがある（パスのみ不可）
- Output Contract に PASS/FAIL 判定が含まれる
- 機微情報パターンが含まれていない
"""

from __future__ import annotations

import re
from typing import Dict, List


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

SECRET_PATTERNS = [
  re.compile(r"\bsk-[A-Za-z0-9_-]{8,}\b"),
  re.compile(r"\b[A-Z0-9_]*(?:API|ACCESS|SECRET|PRIVATE)[A-Z0-9_]*_?KEY\s*=", re.I),
  re.compile(r"-----BEGIN (?:RSA |OPENSSH |EC |DSA )?PRIVATE KEY-----"),
]


def audit_post_write_prompt(prompt: str) -> Dict:
  """プロンプト文字列を監査して結果を返す。

  Returns:
    dict: verdict ("OK" | "DEVIATION"), reasons, exit_code
  """
  reasons: List[str] = []

  _check_required_sections(prompt, reasons)
  _check_target_materials_has_content(prompt, reasons)
  _check_source_materials_has_content(prompt, reasons)
  _check_output_contract_format(prompt, reasons)
  _check_sensitive_information(prompt, reasons)

  verdict = "OK" if not reasons else "DEVIATION"
  return {
    "verdict": verdict,
    "exit_code": 0 if verdict == "OK" else 2,
    "reasons": reasons,
  }


def _check_required_sections(prompt: str, reasons: List[str]) -> None:
  for section in REQUIRED_SECTIONS:
    if section not in prompt:
      reasons.append(f"必須セクションが欠落しています: {section}")


def _check_target_materials_has_content(prompt: str, reasons: List[str]) -> None:
  """Target Materials セクションにコンテンツブロック（```text ... ```）があるか確認する"""
  if "## Target Materials" not in prompt:
    return  # 必須セクション欠如は _check_required_sections で報告済み

  section_text = _extract_section(prompt, "## Target Materials")
  if not _has_content_block(section_text):
    reasons.append(
      "Target Materials セクションにコンテンツブロックがありません。"
      "パス/SHA のみの束は受け付けません"
    )


def _check_source_materials_has_content(prompt: str, reasons: List[str]) -> None:
  """Source Materials セクションにコンテンツブロックがあるか確認する。

  参照元なし（'（参照元なし）'）は許容する。
  """
  if "## Source Materials" not in prompt:
    return

  section_text = _extract_section(prompt, "## Source Materials")
  if "参照元なし" in section_text or "none" in section_text.lower():
    return  # 参照元なしは許容
  if not _has_content_block(section_text):
    reasons.append(
      "Source Materials セクションにコンテンツブロックがありません。"
      "参照元のパス/SHA のみの束は受け付けません"
    )


_OUTPUT_CONTRACT_VERDICT_PATTERN = re.compile(r"verdict\s*:\s*PASS\s*[|/]\s*FAIL", re.I)


def _check_output_contract_format(prompt: str, reasons: List[str]) -> None:
  """Output Contract セクションに 'verdict: PASS | FAIL' 形式の指示があるか確認する"""
  if "## Output Contract" not in prompt:
    return

  section_text = _extract_section(prompt, "## Output Contract")
  if not _OUTPUT_CONTRACT_VERDICT_PATTERN.search(section_text):
    reasons.append(
      "Output Contract セクションに 'verdict: PASS | FAIL' 形式の指示がありません。"
      "単一の PASS または FAIL 2値判定を出力契約として明記してください"
    )


def _check_sensitive_information(prompt: str, reasons: List[str]) -> None:
  """機微情報パターンがプロンプトに含まれていないか確認する"""
  for pattern in SECRET_PATTERNS:
    if pattern.search(prompt):
      reasons.append(
        "機微情報（API キー・秘密鍵等）と思われるパターンが検出されました。"
        "sensitive information をプロンプトに含めないでください"
      )
      return  # 1件検出で十分


def _extract_section(prompt: str, section_header: str) -> str:
  """指定セクションから次のセクションまでの文字列を返す。"""
  start = prompt.find(section_header)
  if start == -1:
    return ""
  # 次の ## セクションを探す
  next_section = prompt.find("\n## ", start + len(section_header))
  if next_section == -1:
    return prompt[start:]
  return prompt[start:next_section]


def _has_content_block(text: str) -> bool:
  """テキストに ```text ... ``` ブロックが含まれるかを返す。"""
  return "```text" in text and "```" in text[text.find("```text") + 7:]
