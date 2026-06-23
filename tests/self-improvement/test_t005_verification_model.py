"""T-005 のテスト：検証モデル。

対応タスク：self-improvement tasks.md T-005
対応設計節：design.md §9.1〜§9.5
対応要件：Requirement 5 受入 1〜4
"""
from tools.self_improvement.impact_analysis import ImpactAnalyzer
from tools.self_improvement.verification_model import VerificationModel


def test_t005_retrospective_simulation_records_scope_and_violation_rate():
  proposal = {"proposal_id": "WP-001", "statistical_evidence": {}}
  records = [
    {"record_id": "r1", "violates": True},
    {"record_id": "r2", "violates": False},
    {"record_id": "r3", "violates": True},
    {"record_id": "r4", "violates": False},
  ]

  result = VerificationModel().run_retrospective_simulation(
    proposal,
    target_scope="past reviews: 4 records",
    records=records,
  )

  assert result["method"] == "retrospective_simulation"
  assert result["target_scope"] == "past reviews: 4 records"
  assert result["target_count"] == 4
  assert result["violation_count"] == 2
  assert result["violation_rate"] == 0.5
  assert proposal["statistical_evidence"]["retrospective_simulation"] == result


def test_t005_pilot_operation_threshold_89_90_91_percent():
  model = VerificationModel()

  assert model.evaluate_pilot_operation([0.89])["promotion_decision"] == "not_ready"
  assert model.evaluate_pilot_operation([0.90])["promotion_decision"] == "enforce"
  assert model.evaluate_pilot_operation([0.91])["promotion_decision"] == "enforce"


def test_t005_pilot_operation_preserves_time_series():
  result = VerificationModel().evaluate_pilot_operation(
    [
      {"session": "s1", "compliance_rate": 0.88},
      {"session": "s2", "compliance_rate": 0.92},
    ],
    period="2 sessions",
  )

  assert result["method"] == "pilot_operation"
  assert result["period"] == "2 sessions"
  assert result["threshold"] == 0.9
  assert result["compliance_series"] == [
    {"session": "s1", "compliance_rate": 0.88},
    {"session": "s2", "compliance_rate": 0.92},
  ]
  assert result["final_compliance_rate"] == 0.92


def test_t005_impact_analysis_detects_internal_links(tmp_path):
  discipline = tmp_path / ".reviewcompass" / "guidance" / "discipline_a.md"
  discipline.parent.mkdir(parents=True)
  discipline.write_text(
    "# A\n\n関連：[[discipline_b]] と [[discipline_c]]\n",
    encoding="utf-8",
  )

  result = ImpactAnalyzer(tmp_path).detect_internal_links()

  assert result == [
    {
      "path": ".reviewcompass/guidance/discipline_a.md",
      "links": ["discipline_b", "discipline_c"],
    }
  ]


def test_t005_impact_analysis_classifies_three_conflict_definitions(tmp_path):
  discipline_a = tmp_path / ".reviewcompass" / "guidance" / "discipline_a.md"
  discipline_b = tmp_path / ".reviewcompass" / "guidance" / "discipline_b.md"
  discipline_a.parent.mkdir(parents=True)
  discipline_a.write_text(
    "---\nname: shared-name\napplies_to: review\n---\n[[discipline_b]]\n同じ場面の規律\n",
    encoding="utf-8",
  )
  discipline_b.write_text(
    "---\nname: shared-name\napplies_to: review\n---\n[[discipline_a]]\n異なる文言の規律\n",
    encoding="utf-8",
  )

  conflicts = ImpactAnalyzer(tmp_path).analyze_conflicts()

  assert conflicts["name_duplicates"] == [
    {
      "name": "shared-name",
      "paths": [
        ".reviewcompass/guidance/discipline_a.md",
        ".reviewcompass/guidance/discipline_b.md",
      ],
    }
  ]
  assert conflicts["content_overlaps"] == [
    {
      "applies_to": "review",
      "paths": [
        ".reviewcompass/guidance/discipline_a.md",
        ".reviewcompass/guidance/discipline_b.md",
      ],
    }
  ]
  assert conflicts["reference_cycles"] == [
    {
      "paths": [
        ".reviewcompass/guidance/discipline_a.md",
        ".reviewcompass/guidance/discipline_b.md",
      ],
    }
  ]


def test_t005_unverifiable_proposal_requires_user_audit():
  result = VerificationModel().mark_unverifiable(
    proposal_id="WP-999",
    reason="3 つの検証手段がいずれも機能しない提案",
  )

  assert result == {
    "proposal_id": "WP-999",
    "verification_status": "user_audit_required",
    "auto_approval": False,
    "reason": "3 つの検証手段がいずれも機能しない提案",
  }
