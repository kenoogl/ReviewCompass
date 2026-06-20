"""T-018 effective prompt manifest red tests."""

import json
import sys
import unittest
from pathlib import Path

import jsonschema


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "tools"))
MANIFEST_SCHEMA = (
  REPO_ROOT / ".reviewcompass" / "schema" / "effective_prompt_manifest.schema.json"
)


def load_json(path):
  with path.open(encoding="utf-8") as f:
    return json.load(f)


def valid_manifest(**overrides):
  manifest = {
    "schema_version": "effective-prompt-manifest-v1",
    "decision_point": {
      "kind": "stage",
      "required_action": "run_workflow_stage",
      "phase": "implementation",
      "stage": "drafting",
      "active_gate": None,
    },
    "source_artifacts": [
      {
        "path": "docs/operations/WORKFLOW_NAVIGATION.md",
        "sha256": "sha256:" + "a" * 64,
      }
    ],
    "required_disciplines": ["docs/operations/WORKFLOW_NAVIGATION.md"],
    "operation_contract": {
      "operation_id": "run_workflow_stage",
      "sha256": "sha256:" + "b" * 64,
    },
    "expected_output_schema": {
      "schema_ref": None,
      "required_sections": ["Findings"],
    },
    "prompt_length": {
      "min_chars": 100,
      "max_chars": 20000,
      "source_ref": "docs/operations/WORKFLOW_DISCIPLINE_MAP.yaml#default_prompt_length_bounds",
      "failure_verdict": "WARN",
    },
    "preconditions_checked": [
      {
        "id": "next-json-loaded",
        "source": "next_json",
        "machine_checked": True,
        "evidence_ref": ".reviewcompass/runtime/effective-prompts/example.prompt.md",
      }
    ],
    "language_task": {
      "document_kind": "review",
      "input": {
        "required_files": ["docs/operations/WORKFLOW_NAVIGATION.md"],
        "state_refs": [],
        "source_refs": [],
      },
      "output_format": {
        "kind": "markdown",
        "required_sections": ["Findings"],
        "schema_ref": None,
      },
      "constraints": ["Do not mutate workflow state."],
    },
    "postconditions": [
      {
        "id": "next-action-compatible",
        "check_kind": "next_action_compatible",
        "source_ref": "stages/operation-contracts.yaml",
      }
    ],
    "on_completion": {
      "next_required_action": "run_workflow_stage",
      "allowed_followups": ["prompt-audit"],
      "forbidden_actions": ["commit", "push", "spec-set"],
    },
  }
  manifest.update(overrides)
  return manifest


class EffectivePromptManifestSchemaTests(unittest.TestCase):
  def test_effective_prompt_manifest_covers_source_digests(self):
    self.assertTrue(MANIFEST_SCHEMA.exists(), f"missing schema: {MANIFEST_SCHEMA}")
    schema = load_json(MANIFEST_SCHEMA)
    validator = jsonschema.Draft202012Validator(schema)

    valid_errors = list(validator.iter_errors(valid_manifest()))
    self.assertEqual(valid_errors, [])

    missing_digest = valid_manifest(
      source_artifacts=[{"path": "docs/operations/WORKFLOW_NAVIGATION.md"}]
    )
    self.assertNotEqual(list(validator.iter_errors(missing_digest)), [])

  def test_prompt_length_bounds_are_required_and_structured(self):
    schema = load_json(MANIFEST_SCHEMA)
    validator = jsonschema.Draft202012Validator(schema)

    missing_failure_verdict = valid_manifest(
      prompt_length={
        "min_chars": 20000,
        "max_chars": 100,
        "source_ref": "docs/operations/WORKFLOW_DISCIPLINE_MAP.yaml#default_prompt_length_bounds",
      }
    )
    errors = list(validator.iter_errors(missing_failure_verdict))
    self.assertNotEqual(errors, [])

    valid_bounds_shape = valid_manifest(
      prompt_length={
        "min_chars": 20000,
        "max_chars": 100,
        "source_ref": "docs/operations/WORKFLOW_DISCIPLINE_MAP.yaml#default_prompt_length_bounds",
        "failure_verdict": "WARN",
      }
    )
    self.assertEqual(list(validator.iter_errors(valid_bounds_shape)), [])

  def test_effective_prompt_builder_validates_manifest_before_returning(self):
    from check_workflow_action.effective_prompt_builder import build_manifest

    data = valid_manifest()
    built = build_manifest(
      decision_point=data["decision_point"],
      source_artifacts=data["source_artifacts"],
      required_disciplines=data["required_disciplines"],
      operation_contract=data["operation_contract"],
      expected_output_schema=data["expected_output_schema"],
      prompt_length=data["prompt_length"],
      preconditions_checked=data["preconditions_checked"],
      language_task=data["language_task"],
      postconditions=data["postconditions"],
      on_completion=data["on_completion"],
    )
    self.assertEqual(built["schema_version"], "effective-prompt-manifest-v1")

    with self.assertRaises(ValueError):
      build_manifest(
        decision_point=data["decision_point"],
        source_artifacts=[{"path": "docs/operations/WORKFLOW_NAVIGATION.md"}],
        required_disciplines=data["required_disciplines"],
        operation_contract=data["operation_contract"],
        expected_output_schema=data["expected_output_schema"],
        prompt_length=data["prompt_length"],
        preconditions_checked=data["preconditions_checked"],
        language_task=data["language_task"],
        postconditions=data["postconditions"],
        on_completion=data["on_completion"],
      )


if __name__ == "__main__":
  unittest.main()
