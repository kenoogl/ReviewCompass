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
.reviewcompass/specs/workflow-management/reviews/2026-06-20-workflow-management-implementation-review-prompt-quality-run/req15-api-review-criteria-draft.md

# Target document
---
criteria_id: workflow-management-implementation-req15-review-2026-06-20-draft
phase: implementation.triad-review
review_target: .reviewcompass/specs/workflow-management/reviews/2026-06-20-workflow-management-implementation-review-run/req15-review-target-manifest.md
intended_actual_run_dir: .reviewcompass/specs/workflow-management/reviews/2026-06-20-workflow-management-implementation-req15-review-run
intended_variant: implementation_review_independent_3way_codex_operator
---

# Req 15 Implementation Review Criteria Draft

## Review Task

Primary judgment question:

Does the Req 15 implementation correctly separate structured language-task judgment from machine execution, while preserving review-run effective prompt metadata compatibility?

## User Review Requirements

This is one item-specific prompt for `workflow-management / implementation / triad-review`.

- Review purpose: defect detection for Req 15 implementation.
- Review object: structured prompt schemas, prompt audit/builder, review-run rounds metadata plumbing, and tests.
- Review focus: language_task schema vocabulary, prompt manifest source/digest coverage, machine task exclusion, on_completion compatibility, prompt manifest recording without deleting existing text prompt metadata.
- Scope boundaries: do not review Req 14 approval gate or Req 16 phase/proxy controls except where the prompt audit directly references those boundaries.
- Prohibited actions: do not authorize commit, push, phase completion, approval, proxy application, or spec.json update.

## Review Target

The actual run must pass these files as target files:

- `.reviewcompass/schema/language_task_io.schema.json`
- `.reviewcompass/schema/effective_prompt_manifest.schema.json`
- `tools/check_workflow_action/effective_prompt_builder.py`
- `tools/check_workflow_action/prompt_audit.py`
- `tools/api_providers/run_role.py` (only prompt manifest path/sha256 recording and compatibility with existing effective prompt fields)
- `tools/api_providers/run_review.py` (only propagation of prompt manifest metadata to `update_review_run_artifacts`)
- `tools/check-workflow-action.py` (only `prompt-audit` CLI wiring)
- `tests/workflow-management/test_language_task_io_schema.py`
- `tests/workflow-management/test_effective_prompt_manifest.py`
- `tests/workflow-management/test_prompt_audit.py`
- `tests/workflow-management/test_prompt_manifest_rounds_recording.py`

## Source Materials

Requirement 15 requires:

- `language_task` with `document_kind`, `input`, `output_format`, and `constraints`;
- `input.required_files`, `input.state_refs`, `input.source_refs`;
- `output_format.kind`, `output_format.required_sections`, and `output_format.schema_ref`;
- effective prompt manifest with `decision_point`, `source_artifacts`, `required_disciplines`, `operation_contract`, `expected_output_schema`, `prompt_length`, `preconditions_checked`, `language_task`, `postconditions`, and `on_completion`;
- prompt audit that detects source/digest gaps, machine task leakage, direct state mutation, output schema gaps, prompt length bounds issues, and next-action/on_completion conflict;
- review-run `rounds.yaml` recording of prompt manifest path/sha256 while preserving existing effective prompt path/sha256 fields.

Design intent:

- `language_task` describes what the model judges; it must not include git operations, review-run artifact creation, approval consume, side-track mutation, operation execution, or direct workflow/spec mutation;
- `prompt-audit` is read-only and cannot itself authorize completion, commit, push, approval, or state mutation;
- `run_role.py` and `run_review.py` may write review-run artifacts as part of their existing review-run artifact responsibility, but the Req 15 change is limited to adding prompt manifest metadata fields and must not replace text effective prompt metadata.

Tasks intent:

- T-018 required red tests first and implementation without altering those tests;
- text-only effective prompt fields remain P1-compatible during transition;
- manifest field presence should improve auditability without breaking existing review-run consumers.

Verification before review:

- T-018 tests passed: `9 passed`.
- `tools/api_providers/tests/test_run_role.py tools/api_providers/tests/test_run_review.py -q`: `31 passed`.

## Required Checks

1. Check that schema vocabulary is fail-closed for unknown machine-action fields.
2. Check that `prompt_audit.py` rejects direct state mutation, machine execution tasks, and incompatible `on_completion`.
3. Check that read-only `prompt-audit` CLI does not write state or consume approvals.
4. Check that `run_role.py` and `run_review.py` preserve existing effective prompt fields while adding manifest fields.
5. Check that source/digest/prompt length structures are specific enough for later audit.
6. Check that tests include negative coverage for machine-task leakage, unknown fields, missing source digest, prompt bounds, on_completion conflict, and metadata coexistence.

## Out Of Scope

- General quality of all API provider code unrelated to prompt manifest metadata.
- Req 14 approval gate implementation.
- Req 16 proxy triage decision implementation.
- Any phase movement or approval.

## Finding Policy

Return YAML only, without Markdown fences.

Use `CRITICAL` for prompt audit or metadata plumbing that authorizes or implies irreversible actions. Use `ERROR` for schema/audit defects that permit machine execution leakage or lose required metadata. Use `WARN` for meaningful compatibility or coverage gaps. Use `INFO` for minor maintainability issues.

findings:
  - severity: ERROR
    target_location: path:line-or-section
    description: concise finding summary
    rationale: why this matters

If there are no findings, return exactly:

findings: []

