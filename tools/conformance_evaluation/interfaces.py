"""Interfaces with adjacent ReviewCompass features."""


class Interfaces:
  FOUNDATION_REFERENCES = {
    "foundation_vocab_ref",
    "foundation_schema_ref",
    "metadata_contract_ref",
  }

  def self_improvement_direction(self) -> str:
    return "conformance-evaluation -> self-improvement"

  def foundation_reference_only(self, references: list) -> bool:
    return all(item in self.FOUNDATION_REFERENCES for item in references)

  def commit_hashes_are_independent(self, target_commit: str, materialization_commit_hash: str) -> bool:
    return bool(target_commit) and bool(materialization_commit_hash) and target_commit != materialization_commit_hash
