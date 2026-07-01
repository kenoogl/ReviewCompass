prompt_id: anthropic_review
provider: anthropic-api
model_id: claude-sonnet-4-6

# Task
Review the target document for the requested phase and criteria.

# Phase
prompt-quality

# Criteria
---
criteria_id: api-review-prompt-quality-review
phase: prompt-quality
review_target: <api-review-criteria-draft.md>
---

# API Review Prompt Quality Review Criteria

Review the target prompt draft itself. Do not review the eventual feature artifact yet.

The question is:

Is the draft prompt suitable to use as the `--criteria-file` for the intended API-mediated review, given that the actual `--target` will be the target artifact named in the draft?

If user-provided review requirements exist, also judge whether the draft prompt preserves and operationalizes those requirements without unauthorized narrowing, broadening, replacement, or added authority.

## Required Quality Checks

Check both general LLM-as-Judge prompt quality and any workflow / phase-specific review requirements.

### General API Review Prompt Quality

The prompt draft must:

1. Show that main identified the materials and judgment points before sending the prompt.
2. Include enough background and related context for the model to avoid guessing.
3. Ask a non-leading analysis question.
4. Define a scope that is neither too broad nor too narrow.
5. Provide or rely on a fixed, parser-friendly output contract when combined with the API review runner template.
6. Avoid credentials, personal data, or unrelated confidential material.
7. Keep `--criteria-file` and `--target` roles distinct.
8. Ensure the target manifest will contain the actual artifact under review.

### User Review Requirements Fit

When the review was requested by a user or by a workflow-specific gate, the prompt draft must:

1. Preserve the requested review purpose, review object, focus, scope boundaries, source materials, output requirements, and prohibited actions.
2. Map those requirements into the review task, required checks, out of scope, and finding policy.
3. Avoid narrowing the requested review so that important user-stated concerns disappear.
4. Avoid broadening the requested review into unrelated judgments or downstream phase decisions.
5. Avoid replacing the requested review question with a more convenient or generic question.
6. Mark assumptions explicitly when the user requirement is ambiguous.
7. Keep workflow-required checks distinguishable from user-requested checks when both apply.
8. Prevent commit, push, phase completion, human approval delegation, or unapproved specification changes unless those actions are explicitly in scope and allowed by the governing workflow.

### Judgment Granularity

The prompt draft must:

1. Contain one primary judgment question.
2. Avoid bundling multiple independent cluster, finding, acceptance, or design-policy judgments into one prompt.
3. Split multiple independent judgments into separate prompt files unless they are inseparable parts of the same decision.
4. Include only the source findings, upstream materials, target summaries, and output fields needed for the specific judgment item.
5. Keep common background short enough that it does not obscure the item-specific evidence.
6. Require separate prompt-quality review evidence for each item-specific prompt when the review is split.

### Source-Material Quality

The prompt draft must:

1. Clearly distinguish review target, source materials, and out-of-scope material.
2. Avoid path-only source material listing.
3. Include required source material as excerpt or structured summary in a model-readable form.
4. Mark front matter paths as provenance when they are not model-readable content.
5. Include unresolved or deferred items when they affect the target review.

### External API Material Policy

The prompt draft may include ReviewCompass repository specifications, designs, tasks, review findings, structured summaries, and evidence paths when they are necessary for API review or proxy_model judgment and the user has approved that API/proxy execution.

The prompt draft must:

1. Exclude API keys, tokens, passwords, nonces, and other secrets.
2. Exclude personal identifiers such as email addresses and phone numbers unless explicitly required and approved.
3. Exclude third-party confidential material that is not allowed to be sent externally.
4. Avoid unnecessary full logs or unrelated files.
5. Use the minimum review-relevant excerpts or structured summaries needed for the judgment item.
6. Not treat ordinary repository-internal specs, designs, review findings, or evidence paths as automatically prohibited solely because they are unpublished.

### Vertical Intent Transfer Requirements

When the review is a phase review under `SESSION_WORKFLOW_GUIDE.md#vertical-intent-transfer-review`, the prompt draft must:

