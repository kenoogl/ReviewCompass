"""tools/experiments/_gen_runtime_impl_triad_temp.py

runtime implementation 段 triad-review（api_mediated）用のプロンプト生成スクリプト（一時）。

レビュー対象（runtime 実装 ＋ テスト ＋ 上流文書 requirements/design/tasks）を結合し、
役別プロンプト（主役／敵対役／判定役）を生成して --out に書き出す。
生成したプロンプトは _experiment_n_model.py に --prompt-file で渡して 3 役を順に実行する。

実装段 triad-review は foundation では subagent_mediated で実施したため api_mediated 用の
プロンプト生成は前例がない。本スクリプトは runtime 用の一時実装で、後で削除予定。

利用者明示承認：実施方式「独立3社API（推奨）」（2026-06-02、AskUserQuestion 選択）。

引数：
- --role <primary|adversarial|judgment>：必須
- --prior-primary <path>：敵対役／判定役で必須（主役応答 YAML＝_experiment_n_model.py 出力）
- --prior-adversarial <path>：判定役で必須（敵対役応答 YAML）
- --out <path>：出力プロンプトファイルパス（必須）
"""
import argparse
import os
import sys
from pathlib import Path
from typing import List, Optional, Tuple

import yaml

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
RUNTIME_CORE = _PROJECT_ROOT / "runtime" / "runtime_core"
TESTS_RUNTIME = _PROJECT_ROOT / "tests" / "runtime"
SPEC_DIR = _PROJECT_ROOT / ".reviewcompass" / "specs" / "runtime"

PERSPECTIVES = """## レビュー観点（実装レビュー5観点、セッション45暫定確定）
1. タスク文書との整合：成果物の構造・内容が tasks.md の完了条件と一致しているか
2. 要件への追跡：実装成果物が要件追跡表（tasks.md §要件追跡）を経て要件本文（requirements.md）まで辿れるか
3. テスト網羅性と信頼性：テストが tasks.md のテスト要件を網羅し、偽陽性（実際は壊れているのに通る）がないか
4. 配置・命名規約の遵守：成果物の場所・ファイル名が design.md と tasks.md の成果物欄に一致するか
5. 機能横断波及の早期検出：実装の決定が他機能（foundation 等）の仕様や配置規約に影響しないか
"""


def collect_files(base: Path, exts: set) -> List[Tuple[str, str]]:
  """base 配下を再帰走査し、拡張子が exts のファイルを (相対パス, 内容) で返す。"""
  results: List[Tuple[str, str]] = []
  for root, dirs, files in os.walk(base):
    dirs[:] = [d for d in dirs if d != "__pycache__"]
    for fn in sorted(files):
      p = Path(root) / fn
      if p.suffix in exts:
        rel = p.relative_to(_PROJECT_ROOT)
        results.append((str(rel), p.read_text(encoding="utf-8")))
  return results


def build_target_section() -> str:
  """上流文書 ＋ 実装成果物 ＋ テストを結合した対象セクションを返す。"""
  parts: List[str] = ["# ========== 上流文書（要件・設計・タスク） =========="]
  for name in ("requirements.md", "design.md", "tasks.md"):
    content = (SPEC_DIR / name).read_text(encoding="utf-8")
    parts.append(f"\n## 上流文書：{name}\n{content}")
  parts.append("\n# ========== 実装成果物（runtime/runtime_core 配下） ==========")
  for rel, content in collect_files(RUNTIME_CORE, {".py", ".yaml", ".md"}):
    parts.append(f"\n### {rel}\n```\n{content}\n```")
  # T-001 成果物の運用文書（docs/operations/RUNTIME.md）も対象に含める。
  runtime_md = _PROJECT_ROOT / "docs" / "operations" / "RUNTIME.md"
  parts.append(
    "\n### docs/operations/RUNTIME.md（T-001 成果物：配置運用ルール）\n```\n"
    + runtime_md.read_text(encoding="utf-8")
    + "\n```"
  )
  parts.append("\n# ========== テスト（tests/runtime 配下） ==========")
  for rel, content in collect_files(TESTS_RUNTIME, {".py"}):
    parts.append(f"\n### {rel}\n```\n{content}\n```")
  return "\n".join(parts)


def read_response_text(path: str) -> str:
  """_experiment_n_model.py の出力 YAML から response_text を取り出す。"""
  data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
  if not isinstance(data, dict) or "response_text" not in data:
    raise ValueError(f"{path} に response_text がありません")
  return data["response_text"]


PRIMARY_INSTRUCTION = """# 役割：主役レビュアー（primary reviewer）

あなたは runtime 機能の実装に対する主役レビュアーです。下記の実装レビュー5観点それぞれに
ついて、実装成果物・テスト・上流文書を照合し、所見を網羅的に挙げてください。事実に基づいて
指摘し、推測には推測と明記してください。

{perspectives}

# 出力形式（厳守）
findings を含む YAML だけを返してください。説明文・前置きは書かないでください。
各所見は次の必須項目を持ちます：
- finding_id：P-001 形式の連番
- perspective：観点番号（1〜5）
- severity：CRITICAL / ERROR / WARN / INFO のいずれか
- target_location：ファイル名と節／行／識別子など具体的な箇所
- description：所見の内容（何が問題か、簡潔に2〜3文）
- rationale：根拠（どの文書のどこと矛盾するか、簡潔に2〜3文）
所見が無ければ findings: [] とします。出力は YAML として解析可能であること。
"""

