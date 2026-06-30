"""tools/api_providers/run_review.py

複数 role を同じ review-run ディレクトリへ集約して実行する薄い orchestrator。
raw / parsed / rounds / summary の生成は run_role.py の成果物関数を再利用する。
"""
import argparse
import hashlib
import re
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
  resolve_default_variant_name,
  resolve_role,
  resolve_variant,
)
from tools.api_providers.providers import (  # noqa: E402
  enable_zshrc_api_key_fallback,
  get_provider,
)
from tools.api_providers.response_formatter import (  # noqa: E402
  format_response,
  parse_response_data,
)
from tools.api_providers.run_role import (  # noqa: E402
  _resolve_effective_prompt_sha256,
  _resolve_prompt_manifest_sha256,
  build_prompt,
  update_review_run_artifacts,
)
from tools.check_workflow_action.prompt_audit import (  # noqa: E402
  audit_manifest,
  load_manifest as load_prompt_manifest,
)
from tools.check_workflow_action import commit_unit  # noqa: E402
from tools.normal_output import join_values, status_line  # noqa: E402

ROLES = ["primary", "adversarial", "judgment"]
NORMALIZED_SEVERITY = {"CRITICAL", "ERROR", "WARN", "INFO"}
POST_WRITE_DEFAULT_VARIANT = "post_write_verification_google"
VERTICAL_REVIEW_REQUIRED_FIELDS = [
  "purpose",
  "responsibility_boundaries",
  "acceptance_criteria",
  "forbidden_actions",
  "unresolved_or_design_deferred_items",
  "intended_target_phase_transfer",
]


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


def _sha256_file(path: Path) -> str:
  import hashlib

  return hashlib.sha256(path.read_bytes()).hexdigest()


def _sha256_data(data: Dict[str, Any]) -> str:
  content = yaml.safe_dump(data, allow_unicode=True, sort_keys=False)
  return hashlib.sha256(content.encode("utf-8")).hexdigest()


def _safe_artifact_stem(model: str) -> str:
  safe_chars = []
  for char in model:
    if char.isalnum() or char in (".", "-", "_"):
      safe_chars.append(char)
    else:
      safe_chars.append("-")
  return "".join(safe_chars).strip("-") or "model"


def _relative_output_paths(model: str, round_id: str) -> Dict[str, str]:
  model_stem = _safe_artifact_stem(model)
  return {
    "raw_path": f"raw/{model_stem}.{round_id}.txt",
    "parsed_path": f"parsed/{model_stem}.{round_id}.yaml",
    "prompt_path": f"prompts/{model_stem}.{round_id}.prompt.md",
  }


def _target_file_entries(target_paths: List[str]) -> List[Dict[str, str]]:
  return [
    {
      "path": target_path,
      "sha256": _sha256_file(Path(target_path)),
    }
    for target_path in target_paths
  ]


