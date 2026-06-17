"""tools/api_providers/run_role.py

API 経路で 1 役を 1 回実行し、結果を標準出力に YAML で返す。
任意指定の出力先がある場合は raw / parsed / review-run 成果物も保存する。
計画書 §5.9.7.1（入出力契約）と §5.23.12.3（プロンプト雛形はフェーズ 4 で整備）を参照。
"""
import argparse
import hashlib
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# 直接実行（python3 tools/api_providers/run_role.py）にも import 経由にも対応する。
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
  sys.path.insert(0, str(_PROJECT_ROOT))

import yaml  # noqa: E402

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


_PROMPT_TEMPLATE_DIR = Path(__file__).resolve().parent / "prompt_templates"
_PROVIDER_PROMPT_TEMPLATES = {
  "anthropic-api": "anthropic_review.md",
  "openai-api": "openai_review.md",
  "gemini-api": "gemini_review.md",
}


def _render_prompt_template(template: str, values: Dict[str, str]) -> str:
  """元テンプレート上の placeholder だけを 1 回置換する。"""
  pattern = re.compile(r"{{\s*([A-Za-z_][A-Za-z0-9_]*)\s*}}")

  def replace(match: re.Match) -> str:
    key = match.group(1)
    return values.get(key, match.group(0))

  return pattern.sub(replace, template)


def _select_prompt_template(provider_name: Optional[str]) -> Tuple[str, str]:
  """provider に応じたプロンプトテンプレート ID と本文を返す。"""
  template_file = _PROVIDER_PROMPT_TEMPLATES.get(
    provider_name or "",
    "default_review.md",
  )
  template_path = _PROMPT_TEMPLATE_DIR / template_file
  if not template_path.exists():
    template_file = "default_review.md"
    template_path = _PROMPT_TEMPLATE_DIR / template_file
  return template_file.removesuffix(".md"), template_path.read_text(encoding="utf-8")


def build_prompt(
  target_path: str,
  phase: str,
  criteria: str,
  prior_finding_paths: List[str],
  provider_name: Optional[str] = None,
  model: Optional[str] = None,
) -> str:
  """対象ファイル内容・段名・観点・前段所見からプロンプト文字列を組み立てる。

  provider ごとの差異を吸収するため、専用テンプレートがあればそれを使う。
  """
  target_content = Path(target_path).read_text(encoding="utf-8")
  prior_parts = []
  for i, prior_path in enumerate(prior_finding_paths, start=1):
    prior_content = Path(prior_path).read_text(encoding="utf-8")
    prior_parts.append(f"# 前段所見 {i}：\n{prior_content}")

  prompt_id, template = _select_prompt_template(provider_name)
  return _render_prompt_template(
    template,
    {
      "prompt_id": prompt_id,
      "provider_name": provider_name or "unknown-provider",
      "model": model or "unknown-model",
      "phase": phase,
      "criteria": criteria,
      "target_path": target_path,
      "target_content": target_content,
      "prior_findings": "\n\n".join(prior_parts) if prior_parts else "なし",
    },
  )


def _call_provider(provider, prompt: str) -> Tuple[str, int, float]:
  """プロバイダーを呼び出し、レスポンス文字列・attempts・所要時間を返す。

  send_request 内部のリトライは内側で処理されるため、本層では attempts=1 と記録する。
  詳細な attempts 計測はサブサイクル 4 完成後の改良対象。
  """
  start = time.monotonic()
  response_text = provider.send_request(prompt)
  duration = time.monotonic() - start
  return response_text, 1, duration


def _sha256_text(value: str) -> str:
  """文字列の sha256 を返す。"""
  return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _sha256_file(path: Path) -> str:
  """ファイル内容の sha256 を返す。"""
  return hashlib.sha256(path.read_bytes()).hexdigest()


def _write_text(path: Path, content: str) -> None:
  """親ディレクトリを作って UTF-8 テキストを書き込む。"""
  path.parent.mkdir(parents=True, exist_ok=True)
  path.write_text(content, encoding="utf-8")


def _load_yaml_dict(path: Path) -> Dict[str, Any]:
  """YAML dict を読み込む。存在しない場合は空 dict。"""
  if not path.exists():
    return {}
  data = yaml.safe_load(path.read_text(encoding="utf-8"))
  return data if isinstance(data, dict) else {}


def _dump_yaml(path: Path, data: Dict[str, Any]) -> None:
  """YAML dict を UTF-8 で書き込む。"""
  path.parent.mkdir(parents=True, exist_ok=True)
  path.write_text(
    yaml.safe_dump(data, allow_unicode=True, sort_keys=False),
    encoding="utf-8",
  )


def _safe_artifact_stem(model: str) -> str:
  """モデル ID を artifact ファイル名に使える最小表記へ変換する。"""
  safe_chars = []
  for char in model:
    if char.isalnum() or char in (".", "-", "_"):
      safe_chars.append(char)
    else:
      safe_chars.append("-")
  return "".join(safe_chars).strip("-") or "model"


