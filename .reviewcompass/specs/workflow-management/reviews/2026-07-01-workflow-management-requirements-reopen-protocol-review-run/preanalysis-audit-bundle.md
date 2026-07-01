---
bundle_id: workflow-management-requirements-reopen-protocol-preanalysis-audit
phase: prompt-quality
target_proposed_review_criteria: .reviewcompass/specs/workflow-management/reviews/2026-07-01-workflow-management-requirements-reopen-protocol-review-run/proposed-review-criteria-outline.md
main_preanalysis: .reviewcompass/specs/workflow-management/reviews/2026-07-01-workflow-management-requirements-reopen-protocol-review-run/main-preanalysis.md
source_materials: embedded
status: draft_for_preanalysis_sufficiency_audit
---

# Preanalysis Audit Bundle: workflow-management requirements reopen-protocol

This bundle is the target for `main-preanalysis-sufficiency-audit`.

The reviewer must not judge `requirements.md` itself yet. The reviewer must judge whether the main preanalysis and proposed API review criteria provide enough source material, scope control, judgment-item separation, and authority boundaries for a later requirements triad-review.

## User And Workflow Review Requirement

- Review purpose: `workflow-management` requirements triad-review preparation during an active reopen.
- Review object: proposed API review criteria for checking whether reopen protocol mechanization requirements were correctly transferred into `requirements.md`.
- Review focus:
  - edited phase full-gate re-execution
  - downstream impact decisions and evidence
  - fail-closed detection at `next --json`, `reopen-finalize`, and commit preflight
  - superseding reopen record policy
  - proxy_model / human-only authority boundary
  - requirements-stage target/source/out-of-scope separation
- Scope boundary:
  - In scope: whether the proposed criteria and main preanalysis are sufficient to support a later requirements review.
  - Out of scope: actual correctness of design.md, tasks.md, implementation code, runner behavior, `spec.json` update, phase transition, commit, push, proxy_model decision, or gate completion.
- Required method:
  - Use the embedded source materials to reconstruct the judgment item independently.
  - Treat main preanalysis as a hypothesis and source-discovery aid, not as an answer key.
  - Identify required prompt changes before the real review-run.

## Review Target Manifest

The later actual review-run target is only:

- `.reviewcompass/specs/workflow-management/requirements.md`

Expected relevant target locations:

- Requirement 3 acceptance criterion 5.
- Requirement 5 acceptance criterion 7.
- Requirement 16 acceptance criteria 11-14.
- Related in-target context: Requirement 2 acceptance criteria 9/13 and Requirement 9 acceptance criteria 3/5.

These target locations are not source material. The actual review-run must pass the full target file as target content.

## Source Materials

The following source material is model-readable context for the audit.

