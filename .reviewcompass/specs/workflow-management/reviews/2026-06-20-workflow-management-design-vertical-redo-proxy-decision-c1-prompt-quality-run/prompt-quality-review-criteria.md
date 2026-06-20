---
criteria_id: proxy-decision-c1-prompt-quality-review
phase: prompt-quality
review_target: proxy-decision-c1-prompt.md
---

# Proxy Decision C1 Prompt Quality Review Criteria

Review the target prompt draft itself. Do not decide C1.

The question is:

Is the draft prompt suitable to give to a proxy_model for deciding only C1, the operation contract / registry / preflight authority boundary cluster, in the `workflow-management` design triad-review?

## Required Quality Checks

### User Review Requirements Fit

The prompt draft must:

1. Preserve the instruction to judge items individually.
2. Judge C1 only and exclude C2-C7.
3. Ask for cluster validity, final label, adopted / rejected findings, required design response, and downstream risk.
4. Avoid direct edits, implementation, commit, push, `spec.json` update, gate completion, or human-only approval.

### Judgment Granularity

The prompt draft must:

1. Contain one primary judgment question.
2. Avoid bundling multiple independent clusters or design-policy judgments.
3. Include only source findings and materials needed for C1.
4. Keep common background short enough that C1-specific evidence remains central.

### Source-Material Quality

The prompt draft must:

1. Clearly distinguish review target, source materials, source findings, and out-of-scope work.
2. Include enough Requirement 12 / 13 context to judge operation contract / registry / preflight authority.
3. Include the current design material relevant to C1 in model-readable form.
4. Include all C1 source finding IDs and enough finding content for traceability.
5. Avoid path-only source material listing as the only basis for judgment.

### Output And Triage Fit

The prompt draft must:

1. Return output compatible with `tools/api_providers/run_proxy_decision.py`: top-level `proxy_model_id` and `decisions` list.
2. Require every C1 source finding ID to be adopted or rejected.
3. Define allowed labels and consistency rules.
4. Confirm authority limits explicitly.
5. Avoid parser-hostile placeholders or ambiguous empty-list instructions.

## Finding Policy

- Report `CRITICAL` if the draft prompt would authorize or imply authorization of commit, push, `spec.json` update, phase transition, gate completion, direct edits, or human-only approval.
- Report `ERROR` if the draft prompt judges anything beyond C1, omits a C1 source finding, lacks required Requirement 12 / 13 context, or produces output unusable by `run_proxy_decision.py`.
- Report `WARN` if the draft prompt is usable but has avoidable ambiguity, framing bias, incomplete source-material presentation, or weak target/source/out-of-scope separation.
- Report `INFO` for minor wording or ergonomics improvements.
- Return `findings: []` only if the draft prompt is safe to use for the intended C1 proxy_model judgment.

## Output Contract

Return YAML only with top-level key `findings`.

Each finding must include:

- `severity`: CRITICAL, ERROR, WARN, or INFO
- `target_location`: specific section in the prompt draft
- `description`: concise finding summary
- `rationale`: why this matters for C1 proxy decision prompt quality

If there are no findings, return exactly:

findings: []
