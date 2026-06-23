"""T-003 のテスト：signal_extraction モデル。

対応タスク：self-improvement tasks.md T-003
対応設計節：design.md §7.1〜§7.4
対応要件：Requirement 2 受入 3、Requirement 3 受入 1
"""
import json

import pytest

from tools.self_improvement.signal_extraction import (
  SignalError,
  SignalExtractor,
  build_signal,
)


EVIDENCE = [
  {
    "source": "review_record",
    "location": "reviews/2026-06-04.yaml",
    "observation": "規律と実体の乖離が複数回観察され、提案候補の根拠として十分である",
  }
]


def test_t003_classifies_four_signal_types():
  extractor = SignalExtractor()

  signals = extractor.extract([
    {
      "signal_id": "SE-001",
      "observed_pattern": "実体運用に定常的パターンがあるが対応規律がない",
      "matching_discipline": None,
      "evidence_count": 1,
      "motivating_evidence_seed": EVIDENCE,
    },
    {
      "signal_id": "SE-002",
      "observed_pattern": "同じ規律違反が閾値以上に累積している",
      "matching_discipline": ".reviewcompass/guidance/discipline_options.md",
      "evidence_count": 3,
      "motivating_evidence_seed": EVIDENCE,
    },
    {
      "signal_id": "SE-003",
      "observed_pattern": "規律はあるが長期間参照されていない",
      "matching_discipline": ".reviewcompass/guidance/discipline_old.md",
      "related_disciplines": [".reviewcompass/guidance/discipline_old.md"],
      "sessions_without_reference": 5,
      "motivating_evidence_seed": EVIDENCE,
    },
    {
      "signal_id": "SE-004",
      "observed_pattern": "複数規律が同じ場面に衝突して適用される",
      "conflicting_disciplines": [
        ".reviewcompass/guidance/discipline_a.md",
        ".reviewcompass/guidance/discipline_b.md",
      ],
      "motivating_evidence_seed": EVIDENCE,
    },
  ])

  assert [signal["signal_type"] for signal in signals] == [
    "discipline_absence",
    "discipline_violation",
    "discipline_obsolete",
    "discipline_conflict",
  ]
  assert [signal["proposed_proposal_type"] for signal in signals] == [
    "new_discipline",
    "update",
    "archive",
    "consolidation",
  ]


def test_t003_respects_violation_and_obsolete_thresholds():
  extractor = SignalExtractor(violation_threshold=3, obsolete_sessions_threshold=5)

  signals = extractor.extract([
    {
      "signal_id": "SE-001",
      "observed_pattern": "違反がまだ閾値未満であり提案候補にしない",
      "matching_discipline": ".reviewcompass/guidance/discipline_options.md",
      "evidence_count": 2,
      "motivating_evidence_seed": EVIDENCE,
    },
    {
      "signal_id": "SE-002",
      "observed_pattern": "参照なし期間がまだ閾値未満であり提案候補にしない",
      "matching_discipline": ".reviewcompass/guidance/discipline_old.md",
      "related_disciplines": [".reviewcompass/guidance/discipline_old.md"],
      "sessions_without_reference": 4,
      "motivating_evidence_seed": EVIDENCE,
    },
  ])

  assert signals == []


def test_t003_requires_related_disciplines_for_obsolete_and_conflict():
  with pytest.raises(SignalError, match="missing_related_disciplines"):
    build_signal(
      signal_id="SE-001",
      signal_type="discipline_conflict",
      observed_pattern="衝突型には関連規律が必要で、空配列なら遮断する",
      related_disciplines=[],
      motivating_evidence_seed=EVIDENCE,
    )


def test_t003_rejects_unknown_signal_type_fail_closed():
  with pytest.raises(SignalError, match="unknown_signal_type"):
    build_signal(
      signal_id="SE-001",
      signal_type="runtime_issue",
      observed_pattern="未知の signal_type は fail-closed として処理を止める",
      related_disciplines=[],
      motivating_evidence_seed=EVIDENCE,
    )


def test_t003_signal_schema_documents_owned_constraints():
  schema = json.loads(
    (SignalExtractor.project_root() / "tools" / "self_improvement" / "schemas" / "signal.schema.json")
    .read_text(encoding="utf-8")
  )

  assert schema["properties"]["signal_type"]["enum"] == [
    "discipline_absence",
    "discipline_violation",
    "discipline_obsolete",
    "discipline_conflict",
  ]
  assert "related_disciplines" in schema["required_for_obsolete_or_conflict"]
