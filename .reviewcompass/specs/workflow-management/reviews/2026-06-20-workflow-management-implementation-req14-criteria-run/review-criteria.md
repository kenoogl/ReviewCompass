---
criteria_id: workflow-management-implementation-req14-approval-side-track-snapshot-transfer-review-criteria
phase: implementation
status: draft_for_prompt_quality_review
---

# workflow-management implementation req14-approval-side-track-snapshot-transfer API Review Criteria

## Review Task

Review the target for: Req 14 implementation upstream transfer for approval gates, side track stack, and workflow-state snapshot.

Primary judgment question:

Does the target satisfy Req 14 implementation upstream transfer for approval gates, side track stack, and workflow-state snapshot, while carrying upstream purpose, responsibility boundaries, acceptance criteria, forbidden actions, unresolved items, and intended transfer without any of the following?

- omission
- weakening
- contradiction
- unsupported addition
- drift

Limit findings to this judgment item.

## User Review Requirements

- Review purpose: workflow-management implementation triad-review
- Review object: Req 14 implementation artifacts
- Review focus:
  - approval/proxy human-only boundary
  - side track stack scope and digest drift
  - workflow-state snapshot as non-authoritative audit aid
- Scope boundaries:
  - In scope:
    - Req 14 schemas, implementation, and focused tests
  - Out of scope:
    - Req 15 structured effective prompt
    - Req 16 proxy triage decision mechanics
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

- `.reviewcompass/schema/approval_gate.schema.json`
- `.reviewcompass/schema/side_track_stack.schema.json`
- `.reviewcompass/schema/workflow_state_snapshot.schema.json`
- `tools/check-workflow-action.py`
- `tools/check_workflow_action/approval_gate.py`
- `tools/check_workflow_action/side_track_stack.py`
- `tools/check_workflow_action/workflow_state_snapshot.py`
- `tests/workflow-management/test_approval_gate.py`
- `tests/workflow-management/test_side_track_stack.py`
- `tests/workflow-management/test_workflow_state_snapshot.py`
- `tests/workflow-management/test_workflow_snapshot_cli.py`

At the actual review-run, pass every path listed here as --target. The API runner reads and injects those file contents into the model prompt; this section is the target manifest, not a substitute for target content.
If any listed target path content is absent from the injected prompt, report ERROR against Review Target and do not return findings: [].

Do not treat this criteria file, a wrapper, or an author-written summary as a substitute for the target.

## Source Materials

### workflow-management-req14-upstream-intent

Purpose: Requirement 14 / design / tasks intent for approval gates, side track stack, and workflow-state snapshot.

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

- purpose: Treat irreversible-operation approval, unexpected side-track work, and current-state visualization as machine-readable state, not as implicit LLM conversation context.
- responsibility_boundaries:
  - Approval gate records distinguish approved, rejected, deferred, and changes_requested decisions and bind them to the target operation, required_action, artifact or staged file set digest, actor, time, and source.
  - record_human_decision records a decision but does not itself authorize the target operation; next --json decides whether to proceed, stay blocked, redraft, or repair.
  - proxy_model may support triage or advisory judgments, but commit, push, spec.json update, phase approval, reopen finalize, and approval_required irreversible operations remain human-only.
  - Side track stack state owns push, pop, current, inspect, repair, allowed scope/files, return target, staged file set, and digest checks.
  - Workflow-state snapshot is a visualization and audit aid derived from next --json, not the state authority.
- acceptance_criteria:
  - Approval gate schema and implementation enforce decision_scope, binding_kind, digest binding, source metadata, and non-approved decision blocking.
  - proxy_model decisions cannot satisfy human_only decisions and cannot replace human approval.
  - Side track frames include frame identity, parent, allowed scope/files, completion conditions, return_to, spawned_from, staged_file_set, staged_file_digest, and max_depth behavior.
  - Side track pop is allowed only for the top frame, and digest/scope drift blocks or warns according to phase.
  - Workflow-state snapshot includes current_work, active_side_tracks, git_tree_summary, post_write_manifest_summary, workflow_state_summary, and source_next_action linkage.
  - Snapshot consumers must recheck next --json and state refs before using it as an operation basis.
- forbidden_actions:
  - Do not treat record_human_decision completion as target-operation approval.
  - Do not let proxy_model pass a human_only approval boundary.
  - Do not use binding_kind none for approval-required irreversible operations.
  - Do not allow non-top side track pop, unallowed staged file overlap, or unexplained digest drift to resume normal work.
  - Do not treat workflow-state snapshot as the source of truth.
- unresolved_or_design_deferred_items:
  - Phase 3 may warn on some side-track drift while Phase 5 blocks; implementation must not claim Phase 5 behavior unless implemented.
  - Future runtime location may replace stages/in-progress/side-track-stack.yaml, but read-only and mutating operations must stay separated.
- unresolved_items_review_rule: If the target claims resolved behavior for an unresolved item without implementation evidence, report WARN or ERROR according to impact.
- intended_target_phase_transfer:
  - Implementation should expose approval gate validation, side track stack state handling, and workflow-state snapshot generation with tests covering human/proxy boundaries and drift checks.
  - Implementation review should verify schemas, tools, and focused tests listed in req14-review-target-manifest.md against the above intent.


## Vertical Intent Transfer Customization

Phase chain:

- requirements.md -> design.md -> tasks.md -> implementation

Use upstream materials only for background and transfer checking. Limit target judgment to the current phase artifact.

## Required Checks

1. Check the target against the single judgment item: Req 14 implementation upstream transfer for approval gates, side track stack, and workflow-state snapshot.
2. Check that the target satisfies preserved user review requirements.
3. Check that source materials are used only for background or required intent transfer.
4. Check that no finding depends on unstated assumptions or path-only source material.
5. Check that this review run and its model output do not approve or authorize commit, push, spec.json mutation, phase transition, or gate completion. This check constrains the review run and model output, not the mere presence or implementation of workflow-operation code; report target-code findings only when behavior bypasses or weakens the required gate.
6. Check each preserved review focus item:
  - approval/proxy human-only boundary
  - side track stack scope and digest drift
  - workflow-state snapshot as non-authoritative audit aid

## Out Of Scope

- Req 15 structured effective prompt
- Req 16 proxy triage decision mechanics
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