1. Limit target judgment to the current phase artifact.
2. Use upstream artifacts only for background and intent-transfer checking.
3. Include upstream purpose, responsibility boundaries, acceptance criteria, forbidden actions, unresolved items, and intended target-phase transfer.
4. Prevent the model from judging downstream tasks or implementation correctness unless downstream invention would be forced by a target omission.

### Output And Triage Fit

The prompt draft must:

1. Use severity labels compatible with the API parser: `CRITICAL`, `ERROR`, `WARN`, `INFO`.
2. Give enough target-location guidance for findings to be triaged.
3. Define when `findings: []` is acceptable.
4. Avoid wording that suppresses findings about critical boundaries while merely trying to prohibit the model from authorizing operations.

## Finding Policy

- Report `CRITICAL` if the draft prompt would authorize or imply authorization of irreversible operations, gate completion, or human-only approvals.
- Report `CRITICAL` if the draft prompt would violate a user-stated prohibited action or authority limit.
- Report `ERROR` if the draft prompt omits, weakens, broadens, or replaces a user-stated review requirement in a way that changes what will be reviewed.
- Report `ERROR` if the draft prompt combines multiple independent judgments so that the model is likely to miss item-specific evidence, conflate labels, or produce unusable decisions.
- Report `ERROR` if the draft prompt would likely cause models to review the wrong target, rely on summaries instead of the real target, miss required upstream-transfer obligations, leak secrets or prohibited third-party confidential material, or produce unusable output.
- Report `WARN` if the draft prompt is usable but has avoidable ambiguity, framing bias, incomplete source-material presentation, weak target/source/out-of-scope separation, incomplete mapping from user requirements to checks, or mildly oversized common background.
- Report `INFO` for minor wording or ergonomics improvements.
- Return `findings: []` only if the draft prompt is safe to use for the intended API review.

## Output Contract

Return YAML only with top-level key `findings`.

Each finding must include:

- `severity`: CRITICAL, ERROR, WARN, or INFO
- `target_location`: specific section in the prompt draft
- `description`: concise finding summary
- `rationale`: why this matters for API review quality

If there are no findings, return exactly:

findings: []


# Output contract
Return YAML only.
The response must include the top-level key findings.
Additional top-level keys are allowed only when the criteria explicitly defines them.
Do not use review: as a wrapper.
Do not use result:, metadata:, or summary: as wrappers.
Do not wrap the YAML in Markdown code fences.
Do not include ```yaml or any other fence marker.
Do not write explanatory prose before or after the YAML.

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
.reviewcompass/specs/workflow-management/reviews/2026-07-01-workflow-management-requirements-reopen-protocol-review-run/proposed-review-criteria-outline.md

# Target document
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
user_review_requirements:
  provided_by: workflow
status: draft_for_prompt_quality_review
---

# workflow-management requirements reopen-protocol Review Criteria

## Review Task

Review `.reviewcompass/specs/workflow-management/requirements.md` for `stages/requirements.yaml#triad-review`.

The review question is:

Does `requirements.md` carry the upstream reopen-protocol intent into requirements-stage policy without omission, weakening, contradiction, unsupported addition, or drift?

Return findings only when the requirements document itself is deficient for this review question.

## Why This Review Exists

This review-run is required because the active reopen edits `workflow-management` requirements. A requirements edit must pass requirements triad-review before review-wave, alignment, approval, downstream phase gates, proxy_model decisions, `spec.json` updates, phase transitions, commit, or push can be treated as complete.

The prior process failure being guarded against is: a reopen that changed `requirements.md` proceeded without rerunning requirements triad-review and review-wave, while design/tasks/implementation impact was handled as late supplemental metadata instead of as normal reopen-chain work.

## User And Workflow Review Requirements

Review purpose:

- Requirements triad-review for reopen protocol mechanization.
- Vertical transfer check from user/workflow decisions, reopen classification, planning notes, and governance documents into `requirements.md`.

Review object:

- `.reviewcompass/specs/workflow-management/requirements.md`.

Review focus:

