prompt_id: gemini_review
provider: gemini-api
model_id: gemini-3.1-pro-preview

# Task
Review the target document for the requested phase and criteria.

# Phase
prompt-quality

# Criteria
---
criteria_id: main-preanalysis-sufficiency-audit
phase: prompt-quality
review_target: <preanalysis-audit-bundle.md>
status: template
---

# Main Preanalysis Sufficiency Audit Criteria

Review the target bundle before the actual API review-run.

The target bundle must contain:

- the user or workflow review requirement
- the source materials needed for the judgment item
- the main session LLM preanalysis
- the proposed API review criteria or prompt

The review question is:

Can the proposed API review prompt derive the needed review judgment from the provided source materials, without relying on the main preanalysis as an answer key, and does the main preanalysis reveal any missing viewpoints, unsupported claims, or framing bias that must be corrected before the real review-run?

## Required Method

Perform the audit in this order:

1. Independently reconstruct the judgment item from the source materials and user or workflow requirement.
2. Compare that reconstruction with the main preanalysis.
3. Judge whether the proposed API review prompt gives enough source material, scope, question, and output instructions for the actual reviewer.
4. Identify required prompt changes before any real review-run.

Treat the main preanalysis as a hypothesis and source-discovery aid. Do not treat it as ground truth.

## Required Checks

### Independent Reconstruction

From the source materials alone, identify:

- the judgment item ID
- the exact review question
- the target artifact or section
- the source materials that are necessary
- the material that is out of scope
- the rationale connecting the source materials to the review question

If multiple independent judgment items are present, report that the proposed review prompt must be split.

### Main Preanalysis Assessment

Compare the main preanalysis against the independent reconstruction.

Check for:

- supported parts that are well grounded in the sources
- missing perspectives or missing source materials
- unsupported, overconfident, or overstated parts
- framing bias, including treating a draft answer as established fact
- source coverage gaps caused by path-only references, summaries without source basis, or omitted upstream context

### Prompt Sufficiency

Judge whether the proposed API review prompt:

- includes enough model-readable source material
- asks one non-leading primary question
- keeps target, source materials, and out-of-scope material distinct
- preserves user or workflow requirements without narrowing, broadening, or replacing them
- defines the expected output clearly enough for the runner
- prevents the reviewer from authorizing commit, push, phase completion, human approval delegation, or unapproved specification changes

## Finding Policy

- Report `CRITICAL` if the prompt would authorize or imply authorization of irreversible operations, human-only approval, phase completion, or unapproved repository changes.
- Report `ERROR` if the prompt cannot support the requested review because source materials are missing, path-only, wrong, or treated as target material.
- Report `ERROR` if multiple independent judgments are bundled into one prompt.
- Report `ERROR` if the prompt depends on the main preanalysis as the answer instead of requiring source-based independent judgment.
- Report `ERROR` if user or workflow review requirements are omitted, narrowed, broadened, or replaced.
- Report `WARN` for usable prompts with avoidable ambiguity, incomplete source mapping, weak target/source separation, or bias risk.
- Report `INFO` for minor clarity or ergonomics improvements.

## Output Contract

Return YAML only. Do not wrap it in Markdown fences.

The response must include these top-level keys:

- `verdict`
- `independent_reconstruction`
- `preanalysis_assessment`
- `prompt_sufficiency`
- `required_prompt_changes`
- `findings`

Use one of these `verdict` values:

- `sufficient`
- `sufficient_with_revisions`
- `insufficient`

Use this shape:

verdict: sufficient_with_revisions
independent_reconstruction:
  judgment_items:
    - item_id: "<stable-id>"
      question: "<source-derived review question>"
      target_files:
        - "<path or section>"
      source_materials:
        - "<path, section, or embedded source label>"
      out_of_scope:
        - "<material or action not judged>"
      rationale: "<why this is the right judgment item>"
preanalysis_assessment:
  supported_parts:
    - "<grounded part>"
  missing_perspectives:
    - "<missing viewpoint or source>"
  unsupported_or_overconfident_parts:
    - "<claim that needs source support or softening>"
  bias_risks:
    - "<framing or anchoring risk>"
prompt_sufficiency:
  information: "sufficient | revisions_needed | insufficient"
  question: "sufficient | revisions_needed | insufficient"
  scope: "sufficient | revisions_needed | insufficient"
  sensitivity_check: "sufficient | revisions_needed | insufficient"
  notes:
    - "<short note>"
required_prompt_changes:
  - "<required change before actual review-run>"
findings:
  - severity: WARN
    target_location: "<section in proposed prompt or bundle>"
    description: "<concise finding>"
    rationale: "<why this matters>"

If there are no defects, return `verdict: sufficient`, complete the assessment keys with empty lists where appropriate, and return:

findings: []


# Output contract
Return YAML only.
The response must include the top-level key findings.
Additional top-level keys are allowed only when the criteria explicitly defines them.
Do not add wrapper keys such as review, result, metadata, or summary.
Do not wrap the YAML in Markdown code fences.
Do not write prose before or after the YAML.

Each finding must include these keys:
- severity
- target_location
- description
- rationale

Use only these severity values:
- CRITICAL
- ERROR
- WARN
- INFO

If there are no findings and the criteria does not define additional top-level keys, return exactly:

findings: []

Valid shape example:

findings:
  - severity: WARN
    target_location: "path or section"
    description: "Plain finding summary"
    rationale: "Why this matters"

# Prior findings
なし

# Target path
.reviewcompass/specs/workflow-management/reviews/2026-07-01-workflow-management-requirements-reopen-protocol-review-run/preanalysis-audit-bundle.md

# Target document
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

## Source Materials

The following source material is model-readable context for the audit.

