"""Interfaces with adjacent ReviewCompass features."""


class Interfaces:
  def self_improvement_direction(self) -> str:
    return "conformance-evaluation -> self-improvement"

  def foundation_reference_only(self, references: list) -> bool:
    return all("foundation" in item or "metadata_contract" in item for item in references)

  def commit_hashes_are_independent(self, target_commit: str, materialization_commit_hash: str) -> bool:
    return bool(target_commit) and bool(materialization_commit_hash)

