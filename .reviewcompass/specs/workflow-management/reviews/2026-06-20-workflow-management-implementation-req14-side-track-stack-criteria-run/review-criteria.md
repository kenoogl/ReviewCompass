---
criteria_id: workflow-management-implementation-req14-side-track-stack-transfer-review-criteria
phase: implementation
status: draft_for_prompt_quality_review
---

# workflow-management implementation req14-side-track-stack-transfer API Review Criteria

## Review Task

Review the target for: Req 14 side track stack implementation upstream transfer.

Primary judgment question:

Does the target satisfy Req 14 side track stack implementation upstream transfer, while carrying upstream purpose, responsibility boundaries, acceptance criteria, forbidden actions, unresolved items, and intended transfer without any of the following?

- omission
- weakening
- contradiction
- unsupported addition
- drift

Limit findings to this judgment item.

## User Review Requirements

- Review purpose: workflow-management implementation triad-review
- Review object: Req 14 side track stack implementation artifacts
- Review focus:
  - side track stack scope and return target
  - staged file digest drift handling
- Scope boundaries:
  - In scope:
    - side track stack schema, implementation, CLI integration, and focused tests
  - Out of scope:
    - approval gate behavior
    - workflow-state snapshot behavior
- Output requirements:
  - parser-compatible findings
- Prohibited actions:
  - commit
  - push
  - spec.json update
  - phase completion
- Requirement-to-prompt mapping:
  - Review purpose -> Review Task and Required Checks
  - Review focus -> Required Checks
  - Scope boundaries -> Review Target and Out Of Scope
  - Output requirements -> Finding Policy
  - Prohibited actions -> Out Of Scope and Finding Policy

## Generic API Review Core

- Keep criteria and target roles distinct.
- Treat the target files as the only review target.
- Treat source materials as background or intent-transfer evidence, not as targets.
- Do not use path-only source materials as model-readable evidence.
- Preserve user review requirements without narrowing, broadening, or replacement.
- Exclude credentials, personal identifiers, third-party non-sendable confidential material, and unrelated logs.
- Return parser-compatible findings only.

## Review Target

- `.reviewcompass/schema/side_track_stack.schema.json`
- `tools/check-workflow-action.py`
- `tools/check_workflow_action/side_track_stack.py`
- `tests/workflow-management/test_side_track_stack.py`

At the actual review-run, pass every path listed here as --target. The API runner reads and injects those file contents into the model prompt; this section is the target manifest, not a substitute for target content.
If any listed target path content is absent from the injected prompt, report ERROR against Review Target and do not return findings: [].

Do not treat this criteria file, a wrapper, or an author-written summary as a substitute for the target.

## Source Materials

### workflow-management-req14-side-track-stack-upstream-intent

Purpose: Requirement 14 / design / tasks intent for side track stack scope, return target, and digest drift.

- source_paths:
  - .reviewcompass/specs/workflow-management/requirements.md
  - .reviewcompass/specs/workflow-management/design.md
  - .reviewcompass/specs/workflow-management/tasks.md
- source_paths_note: source_paths are provenance only; use the structured summary fields below as the model-readable upstream intent material.
- source_anchors:
  - .reviewcompass/specs/workflow-management/requirements.md sha256:e7621e6d56a3ef42085e2864a88366d670e55c304668dd21f48dde32411e13f3
  - .reviewcompass/specs/workflow-management/design.md sha256:ac6bd42e57b507a615af3ed6a40f3c031f56fe75f27e7f1fcc12ddcb4dc46558
  - .reviewcompass/specs/workflow-management/tasks.md sha256:053858cf4abf94bd7b54bf8a45a8ca9504afef39ea8be48bd282193f95e84098

Structured Summary (model-readable upstream intent):

- purpose: Treat unexpected side-track work as explicit stack state with bounded scope, return target, and staged-file digest checks.
- responsibility_boundaries:
  - Side track stack state owns push, pop, current, inspect, repair, allowed scope/files, return target, staged file set, and digest checks.
  - Read-only inspection and mutating stack operations must remain separated.
  - Normal workflow resumption depends on top-frame completion and acceptable staged-file/digest state.
- acceptance_criteria:
  - Side track frames include frame identity, parent, allowed scope/files, completion conditions, return_to, spawned_from, staged_file_set, staged_file_digest, and max_depth behavior.
  - Side track pop is allowed only for the top frame.
  - Digest/scope drift blocks or warns according to the current phase contract.
  - Focused tests cover push, pop, current, inspect, repair, max depth, non-top pop, scope overlap, and digest drift.
- forbidden_actions:
  - Do not allow non-top side track pop.
  - Do not allow unallowed staged file overlap to resume normal work.
  - Do not allow unexplained digest drift to resume normal work without the required warning or block.
- unresolved_or_design_deferred_items:
  - Phase 3 may warn on some side-track drift while Phase 5 blocks; this implementation target is Phase 3 and must not claim Phase 5 behavior unless implemented.
  - Future runtime location may replace stages/in-progress/side-track-stack.yaml, but read-only and mutating operations must stay separated.
- unresolved_items_review_rule: If the target claims resolved behavior for an unresolved item without implementation evidence, report WARN or ERROR according to impact.
- intended_target_phase_transfer:
  - Implementation should expose side track stack state handling and focused tests for scope, top-frame, return target, and digest drift behavior.


## Vertical Intent Transfer Customization

Phase chain:

- requirements.md -> design.md -> tasks.md -> implementation

Use upstream materials only for background and transfer checking. Limit target judgment to the current phase artifact.

## Required Checks

1. Check the target against the single judgment item: Req 14 side track stack implementation upstream transfer.
2. Check that the target satisfies preserved user review requirements.
3. Check that source materials are used only for background or required intent transfer.
4. Check that no finding depends on unstated assumptions or path-only source material.
5. Check that this review run and its model output do not approve or authorize commit, push, spec.json mutation, phase transition, or gate completion. This check constrains the review run and model output, not the mere presence or implementation of workflow-operation code; report target-code findings only when behavior bypasses or weakens the required gate.
6. Check each preserved review focus item:
  - side track stack scope and return target
  - staged file digest drift handling

## Out Of Scope

- approval gate behavior
- workflow-state snapshot behavior
- Do not approve or authorize commit, push, spec.json mutation, phase transition, or gate completion.
- These limits constrain this review run and the reviewing model; do not treat the mere presence or implementation of workflow-operation code as a violation solely because it mentions those operations.
- Do not judge downstream correctness unless a target omission would force downstream invention.

## Finding Policy

- Use CRITICAL for bypass of human-only approval or irreversible-operation boundaries.
- Use ERROR for missing required behavior, weakened user requirements, or unsupported target behavior.
- Use WARN for meaningful ambiguity, weak traceability, or coverage gaps.
- Use INFO only for minor non-blocking improvements.
- For each finding, identify the target file and the narrowest available location such as line number, function, schema field, or test case.
- Traceable evidence means a target file plus the narrowest available anchor for every checked claim, such as a line number, function name, schema field, CLI option, fixture, or test case.
- Return findings: [] if and only if every required check passes with traceable evidence and no deviation from the preserved review requirements or upstream intent.
