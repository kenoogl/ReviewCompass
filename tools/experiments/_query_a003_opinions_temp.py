"""A-003 対処方針について 3 モデルに意見を聞く一時スクリプト。

実行：
  zsh -c 'source ~/.zshrc && /Users/Daily/Development/ReviewCompass/.venv/bin/python3 \
    tools/experiments/_query_a003_opinions_temp.py'

§0.4 実験意識：推奨案は伏せ、3 案を対称的に提示してバイアスを最小化する。
"""
import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
  sys.path.insert(0, str(_PROJECT_ROOT))

from tools.api_providers.providers import get_provider  # noqa: E402

PROMPT = """\
あなたはソフトウェア仕様レビューの専門家です。ReviewCompass というプロジェクトの
仕様文書間の不整合（所見 A-003）について、中立的に意見を述べてください。

## 背景

ReviewCompass は 7 機能（foundation／runtime／evaluation／analysis／workflow-management／
self-improvement／conformance-evaluation）から成る。foundation 機能が共通の語彙正本
（状態・分類の語彙の正式定義）を所有し、他機能は再定義せず参照する規約である。

workflow-management 機能（所定手続きの定義と機械強制を担う）の仕様文書 3 種
（requirements.md／design.md／tasks.md）の間で、「foundation のどの語彙を参照するか」の
記述が食い違っている（所見 A-003）。

## 事実

foundation は 2 種類の語彙群を持つ：
- 状態軸 4 件：run_status（実行ライフサイクル）／validator_status（検証結果）／
  human_signoff_status（承認状態）／evidence_class（証拠区分）
- 語彙正本 7 件（下流は再定義禁止）：counter_status／validator_status／evidence_class／
  review_mode／severity／final_label／confidence_label
（両者で重なるのは validator_status と evidence_class の 2 件のみ。単純な新旧の置換ではない）

3 文書の現状：
- requirements.md：「状態軸語彙」4 件を参照、と記述
- design.md：「状態軸の語彙（run_status／validator_status 等）」と記述（4 件側の枠組み）
- tasks.md：「語彙正本」7 件を参照、と記述

さらに重要な事実：foundation の design.md は、workflow-management を多くの語彙の
「再定義禁止対象」から明示的に除外している（例：severity には「workflow-management は
所見の重大度を直接扱わないため参照禁止対象に含めない」と明記）。workflow-management が
実際に foundation から読むのは、レビュー記録の冒頭メタデータにある review_mode
（レビュー方式の語彙）程度で、所見（finding）や実行ライフサイクルは扱わない。

## 候補案

- 案ア：requirements.md を tasks.md と同じ「語彙正本 7 件」に統一する
- 案イ：workflow-management が実際に参照する最小集合（review_mode 中心）に 3 文書を統一する
- 案ウ：「foundation の語彙正本を再定義せず参照する」とだけ書き、具体的な列挙をやめる

## 質問

案ア・イ・ウのどれが最も適切か、理由とともに述べてください。3 案以外に良い案があれば
それも提案してください。回答は簡潔に、次の順で：（1）推奨案 （2）理由 （3）後段（下流の
設計・実装・機械検証）への影響。
"""

MODELS = [
  ("anthropic-api", "claude-opus-4-7", "opus-4.7"),
  ("openai-api", "gpt-5.5", "gpt-5.5"),
  ("gemini-api", "gemini-3.5-flash", "gemini-3.5-flash"),
]


def main():
  for provider_name, model, label in MODELS:
    print("=" * 70)
    print(f"### {label}（{provider_name} / {model}）")
    print("=" * 70)
    try:
      provider_cls = get_provider(provider_name)
      provider = provider_cls(model=model, timeout_seconds=120, max_retries=1)
      response = provider.send_request(PROMPT)
      print(response)
    except Exception as exc:
      print(f"[エラー] {type(exc).__name__}: {exc}")
    print()


if __name__ == "__main__":
  main()
