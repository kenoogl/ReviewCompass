"""D-023 deployment independence lint の契約テスト。"""
from pathlib import Path

from tools.deployment_independence_lint import lint_paths, lint_text


def test_lint_text_rejects_unix_absolute_path():
  findings = lint_text(
    "docs/notes/example.md",
    "source: /Users/Daily/Development/ReviewCompass/docs/notes/example.md\n",
  )

  assert len(findings) == 1
  assert findings[0]["kind"] == "absolute_path"
  assert findings[0]["line"] == 1


def test_lint_text_rejects_windows_absolute_path():
  findings = lint_text(
    "config/example.yaml",
    "path: C:\\Users\\Daily\\ReviewCompass\\config.yaml\n",
  )

  assert len(findings) == 1
  assert findings[0]["kind"] == "absolute_path"


def test_lint_text_allows_external_urls():
  findings = lint_text(
    "docs/notes/example.md",
    "See https://example.com/path/to/spec and file docs/notes/example.md\n",
  )

  assert findings == []


def test_lint_text_allows_declared_temporary_audit_path():
  findings = lint_text(
    "docs/notes/example.md",
    "temporary audit output: /private/tmp/reviewcompass-raw-triage-postwrite-target.md\n",
  )

  assert findings == []


def test_lint_paths_scans_markdown_yaml_and_json_only(tmp_path):
  ok_md = tmp_path / "ok.md"
  bad_yaml = tmp_path / "bad.yaml"
  ignored_txt = tmp_path / "ignored.txt"
  ok_md.write_text("relative: docs/notes/example.md\n", encoding="utf-8")
  bad_yaml.write_text("path: /Users/Daily/Development/ReviewCompass/config.yaml\n", encoding="utf-8")
  ignored_txt.write_text("path: /Users/Daily/Development/ReviewCompass/ignored\n", encoding="utf-8")

  findings = lint_paths([tmp_path])

  assert [finding["path"] for finding in findings] == [str(bad_yaml)]


def test_lint_paths_accepts_single_file(tmp_path):
  target = tmp_path / "schema.json"
  target.write_text('{"path": "/Users/Daily/Development/ReviewCompass/schema.json"}\n', encoding="utf-8")

  findings = lint_paths([target])

  assert len(findings) == 1
  assert findings[0]["path"] == str(target)