```yaml
source_materials:
  - key: reopen-protocol-mechanization-plan
    purpose: Upstream planning and user/workflow decision material for why this reopen exists.
    source_path: .reviewcompass/backlog/plans/plan-2026-07-01-reopen-protocol-mechanization-review.yaml
    problem:
      - A previous requirements-changing reopen did not rerun requirements triad-review and review-wave.
      - Downstream design/tasks/implementation impact was handled as late supplemental metadata.
      - Missing downstream decisions were detected too late, around finalize or commit.
    invariants:
      - id: RPMR-I1
        statement: edited_phases must be machine-readable.
      - id: RPMR-I2
        statement: edited phases require triad-review, review-wave, alignment, and approval.
      - id: RPMR-I3
        statement: upstream phase edits require impacted_downstream_phases and downstream_impact_decisions.
      - id: RPMR-I4
        statement: downstream no-change decisions still need gate, feature_scope, decision, rationale, and evidence.
      - id: RPMR-I5
        statement: next --json must return reopen missing work instead of normal completion when gates or decisions are missing.
      - id: RPMR-I6
        statement: reopen-finalize must recompute required gates and decisions before completed record creation.
      - id: RPMR-I7
        statement: commit preflight is a final guard, not the first normal detector.
    open_policy_question:
      - id: RPMR-Q3
        statement: Push済みで手続き不備のある completed reopen は履歴改変ではなく superseding reopen record として扱う。
  - key: current-reopen-state
    purpose: Active reopen state that the requirements review is preparing to evaluate.
    source_path: stages/in-progress/reopen-procedure-2026-07-01.yaml
    structured_state:
      classification: R-0
      edited_phases:
        - requirements
      impacted_downstream_phases:
        - design
        - tasks
        - implementation
      full_reopen_downstream_phases:
        - design
        - tasks
        - implementation
      downstream_impact_decisions: []
      drafting_completed_gates:
        - stages/requirements.yaml#drafting
      active_gate: stages/requirements.yaml#triad-review
      pending_gates:
        - stages/requirements.yaml#triad-review
        - stages/requirements.yaml#review-wave
        - stages/requirements.yaml#alignment
        - stages/requirements.yaml#approval
        - stages/design.yaml#triad-review
        - stages/design.yaml#review-wave
        - stages/design.yaml#alignment
        - stages/design.yaml#approval
        - stages/tasks.yaml#triad-review
        - stages/tasks.yaml#review-wave
        - stages/tasks.yaml#alignment
        - stages/tasks.yaml#approval
        - stages/implementation.yaml#triad-review
        - stages/implementation.yaml#review-wave
        - stages/implementation.yaml#alignment
        - stages/implementation.yaml#approval
  - key: current-spec-state
    purpose: Current machine state after reopen flag rollback.
    source_path: .reviewcompass/specs/workflow-management/spec.json
    structured_state:
      requirements:
        drafting: true
        triad-review: false
        review-wave: false
        alignment: false
        approval: false
      design_tasks_implementation:
        drafting_through_approval: false
      recheck:
        upstream_change_pending: true
        impacted_downstream_phases:
          - design
          - tasks
          - implementation
  - key: reopen-procedure-guidance
    purpose: Governing reopen procedure.
    source_path: .reviewcompass/guidance/REOPEN_PROCEDURE.md
    structured_summary:
      - A phase with substantive canonical artifact changes must rerun triad-review, review-wave, alignment, and approval.
      - Downstream impact decisions are required for requirements/design/tasks/implementation edits, not only intent edits.
      - No-change downstream decisions still need gate, feature scope, decision, rationale, and evidence.
      - Missing required gates or decisions must fail closed.
  - key: vertical-intent-transfer-guidance
    purpose: Governing review-scope rule for requirements triad-review.
    source_path: .reviewcompass/guidance/SESSION_WORKFLOW_GUIDE.md#vertical-intent-transfer-review
    structured_summary:
      - Requirements review checks upstream decision materials against requirements.md.
      - design.md and tasks.md may be source context but are not correctness targets for requirements review.
      - Source materials must not be path-only.
      - Required prompt material includes purpose, responsibility boundaries, acceptance criteria, forbidden actions, unresolved items, and intended target-phase transfer.
  - key: api-review-protocol-guidance
    purpose: Governing TRIAD review / API review-run sequence.
    source_paths:
      - .reviewcompass/guidance/API_REVIEW_PROMPT_QUALITY.md
      - .reviewcompass/guidance/discipline_llm_as_judge_prompting.md
      - .reviewcompass/guidance/SESSION_WORKFLOW_GUIDE.md#3.3-a-2
    structured_summary:
      - main preanalysis precedes review-run and is not ground truth.
      - preanalysis sufficiency audit must verify material selection, split, judgment items, and source selection.
      - prompt quality review requires adversarial review, main revision, and judgment approval before actual review-run.
      - actual review-run must save raw, parsed, rounds, model summary, triage, and target manifest artifacts.
      - user-visible triage is a required stop before proxy_model, implementation edits, spec.json update, or phase movement.
      - proxy_model cannot authorize commit, push, spec.json update, phase transition, or human-only approval.
    exact_governing_excerpts:
      - Before proxy_model, implementation edits, spec.json update, or phase transition, present variant, role/provider/model, raw summary, clusters, triage proposal, must-fix candidates, and proxy_model scope, then stop.
      - If variant or role assignment is ambiguous, do not start the review-run.
      - proxy_model decides important findings; implementation is separate; commit, push, spec.json update, and phase transition require explicit human approval.
      - Standard order is main preanalysis, preanalysis sufficiency audit, API review criteria draft, prompt quality review, actual review-run, raw/parsed/model summary/triage, and optional proxy_model decision.
      - Required changes from preanalysis sufficiency audit must be reflected before prompt quality review.
  - key: behavior-path-source-summary
    purpose: Behavior-path source material for fail-closed claims.
    source_paths:
      - tools/check-workflow-action.py
      - tests/tools/test_check_workflow_action.py
    structured_summary:
      - _required_downstream_impact_phases_for_edited_phases derives downstream phases from edited phases.
      - _gate_chain_for_edited_phases_and_downstream expands edited phases and downstream full reopen phases to full gates.
      - _reopen_downstream_impact_action returns record_reopen_downstream_impact_decision when downstream decisions are missing.
      - validate_reopen_completion_impact_decisions and _validate_reopen_finalize_downstream_impact_decisions reject missing downstream decisions.
      - Focused tests cover edited phase downstream scope, design edit dynamic downstream scope, false scope dynamic downstream phase, and finalize rejection when downstream decisions are missing.
    source_limit:
      - Use these as source material only for requirements behavior-path claims. Do not make code correctness the target of requirements review.
```

## Main Preanalysis Excerpt

The main session LLM produced `.reviewcompass/specs/workflow-management/reviews/2026-07-01-workflow-management-requirements-reopen-protocol-review-run/main-preanalysis.md`. Treat it as a hypothesis, not as ground truth.

