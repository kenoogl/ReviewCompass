"""tools/api_providers/run_role.py

API 経路で 1 役を 1 回実行し、結果を標準出力に YAML で返す。
書き込み権限を持たない（ファイル遮断規律、計画書 §5.9.1）。
計画書 §5.9.7.1（入出力契約）と §5.23.12.3（プロンプト雛形はフェーズ 4 で整備）を参照。
"""
import argparse
import sys
import time
from pathlib import Path
from typing import List, Optional, Tuple

# 直接実行（python3 tools/api_providers/run_role.py）にも import 経由にも対応する。
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
  sys.path.insert(0, str(_PROJECT_ROOT))

from tools.api_providers.config_loader import (  # noqa: E402
  load_config,
  resolve_connection_settings,
  resolve_role,
  resolve_variant,
)
from tools.api_providers.providers import get_provider  # noqa: E402
from tools.api_providers.response_formatter import (  # noqa: E402
  format_response,
  parse_response_text,
)


def build_prompt(
  target_path: str,
  phase: str,
  criteria: str,
  prior_finding_paths: List[str],
) -> str:
  """対象ファイル内容・段名・観点・前段所見からプロンプト文字列を組み立てる。

  プロンプト雛形は計画書 §5.23.12.3 のとおりフェーズ 4 で整備する。
  本実装は最小構造（メタデータ＋対象文書＋前段所見）のみ。
  """
  target_content = Path(target_path).read_text(encoding="utf-8")
  parts = [
    f"# 段：{phase}",
    f"# 観点：{criteria}",
    "",
    "# 対象文書：",
    target_content,
  ]
  for i, prior_path in enumerate(prior_finding_paths, start=1):
    prior_content = Path(prior_path).read_text(encoding="utf-8")
    parts.append(f"\n# 前段所見 {i}：")
    parts.append(prior_content)
  parts.append(
    "\n# 出力形式：findings を含む YAML を返してください。"
    "各所見には severity／target_location／description／rationale を必須項目として含めます。"
  )
  return "\n".join(parts)


def _call_provider(provider, prompt: str) -> Tuple[str, int, float]:
  """プロバイダーを呼び出し、レスポンス文字列・attempts・所要時間を返す。

  send_request 内部のリトライは内側で処理されるため、本層では attempts=1 と記録する。
  詳細な attempts 計測はサブサイクル 4 完成後の改良対象。
  """
  start = time.monotonic()
  response_text = provider.send_request(prompt)
  duration = time.monotonic() - start
  return response_text, 1, duration


def _parse_argv(argv: Optional[List[str]]) -> argparse.Namespace:
  """引数解析。計画書 §5.9.7.1 の長オプション 6 種＋ --config に対応。"""
  parser = argparse.ArgumentParser(
    description="API 経路で 1 役を 1 回実行し、結果を標準出力に YAML で返す。",
  )
  parser.add_argument(
    "--role",
    required=True,
    choices=["primary", "adversarial", "judgment"],
    help="役名（必須）",
  )
  parser.add_argument(
    "--variant",
    default=None,
    help="variant 名。未指定なら default を使う",
  )
  parser.add_argument(
    "--target",
    required=True,
    help="対象文書ファイルパス（必須）",
  )
  parser.add_argument(
    "--phase",
    required=True,
    help="段名（例：requirements_triad_review、必須）",
  )
  parser.add_argument(
    "--criteria",
    required=True,
    help="観点識別子（例：観点-1、必須）",
  )
  parser.add_argument(
    "--prior-finding",
    action="append",
    default=[],
    help="前段役の所見ファイルパス（複数指定可）",
  )
  parser.add_argument(
    "--config",
    default="config/api-settings.yaml",
    help="API 設定ファイルパス（既定 config/api-settings.yaml）",
  )
  return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
  """メイン処理。エラー時は標準エラーに理由を書いて非ゼロを返す。"""
  args = _parse_argv(argv)
  try:
    config = load_config(args.config)
    variant_config = resolve_variant(config, args.variant)
    role_config = resolve_role(variant_config, args.role)
    connection_defaults = config.get("connection", {})
    connection_settings = resolve_connection_settings(role_config, connection_defaults)

    provider_name = role_config["provider"]
    model = role_config["model"]
    provider_cls = get_provider(provider_name)
    provider = provider_cls(
      model=model,
      timeout_seconds=connection_settings.get("timeout_seconds", 60),
      max_retries=connection_settings.get("max_retries", 1),
    )

    prompt = build_prompt(args.target, args.phase, args.criteria, args.prior_finding)
    response_text, attempts, duration_seconds = _call_provider(provider, prompt)
    findings = parse_response_text(response_text)
    output = format_response(
      role=args.role,
      provider=provider_name,
      model=model,
      attempts=attempts,
      duration_seconds=round(duration_seconds, 3),
      findings=findings,
    )
    sys.stdout.write(output)
    return 0
  except Exception as exc:
    sys.stderr.write(f"エラー：{type(exc).__name__}: {exc}\n")
    return 1


if __name__ == "__main__":
  sys.exit(main())