ADVERSARIAL_INSTRUCTION = """# 役割：敵対役レビュアー（adversarial reviewer）

あなたは runtime 機能の実装に対する敵対役レビュアーです。下記の主役所見を1件ずつ検証し
（同意するか、反証を挙げて覆すか）、さらに主役が見落とした所見を独立に発見してください。
主役の判断に引きずられず、反対の立場から厳しく検証してください。

{perspectives}

# 主役の所見（検証対象）
{primary_findings}

# 出力形式（厳守）
findings を含む YAML だけを返してください。説明文・前置きは書かないでください。
- 主役所見の検証：各 finding_id（P-xxx）について verdict（agree / refute）と reason（2〜3文）
- 独立発見：finding_id を A-001 形式とし、perspective／severity／target_location／description／rationale
構造例：
findings:
  - finding_id: P-001
    verdict: refute
    reason: ...
  - finding_id: A-001
    perspective: 3
    severity: ERROR
    target_location: ...
    description: ...
    rationale: ...
出力は YAML として解析可能であること。
"""

JUDGMENT_INSTRUCTION = """# 役割：判定役レビュアー（judgment reviewer）

あなたは runtime 機能の実装に対する判定役です。主役と敵対役の全所見を精査し、各所見に
対応優先度（judgment）と波及種別（waveband）を判定してください。敵対役の反証が正当なら
主役所見を覆して構いません。判断は実装・テスト・上流文書の事実に基づいてください。

{perspectives}

# 対応優先度（judgment）の語彙
- must-fix：仕様の致命的または重要な欠落、修正必須
- should-fix：改善余地、修正推奨
- leave-as-is：問題なし、修正不要

# 波及種別（waveband）の語彙（運営ガイド §3.2）
- in_feature：当該機能（runtime）の修正のみで完結（機能内対処）
- cross_feature：同フェーズ内の他機能の仕様修正も必要（波及）
- upstream：上流フェーズ（requirements／design／tasks）の修正が必要（遡及）
- leave-as-is：修正不要
- deferred：将来フェーズで対処（延期）

# 主役の所見
{primary_findings}

# 敵対役の所見
{adversarial_findings}

# 出力形式（厳守）
findings を含む YAML だけを返してください。説明文・前置きは書かないでください。
主役 P-xxx・敵対役 A-xxx の全件について：
- finding_id
- judgment：must-fix / should-fix / leave-as-is
- waveband：in_feature / cross_feature / upstream / leave-as-is / deferred
- rationale：判定根拠（2〜3文）
構造例：
findings:
  - finding_id: P-001
    judgment: must-fix
    waveband: in_feature
    rationale: ...
出力は YAML として解析可能であること。
"""


def build_primary_prompt() -> str:
  return PRIMARY_INSTRUCTION.format(perspectives=PERSPECTIVES) + "\n\n" + build_target_section()


def build_adversarial_prompt(primary_text: str) -> str:
  head = ADVERSARIAL_INSTRUCTION.format(
    perspectives=PERSPECTIVES, primary_findings=primary_text
  )
  return head + "\n\n" + build_target_section()


def build_judgment_prompt(primary_text: str, adversarial_text: str) -> str:
  head = JUDGMENT_INSTRUCTION.format(
    perspectives=PERSPECTIVES,
    primary_findings=primary_text,
    adversarial_findings=adversarial_text,
  )
  return head + "\n\n" + build_target_section()


def _parse_argv(argv: Optional[List[str]]) -> argparse.Namespace:
  parser = argparse.ArgumentParser(
    description="runtime implementation triad-review のプロンプト生成（一時）"
  )
  parser.add_argument("--role", required=True, choices=["primary", "adversarial", "judgment"])
  parser.add_argument("--prior-primary", default=None, help="主役応答 YAML パス")
  parser.add_argument("--prior-adversarial", default=None, help="敵対役応答 YAML パス")
  parser.add_argument("--out", required=True, help="出力プロンプトファイルパス")
  return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
  args = _parse_argv(argv)
  try:
    if args.role == "primary":
      prompt = build_primary_prompt()
    elif args.role == "adversarial":
      if not args.prior_primary:
        raise ValueError("--prior-primary が必要です")
      prompt = build_adversarial_prompt(read_response_text(args.prior_primary))
    else:  # judgment
      if not (args.prior_primary and args.prior_adversarial):
        raise ValueError("--prior-primary と --prior-adversarial が必要です")
      prompt = build_judgment_prompt(
        read_response_text(args.prior_primary),
        read_response_text(args.prior_adversarial),
      )
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(prompt, encoding="utf-8")
    sys.stdout.write(f"wrote {args.out} ({len(prompt)} chars)\n")
    return 0
  except Exception as exc:
    sys.stderr.write(f"エラー：{type(exc).__name__}: {exc}\n")
    return 1


if __name__ == "__main__":
  sys.exit(main())