def _write_raw_response(raw_out: Optional[str], response_text: str) -> Optional[str]:
  """明示 raw-out があれば provider 生応答を保存し sha256 を返す。"""
  if not raw_out:
    return None
  path = Path(raw_out)
  _write_text(path, response_text)
  return _sha256_file(path)


def _write_parsed_response(parsed_out: Optional[str], formatted_output: str) -> Optional[str]:
  """明示 parsed-out があれば整形済み YAML を保存し sha256 を返す。"""
  if not parsed_out:
    return None
  path = Path(parsed_out)
  _write_text(path, formatted_output)
  return _sha256_file(path)


def _relative_to_run(run_dir: Path, path: Path) -> str:
  """review-run ディレクトリからの相対パスを返す。"""
  try:
    return str(path.relative_to(run_dir))
  except ValueError:
    return str(path)


def _severity_counts(findings: Optional[List[Dict[str, Any]]]) -> Dict[str, int]:
  """所見重大度ごとの件数を返す。"""
  counts: Dict[str, int] = {}
  for finding in findings or []:
    if not isinstance(finding, dict):
      continue
    severity = finding.get("severity") or "UNKNOWN"
    counts[str(severity)] = counts.get(str(severity), 0) + 1
  return counts


def _upsert_by_keys(items: List[Dict[str, Any]], new_item: Dict[str, Any], keys: List[str]) -> None:
  """keys が一致する既存 dict を置き換え、なければ追加する。"""
  for index, item in enumerate(items):
    if all(item.get(key) == new_item.get(key) for key in keys):
      items[index] = new_item
      return
  items.append(new_item)


def update_review_run_artifacts(
  review_run_dir: str,
  *,
  round_id: str,
  target_path: str,
  phase: str,
  criteria: str,
  role: str,
  provider: str,
  model: str,
  prompt: str,
  response_text: str,
  attempts: int,
  duration_seconds: float,
  parse_status: str,
  findings: Optional[List[Dict[str, Any]]],
  formatted_output: Optional[str],
  effective_prompt_path: Optional[str] = None,
  effective_prompt_sha256: Optional[str] = None,
) -> None:
  """1 回の API 応答を review-run 成果物へ反映する。"""
  run_dir = Path(review_run_dir)
  raw_dir = run_dir / "raw"
  parsed_dir = run_dir / "parsed"
  model_stem = _safe_artifact_stem(model)
  raw_path = raw_dir / f"{model_stem}.{round_id}.txt"
  parsed_path = parsed_dir / f"{model_stem}.{round_id}.yaml"

  _write_text(raw_path, response_text)
  raw_sha256 = _sha256_file(raw_path)
  parsed_sha256 = None
  if formatted_output is not None:
    _write_text(parsed_path, formatted_output)
    parsed_sha256 = _sha256_file(parsed_path)

  target_file = Path(target_path)
  target_sha256 = _sha256_file(target_file)
  now = datetime.now(timezone.utc).isoformat()

  _dump_yaml(
    run_dir / "target-manifest.yaml",
    {
      "run_id": run_dir.name,
      "target_files": [
        {
          "path": target_path,
          "sha256": target_sha256,
        },
      ],
    },
  )

  rounds_path = run_dir / "rounds.yaml"
  rounds = _load_yaml_dict(rounds_path)
  model_results = rounds.get("model_results")
  if not isinstance(model_results, list):
    model_results = []

  model_result = {
    "model_id": model,
    "provider": provider,
    "role": role,
    "treatment": role,
    "invocation_path": "api",
    "raw_path": _relative_to_run(run_dir, raw_path),
    "raw_sha256": raw_sha256,
    "parsed_path": _relative_to_run(run_dir, parsed_path) if formatted_output is not None else None,
    "parsed_sha256": parsed_sha256,
    "parse_status": parse_status,
    "formatted_by": "parser",
    "formatted_by_actor_type": "orchestrator",
    "formatted_by_actor": "run_role.py",
    "formatted_at": now,
    "follow_up_action": "triage" if parse_status == "parsed" else "format_pending",
    "attempts": attempts,
    "duration_seconds": round(duration_seconds, 3),
  }
  _upsert_by_keys(model_results, model_result, ["model_id", "role"])

  rounds_update = {
    "round_id": round_id,
    "purpose": phase,
    "invocation_timestamp": now,
    "target_files": [
      {
        "path": target_path,
        "sha256": target_sha256,
      },
    ],
    "criteria": criteria,
    "prompt_sha256": _sha256_text(prompt),
    "model_results": model_results,
  }
  if effective_prompt_path:
    rounds_update["effective_prompt_path"] = effective_prompt_path
  if effective_prompt_sha256:
    rounds_update["effective_prompt_sha256"] = effective_prompt_sha256
  rounds.update(rounds_update)
  _dump_yaml(rounds_path, rounds)

  summary_path = run_dir / "model-result-summary.yaml"
  summary = _load_yaml_dict(summary_path)
  summary_models = summary.get("models")
  if not isinstance(summary_models, list):
    summary_models = []
  findings_count = len(findings or [])
  summary_model = {
    "model_id": model,
    "raw_path": _relative_to_run(run_dir, raw_path),
    "parse_status": parse_status,
    "triage_status": "no_findings" if parse_status == "parsed" and findings_count == 0 else "triage_pending",
    "findings_count": findings_count,
    "findings_count_by_severity": _severity_counts(findings),
    "must_fix_count": 0,
    "should_fix_count": 0,
    "leave_as_is_count": 0,
    "human_required_count": 0,
  }
  _upsert_by_keys(summary_models, summary_model, ["model_id"])
  summary.update({
    "run_id": run_dir.name,
    "models": summary_models,
  })
  _dump_yaml(summary_path, summary)


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
  parser.add_argument(
    "--raw-out",
    default=None,
    help="provider 生応答の保存先。parse 成否に関係なく保存する",
  )
  parser.add_argument(
    "--parsed-out",
    default=None,
    help="整形済み YAML の保存先。parse 成功時のみ保存する",
  )
  parser.add_argument(
    "--review-run-dir",
    default=None,
    help="review-run 成果物ディレクトリ。raw/parsed/rounds/summary を更新する",
  )
  parser.add_argument(
    "--round-id",
    default="round-1",
    help="review-run に記録する round_id",
  )
  parser.add_argument(
    "--effective-prompt-path",
    default=None,
    help="判定点ごとに生成された effective prompt ファイルのパス",
  )
  parser.add_argument(
    "--effective-prompt-sha256",
    default=None,
    help="effective prompt ファイルの sha256。未指定ならファイルから計算する",
  )
  return parser.parse_args(argv)


