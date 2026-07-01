"""API review criteria builder with generic core and customization hooks."""

from __future__ import annotations

from dataclasses import dataclass, field
import re
from typing import Any, Dict, Iterable, List, Sequence


VERTICAL_REQUIRED_FIELDS = (
  "purpose",
  "responsibility_boundaries",
  "acceptance_criteria",
  "forbidden_actions",
  "unresolved_or_deferred",
  "intended_target_phase_transfer",
)

PROMPT_MATERIALIZATION_REQUIRED_ITEMS = (
  "upstream_excerpt_or_structured_summary",
  "target_phase_artifact_excerpt",
  "review_target",
  "out_of_scope",
)

UPSTREAM_SUMMARY_REQUIRED_FIELDS = (
  "purpose",
  "responsibility_boundaries",
  "acceptance_criteria",
  "forbidden_actions",
  "unresolved_or_design_deferred_items",
  "intended_target_phase_transfer",
)


@dataclass
class SourceMaterial:
  """Model-readable source material for API review criteria."""

  key: str
  purpose: str
  source_paths: List[str] = field(default_factory=list)
  source_anchors: List[str] = field(default_factory=list)
  content: str | None = None
  purpose_field: str | None = None
  responsibility_boundaries: List[str] = field(default_factory=list)
  acceptance_criteria: List[str] = field(default_factory=list)
  forbidden_actions: List[str] = field(default_factory=list)
  unresolved_or_deferred: List[str] = field(default_factory=list)
  intended_target_phase_transfer: List[str] = field(default_factory=list)

  def has_vertical_fields(self) -> bool:
    return all([
      bool(self.purpose_field),
      bool(self.responsibility_boundaries),
      bool(self.acceptance_criteria),
      bool(self.forbidden_actions),
      bool(self.unresolved_or_deferred),
      bool(self.intended_target_phase_transfer),
    ])


@dataclass
class UserReviewRequirements:
  """User-provided review requirements preserved in the criteria."""

  purpose: str
  object: str
  focus: List[str] = field(default_factory=list)
  output_requirements: List[str] = field(default_factory=list)
  prohibited_actions: List[str] = field(default_factory=list)


@dataclass
class VerticalIntentTransfer:
  """Vertical intent transfer customization for phase reviews."""

  chain: List[str]


