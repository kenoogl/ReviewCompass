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
  _resolve_effective_prompt_sha256,
  _render_prompt_template,
  _select_prompt_template,
  build_prompt,
  update_review_run_artifacts,
)
from tools.check_workflow_action import external_api_approval  # noqa: E402

ROLES = ["primary", "adversarial", "judgment"]
NORMALIZED_SEVERITY = {"CRITICAL", "ERROR", "WARN", "INFO"}
POST_WRITE_DEFAULT_VARIANT = "post_write_verification_google"


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


def write_review_summary_markdown(review_run_dir: str, variant_name: str = "default") -> str:
  """model-result-summary.yaml からユーザ提示用 Markdown を生成する。"""
  run_dir = Path(review_run_dir)
  summary = _load_yaml_dict(run_dir / "model-result-summary.yaml")
  rounds = _load_yaml_dict(run_dir / "rounds.yaml")
  models = summary.get("models")
  if not isinstance(models, list):
    models = []
  model_results = rounds.get("model_results")
  if not isinstance(model_results, list):
    model_results = []

  lines = [
    f"# Review run summary: {run_dir.name}",
    "",
    f"variant: {variant_name}",
    "",
    "## Role assignments",
    "",
    "| role | path | provider | model |",
    "| --- | --- | --- | --- |",
  ]
  for item in model_results:
    if not isinstance(item, dict):
      continue
    lines.append(
      "| {role} | {path} | {provider} | {model} |".format(
        role=item.get("role"),
        path=item.get("invocation_path"),
        provider=item.get("provider"),
        model=item.get("model_id"),
      )
    )
  lines.extend([
    "",
    "## Model results",
    "",
    "| model_id | parse_status | triage_status | findings | severity | raw |",
    "| --- | --- | --- | ---: | --- | --- |",
  ])
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
    "3. Present the variant, role assignments, raw/model summary, same-root clusters, and three-level triage to the user.",
    "4. Stop at the 利用者提示ゲート before asking proxy_model, editing implementation, updating spec.json, or moving phases.",
    "5. Resolve human_required items before treating the run as complete.",
  ])
  content = "\n".join(lines) + "\n"
  (run_dir / "review_summary.md").write_text(content, encoding="utf-8")
  return content


def _parse_argv(argv: Optional[List[str]]) -> argparse.Namespace:
  parser = argparse.ArgumentParser(
    description="3 role API review を同じ review-run に集約して実行する。",
  )
  parser.add_argument("--variant", default=None, help="variant 名。未指定なら default")
  parser.add_argument(
    "--target",
    action="append",
    required=True,
    help="対象文書ファイルパス。複数指定可",
  )
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
  parser.add_argument(
    "--external-api-approval-record",
    default=None,
    help="外部 API 送信承認 record（post_write_verification の API 経路で必須）",
  )
  return parser.parse_args(argv)


def _select_variant_name(args) -> Optional[str]:
  """phase に応じた実効 variant 名を返す。"""
  if args.variant == "default":
    return None
  if args.variant:
    return args.variant
  if args.phase == "post_write_verification":
    return POST_WRITE_DEFAULT_VARIANT
  return None


def _roles_for_variant(variant_config: Dict[str, Any]) -> List[str]:
  """variant の required_roles があればそれを使い、なければ 3 役を使う。"""
  required_roles = variant_config.get("required_roles")
  if isinstance(required_roles, list) and required_roles:
    return [role for role in required_roles if isinstance(role, str)]
  return list(ROLES)


def _target_files(args) -> List[str]:
  return list(args.target or [])


def _target_path_label(target_files: List[str]) -> str:
  if len(target_files) == 1:
    return target_files[0]
  return "multiple:" + ",".join(target_files)


def _build_prompt_for_targets(
  target_files: List[str],
  phase: str,
  criteria: str,
  prior_finding_paths: List[str],
  provider_name: Optional[str] = None,
  model: Optional[str] = None,
) -> str:
  if len(target_files) == 1:
    return build_prompt(
      target_files[0],
      phase,
      criteria,
      prior_finding_paths,
      provider_name=provider_name,
      model=model,
    )
  target_parts = []
  for target_path in target_files:
    target_content = Path(target_path).read_text(encoding="utf-8")
    target_parts.append(f"# FILE: {target_path}\n{target_content}")
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
      "target_path": _target_path_label(target_files),
      "target_content": "\n\n".join(target_parts),
      "prior_findings": "\n\n".join(prior_parts) if prior_parts else "なし",
    },
  )


