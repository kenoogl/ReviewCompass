---
criteria_id: workflow-management-design-reopen-protocol-transfer-review-criteria
phase: design
status: draft_for_prompt_quality_review
---

# workflow-management design reopen-protocol-transfer API Review Criteria

## Review Task

Review the target for: reopen protocol requirements-to-design transfer.

Primary judgment question:

Does the target satisfy reopen protocol requirements-to-design transfer, while carrying upstream purpose, responsibility boundaries, acceptance criteria, forbidden actions, unresolved items, and intended transfer without any of the following?

- omission
- weakening
- contradiction
- unsupported addition
- drift

Limit findings to this judgment item.

## User Review Requirements

- Review purpose: design triad-review for reopen protocol mechanization
- Review object: design.md
- Review focus:
  - requirements-to-design vertical transfer
  - edited phase full gate chain
  - downstream impact decision evidence
  - fail-closed next/finalize/commit detection order
  - Requirement 12 next output contract
  - Requirement 16 proxy and human-only priority boundary
- Scope boundaries:
  - In scope:
    - design.md transfer of requirements and workflow guidance
  - Out of scope:
    - tasks.md correctness
    - implementation code correctness
    - runner/test behavior correctness
    - spec.json update
    - phase or gate completion
    - commit or push authorization
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

- `.reviewcompass/specs/workflow-management/design.md`

At the actual review-run, pass every path listed here as --target. The API runner reads and injects those file contents into the model prompt; this section is the target manifest, not a substitute for target content.
If any listed target path content is absent from the injected prompt, report ERROR against Review Target and do not return findings: [].

Do not treat this criteria file, a wrapper, or an author-written summary as a substitute for the target.

## Source Materials

### requirements-contract

Purpose: Upstream canonical requirements that design.md must carry into the design layer.

- source_paths:
  - .reviewcompass/specs/workflow-management/requirements.md
- source_paths_note: source_paths are provenance only; use the structured summary fields below as the model-readable upstream intent material.

Structured Summary (model-readable upstream intent):

- purpose: Verify that design.md carries the reopen protocol mechanization contract from requirements.md into design without omission, weakening, contradiction, unsupported addition, target/source confusion, or authorization drift.

- responsibility_boundaries:
  - design.md is the review target; requirements.md is source material.
  - tasks.md, implementation code, runner behavior, spec.json update, gate completion, commit, and push are out of scope for correctness judgment at this design gate.
  - `next --json` is the normal early detector; `reopen-finalize` is the completion guard; commit preflight is only the final guard.
  - proxy_model may assist finding triage but must not authorize human-only decisions or irreversible operations.
- acceptance_criteria:
  - Requirement 5 acceptance 7 requires `edited_phases` and `impacted_downstream_phases` in reopen state.
  - Each phase in `edited_phases` must rerun `triad-review`, `review-wave`, `alignment`, and `approval`.
  - Downstream `no_impact` and `existing_sufficient` decisions still require gate, feature scope, decision, rationale, and evidence.
  - `next --json` must detect missing edited phase gates or downstream decisions before normal completion.
  - `reopen-finalize` must recompute required gates and decisions before creating a completed reopen record.
  - Already-pushed incomplete completed reopen records are handled by superseding reopen records, not silent history rewriting.
  - Requirement 12 acceptance 13 exact field list: 「現在の本線、次に実行すべき `required_action`、phase、stage、reopen scope、impact review scope、 direct features、indirect features、flag policy、`next_pending_gate`、 `next_drafting_gate`、`pending_gates`、`completed_gates`、superseded gate の有無、参照した state files」.

  - Requirement 12 requires WARN or DEVIATION, not OK, when reopen scope or impact review scope is missing, contradictory, stale, or inconsistent with feature_impact_decisions, spec.json, pending_gates, drafting_completed_gates, or downstream_impact_decisions.
  - Requirement 14 acceptance 11 keeps commit, push, spec.json update, phase approval, reopen finalize, and approval_required irreversible operation authorization human-only.
  - Requirement 16 acceptance 13-14 makes evidence completeness, finding/cluster coverage, approval gate record, approval_required operation contract, review-wave impact evidence, and human-only boundary determine proxy applicability.
  - Human-only decision boundary, unresolved approval gate, approval_required:true operations, and unresolved review-wave impact evidence take priority over proxy applicability; triage leave-as-is or proxy approved cannot cancel human-required evidence.
- forbidden_actions:
  - Do not treat design target excerpts or preanalysis claims as proof that design.md satisfies the requirements.
  - Do not allow proxy_model to authorize commit, push, spec.json update, phase/gate completion, reopen finalize, or human approval delegation.
  - Do not use current implementation behavior as normative source unless criteria embeds approved code/test excerpts for a supporting behavior-path question.