def build_api_review_criteria(
  *,
  feature: str,
  phase: str,
  topic: str,
  review_target_paths: Sequence[str],
  judgment_item: str | Sequence[str],
  review_purpose: str,
  review_object: str,
  review_focus: Sequence[str],
  scope_boundaries: Dict[str, Sequence[str]],
  source_materials: Sequence[SourceMaterial],
  user_requirements: UserReviewRequirements | None = None,
  vertical_intent: VerticalIntentTransfer | None = None,
  preanalysis_audit_changes: Sequence[str] | None = None,
) -> str:
  """Build an API review criteria document.

  The builder owns the generic core. Optional customization objects add
  phase-specific requirements without changing the core contract.
  """
  if not isinstance(judgment_item, str):
    raise ValueError("API review criteria must contain exactly one judgment item")
  if not review_target_paths:
    raise ValueError("at least one review target path is required")
  if not source_materials:
    raise ValueError("at least one model-readable source material is required")
  _validate_generic_source_materials(source_materials)
  if vertical_intent:
    _validate_vertical_source_materials(source_materials)

  lines = [
    "---",
    f"criteria_id: {feature}-{phase}-{topic}-review-criteria",
    f"phase: {phase}",
    "status: draft_for_prompt_quality_review",
    "---",
    "",
    f"# {feature} {phase} {topic} API Review Criteria",
    "",
    "## Review Task",
    "",
    f"Review the target for: {judgment_item}.",
    "",
    "Primary judgment question:",
    "",
    _primary_question(review_purpose, judgment_item, bool(vertical_intent)),
    "",
    "Limit findings to this judgment item.",
    "",
    "## User Review Requirements",
    "",
  ]
  lines.extend(_render_user_requirements(
    review_purpose=review_purpose,
    review_object=review_object,
    review_focus=review_focus,
    scope_boundaries=scope_boundaries,
    user_requirements=user_requirements,
  ))
  lines.extend([
    "",
    "## Generic API Review Core",
    "",
    "- Keep criteria and target roles distinct.",
    "- Treat the target files as the only review target.",
    "- Treat source materials as background or intent-transfer evidence, not as targets.",
    "- Do not use path-only source materials as model-readable evidence.",
    "- Preserve user review requirements without narrowing, broadening, or replacement.",
    "- Exclude credentials, personal identifiers, third-party non-sendable confidential material, and unrelated logs.",
    "- Return parser-compatible findings only.",
    "",
    "## Review Target",
    "",
  ])
  for path in review_target_paths:
    lines.append(f"- `{path}`")
  lines.extend([
    "",
    "At the actual review-run, pass every path listed here as --target. The API runner reads and injects those file contents into the model prompt; this section is the target manifest, not a substitute for target content.",
    "If any listed target path content is absent from the injected prompt, report ERROR against Review Target and do not return findings: [].",
    "",
    "Do not treat this criteria file, a wrapper, or an author-written summary as a substitute for the target.",
    "",
    "## Source Materials",
    "",
  ])
  for material in source_materials:
    lines.extend(_render_source_material(material, vertical=bool(vertical_intent)))
  if vertical_intent:
    lines.extend(_render_vertical_customization(vertical_intent))
  if preanalysis_audit_changes:
    lines.extend(_render_preanalysis_audit_changes(preanalysis_audit_changes))
  lines.extend([
    "",
    "## Required Checks",
    "",
    f"1. Check the target against the single judgment item: {judgment_item}.",
    "2. Check that the target satisfies preserved user review requirements.",
    "3. Check that source materials are used only for background or required intent transfer.",
    "4. Check that no finding depends on unstated assumptions or path-only source material.",
    "5. Check that this review run and its model output do not approve or authorize commit, push, spec.json mutation, phase transition, or gate completion. This check constrains the review run and model output, not the mere presence or implementation of workflow-operation code; report target-code findings only when behavior bypasses or weakens the required gate.",
    "6. Check each preserved review focus item:",
  ])
  lines.extend(_bullet_lines(_review_focus_items(review_focus, user_requirements), indent="  "))
  lines.extend([
    "",
    "## Out Of Scope",
    "",
  ])
  for item in scope_boundaries.get("out_of_scope", []):
    lines.append(f"- {item}")
  lines.extend([
    "- Do not approve or authorize commit, push, spec.json mutation, phase transition, or gate completion.",
    "- These limits constrain this review run and the reviewing model; do not treat the mere presence or implementation of workflow-operation code as a violation solely because it mentions those operations.",
    "- Do not judge downstream correctness unless a target omission would force downstream invention.",
    "",
    "## Finding Policy",
    "",
    "- Use CRITICAL for bypass of human-only approval or irreversible-operation boundaries.",
    "- Use ERROR for missing required behavior, weakened user requirements, or unsupported target behavior.",
    "- Use WARN for meaningful ambiguity, weak traceability, or coverage gaps.",
    "- Use INFO only for minor non-blocking improvements.",
    "- For each finding, identify the target file and the narrowest available location such as line number, function, schema field, or test case.",
    "- Traceable evidence means a target file plus the narrowest available anchor for every checked claim, such as a line number, function name, schema field, CLI option, fixture, or test case.",
    "- Return findings: [] if and only if every required check passes with traceable evidence and no deviation from the preserved review requirements or upstream intent.",
  ])
  return "\n".join(lines).rstrip() + "\n"


