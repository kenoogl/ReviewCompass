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
duration_seconds: 21.828
findings:
- severity: WARN
  target_location: Source Materials / Verification before review
  description: Verification evidence is stated as prose assertions ('13 passed', 'OK')
    rather than structured excerpts or attached test output.
  rationale: A reviewing model cannot independently confirm the verification claims.
    Inline structured summaries or excerpts of actual test output would let the model
    distinguish confirmed-passing boundaries from unverified ones, reducing the risk
    of treating unverified claims as evidence.
- severity: WARN
  target_location: Review Target (file list)
  description: The target manifest path is declared in the front matter but the criteria
    draft does not confirm that the manifest will contain all eleven listed files
    as actual content, not path-only references.
  rationale: If the manifest lists paths without including file content or structured
    summaries, the reviewing model will have to judge against path stubs rather than
    real artifact content, which risks missing defects in schema fields, predicate
    logic, and CLI wiring.
- severity: WARN
  target_location: Source Materials (Req 14 / Req 15 cross-reference)
  description: The prompt states that Req 14 approval gate internals and Req 15 prompt
    audit internals are out of scope 'except as source evidence for proxy blocking,'
    but provides no excerpt or structured summary of the approval-gate record schema
    or structured-prompt evidence fields that the proxy triage checker is expected
    to consume.
  rationale: Without at least a minimal structured summary of the upstream evidence
    fields, the model cannot verify whether the proxy triage decision checker correctly
    reads and fails-closed on missing Req 14 / Req 15 source evidence, which is a
    stated Required Check (items 3 and 4).
- severity: WARN
  target_location: Required Checks / Check 7
  description: The check for unresolved review-wave consumer impact blocking references
    'required carry-forward and downstream impact evidence' without defining what
    constitutes sufficient carry-forward evidence or where in the target files it
    should appear.
  rationale: Ambiguous acceptance criteria for a boundary check increases the risk
    that the reviewing model applies inconsistent or overly lenient judgment when
    evaluating test_review_wave_consumer_impact.py coverage.
- severity: INFO
  target_location: Finding Policy (example YAML block)
  description: The finding policy section includes an example YAML finding with a
    placeholder format ('path:line-or-section') that is slightly inconsistent with
    the API runner output contract, which expects a plain string for target_location.
  rationale: Minor ergonomics issue; the placeholder format is clear enough but could
    be made explicitly illustrative to avoid a model interpreting 'path:line-or-section'
    as a required literal format.
- severity: INFO
  target_location: Front matter / intended_actual_run_dir
  description: The intended_actual_run_dir value differs from the review_target directory
    prefix, which may cause confusion about where artifacts will be written during
    the actual run.
  rationale: Not a blocking issue but noting the directory name inconsistency (prompt-quality-run
    vs implementation-req16-review-run) for traceability during actual run setup.


# Target path
.reviewcompass/specs/workflow-management/reviews/2026-06-20-workflow-management-implementation-review-prompt-quality-run/req16-api-review-criteria-draft.md

# Target document
---
criteria_id: workflow-management-implementation-req16-review-2026-06-20-draft
phase: implementation.triad-review
review_target: .reviewcompass/specs/workflow-management/reviews/2026-06-20-workflow-management-implementation-review-run/req16-review-target-manifest.md
intended_actual_run_dir: .reviewcompass/specs/workflow-management/reviews/2026-06-20-workflow-management-implementation-req16-review-run
intended_variant: implementation_review_independent_3way_codex_operator
---

# Req 16 Implementation Review Criteria Draft

## Review Task

Primary judgment question:

Does the Req 16 implementation correctly provide read-only implementation phase controls and proxy triage decision checks that preserve human-required boundaries and active reopen / impact review scope separation?

## User Review Requirements

This is one item-specific prompt for `workflow-management / implementation / triad-review`.

- Review purpose: defect detection for Req 16 implementation.
- Review object: implementation phase schema/plan, operation-list, proxy triage decision schema/checks, review-wave consumer impact checks, and CLI wiring.
- Review focus: Phase 0–6 coverage, read-only operation-list and implementation-phase-check, fixed human-required predicate order, proxy decision evidence completeness/coverage, approval scope mismatch, active reopen scope versus `spec.json.reopened`, unresolved review-wave impact blocking.
- Scope boundaries: do not review Req 14 or Req 15 except where proxy triage checks consume approval/prompt evidence as source material.
- Prohibited actions: do not authorize commit, push, phase completion, approval, proxy application, or spec.json update.

## Review Target

The authoritative target file list is `req16-review-target-manifest.md`. The actual run must pass that manifest and every file listed there as target files. The inline summary below is for human readability only; if it differs from the manifest, report the mismatch.

Human-readable target summary: implementation phase schema/plan; proxy triage decision schema; implementation phase checker; operation-list builder; proxy triage decision checker; CLI wiring for `implementation-phase-check`, `operation-list`, and `proxy-triage-decision-check`; and five focused T-019 test files.