```yaml
candidate_review_requirement:
  gate: stages/requirements.yaml#triad-review
  target:
    - .reviewcompass/specs/workflow-management/requirements.md
  review_question: >
    Does requirements.md carry the upstream reopen-protocol intent into requirements-stage
    policy without omission, weakening, contradiction, unsupported addition, or drift?
claim_decomposition:
  - id: edited_phase_full_gate_requirement
    target: Requirement 5 acceptance criterion 7
    source:
      - plan invariants RPMR-I1/RPMR-I2
      - REOPEN_PROCEDURE step 3
      - current reopen pending gates
    out_of_scope:
      - implementation correctness
  - id: downstream_impact_decision_requirement
    target:
      - Requirement 5 acceptance criterion 7
      - Requirement 16 acceptance criteria 11/12
      - Requirement 9 acceptance criteria 3/5 as related in-target context, not source material
    source:
      - plan invariants RPMR-I3/RPMR-I4
      - REOPEN_PROCEDURE step 3
      - current spec recheck state
    out_of_scope:
      - design/tasks/implementation correctness
  - id: fail_closed_surfaces
    target:
      - Requirement 5 acceptance criterion 7
      - Requirement 2 acceptance criteria 9/13 as related in-target context, not source material
    source:
      - plan invariants RPMR-I5/RPMR-I6/RPMR-I7
      - runner functions
      - related tests
  - id: superseding_reopen_record_policy
    target: Requirement 5 acceptance criterion 7
    source:
      - plan question RPMR-Q3
      - current reopen trigger
      - reopen procedure history policy
  - id: proxy_model_human_only_boundary
    target:
      - Requirement 3 acceptance criterion 5
      - Requirement 16 acceptance criteria 13/14
    source:
      - SESSION_WORKFLOW_GUIDE 3.3-a-2
      - API_REVIEW_PROMPT_QUALITY
  - id: review_scope_boundary
    target:
      - requirements.md
    source:
      - vertical intent transfer guidance
      - current next required inputs
      - reopen procedure
recommended_prompt_split:
  default: one requirements review prompt
  possible_split_if_auditor_requires:
    - requirements vertical transfer
    - behavior-path contract sufficiency
unread_or_assumptions:
  - Older completed reopen record body is not read because the target is superseding policy, not rejudging old records.
  - Full design/tasks/implementation bodies are not read because downstream correctness is out of scope.
  - Variant and role assignment are not yet fixed, so actual review-run must not start until later protocol steps.
```

## Proposed API Review Criteria

The following proposed criteria is the object being audited for sufficiency.

```markdown
---
criteria_id: workflow-management-requirements-reopen-protocol-review-criteria
phase: requirements
gate: stages/requirements.yaml#triad-review
intended_review_target:
  - .reviewcompass/specs/workflow-management/requirements.md
source_materials:
  note: "Front matter records provenance only. Model-readable source material is embedded in the body; the actual review-run must not depend on the preanalysis audit bundle."
  embedded:
    - reopen-protocol-mechanization-plan
    - current-reopen-state
    - current-spec-state
    - reopen-procedure-guidance
    - vertical-intent-transfer-guidance
    - api-review-protocol-guidance
    - behavior-path-source-summary
status: draft_for_prompt_quality_review
---

# workflow-management requirements reopen-protocol Review Criteria

## Review Task

Review `.reviewcompass/specs/workflow-management/requirements.md` for `stages/requirements.yaml#triad-review`.

The review question is:

Does `requirements.md` carry the upstream reopen-protocol intent into requirements-stage policy without omission, weakening, contradiction, unsupported addition, or drift?

Return findings only when the requirements document itself is deficient for this review question.

## Required Checks

1. Check whether `requirements.md` requires every edited phase to rerun triad-review, review-wave, alignment, and approval, and whether the text avoids implying that alignment/approval alone is enough.
2. Check whether `requirements.md` requires downstream impact decisions for affected downstream phases, including no-change decisions with gate, feature scope, decision, rationale, and evidence.
3. Check whether `requirements.md` requires missing gates or decisions to be detected by `next --json` and `reopen-finalize`, with commit preflight as a final guard rather than the first normal detector.
4. Check whether `requirements.md` requires incomplete completed reopen records to be handled as superseding reopen records with replacement reasons, rather than silent history rewriting.
5. Check whether `requirements.md` preserves proxy_model and human-only authority boundaries.
6. Check whether the requirements text keeps current active reopen scope, downstream impact review scope, historical reopen flags, consumer/derivative feature impact, and future downstream correctness review distinct enough for later phases.
7. Use the behavior-path source summary only to evaluate whether `requirements.md` makes sufficient behavior-path policy claims. Do not turn runner or test behavior into a code-correctness finding at this requirements gate.

## Out Of Scope

- Do not judge whether design.md, tasks.md, or implementation code is correct.
- Do not judge whether current runner implementation fully satisfies the requirements.
- Do not approve or authorize commit, push, `spec.json` mutation, phase transition, gate completion, proxy_model use, or human approval delegation.
- Do not treat source material defects as target findings unless they create a requirements transfer defect.
- Do not use main preanalysis as an answer key.
- Do not audit this criteria file, the preanalysis, or the prompt split in the actual requirements review-run.

## Source Materials

Use only the source materials embedded in the proposed criteria body. The actual review-run criteria must be self-contained and must not rely on this preanalysis audit bundle. Source material must be model-readable and must not be path-only.
```

The full proposed criteria file is also stored at:

- `.reviewcompass/specs/workflow-management/reviews/2026-07-01-workflow-management-requirements-reopen-protocol-review-run/proposed-review-criteria-outline.md`
