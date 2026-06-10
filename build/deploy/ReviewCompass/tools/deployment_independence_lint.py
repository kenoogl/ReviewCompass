"""Deployment independence lint for D-023.

Markdown / YAML / JSON 成果物に混入したローカル絶対パスを検出する。
"""
import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, Iterable, List

SCANNED_SUFFIXES = {".md", ".yaml", ".yml", ".json"}
UNIX_ABSOLUTE_PATH_RE = re.compile(r"(?<![\w:])/(?:Users|Volumes|private|tmp|var|opt|home)/[^\s'\"<>)]*")
WINDOWS_ABSOLUTE_PATH_RE = re.compile(r"\b[A-Za-z]:\\[^\s'\"<>)]*")
URL_RE = re.compile(r"https?://[^\s'\"<>)]*")
ALLOWED_TEMP_PREFIXES = (
  "/private/tmp/reviewcompass-",
  "/tmp/reviewcompass-",
)


def _url_spans(text: str) -> List[range]:
  return [range(match.start(), match.end()) for match in URL_RE.finditer(text)]


def _inside_any_span(index: int, spans: Iterable[range]) -> bool:
  return any(index in span for span in spans)


def _is_allowed_absolute_path(value: str) -> bool:
  return any(value.startswith(prefix) for prefix in ALLOWED_TEMP_PREFIXES)


def lint_text(path: str, text: str) -> List[Dict[str, object]]:
  """1 ファイル分の text から配置非依存性違反を返す。"""
  findings: List[Dict[str, object]] = []
  for line_number, line in enumerate(text.splitlines(), start=1):
    spans = _url_spans(line)
    for pattern in (UNIX_ABSOLUTE_PATH_RE, WINDOWS_ABSOLUTE_PATH_RE):
      for match in pattern.finditer(line):
        value = match.group(0)
        if _inside_any_span(match.start(), spans):
          continue
        if _is_allowed_absolute_path(value):
          continue
        findings.append({
          "path": path,
          "line": line_number,
          "kind": "absolute_path",
          "value": value,
        })
  return findings


def _iter_scannable_files(paths: Iterable[Path]) -> Iterable[Path]:
  for path in paths:
    if path.is_file():
      if path.suffix in SCANNED_SUFFIXES:
        yield path
      continue
    if path.is_dir():
      for child in sorted(path.rglob("*")):
        if child.is_file() and child.suffix in SCANNED_SUFFIXES:
          yield child


def lint_paths(paths: Iterable[Path]) -> List[Dict[str, object]]:
  """指定 path 群配下の Markdown / YAML / JSON を lint する。"""
  findings: List[Dict[str, object]] = []
  for path in _iter_scannable_files(paths):
    try:
      text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
      continue
    findings.extend(lint_text(str(path), text))
  return findings


def main(argv=None) -> int:
  parser = argparse.ArgumentParser(description="Lint deployment-independent artifact paths.")
  parser.add_argument("paths", nargs="+", help="Files or directories to scan.")
  parser.add_argument("--json", action="store_true", help="Print findings as JSON.")
  args = parser.parse_args(argv)

  findings = lint_paths([Path(path) for path in args.paths])
  if args.json:
    print(json.dumps({"findings": findings}, ensure_ascii=False, indent=2))
  else:
    for finding in findings:
      print(
        "{path}:{line}: {kind}: {value}".format(
          path=finding["path"],
          line=finding["line"],
          kind=finding["kind"],
          value=finding["value"],
        )
      )
  return 1 if findings else 0


if __name__ == "__main__":
  sys.exit(main())