- unresolved_or_design_deferred_items:
  - The actual correctness of tasks.md, implementation code, runner behavior, and current tests is deferred to downstream gates.
- unresolved_items_review_rule: If the target claims resolved behavior for an unresolved item without implementation evidence, report WARN or ERROR according to impact.
- intended_target_phase_transfer:
  - design.md must define the design model for edited phase full gate chains, downstream impact decision evidence, fail-closed detection surfaces, active reopen/impact scope separation, Requirement 12 next output, and proxy/human-only authorization boundaries.

### reopen-procedure-and-review-guidance

Purpose: Workflow guidance governing reopen and design triad-review scope.

- source_paths:
  - .reviewcompass/guidance/REOPEN_PROCEDURE.md
  - .reviewcompass/guidance/SESSION_WORKFLOW_GUIDE.md#vertical-intent-transfer-review
  - .reviewcompass/guidance/SESSION_WORKFLOW_GUIDE.md#3.3-a-2
  - .reviewcompass/guidance/API_REVIEW_PROMPT_QUALITY.md
- source_paths_note: source_paths are provenance only; use the structured summary fields below as the model-readable upstream intent material.

Structured Summary (model-readable upstream intent):

- purpose: Preserve the protocol order and review-scope boundaries while drafting and reviewing design-stage criteria for the active reopen.

- responsibility_boundaries:
  - A phase whose canonical text was substantially changed must rerun triad-review, review-wave, alignment, and approval.
  - Design review checks requirements.md to design.md transfer; downstream artifact correctness is not judged.
  - Source materials must not be path-only and must separate purpose, boundaries, acceptance criteria, forbidden actions, unresolved items, and target-phase transfer.
  - After actual review-run, user-visible triage is required before proxy_model, implementation edits, spec.json update, or phase movement.
- acceptance_criteria:
  - REOPEN_PROCEDURE 第3過程 requires drafting before triad-review when canonical text is edited and triad-review is the first pending review gate.
  - REOPEN_PROCEDURE 第3過程 requires downstream impact decisions for requirements, design, tasks, and implementation edits, including no-change decisions.
  - REOPEN_PROCEDURE 第4過程 requires feature_impact_decisions, new_feature_decision, impacted_downstream_phases, and downstream_impact_decisions covering pending gates before completion.
  - SESSION_WORKFLOW_GUIDE vertical review requires checking upstream purpose, responsibility boundaries, acceptance criteria, and forbidden actions for omission, weakening, drift, or unsupported additions.
  - API_REVIEW_PROMPT_QUALITY requires main preanalysis, preanalysis sufficiency audit, criteria draft, prompt quality review, actual review-run, and user-visible triage in order.
- forbidden_actions:
  - Do not start actual review-run before criteria draft and prompt quality review.
  - Do not treat prompt-quality-run or preanalysis audit as gate completion.
  - Do not call proxy_model or update spec.json before the user-visible triage gate after actual review-run.
- unresolved_or_design_deferred_items:
  - Actual design review findings are deferred until prompt-quality-approved criteria are used in the actual review-run.
- unresolved_items_review_rule: If the target claims resolved behavior for an unresolved item without implementation evidence, report WARN or ERROR according to impact.
- intended_target_phase_transfer:
  - The criteria must preserve design target/source/out-of-scope separation and must prevent premature gate completion or irreversible operation authorization.

### active-reopen-state

Purpose: Current machine state for the active reopen design triad-review.

- source_paths:
  - stages/in-progress/reopen-procedure-2026-07-01.yaml
  - .reviewcompass/specs/workflow-management/spec.json
- source_paths_note: source_paths are provenance only; use the structured summary fields below as the model-readable upstream intent material.

Structured Summary (model-readable upstream intent):

- purpose: Provide active scope and state context for the design criteria without turning state files into review targets.

- responsibility_boundaries:
  - Active gate is `stages/design.yaml#triad-review`.
  - Requirements gates are completed; design drafting is completed.
  - Design/tasks/implementation triad-review, review-wave, alignment, and approval remain pending.
  - spec.json design/tasks/implementation workflow flags remain false through approval.
- acceptance_criteria:
  - The criteria must treat `.reviewcompass/specs/workflow-management/design.md` as the only actual design review target.
  - The criteria must keep active reopen scope distinct from historical `spec.json.reopened`.
  - The criteria must check active reopen scope and impact review scope only as source context for design transfer.
- forbidden_actions:
  - Do not mutate workflow_state, spec.json, pending_gates, or completed_gates from criteria generation.
  - Do not advance `stages/design.yaml#triad-review` from criteria generation.
- unresolved_or_design_deferred_items:
  - Whether design.md passes actual triad-review remains unresolved until actual review-run and user-visible triage.
