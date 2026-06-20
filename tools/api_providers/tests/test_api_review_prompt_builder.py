"""API review prompt builder core/customization tests."""

import pytest

from tools.api_providers.api_review_prompt_builder import (
  SourceMaterial,
  UserReviewRequirements,
  VerticalIntentTransfer,
  build_api_review_criteria,
  build_api_review_criteria_from_next_action,
  vertical_intent_from_next_action,
)


TRIAD_REVIEW_NEXT_ACTION = {
  "kind": "stage",
  "feature": "workflow-management",
  "phase": "implementation",
  "stage": "triad-review",
  "required_inputs": [
    {
      "id": "target_feature_documents",
      "paths": [
        ".reviewcompass/specs/workflow-management/requirements.md",
        ".reviewcompass/specs/workflow-management/design.md",
        ".reviewcompass/specs/workflow-management/tasks.md",
      ],
    },
    {
      "id": "vertical_intent_transfer_check",
      "phase_chains": {
        "implementation": [
          "requirements.md",
          "design.md",
          "tasks.md",
          "implementation",
        ],
      },
      "prompt_materialization_contract": {
        "source_materials_must_not_be_path_only": True,
        "required_prompt_material": [
          "upstream_excerpt_or_structured_summary",
          "target_phase_artifact_excerpt",
          "review_target",
          "out_of_scope",
        ],
        "upstream_summary_fields": [
          "purpose",
          "responsibility_boundaries",
          "acceptance_criteria",
          "forbidden_actions",
          "unresolved_or_design_deferred_items",
          "intended_target_phase_transfer",
        ],
      },
    },
  ],
}


def test_build_api_review_criteria_preserves_generic_core_and_user_requirements():
  criteria = build_api_review_criteria(
    feature="workflow-management",
    phase="implementation",
    topic="approval-gate",
    review_target_paths=["tools/check_workflow_action/approval_gate.py"],
    judgment_item="approval gate fail-closed behavior",
    review_purpose="defect detection",
    review_object="implementation artifact",
    review_focus=["approval/proxy boundary", "digest binding"],
    scope_boundaries={
      "in_scope": ["approval gate schema and validator"],
      "out_of_scope": ["side-track stack", "workflow snapshot"],
    },
    source_materials=[
      SourceMaterial(
        key="requirement-14",
        purpose="approval gate upstream requirement",
        content="Purpose: prevent approval/proxy bypass.\nForbidden: proxy must not satisfy human_only.",
      )
    ],
    user_requirements=UserReviewRequirements(
      purpose="API review for approval gate only",
      object="approval gate implementation",
      focus=["human_only cannot be proxied"],
      output_requirements=["parser-compatible findings"],
      prohibited_actions=["commit", "push", "spec.json update"],
    ),
  )

  assert "## User Review Requirements" in criteria
  assert "API review for approval gate only" in criteria
  assert "human_only cannot be proxied" in criteria
  assert "Check each preserved review focus item" in criteria
  assert "approval/proxy boundary" in criteria
  assert "digest binding" in criteria
  assert "Output requirements -> Finding Policy" in criteria
  assert "## Review Target" in criteria
  assert "tools/check_workflow_action/approval_gate.py" in criteria
  assert "## Source Materials" in criteria
  assert "Purpose: prevent approval/proxy bypass." in criteria
  assert "create a separate criteria file" not in criteria
  assert "Ask one non-leading primary judgment question" not in criteria
  assert "Limit findings to this judgment item." in criteria
  assert "commit" in criteria
  assert "spec.json update" in criteria


def test_prohibited_user_actions_are_not_mapped_to_target_code_behavior():
  criteria = build_api_review_criteria(
    feature="workflow-management",
    phase="implementation",
    topic="approval-gate-transfer",
    review_target_paths=["tools/check_workflow_action/approval_gate.py"],
    judgment_item="approval gate upstream transfer",
    review_purpose="workflow-management implementation triad-review",
    review_object="approval gate implementation",
    review_focus=["approval/proxy boundary"],
    scope_boundaries={
      "in_scope": ["approval gate schema and validator"],
      "out_of_scope": ["commit", "push", "spec.json update"],
    },
    source_materials=[
      SourceMaterial(
        key="requirement-14",
        purpose="approval gate upstream requirement",
        content="Purpose: prevent approval/proxy bypass.",
      )
    ],
    user_requirements=UserReviewRequirements(
      purpose="API review only",
      object="approval gate implementation",
      focus=["human_only cannot be proxied"],
      output_requirements=["parser-compatible findings"],
      prohibited_actions=["commit", "push", "spec.json update", "phase completion"],
    ),
  )

  assert "target does not authorize commit" not in criteria
  assert "Do not approve or authorize commit" in criteria
  assert "These limits constrain this review run and the reviewing model" in criteria
  assert "This check constrains the review run and model output" in criteria
  assert "mere presence or implementation of workflow-operation code" in criteria
  assert "legitimate target code" not in criteria
  assert "Return findings: [] if and only if every required check passes" in criteria
  assert "if and only if" in criteria
  assert "For each finding, identify the target file" in criteria
  assert "Traceable evidence means" in criteria