def _api_review_metadata(
  config: Dict[str, Any],
  variant_name: Optional[str],
  roles: List[str],
) -> Tuple[List[str], List[str], bool]:
  """variant の API role から provider/model 一覧を返す。"""
  variant_config = resolve_variant(config, variant_name)
  providers = []
  models = []
  has_api_role = False
  for role in roles:
    role_config = resolve_role(variant_config, role)
    if role_config.get("path") != "api":
      continue
    has_api_role = True
    providers.append(role_config["provider"])
    models.append(role_config["model"])
  return providers, models, has_api_role


def _validate_external_api_approval_if_needed(
  args,
  config: Dict[str, Any],
  variant_name: Optional[str],
  roles: List[str],
) -> None:
  providers, models, has_api_role = _api_review_metadata(config, variant_name, roles)
  if args.phase != "post_write_verification" or not has_api_role:
    return
  if not args.external_api_approval_record:
    raise RuntimeError(
      "external-api-approval record がありません。"
      "tools/check-workflow-action.py external-api-approval prepare/record で"
      "外部 API 送信承認を作成してください。"
    )
  approval = external_api_approval.load_approval_record(
    args.external_api_approval_record
  )
  expected = {
    "target_files": _target_files(args),
    "phase": args.phase,
    "criteria": args.criteria,
    "variant": variant_name or "default",
    "review_run_dir": args.review_run_dir,
    "providers": providers,
    "models": models,
  }
  errors = external_api_approval.validate(
    _approval_record_cwd(args.external_api_approval_record),
    approval,
    expected,
  )
  if errors:
    raise RuntimeError("external-api-approval record が無効です: " + "; ".join(errors))


def _approval_record_cwd(record_path: str) -> Path:
  path = Path(record_path)
  if not path.is_absolute():
    return Path.cwd()
  parts = path.parts
  suffix = (".reviewcompass", "runtime", "approvals")
  for index in range(0, len(parts) - len(suffix)):
    if parts[index:index + len(suffix)] == suffix:
      return Path(*parts[:index])
  return Path.cwd()


def _run_one_role(
  args,
  config: Dict[str, Any],
  variant_name: Optional[str],
  role: str,
) -> int:
  """1 role を実行して review-run 成果物へ反映する。"""
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

  target_files = _target_files(args)
  prompt = _build_prompt_for_targets(
    target_files,
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
  try:
    findings = parse_response_text(response_text)
  except Exception:
    update_review_run_artifacts(
      args.review_run_dir,
      round_id=args.round_id,
      target_path=_target_path_label(target_files),
      target_files=target_files,
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
      effective_prompt_path=args.effective_prompt_path,
      effective_prompt_sha256=effective_prompt_sha256,
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
    target_path=_target_path_label(target_files),
    target_files=target_files,
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
    effective_prompt_path=args.effective_prompt_path,
    effective_prompt_sha256=effective_prompt_sha256,
  )
  return 0


def main(argv: Optional[List[str]] = None) -> int:
  args = _parse_argv(argv)
  exit_code = 0
  try:
    config = load_config(args.config)
    variant_name = _select_variant_name(args)
    variant_config = resolve_variant(config, variant_name)
    roles = _roles_for_variant(variant_config)
    _validate_external_api_approval_if_needed(args, config, variant_name, roles)
    for role in roles:
      role_exit_code = _run_one_role(args, config, variant_name, role)
      if role_exit_code != 0:
        exit_code = 1
    initialize_triage_draft(args.review_run_dir)
    summary_variant_name = variant_name or "default"
    summary_markdown = write_review_summary_markdown(
      args.review_run_dir,
      summary_variant_name,
    )
    sys.stdout.write(summary_markdown)
    return exit_code
  except Exception as exc:
    sys.stderr.write(f"エラー：{type(exc).__name__}: {exc}\n")
    return 1


if __name__ == "__main__":
  sys.exit(main())
