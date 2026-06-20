---
criteria_id: workflow-management-implementation-req16-phase-proxy-triage-transfer-review-criteria
phase: implementation
status: prompt_quality_reviewed_nonblocking_warnings_addressed
---

# workflow-management implementation req16-phase-proxy-triage-transfer API Review Criteria

## Review Task

Review the target for: Req 16 implementation upstream transfer for phased implementation and proxy triage decision mechanics.

Primary judgment question:

Does the target satisfy Req 16 implementation upstream transfer for phased implementation and proxy triage decision mechanics, while carrying upstream purpose, responsibility boundaries, acceptance criteria, forbidden actions, unresolved items, and intended transfer without omission, weakening, contradiction, unsupported addition, or drift?

Do not combine multiple independent judgments in this prompt. If another cluster, finding, artifact, or design-policy judgment is needed, create a separate criteria file and run separate prompt-quality review.

## User Review Requirements

- Review purpose: workflow-management implementation triad-review
- Review object: Req 16 implementation artifacts
- Review focus:
  - Phase 0 to 6 separation and read-only boundaries
  - proxy decision evidence completeness and coverage
  - human-required predicate priority
- Scope boundaries:
  - In scope:
    - Req 16 schemas, implementation, operation contract connections, and focused tests
  - Out of scope:
    - Req 14 side track state implementation
    - Req 15 prompt audit implementation
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
  - Prohibited actions -> Out Of Scope and Finding Policy

## Generic API Review Core

- Keep criteria and target roles distinct.
- Treat the target files as the only review target.
- Treat source materials as background or intent-transfer evidence, not as targets.
- Do not use path-only source materials as model-readable evidence.
- Ask one non-leading primary judgment question.
- Preserve user review requirements without narrowing, broadening, or replacement.
- Exclude credentials, personal identifiers, third-party non-sendable confidential material, and unrelated logs.
- Return parser-compatible findings only.

## Review Target

The authoritative target file set is
`.reviewcompass/specs/workflow-management/reviews/2026-06-20-workflow-management-implementation-review-run/req16-review-target-manifest.md`
and the target files supplied by the review runner. The list below is an orientation
copy only; if it diverges from the manifest or runner target set, treat the manifest
and runner target set as authoritative and report the mismatch.

- `.reviewcompass/schema/implementation_phase.schema.json`
- `.reviewcompass/schema/proxy_triage_decision.schema.json`
- `.reviewcompass/schema/operation_contract.schema.json`
- `.reviewcompass/schema/required_action.schema.json`
- `tools/check-workflow-action.py`
- `tools/check_workflow_action/implementation_phases.py`
- `tools/check_workflow_action/operation_contracts.py`
- `tools/check_workflow_action/operation_list.py`
- `tools/check_workflow_action/operation_registry.py`
- `tools/check_workflow_action/proxy_triage_decisions.py`
- `tests/workflow-management/test_implementation_phase_plan.py`
- `tests/workflow-management/test_operation_list_read_only.py`
- `tests/workflow-management/test_proxy_triage_decision_machine.py`
- `tests/workflow-management/test_review_wave_consumer_impact.py`
- `tests/workflow-management/test_implementation_phase_cli.py`
- `tests/workflow-management/test_operation_contract_cli.py`
- `tests/workflow-management/test_operation_contract_schema.py`
- `tests/workflow-management/test_required_action_contract_mapping.py`

Do not treat this criteria file, a wrapper, or an author-written summary as a substitute for the target.

## Source Materials

### workflow-management-req16-upstream-intent

Purpose: Requirement 16 / design / tasks intent for phased implementation and proxy_model triage decision mechanics.
This is a structured summary of the upstream phase chain, paraphrased from
`.reviewcompass/specs/workflow-management/requirements.md`,
`.reviewcompass/specs/workflow-management/design.md`, and
`.reviewcompass/specs/workflow-management/tasks.md`. Use it as intent-transfer
evidence; do not treat it as a replacement for target files.

- purpose: Separate selection-layer and execution-layer mechanization into Phase 0 to Phase 6 so TDD implementation does not mix unrelated behavior or break existing workflow.
- responsibility_boundaries:
  - Phase 0 owns D-003 action selection, required_action uniqueness, invariants, reopen plan compiler, and workflow-state repair detection.
  - Phase 1 owns schemas without changing runtime behavior.
  - Phase 2 owns read-only registry / operation-list behavior and must not mutate next --json state.
  - Phase 3 owns advisory preflight; Phase 5 promotes selected warnings to mechanical blocking.
  - Phase 4 owns structured prompt generation; Phase 6 owns advisory LLM judge audit.
  - proxy_model triage decision mechanics depend on evidence completeness, finding/cluster coverage, approval gate records, operation contracts, review-wave impact evidence, and human-only boundaries, not provider or model name.