def build_api_review_criteria_from_next_action(
  *,
  next_action: Dict[str, Any],
  topic: str,
  review_target_paths: Sequence[str],
  judgment_item: str | Sequence[str],
  review_purpose: str,
  review_object: str,
  review_focus: Sequence[str],
  scope_boundaries: Dict[str, Sequence[str]],
  source_materials: Sequence[SourceMaterial],
  user_requirements: UserReviewRequirements | None = None,
  preanalysis_audit_changes: Sequence[str] | None = None,
) -> str:
  """Build criteria using the workflow next-action point as the customization source."""
  feature = _required_next_action_str(next_action, "feature")
  phase = _required_next_action_str(next_action, "phase")
  vertical_intent = None
  if _next_action_requires_vertical_intent(next_action):
    _required_input(next_action, "target_feature_documents")
    vertical_intent = vertical_intent_from_next_action(next_action)

  return build_api_review_criteria(
    feature=feature,
    phase=phase,
    topic=topic,
    review_target_paths=review_target_paths,
    judgment_item=judgment_item,
    review_purpose=review_purpose,
    review_object=review_object,
    review_focus=review_focus,
    scope_boundaries=scope_boundaries,
    source_materials=source_materials,
    user_requirements=user_requirements,
    vertical_intent=vertical_intent,
    preanalysis_audit_changes=preanalysis_audit_changes,
  )


def vertical_intent_from_next_action(next_action: Dict[str, Any]) -> VerticalIntentTransfer:
  """Extract the current phase's vertical intent contract from next_action."""
  phase = _required_next_action_str(next_action, "phase")
  vertical_input = _required_input(next_action, "vertical_intent_transfer_check")
  phase_chains = vertical_input.get("phase_chains")
  if not isinstance(phase_chains, dict):
    raise ValueError("vertical_intent_transfer_check.phase_chains is required")
  phase_chain = phase_chains.get(phase)
  if not isinstance(phase_chain, list) or not phase_chain:
    raise ValueError(f"vertical intent phase chain is missing for phase: {phase}")
  _validate_prompt_materialization_contract(
    vertical_input.get("prompt_materialization_contract")
  )
  return VerticalIntentTransfer(chain=[str(item) for item in phase_chain])


def _primary_question(review_purpose: str, judgment_item: str, vertical: bool) -> str:
  if vertical:
    return (
      f"Does the target satisfy {judgment_item}, while carrying upstream purpose, "
      "responsibility boundaries, acceptance criteria, forbidden actions, unresolved "
      "items, and intended transfer without any of the following?\n\n"
      "- omission\n"
      "- weakening\n"
      "- contradiction\n"
      "- unsupported addition\n"
      "- drift"
    )
  return f"Does the target satisfy {judgment_item} for {review_purpose} without unsupported assumptions?"


def _render_user_requirements(
  *,
  review_purpose: str,
  review_object: str,
  review_focus: Sequence[str],
  scope_boundaries: Dict[str, Sequence[str]],
  user_requirements: UserReviewRequirements | None,
) -> List[str]:
  purpose = user_requirements.purpose if user_requirements else review_purpose
  review_object_value = user_requirements.object if user_requirements else review_object
  focus = _review_focus_items(review_focus, user_requirements)
  output_requirements = (
    user_requirements.output_requirements if user_requirements else ["parser-compatible findings"]
  )
  prohibited_actions = (
    user_requirements.prohibited_actions
    if user_requirements
    else ["commit", "push", "spec.json update", "phase completion"]
  )
  lines = [
    f"- Review purpose: {purpose}",
    f"- Review object: {review_object_value}",
    "- Review focus:",
  ]
  lines.extend(_bullet_lines(focus, indent="  "))
  lines.append("- Scope boundaries:")
  lines.append("  - In scope:")
  lines.extend(_bullet_lines(scope_boundaries.get("in_scope", []), indent="    "))
  lines.append("  - Out of scope:")
  lines.extend(_bullet_lines(scope_boundaries.get("out_of_scope", []), indent="    "))
  lines.append("- Output requirements:")
  lines.extend(_bullet_lines(output_requirements, indent="  "))
  lines.append("- Prohibited actions:")
  lines.extend(_bullet_lines(prohibited_actions, indent="  "))
  lines.append("- Requirement-to-prompt mapping:")
  lines.append("  - Review purpose -> Review Task and Required Checks")
  lines.append("  - Review focus -> Required Checks")
  lines.append("  - Scope boundaries -> Review Target and Out Of Scope")
  lines.append("  - Output requirements -> Finding Policy")
  lines.append("  - Prohibited actions -> Out Of Scope and Finding Policy")
  return lines