## Source Materials

Requirement 16 requires:

- Phase 0–6 implementation plan and schema, with entry criteria, exit criteria, allowed operations, forbidden operations, required tests, and commit boundary;
- Phase 2 read-only `operation-list --json` that reports operation `canonical_commands`, `effect_kind`, `approval_required`, `sequence`, and `pending_conflicts` without changing `next --json`;
- proxy triage decision schema containing raw response, parsed findings, decision prompt, proxy raw response, candidate decisions, selected decision, reasoning summary, final application target, and approval scope;
- human-required predicate based on evidence completeness, finding/cluster coverage, operation contract, approval gate record, review-wave impact, and active reopen / impact review scope;
- fixed priority where human-only decision, unresolved approval gate, `approval_required=true` operation, and unresolved review-wave impact override proxy labels like leave-as-is or proxy-approved;
- `spec.json.reopened` treated as history, not active reopen scope.

Design intent:

- `implementation-phase-check`, `operation-list`, and `proxy-triage-decision-check` are read-only CLI commands and must not mutate workflow state, review-run artifacts, approvals, or spec.json;
- proxy decision checks may return `DEVIATION` and block proxy apply, but they do not apply fixes or triage decisions;
- active reopen scope must come from reopen records, while `spec.json.reopened` remains historical context.
- Req 14 source evidence expected by proxy checks: approval gate record fields include `decision_scope`, `decision`, `decided_by`, `target_operation_id`, `target_required_action`, `binding_kind`, digests, and `consumed`.
- Req 15 source evidence expected by proxy/phase checks: structured prompt evidence fields include prompt manifest path/sha256, source artifact path/sha256, operation contract ID/sha256, and postcondition/on_completion compatibility status.

Tasks intent:

- T-019 required red tests first and implementation without altering those tests;
- tests must cover Phase 0–6 coverage, read-only operation-list preserving `next --json`, proxy evidence completeness, human-required priority, coverage mismatch, approval scope mismatch, fixed predicate order, and review-wave consumer impact blocking.

Verification before review:

- Structured evidence:
  - command: `.venv/bin/python3 -m pytest tests/workflow-management/test_implementation_phase_plan.py tests/workflow-management/test_operation_list_read_only.py tests/workflow-management/test_proxy_triage_decision_machine.py tests/workflow-management/test_review_wave_consumer_impact.py tests/workflow-management/test_implementation_phase_cli.py -q`
  - observed result: `13 passed`
  - scope: phase plan, operation-list read-only behavior, proxy triage decision checks, review-wave consumer impact, CLI.
- Related operation contract evidence:
  - command: `.venv/bin/python3 -m pytest tests/workflow-management/test_operation_contract_cli.py tests/workflow-management/test_operation_contract_schema.py tests/workflow-management/test_required_action_contract_mapping.py -q`
  - observed result: `12 passed`
  - scope: operation contract/schema/required_action connection.
- CLI evidence:
  - command: `.venv/bin/python3 tools/check-workflow-action.py implementation-phase-check --feature workflow-management --json`
  - observed result: `verdict=OK`
  - command: `.venv/bin/python3 tools/check-workflow-action.py operation-list --json`
  - observed result: `verdict=OK`, `operation_mode=read_only`.

## Required Checks

1. Check Phase 0–6 plan coverage and whether `active_phase` / criteria fields are meaningful enough for implementation control.
2. Check that `operation-list` is read-only and preserves `next --json` behavior.
3. Check that proxy triage decision schema and checker fail closed on missing raw/prompt/candidate/selected/reason/target evidence.
4. Check that human-required predicate priority cannot be bypassed by proxy-selected `leave-as-is` or `proxy_approved`.
5. Check that approval scope mismatch and coverage mismatch return `DEVIATION`.
6. Check that `spec.json.reopened` is not treated as active reopen scope.
7. Check that unresolved review-wave consumer impact blocks proxy apply unless evidence includes: a carry-forward register entry or equivalent structured register data, downstream impact decisions, and `spec_recheck.impacted_downstream_phases`.
8. Check that tests cover each listed fail-closed boundary.

## Out Of Scope

- General implementation of actual proxy apply or triage mutation.
- Req 14 approval gate internals except as source evidence for proxy blocking.
- Req 15 prompt audit internals except as source evidence for structured prompt controls.
- Any phase movement or approval.

## Finding Policy

Return YAML only, without Markdown fences.

Use `CRITICAL` for proxy or phase controls that would bypass human-required evidence or mutate state through read-only commands. Use `ERROR` for fail-closed or evidence completeness defects. Use `WARN` for meaningful plan, coverage, or auditability gaps. Use `INFO` for minor maintainability or wording issues that do not affect safety or auditability.

Return the parser-compatible YAML shape defined by the review runner. Return `findings: []` only when no actionable implementation issue is found for Req 16.