- acceptance_criteria:
  - Phase plan covers Phase 0 through Phase 6 in order, with entry criteria, exit criteria, allowed operations, forbidden operations, required tests, and commit boundary.
  - implementation-phase-check fails on missing phase coverage, order violations, unmet criteria, forbidden operation evidence, and stale or missing required snapshot evidence.
  - operation-list exposes read-only registry fields such as canonical commands, effect_kind, approval_required, sequence, and pending conflicts without changing next --json.
  - proxy triage decision records raw response, prompt, candidates, selected decision, reason, final target, coverage, and mapping.
  - human-required predicate blocks proxy application when decision_scope is human_only, approval gate is unresolved, operation approval_required is true, review-wave impact evidence is unresolved, or required evidence is missing or conflicting.
  - spec.json.reopened is treated as history, not active reopen scope.
- forbidden_actions:
  - Do not mix multiple implementation phases into one completion claim.
  - Do not treat provider or model identity as the proxy decision safety basis.
  - Do not allow leave-as-is, proxy_approved, or selected proxy decision to override human-required evidence.
  - Do not treat review_triage_decide approval as apply-fixes approval when scopes differ.
  - Do not treat review-wave consumer impact as complete without carry-forward or downstream impact evidence.
- unresolved_or_design_deferred_items:
  - Later phases may be advisory until mechanical blocking is intentionally enabled.
  - Existing proxy decision artifact formats may need mapping before a single schema can cover all historical runs.
- intended_target_phase_transfer:
  - Implementation should provide phase plan schema/checking, read-only operation-list, proxy triage decision validation, human-required predicate checks, and review-wave consumer impact checks.
  - Implementation review should verify schemas, tools, and focused tests listed in req16-review-target-manifest.md against this intent.

### req16-verification-context

Verification snapshots are smoke evidence only. Passing tests are not proof of
correctness and must not suppress findings. Use the target test files themselves
to evaluate whether the boundaries are meaningfully covered.

- `test_implementation_phase_plan.py` and `test_implementation_phase_cli.py`: cover phase plan schema/check behavior and CLI reporting.
- `test_operation_list_read_only.py`: covers read-only operation-list behavior and no state mutation from listing.
- `test_proxy_triage_decision_machine.py`: covers proxy decision record validation, evidence completeness, final target mapping, and human-required blocking predicates.
- `test_review_wave_consumer_impact.py`: covers review-wave consumer impact / downstream evidence checks.
- `test_operation_contract_cli.py`, `test_operation_contract_schema.py`, and `test_required_action_contract_mapping.py`: cover operation contract schema, mapping, registry drift, and required_action coverage.

### req14-req15-minimal-source-evidence-for-req16

Req14 and Req15 internals are not review targets. They are source evidence only
where Req16 explicitly depends on them.

- Req14 approval-gate evidence expected by Req16 proxy blocking:
  - approval decisions carry `decision_scope`, `decided_by`, `decision`,
    `target_operation_id`, `target_required_action`, digest binding fields,
    `next_action_expectation`, and `consumed`
  - `human_only` approval cannot be satisfied by `proxy_model` or `llm`
  - non-approved decisions do not authorize target operations
  - approval-required operation contracts must force human-required handling
- Req15 structured-prompt evidence expected by Req16 proxy decision checks:
  - prompt/effective-prompt metadata has path and sha256 traceability
  - prompt audit output is advisory unless an explicit gate consumes it
  - language-task material is separated from machine-operation authorization

Do not review full Req14 or Req15 correctness beyond these dependency points.

### review-wave-impact-evidence-definition

For Required Check 7 and review-wave consumer impact behavior, sufficient evidence
means the target preserves enough machine-readable state or records to distinguish:

- no downstream consumer impact
- downstream impact carried forward with a target feature or phase
- unresolved carry-forward item that must block proxy application or phase movement
- resolved downstream impact with evidence path or decision record

If the implementation treats a missing or conflicting carry-forward / downstream
impact record as complete, report it.

## Vertical Intent Transfer Customization

Phase chain:

- requirements.md -> design.md -> tasks.md -> implementation

Use upstream materials only for background and transfer checking. Limit target judgment to the current phase artifact.

## Required Checks

1. Check the target against the single judgment item: Req 16 implementation upstream transfer for phased implementation and proxy triage decision mechanics.
2. Check that the target satisfies preserved user review requirements.
3. Check that source materials are used only for background or required intent transfer.
4. Check that no finding depends on unstated assumptions or path-only source material.
5. Check that Req14 / Req15 dependency evidence is used only for the explicit Req16 proxy blocking predicates above.
6. Check that review-wave consumer impact handling distinguishes unresolved carry-forward from resolved/no-impact states.
7. Check that the target does not authorize commit, push, spec.json mutation, phase transition, or gate completion.

## Out Of Scope

- Req 14 side track state implementation
- Req 15 prompt audit implementation
- Do not approve or authorize commit, push, spec.json mutation, phase transition, or gate completion.
- Do not judge downstream correctness unless a target omission would force downstream invention.

## Finding Policy

- Use CRITICAL for bypass of human-only approval or irreversible-operation boundaries.
- Use ERROR for missing required behavior, weakened user requirements, or unsupported target behavior.
- Use WARN for meaningful ambiguity, weak traceability, or coverage gaps.
- Use INFO only for minor non-blocking improvements.
- Use precise target locations such as `path`, `path:function`, or `path:section`.
- Return findings: [] only when the target is traceable, correctly scoped, and sufficiently grounded.
