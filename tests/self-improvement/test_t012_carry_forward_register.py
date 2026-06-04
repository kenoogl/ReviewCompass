"""T-012 のテスト：固有台帳内容の抽象化。

対応タスク：self-improvement tasks.md T-012
対応設計節：design.md §6.4、§13.5
対応要件：Requirement 2 受入 1〜4、配布先一般性
"""
import json

import yaml

from tools.self_improvement.carry_forward_register import (
  CarryForwardRegister,
  audit_legacy_reference_targets,
  count_unresolved_items,
  general_field_local_reference_violations,
  parse_pending_markdown,
)


SAMPLE_MARKDOWN = """# 機能横断レビューで扱う所見の集約

## 3. 未消化の所見

### A-021：workflow-management と self-improvement の状態遷移が不整合

- **検出**：セッション 41、self-improvement implementation review
- **記録**：[review.md](specs/self-improvement/reviews/review.md)
- **重大度**：WARN
- **判定**：must-fix
- **波及範囲**：
  - **self-improvement**：`.reviewcompass/specs/self-improvement/design.md` §13.5
  - **workflow-management**：`.reviewcompass/specs/workflow-management/design.md` §6
- **対処方針**：時系列契約を一つの正本に寄せる

### A-022：変換には人の判断が必要

- **検出**：セッション 42
- 自由記述だけで、構造化に必要な範囲が不足している

### A-023：既に処理された所見 ✅ 対処済み（2026-06-04）

- **対処内容**：処理済み
"""


def test_t012_parses_markdown_into_abstract_register_items():
  register = parse_pending_markdown(SAMPLE_MARKDOWN)

  assert [item["item_id"] for item in register["items"]] == [
    "carry-forward-021",
    "carry-forward-022",
    "carry-forward-023",
  ]
  first = register["items"][0]
  assert first["scope"] == "cross_scope"
  assert first["source_feature"] == "self-improvement"
  assert first["target_feature_or_phase"] == ["self-improvement", "workflow-management"]
  assert first["finding_summary"] == "workflow-management と self-improvement の状態遷移が不整合"
  assert first["status"] == "open"
  assert first["decision_needed"] is False
  assert first["carry_forward_reason"] == "時系列契約を一つの正本に寄せる"
  assert first["resolution"] is None


def test_t012_isolates_reviewcompass_specific_context():
  register = parse_pending_markdown(SAMPLE_MARKDOWN)
  first = register["items"][0]

  judgment_payload = {
    "item_id": first["item_id"],
    "scope": first["scope"],
    "source_feature": first["source_feature"],
    "target_feature_or_phase": first["target_feature_or_phase"],
    "finding_summary": first["finding_summary"],
    "carry_forward_reason": first["carry_forward_reason"],
  }

  assert "A-021" not in json.dumps(judgment_payload, ensure_ascii=False)
  assert "セッション 41" not in json.dumps(judgment_payload, ensure_ascii=False)
  assert ".reviewcompass/" not in json.dumps(judgment_payload, ensure_ascii=False)
  assert first["project_local_context"]["legacy_id"] == "A-021"
  assert first["project_local_context"]["detected_session"] == "セッション 41"
  assert first["evidence_refs"] == [
    {
      "label": "review.md",
      "path": "specs/self-improvement/reviews/review.md",
    }
  ]


def test_t012_general_fields_do_not_keep_local_spec_references():
  markdown = """# ledger

### A-024：本機能 §12.3 と設計書 判断 7 のローカル参照

- **検出**：セッション 43、workflow-management review
- **記録**：[design.md](.reviewcompass/specs/workflow-management/design.md)
- **波及範囲**：
  - **workflow-management**：`.reviewcompass/specs/workflow-management/design.md` §7
  - **self-improvement**：`.reviewcompass/specs/self-improvement/tasks.md` T-010
- **対処方針**：runtime Req 6 受入 2 と foundation Req 6 受入 10 の両方に値を追加し、本機能 §12.3 と設計書 判断 7 と T-010 を更新する
"""

  register = parse_pending_markdown(markdown)
  item = register["items"][0]

  assert item["finding_summary"] == "ローカル参照"
  assert item["carry_forward_reason"] == "関連仕様の値と時系列契約を整合させる"
  assert "legacy_references" not in item["project_local_context"]
  assert general_field_local_reference_violations(register) == []


