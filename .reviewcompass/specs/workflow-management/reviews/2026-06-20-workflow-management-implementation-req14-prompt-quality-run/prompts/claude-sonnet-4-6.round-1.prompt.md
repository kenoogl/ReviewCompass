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
The top-level key must be exactly findings.
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

If there are no findings, return exactly:

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
.reviewcompass/specs/workflow-management/reviews/2026-06-20-workflow-management-implementation-review-prompt-quality-run/req14-api-review-criteria-draft.md

# Target document
---
criteria_id: workflow-management-implementation-req14-review-2026-06-20-draft
phase: implementation.triad-review
review_target: .reviewcompass/specs/workflow-management/reviews/2026-06-20-workflow-management-implementation-review-run/req14-review-target-manifest.md
intended_actual_run_dir: .reviewcompass/specs/workflow-management/reviews/2026-06-20-workflow-management-implementation-req14-review-run
intended_variant: implementation_review_independent_3way_codex_operator
---

# Req 14 Implementation Review Criteria Draft

## Review Task

Primary judgment question:

Does the Req 14 implementation correctly preserve the approved requirements → design → tasks intent for approval gates, side-track stack, and workflow-state snapshots, without creating an approval/proxy bypass or unintended state mutation path?

## User Review Requirements

This is one item-specific prompt for `workflow-management / implementation / triad-review`.

- Review purpose: defect detection for Req 14 implementation.
- Review object: Req 14 schema, modules, CLI exposure, and tests.
- Review focus: approval/proxy boundary, decision consumption, digest/target binding, side-track scope and depth, snapshot drift detection, read-only CLI boundaries.
- Scope boundaries: do not review Req 15 or Req 16 except where `check-workflow-action.py` wiring creates a direct boundary issue.
- Prohibited actions: do not authorize commit, push, phase completion, approval, proxy application, or spec.json update.

## Review Target

The actual run must pass these files as target files so the model sees their current contents:

- `.reviewcompass/schema/approval_gate.schema.json`
- `.reviewcompass/schema/side_track_stack.schema.json`
- `.reviewcompass/schema/workflow_state_snapshot.schema.json`
- `tools/check_workflow_action/approval_gate.py`
- `tools/check_workflow_action/side_track_stack.py`
- `tools/check_workflow_action/workflow_state_snapshot.py`
- `tools/check-workflow-action.py` (only the `workflow-snapshot` and `side-track-stack current` CLI wiring, plus any approval-gate integration relevant to Req 14)
- `tests/workflow-management/test_approval_gate.py`
- `tests/workflow-management/test_side_track_stack.py`
- `tests/workflow-management/test_workflow_state_snapshot.py`
- `tests/workflow-management/test_workflow_snapshot_cli.py`

## Source Materials

Requirement 14 requires:

- approval gate records with decision scope, target operation, target required action, artifact digest, staged file set digest, source digest, next-action expectation, and consumed state;
- proxy / human boundaries where `human_only` cannot be satisfied by proxy decision;
- side-track stack with allowed files, max depth, return conditions, and mainline restoration;
- workflow-state snapshot containing current work, side tracks, git tree summary, post-write manifest summary, and workflow state summary;
- drift detection for pending/completed gates, staged file set, operation contract, and snapshot evidence.

Design intent:

- read-only operations must stay read-only: `workflow-snapshot` and `side-track-stack current` must not mutate files;
- mutating helper functions, if present in modules, may only be accepted when they are bounded by explicit operation contract / caller responsibility and are not exposed by the read-only CLI;
- decision records must fail closed on target mismatch, digest mismatch, unresolved/non-approved decision, or human-only boundary.

Tasks intent:

- T-017 required red tests before implementation;
- tests must include negative cases for `binding_kind=none`, target operation mismatch, digest mismatch, side-track allowed_files/max_depth, and snapshot completed gate / operation contract drift.

Verification before review:

- `tests/workflow-management/test_approval_gate.py tests/workflow-management/test_side_track_stack.py tests/workflow-management/test_workflow_state_snapshot.py tests/workflow-management/test_workflow_snapshot_cli.py -q`: passed.

## Required Checks

1. Check that approval records fail closed for missing or mismatched target operation, required action, digest, decision scope, and consumed state.
2. Check that proxy decisions cannot satisfy `human_only` gates or approval-required target operations.
3. Check that side-track stack constraints cannot be bypassed by missing allowed files, excessive depth, or ambiguous return condition.
4. Check that snapshot output has enough structured evidence to detect workflow-state drift without mutating state.
5. Check that read-only CLI commands in scope do not write files or consume decisions.
6. Check that tests include explicit negative coverage for the fail-closed boundaries listed above.

## Out Of Scope

- Req 15 structured prompt audit.
- Req 16 implementation phase plan and proxy triage decision machine.
- Approval of phase movement or any spec.json update.

## Finding Policy

Return YAML only, without Markdown fences.

Use `CRITICAL` for approval/proxy bypass or unintended mutation by read-only CLI. Use `ERROR` for fail-closed defects or missing required evidence fields. Use `WARN` for meaningful test/evidence coverage gaps. Use `INFO` for minor maintainability issues.

findings:
  - severity: ERROR
    target_location: path:line-or-section
    description: concise finding summary
    rationale: why this matters

If there are no findings, return exactly:

findings: []