- Edited phase full-gate re-execution.
- Downstream phase impact decisions with evidence even when downstream documents do not change.
- Fail-closed detection at `next --json`, `reopen-finalize`, and commit preflight.
- Superseding reopen record policy for already-pushed incomplete reopen records.
- proxy_model and human-only authority boundaries.
- Requirements-stage target/source/out-of-scope separation.

Scope boundaries:

- In scope: whether the target requirements text carries the reopen protocol requirements and authority limits needed by later design/tasks/implementation work.
- Out of scope: judging design.md, tasks.md, implementation code, or current runner correctness as final correctness targets.
- Source-only: runner, guard, preflight, and tests may be used to understand behavior-path claims, but implementation defects are not target findings at this gate unless they reveal a requirements omission or contradiction.

Output requirements:

- Parser-compatible findings.
- Include `findings: []` only when the target requirements text is traceable, sufficiently scoped, and internally consistent for the stated review question.

Prohibited actions and authority limits:

- Do not authorize commit, push, `spec.json` update, phase transition, gate completion, proxy_model decision, or human approval delegation.
- Do not treat this review-run, prompt-quality-run, or a proxy_model answer as approval to mutate workflow state.

Requirement-to-prompt mapping:

- Edited phase full-gate requirement -> Review Task, Source Materials, Required Checks 1.
- Downstream impact decision evidence -> Review Task, Source Materials, Required Checks 2.
- Fail-closed behavior paths -> Review Task, behavior-path source summary, Required Checks 3.
- Superseding reopen record policy -> Source Materials, Required Checks 4.
- proxy_model boundary -> Source Materials, Required Checks 5, Out Of Scope.
- Requirements-stage scope -> Scope boundaries, Required Checks 6.

## Review Target

The review target is only:

- `.reviewcompass/specs/workflow-management/requirements.md`

At the actual review-run, pass this path as the review target. Do not treat this criteria file, a wrapper, source summaries, design/tasks/implementation documents, or author-written preanalysis as a substitute for the target document.

Target sections expected to be relevant. These are target locations, not source material; the actual review-run must receive the full `requirements.md` file as target content.

- Requirement 3 acceptance criterion 5.
- Requirement 5 acceptance criterion 7.
- Requirement 16 acceptance criteria 11-14.
- Related in-target context: Requirement 2 acceptance criteria 9/13 and Requirement 9 acceptance criteria 3/5.

## Source Materials

Use these source materials only for background and intent-transfer checking. Do not judge these source materials as review targets unless the requirements document omits, weakens, or contradicts their required transfer.

### reopen-protocol-mechanization-plan

Source path:

- `.reviewcompass/backlog/plans/plan-2026-07-01-reopen-protocol-mechanization-review.yaml`

Purpose:

- Correct a process failure where a requirements-changing reopen did not rerun requirements triad-review/review-wave and downstream impact was deferred until finalize/commit repair.

Responsibility boundaries:

- A phase whose canonical artifact is substantively edited must be marked as an edited phase.
- Edited phases require full review gates, not only alignment/approval.
- Downstream impact must be recorded as normal reopen-chain work, not late metadata.
- Completed records already pushed should not be rewritten silently; use a superseding reopen record with a reason.

Acceptance criteria / required transfer:

- RPMR-I1: reopen state keeps the substantively edited phases as `edited_phases` or an equivalent machine-readable field.
- RPMR-I2: each phase in `edited_phases` requires triad-review, review-wave, alignment, and approval; drafting completion is checked where drafting is required.
- RPMR-I3: upstream phase edits require downstream phase impact coverage through `impacted_downstream_phases` and `downstream_impact_decisions`.
- RPMR-I4: downstream no-change decisions still need gate, feature scope, decision, rationale, and evidence.
- RPMR-I5: `next --json` detects missing edited phase gates or downstream decisions before normal completion.
- RPMR-I6: `reopen-finalize` recomputes required gates and decisions before creating a completed record.
- RPMR-I7: commit preflight is a final guard, not the first expected detection point.
- RPMR-Q3: already-pushed incomplete completed reopen records should be handled by a superseding reopen record with replacement rationale, not by silent history rewriting.

