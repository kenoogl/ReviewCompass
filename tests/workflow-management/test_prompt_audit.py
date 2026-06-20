"""T-018 prompt audit red tests."""

import importlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "tools"))
SCRIPT = REPO_ROOT / "tools" / "check-workflow-action.py"


def manifest(**overrides):
  data = {
    "schema_version": "effective-prompt-manifest-v1",
    "decision_point": {"kind": "stage", "required_action": "run_workflow_stage"},
    "source_artifacts": [
      {"path": "docs/operations/WORKFLOW_NAVIGATION.md", "sha256": "sha256:" + "a" * 64}
    ],
    "prompt_length": {
      "min_chars": 100,
      "max_chars": 20000,
      "source_ref": "docs/operations/WORKFLOW_DISCIPLINE_MAP.yaml#default_prompt_length_bounds",
      "failure_verdict": "WARN",
    },
    "language_task": {
      "document_kind": "review",
      "input": {"required_files": [], "state_refs": [], "source_refs": []},
      "output_format": {"kind": "markdown", "required_sections": ["Findings"], "schema_ref": None},
      "constraints": ["Do not mutate workflow state."],
    },
    "postconditions": [
      {"id": "compat", "check_kind": "next_action_compatible", "source_ref": "contract"}
    ],
    "on_completion": {
      "next_required_action": "run_workflow_stage",
      "allowed_followups": ["prompt-audit"],
      "forbidden_actions": ["commit", "push", "spec-set"],
    },
  }
  data.update(overrides)
  return data


class PromptAuditTests(unittest.TestCase):
  def _module(self):
    return importlib.import_module("check_workflow_action.prompt_audit")

  def test_prompt_audit_rejects_direct_state_mutation_instruction(self):
    module = self._module()
    data = manifest(
      on_completion={
        "next_required_action": "commit_stop_point",
        "allowed_followups": ["spec.json を更新して commit する"],
        "forbidden_actions": [],
      }
    )

    result = module.audit_manifest(data)

    self.assertEqual(result["verdict"], "DEVIATION")
    self.assertIn("on_completion", "\n".join(result["reasons"]))

  def test_prompt_audit_rejects_machine_execution_steps_beyond_state_mutation(self):
    module = self._module()
    data = manifest()
    data["language_task"]["constraints"] = [
      "Create review-run artifacts.",
      "Consume approval gate.",
      "Mutate side-track stack.",
      "Execute operation.",
    ]

    result = module.audit_manifest(data)

    self.assertEqual(result["verdict"], "DEVIATION")
    self.assertIn("machine", "\n".join(result["reasons"]).lower())

  def test_prompt_audit_rejects_on_completion_not_next_action_compatible(self):
    module = self._module()
    data = manifest(
      on_completion={
        "next_required_action": "commit_stop_point",
        "allowed_followups": ["commit"],
        "forbidden_actions": ["commit"],
      }
    )

    result = module.audit_manifest(
      data,
      current_next_action={"required_action": "run_workflow_stage"},
    )

    self.assertEqual(result["verdict"], "DEVIATION")
    self.assertIn("next_action_compatible", "\n".join(result["reasons"]))

  def test_prompt_audit_cli_reads_manifest_json(self):
    with tempfile.TemporaryDirectory() as tmp:
      path = Path(tmp) / "prompt-manifest.yaml"
      path.write_text(yaml.safe_dump(manifest()), encoding="utf-8")

      result = subprocess.run(
        [sys.executable, str(SCRIPT), "prompt-audit", "--prompt-manifest", str(path), "--json"],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        timeout=30,
      )

    self.assertEqual(result.returncode, 0, result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["verdict"], "OK")


if __name__ == "__main__":
  unittest.main()
