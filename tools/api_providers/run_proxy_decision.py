"""proxy_model 判定を正式 API provider 経路で実行する entrypoint。

実験用スクリプトを経由せず、config/api-settings.yaml の single-role variant を使って
proxy_model の raw response / parsed decisions / metadata を review-run 配下へ記録する。
"""
import argparse
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

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
from tools.api_providers.external_api_approval import (  # noqa: E402
  validate_external_api_approval,
)
from tools.api_providers.providers import (  # noqa: E402
  enable_zshrc_api_key_fallback,
  get_provider,
)
from tools.normal_output import status_line  # noqa: E402


def _parse_argv(argv: Optional[List[str]]) -> argparse.Namespace:
  parser = argparse.ArgumentParser(
    description="proxy_model 判定を正式 API provider 経路で実行する。",
  )
  parser.add_argument("--variant", default="proxy_model_openai_gpt_55")
  parser.add_argument("--prompt-file", required=True)
  parser.add_argument("--review-run-dir", required=True)
  parser.add_argument("--config", default="config/api-settings.yaml")
  parser.add_argument("--raw-out", default="proxy-decision-response.yaml")
  parser.add_argument("--parsed-out", default="proxy-decision-decisions.yaml")
  parser.add_argument("--metadata-out", default="proxy-decision-metadata.yaml")
  parser.add_argument(
    "--external-approval-record",
    help="外部 API 送信用の利用者承認レコード。指定時は送信前に provider/model/prompt/material を検査する。",
  )
  parser.add_argument("--verbose", action="store_true")
  return parser.parse_args(argv)


def _dump_yaml(path: Path, data: Dict[str, Any]) -> None:
  path.parent.mkdir(parents=True, exist_ok=True)
  path.write_text(
    yaml.safe_dump(data, allow_unicode=True, sort_keys=False),
    encoding="utf-8",
  )


def _read_prompt(path: Path) -> str:
  return path.read_text(encoding="utf-8")


def _validate_variant(variant_name: str, variant_config: Dict[str, Any]) -> None:
  if variant_config.get("variant_type") != "single_role":
    raise ValueError(f"proxy_model variant must be single_role: {variant_name}")
  required_roles = variant_config.get("required_roles")
  if required_roles != ["primary"]:
    raise ValueError(f"proxy_model variant must require only primary: {variant_name}")
  primary = resolve_role(variant_config, "primary")
  if primary.get("path") != "api":
    raise ValueError(f"proxy_model primary role must use api path: {variant_name}")


def _parse_decisions(response_text: str) -> Dict[str, Any]:
  data = yaml.safe_load(response_text)
  if not isinstance(data, dict):
    raise ValueError("proxy_model response must be a YAML mapping")
  if not isinstance(data.get("proxy_model_id"), str):
    raise ValueError("proxy_model response must contain proxy_model_id")
  if "decisions" in data and not isinstance(data.get("decisions"), list):
    raise ValueError("proxy_model response decisions must be a list when present")
  return data


def _relative_name(path: Path) -> str:
  return path.name


def main(argv: Optional[List[str]] = None) -> int:
  enable_zshrc_api_key_fallback()
  args = _parse_argv(argv)
  try:
    config = load_config(args.config)
    variant_config = resolve_variant(config, args.variant)
    _validate_variant(args.variant, variant_config)
    role_config = resolve_role(variant_config, "primary")
    connection_settings = resolve_connection_settings(
      role_config,
      config.get("connection", {}),
    )

    provider_name = role_config["provider"]
    model = role_config["model"]
    prompt_path = Path(args.prompt_file)
    prompt = _read_prompt(prompt_path)
    external_approval_record = None
    if args.external_approval_record:
      external_approval_record = validate_external_api_approval(
        args.external_approval_record,
        prompt_path=str(prompt_path),
        provider=provider_name,
        model=model,
        purpose="proxy_model_decision",
        prompt_text=prompt,
      )
    provider_cls = get_provider(provider_name)
    provider = provider_cls(
      model=model,
      timeout_seconds=connection_settings.get("timeout_seconds", 60),
      max_retries=connection_settings.get("max_retries", 1),
    )

    run_dir = Path(args.review_run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    raw_path = run_dir / args.raw_out
    parsed_path = run_dir / args.parsed_out
    metadata_path = run_dir / args.metadata_out

    start = time.monotonic()
    response_text = provider.send_messages([{"role": "user", "content": prompt}])
    duration_seconds = round(time.monotonic() - start, 3)
    raw_path.write_text(response_text, encoding="utf-8")

    metadata = {
      "variant": args.variant,
      "provider": provider_name,
      "model": model,
      "prompt_path": str(prompt_path),
      "raw_response_path": _relative_name(raw_path),
      "parsed_decisions_path": _relative_name(parsed_path),
      "duration_seconds": duration_seconds,
    }
    if external_approval_record is not None:
      metadata["external_approval_record_path"] = args.external_approval_record
      metadata["external_approval_record_schema_version"] = external_approval_record.get(
        "schema_version"
      )

    try:
      parsed = _parse_decisions(response_text)
    except Exception:
      metadata["parse_status"] = "parse_failed"
      _dump_yaml(metadata_path, metadata)
      raise

    _dump_yaml(parsed_path, parsed)
    metadata["parse_status"] = "parsed"
    _dump_yaml(metadata_path, metadata)

    fields = {
      "review_run_dir": args.review_run_dir,
      "provider": provider_name,
      "model": model,
      "raw": str(raw_path),
      "parsed": str(parsed_path),
    }
    if args.verbose:
      sys.stdout.write(yaml.safe_dump(metadata, allow_unicode=True, sort_keys=False))
    else:
      sys.stdout.write(status_line("OK", "run_proxy_decision", fields))
    return 0
  except Exception as exc:
    sys.stderr.write(f"エラー：{type(exc).__name__}: {exc}\n")
    return 1


if __name__ == "__main__":
  sys.exit(main())