def test_vertical_intent_customization_requires_structured_upstream_fields():
  with pytest.raises(ValueError, match="vertical intent source material"):
    build_api_review_criteria(
      feature="workflow-management",
      phase="implementation",
      topic="bad-vertical",
      review_target_paths=["tools/check_workflow_action/approval_gate.py"],
      judgment_item="approval gate transfer",
      review_purpose="upstream transfer check",
      review_object="implementation artifact",
      review_focus=["vertical intent transfer"],
      scope_boundaries={"in_scope": ["approval gate"], "out_of_scope": []},
      source_materials=[
        SourceMaterial(
          key="requirement-14",
          purpose="approval gate upstream requirement",
          content="Requirement 14 path only: .reviewcompass/specs/workflow-management/requirements.md",
        )
      ],
      vertical_intent=VerticalIntentTransfer(
        chain=["requirements.md", "design.md", "tasks.md", "implementation"],
      ),
    )


def test_generic_core_rejects_path_only_source_material():
  with pytest.raises(ValueError, match="path-only"):
    build_api_review_criteria(
      feature="workflow-management",
      phase="implementation",
      topic="path-only",
      review_target_paths=["tools/check_workflow_action/approval_gate.py"],
      judgment_item="approval gate fail-closed behavior",
      review_purpose="defect detection",
      review_object="implementation artifact",
      review_focus=["approval/proxy boundary"],
      scope_boundaries={"in_scope": ["approval gate"], "out_of_scope": []},
      source_materials=[
        SourceMaterial(
          key="requirement-14",
          purpose="approval gate upstream requirement",
          content="- `.reviewcompass/specs/workflow-management/requirements.md`\n",
        )
      ],
    )


def test_vertical_intent_customization_materializes_required_fields():
  criteria = build_api_review_criteria(
    feature="workflow-management",
    phase="implementation",
    topic="approval-gate-transfer",
    review_target_paths=["tools/check_workflow_action/approval_gate.py"],
    judgment_item="approval gate upstream transfer",
    review_purpose="upstream transfer check",
    review_object="implementation artifact",
    review_focus=["vertical intent transfer"],
    scope_boundaries={"in_scope": ["approval gate"], "out_of_scope": ["side-track stack"]},
    source_materials=[
      SourceMaterial(
        key="requirement-14",
        purpose="approval gate upstream requirement",
        source_paths=[
          ".reviewcompass/specs/workflow-management/requirements.md",
          ".reviewcompass/specs/workflow-management/design.md",
          ".reviewcompass/specs/workflow-management/tasks.md",
        ],
        source_anchors=[
          ".reviewcompass/specs/workflow-management/requirements.md sha256:req",
          ".reviewcompass/specs/workflow-management/design.md sha256:design",
          ".reviewcompass/specs/workflow-management/tasks.md sha256:tasks",
        ],
        purpose_field="prevent approval/proxy bypass",
        responsibility_boundaries=["proxy decisions cannot satisfy human_only"],
        acceptance_criteria=["target digest mismatch fails closed"],
        forbidden_actions=["consume approval on read-only review"],
        unresolved_or_deferred=["none"],
        intended_target_phase_transfer=[
          "validator rejects proxy approval for human_only gates"
        ],
      )
    ],
    vertical_intent=VerticalIntentTransfer(
      chain=["requirements.md", "design.md", "tasks.md", "implementation"],
    ),
  )

  assert "## Vertical Intent Transfer Customization" in criteria
  assert "requirements.md -> design.md -> tasks.md -> implementation" in criteria
  assert "- omission" in criteria
  assert "- weakening" in criteria
  assert "- source_paths:" in criteria
  assert "source_paths are provenance only" in criteria
  assert "source_anchors:" in criteria
  assert "At the actual review-run, pass every path listed here as --target" in criteria
  assert "If any listed target path content is absent" in criteria
  assert "Structured Summary (model-readable upstream intent)" in criteria
  assert ".reviewcompass/specs/workflow-management/requirements.md" in criteria
  assert "prevent approval/proxy bypass" in criteria
  assert "proxy decisions cannot satisfy human_only" in criteria
  assert "target digest mismatch fails closed" in criteria
  assert "consume approval on read-only review" in criteria
  assert "unresolved_or_design_deferred_items" in criteria
  assert "unresolved_or_deferred:" not in criteria
  assert "If the target claims resolved behavior for an unresolved item" in criteria


