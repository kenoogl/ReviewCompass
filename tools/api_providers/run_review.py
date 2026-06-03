"""tools/api_providers/run_review.py

複数 role を同じ review-run ディレクトリへ集約して実行する薄い orchestrator。
raw / parsed / rounds / summary の生成は run_role.py の成果物関数を再利用する。
"""
import argparse
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

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
from tools.api_providers.run_role import (  # noqa: E402
  build_prompt,
  update_review_run_artifacts,
)

ROLES = ["primary", "adversarial", "judgment"]
NORMALIZED_SEVERITY = {"CRITICAL", "ERROR", "WARN", "INFO"}


def _load_yaml_dict(path: Path) -> Dict[str, Any]:
  if not path.exists():
    return {}
  data = yaml.safe_load(path.read_text(encoding="utf-8"))
  return data if isinstance(data, dict) else {}


def _dump_yaml(path: Path, data: Dict[str, Any]) -> None:
  path.parent.mkdir(parents=True, exist_ok=True)
  path.write_text(
    yaml.safe_dump(data, allow_unicode=True, sort_keys=False),
    encoding="utf-8",
  )


def _call_provider(provider, prompt: str) -> Tuple[str, int, float]:
  start = time.monotonic()
  response_text = provider.send_request(prompt)
  return response_text, 1, time.monotonic() - start


def _normalize_severity(value: Any) -> str:
  severity = str(value or "INFO").upper()
  return severity if severity in NORMALIZED_SEVERITY else "INFO"


def _load_parsed_findings(review_run_dir: Path, parsed_path: Optional[str]) -> List[Dict[str, Any]]:
  if not parsed_path:
    return []
  parsed_file = review_run_dir / parsed_path
  data = _load_yaml_dict(parsed_file)
  findings = data.get("findings")
  return findings if isinstance(findings, list) else []


def initialize_triage_draft(review_run_dir: str) -> None:
  """parsed findings から human_required の triage 下書きを生成する。"""
  run_dir = Path(review_run_dir)
  rounds = _load_yaml_dict(run_dir / "rounds.yaml")
  model_results = rounds.get("model_results")
  if not isinstance(model_results, list):
    model_results = []

  now = datetime.now(timezone.utc).isoformat()
  items: List[Dict[str, Any]] = []
  for model_result in model_results:
    if not isinstance(model_result, dict):
      continue
    if model_result.get("parse_status") != "parsed":
      continue
    findings = _load_parsed_findings(run_dir, model_result.get("parsed_path"))
    for index, finding in enumerate(findings, start=1):
      if not isinstance(finding, dict):
        continue
      severity_original = finding.get("severity", "INFO")
      items.append({
        "finding_id": (
          f"{run_dir.name}-{model_result.get('model_id')}-"
          f"{model_result.get('role')}-{index:03d}"
        ),
        "run_id": run_dir.name,
        "source_model": model_result.get("model_id"),
        "source_round": rounds.get("round_id"),
        "source_raw_path": model_result.get("raw_path"),
        "source_parsed_path": model_result.get("parsed_path"),
        "severity_original": severity_original,
        "severity_normalized": _normalize_severity(severity_original),
        "target_location": finding.get("target_location"),
        "plain_language_summary": finding.get("description"),
        "final_label": None,
        "decision_status": "human_required",
        "decision_actor": None,
        "decision_actor_type": "human",
        "decision_at": None,
        "decision_reason": finding.get("rationale"),
        "applied_files": [],
        "superseded_by": None,
      })

  _dump_yaml(
    run_dir / "triage.yaml",
    {
      "run_id": run_dir.name,
      "triage_status": "draft",
      "generated_at": now,
      "decision_actor": None,
      "decision_actor_type": "human",
      "items": items,
    },
  )


