from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REVIEW = (
  ROOT
  / ".reviewcompass/specs/conformance-evaluation/reviews"
  / "2026-06-09-completed-followup-requirements-design-conflict-review.md"
)


def test_completed_followup_conflict_review_records_minimal_change_policy():
  text = REVIEW.read_text(encoding="utf-8")

  assert "既存項目は原則変更しない" in text
  assert "既存項目への直接変更は、衝突または整合性崩れを直す最小差分に限る" in text


def test_completed_followup_conflict_review_flags_design_requirement_count():
  text = REVIEW.read_text(encoding="utf-8")

  assert "minor_conflict_found" in text
  assert "design.md §20.3" in text
  assert "全 10 件" in text
  assert "全 11 件" in text


def test_completed_followup_conflict_review_preserves_existing_boundaries():
  text = REVIEW.read_text(encoding="utf-8")

  assert "Requirement 9" in text
  assert "Requirement 10" in text
  assert "draft-only" in text
  assert "自動的な requirements/design 本体更新とは扱わない" in text
  assert "既存の 2 モード構造、6 criteria、tasks.md 本体の範囲外扱い" in text


def test_completed_followup_design_requirement_count_is_current():
  design = (
    ROOT / ".reviewcompass/specs/conformance-evaluation/design.md"
  ).read_text(encoding="utf-8")

  assert "requirements.md の全 10 件の Requirement" not in design
  assert "requirements.md の全 12 件の Requirement" in design