def test_builder_rejects_multiple_independent_judgment_items():
  with pytest.raises(ValueError, match="one judgment item"):
    build_api_review_criteria(
      feature="workflow-management",
      phase="implementation",
      topic="bundled",
      review_target_paths=["tools/check-workflow-action.py"],
      judgment_item=[
        "approval gate behavior",
        "side-track behavior",
      ],
      review_purpose="defect detection",
      review_object="implementation artifact",
      review_focus=["approval", "side-track"],
      scope_boundaries={"in_scope": ["approval", "side-track"], "out_of_scope": []},
      source_materials=[
        SourceMaterial(
          key="requirement-14",
          purpose="workflow management requirement",
          content="Requirement 14 excerpt.",
        )
      ],
    )


def test_vertical_intent_from_next_action_uses_current_phase_chain():
  vertical_intent = vertical_intent_from_next_action(TRIAD_REVIEW_NEXT_ACTION)

  assert vertical_intent == VerticalIntentTransfer(
    chain=["requirements.md", "design.md", "tasks.md", "implementation"]
  )


def test_build_api_review_criteria_from_next_action_applies_required_inputs():
  criteria = build_api_review_criteria_from_next_action(
    next_action=TRIAD_REVIEW_NEXT_ACTION,
    topic="approval-gate-transfer",
    review_target_paths=["tools/check-workflow-action.py"],
    judgment_item="approval gate upstream transfer",
    review_purpose="upstream transfer check",
    review_object="implementation artifact",
    review_focus=["vertical intent transfer"],
    scope_boundaries={
      "in_scope": ["approval gate implementation"],
      "out_of_scope": ["review-run execution", "spec.json phase movement"],
    },
    source_materials=[
      SourceMaterial(
        key="workflow-management-requirements-design-tasks",
        purpose="upstream workflow-management intent",
        purpose_field="keep approval and proxy boundaries explicit",
        responsibility_boundaries=["proxy_model is not a substitute for human approval"],
        acceptance_criteria=["prompt material includes concrete upstream intent"],
        forbidden_actions=["pass only file paths as review evidence"],
        unresolved_or_deferred=["none"],
        intended_target_phase_transfer=[
          "implementation must preserve approval/proxy separation"
        ],
      )
    ],
  )

  assert "criteria_id: workflow-management-implementation-approval-gate-transfer-review-criteria" in criteria
  assert "requirements.md -> design.md -> tasks.md -> implementation" in criteria
  assert "pass only file paths as review evidence" in criteria


def test_build_api_review_criteria_from_next_action_requires_vertical_input_contract():
  next_action = {
    "kind": "stage",
    "feature": "workflow-management",
    "phase": "implementation",
    "stage": "triad-review",
    "required_inputs": [
      {
        "id": "target_feature_documents",
        "paths": [
          ".reviewcompass/specs/workflow-management/requirements.md",
          ".reviewcompass/specs/workflow-management/design.md",
          ".reviewcompass/specs/workflow-management/tasks.md",
        ],
      },
    ],
  }

  with pytest.raises(ValueError, match="vertical_intent_transfer_check"):
    build_api_review_criteria_from_next_action(
      next_action=next_action,
      topic="approval-gate-transfer",
      review_target_paths=["tools/check-workflow-action.py"],
      judgment_item="approval gate upstream transfer",
      review_purpose="upstream transfer check",
      review_object="implementation artifact",
      review_focus=["vertical intent transfer"],
      scope_boundaries={"in_scope": ["approval gate"], "out_of_scope": []},
      source_materials=[
        SourceMaterial(
          key="workflow-management-requirements-design-tasks",
          purpose="upstream workflow-management intent",
          content="Purpose: preserve approval/proxy separation.",
        )
      ],
    )
