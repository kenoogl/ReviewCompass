"""post-write API review 前後の機械化入口。

next --json が示す post_write_verification 地点から、review-target 生成に
必要な固定引数を決める。API review 自体と実質所見の判断は扱わない。
"""
import argparse
import json
import re
import subprocess
import sys
from datetime import date
from pathlib import Path
from typing import Any, Dict, List, Optional

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
  sys.path.insert(0, str(_PROJECT_ROOT))

import yaml  # noqa: E402

from tools.api_providers import prepare_post_write_review  # noqa: E402
from tools.api_providers.review_triage import write_manifest  # noqa: E402
from tools.normal_output import status_line  # noqa: E402


STANDARD_SOURCE_MATERIAL_CANDIDATES = [
  ".reviewcompass/guidance/WORKFLOW_NAVIGATION.md",
  ".reviewcompass/guidance/API_REVIEW_PROMPT_QUALITY.md",
  ".reviewcompass/guidance/discipline_post_write_verification.md",
  ".reviewcompass/specs/workflow-management/post-write-verification-spec.yaml",
]


def _load_yaml_or_json(path: Path) -> Dict[str, Any]:
  data = yaml.safe_load(path.read_text(encoding="utf-8"))
  return data if isinstance(data, dict) else {}


def _load_next_action_from_command() -> Dict[str, Any]:
  output = subprocess.check_output(
    [
      sys.executable,
      "tools/check-workflow-action.py",
      "next",
      "--json",
    ],
    text=True,
  )
  data = json.loads(output)
  return data if isinstance(data, dict) else {}


def _load_next_action(path: Optional[str]) -> Dict[str, Any]:
  if path:
    return _load_yaml_or_json(Path(path))
  return _load_next_action_from_command()


def _next_action_payload(data: Dict[str, Any]) -> Dict[str, Any]:
  next_action = data.get("next_action")
  return next_action if isinstance(next_action, dict) else {}


def _target_files(next_action: Dict[str, Any]) -> List[str]:
  value = next_action.get("target_files")
  if isinstance(value, list):
    return [str(item) for item in value if isinstance(item, str) and item.strip()]
  single = next_action.get("file")
  if isinstance(single, str) and single.strip():
    return [single]
  return []


def _slug(value: str) -> str:
  text = Path(value).stem.lower()
  text = re.sub(r"[^a-z0-9]+", "_", text)
  return text.strip("_") or "target"


def criteria_id_for_targets(targets: List[str]) -> str:
  """target list から固定 criteria_id を作る。"""
  slugs = [_slug(target) for target in targets]
  unique_slugs = []
  for slug in slugs:
    if slug not in unique_slugs:
      unique_slugs.append(slug)
  if len(unique_slugs) > 3:
    unique_slugs = unique_slugs[:3] + [f"and_{len(slugs) - 3}_more"]
  return "post_write_verification__" + "__".join(unique_slugs)


def default_review_run_dir(targets: List[str]) -> Path:
  """標準 review-run dir を決める。"""
  return (
    Path(".reviewcompass")
    / "evidence"
    / "review-runs"
    / f"{date.today().isoformat()}-{criteria_id_for_targets(targets)}"
  )


def source_materials_for_targets(targets: List[str]) -> List[str]:
  """post-write review 用の標準 source materials を返す。"""
  target_paths = {str(Path(target).resolve()) for target in targets}
  selected = []
  for candidate in STANDARD_SOURCE_MATERIAL_CANDIDATES:
    path = Path(candidate)
    if not path.is_file():
      continue
    resolved = str(path.resolve())
    if resolved in target_paths:
      continue
    selected.append(str(path.resolve()))
  return selected


def change_summary_for_targets(targets: List[str]) -> str:
  return (
    "post-write verification target files changed: "
    + ", ".join(targets)
  )


def review_question_for_targets(_targets: List[str]) -> str:
  return (
    "Verify that the listed post-write target files are consistent with the "
    "source materials, keep target/source/out-of-scope separation clear, and "
    "do not weaken prompt-manifest preflight, finding policy, or "
    "post-write verification stop conditions."
  )


def _prepare(args: argparse.Namespace) -> int:
  next_data = _load_next_action(args.next_action_file)
  next_action = _next_action_payload(next_data)
  if next_action.get("kind") != "post_write_verification":
    sys.stderr.write(
      "エラー：next_action.kind is not post_write_verification\n"
    )
    return 1
  targets = _target_files(next_action)
  if not targets:
    sys.stderr.write("エラー：next_action target_files is empty\n")
    return 1

  absolute_targets = [str(Path(target).resolve()) for target in targets]
  missing = [target for target in absolute_targets if not Path(target).is_file()]
  if missing:
    sys.stderr.write(f"エラー：target file not found: {', '.join(missing)}\n")
    return 1

  review_run_dir = (
    Path(args.review_run_dir)
    if args.review_run_dir
    else default_review_run_dir(targets)
  )
  source_materials = source_materials_for_targets(absolute_targets)
  prepare_args: List[str] = []
  for target in absolute_targets:
    prepare_args.extend(["--target", target])
  for source_material in source_materials:
    prepare_args.extend(["--source-material", source_material])
  prepare_args.extend([
    "--review-run-dir", str(review_run_dir),
    "--criteria-id", criteria_id_for_targets(targets),
    "--change-summary", change_summary_for_targets(targets),
    "--review-question", review_question_for_targets(targets),
  ])
  result = prepare_post_write_review.main(prepare_args)
  if result != 0:
    return result
  sys.stdout.write(status_line(
    "OK",
    "post_write_review_flow_prepare",
    {
      "review_run_dir": review_run_dir,
      "targets": len(targets),
      "source_materials": len(source_materials),
    },
  ))
  return 0


def _finalize_no_findings(args: argparse.Namespace) -> int:
  try:
    output = write_manifest(args.review_run_dir, args.out)
  except Exception as exc:
    sys.stderr.write(f"エラー：{type(exc).__name__}: {exc}\n")
    return 1
  sys.stdout.write(status_line(
    "OK",
    "post_write_review_flow_finalize_no_findings",
    {
      "manifest": output,
      "review_run_dir": args.review_run_dir,
    },
  ))
  return 0


def _parse_argv(argv: Optional[List[str]]) -> argparse.Namespace:
  parser = argparse.ArgumentParser(
    description="post-write API review 前後の機械化入口。",
  )
  subparsers = parser.add_subparsers(dest="command", required=True)

  prepare_parser = subparsers.add_parser("prepare")
  prepare_parser.add_argument("--next-action-file")
  prepare_parser.add_argument("--review-run-dir")

  finalize_parser = subparsers.add_parser("finalize-no-findings")
  finalize_parser.add_argument("--review-run-dir", required=True)
  finalize_parser.add_argument("--out", default="auto")

  return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
  args = _parse_argv(argv)
  if args.command == "prepare":
    return _prepare(args)
  if args.command == "finalize-no-findings":
    return _finalize_no_findings(args)
  return 1


if __name__ == "__main__":
  sys.exit(main())
