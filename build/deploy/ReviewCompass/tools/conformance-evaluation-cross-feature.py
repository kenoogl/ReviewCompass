#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
  sys.path.insert(0, str(REPO_ROOT))

from tools.conformance_evaluation.cross_feature_workflow import (
  CrossFeatureDriftWorkflow,
)


def _json_safe_result(result):
  return {
    "feature": result["feature"],
    "check_record": result["check_record"],
    "draft_dir": result["draft_dir"],
    "draft_files": result["draft_files"],
    "traceability": result["traceability"],
  }


def main(argv=None):
  parser = argparse.ArgumentParser(
    description="Run the cross-feature conformance drift workflow.",
  )
  parser.add_argument("--root", default=".", help="Output root for generated artifacts.")
  parser.add_argument("--run-date", required=True, help="Run date, e.g. 2026-06-08.")
  parser.add_argument(
    "--ownership-fixture",
    default=None,
    help="Path to the cross-feature contract ownership fixture.",
  )
  parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
  args = parser.parse_args(argv)

  ownership_fixture = Path(args.ownership_fixture) if args.ownership_fixture else None
  if ownership_fixture is not None and not ownership_fixture.exists():
    payload = {
      "ok": False,
      "error": "ownership_fixture_not_found",
      "path": str(ownership_fixture),
    }
    if args.json:
      print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    else:
      print(f"ownership_fixture_not_found: {ownership_fixture}", file=sys.stderr)
    return 2

  result = CrossFeatureDriftWorkflow(args.root).run(
    run_date=args.run_date,
    ownership_fixture=ownership_fixture,
  )
  payload = _json_safe_result(result)

  if args.json:
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
  else:
    print(payload["check_record"])
    print(payload["draft_dir"])
  return 0


if __name__ == "__main__":
  raise SystemExit(main())
