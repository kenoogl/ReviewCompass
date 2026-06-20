# tools/api_providers/tests/test_response_formatter.py
# レスポンス整形機構のテスト（サブサイクル 4-B、TDD 先行）。
# 計画書 §5.9.7.1（run_role.py 出力契約）／§5.9.3（所見メタデータ）参照。
# 出力 YAML のキー順は role → provider → model → attempts → duration_seconds → findings。
# 日本語は UTF-8 のまま出力（allow_unicode=True）、キー順は固定（sort_keys=False）。

import sys
from pathlib import Path

# プロジェクトルートを sys.path に追加
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
  sys.path.insert(0, str(_PROJECT_ROOT))

import pytest
import yaml

from tools.api_providers.response_formatter import (
  format_response,
  parse_response_data,
  parse_response_text,
)


# --- 1. format_response の正常系（基本フォーマット） ---


def test_format_response_empty_findings():
  """findings が空リストでも整形でき、必須メタデータが含まれる。"""
  output = format_response(
    role="primary",
    provider="anthropic-api",
    model="claude-opus-4-7",
    attempts=1,
    duration_seconds=5.2,
    findings=[],
  )
  parsed = yaml.safe_load(output)
  assert parsed["role"] == "primary"
  assert parsed["provider"] == "anthropic-api"
  assert parsed["model"] == "claude-opus-4-7"
  assert parsed["attempts"] == 1
  assert parsed["duration_seconds"] == 5.2
  assert parsed["findings"] == []


def test_format_response_with_one_finding():
  """findings 1 件で必須フィールドが含まれる。"""
  findings = [
    {
      "severity": "WARN",
      "target_location": "foundation/requirements.md §3.1",
      "description": "用語の重複定義",
      "rationale": "§3.1 と §5.2 で別意味の P1 が併存",
    }
  ]
  output = format_response(
    role="adversarial",
    provider="openai-api",
    model="gpt-5.5",
    attempts=2,
    duration_seconds=12.3,
    findings=findings,
  )
  parsed = yaml.safe_load(output)
  assert len(parsed["findings"]) == 1
  assert parsed["findings"][0]["severity"] == "WARN"
  assert parsed["findings"][0]["target_location"] == "foundation/requirements.md §3.1"


def test_format_response_with_evidence_type_and_verifying_commands():
  """findings に evidence_type と verifying_commands が含まれる場合の整形。"""
  findings = [
    {
      "severity": "ERROR",
      "target_location": "design.md §2.3",
      "description": "未定義語",
      "rationale": "P1 が定義されていない",
      "evidence_type": "fact",
      "verifying_commands": ["grep -n 'P1' design.md"],
    }
  ]
  output = format_response(
    role="judgment",
    provider="anthropic-api",
    model="claude-opus-4-7",
    attempts=1,
    duration_seconds=8.0,
    findings=findings,
  )
  parsed = yaml.safe_load(output)
  assert parsed["findings"][0]["evidence_type"] == "fact"
  assert parsed["findings"][0]["verifying_commands"] == ["grep -n 'P1' design.md"]


def test_format_response_with_multiple_findings_preserves_order():
  """findings が複数件で順序が保持される。"""
  findings = [
    {"severity": "CRITICAL", "target_location": "a.md", "description": "1 件目", "rationale": "rationale 1"},
    {"severity": "ERROR", "target_location": "b.md", "description": "2 件目", "rationale": "rationale 2"},
    {"severity": "WARN", "target_location": "c.md", "description": "3 件目", "rationale": "rationale 3"},
  ]
  output = format_response(
    role="primary",
    provider="anthropic-api",
    model="claude-opus-4-7",
    attempts=1,
    duration_seconds=10.0,
    findings=findings,
  )
  parsed = yaml.safe_load(output)
  assert [f["description"] for f in parsed["findings"]] == ["1 件目", "2 件目", "3 件目"]


def test_format_response_preserves_extra_review_fields():
  """findings 以外の構造化レビュー結果もトップレベルに保持する。"""
  output = format_response(
    role="adversarial",
    provider="anthropic-api",
    model="claude-sonnet-4-6",
    attempts=1,
    duration_seconds=7.0,
    findings=[],
    extra_fields={
      "verdict": "sufficient_with_revisions",
      "preanalysis_assessment": {
        "missing_perspectives": ["source coverage"],
      },
    },
  )
  parsed = yaml.safe_load(output)
  assert parsed["verdict"] == "sufficient_with_revisions"
  assert parsed["preanalysis_assessment"]["missing_perspectives"] == ["source coverage"]
  assert parsed["findings"] == []


def test_format_response_rejects_reserved_extra_field():
  """メタデータや findings を extra_fields から上書きしない。"""
  with pytest.raises(ValueError):
    format_response(
      role="adversarial",
      provider="anthropic-api",
      model="claude-sonnet-4-6",
      attempts=1,
      duration_seconds=7.0,
      findings=[],
      extra_fields={"model": "different-model"},
    )


# --- 2. 日本語と UTF-8 出力 ---


def test_format_response_japanese_text_kept_as_utf8():
  """日本語の自由記述が UTF-8 のまま出力され、ASCII エスケープされない。"""
  findings = [
    {
      "severity": "WARN",
      "target_location": "foundation/要件.md",
      "description": "対象アプリへの配置で語彙整合が崩れる",
      "rationale": "計画書 §5.18.7 と仕様が食い違う",
    }
  ]
  output = format_response(
    role="primary",
    provider="anthropic-api",
    model="claude-opus-4-7",
    attempts=1,
    duration_seconds=5.0,
    findings=findings,
  )
  # ASCII エスケープされていない（生の日本語が含まれる）
  assert "対象アプリへの配置で語彙整合が崩れる" in output
  assert "計画書 §5.18.7 と仕様が食い違う" in output
  # \u エスケープが出ていないこと
  assert "\\u" not in output


