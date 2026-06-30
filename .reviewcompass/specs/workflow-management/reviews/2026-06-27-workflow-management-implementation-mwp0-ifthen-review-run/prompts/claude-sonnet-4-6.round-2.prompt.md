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
.reviewcompass/specs/workflow-management/reviews/2026-06-27-workflow-management-implementation-mwp0-ifthen-review-run/review-criteria.md

# Target document
---
criteria_id: wm-implementation-mwp0-ifthen-2026-06-27
phase: implementation
stage: triad-review
---

# workflow-management implementation review — MWP-0: if/then constraint completeness

## Review Task

Review the target files for: MWP-0 T-020 if/then constraint completeness.

Primary judgment question:

Do the if/then constraints added to `next_action_response.schema.json` in allOf entries ①②③⑤ implement all field constraints specified in 受入 11(6)①②③⑤ without omission, weakening, or unsupported addition, and does the test class `SchemaIfThenConstraintTests` sufficiently cover the specified constraints?

Do not combine multiple independent judgments in this prompt. This review covers only if/then constraint completeness. Kind value separation and reason/reasons separation are reviewed in separate criteria.

## Review Target

The authoritative target is the file set supplied by the review runner.

- `.reviewcompass/schema/next_action_response.schema.json`
- `tests/tools/test_t020_kind_redesign.py`

Do not treat this criteria file or any author-written summary as a substitute for the target files.

## Source Materials

### mwp0-if-then-upstream-intent

Purpose: Requirement 2 / design / tasks intent for if/then field constraints on required_action values.
Use as intent-transfer evidence and background only. Do not treat as a replacement for target files.

受入 11(6) — required_action 値ごとのフィールド制約（原文）:

```
① commit_stop_point の時：active_gate=null・phase=null・stage=null・blocked_by.type="commit_stop_point"
② run_reopen_pending_gate の時：active_gate 非 null・phase/stage は active_gate と一致・blocked_by=null
③ run_reopen_drafting の時：active_gate は stages/<phase>.yaml#drafting 形式・phase/stage はその drafting 単位と一致
④ repair_workflow_state の時（T-015 実装済み、本レビュー対象外）
⑤ wait_for_human_decision の時：blocked_by.type で停止理由を区別
⑥ run_maintenance の時（T-015 実装済み、本レビュー対象外）

上記①〜⑥の制約は D-003 §4.2 で確定している制約の全てであり、これ以外の required_action 種別には
確定した追加フィールド制約はない（universal 必須フィールドのみが適用される）。
```

設計 §5.2 — if/then 制約の配置方針:

```
受入 11(6) の制約①②③⑤は if/then 構文で next_action の allOf 内に定義する（MWP-0 T-020 の責務）。
```

T-020 先送り事項(a) — 完了条件 3:

```
(a) 受入 11(6)①②③⑤の required_action 値ごとのフィールド制約を next_action_response.schema.json の
    if/then 構文で定義する（④の repair_reasons と⑥の action_parameters は T-015 完了条件2で対処済みのため除外）。

完了条件 3: スキーマの if/then 制約（先送り事項(a)）の失敗テストが作成され、実装で通過する。
```

## Required Checks

1. Check each of ①②③⑤ in the allOf section: does the if/then entry enforce all and only the constraints stated in 受入 11(6) for that required_action value?
2. Check the SchemaIfThenConstraintTests class in the test file: does it cover the failure cases for each constraint clause stated in 受入 11(6)①②③⑤?
3. Check that the constraints for ④ and ⑥ (T-015 implemented) are present but are not weakened or removed by the new entries.
4. Check that no if/then entry adds constraints not specified in 受入 11(6) or design §5.2.

## Out Of Scope

- Kind value separation (7 values vs 3 values) — separate criteria
- reason vs reasons semantic separation — separate criteria
- Commit, push, spec.json update, phase completion, or human approval delegation

## Finding Policy

- Use CRITICAL for a constraint that bypasses a required_action boundary or allows a forbidden state.
- Use ERROR for a missing constraint clause, a weakened constraint, or a test gap that leaves a constraint unverifiable.
- Use WARN for meaningful ambiguity, weak traceability between requirement and schema clause, or partial coverage.
- Use INFO only for minor non-blocking improvements.
- Use precise target locations such as `path`, `path:allOf[n]`, or `path:class.method`.
- Return `findings: []` only when every constraint in 受入 11(6)①②③⑤ is fully and accurately implemented and tested.