def write_review_execution_spec(
  *,
  args: argparse.Namespace,
  criteria: str,
  criteria_source_path: Optional[str],
  criteria_source_sha256: Optional[str],
  variant_name: Optional[str],
  roles: List[str],
  role_configs: Dict[str, Dict[str, Any]],
) -> Dict[str, Any]:
  """API 呼び出し前に review-run の実行予定を単一 spec として保存する。"""
  run_dir = Path(args.review_run_dir)
  target_paths = [str(path) for path in args.target]
  spec_path = run_dir / "review-execution-spec.yaml"
  now = datetime.now(timezone.utc).isoformat()
  role_outputs = []
  for role in roles:
    role_config = role_configs[role]
    model = role_config["model"]
    role_outputs.append({
      "role": role,
      "provider": role_config["provider"],
      "model": model,
      "outputs": _relative_output_paths(model, args.round_id),
    })

  spec = {
    "schema_version": "review-execution-spec-v1",
    "review_run_id": run_dir.name,
    "execution_spec_path": "review-execution-spec.yaml",
    "created_at": now,
    "round_id": args.round_id,
    "phase": args.phase,
    "criteria": criteria,
    "criteria_source_path": criteria_source_path,
    "criteria_source_sha256": criteria_source_sha256,
    "variant": variant_name or "default",
    "target_files": _target_file_entries(target_paths),
    "inputs": {
      "target_paths": target_paths,
      "prior_finding_paths": list(args.prior_finding),
      "effective_prompt_path": args.effective_prompt_path,
      "prompt_manifest_path": args.prompt_manifest_path,
    },
    "roles": role_outputs,
    "intended_outputs": {
      "execution_spec_path": "review-execution-spec.yaml",
      "target_manifest_path": "target-manifest.yaml",
      "rounds_path": "rounds.yaml",
      "model_result_summary_path": "model-result-summary.yaml",
      "triage_path": "triage.yaml",
      "review_summary_path": "review_summary.md",
    },
  }
  spec["execution_spec_sha256"] = _sha256_data(spec)
  _dump_yaml(spec_path, spec)
  return spec


def _attach_execution_spec_reference(review_run_dir: str, spec: Dict[str, Any]) -> None:
  """run_role が作成した review-run 成果物へ spec 参照を付与する。"""
  run_dir = Path(review_run_dir)
  reference = {
    "execution_spec_path": spec["execution_spec_path"],
    "execution_spec_sha256": spec["execution_spec_sha256"],
  }
  for artifact_name in (
    "target-manifest.yaml",
    "rounds.yaml",
    "model-result-summary.yaml",
  ):
    path = run_dir / artifact_name
    artifact = _load_yaml_dict(path)
    artifact.update(reference)
    _dump_yaml(path, artifact)


def audit_review_execution_spec(review_run_dir: str) -> Dict[str, Any]:
  """ReviewExecutionSpec と成果物参照の一致を機械検査する。"""
  run_dir = Path(review_run_dir)
  spec_path = run_dir / "review-execution-spec.yaml"
  reasons = []
  spec = _load_yaml_dict(spec_path)
  if not spec:
    return {
      "verdict": "DEVIATION",
      "reasons": ["review-execution-spec.yaml missing"],
    }
  expected_path = spec.get("execution_spec_path")
  expected_sha256 = spec.get("execution_spec_sha256")
  expected_outputs = spec.get("intended_outputs")
  if not isinstance(expected_outputs, dict):
    expected_outputs = {}

  checks = {
    "target-manifest.yaml": expected_outputs.get("target_manifest_path", "target-manifest.yaml"),
    "rounds.yaml": expected_outputs.get("rounds_path", "rounds.yaml"),
    "model-result-summary.yaml": expected_outputs.get(
      "model_result_summary_path",
      "model-result-summary.yaml",
    ),
  }
  for label, relative_path in checks.items():
    artifact = _load_yaml_dict(run_dir / str(relative_path))
    if not artifact:
      reasons.append(f"{label} missing")
      continue
    if artifact.get("execution_spec_path") != expected_path:
      reasons.append(f"{label} execution_spec_path mismatch")
    if expected_sha256 and artifact.get("execution_spec_sha256") != expected_sha256:
      reasons.append(f"{label} execution_spec_sha256 mismatch")

  return {
    "verdict": "OK" if not reasons else "DEVIATION",
    "reasons": reasons,
  }


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
    "--default-variant-for",
    default=None,
    help="operation_defaults から既定 variant を解決する場面名",
  )
  parser.add_argument(
    "--target",
    required=True,
    action="append",
    help="対象文書ファイルパス（複数指定可）",
  )
  parser.add_argument("--phase", required=True, help="段名")
  parser.add_argument("--criteria", default=None, help="観点識別子")
  parser.add_argument(
    "--criteria-file",
    default=None,
    help="観点本文を含むファイル。指定時は --criteria の代わりに本文を使う",
  )
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
    "--prompt-manifest-path",
    default=None,
    help="構造化 effective prompt manifest ファイルのパス",
  )
  parser.add_argument(
    "--prompt-manifest-sha256",
    default=None,
    help="prompt manifest ファイルの sha256。未指定ならファイルから計算する",
  )
  parser.add_argument(
    "--verbose",
    action="store_true",
    help="正常系でも review_summary.md の本文を標準出力へ表示する",
  )
  return parser.parse_args(argv)