# --- 3. キー順の保持 ---


def test_format_response_top_level_key_order():
  """出力 YAML のトップレベルキー順が role → provider → model → attempts → duration_seconds → findings の順。"""
  output = format_response(
    role="primary",
    provider="anthropic-api",
    model="claude-opus-4-7",
    attempts=1,
    duration_seconds=5.0,
    findings=[],
  )
  # 各キーの出現位置を計算
  positions = [
    output.index("role:"),
    output.index("provider:"),
    output.index("model:"),
    output.index("attempts:"),
    output.index("duration_seconds:"),
    output.index("findings:"),
  ]
  # 順序が単調増加（つまり指定順に並んでいる）であることを確認
  assert positions == sorted(positions)


# --- 4. parse_response_text の正常系 ---


def test_parse_response_text_returns_findings_list():
  """API レスポンスの YAML 文字列から findings リストを返す。"""
  response_text = """
findings:
  - severity: WARN
    target_location: a.md
    description: テスト所見
    rationale: テスト根拠
"""
  findings = parse_response_text(response_text)
  assert isinstance(findings, list)
  assert len(findings) == 1
  assert findings[0]["severity"] == "WARN"
  assert findings[0]["description"] == "テスト所見"


def test_parse_response_data_preserves_structured_review_keys():
  """検査用レスポンスの verdict / assessment / prompt_sufficiency を保持する。"""
  response_text = """
verdict: sufficient_with_revisions
independent_reconstruction:
  judgment_items:
    - item_id: req14_approval_gate
      question: 承認ゲートを検査できるか
      target_files:
        - tasks.md
      source_materials:
        - requirements.md#Req14
      out_of_scope:
        - 実装修正
      rationale: 上流意図との接続が必要
preanalysis_assessment:
  supported_parts:
    - Req14 は分割が必要
  missing_perspectives:
    - APIレビューのデータソース網羅
  unsupported_or_overconfident_parts: []
  bias_risks:
    - main preanalysis を正解扱いする危険
prompt_sufficiency:
  information: revisions_needed
  question: sufficient
  scope: revisions_needed
  sensitivity_check: sufficient
  notes:
    - source を先に独立再構成させるべき
required_prompt_changes:
  - main preanalysis は仮説として扱わせる
findings:
  - severity: WARN
    target_location: review prompt
    description: preanalysis の扱いが強すぎる
    rationale: レビュー側の独立判断を阻害する
"""
  parsed = parse_response_data(response_text)
  assert parsed["verdict"] == "sufficient_with_revisions"
  assert parsed["independent_reconstruction"]["judgment_items"][0]["item_id"] == "req14_approval_gate"
  assert parsed["preanalysis_assessment"]["bias_risks"] == ["main preanalysis を正解扱いする危険"]
  assert parsed["prompt_sufficiency"]["information"] == "revisions_needed"
  assert parsed["required_prompt_changes"] == ["main preanalysis は仮説として扱わせる"]
  assert parsed["findings"][0]["severity"] == "WARN"


def test_parse_response_text_returns_findings_only_for_structured_review():
  """互換 API は構造化レビュー結果から findings だけを返す。"""
  response_text = """
verdict: sufficient
prompt_sufficiency:
  information: sufficient
findings:
  - severity: INFO
    target_location: review prompt
    description: 問題なし
    rationale: 必要項目を満たす
"""
  findings = parse_response_text(response_text)
  assert findings == [
    {
      "severity": "INFO",
      "target_location": "review prompt",
      "description": "問題なし",
      "rationale": "必要項目を満たす",
    }
  ]


# --- 5. parse_response_text の fail-closed 系 ---


def test_parse_response_text_invalid_yaml_raises():
  """不正な YAML 入力なら yaml.YAMLError を投げる（fail-closed）。"""
  response_text = "this is: not: valid: yaml: at all:"
  with pytest.raises(yaml.YAMLError):
    parse_response_text(response_text)


def test_parse_response_text_missing_findings_key_raises():
  """findings キーが存在しない場合は ValueError を投げる。"""
  response_text = """
other_key: value
"""
  with pytest.raises(ValueError):
    parse_response_text(response_text)


def test_parse_response_text_findings_not_list_raises():
  """findings の値がリストでない場合は ValueError を投げる。"""
  response_text = """
findings:
  severity: WARN
  description: これはリストではなく辞書
"""
  with pytest.raises(ValueError):
    parse_response_text(response_text)


def test_parse_response_text_strips_yaml_code_block():
  """```yaml ... ``` のコードブロック形式でも正常にパースできる。"""
  response_text = "```yaml\nfindings:\n  - severity: INFO\n    target_location: a.md\n    description: コードブロックテスト\n    rationale: 根拠\n```"
  findings = parse_response_text(response_text)
  assert isinstance(findings, list)
  assert findings[0]["description"] == "コードブロックテスト"


def test_parse_response_text_strips_plain_code_block():
  """``` ... ``` （yaml なし）のコードブロック形式でも正常にパースできる。"""
  response_text = "```\nfindings:\n  - severity: INFO\n    target_location: b.md\n    description: プレーンブロックテスト\n    rationale: 根拠\n```"
  findings = parse_response_text(response_text)
  assert isinstance(findings, list)
  assert findings[0]["description"] == "プレーンブロックテスト"
