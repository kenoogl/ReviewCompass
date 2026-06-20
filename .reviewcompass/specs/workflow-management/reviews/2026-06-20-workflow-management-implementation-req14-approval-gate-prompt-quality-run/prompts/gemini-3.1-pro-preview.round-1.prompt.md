prompt_id: gemini_review
provider: gemini-api
model_id: gemini-3.1-pro-preview

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
The top-level key must be exactly findings.
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

If there are no findings, return exactly:

findings: []

Valid shape example:

findings:
  - severity: WARN
    target_location: "path or section"
    description: "Plain finding summary"
    rationale: "Why this matters"

# Prior findings
# 前段所見 1：
role: adversarial
provider: anthropic-api
model: claude-sonnet-4-6
attempts: 1
duration_seconds: 19.943
findings:
- severity: WARN
  target_location: Source Materials / source_paths_note
  description: Source paths are declared as provenance-only with a structured summary
    provided as the model-readable upstream intent, but the structured summary does
    not indicate which fields were extracted from which source document. If the structured
    summary omits or misrepresents a material detail from requirements.md, design.md,
    or tasks.md, the reviewing model has no way to detect that gap without access
    to the originals.
  rationale: The structured summary is the sole model-readable evidence for upstream
    intent transfer. If it is incomplete or partially stale relative to the sha256-anchored
    source files, the reviewing model will assess transfer fidelity against a potentially
    truncated baseline, silently missing omissions in the target. A cross-reference
    note mapping each structured-summary field to its source document and section
    would reduce this risk without requiring full file inclusion.
- severity: WARN
  target_location: Required Checks / Check 5 and Out Of Scope
  description: Check 5 instructs the model that the check 'constrains the review run
    and model output, not the mere presence or implementation of workflow-operation
    code' and directs it to 'report target-code findings only when behavior bypasses
    or weakens the required gate.' The Out Of Scope section repeats a nearly identical
    carve-out. This double-layered framing risks suppressing findings about real gate-weakening
    behaviors because the model may interpret the repeated carve-out as a general
    instruction to be lenient toward any code that mentions irreversible operations,
    even when that code demonstrably bypasses the boundary.
  rationale: 'Wording that over-qualifies when to report on gate-related code can
    unintentionally raise the model''s threshold for flagging CRITICAL or ERROR conditions,
    which is the opposite of the intended effect. The carve-out is conceptually correct
    but should be stated once and more precisely: the prohibition applies to the reviewing
    model''s own output actions, not to findings about target artifacts that bypass
    the gate.'
- severity: INFO
  target_location: Review Target / target manifest note
  description: 'The note ''If any listed target path content is absent from the injected
    prompt, report ERROR against Review Target and do not return findings: []'' is
    a useful guard, but it instructs the model to emit an ERROR finding rather than
    a CRITICAL finding when the actual target is missing. A missing target makes the
    entire review invalid, which is more severe than a single ERROR finding would
    convey.'
  rationale: Aligning the severity of a missing-target signal with the actual impact
    (the review cannot proceed correctly) would make triage clearer for operators
    reading the output. This is a minor ergonomics improvement and does not block
    use of the prompt.
- severity: INFO
  target_location: Source Materials / source_anchors
  description: The sha256 anchors are listed for provenance but there is no instruction
    telling the reviewing model what to do if the injected structured summary appears
    inconsistent with those anchors or if a future run regenerates the summary from
    a different file version. The anchors are currently inert from the model's perspective.
  rationale: Adding a brief note that the anchors identify the exact file versions
    from which the structured summary was derived, and that the model should flag
    any apparent internal inconsistency in the summary, would make the anchors actionable
    rather than decorative. This is a minor improvement.


# Target path
.reviewcompass/specs/workflow-management/reviews/2026-06-20-workflow-management-implementation-req14-approval-gate-criteria-run/review-criteria.md

# Target document
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

