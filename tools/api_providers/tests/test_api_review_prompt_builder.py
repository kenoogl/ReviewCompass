"""API review prompt builder core/customization tests."""

import pytest

from tools.api_providers.api_review_prompt_builder import (
  SourceMaterial,
  UserReviewRequirements,
  VerticalIntentTransfer,
  build_api_review_criteria,
)


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
  assert "## Review Target" in criteria
  assert "tools/check_workflow_action/approval_gate.py" in criteria
  assert "## Source Materials" in criteria
  assert "Purpose: prevent approval/proxy bypass." in criteria
  assert "Do not combine multiple independent judgments" in criteria
  assert "commit" in criteria
  assert "spec.json update" in criteria


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
  assert "prevent approval/proxy bypass" in criteria
  assert "proxy decisions cannot satisfy human_only" in criteria
  assert "target digest mismatch fails closed" in criteria
  assert "consume approval on read-only review" in criteria


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