Forbidden or high-risk drift:

- Treating downstream impact as optional supplemental metadata.
- Letting completed reopen records be generated before required gates or decisions are present.
- Relying on commit preflight as the first normal detector.

### current-reopen-state

Source path:

- `stages/in-progress/reopen-procedure-2026-07-01.yaml`

Structured summary:

- classification: `R-0`
- edited_phases: `requirements`
- impacted_downstream_phases: `design`, `tasks`, `implementation`
- full_reopen_downstream_phases: `design`, `tasks`, `implementation`
- downstream_impact_decisions: empty at this moment
- drafting_completed_gates: `stages/requirements.yaml#drafting`
- active gate: `stages/requirements.yaml#triad-review`
- pending gates: requirements/design/tasks/implementation triad-review, review-wave, alignment, approval

Intended target-phase transfer:

- The requirements document should support this kind of active state: requirements was edited, downstream phases remain in scope, and the review cannot be considered complete before required gates and downstream decisions are recorded.

### current-spec-state

Source path:

- `.reviewcompass/specs/workflow-management/spec.json`

Structured summary:

- requirements drafting is true.
- requirements triad-review, review-wave, alignment, and approval are false.
- design/tasks/implementation drafting, triad-review, review-wave, alignment, and approval are false.
- `recheck.upstream_change_pending` is true.
- `recheck.impacted_downstream_phases` includes design, tasks, and implementation.

Intended target-phase transfer:

- Requirements must distinguish active reopen scope from historical reopen flags, and must not imply that downstream gates can stay complete after upstream requirements changed.

### reopen-procedure-guidance

Source path:

- `.reviewcompass/guidance/REOPEN_PROCEDURE.md`

Structured summary:

- A phase whose canonical artifact is substantively changed re-enters triad-review, review-wave, alignment, and approval.
- Downstream impact is assessed for requirements, design, tasks, and implementation, not only for intent changes.
- Even when downstream changes are unnecessary, the decision needs gate, feature scope, decision, rationale, and evidence.
- Reopen progress should fail closed when required gates or impact evidence are missing.

### vertical-intent-transfer-guidance

Source path:

- `.reviewcompass/guidance/SESSION_WORKFLOW_GUIDE.md#vertical-intent-transfer-review`

Structured summary:

- Requirements review checks upstream decision materials against `requirements.md`.
- For requirements review, downstream documents are source context at most, not correctness targets.
- Source materials must not be path-only.
- The prompt must separate purpose, responsibility boundaries, acceptance criteria, forbidden actions, unresolved/deferred items, and intended target-phase transfer.

### api-review-protocol-guidance

Source paths:

- `.reviewcompass/guidance/API_REVIEW_PROMPT_QUALITY.md`
- `.reviewcompass/guidance/discipline_llm_as_judge_prompting.md`
- `.reviewcompass/guidance/SESSION_WORKFLOW_GUIDE.md#3.3-a-2`

Structured summary:

- Main preanalysis is a hypothesis and source-selection aid, not an answer key.
- Preanalysis sufficiency audit must check material selection, judgment item split, and source coverage before real review-run.
- Prompt quality review must use adversarial review, main revision, and judgment approval; actual review-run starts only when judgment has no findings.
- After actual review-run, raw/parsed/rounds/model-summary/triage artifacts and user-visible triage must be presented before proxy_model, implementation edits, `spec.json` updates, or phase movement.
- proxy_model may judge important finding triage, but cannot authorize commit, push, `spec.json` update, phase transition, or human-only approval.

Exact governing excerpts needed for authority boundaries:

