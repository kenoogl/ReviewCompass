"""文書リンク検査ツールの契約テスト。"""
from pathlib import Path

from tools.document_link_lint import lint_paths, lint_path_texts


def test_lint_paths_detects_missing_markdown_link_target(tmp_path):
  source = tmp_path / "docs" / "guide.md"
  source.parent.mkdir()
  source.write_text("[missing](missing.md)\n", encoding="utf-8")

  findings = lint_paths([source], root=tmp_path)

  assert len(findings) == 1
  assert findings[0]["kind"] == "missing_file"
  assert findings[0]["target"] == "docs/missing.md"


def test_lint_paths_detects_missing_anchor(tmp_path):
  source = tmp_path / "docs" / "guide.md"
  target = tmp_path / "docs" / "target.md"
  source.parent.mkdir()
  source.write_text("[target](target.md#missing-anchor)\n", encoding="utf-8")
  target.write_text("# Present Anchor\n", encoding="utf-8")

  findings = lint_paths([source, target], root=tmp_path)

  assert len(findings) == 1
  assert findings[0]["kind"] == "missing_anchor"
  assert findings[0]["anchor"] == "missing-anchor"


def test_lint_paths_accepts_explicit_html_anchor(tmp_path):
  source = tmp_path / "docs" / "guide.md"
  target = tmp_path / "docs" / "target.md"
  source.parent.mkdir()
  source.write_text("[target](target.md#stable-id)\n", encoding="utf-8")
  target.write_text('<a id="stable-id"></a>\n\n## Heading\n', encoding="utf-8")

  findings = lint_paths([source, target], root=tmp_path)

  assert findings == []


def test_lint_paths_skips_review_run_prompt_artifacts(tmp_path):
  prompt = (
    tmp_path
    / ".reviewcompass"
    / "specs"
    / "workflow-management"
    / "reviews"
    / "2026-06-19-review-run"
    / "prompts"
    / "gpt-5.4.round-1.prompt.md"
  )
  prompt.parent.mkdir(parents=True)
  prompt.write_text("[copied source link](../../../missing/source.md)\n", encoding="utf-8")

  findings = lint_paths([prompt], root=tmp_path)

  assert findings == []


def test_lint_path_texts_skips_review_run_prompt_artifacts(tmp_path):
  prompt = Path(
    ".reviewcompass/specs/workflow-management/reviews/2026-06-19-review-run/prompts/gpt-5.4.round-1.prompt.md"
  )

  findings = lint_path_texts(
    {
      prompt: "[copied source link](../../../missing/source.md)\n",
    },
    root=tmp_path,
  )

  assert findings == []


def test_lint_path_texts_prefers_supplied_text_over_file_content(tmp_path):
  source = tmp_path / "docs" / "guide.md"
  target = tmp_path / "docs" / "target.md"
  source.parent.mkdir()
  source.write_text("[target](target.md#present-anchor)\n", encoding="utf-8")
  target.write_text("# Present Anchor\n", encoding="utf-8")

  findings = lint_path_texts(
    {
      Path("docs/guide.md"): "[target](target.md#missing-anchor)\n",
    },
    root=tmp_path,
  )

  assert len(findings) == 1
  assert findings[0]["kind"] == "missing_anchor"
  assert findings[0]["anchor"] == "missing-anchor"


def test_lint_paths_reads_workflow_discipline_map_prompt_refs(tmp_path):
  map_file = tmp_path / "docs" / "operations" / "WORKFLOW_DISCIPLINE_MAP.yaml"
  map_file.parent.mkdir(parents=True)
  map_file.write_text(
    "decision_points:\n"
    "  precheck_subcommand:\n"
    "    - id: spec-set\n"
    "      prompt_source_refs:\n"
    "        - docs/operations/MISSING.md#spec-set\n",
    encoding="utf-8",
  )

  findings = lint_paths([map_file], root=tmp_path)

  assert len(findings) == 1
  assert findings[0]["kind"] == "missing_file"
  assert findings[0]["source_kind"] == "prompt_source_refs"


def test_lint_paths_warns_when_precheck_map_ref_lacks_details(tmp_path):
  map_file = tmp_path / ".reviewcompass" / "guidance" / "WORKFLOW_DISCIPLINE_MAP.yaml"
  precheck = tmp_path / ".reviewcompass" / "guidance" / "WORKFLOW_PRECHECK.md"
  details = tmp_path / ".reviewcompass" / "guidance" / "WORKFLOW_PRECHECK_DETAILS.md"
  map_file.parent.mkdir(parents=True)
  precheck.write_text('<a id="commit"></a>\n\n## commit\n', encoding="utf-8")
  details.write_text('<a id="commit"></a>\n\n## commit\n', encoding="utf-8")
  map_file.write_text(
    "decision_points:\n"
    "  precheck_subcommand:\n"
    "    - id: commit\n"
    "      prompt_source_refs:\n"
    "        - .reviewcompass/guidance/WORKFLOW_PRECHECK.md#commit\n",
    encoding="utf-8",
  )

  findings = lint_paths([map_file, precheck, details], root=tmp_path)

  assert len(findings) == 1
  assert findings[0]["kind"] == "missing_companion_ref"
  assert findings[0]["expected"] == ".reviewcompass/guidance/WORKFLOW_PRECHECK_DETAILS.md#commit"


def test_lint_paths_accepts_precheck_map_ref_with_details(tmp_path):
  map_file = tmp_path / ".reviewcompass" / "guidance" / "WORKFLOW_DISCIPLINE_MAP.yaml"
  precheck = tmp_path / ".reviewcompass" / "guidance" / "WORKFLOW_PRECHECK.md"
  details = tmp_path / ".reviewcompass" / "guidance" / "WORKFLOW_PRECHECK_DETAILS.md"
  map_file.parent.mkdir(parents=True)
  precheck.write_text('<a id="commit"></a>\n\n## commit\n', encoding="utf-8")
  details.write_text('<a id="commit"></a>\n\n## commit\n', encoding="utf-8")
  map_file.write_text(
    "decision_points:\n"
    "  precheck_subcommand:\n"
    "    - id: commit\n"
    "      prompt_source_refs:\n"
    "        - .reviewcompass/guidance/WORKFLOW_PRECHECK.md#commit\n"
    "        - .reviewcompass/guidance/WORKFLOW_PRECHECK_DETAILS.md#commit\n",
    encoding="utf-8",
  )

  findings = lint_paths([map_file, precheck, details], root=tmp_path)

  assert findings == []
