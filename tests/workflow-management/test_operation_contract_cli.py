"""T-016 operation-contract-check CLI tests."""

import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "tools" / "check-workflow-action.py"


def run(args, cwd=REPO_ROOT):
  return subprocess.run(
    ["python3", str(SCRIPT)] + list(args),
    cwd=str(cwd),
    capture_output=True,
    text=True,
    timeout=30,
  )


class OperationContractCliTests(unittest.TestCase):
  def test_operation_contract_check_json_returns_ok_for_repository_contracts(self):
    result = run(["operation-contract-check", "--json"])

    self.assertEqual(result.returncode, 0, result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["verdict"], "OK")
    self.assertEqual(data["unmapped_required_actions"], [])
    self.assertEqual(data["unknown_required_actions"], [])
    self.assertEqual(data["registry_contract_drift"], [])

  def test_operation_contract_check_reports_unmapped_required_action(self):
    tmp = Path(tempfile.mkdtemp())
    try:
      shutil.copytree(REPO_ROOT / ".reviewcompass", tmp / ".reviewcompass", dirs_exist_ok=True)
      (tmp / "stages").mkdir(parents=True, exist_ok=True)
      shutil.copy(REPO_ROOT / "stages" / "operation-registry.yaml", tmp / "stages" / "operation-registry.yaml")
      contracts = {
        "schema_version": "operation-contracts-v1",
        "operations": [
          {
            "schema_version": "operation-contract-v1",
            "operation_id": "completed",
            "required_action": "completed",
            "effect_kind": "read",
            "approval_required": False,
            "approval_contract_refs": [],
            "phase_boundary": "none",
            "sequence": {"mode": "parallel_ok", "internal_steps": []},
            "actor": {"kind": "tool", "source": "required_action baseline"},
            "branching": {"has_branches": False, "branches": []},
            "max_effect_kind": "read",
            "preconditions": [],
            "postconditions": [],
            "side_effects": [],
            "commit_boundary": {"required": False},
            "workflow_state_effect": {"kind": "none"},
            "canonical_invocation": {"entrypoint": None},
          }
        ],
      }
      (tmp / "stages" / "operation-contracts.yaml").write_text(
        yaml.safe_dump(contracts, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
      )

      result = run(["operation-contract-check", "--json"], cwd=tmp)

      self.assertEqual(result.returncode, 2)
      data = json.loads(result.stdout)
      self.assertEqual(data["verdict"], "DEVIATION")
      self.assertIn("commit_stop_point", data["unmapped_required_actions"])
    finally:
      shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
  unittest.main()