def _resolve_effective_prompt_sha256(path_value: Optional[str], sha_value: Optional[str]) -> Optional[str]:
  """effective prompt sha256 を明示値またはファイル内容から返す。

  凍結期（P3 まで）は読み取りを新→旧の順でフォールバックする
  （正本は check_workflow_action/runtime_paths.py）。
  """
  if sha_value:
    return sha_value
  if not path_value:
    return None
  from tools.check_workflow_action.runtime_paths import resolve_effective_prompt_read_path

  resolved = resolve_effective_prompt_read_path(Path.cwd(), path_value)
  path = Path(resolved)
  if not path.is_file():
    return None
  return _sha256_file(path)


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

    prompt = build_prompt(
      args.target,
      args.phase,
      args.criteria,
      args.prior_finding,
      provider_name=provider_name,
      model=model,
    )
    effective_prompt_sha256 = _resolve_effective_prompt_sha256(
      args.effective_prompt_path,
      args.effective_prompt_sha256,
    )
    response_text, attempts, duration_seconds = _call_provider(provider, prompt)
    _write_raw_response(args.raw_out, response_text)
    try:
      findings = parse_response_text(response_text)
    except Exception:
      if args.review_run_dir:
        update_review_run_artifacts(
          args.review_run_dir,
          round_id=args.round_id,
          target_path=args.target,
          phase=args.phase,
          criteria=args.criteria,
          role=args.role,
          provider=provider_name,
          model=model,
          prompt=prompt,
          response_text=response_text,
          attempts=attempts,
          duration_seconds=duration_seconds,
          parse_status="parse_failed",
          findings=None,
          formatted_output=None,
          effective_prompt_path=args.effective_prompt_path,
          effective_prompt_sha256=effective_prompt_sha256,
        )
      raise
    output = format_response(
      role=args.role,
      provider=provider_name,
      model=model,
      attempts=attempts,
      duration_seconds=round(duration_seconds, 3),
      findings=findings,
    )
    _write_parsed_response(args.parsed_out, output)
    if args.review_run_dir:
      update_review_run_artifacts(
        args.review_run_dir,
        round_id=args.round_id,
        target_path=args.target,
        phase=args.phase,
        criteria=args.criteria,
        role=args.role,
        provider=provider_name,
        model=model,
        prompt=prompt,
        response_text=response_text,
        attempts=attempts,
        duration_seconds=duration_seconds,
        parse_status="parsed",
        findings=findings,
        formatted_output=output,
        effective_prompt_path=args.effective_prompt_path,
        effective_prompt_sha256=effective_prompt_sha256,
      )
    sys.stdout.write(output)
    return 0
  except Exception as exc:
    sys.stderr.write(f"エラー：{type(exc).__name__}: {exc}\n")
    return 1


if __name__ == "__main__":
  sys.exit(main())