```yaml
source_materials:
  - key: target-requirements-excerpts
    purpose: Current requirements text that the later real review-run will judge.
    source_path: .reviewcompass/specs/workflow-management/requirements.md
    relevant_excerpts:
      - section: Requirement 3 acceptance criterion 5
        text: >
          proxy_model may decide important findings, but commit, push, spec.json update,
          and phase transition are not delegated to proxy_model.
      - section: Requirement 5 acceptance criterion 7
        text: >
          reopen state keeps edited_phases and impacted_downstream_phases. Edited phases
          must rerun triad-review, review-wave, alignment, and approval. Downstream impact
          decisions must record at least target gate, feature scope, decision, rationale,
          and evidence. next --json, reopen-finalize, and commit preflight fail closed
          when edited-phase gates or downstream decisions are missing. Existing incomplete
          completed reopen records are superseded with replacement reasons rather than
          rewritten.
      - section: Requirement 16 acceptance criteria 11-14
        text: >
          Active reopen scope is separate from historical spec.json.reopened. Workflow
          management changes can affect consumer or derivative features. proxy_model
          applicability is evidence-based, and human-required predicates override proxy
          decisions.
  - key: reopen-protocol-mechanization-plan
    purpose: Upstream planning and user/workflow decision material for why this reopen exists.
    source_path: .reviewcompass/backlog/plans/plan-2026-07-01-reopen-protocol-mechanization-review.yaml
    problem:
      - A previous requirements-changing reopen did not rerun requirements triad-review and review-wave.
      - Downstream design/tasks/implementation impact was handled as late supplemental metadata.
      - Missing downstream decisions were detected too late, around finalize or commit.
    invariants:
      - edited_phases must be machine-readable.
      - edited phases require triad-review, review-wave, alignment, and approval.
      - upstream phase edits require impacted_downstream_phases and downstream_impact_decisions.
      - downstream no-change decisions still need gate, feature_scope, decision, rationale, and evidence.
      - next --json must return reopen missing work instead of normal completion when gates or decisions are missing.
      - reopen-finalize must recompute required gates and decisions before completed record creation.
      - commit preflight is a final guard, not the first normal detector.
    open_policy_question:
      - Push済みで手続き不備のある completed reopen は履歴改変ではなく superseding reopen record として扱う。
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
    Does requirements.md preserve the reopen protocol mechanization requirement,
    including edited phase full-gate re-execution, downstream impact decision evidence,
    fail-closed detection points, superseding reopen records, proxy_model authority
    boundaries, and requirements-stage scope boundaries, without omission, weakening,
    contradiction, unsupported addition, or drift?
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
      - Requirement 9 acceptance criteria 3/5
      - Requirement 16 acceptance criteria 11/12
    source:
      - plan invariants RPMR-I3/RPMR-I4
      - REOPEN_PROCEDURE step 3
      - current spec recheck state
    out_of_scope:
      - design/tasks/implementation correctness
  - id: fail_closed_surfaces
    target:
      - Requirement 5 acceptance criterion 7
      - Requirement 2 acceptance criteria 9/13
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
  note: "Front matter records provenance only. Model-readable source material must be embedded in the body."
  embedded:
    - reopen-protocol-mechanization-plan
    - current-reopen-state
    - current-spec-state
    - reopen-procedure-guidance
    - vertical-intent-transfer-guidance
    - api-review-protocol-guidance
    - behavior-path-source-summary
status: draft_for_preanalysis_sufficiency_audit
---

# workflow-management requirements reopen-protocol Review Criteria

## Review Task

Review `.reviewcompass/specs/workflow-management/requirements.md` for `stages/requirements.yaml#triad-review`.

The review question is:

Does `requirements.md` preserve the reopen protocol mechanization requirement, including edited phase full-gate re-execution, downstream impact decision evidence, fail-closed detection points, superseding reopen records, proxy_model authority boundaries, and requirements-stage scope boundaries, without omission, weakening, contradiction, unsupported addition, or drift?

Return findings only when the requirements document itself is deficient for this review question.

## Required Checks

1. Check whether `requirements.md` requires every edited phase to rerun triad-review, review-wave, alignment, and approval, and whether the text avoids implying that alignment/approval alone is enough.
2. Check whether `requirements.md` requires downstream impact decisions for affected downstream phases, including no-change decisions with gate, feature scope, decision, rationale, and evidence.
3. Check whether `requirements.md` requires missing gates or decisions to be detected by `next --json` and `reopen-finalize`, with commit preflight as a final guard rather than the first normal detector.
4. Check whether `requirements.md` requires incomplete completed reopen records to be handled as superseding reopen records with replacement reasons, rather than silent history rewriting.
5. Check whether `requirements.md` preserves proxy_model and human-only authority boundaries.
6. Check whether the requirements text keeps current active reopen scope, downstream impact review scope, historical reopen flags, consumer/derivative feature impact, and future downstream correctness review distinct enough for later phases.
7. Check that the target satisfies the preserved workflow review requirements without narrowing, broadening, or replacing the requested review question.
8. Check whether the prompt combines independent judgment items that should be split before actual review-run.

## Out Of Scope

- Do not judge whether design.md, tasks.md, or implementation code is correct.
- Do not judge whether current runner implementation fully satisfies the requirements.
- Do not approve or authorize commit, push, `spec.json` mutation, phase transition, gate completion, proxy_model use, or human approval delegation.
- Do not treat source material defects as target findings unless they create a requirements transfer defect.
- Do not use main preanalysis as an answer key.

## Source Materials

Use the embedded source materials in this audit bundle and the full proposed criteria file. Source material must be model-readable and must not be path-only.
```

The full proposed criteria file is also stored at:

- `.reviewcompass/specs/workflow-management/reviews/2026-07-01-workflow-management-requirements-reopen-protocol-review-run/proposed-review-criteria-outline.md`

