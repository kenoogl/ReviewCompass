#!/usr/bin/env python3
from __future__ import annotations

import argparse
import fnmatch
import shutil
from pathlib import Path

import yaml


DEFAULT_MANIFEST = "deploy-manifest.yaml"


def _relative_posix(path: Path, root: Path) -> str:
  return path.relative_to(root).as_posix()


def _validate_manifest_path(path: str) -> None:
  candidate = Path(path)
  if candidate.is_absolute() or ".." in candidate.parts:
    raise ValueError(f"manifest path must be repository-relative: {path}")


def _load_manifest(manifest_path: Path) -> dict:
  data = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
  if not isinstance(data, dict):
    raise ValueError("deploy manifest must be a mapping")
  if data.get("source_policy", {}).get("mode") != "allowlist":
    raise ValueError("deploy manifest source_policy.mode must be allowlist")
  return data


def _matches_any(path: str, patterns: list[str]) -> bool:
  return any(fnmatch.fnmatch(path, pattern) for pattern in patterns)


def _expand_include(repo_root: Path, pattern: str) -> list[Path]:
  _validate_manifest_path(pattern)
  source = repo_root / pattern
  if pattern.endswith("/**"):
    base_dir = repo_root / pattern[:-3]
    if base_dir.is_dir():
      return sorted(path for path in base_dir.rglob("*") if path.is_file())
    return []
  if any(ch in pattern for ch in "*?["):
    return sorted(path for path in repo_root.glob(pattern) if path.is_file())
  if source.is_file():
    return [source]
  if source.is_dir():
    return sorted(path for path in source.rglob("*") if path.is_file())
  return []


def _assert_safe_output_directory(repo_root: Path, output_dir: Path) -> None:
  resolved_repo = repo_root.resolve()
  resolved_output = output_dir.resolve()
  unsafe_targets = {
    resolved_repo,
    resolved_repo.parent,
    Path("/"),
    Path.home().resolve(),
  }
  if resolved_output in unsafe_targets:
    raise ValueError(f"unsafe output directory: {output_dir}")
  if (resolved_output / ".git").exists():
    raise ValueError(f"unsafe output directory: {output_dir}")


def _clean_output_directory(repo_root: Path, output_dir: Path) -> None:
  _assert_safe_output_directory(repo_root, output_dir)
  if output_dir.exists():
    shutil.rmtree(output_dir)


def build_package(
  *,
  repo_root: Path,
  manifest_path: Path,
  output_dir: Path | None = None,
  clean: bool = False,
) -> dict:
  repo_root = repo_root.resolve()
  manifest_path = manifest_path.resolve()
  manifest = _load_manifest(manifest_path)

  if output_dir is None:
    output_dir = repo_root / manifest["output"]["default_directory"]
  output_dir = output_dir.resolve()

  if clean:
    _clean_output_directory(repo_root, output_dir)
  else:
    _assert_safe_output_directory(repo_root, output_dir)

  include_patterns = [entry["path"] for entry in manifest.get("include", [])]
  exclude_patterns = [entry["path"] for entry in manifest.get("exclude", [])]
  for pattern in [*include_patterns, *exclude_patterns]:
    _validate_manifest_path(pattern)

  unresolved: list[str] = []
  selected: dict[str, Path] = {}
  excluded: list[dict] = []

  for pattern in include_patterns:
    matched = _expand_include(repo_root, pattern)
    if not matched:
      unresolved.append(pattern)
      continue
    for source_path in matched:
      relative_path = _relative_posix(source_path, repo_root)
      if _matches_any(relative_path, exclude_patterns):
        excluded.append({"path": relative_path})
        continue
      selected[relative_path] = source_path

  if unresolved:
    raise FileNotFoundError(
      "manifest include entries did not resolve to files: "
      + ", ".join(sorted(unresolved))
    )

  copied: list[dict] = []
  for relative_path, source_path in sorted(selected.items()):
    target_path = output_dir / relative_path
    target_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source_path, target_path)
    copied.append({"path": relative_path})

  return {
    "manifest": _relative_posix(manifest_path, repo_root),
    "output_dir": str(output_dir),
    "copied": copied,
    "excluded": sorted(excluded, key=lambda entry: entry["path"]),
  }


def _parse_args() -> argparse.Namespace:
  parser = argparse.ArgumentParser(
    description="Build a ReviewCompass deployment package from deploy-manifest.yaml.",
  )
  parser.add_argument(
    "--manifest",
    default=DEFAULT_MANIFEST,
    help="Path to the deployment manifest.",
  )
  parser.add_argument(
    "--out",
    help="Output directory. Defaults to output.default_directory in the manifest.",
  )
  parser.add_argument(
    "--clean",
    action="store_true",
    help="Remove the output directory before copying files.",
  )
  return parser.parse_args()


def main() -> int:
  args = _parse_args()
  repo_root = Path.cwd()
  result = build_package(
    repo_root=repo_root,
    manifest_path=repo_root / args.manifest,
    output_dir=Path(args.out) if args.out else None,
    clean=args.clean,
  )
  print(f"copied {len(result['copied'])} files to {result['output_dir']}")
  return 0


if __name__ == "__main__":
  raise SystemExit(main())
