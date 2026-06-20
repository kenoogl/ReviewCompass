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
duration_seconds: 22.607
findings:
- severity: WARN
  target_location: Source Materials / workflow-management-req14-upstream-intent /
    source_paths
  description: Source materials are listed as paths only without excerpts or structured
    summaries inline.
  rationale: The prompt-quality criteria require that source material be included
    as excerpt or structured summary in model-readable form, not as path-only listings.
    The structured intent block below the paths partially compensates by providing
    purpose, responsibility_boundaries, acceptance_criteria, forbidden_actions, and
    unresolved items inline, but the raw .md files themselves are referenced only
    by path. The reviewing model cannot read those files directly through the criteria
    file alone. If the runner injects file contents at execution time this is acceptable,
    but the criteria file should clarify that the runner will inject those file contents
    or confirm the structured summary below is the authoritative model-readable substitute,
    so there is no ambiguity about whether the paths are provenance markers or expected
    file injections.
- severity: WARN
  target_location: Review Target
  description: Review target lists twelve files by path only without any structural
    summary, excerpt, or runner injection note.
  rationale: Source-material quality checks require that the criteria file not rely
    solely on path listings when the content must be model-readable. For the review
    target specifically, the criteria file correctly states 'Do not treat this criteria
    file, a wrapper, or an author-written summary as a substitute for the target,'
    implying actual file content must reach the model. However, no runner injection
    note or manifest reference is present to confirm how the actual artifact content
    will be supplied. If the runner reliably injects all listed target paths as content,
    this is workable, but the absence of an explicit injection note leaves ambiguity
    about whether the model will receive the actual code or only paths.
- severity: WARN
  target_location: Required Checks / check 5
  description: Check 5 conflates a scope boundary (this review run must not authorize
    operations) with a finding-policy trigger in a way that could suppress legitimate
    findings about target code implementing those same operations.
  rationale: The Out Of Scope section already includes the clarifying note that legitimate
    target code mentioning workflow operations should not be flagged solely for mentioning
    them. Check 5 does not include that clarification and a model reading checks linearly
    could interpret it as a reason to avoid reporting findings about approval or commit
    logic in the target code. Repeating the exemption note in Check 5 or linking explicitly
    to the Out Of Scope clarification would reduce this risk.
- severity: INFO
  target_location: Primary judgment question
  description: 'The primary judgment question is slightly compound: it asks whether
    the target satisfies Req 14 upstream transfer AND carries upstream intent without
    omission, weakening, contradiction, unsupported addition, or drift as a single
    sentence.'
  rationale: This is a single inseparable vertical-intent-transfer judgment, so bundling
    is acceptable under the criteria. However, the list of five sub-conditions (omission,
    weakening, contradiction, unsupported addition, drift) embedded in one sentence
    could cause a model to treat partial satisfaction as full pass. Numbering or bullet-separating
    the sub-conditions would improve clarity without splitting into independent prompts.
- severity: INFO
  target_location: Finding Policy
  description: 'Finding policy does not explicitly define when findings: [] is acceptable,
    only stating the condition negatively (''only when every required check passes'').'
  rationale: 'The output contract check requires that the prompt define when findings:
    [] is acceptable. A positive statement such as ''Return findings: [] if and only
    if all twelve target artifacts satisfy every required check with traceable evidence
    and no deviation is found'' would make the acceptance condition unambiguous for
    the reviewing model and the parser.'


# Target path
.reviewcompass/specs/workflow-management/reviews/2026-06-20-workflow-management-implementation-req14-criteria-run/review-criteria.md

# Target document
---
criteria_id: workflow-management-implementation-req14-approval-side-track-snapshot-transfer-review-criteria
phase: implementation
status: draft_for_prompt_quality_review
---

# workflow-management implementation req14-approval-side-track-snapshot-transfer API Review Criteria

## Review Task

Review the target for: Req 14 implementation upstream transfer for approval gates, side track stack, and workflow-state snapshot.

Primary judgment question:

Does the target satisfy Req 14 implementation upstream transfer for approval gates, side track stack, and workflow-state snapshot, while carrying upstream purpose, responsibility boundaries, acceptance criteria, forbidden actions, unresolved items, and intended transfer without omission, weakening, contradiction, unsupported addition, or drift?

Do not combine multiple independent judgments in this prompt. If another cluster, finding, artifact, or design-policy judgment is needed, create a separate criteria file and run separate prompt-quality review.

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

Do not treat this criteria file, a wrapper, or an author-written summary as a substitute for the target.

## Source Materials

### workflow-management-req14-upstream-intent

Purpose: Requirement 14 / design / tasks intent for approval gates, side track stack, and workflow-state snapshot.

- source_paths:
  - .reviewcompass/specs/workflow-management/requirements.md
  - .reviewcompass/specs/workflow-management/design.md
  - .reviewcompass/specs/workflow-management/tasks.md
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
5. Check that this review run and its model output do not approve or authorize commit, push, spec.json mutation, phase transition, or gate completion.

## Out Of Scope

- Req 15 structured effective prompt
- Req 16 proxy triage decision mechanics
- Do not approve or authorize commit, push, spec.json mutation, phase transition, or gate completion.
- These limits constrain this review run and the reviewing model; do not treat legitimate target code that implements workflow operations as a violation solely because it mentions those operations.
- Do not judge downstream correctness unless a target omission would force downstream invention.

## Finding Policy

- Use CRITICAL for bypass of human-only approval or irreversible-operation boundaries.
- Use ERROR for missing required behavior, weakened user requirements, or unsupported target behavior.
- Use WARN for meaningful ambiguity, weak traceability, or coverage gaps.
- Use INFO only for minor non-blocking improvements.
- Return findings: [] only when every required check passes with traceable evidence and no deviation from the preserved review requirements or upstream intent.

