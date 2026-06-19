"""post-write API 検査前の review-target を生成する。

対象ファイル、検査観点、scope、finding policy、機微情報チェックを
review-run 配下へ記録し、run_review.py の --criteria-file として渡せる
criteria 正本を作る。
"""
import argparse
import hashlib
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
  sys.path.insert(0, str(_PROJECT_ROOT))

import yaml  # noqa: E402
from tools.normal_output import status_line  # noqa: E402


SECRET_PATTERNS = [
  re.compile(r"\b[A-Z0-9_]*(?:API|ACCESS|SECRET|PRIVATE)[A-Z0-9_]*_?KEY\s*=", re.I),
  re.compile(r"\bsk-[A-Za-z0-9_-]{8,}\b"),
  re.compile(r"-----BEGIN (?:RSA |OPENSSH |EC |DSA )?PRIVATE KEY-----"),
]


def _sha256_file(path: Path) -> str:
  return hashlib.sha256(path.read_bytes()).hexdigest()


def _target_entries(targets: List[str]) -> List[Dict[str, str]]:
  return [
    {
      "path": target,
      "sha256": _sha256_file(Path(target)),
    }
    for target in targets
  ]


def _secret_hits(targets: List[str]) -> List[Dict[str, str]]:
  hits = []
  for target in targets:
    content = Path(target).read_text(encoding="utf-8")
    for line_number, line in enumerate(content.splitlines(), start=1):
      if any(pattern.search(line) for pattern in SECRET_PATTERNS):
        hits.append({
          "path": target,
          "line": str(line_number),
          "reason": "secret_like_token",
        })
  return hits


def _render_review_target(
  *,
  criteria_id: str,
  targets: List[str],
  target_entries: List[Dict[str, str]],
  change_summary: str,
  review_question: Optional[str],
  sensitive_status: str,
  generated_at: str,
) -> str:
  question = review_question or (
    "Verify that the post-write targets satisfy the stated workflow contract "
    "and do not introduce contradictory instructions."
  )
  lines = [
    "# Post-write Review Target",
    "",
    f"criteria_id: {criteria_id}",
    "phase: post_write_verification",
    f"generated_at: {generated_at}",
    "",
    "## Change Summary",
    "",
    change_summary,
    "",
    "## Review Question",
    "",
    question,
    "",
    "## Target Files",
    "",
  ]
  for entry in target_entries:
    lines.append(f"- {entry['path']} sha256={entry['sha256']}")
  lines.extend([
    "",
    "## Scope",
    "",
    "- Check whether the changed target files clearly state the intended contract.",
    "- Check whether related instructions are mutually consistent across targets.",
    "- Check whether the documented procedure is actionable before API review, triage, manifest, or commit steps continue.",
    "",
    "## Out Of Scope",
    "",
    "- Do not request unrelated refactors or style-only rewrites.",
    "- Do not judge files that are not listed in Target Files.",
    "- Do not treat missing implementation work as a document defect unless the target text claims it already exists.",
    "",
    "## Finding Policy",
    "",
    "- Report must-fix findings for contradictions, missing required gates, or instructions that would allow an unsafe workflow action.",
    "- Report should-fix findings for ambiguity that could cause repeated manual judgment or unnecessary API review loops.",
    "- Return findings: [] when the target files are internally consistent for this review question.",
    "",
    "## Sensitive Information Check",
    "",
    f"- status: {sensitive_status}",
    "- External API review must not proceed if this section reports potential secrets.",
    "",
  ])
  return "\n".join(lines)


def _parse_argv(argv: Optional[List[str]]) -> argparse.Namespace:
  parser = argparse.ArgumentParser(
    description="post-write API 検査用 review-target を review-run 配下に生成する。",
  )
  parser.add_argument(
    "--target",
    required=True,
    action="append",
    help="検査対象ファイル。複数指定可",
  )
  parser.add_argument(
    "--review-run-dir",
    required=True,
    help="review-target を置く review-run ディレクトリ",
  )
  parser.add_argument(
    "--criteria-id",
    required=True,
    help="review-target に記録する criteria ID",
  )
  parser.add_argument(
    "--change-summary",
    required=True,
    help="今回の変更目的。review-target の Change Summary に入る",
  )
  parser.add_argument(
    "--review-question",
    default=None,
    help="検査モデルに問う具体的な質問",
  )
  return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
  args = _parse_argv(argv)
  targets = [str(Path(target)) for target in args.target]
  missing = [target for target in targets if not Path(target).is_file()]
  if missing:
    sys.stderr.write(f"エラー：target file not found: {', '.join(missing)}\n")
    return 1

  hits = _secret_hits(targets)
  if hits:
    sys.stderr.write("エラー：外部 API 送信前の機微情報チェックで停止しました\n")
    for hit in hits:
      sys.stderr.write(f"- {hit['path']}:{hit['line']} {hit['reason']}\n")
    return 2

  run_dir = Path(args.review_run_dir)
  run_dir.mkdir(parents=True, exist_ok=True)
  generated_at = datetime.now(timezone.utc).isoformat()
  target_entries = _target_entries(targets)
  review_target = _render_review_target(
    criteria_id=args.criteria_id,
    targets=targets,
    target_entries=target_entries,
    change_summary=args.change_summary,
    review_question=args.review_question,
    sensitive_status="passed",
    generated_at=generated_at,
  )
  review_target_path = run_dir / "review-target.md"
  review_target_path.write_text(review_target, encoding="utf-8")
  metadata: Dict[str, Any] = {
    "run_id": run_dir.name,
    "phase": "post_write_verification",
    "criteria_id": args.criteria_id,
    "criteria_file": str(review_target_path),
    "criteria_file_sha256": _sha256_file(review_target_path),
    "target_files": target_entries,
    "sensitive_information_check": {
      "status": "passed",
      "checked_at": generated_at,
    },
    "recommended_run_review_args": {
      "criteria_file": str(review_target_path),
      "phase": "post_write_verification",
    },
  }
  (run_dir / "review-target.yaml").write_text(
    yaml.safe_dump(metadata, allow_unicode=True, sort_keys=False),
    encoding="utf-8",
  )
  sys.stdout.write(status_line(
    "OK",
    "prepare_post_write_review",
    {
      "review_target": review_target_path,
      "metadata": run_dir / "review-target.yaml",
      "targets": len(targets),
    },
  ))
  return 0


if __name__ == "__main__":
  sys.exit(main())
