"""T-019 review-wave consumer impact red tests."""

import importlib
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "tools"))


class ReviewWaveConsumerImpactTests(unittest.TestCase):
  def _module(self):
    return importlib.import_module("check_workflow_action.proxy_triage_decisions")

  def test_reopened_history_flag_is_not_active_scope(self):
    module = self._module()
    result = module.resolve_active_reopen_scope(
      spec_reopened={"requirements": True, "design": True},
      reopen_record=None,
    )

    self.assertEqual(result["verdict"], "DEVIATION")
    self.assertNotIn("requirements", result.get("active_reopen_scope", []))
    self.assertIn("active reopen scope", "\n".join(result["reasons"]).lower())

  def test_review_wave_consumer_impact_blocks_without_carry_forward_register(self):
    module = self._module()
    result = module.evaluate_review_wave_consumer_impact(
      review_wave_summary={"consumer_impacts": [{"feature": "runtime", "status": "unresolved"}]},
      carry_forward_register=None,
      downstream_impact_decisions=[],
      spec_recheck={"impacted_downstream_phases": ["design"]},
    )

    self.assertEqual(result["verdict"], "DEVIATION")
    self.assertTrue(result["blocks_proxy_apply"])
    self.assertIn("carry-forward", "\n".join(result["blocking_reasons"]))


if __name__ == "__main__":
  unittest.main()
