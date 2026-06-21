"""Markdown と workflow discipline map のリンク整合を検査する。"""
import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Set, Tuple

import yaml


SCANNED_SUFFIXES = {".md", ".yaml", ".yml"}
MARKDOWN_LINK_RE = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
HTML_ANCHOR_RE = re.compile(r"<a\s+[^>]*id=[\"']([^\"']+)[\"']", re.IGNORECASE)
HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*#*\s*$")

PRECHECK_DETAIL_COMPANIONS = {
  "spec-set": ".reviewcompass/guidance/WORKFLOW_PRECHECK_DETAILS.md#spec-set",
  "commit": ".reviewcompass/guidance/WORKFLOW_PRECHECK_DETAILS.md#commit",
  "push": ".reviewcompass/guidance/WORKFLOW_PRECHECK_DETAILS.md#push",
  "audit-commit": ".reviewcompass/guidance/WORKFLOW_PRECHECK_DETAILS.md#audit-commit",
  "reopen-start": ".reviewcompass/guidance/WORKFLOW_PRECHECK_DETAILS.md#commit",
}


def _repo_relative(path: Path, root: Path) -> str:
  try:
    return str(path.resolve().relative_to(root.resolve()))
  except ValueError:
    return str(path)


def _heading_slug(text: str) -> str:
  value = text.strip().lower()
  value = re.sub(r"<[^>]+>", "", value)
  value = re.sub(r"[`*_~]", "", value)
  value = re.sub(r"[^\w\-\sぁ-んァ-ヶ一-龠ー/\.]+", "", value)
  value = re.sub(r"\s+", "-", value)
  return value


def _anchors_for_text(text: str) -> Set[str]:
  anchors: Set[str] = set()
  for match in HTML_ANCHOR_RE.finditer(text):
    anchors.add(match.group(1))
  for line in text.splitlines():
    match = HEADING_RE.match(line)
    if match:
      anchors.add(_heading_slug(match.group(2)))
  return anchors


def _anchors_for(path: Path) -> Set[str]:
  try:
    text = path.read_text(encoding="utf-8")
  except UnicodeDecodeError:
    return set()
  return _anchors_for_text(text)


def _iter_scannable_files(paths: Iterable[Path]) -> Iterable[Path]:
  for path in paths:
    if path.is_file():
      if path.suffix in SCANNED_SUFFIXES and not _is_review_run_prompt_artifact(path):
        yield path
      continue
    if path.is_dir():
      for child in sorted(path.rglob("*")):
        if (
          child.is_file()
          and child.suffix in SCANNED_SUFFIXES
          and not _is_review_run_prompt_artifact(child)
        ):
          yield child


def _is_review_run_prompt_artifact(path: Path) -> bool:
  parts = path.parts
  return (
    "reviews" in parts
    and "prompts" in parts
    and path.name.endswith(".prompt.md")
  )


def _parse_ref(ref: str) -> Tuple[str, str]:
  clean = ref.strip().split()[0].strip("<>")
  path, sep, anchor = clean.partition("#")
  if clean.startswith("#"):
    return "", clean[1:]
  return path, anchor if sep else ""


def _resolve_target(source: Path, ref_path: str, root: Path, base: Optional[Path]) -> Path:
  if not ref_path:
    return source
  path = Path(ref_path)
  if path.is_absolute():
    return root / str(path).lstrip("/")
  base_dir = base if base is not None else source.parent
  return (base_dir / path).resolve()


def _finding(
  source: Path,
  root: Path,
  line: int,
  kind: str,
  ref: str,
  target: Path,
  source_kind: str,
  anchor: str = "",
  expected: str = "",
) -> Dict[str, object]:
  finding: Dict[str, object] = {
    "path": _repo_relative(source, root),
    "line": line,
    "kind": kind,
    "ref": ref,
    "target": _repo_relative(target, root),
    "source_kind": source_kind,
  }
  if anchor:
    finding["anchor"] = anchor
  if expected:
    finding["expected"] = expected
  return finding


class LinkChecker:
  def __init__(self, root: Path, text_overrides: Optional[Dict[Path, str]] = None):
    self.root = root.resolve()
    self._anchor_cache: Dict[Path, Set[str]] = {}
    self.text_overrides = {
      path.resolve(): text
      for path, text in (text_overrides or {}).items()
    }

  def anchors_for(self, path: Path) -> Set[str]:
    resolved = path.resolve()
    if resolved in self.text_overrides:
      return _anchors_for_text(self.text_overrides[resolved])
    if resolved not in self._anchor_cache:
      self._anchor_cache[resolved] = _anchors_for(resolved)
    return self._anchor_cache[resolved]

  def target_exists(self, path: Path) -> bool:
    return path.resolve() in self.text_overrides or path.exists()

  def check_ref(
    self,
    source: Path,
    line: int,
    ref: str,
    source_kind: str,
    base: Optional[Path] = None,
  ) -> List[Dict[str, object]]:
    if ref.startswith(("http://", "https://", "mailto:")):
      return []
    ref_path, anchor = _parse_ref(ref)
    target = _resolve_target(source, ref_path, self.root, base)
    if not self.target_exists(target):
      return [_finding(source, self.root, line, "missing_file", ref, target, source_kind, anchor)]
    if anchor and anchor not in self.anchors_for(target):
      return [_finding(source, self.root, line, "missing_anchor", ref, target, source_kind, anchor)]
    return []