def _resolve_criteria(args: argparse.Namespace) -> Tuple[str, Optional[str], Optional[str]]:
  """--criteria / --criteria-file から実効 criteria と出典情報を返す。"""
  if bool(args.criteria) == bool(args.criteria_file):
    raise ValueError("--criteria または --criteria-file のどちらか一方を指定してください")
  if args.criteria_file:
    path = Path(args.criteria_file)
    criteria = path.read_text(encoding="utf-8")
    return criteria, str(path), _sha256_file(path)
  return args.criteria, None, None


def _looks_like_vertical_intent_review(criteria: str) -> bool:
  lowered = criteria.lower()
  markers = [
    "vertical intent",
    "intent-transfer",
    "intent transfer",
    "上流意図",
    "意図伝達",
    "upstream purpose",
    "responsibility boundaries",
    "forbidden actions",
  ]
  return any(marker in lowered for marker in markers)


def _source_materials_body(criteria: str) -> str:
  match = re.search(
    r"(?ims)^#{2,6}\s*source materials\s*$\n(?P<body>.*?)(?=^#{2,6}\s|\Z)",
    criteria,
  )
  return match.group("body").strip() if match else ""


def _has_upstream_structured_summary(criteria: str) -> bool:
  lowered = criteria.lower()
  return all(field in lowered for field in VERTICAL_REVIEW_REQUIRED_FIELDS)


def _source_materials_are_paths_only(criteria: str) -> bool:
  body = _source_materials_body(criteria)
  if not body:
    return False
  meaningful_lines = [
    line.strip()
    for line in body.splitlines()
    if line.strip() and not line.strip().startswith("Use these source materials")
  ]
  if not meaningful_lines:
    return False

  path_line_re = re.compile(
    r"^[-*]\s+`?[\w./{}-]+\.(?:md|yaml|yml|json|txt)(?:#[\w./{}-]+)?`?\s*$",
  )
  return all(path_line_re.match(line) for line in meaningful_lines)


def validate_review_prompt_preflight(args: argparse.Namespace, criteria: str) -> List[str]:
  """API 送信前に review prompt の機械的な最低条件を検査する。"""
  if args.phase != "triad-review" or not _looks_like_vertical_intent_review(criteria):
    return []

  errors = []
  has_structured_summary = _has_upstream_structured_summary(criteria)
  if _source_materials_are_paths_only(criteria) and not has_structured_summary:
    errors.append(
      "source materials are listed only as paths; include upstream excerpt or structured summary"
    )
  if not has_structured_summary:
    errors.append(
      "upstream structured summary is missing required fields: "
      + ", ".join(VERTICAL_REVIEW_REQUIRED_FIELDS)
    )
  return errors


def _workspace_root_from_artifact_path(path: Path) -> Path:
  for candidate in [path, *path.parents]:
    if candidate.name == ".reviewcompass":
      return candidate.parent
  local_root = path.parent
  local_commit_unit_path = (
    local_root / ".reviewcompass" / "runtime" / "work-units" / "commit-unit.json"
  )
  if local_commit_unit_path.is_file():
    return local_root
  return Path.cwd()


def _load_commit_unit_binding_for_manifest(
  manifest_path: str,
) -> Tuple[Optional[Dict[str, Any]], List[str]]:
  workspace_root = _workspace_root_from_artifact_path(Path(manifest_path))
  record, errors = commit_unit.load(workspace_root)
  if errors:
    return None, errors
  if not isinstance(record, dict):
    return None, ["commit unit record が mapping ではありません"]
  binding = {
    "work_unit_id": record.get("work_unit_id"),
    "commit_unit_id": record.get("commit_unit_id"),
    "staged_digest": record.get("staged_digest"),
  }
  return binding, []


