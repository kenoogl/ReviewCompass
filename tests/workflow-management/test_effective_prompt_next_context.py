"""Effective prompt next-action context tests."""

import importlib.util
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "tools" / "check-workflow-action.py"


def load_workflow_action_module():
  sys.path.insert(0, str(REPO_ROOT / "tools"))
  spec = importlib.util.spec_from_file_location("check_workflow_action_cli", SCRIPT)
  module = importlib.util.module_from_spec(spec)
  assert spec.loader is not None
  spec.loader.exec_module(module)
  return module


class EffectivePromptNextContextTests(unittest.TestCase):
  def test_stage_triad_review_effective_prompt_contains_required_inputs(self):
    module = load_workflow_action_module()
    next_action = {
      "kind": "stage",
      "feature": "workflow-management",
      "phase": "implementation",
      "stage": "triad-review",
      "reason": "workflow-management の implementation.triad-review が未完了です",
    }

    augmented = module.attach_required_context(REPO_ROOT, next_action)
    prompt_meta = augmented["effective_prompt"]
    prompt_path = REPO_ROOT / prompt_meta["effective_prompt_path"]
    prompt_text = prompt_path.read_text(encoding="utf-8")

    self.assertIn('"required_inputs"', prompt_text)
    self.assertIn('"target_feature_documents"', prompt_text)
    self.assertIn('"vertical_intent_transfer_check"', prompt_text)
    self.assertIn('"prompt_materialization_contract"', prompt_text)


if __name__ == "__main__":
  unittest.main()
