---
criteria_id: api-review-prompt-quality-review
phase: prompt-quality
review_target: design-review-criteria-draft.md
---

# API Review Prompt Quality Review Criteria

Review the target prompt draft itself. Do not review `design.md` yet.

The question is:

Is the draft prompt suitable to use as the `--criteria-file` for an API-mediated design triad-review where the actual `--target` will be `.reviewcompass/specs/workflow-management/design.md`?

## Required Quality Checks

Check both general LLM-as-Judge prompt quality and this workflow's vertical-intent review requirements.

### General API review prompt quality

The prompt draft must:

1. Show that the main LLM identified the materials and judgment points before sending the prompt.
2. Include enough background and related design context for the model to avoid guessing.
3. Ask a non-leading analysis question.
4. Define a scope that is neither too broad nor too narrow.
5. Provide a fixed, parser-friendly output contract when combined with the API review runner template.
6. Avoid including credentials, personal data, or unrelated confidential material.

### Vertical intent transfer requirements

The prompt draft must:

1. Clearly distinguish review target, source materials, and out-of-scope material.
2. Limit the target judgment to the current phase artifact, here `design.md`.
3. Use source materials only for background and intent-transfer checking.
4. Avoid path-only source material listing.
5. Include upstream purpose, responsibility boundaries, acceptance criteria, forbidden actions, unresolved items, and intended target-phase transfer in a model-readable form.
6. Ensure the actual design artifact can be reviewed, rather than only an author-written summary.
7. Prevent the model from judging downstream tasks or implementation correctness.

## Finding Policy

- Report `ERROR` if the draft prompt would likely cause models to review the wrong target, rely on summaries instead of the real target, miss upstream-transfer obligations, or produce unusable output.
- Report `WARN` if the draft prompt is usable but has avoidable ambiguity, framing bias, or incomplete source-material presentation.
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