def write_review_summary_markdown(review_run_dir: str) -> str:
  """model-result-summary.yaml からユーザ提示用 Markdown を生成する。"""
  run_dir = Path(review_run_dir)
  summary = _load_yaml_dict(run_dir / "model-result-summary.yaml")
  models = summary.get("models")
  if not isinstance(models, list):
    models = []

  lines = [
    f"# Review run summary: {run_dir.name}",
    "",
    "| model_id | parse_status | triage_status | findings | severity | raw |",
    "| --- | --- | --- | ---: | --- | --- |",
  ]
  for item in models:
    if not isinstance(item, dict):
      continue
    severity_counts = item.get("findings_count_by_severity") or {}
    severity_text = ", ".join(
      f"{key}:{value}" for key, value in sorted(severity_counts.items())
    )
    lines.append(
      "| {model_id} | {parse_status} | {triage_status} | {findings_count} | {severity} | {raw_path} |".format(
        model_id=item.get("model_id"),
        parse_status=item.get("parse_status"),
        triage_status=item.get("triage_status"),
        findings_count=item.get("findings_count", 0),
        severity=severity_text or "-",
        raw_path=item.get("raw_path"),
      )
    )
  lines.extend([
    "",
    "## Next steps",
    "",
    "1. Read raw responses for any parse_failed or triage_pending model.",
    "2. Move finding-level judgments into triage.yaml.",
    "3. Resolve human_required items before treating the run as complete.",
  ])
  content = "\n".join(lines) + "\n"
  (run_dir / "review_summary.md").write_text(content, encoding="utf-8")
  return content


def _parse_argv(argv: Optional[List[str]]) -> argparse.Namespace:
  parser = argparse.ArgumentParser(
    description="3 role API review を同じ review-run に集約して実行する。",
  )
  parser.add_argument("--variant", default=None, help="variant 名。未指定なら default")
  parser.add_argument("--target", required=True, help="対象文書ファイルパス")
  parser.add_argument("--phase", required=True, help="段名")
  parser.add_argument("--criteria", required=True, help="観点識別子")
  parser.add_argument("--review-run-dir", required=True, help="review-run 成果物ディレクトリ")
  parser.add_argument("--round-id", default="round-1", help="round ID")
  parser.add_argument("--config", default="config/api-settings.yaml", help="API 設定ファイル")
  parser.add_argument(
    "--prior-finding",
    action="append",
    default=[],
    help="前段役の所見ファイルパス（複数指定可）",
  )
  return parser.parse_args(argv)


def _run_one_role(args, config: Dict[str, Any], role: str) -> int:
  """1 role を実行して review-run 成果物へ反映する。"""
  variant_name = None if args.variant == "default" else args.variant
  variant_config = resolve_variant(config, variant_name)
  role_config = resolve_role(variant_config, role)
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
  try:
    findings = parse_response_text(response_text)
  except Exception:
    update_review_run_artifacts(
      args.review_run_dir,
      round_id=args.round_id,
      target_path=args.target,
      phase=args.phase,
      criteria=args.criteria,
      role=role,
      provider=provider_name,
      model=model,
      prompt=prompt,
      response_text=response_text,
      attempts=attempts,
      duration_seconds=duration_seconds,
      parse_status="parse_failed",
      findings=None,
      formatted_output=None,
    )
    return 1

  output = format_response(
    role=role,
    provider=provider_name,
    model=model,
    attempts=attempts,
    duration_seconds=round(duration_seconds, 3),
    findings=findings,
  )
  update_review_run_artifacts(
    args.review_run_dir,
    round_id=args.round_id,
    target_path=args.target,
    phase=args.phase,
    criteria=args.criteria,
    role=role,
    provider=provider_name,
    model=model,
    prompt=prompt,
    response_text=response_text,
    attempts=attempts,
    duration_seconds=duration_seconds,
    parse_status="parsed",
    findings=findings,
    formatted_output=output,
  )
  return 0


def main(argv: Optional[List[str]] = None) -> int:
  args = _parse_argv(argv)
  exit_code = 0
  try:
    config = load_config(args.config)
    for role in ROLES:
      role_exit_code = _run_one_role(args, config, role)
      if role_exit_code != 0:
        exit_code = 1
    initialize_triage_draft(args.review_run_dir)
    summary_markdown = write_review_summary_markdown(args.review_run_dir)
    sys.stdout.write(summary_markdown)
    return exit_code
  except Exception as exc:
    sys.stderr.write(f"エラー：{type(exc).__name__}: {exc}\n")
    return 1


if __name__ == "__main__":
  sys.exit(main())
