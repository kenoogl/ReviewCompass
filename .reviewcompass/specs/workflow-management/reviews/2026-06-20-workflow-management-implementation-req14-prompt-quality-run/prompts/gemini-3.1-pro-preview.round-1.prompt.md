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
duration_seconds: 22.091
findings:
- severity: WARN
  target_location: '## Source Materials — Verification before review'
  description: The verification note states tests 'passed' but this is asserted inline
    rather than provided as an evidence excerpt or structured summary. The reviewing
    model cannot verify the claim and must treat it as an unconfirmed assertion.
  rationale: Source-material quality rules require that required source material be
    included as excerpt or structured summary in a model-readable form. A bare pass/fail
    assertion without a log excerpt or structured summary leaves the model unable
    to assess whether test coverage was actually exercised against the current implementation
    files.
- severity: WARN
  target_location: '## Review Target — target file list item for check-workflow-action.py'
  description: The entry for `tools/check-workflow-action.py` includes a parenthetical
    inline scope restriction ('only the workflow-snapshot and side-track-stack current
    CLI wiring, plus any approval-gate integration relevant to Req 14'). This narrows
    the file to a sub-section without specifying line ranges or a structured excerpt,
    which may cause inconsistent scoping across the three independent reviewers in
    the triad.
  rationale: Ambiguous file-scope instructions can cause one model to review the whole
    file while another reviews only the named sections, making triad findings non-comparable.
    A concrete line range or a manifest-level structured excerpt would make the scope
    deterministic.
- severity: WARN
  target_location: '## Required Checks — Check 4'
  description: Check 4 asks the model to verify that snapshot output 'has enough structured
    evidence to detect workflow-state drift without mutating state.' The phrase 'enough
    structured evidence' is evaluative but no acceptance threshold or minimum required
    fields are stated beyond the source materials bullet list. The model must independently
    decide what qualifies as sufficient, introducing framing latitude.
  rationale: Criterion 3 of General API Review Prompt Quality requires a non-leading
    but also well-bounded analysis question. Without an explicit minimum-fields criterion
    or reference to the Req 14 field list in Source Materials, different models in
    the triad may reach different conclusions about sufficiency, reducing inter-rater
    comparability.
- severity: WARN
  target_location: '## Finding Policy — severity label mapping'
  description: 'The finding policy defines four severity labels (CRITICAL, ERROR,
    WARN, INFO) and maps them to categories, but the INFO label is defined only implicitly
    via the example (''minor maintainability issues'') rather than by an explicit
    rule. The policy also does not state when `findings: []` is acceptable, which
    is a required element per the output-and-triage-fit criteria.'
  rationale: 'Output-and-triage-fit rules require the prompt to define when findings:
    [] is acceptable. Its absence may cause a conservative model to emit placeholder
    findings rather than an empty list, or an aggressive model to suppress findings
    it judges as below INFO threshold.'
- severity: INFO
  target_location: '## Review Task — Primary judgment question'
  description: The primary judgment question includes three coordinated sub-topics
    (approval gates, side-track stack, workflow-state snapshots) joined by 'and'.
    These are inseparable parts of Req 14 and are correctly unified, but the question
    would be marginally clearer if the phrase 'without creating an approval/proxy
    bypass or unintended state mutation path' were broken into two parallel clauses
    to match the two distinct risk types.
  rationale: Minor wording improvement; does not affect model judgment but would make
    the question easier to parse and map to finding severity categories.
- severity: INFO
  target_location: '## Source Materials — Tasks intent'
  description: The tasks intent section mentions T-017 required red tests before implementation
    but does not state whether the red-test-first obligation is in scope for the review
    (i.e., whether the model should verify that the test files predate the implementation
    commits) or whether it is background context only.
  rationale: Clarifying whether TDD ordering verification is in or out of scope would
    prevent the model from spending analysis budget on a git-history check it cannot
    perform from file contents alone, and would avoid inconsistent triad findings
    on this point.


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

The authoritative target file list is `req14-review-target-manifest.md`. The actual run must pass that manifest and every file listed there as target files, so the model sees current file contents rather than path stubs.

Human-readable target summary: approval/side-track/snapshot schemas, their three modules, `check-workflow-action.py` CLI wiring for `workflow-snapshot` and `side-track-stack current`, and four focused test files. If this summary and the manifest differ, the manifest is authoritative and the review should report the mismatch.

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
- TDD ordering is background only for this API review. Judge current test and implementation content; do not reconstruct git history.

Verification before review:

- Structured evidence:
  - command: `.venv/bin/python3 -m pytest tests/workflow-management/test_approval_gate.py tests/workflow-management/test_side_track_stack.py tests/workflow-management/test_workflow_state_snapshot.py tests/workflow-management/test_workflow_snapshot_cli.py -q`
  - observed result: `21 passed`
  - scope: approval gate, side-track stack, workflow-state snapshot, workflow-snapshot CLI.
- Full workflow-management test sweep:
  - command: `.venv/bin/python3 -m pytest tests/workflow-management -q`
  - observed result: `55 passed`
  - scope: all workflow-management focused tests present at implementation drafting completion.

## Required Checks

1. Check that approval records fail closed for missing or mismatched target operation, required action, digest, decision scope, and consumed state.
2. Check that proxy decisions cannot satisfy `human_only` gates or approval-required target operations.
3. Check that side-track stack constraints cannot be bypassed by missing allowed files, excessive depth, or ambiguous return condition.
4. Check that snapshot output has at least these structured evidence groups: `current_work`, `active_side_tracks`, `git_tree_summary`, `post_write_manifest_summary`, and `workflow_state_summary`; and that tests cover completed gate / operation contract drift.
5. Check that read-only CLI commands in scope do not write files or consume decisions.
6. Check that tests include explicit negative coverage for the fail-closed boundaries listed above.

## Out Of Scope

- Req 15 structured prompt audit.
- Req 16 implementation phase plan and proxy triage decision machine.
- Approval of phase movement or any spec.json update.

## Finding Policy

Return YAML only, without Markdown fences.

Use `CRITICAL` for approval/proxy bypass or unintended mutation by read-only CLI. Use `ERROR` for fail-closed defects or missing required evidence fields. Use `WARN` for meaningful test/evidence coverage gaps. Use `INFO` for minor maintainability or wording issues that do not affect safety or auditability.

Return the parser-compatible YAML shape defined by the review runner. Return `findings: []` only when no actionable implementation issue is found for Req 14.

