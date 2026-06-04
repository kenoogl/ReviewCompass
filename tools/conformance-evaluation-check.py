#!/usr/bin/env python3
"""CLI placeholder for conformance-evaluation machine checks."""
from tools.conformance_evaluation.machine_verification import MachineVerification


def main() -> int:
  MachineVerification()
  return 0


if __name__ == "__main__":
  raise SystemExit(main())