- unresolved_items_review_rule: If the target claims resolved behavior for an unresolved item without implementation evidence, report WARN or ERROR according to impact.
- intended_target_phase_transfer:
  - The criteria should direct reviewers to inspect design.md for active scope, downstream impact decision, next output, and human-only authorization design responsibilities.


## Vertical Intent Transfer Customization

Phase chain:

- requirements.md -> design.md

Use upstream materials only for background and transfer checking. Limit target judgment to the current phase artifact.

## Required Prompt Changes From Preanalysis Audit

The preanalysis sufficiency audit required the following prompt changes. Treat these as mandatory criteria-draft constraints, not optional advice.

- Add a structurally distinct PROHIBITED ACTIONS block to the criteria that explicitly lists: commit, push, spec.json update, phase approval, gate completion, phase completion, reopen finalize, proxy_model decision authorization, human approval delegation, and unapproved specification changes. Do not rely on prose-only prohibition buried in meta-checks.
- Add an explicit instruction that design.md target excerpt presence in the bundle is not evidence of correct requirements transfer; the later reviewer must judge the full target file independently and must not treat excerpt inclusion as confirmation.
- Generalize the missing-section finding condition (currently only stated for Claim 8 / proxy_model) to all required design sections. If a required design section is absent or cannot be located, the reviewer must treat absence as a potential finding rather than treating the check as vacuously satisfied.
- Embed the exact Requirement 12 acceptance 13 Japanese field enumeration verbatim in the criteria rather than paraphrasing it, to prevent paraphrase drift in the later review-run.
- Add an explicit finding condition for Requirement 16 acceptance 13-14 priority ordering: the later reviewer must check whether design.md states that human-only decision boundary, unresolved approval gate, approval_required:true operations, and unresolved review-wave impact evidence each take priority over proxy applicability, and that triage leave-as-is or proxy approved cannot cancel human-required evidence.
- Remove or demote 'behavior-path source summary' from co-equal source status in Claim 4 of the preanalysis before criteria draft, or add an explicit note in the criteria that behavior-path paths are provenance hints only and no finding may depend on unapproved implementation behavior.
- Embed the run_review.py output contract (verdict, reviewed_target, source_materials_used, findings, out_of_scope_not_judged; findings fields: severity, target_location, description, rationale, source_materials) explicitly in the criteria file, not only referenced in a meta-check.
- Add a direct instruction in the criteria that the preanalysis claim list is hypothesis context only and must not be used as an exhaustive checklist, coverage proof, or answer key by the later reviewer.

## Missing Section Handling

- If a named target section is absent, renamed, or structurally reorganized, search the full target file for equivalent design responsibility.
- If the responsibility cannot be located, report a finding instead of treating the missing anchor as a pass.
- Do not use absence of a named anchor as a reason to skip the check.

## Target Excerpt Handling

- Any target excerpt presence is not evidence of correct requirements transfer.
- Judge the full target file independently.
- Do not treat excerpt inclusion in preparation materials as confirmation that the target satisfies the source contract.

## Preanalysis Handling

- Treat the preanalysis claim list as hypothesis context only.
- Do not use the preanalysis as an exhaustive checklist, answer key, or coverage proof.
- Derive findings independently from source materials and the full target.

## PROHIBITED ACTIONS

- commit
- push
- spec.json update
- phase approval
- gate completion
- phase completion
- reopen finalize
- proxy_model decision authorization
- human approval delegation
- implementation edits
- unapproved specification changes

## Output Contract

Return YAML with these top-level fields:

- `verdict`
- `reviewed_target`
- `source_materials_used`
- `findings`
- `out_of_scope_not_judged`

Each `findings` item must contain:

- `severity`: one of `CRITICAL`, `ERROR`, `WARN`, `INFO`
- `target_location`
- `description`
- `rationale`
- `source_materials`

## Required Checks

1. Check the target against the single judgment item: reopen protocol requirements-to-design transfer.
2. Check that the target satisfies preserved user review requirements.
3. Check that source materials are used only for background or required intent transfer.
4. Check that no finding depends on unstated assumptions or path-only source material.
5. Check that this review run and its model output do not approve or authorize commit, push, spec.json mutation, phase transition, or gate completion. This check constrains the review run and model output, not the mere presence or implementation of workflow-operation code; report target-code findings only when behavior bypasses or weakens the required gate.
6. Check each preserved review focus item:
  - requirements-to-design vertical transfer
  - edited phase full gate chain
  - downstream impact decision evidence
  - fail-closed next/finalize/commit detection order
  - Requirement 12 next output contract
  - Requirement 16 proxy and human-only priority boundary

## Out Of Scope

- tasks.md correctness
- implementation code correctness
- runner/test behavior correctness
- spec.json update
- phase or gate completion
- commit or push authorization
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
