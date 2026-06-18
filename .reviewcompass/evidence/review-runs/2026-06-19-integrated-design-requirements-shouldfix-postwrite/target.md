---
review_target: integrated_design_requirements_shouldfix_postwrite
date: 2026-06-19
phase: post_write_verification
criteria: integrated_design_requirements_shouldfix_reflection
---

# Integrated Design Requirements Should-Fix Reflection

## Purpose

Verify that the should-fix candidates from the 3-way traceability review were reflected in the current edits to:

- `intent/INTENT.md`
- `.reviewcompass/specs/workflow-management/requirements.md`

## Source Review

The source run was:

- `.reviewcompass/evidence/review-runs/2026-06-19-integrated-design-requirements-traceability-3way-rerun/`

The review found no must-fix items. The should-fix candidates to reflect were:

1. Make workflow-management's task classification responsibility explicit at the intent level.
2. Make current position, return target, side-track visibility, and approval waiting visible as state rather than conversation context.
3. Strengthen Requirement 13 so the 19 `required_action` mapping cannot be read as partial, and conditional operations are not reduced to a single ambiguous value.
4. Preserve unresolved design choices for composite `effect_kind` representation and `record_human_decision` linkage.
5. Strengthen Requirement 15 so LLM judge audit covers missing mechanical tasks, precondition coverage, and postcondition checkability.
6. Clarify Requirement 16 Phase 1/Phase 0 ordering, the minimal AC10/AC11 precondition, and stable D-003 anchoring.

## Review Question

Check whether the current changed documents reflect those should-fix candidates without introducing unrelated scope, contradiction, or implementation-level overreach.

Do not evaluate implementation correctness. This is a documentation post-write verification.