- `SESSION_WORKFLOW_GUIDE.md#3.3-a-2`: before proxy_model, implementation edits, `spec.json` update, or phase transition, present variant, role/provider/model, raw summary, clusters, triage proposal, must-fix candidates, and the proxy_model scope, then stop.
- `SESSION_WORKFLOW_GUIDE.md#3.3-a-2`: if variant or role assignment is ambiguous, do not start the review-run.
- `SESSION_WORKFLOW_GUIDE.md#3.3-a-2`: proxy_model decides important findings; implementation is separate; commit, push, `spec.json` update, and phase transition require explicit human approval.
- `API_REVIEW_PROMPT_QUALITY.md#8`: standard order is main preanalysis, preanalysis sufficiency audit, API review criteria draft, prompt quality review, actual review-run, raw/parsed/model summary/triage, and optional proxy_model decision.
- `API_REVIEW_PROMPT_QUALITY.md#8`: required changes from preanalysis sufficiency audit must be reflected before prompt quality review.

### behavior-path-source-summary

Source paths:

- `tools/check-workflow-action.py`
- `tests/tools/test_check_workflow_action.py`

Structured summary:

- `_required_downstream_impact_phases_for_edited_phases` derives downstream phases dynamically from edited phases.
- `_gate_chain_for_edited_phases_and_downstream` expands edited phases and downstream full reopen phases to required full gates.
- `_reopen_downstream_impact_action` returns `record_reopen_downstream_impact_decision` when downstream decisions are missing.
- `validate_reopen_completion_impact_decisions` and `_validate_reopen_finalize_downstream_impact_decisions` reject incomplete completed/finalize records.
- Focused tests cover initializing edited phase downstream scope, design edit dynamic downstream scope, false scope dynamic downstream phase, and finalize rejection when impacted downstream decisions are missing.

Use this behavior-path material only to assess whether the requirements text makes behavior-path claims sufficiently explicit. Do not judge code correctness as the target of this requirements review.

## Required Checks

1. Check whether `requirements.md` requires every edited phase to rerun triad-review, review-wave, alignment, and approval, and whether the text avoids implying that alignment/approval alone is enough.
2. Check whether `requirements.md` requires downstream impact decisions for affected downstream phases, including no-change decisions with gate, feature scope, decision, rationale, and evidence.
3. Check whether `requirements.md` requires missing gates or decisions to be detected by `next --json` and `reopen-finalize`, with commit preflight as a final guard rather than the first normal detector.
4. Check whether `requirements.md` requires incomplete completed reopen records to be handled as superseding reopen records with replacement reasons, rather than silent history rewriting.
5. Check whether `requirements.md` preserves proxy_model and human-only authority boundaries: proxy_model may support important-issue judgment, but must not authorize commit, push, `spec.json` mutation, phase transition, or human-only approval.
6. Check whether the requirements text keeps current active reopen scope, downstream impact review scope, historical reopen flags, consumer/derivative feature impact, and future downstream correctness review distinct enough for later phases.
7. Use the behavior-path source summary only to evaluate whether `requirements.md` makes sufficient behavior-path policy claims. Do not turn runner or test behavior into a code-correctness finding at this requirements gate.

## Out Of Scope

- Do not judge whether design.md, tasks.md, or implementation code is correct.
- Do not judge whether current runner implementation fully satisfies the requirements.
- Do not approve or authorize commit, push, `spec.json` mutation, phase transition, gate completion, proxy_model use, or human approval delegation.
- Do not treat source material defects as target findings unless they create a requirements transfer defect.
- Do not use main preanalysis as an answer key.
- Do not audit this criteria file, the preanalysis, or the prompt split in the actual requirements review-run.

## Finding Policy

- Report `CRITICAL` if the target requirements would authorize or imply authorization of commit, push, `spec.json` mutation, phase transition, gate completion, proxy_model substitution for human-only judgment, or human approval delegation.
- Report `ERROR` if the target omits, weakens, broadens, or replaces a workflow review requirement in a way that changes the review outcome.
- Report `ERROR` if edited phase full-gate requirements, downstream impact decision evidence, fail-closed detection points, superseding reopen record policy, or proxy_model authority boundaries are missing, contradicted, or ambiguous enough to require downstream invention.
- Report `WARN` for ambiguity likely to force repeated manual judgment, weak traceability, unclear state boundaries, or overclaiming completion.
- Report `INFO` only for non-blocking traceability improvements.
- Return `findings: []` only when the target is traceable, internally consistent, correctly scoped, and sufficiently grounded for downstream phases.

