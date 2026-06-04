from pathlib import Path

import pytest

from tools.self_improvement.traceability import (
  EXPECTED_MODEL_NAMES,
  EXPECTED_TASK_TESTS,
  TraceabilityAudit,
)


ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture
def audit():
  return TraceabilityAudit(ROOT)


def test_t011_expected_task_tests_are_present(audit):
  assert audit.missing_task_tests() == []
  assert sorted(EXPECTED_TASK_TESTS) == [f"T-{index:03d}" for index in range(1, 12)]


def test_t011_seven_models_have_all_three_test_levels(audit):
  coverage = audit.model_level_coverage()

  assert sorted(coverage) == sorted(EXPECTED_MODEL_NAMES)
  for levels in coverage.values():
    assert levels == {"unit", "integration", "acceptance"}


def test_t011_requirements_traceability_is_bidirectional(audit):
  assert audit.requirements_traceability_issues() == []


def test_t011_dvt_unresolved_items_have_deferral_reasons(audit):
  assert audit.dvt_gate_issues() == []


def test_t011_key_regression_surfaces_are_covered(audit):
  assert audit.key_regression_coverage() == {
    "proposal_schema_validity": True,
    "foundation_vocab_reference_only": True,
    "superseded_reopen_five_steps": True,
    "effect_metrics": True,
    "rollback_integrity": True,
    "workflow_materialized_at_sync": True,
  }
