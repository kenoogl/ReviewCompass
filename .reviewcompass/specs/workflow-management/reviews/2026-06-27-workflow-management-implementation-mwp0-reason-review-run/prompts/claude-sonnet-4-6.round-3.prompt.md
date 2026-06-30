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
.reviewcompass/specs/workflow-management/reviews/2026-06-27-workflow-management-implementation-mwp0-reason-review-run/review-criteria.md

# Target document
---
criteria_id: wm-implementation-mwp0-reason-2026-06-27
phase: implementation
stage: triad-review
---

# workflow-management implementation review — MWP-0: reason vs reasons separation

## Review Task

Review the target files for: MWP-0 T-020 prior deferred item (b) — reason vs reasons semantic separation.

Primary judgment question:

Is the semantic distinction between the `reason` field inside `next_action` (described in design §5.3 as a common field for all kind values) and the top-level `reasons` array (one of the 5 required fields in the response) sufficiently defined in the schema and upstream design documents, and is the deferred item (b) from T-020 addressed?

Do not combine multiple independent judgments in this prompt. This review covers only the reason vs reasons separation. if/then constraints and kind value separation are reviewed in separate criteria.

## Review Target

The authoritative target is the file set supplied by the review runner.

- `.reviewcompass/schema/next_action_response.schema.json`
- `design-section-5-2-5-3-excerpt.md` (verbatim excerpt from `.reviewcompass/specs/workflow-management/design.md` §5.2 and §5.3, covering the reason/reasons fields and next_action required field list)

Do not treat this criteria file or any author-written summary as a substitute for the target files.

## Source Materials

### mwp0-reason-upstream-intent

Purpose: T-020 deferred item (b) text for background context.
The authoritative design document content is provided as `design-section-5-2-5-3-excerpt.md` in the review target above.
Use this section for background intent only.

T-020 先送り事項(b):

```
next_action 内の reason フィールドと最上位の reasons 配列の責務差を設計書と実装で明確化する。
```

T-020 完了条件一覧（reason に関連する条件の明示なし）:

```
1. next --json の kind 値域が7値に限定されること
2. commit-preflight サブコマンドが3値の kind を返すこと
3. スキーマの if/then 制約の失敗テストが作成され通過すること
4. WORKFLOW_NAVIGATION.md の更新
5. 廃止表現の統一

先送り事項(b)（reason vs reasons の責務明確化）に対応する完了条件は T-020 完了条件一覧に明示されていない。
```

## Required Checks

1. Check whether `next_action_response.schema.json` defines a `reason` field within `next_action.properties` or `next_action.required`, and whether this matches the intent described in design §5.3 (all-kind common field).
2. Check whether the top-level `reasons` array defined in the schema has a schema-level description or differentiation from the inner `reason` field.
3. Check whether the deferred item (b) from T-020 — "clarify the responsibility difference between the inner reason field and the top-level reasons array in design and implementation" — is addressed by either the schema (`next_action_response.schema.json`) or the design document excerpt (`design-section-5-2-5-3-excerpt.md`).
4. Check whether the presence or absence of `reason` in the schema matches what the design document (`design-section-5-2-5-3-excerpt.md` §5.3 common fields table) specifies. If the schema omits `reason` from `next_action.required` or `next_action.properties` while the design lists it as a common field, determine whether that omission is documented as intentional anywhere in the target files.

## Out Of Scope

- if/then field constraints — separate criteria
- kind value separation — separate criteria
- Commit, push, spec.json update, phase completion, or human approval delegation

## Finding Policy

- Use CRITICAL for a contradiction that breaks the schema's required field contract.
- Use ERROR for an unaddressed T-020 deferred item (b) where the required clarification is missing from both schema and upstream documents, or for a discrepancy between design §5.3 and the schema that is not intentional and not documented.
- Use WARN for meaningful ambiguity, undocumented intentional omission, or incomplete traceability between design §5.3 and schema.
- Use INFO only for minor non-blocking improvements.
- Use precise target locations such as `path` or `path:section`.
- Return `findings: []` only when the reason vs reasons distinction is sufficiently defined and T-020 deferred item (b) is verifiably addressed.

