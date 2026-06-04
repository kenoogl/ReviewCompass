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
  assert sorted(EXPECTED_TASK_TESTS) == [f"T-{index:03d}" for index in range(1, 13)]


def test_t011_seven_models_have_all_three_test_levels(audit):
  coverage = audit.model_level_coverage()

  assert sorted(coverage) == sorted(EXPECTED_MODEL_NAMES)
  for levels in coverage.values():
    assert levels == {"unit", "integration", "acceptance"}


def test_t011_model_level_coverage_matches_design_table_evidence(tmp_path):
  design_path = tmp_path / ".reviewcompass" / "specs" / "self-improvement" / "design.md"
  design_path.parent.mkdir(parents=True)
  design_path.write_text(
    """
### 18.1 テスト対象とテストレベル

| モデル | 単体テスト | 結合テスト | 受入テスト |
|---|---|---|---|
| **入力モデル（§6）** | 5 種類の入力源ごとの読み込みテスト、来歴情報 3 要素の付与テスト | 上流機能（runtime ／ evaluation）出力との連結テスト | 全 5 入力源を網羅した実データでの取り込み |
| **承認モデル（§10）** | あり | 承認後の git mv 動作、workflow-management への手続き入力提供 | フェーズ境目の利用者監査シミュレーション |
### 18.2 テスト戦略の重点ポイント
""",
    encoding="utf-8",
  )

  coverage = TraceabilityAudit(tmp_path).model_level_coverage()

  assert coverage["入力モデル"] == {"unit", "integration", "acceptance"}
  assert coverage["承認モデル"] == {"integration", "acceptance"}


def test_t011_requirements_traceability_is_bidirectional(audit):
  assert audit.requirements_traceability_issues() == []


def test_t011_requirements_traceability_ignores_non_requirement_rows(tmp_path):
  tasks_path = tmp_path / ".reviewcompass" / "specs" / "self-improvement" / "tasks.md"
  tasks_path.parent.mkdir(parents=True)
  tasks_path.write_text(
    """
## 要件追跡

| 要件 | 対応タスク |
|------|-----------|
| Requirement 1 受入 1：workflow 層改善のみ | T-001〜T-012 |
| Boundary Context 隣接期待：foundation | なし |
| Boundary Context 隣接期待：runtime | なし |

## テスト戦略
""",
    encoding="utf-8",
  )

  assert TraceabilityAudit(tmp_path).requirements_traceability_issues() == []


def test_t011_requirements_traceability_detects_missing_task_references(tmp_path):
  tasks_path = tmp_path / ".reviewcompass" / "specs" / "self-improvement" / "tasks.md"
  tasks_path.parent.mkdir(parents=True)
  tasks_path.write_text(
    """
## 要件追跡

| 要件 | 対応タスク |
|------|-----------|
| Requirement 1 受入 1：workflow 層改善のみ | T-001〜T-010 |

## テスト戦略
""",
    encoding="utf-8",
  )

  issues = TraceabilityAudit(tmp_path).requirements_traceability_issues()

  assert "T-011 is not referenced by requirements traceability" in issues
  assert "T-012 is not referenced by requirements traceability" in issues


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


def test_t011_superseded_reopen_coverage_does_not_depend_on_word_five(tmp_path):
  approval_path = tmp_path / "tools" / "self_improvement" / "approval_model.py"
  approval_test_path = tmp_path / "tests" / "self-improvement" / "test_t006_approval_model.py"
  machine_path = tmp_path / "tests" / "self-improvement" / "test_t009_machine_verification.py"
  approval_path.parent.mkdir(parents=True)
  approval_test_path.parent.mkdir(parents=True)
  approval_path.write_text(
    """
class ApprovalModel:
  def supersede(
    self,
    proposal_path,
    *,
    superseded_by,
    superseded_at,
    reopen_reason,
    approval_text,
    declaration,
    new_conclusion,
  ):
    self._require_approval(approval_text)
    if not all([declaration, new_conclusion, superseded_by, superseded_at, reopen_reason]):
      raise ApprovalError("missing_reopen_fields")
    proposal["superseded_by"] = superseded_by
    proposal["superseded_at"] = superseded_at
    proposal["reopen_reason"] = reopen_reason
""",
    encoding="utf-8",
  )
  approval_test_path.write_text(
    """
def test_t006_superseded_transition_requires_reopen_fields():
  assert {
    "declaration",
    "reopen_reason",
    "new_conclusion",
    "approval_text",
    "superseded_by",
    "superseded_at",
  }
""",
    encoding="utf-8",
  )
  machine_path.write_text(
    """
def check_superseded_fields():
  pass

def test_t009_mv4_requires_superseded_three_fields():
  assert "superseded_by"
  assert "superseded_at"
  assert "reopen_reason"
""",
    encoding="utf-8",
  )

  assert TraceabilityAudit(tmp_path).key_regression_coverage()["superseded_reopen_five_steps"]