def _review_focus_items(
  review_focus: Sequence[str],
  user_requirements: UserReviewRequirements | None,
) -> List[str]:
  combined: List[str] = []
  for item in list(review_focus) + (user_requirements.focus if user_requirements else []):
    text = str(item)
    if text not in combined:
      combined.append(text)
  return combined


def _render_source_material(material: SourceMaterial, *, vertical: bool) -> List[str]:
  lines = [
    f"### {material.key}",
    "",
    f"Purpose: {material.purpose}",
    "",
  ]
  if vertical:
    if material.source_paths:
      lines.append("- source_paths:")
      lines.extend(_bullet_lines(material.source_paths, indent="  "))
      lines.append("- source_paths_note: source_paths are provenance only; use the structured summary fields below as the model-readable upstream intent material.")
    if material.source_anchors:
      lines.append("- source_anchors:")
      lines.extend(_bullet_lines(material.source_anchors, indent="  "))
    lines.extend(["", "Structured Summary (model-readable upstream intent):", ""])
    lines.extend([
      f"- purpose: {material.purpose_field}",
      "- responsibility_boundaries:",
    ])
    lines.extend(_bullet_lines(material.responsibility_boundaries, indent="  "))
    lines.append("- acceptance_criteria:")
    lines.extend(_bullet_lines(material.acceptance_criteria, indent="  "))
    lines.append("- forbidden_actions:")
    lines.extend(_bullet_lines(material.forbidden_actions, indent="  "))
    lines.append("- unresolved_or_design_deferred_items:")
    lines.extend(_bullet_lines(material.unresolved_or_deferred, indent="  "))
    if material.unresolved_or_deferred:
      lines.append("- unresolved_items_review_rule: If the target claims resolved behavior for an unresolved item without implementation evidence, report WARN or ERROR according to impact.")
    lines.append("- intended_target_phase_transfer:")
    lines.extend(_bullet_lines(material.intended_target_phase_transfer, indent="  "))
    lines.append("")
  else:
    if not material.content:
      raise ValueError(f"source material {material.key} must include content")
    lines.extend([material.content, ""])
  return lines


def _render_vertical_customization(vertical_intent: VerticalIntentTransfer) -> List[str]:
  return [
    "",
    "## Vertical Intent Transfer Customization",
    "",
    "Phase chain:",
    "",
    "- " + " -> ".join(vertical_intent.chain),
    "",
    "Use upstream materials only for background and transfer checking. Limit target judgment to the current phase artifact.",
  ]


def _render_preanalysis_audit_changes(changes: Sequence[str]) -> List[str]:
  lines = [
    "",
    "## Required Prompt Changes From Preanalysis Audit",
    "",
    "The preanalysis sufficiency audit required the following prompt changes. Treat these as mandatory criteria-draft constraints, not optional advice.",
    "",
  ]
  lines.extend(_bullet_lines(changes))
  lines.extend([
    "",
    "## Missing Section Handling",
    "",
    "- If a named target section is absent, renamed, or structurally reorganized, search the full target file for equivalent design responsibility.",
    "- If the responsibility cannot be located, report a finding instead of treating the missing anchor as a pass.",
    "- Do not use absence of a named anchor as a reason to skip the check.",
    "",
    "## Target Excerpt Handling",
    "",
    "- Any target excerpt presence is not evidence of correct requirements transfer.",
    "- Judge the full target file independently.",
    "- Do not treat excerpt inclusion in preparation materials as confirmation that the target satisfies the source contract.",
    "",
    "## Preanalysis Handling",
    "",
    "- Treat the preanalysis claim list as hypothesis context only.",
    "- Do not use the preanalysis as an exhaustive checklist, answer key, or coverage proof.",
    "- Derive findings independently from source materials and the full target.",
    "",
    "## PROHIBITED ACTIONS",
    "",
    "- commit",
    "- push",
    "- spec.json update",
    "- phase approval",
    "- gate completion",
    "- phase completion",
    "- reopen finalize",
    "- proxy_model decision authorization",
    "- human approval delegation",
    "- implementation edits",
    "- unapproved specification changes",
    "",
    "## Output Contract",
    "",
    "Return YAML with these top-level fields:",
    "",
    "- `verdict`",
    "- `reviewed_target`",
    "- `source_materials_used`",
    "- `findings`",
    "- `out_of_scope_not_judged`",
    "",
    "Each `findings` item must contain:",
    "",
    "- `severity`: one of `CRITICAL`, `ERROR`, `WARN`, `INFO`",
    "- `target_location`",
    "- `description`",
    "- `rationale`",
    "- `source_materials`",
  ])
  return lines


