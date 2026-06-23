"""Impact analysis helpers for discipline references."""
import re
from pathlib import Path

import yaml


INTERNAL_LINK_PATTERN = re.compile(r"\[\[([^\]]+)\]\]")


class ImpactAnalyzer:
  def __init__(self, root: Path):
    self.root = Path(root)

  def detect_internal_links(self):
    results = []
    for path in self._discipline_paths():
      links = INTERNAL_LINK_PATTERN.findall(path.read_text(encoding="utf-8"))
      if links:
        results.append({
          "path": self._relative(path),
          "links": links,
        })
    return results

  def analyze_conflicts(self):
    metadata = {
      self._relative(path): self._read_metadata(path)
      for path in self._discipline_paths()
    }
    links_by_path = {
      self._relative(path): INTERNAL_LINK_PATTERN.findall(path.read_text(encoding="utf-8"))
      for path in self._discipline_paths()
    }
    return {
      "name_duplicates": self._duplicates(metadata, "name"),
      "content_overlaps": self._duplicates(metadata, "applies_to"),
      "reference_cycles": self._reference_cycles(links_by_path),
    }

  def _discipline_paths(self):
    return sorted((self.root / ".reviewcompass" / "guidance").glob("discipline_*.md"))

  def _relative(self, path: Path) -> str:
    return str(path.relative_to(self.root))

  def _read_metadata(self, path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
      return {}
    parts = text.split("---", 2)
    if len(parts) < 3:
      return {}
    data = yaml.safe_load(parts[1]) or {}
    return data if isinstance(data, dict) else {}

  def _duplicates(self, metadata, key):
    by_value = {}
    for path, values in metadata.items():
      value = values.get(key)
      if value:
        by_value.setdefault(value, []).append(path)
    return [
      {
        key: value,
        "paths": paths,
      }
      for value, paths in sorted(by_value.items())
      if len(paths) > 1
    ]

  def _reference_cycles(self, links_by_path):
    cycles = []
    normalized = {
      path: {self._link_to_path(link) for link in links}
      for path, links in links_by_path.items()
    }
    for path, linked_paths in sorted(normalized.items()):
      for linked_path in sorted(linked_paths):
        if linked_path <= path:
          continue
        if path in normalized.get(linked_path, set()):
          cycles.append({"paths": [path, linked_path]})
    return cycles

  def _link_to_path(self, link: str) -> str:
    name = link if link.endswith(".md") else f"{link}.md"
    return f".reviewcompass/guidance/{name}"
