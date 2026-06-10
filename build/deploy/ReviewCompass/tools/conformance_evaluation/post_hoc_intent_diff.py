"""Post-hoc intent difference extraction for existing systems."""
from pathlib import Path


class PostHocIntentDiffError(ValueError):
  """Raised when post-hoc intent diff input or output is invalid."""


ALLOWED_CLASSIFICATIONS = {
  "existing_sufficient",
  "spec_update_candidate",
  "design_conflict_candidate",
  "downstream_impact_candidate",
  "implementation_change_candidate",
}


REQUIRED_CANDIDATE_FIELDS = {
  "feature",
  "phase",
  "classification",
  "code_refs",
  "existing_spec_refs",
  "reasoning_summary",
  "needs_human_decision",
}


class PostHocIntentDiff:
  """Extract candidate downstream impacts from a newly added intent."""

  def __init__(self, root: Path):
    self.root = Path(root)

  def extract(
    self,
    *,
    added_intent: str,
    feature_partitioning: str,
    existing_specs: dict,
    implementation_refs: list,
    run_date: str,
  ) -> dict:
    self._validate_inputs(
      added_intent=added_intent,
      feature_partitioning=feature_partitioning,
      existing_specs=existing_specs,
      implementation_refs=implementation_refs,
      run_date=run_date,
    )
    candidates = [
      self._conformance_candidate(
        added_intent,
        existing_specs.get("conformance-evaluation", {}),
        implementation_refs,
      ),
      self._workflow_management_candidate(
        added_intent,
        existing_specs.get("workflow-management", {}),
        implementation_refs,
      ),
    ]
    for candidate in candidates:
      self.validate_candidate(candidate)
    record_path = self._write_record(
      run_date=run_date,
      added_intent=added_intent,
      feature_partitioning=feature_partitioning,
      candidates=candidates,
    )
    return {
      "mode_internal": "post_hoc_intent_diff",
      "added_intent": added_intent,
      "feature_partitioning": feature_partitioning,
      "candidates": candidates,
      "record_path": str(record_path),
    }

  def validate_candidate(self, candidate: dict) -> None:
    if not isinstance(candidate, dict):
      raise PostHocIntentDiffError("candidate_must_be_mapping")
    missing = sorted(REQUIRED_CANDIDATE_FIELDS - set(candidate))
    if missing:
      raise PostHocIntentDiffError(f"missing_candidate_fields: {missing}")
    if candidate["classification"] not in ALLOWED_CLASSIFICATIONS:
      raise PostHocIntentDiffError(
        f"unknown_classification: {candidate['classification']}"
      )
    if not isinstance(candidate["code_refs"], list):
      raise PostHocIntentDiffError("code_refs_must_be_list")
    if not isinstance(candidate["existing_spec_refs"], list):
      raise PostHocIntentDiffError("existing_spec_refs_must_be_list")
    if not isinstance(candidate["needs_human_decision"], bool):
      raise PostHocIntentDiffError("needs_human_decision_must_be_bool")

  def _validate_inputs(
    self,
    *,
    added_intent: str,
    feature_partitioning: str,
    existing_specs: dict,
    implementation_refs: list,
    run_date: str,
  ) -> None:
    if not isinstance(added_intent, str) or not added_intent.strip():
      raise PostHocIntentDiffError("added_intent_required")
    if not isinstance(feature_partitioning, str) or not feature_partitioning.strip():
      raise PostHocIntentDiffError("feature_partitioning_required")
    if not isinstance(existing_specs, dict):
      raise PostHocIntentDiffError("existing_specs_must_be_mapping")
    if not isinstance(implementation_refs, list) or not implementation_refs:
      raise PostHocIntentDiffError("implementation_refs_required")
    if not isinstance(run_date, str) or not run_date.strip():
      raise PostHocIntentDiffError("run_date_required")

  def _conformance_candidate(
    self,
    added_intent: str,
    specs: dict,
    implementation_refs: list,
  ) -> dict:
    return {
      "candidate_id": "PHID-CE-001",
      "feature": "conformance-evaluation",
      "phase": "implementation",
      "classification": "implementation_change_candidate",
      "code_refs": self._matching_code_refs(
        implementation_refs,
        "tools/conformance_evaluation/",
      ),
      "existing_spec_refs": self._spec_refs("conformance-evaluation", specs),
      "reasoning_summary": (
        "追加 intent は既存コードと既存仕様を照合して下流候補を作る必要があるため、"
        "conformance-evaluation の既存システム差分抽出として扱う。"
      ),
      "needs_human_decision": False,
      "added_intent_summary": added_intent,
    }

  def _workflow_management_candidate(
    self,
    added_intent: str,
    specs: dict,
    implementation_refs: list,
  ) -> dict:
    return {
      "candidate_id": "PHID-WM-001",
      "feature": "workflow-management",
      "phase": "tasks",
      "classification": "downstream_impact_candidate",
      "code_refs": self._matching_code_refs(
        implementation_refs,
        "tools/check-workflow-action.py",
      ),
      "existing_spec_refs": self._spec_refs("workflow-management", specs),
      "reasoning_summary": (
        "差分候補は仕様本文を直接更新せず、workflow-management の reopen 手続きへ"
        "引き渡して既存 feature reopen または新規 feature 必要性を判定する。"
      ),
      "needs_human_decision": False,
      "handoff_target": "workflow-management",
      "write_policy": "handoff_only",
      "added_intent_summary": added_intent,
    }

  def _matching_code_refs(self, implementation_refs: list, path_prefix: str) -> list:
    matches = []
    for ref in implementation_refs:
      if not isinstance(ref, dict):
        continue
      path = ref.get("path", "")
      if path.startswith(path_prefix) or path == path_prefix:
        matches.append(dict(ref))
    if matches:
      return matches
    return [
      dict(ref) for ref in implementation_refs
      if isinstance(ref, dict)
    ]

  def _spec_refs(self, feature: str, specs: dict) -> list:
    refs = []
    for phase in ("requirements", "design", "tasks"):
      value = specs.get(phase) if isinstance(specs, dict) else None
      if value:
        refs.append({
          "feature": feature,
          "phase": phase,
          "source": str(value),
        })
    return refs

  def _write_record(
    self,
    *,
    run_date: str,
    added_intent: str,
    feature_partitioning: str,
    candidates: list,
  ) -> Path:
    path = (
      self.root
      / ".reviewcompass"
      / "specs"
      / "conformance-evaluation"
      / "conformance"
      / f"{run_date}-post-hoc-intent-diff.md"
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
      self._record_text(
        added_intent=added_intent,
        feature_partitioning=feature_partitioning,
        candidates=candidates,
      ),
      encoding="utf-8",
    )
    return path

  def _record_text(
    self,
    *,
    added_intent: str,
    feature_partitioning: str,
    candidates: list,
  ) -> str:
    lines = [
      "---",
      "type: conformance_evaluation",
      "mode_internal: post_hoc_intent_diff",
      "author: implementation",
      "reviewer: workflow",
      "---",
      "",
      "# post_hoc_intent_diff",
      "",
      "## Added Intent",
      "",
      added_intent,
      "",
      "## Feature Partitioning",
      "",
      feature_partitioning,
      "",
      "## Candidates",
      "",
    ]
    for candidate in candidates:
      lines.extend([
        f"- candidate_id: {candidate.get('candidate_id', '')}",
        f"  feature: {candidate['feature']}",
        f"  phase: {candidate['phase']}",
        f"  classification: {candidate['classification']}",
        f"  needs_human_decision: {str(candidate['needs_human_decision']).lower()}",
        f"  reasoning_summary: {candidate['reasoning_summary']}",
      ])
      if candidate.get("handoff_target"):
        lines.append(f"  handoff_target: {candidate['handoff_target']}")
    lines.append("")
    return "\n".join(lines)