def _markdown_findings(path: Path, checker: LinkChecker) -> List[Dict[str, object]]:
  findings: List[Dict[str, object]] = []
  resolved = path.resolve()
  if resolved in checker.text_overrides:
    lines = checker.text_overrides[resolved].splitlines()
  else:
    try:
      lines = path.read_text(encoding="utf-8").splitlines()
    except UnicodeDecodeError:
      return findings
  for line_number, line in enumerate(lines, start=1):
    for match in MARKDOWN_LINK_RE.finditer(line):
      findings.extend(checker.check_ref(path, line_number, match.group(1), "markdown"))
  return findings


def _walk_prompt_source_refs(value):
  if isinstance(value, dict):
    for key, child in value.items():
      if key == "prompt_source_refs" and isinstance(child, list):
        yield child
      else:
        yield from _walk_prompt_source_refs(child)
  elif isinstance(value, list):
    for child in value:
      yield from _walk_prompt_source_refs(child)


def _line_for_ref(text: str, ref: str) -> int:
  for line_number, line in enumerate(text.splitlines(), start=1):
    if ref in line:
      return line_number
  return 1


def _workflow_map_findings(path: Path, checker: LinkChecker) -> List[Dict[str, object]]:
  if path.name != "WORKFLOW_DISCIPLINE_MAP.yaml":
    return []
  try:
    text = path.read_text(encoding="utf-8")
    data = yaml.safe_load(text)
  except (UnicodeDecodeError, yaml.YAMLError):
    return []

  findings: List[Dict[str, object]] = []
  for refs in _walk_prompt_source_refs(data):
    ref_set = set(refs)
    for ref in refs:
      line = _line_for_ref(text, ref)
      findings.extend(
        checker.check_ref(
          path,
          line,
          ref,
          "prompt_source_refs",
          base=checker.root,
        )
      )
    for anchor, expected in PRECHECK_DETAIL_COMPANIONS.items():
      contract_ref = f".reviewcompass/guidance/WORKFLOW_PRECHECK.md#{anchor}"
      if contract_ref in ref_set and expected not in ref_set:
        target_path, _, target_anchor = expected.partition("#")
        findings.append(
          _finding(
            path,
            checker.root,
            _line_for_ref(text, contract_ref),
            "missing_companion_ref",
            contract_ref,
            checker.root / target_path,
            "prompt_source_refs",
            target_anchor,
            expected,
          )
        )
  return findings


def lint_paths(paths: Iterable[Path], root: Optional[Path] = None) -> List[Dict[str, object]]:
  """指定 path 群の Markdown links と prompt_source_refs を検査する。"""
  resolved_root = (root or Path.cwd()).resolve()
  checker = LinkChecker(resolved_root)
  findings: List[Dict[str, object]] = []
  for path in _iter_scannable_files(paths):
    findings.extend(_markdown_findings(path, checker))
    findings.extend(_workflow_map_findings(path, checker))
  return findings


def lint_path_texts(
  path_texts: Dict[Path, str],
  root: Optional[Path] = None,
) -> List[Dict[str, object]]:
  """指定 path の内容を渡された text として扱い、リンクを検査する。"""
  resolved_root = (root or Path.cwd()).resolve()
  resolved_texts = {
    (resolved_root / path if not path.is_absolute() else path).resolve(): text
    for path, text in path_texts.items()
  }
  checker = LinkChecker(resolved_root, text_overrides=resolved_texts)
  findings: List[Dict[str, object]] = []
  for path in path_texts:
    resolved_path = (resolved_root / path if not path.is_absolute() else path).resolve()
    if _is_review_run_prompt_artifact(resolved_path):
      continue
    findings.extend(_markdown_findings(resolved_path, checker))
    findings.extend(_workflow_map_findings(resolved_path, checker))
  return findings


def main(argv: Optional[Sequence[str]] = None) -> int:
  parser = argparse.ArgumentParser(description="Lint document links and workflow prompt references.")
  parser.add_argument("paths", nargs="+", help="Files or directories to scan.")
  parser.add_argument("--root", default=".", help="Repository root for resolving map references.")
  parser.add_argument("--json", action="store_true", help="Print findings as JSON.")
  args = parser.parse_args(argv)

  root = Path(args.root)
  findings = lint_paths([Path(path) for path in args.paths], root=root)
  if args.json:
    print(json.dumps({"findings": findings}, ensure_ascii=False, indent=2))
  else:
    for finding in findings:
      suffix = ""
      if "anchor" in finding:
        suffix += f"#{finding['anchor']}"
      if "expected" in finding:
        suffix += f" expected={finding['expected']}"
      print(
        "{path}:{line}: {kind}: {ref} -> {target}{suffix}".format(
          path=finding["path"],
          line=finding["line"],
          kind=finding["kind"],
          ref=finding["ref"],
          target=finding["target"],
          suffix=suffix,
        )
      )
  return 1 if findings else 0


if __name__ == "__main__":
  sys.exit(main())