def _unit_binding_mismatch_errors(
  manifest_binding: Dict[str, Any],
  current_binding: Dict[str, Any],
) -> List[str]:
  errors = []
  for key in ("work_unit_id", "commit_unit_id", "staged_digest"):
    if manifest_binding.get(key) != current_binding.get(key):
      errors.append(f"unit binding mismatch: {key}")
  return errors


def validate_post_write_prompt_manifest_preflight(args: argparse.Namespace) -> List[str]:
  """post-write review-run 起動前に effective prompt manifest を検査する。"""
  if args.phase != "post_write_verification" or not args.prompt_manifest_path:
    return []

  manifest = load_prompt_manifest(args.prompt_manifest_path)
  decision_point = manifest.get("decision_point")
  decision_kind = None
  if isinstance(decision_point, dict):
    decision_kind = decision_point.get("kind")

  errors = []
  if decision_kind != "post_write_verification":
    errors.append(
      "post_write_verification requires prompt manifest "
      f"decision_point.kind=post_write_verification; got {decision_kind}"
    )

  audit_result = audit_manifest(manifest)
  if audit_result.get("verdict") != "OK":
    reasons = audit_result.get("reasons")
    reason_text = "; ".join(str(reason) for reason in reasons or [])
    errors.append(f"prompt manifest audit failed: {reason_text}")

  manifest_binding = manifest.get("unit_binding")
  if isinstance(manifest_binding, dict):
    current_binding, binding_errors = _load_commit_unit_binding_for_manifest(
      args.prompt_manifest_path
    )
    if binding_errors:
      errors.append(
        "unit binding check failed: " + "; ".join(str(error) for error in binding_errors)
      )
    elif current_binding is None:
      errors.append("unit binding check failed: current commit unit is missing")
    else:
      errors.extend(_unit_binding_mismatch_errors(manifest_binding, current_binding))
  return errors


def _select_variant_name(args: argparse.Namespace, config: Dict[str, Any]) -> Optional[str]:
  """phase に応じた実効 variant 名を返す。"""
  if args.variant and args.default_variant_for:
    raise ValueError("--variant と --default-variant-for は同時に指定できません")
  if args.default_variant_for:
    return resolve_default_variant_name(config, args.default_variant_for)
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
  criteria, criteria_source_path, criteria_source_sha256 = _resolve_criteria(args)

  prompt = build_prompt(
    args.target,
    args.phase,
    criteria,
    args.prior_finding,
    provider_name=provider_name,
    model=model,
  )
  effective_prompt_sha256 = _resolve_effective_prompt_sha256(
    args.effective_prompt_path,
    args.effective_prompt_sha256,
  )
  prompt_manifest_sha256 = _resolve_prompt_manifest_sha256(
    args.prompt_manifest_path,
    args.prompt_manifest_sha256,
  )
  response_text, attempts, duration_seconds = _call_provider(provider, prompt)
  try:
    parsed_response = parse_response_data(response_text)
    findings = parsed_response["findings"]
  except Exception:
    update_review_run_artifacts(
      args.review_run_dir,
      round_id=args.round_id,
      target_path=args.target,
      phase=args.phase,
      criteria=criteria,
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
      prompt_manifest_path=args.prompt_manifest_path,
      prompt_manifest_sha256=prompt_manifest_sha256,
      criteria_source_path=criteria_source_path,
      criteria_source_sha256=criteria_source_sha256,
    )
    return 1

  extra_fields = {
    key: value
    for key, value in parsed_response.items()
    if key != "findings"
  }
  output = format_response(
    role=role,
    provider=provider_name,
    model=model,
    attempts=attempts,
    duration_seconds=round(duration_seconds, 3),
    findings=findings,
    extra_fields=extra_fields,
  )
  update_review_run_artifacts(
    args.review_run_dir,
    round_id=args.round_id,
    target_path=args.target,
    phase=args.phase,
    criteria=criteria,
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
    prompt_manifest_path=args.prompt_manifest_path,
    prompt_manifest_sha256=prompt_manifest_sha256,
    criteria_source_path=criteria_source_path,
    criteria_source_sha256=criteria_source_sha256,
  )
  return 0


