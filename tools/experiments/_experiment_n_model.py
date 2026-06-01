"""tools/experiments/_experiment_n_model.py

7 モデル比較実験用の一時スクリプト（マルチターン対応）。
セッション 31（2026-05-27）の 7 モデル比較実験で使用、後で削除予定。
関連実験ノート：docs/experiments/n-model-comparison.md
利用者明示承認「はい」（推奨案の組み合わせ採用、セッション 31）。

スクリプト仕様：
- 責務範囲：対話履歴管理を含む（案 Q）
- 出力形式：標準出力に YAML（案 b）
- 保存先：tools/experiments/_experiment_n_model.py（案 (ii)）
- 判定者指定：プロバイダー名 ＋ モデル名（案 (β)）

引数：
- --provider <anthropic-api|openai-api|gemini-api>：必須
- --model <モデル名>：必須
- --prompt-file <パス>：必須（1 ターン目のプロンプト本文）
- --history-file <パス>：省略可（前ターンまでの対話履歴 YAML）
- --turn-number <整数>：省略可（既定 1、メタデータ用）
- --timeout-seconds <整数>：省略可（既定 60。GPT-5.5 は 300 を指定すること）

標準出力 YAML 形式：
- provider / model / turn_number / duration_seconds / sent_messages_count / response_text
"""
import argparse
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional

import yaml

# プロジェクトルートを sys.path に追加（直接実行・import 経由の両方に対応）
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
  sys.path.insert(0, str(_PROJECT_ROOT))

from tools.api_providers.providers import get_provider  # noqa: E402


def load_prompt_file(path: str) -> str:
  """指定パスのテキストファイルを UTF-8 で読み込む。"""
  return Path(path).read_text(encoding="utf-8")


def build_messages_from_history(
  prompt: str,
  history_file_path: Optional[str] = None,
) -> List[Dict[str, str]]:
  """履歴ファイル＋新プロンプトから messages 配列を組み立てる。

  履歴ファイルが None の場合は user メッセージ 1 件のみ。
  履歴ファイル指定時は YAML として読み込み、最後に新プロンプト（role: user）を追加。
  履歴が messages のリスト形式でない場合は ValueError。
  """
  if history_file_path is None:
    return [{"role": "user", "content": prompt}]

  history_text = Path(history_file_path).read_text(encoding="utf-8")
  history = yaml.safe_load(history_text)

  if not isinstance(history, list):
    raise ValueError(
      f"履歴ファイル {history_file_path} は messages のリスト形式でなければなりません"
    )

  return list(history) + [{"role": "user", "content": prompt}]


def _parse_argv(argv: Optional[List[str]]) -> argparse.Namespace:
  """引数解析。必須引数欠落時は argparse が SystemExit を投げる。"""
  parser = argparse.ArgumentParser(
    description="7 モデル比較実験用、API 経路で 1 ターンの呼び出しを行う"
  )
  parser.add_argument("--provider", required=True, help="プロバイダー名（anthropic-api／openai-api／gemini-api）")
  parser.add_argument("--model", required=True, help="モデル名")
  parser.add_argument("--prompt-file", required=True, help="プロンプトファイルパス")
  parser.add_argument(
    "--history-file",
    default=None,
    help="対話履歴ファイルパス（YAML 形式、省略時は単発）",
  )
  parser.add_argument(
    "--turn-number",
    type=int,
    default=1,
    help="ターン番号（メタデータ用、既定 1）",
  )
  parser.add_argument(
    "--timeout-seconds",
    type=int,
    default=60,
    help="API タイムアウト秒数（既定 60。GPT-5.5 は 300 を指定すること）",
  )
  return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
  """メイン処理。エラー時は標準エラーに理由を書いて非ゼロを返す。"""
  args = _parse_argv(argv)

  try:
    prompt = load_prompt_file(args.prompt_file)
    messages = build_messages_from_history(prompt, args.history_file)

    provider_cls = get_provider(args.provider)
    provider = provider_cls(model=args.model, timeout_seconds=args.timeout_seconds)

    start = time.monotonic()
    response_text = provider.send_messages(messages)
    duration = time.monotonic() - start

    output = {
      "provider": args.provider,
      "model": args.model,
      "turn_number": args.turn_number,
      "duration_seconds": round(duration, 3),
      "sent_messages_count": len(messages),
      "response_text": response_text,
    }

    sys.stdout.write(yaml.dump(output, allow_unicode=True, sort_keys=False))
    return 0

  except Exception as exc:
    sys.stderr.write(f"エラー：{type(exc).__name__}: {exc}\n")
    return 1


if __name__ == "__main__":
  sys.exit(main())
