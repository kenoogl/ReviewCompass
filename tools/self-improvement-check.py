#!/usr/bin/env python3
"""CLI wrapper for self-improvement machine verification."""
import argparse
import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
  sys.path.insert(0, str(REPO_ROOT))

from tools.self_improvement.machine_verification import (
  MachineVerification,
  VerificationStatus,
)


def _commit_exists(commit_hash: str) -> bool:
  return subprocess.run(
    ["git", "cat-file", "-e", f"{commit_hash}^{{commit}}"],
    capture_output=True,
    text=True,
  ).returncode == 0


def _format(checks):
  verdict = (
    VerificationStatus.DEVIATION
    if any(check.status == VerificationStatus.DEVIATION for check in checks)
    else VerificationStatus.OK
  )
  return {
    "verdict": verdict.value,
    "checks": [check.to_dict() for check in checks],
  }


def main(argv=None):
  parser = argparse.ArgumentParser()
  sub = parser.add_subparsers(dest="command", required=True)

  mv1 = sub.add_parser("mv1")
  mv1.add_argument("--actor-feature", required=True)
  mv1.add_argument("--changed-file", action="append", default=[])
  mv1.add_argument("--json", action="store_true")

  all_cmd = sub.add_parser("all")
  all_cmd.add_argument("--actor-feature", required=True)
  all_cmd.add_argument("--changed-file", action="append", default=[])
  all_cmd.add_argument("--proposal-path", action="append", default=[])
  all_cmd.add_argument("--metric-date", required=True)
  all_cmd.add_argument("--json", action="store_true")

  args = parser.parse_args(argv)
  verifier = MachineVerification(Path.cwd())

  if args.command == "mv1":
    output = _format([
      verifier.check_direct_discipline_writes(
        changed_files=args.changed_file,
        actor_feature=args.actor_feature,
      )
    ])
  else:
    output = verifier.run_all(
      changed_files=args.changed_file,
      actor_feature=args.actor_feature,
      proposal_paths=[Path(path) for path in args.proposal_path],
      metric_date=args.metric_date,
      commit_exists=_commit_exists,
    )

  if args.json:
    print(json.dumps(output, ensure_ascii=False, indent=2))
  else:
    print(output["verdict"])
    for check in output["checks"]:
      for reason in check["reasons"]:
        print(f"- {check['check_id']}: {reason}")
  return 2 if output["verdict"] == "DEVIATION" else 0


if __name__ == "__main__":
  raise SystemExit(main())
