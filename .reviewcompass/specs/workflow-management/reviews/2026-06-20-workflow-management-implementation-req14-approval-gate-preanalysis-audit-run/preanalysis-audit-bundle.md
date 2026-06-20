---
bundle_id: workflow-management-implementation-req14-approval-gate-preanalysis-audit
phase: prompt-quality
target_proposed_review_criteria: .reviewcompass/specs/workflow-management/reviews/2026-06-20-workflow-management-implementation-req14-approval-gate-criteria-run/review-criteria.md
main_preanalysis: .reviewcompass/specs/workflow-management/reviews/2026-06-20-workflow-management-implementation-review-run/review-preanalysis.yaml
source_materials: .reviewcompass/specs/workflow-management/reviews/2026-06-20-workflow-management-implementation-review-run/source-materials/req14-approval-gate-source-materials.yaml
status: draft_for_preanalysis_sufficiency_audit
---

# Preanalysis Audit Bundle: Req14 Approval Gate

This bundle is the target for `main-preanalysis-sufficiency-audit`.

The reviewer must not judge the implementation artifacts themselves. The reviewer must judge whether the proposed API review criteria can support a later implementation review.

## User And Workflow Review Requirement

- Review purpose: workflow-management implementation triad-review preparation.
- Review object: proposed API review criteria for Req 14 approval gate implementation upstream transfer.
- Review focus:
  - approval/proxy human-only boundary
  - approval decision binding and digest checks
- Scope boundary:
  - In scope: approval gate schema, implementation, CLI integration, and focused tests as the future implementation review target.
  - Out of scope: side track stack behavior, workflow-state snapshot behavior, commit, push, spec.json update, phase completion, and actual implementation triage.
- Required method:
  - Use source materials as upstream intent.
  - Use main preanalysis as a hypothesis and source-discovery aid, not as an answer key.
  - Check whether the proposed criteria gives a later API reviewer enough information to independently judge the implementation target.

## Source Materials

The following source material is model-readable upstream intent for Req 14 approval gate.

```yaml
source_materials:
  - key: workflow-management-req14-approval-gate-upstream-intent
    purpose: Requirement 14 / design / tasks intent for approval gates and human-only approval boundaries.
    source_paths:
      - .reviewcompass/specs/workflow-management/requirements.md
      - .reviewcompass/specs/workflow-management/design.md
      - .reviewcompass/specs/workflow-management/tasks.md
    source_anchors:
      - .reviewcompass/specs/workflow-management/requirements.md sha256:e7621e6d56a3ef42085e2864a88366d670e55c304668dd21f48dde32411e13f3
      - .reviewcompass/specs/workflow-management/design.md sha256:ac6bd42e57b507a615af3ed6a40f3c031f56fe75f27e7f1fcc12ddcb4dc46558
      - .reviewcompass/specs/workflow-management/tasks.md sha256:053858cf4abf94bd7b54bf8a45a8ca9504afef39ea8be48bd282193f95e84098
    purpose_field: Treat irreversible-operation approval as machine-readable state, not as implicit LLM conversation context.
    responsibility_boundaries:
      - Approval gate records distinguish approved, rejected, deferred, and changes_requested decisions and bind them to the target operation, required_action, artifact or staged file set digest, actor, time, and source.
      - record_human_decision records a decision but does not itself authorize the target operation; next --json decides whether to proceed, stay blocked, redraft, or repair.
      - proxy_model may support triage or advisory judgments, but commit, push, spec.json update, phase approval, reopen finalize, and approval_required irreversible operations remain human-only.
    acceptance_criteria:
      - Approval gate schema and implementation enforce decision_scope, binding_kind, digest binding, source metadata, and non-approved decision blocking.
      - proxy_model decisions cannot satisfy human_only decisions and cannot replace human approval.
      - Focused tests cover approved, rejected, deferred, changes_requested, stale digest, wrong actor/source, and proxy/human boundary behavior.
    forbidden_actions:
      - Do not treat record_human_decision completion as target-operation approval.
      - Do not let proxy_model pass a human_only approval boundary.
      - Do not use binding_kind none for approval-required irreversible operations.
    unresolved_or_design_deferred_items:
      - No approval-gate-specific deferred item may weaken the human-only approval boundary in the current implementation.
    intended_target_phase_transfer:
      - Implementation should expose approval gate validation and tests covering human/proxy boundaries, digest binding, and non-approved decision blocking.
```

## Main Preanalysis Excerpt

The main session LLM produced this relevant preanalysis. Treat it as a hypothesis, not as ground truth.

```yaml
candidate_judgment_item:
  item_id: req14_approval_gate
  judgment_question: Does Req 14 approval gate implementation preserve upstream human-only approval, decision binding, digest binding, and non-approved blocking behavior?
  recommended_split: standalone
  target_files:
    - .reviewcompass/schema/approval_gate.schema.json
    - tools/check-workflow-action.py
    - tools/check_workflow_action/approval_gate.py
    - tests/workflow-management/test_approval_gate.py
  source_materials:
    - .reviewcompass/specs/workflow-management/reviews/2026-06-20-workflow-management-implementation-review-run/source-materials/req14-approval-gate-source-materials.yaml
  out_of_scope:
    - side track stack behavior
    - workflow-state snapshot behavior
  prompt_requirements:
    - Do not turn review-run prohibited actions into target-code false positives.
    - Report target-code issues only when behavior bypasses or weakens approval gates.
useful_discoveries:
  - id: preanalysis-002
    severity: ERROR
    finding: Req 14 cannot be reviewed as one combined judgment.
    impact: API prompts should split Req 14 into approval-gate, side-track-stack, and workflow-state-snapshot criteria.
  - id: preanalysis-005
    severity: WARN
    finding: Verification snapshots should not be passed as bare pass-count assertions.
    impact: API prompts should include actual command output excerpts or structured test coverage summaries, and should not imply that passing tests are proof of correctness.
```