def test_t012_generated_import_has_no_local_references_in_general_fields():
  path = (
    CarryForwardRegister.project_root()
    / "learning"
    / "workflow"
    / "carry-forward-register"
    / "reviewcompass-import.yaml"
  )
  register = yaml.safe_load(path.read_text(encoding="utf-8"))

  assert general_field_local_reference_violations(register) == []


def test_t012_generated_import_has_no_weak_legacy_reference_lists():
  path = (
    CarryForwardRegister.project_root()
    / "learning"
    / "workflow"
    / "carry-forward-register"
    / "reviewcompass-import.yaml"
  )
  register = yaml.safe_load(path.read_text(encoding="utf-8"))

  for item in register["items"]:
    context = item.get("project_local_context") or {}
    assert "legacy_references" not in context


def test_t012_markdown_source_is_moved_out_of_reviewcompass_root():
  root = CarryForwardRegister.project_root()

  assert not (root / ".reviewcompass" / "pending-cross-feature-findings.md").exists()
  assert (
    root
    / "learning"
    / "workflow"
    / "carry-forward-register"
    / "sources"
    / "reviewcompass-pending-cross-feature-findings.md"
  ).is_file()


def test_t012_audits_reusable_references_only(tmp_path):
  reusable = tmp_path / "TODO_NEXT_SESSION.md"
  reusable.write_text(
    "old `.reviewcompass/pending-cross-feature-findings.md`\n",
    encoding="utf-8",
  )
  historical = tmp_path / "docs" / "sessions" / "session.md"
  historical.parent.mkdir(parents=True)
  historical.write_text(
    "historical `.reviewcompass/pending-cross-feature-findings.md`\n",
    encoding="utf-8",
  )
  new_source = tmp_path / "docs" / "notes" / "source.md"
  new_source.parent.mkdir(parents=True)
  new_source.write_text(
    "`learning/workflow/carry-forward-register/sources/reviewcompass-pending-cross-feature-findings.md`\n",
    encoding="utf-8",
  )
  review_target = (
    tmp_path
    / ".reviewcompass"
    / "specs"
    / "runtime"
    / "reviews"
    / "run"
    / "review-target.md"
  )
  review_target.parent.mkdir(parents=True)
  review_target.write_text(
    "bundle `.reviewcompass/pending-cross-feature-findings.md`\n",
    encoding="utf-8",
  )

  violations = audit_legacy_reference_targets(tmp_path)

  assert sorted(violation.path for violation in violations) == [
    ".reviewcompass/specs/runtime/reviews/run/review-target.md",
    "TODO_NEXT_SESSION.md",
  ]


def test_t012_marks_incomplete_conversion_for_human_decision():
  register = parse_pending_markdown(SAMPLE_MARKDOWN)
  second = register["items"][1]

  assert second["decision_needed"] is True
  assert "missing_target_feature_or_phase" in second["decision_reasons"]
  assert second["status"] == "open"


def test_t012_counts_only_unresolved_items():
  register = parse_pending_markdown(SAMPLE_MARKDOWN)

  assert count_unresolved_items(register) == 2
  assert register["items"][2]["status"] == "resolved"


def test_t012_writes_register_yaml(tmp_path):
  source = tmp_path / ".reviewcompass" / "pending-cross-feature-findings.md"
  source.parent.mkdir(parents=True)
  source.write_text(SAMPLE_MARKDOWN, encoding="utf-8")
  out = tmp_path / "learning" / "workflow" / "carry-forward-register" / "reviewcompass-import.yaml"

  written = CarryForwardRegister(tmp_path).write_import(source, out)

  assert written == out
  data = yaml.safe_load(out.read_text(encoding="utf-8"))
  assert data["register_id"] == "carry-forward-register"
  assert count_unresolved_items(data) == 2


def test_t012_schema_documents_required_fields():
  schema_path = (
    CarryForwardRegister.project_root()
    / "learning"
    / "workflow"
    / "schemas"
    / "carry-forward-register.schema.json"
  )
  schema = json.loads(schema_path.read_text(encoding="utf-8"))

  item_required = schema["properties"]["items"]["items"]["required"]
  assert "item_id" in item_required
  assert "scope" in item_required
  assert "source_feature" in item_required
  assert "target_feature_or_phase" in item_required
  assert "finding_summary" in item_required
  assert "decision_needed" in item_required
  assert "evidence_refs" in item_required