def _validate_vertical_source_materials(source_materials: Sequence[SourceMaterial]) -> None:
  for material in source_materials:
    if not material.has_vertical_fields():
      missing = ", ".join(
        field_name
        for field_name, present in _vertical_presence(material).items()
        if not present
      )
      raise ValueError(
        f"vertical intent source material {material.key} is missing fields: {missing}"
      )


def _validate_generic_source_materials(source_materials: Sequence[SourceMaterial]) -> None:
  for material in source_materials:
    if material.content and _content_is_path_only(material.content):
      raise ValueError(f"source material {material.key} is path-only")


def _content_is_path_only(content: str) -> bool:
  lines = [
    line.strip()
    for line in content.splitlines()
    if line.strip()
  ]
  if not lines:
    return False
  path_line_re = re.compile(
    r"^[-*]?\s*`?[\w./{}-]+\.(?:md|yaml|yml|json|txt|py)(?:#[\w./{}-]+)?`?\s*$"
  )
  return all(path_line_re.match(line) for line in lines)


def _vertical_presence(material: SourceMaterial) -> Dict[str, bool]:
  return {
    "purpose": bool(material.purpose_field),
    "responsibility_boundaries": bool(material.responsibility_boundaries),
    "acceptance_criteria": bool(material.acceptance_criteria),
    "forbidden_actions": bool(material.forbidden_actions),
    "unresolved_or_deferred": bool(material.unresolved_or_deferred),
    "intended_target_phase_transfer": bool(material.intended_target_phase_transfer),
  }


def _required_next_action_str(next_action: Dict[str, Any], key: str) -> str:
  value = next_action.get(key)
  if not isinstance(value, str) or not value:
    raise ValueError(f"next_action.{key} is required")
  return value


def _next_action_requires_vertical_intent(next_action: Dict[str, Any]) -> bool:
  return (
    next_action.get("kind") == "stage"
    and next_action.get("stage") == "triad-review"
  )


def _required_input(next_action: Dict[str, Any], input_id: str) -> Dict[str, Any]:
  required_inputs = next_action.get("required_inputs")
  if not isinstance(required_inputs, list):
    raise ValueError("next_action.required_inputs is required")
  for item in required_inputs:
    if isinstance(item, dict) and item.get("id") == input_id:
      return item
  raise ValueError(f"required input {input_id} is missing")


def _validate_prompt_materialization_contract(contract: Any) -> None:
  if not isinstance(contract, dict):
    raise ValueError("prompt_materialization_contract is required")
  if contract.get("source_materials_must_not_be_path_only") is not True:
    raise ValueError("source_materials_must_not_be_path_only must be true")
  required_material = contract.get("required_prompt_material")
  if not isinstance(required_material, list):
    raise ValueError("required_prompt_material is required")
  missing_material = [
    item for item in PROMPT_MATERIALIZATION_REQUIRED_ITEMS
    if item not in required_material
  ]
  if missing_material:
    raise ValueError(
      "required_prompt_material is missing: " + ", ".join(missing_material)
    )
  upstream_fields = contract.get("upstream_summary_fields")
  if not isinstance(upstream_fields, list):
    raise ValueError("upstream_summary_fields is required")
  missing_fields = [
    field_name for field_name in UPSTREAM_SUMMARY_REQUIRED_FIELDS
    if field_name not in upstream_fields
  ]
  if missing_fields:
    raise ValueError(
      "upstream_summary_fields is missing: " + ", ".join(missing_fields)
    )


def _bullet_lines(values: Iterable[Any], *, indent: str = "") -> List[str]:
  items = [str(value) for value in values]
  if not items:
    return [f"{indent}- None"]
  return [f"{indent}- {item}" for item in items]