## Proposed API Review Criteria

The following proposed criteria is the object being audited for sufficiency.

```markdown
---
criteria_id: workflow-management-implementation-req14-approval-gate-transfer-review-criteria
phase: implementation
status: draft_for_prompt_quality_review
---

# workflow-management implementation req14-approval-gate-transfer API Review Criteria

## Review Task

Review the target for: Req 14 approval gate implementation upstream transfer.

Primary judgment question:

Does the target satisfy Req 14 approval gate implementation upstream transfer, while carrying upstream purpose, responsibility boundaries, acceptance criteria, forbidden actions, unresolved items, and intended transfer without any of the following?

- omission
- weakening
- contradiction
- unsupported addition
- drift

Limit findings to this judgment item.

## User Review Requirements

- Review purpose: workflow-management implementation triad-review
- Review object: Req 14 approval gate implementation artifacts
- Review focus:
  - approval/proxy human-only boundary
  - approval decision binding and digest checks
- Scope boundaries:
  - In scope:
    - approval gate schema, implementation, CLI integration, and focused tests
  - Out of scope:
    - side track stack behavior
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

- `.reviewcompass/schema/approval_gate.schema.json`
- `tools/check-workflow-action.py`
- `tools/check_workflow_action/approval_gate.py`
- `tests/workflow-management/test_approval_gate.py`

At the actual review-run, pass every path listed here as --target. The API runner reads and injects those file contents into the model prompt; this section is the target manifest, not a substitute for target content.
If any listed target path content is absent from the injected prompt, report ERROR against Review Target and do not return findings: [].

Do not treat this criteria file, a wrapper, or an author-written summary as a substitute for the target.

## Source Materials

### workflow-management-req14-approval-gate-upstream-intent

Purpose: Requirement 14 / design / tasks intent for approval gates and human-only approval boundaries.

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

- purpose: Treat irreversible-operation approval as machine-readable state, not as implicit LLM conversation context.
- responsibility_boundaries:
  - Approval gate records distinguish approved, rejected, deferred, and changes_requested decisions and bind them to the target operation, required_action, artifact or staged file set digest, actor, time, and source.
  - record_human_decision records a decision but does not itself authorize the target operation; next --json decides whether to proceed, stay blocked, redraft, or repair.
  - proxy_model may support triage or advisory judgments, but commit, push, spec.json update, phase approval, reopen finalize, and approval_required irreversible operations remain human-only.
- acceptance_criteria:
  - Approval gate schema and implementation enforce decision_scope, binding_kind, digest binding, source metadata, and non-approved decision blocking.
  - proxy_model decisions cannot satisfy human_only decisions and cannot replace human approval.
  - Focused tests cover approved, rejected, deferred, changes_requested, stale digest, wrong actor/source, and proxy/human boundary behavior.
- forbidden_actions:
  - Do not treat record_human_decision completion as target-operation approval.
  - Do not let proxy_model pass a human_only approval boundary.
  - Do not use binding_kind none for approval-required irreversible operations.
- unresolved_or_design_deferred_items:
  - No approval-gate-specific deferred item may weaken the human-only approval boundary in the current implementation.
- unresolved_items_review_rule: If the target claims resolved behavior for an unresolved item without implementation evidence, report WARN or ERROR according to impact.
- intended_target_phase_transfer:
  - Implementation should expose approval gate validation and tests covering human/proxy boundaries, digest binding, and non-approved decision blocking.

## Vertical Intent Transfer Customization

Phase chain:

- requirements.md -> design.md -> tasks.md -> implementation

Use upstream materials only for background and transfer checking. Limit target judgment to the current phase artifact.

## Required Checks

1. Check the target against the single judgment item: Req 14 approval gate implementation upstream transfer.
2. Check that the target satisfies preserved user review requirements.
3. Check that source materials are used only for background or required intent transfer.
4. Check that no finding depends on unstated assumptions or path-only source material.
5. Check that this review run and its model output do not approve or authorize commit, push, spec.json mutation, phase transition, or gate completion. This check constrains the review run and model output, not the mere presence or implementation of workflow-operation code; report target-code findings only when behavior bypasses or weakens the required gate.
6. Check each preserved review focus item:
  - approval/proxy human-only boundary
  - approval decision binding and digest checks

## Out Of Scope

- side track stack behavior
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
```

## Prior Prompt-Quality Evidence

This prior judgment is context for the audit. It is not ground truth.

```yaml
role: judgment
provider: gemini-api
model: gemini-3.1-pro-preview
findings:
  - severity: WARN
    target_location: Source Materials / source_paths_note
    description: Structured summary lacks cross-references to original source documents.
    rationale: The structured summary is the sole model-readable upstream intent material. Without a cross-reference mapping its fields back to specific source documents and sections, the reviewing model has no way to detect if the summary omits or misrepresents material details from the originals.
  - severity: WARN
    target_location: Required Checks / Check 5 and Out Of Scope
    description: Repeated carve-outs risk suppressing findings about critical boundary-weakening code.
    rationale: The prompt explicitly instructs the model not to treat mere presence as a violation and to report target-code findings only when behavior bypasses or weakens the gate. This may make the model overly lenient and miss real gate bypasses.
  - severity: INFO
    target_location: Review Target / Target manifest note
    description: Instructs the model to emit an ERROR instead of a CRITICAL when target path content is absent.
    rationale: A missing target artifact makes the entire API review invalid.
  - severity: INFO
    target_location: Source Materials / source_anchors
    description: SHA256 source anchors are inert and lack evaluation instructions.
    rationale: The anchors are provenance, but no instruction makes them actionable.
```
