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
.reviewcompass/specs/workflow-management/reviews/2026-06-27-workflow-management-implementation-mwp0-kind-sep-review-run/review-criteria.md

# Target document
---
criteria_id: wm-implementation-mwp0-kind-sep-2026-06-27
phase: implementation
stage: triad-review
---

# workflow-management implementation review — MWP-0: kind value separation

## Review Task

Review the target files for: MWP-0 kind value separation between `next --json` and `commit-preflight`.

Primary judgment question:

Does the implementation ensure that `next --json` outputs only the 7 specified kind values and `commit-preflight` outputs only the 3 specified kind values, as required by 受入 12 and T-020 completion conditions 1 and 2?

Do not combine multiple independent judgments in this prompt. This review covers only kind value separation. if/then constraint completeness and reason/reasons separation are reviewed in separate criteria.

## Review Target

The authoritative target is the file set supplied by the review runner.

- `.reviewcompass/schema/next_action_response.schema.json`
- `.reviewcompass/schema/commit_preflight_response.schema.json`
- `commit-preflight-implementation-excerpt.py` (extracted from `tools/check-workflow-action.py` lines 4151-4223)
- `tests/tools/test_t020_kind_redesign.py`

Do not treat this criteria file or any author-written summary as a substitute for the target files.

## Source Materials

### mwp0-kind-separation-upstream-intent

Purpose: Requirement 2 受入 12 and T-020 completion conditions 1–2 as upstream intent for kind value separation.
Use as intent-transfer evidence and background only. Do not treat as a replacement for target files.

受入 12 — kind 値分離の仕様（原文）:

```
本機能は commit_candidate、commit_mixing_risk、commit_unit_stale の3種類の判定を next --json の
kind から除外し、commit-preflight サブコマンドの出力にのみ含める。これらの判定は「作業の現在地カテゴリ」
ではなく「コミット操作の前確認」であり、next --json の kind は作業の現在地のみを示す7種類
（completed / in_progress / blocking_in_progress / verification_pending /
  reopen_in_progress / feature_definition_required / unknown）に限定する。
```

T-020 完了条件 1–2:

```
1. next --json の kind 値域が7値に限定され、旧3値が出力されないことを pytest で確認できる。
2. commit-preflight サブコマンドが3値の kind を返し、他の kind を返さないことを pytest で確認できる。
```

### kind-value-constants

```
next --json の許容 kind 値（7つ）:
  in_progress, blocking_in_progress, verification_pending,
  reopen_in_progress, feature_definition_required, completed, unknown

commit-preflight の許容 kind 値（3つ）:
  commit_candidate, commit_mixing_risk, commit_unit_stale
```

## Required Checks

1. Check that `next_action_response.schema.json` defines exactly the 7 permitted kind values in the enum.
2. Check that `commit_preflight_response.schema.json` defines exactly the 3 permitted kind values in the enum.
3. Check that the `_commit_preflight_next_action` implementation in the excerpt can only return kind values that are acceptable under 受入 12. Trace all code paths including delegated functions where their return kind can be determined.
4. Check that the test classes `NextActionSchemaKindValueTests`, `CommitPreflightSchemaTests`, `NextActionKindBehaviorTests`, and `CommitPreflightKindBehaviorTests` in `test_t020_kind_redesign.py` cover the key directions of T-020 completion conditions 1 and 2.
5. Check whether the test `test_commit_preflight_kind_is_always_commit_related` accurately reflects the constraints of 受入 12.

## Out Of Scope

- if/then field constraints (①②③⑤) — separate criteria
- reason vs reasons semantic separation — separate criteria
- Commit, push, spec.json update, phase completion, or human approval delegation

## Finding Policy

- Use CRITICAL for a code path that definitively violates the kind value boundary stated in 受入 12.
- Use ERROR for a schema enum mismatch, a missing test direction, a test assertion that contradicts the acceptance criterion, or a code path that makes the kind separation unverifiable.
- Use WARN for meaningful ambiguity, weak test traceability, or a code path where the kind value cannot be determined from the provided material.
- Use INFO only for minor non-blocking improvements.
- Use precise target locations such as `path`, `path:function`, or `path:class.method`.
- Return `findings: []` only when kind separation is fully and correctly implemented and verified.