def _summary_fields(review_run_dir: str, roles: List[str]) -> Dict[str, Any]:
  """正常系 human output 用の短い summary fields を返す。"""
  run_dir = Path(review_run_dir)
  summary = _load_yaml_dict(run_dir / "model-result-summary.yaml")
  models = summary.get("models")
  if not isinstance(models, list):
    models = []
  model_ids = [
    item.get("model_id")
    for item in models
    if isinstance(item, dict) and item.get("model_id")
  ]
  findings = sum(
    int(item.get("findings_count", 0) or 0)
    for item in models
    if isinstance(item, dict)
  )
  parse_failed = sum(
    1
    for item in models
    if isinstance(item, dict) and item.get("parse_status") == "parse_failed"
  )
  return {
    "review_run_dir": review_run_dir,
    "summary": str(run_dir / "review_summary.md"),
    "roles": len(roles),
    "model_ids": join_values(model_ids),
    "findings": findings,
    "parse_failed": parse_failed,
  }


def main(argv: Optional[List[str]] = None) -> int:
  enable_zshrc_api_key_fallback()
  args = _parse_argv(argv)
  exit_code = 0
  try:
    criteria, _, _ = _resolve_criteria(args)
    preflight_errors = validate_review_prompt_preflight(args, criteria)
    if preflight_errors:
      sys.stderr.write("エラー：vertical intent transfer prompt preflight failed\n")
      for error in preflight_errors:
        sys.stderr.write(f"  - {error}\n")
      return 1
    post_write_preflight_errors = validate_post_write_prompt_manifest_preflight(args)
    if post_write_preflight_errors:
      sys.stderr.write("エラー：post-write review prompt preflight failed\n")
      for error in post_write_preflight_errors:
        sys.stderr.write(f"  - {error}\n")
      return 1

    config = load_config(args.config)
    variant_name = _select_variant_name(args, config)
    variant_config = resolve_variant(config, variant_name)
    roles = _roles_for_variant(variant_config)
    role_configs = {
      role: resolve_role(variant_config, role)
      for role in roles
    }
    _, criteria_source_path, criteria_source_sha256 = _resolve_criteria(args)
    execution_spec = write_review_execution_spec(
      args=args,
      criteria=criteria,
      criteria_source_path=criteria_source_path,
      criteria_source_sha256=criteria_source_sha256,
      variant_name=variant_name,
      roles=roles,
      role_configs=role_configs,
    )
    for role in roles:
      role_exit_code = _run_one_role(args, config, variant_name, role)
      if role_exit_code != 0:
        exit_code = 1
    _attach_execution_spec_reference(args.review_run_dir, execution_spec)
    initialize_triage_draft(args.review_run_dir)
    summary_variant_name = variant_name or "default"
    summary_markdown = write_review_summary_markdown(
      args.review_run_dir,
      summary_variant_name,
    )
    if args.verbose:
      sys.stdout.write(summary_markdown)
    else:
      verdict = "OK" if exit_code == 0 else "WARN"
      sys.stdout.write(status_line(
        verdict,
        "run_review",
        _summary_fields(args.review_run_dir, roles),
      ))
    return exit_code
  except Exception as exc:
    sys.stderr.write(f"エラー：{type(exc).__name__}: {exc}\n")
    return 1


if __name__ == "__main__":
  sys.exit(main())
