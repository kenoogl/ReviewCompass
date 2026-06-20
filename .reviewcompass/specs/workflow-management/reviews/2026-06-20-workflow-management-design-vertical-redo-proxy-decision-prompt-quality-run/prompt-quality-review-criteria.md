---
criteria_id: proxy-decision-prompt-quality-review
phase: prompt-quality
review_target: proxy-decision-prompt-draft.md
---

# Proxy Decision Prompt Quality Review Criteria

Review the target prompt draft itself. Do not judge the C1-C7 clusters yet.

The question is:

Is the draft prompt suitable to give to a proxy_model for deciding C1-C7 cluster validity, final triage labels, and required design responses for the `workflow-management` design triad-review?

If user-provided review requirements exist, also judge whether the draft prompt preserves and operationalizes those requirements without unauthorized narrowing, broadening, replacement, or added authority.

## Required Quality Checks

Check both general LLM-as-Judge prompt quality and the workflow-specific proxy decision requirements.

### General API Review Prompt Quality

The prompt draft must:

1. Show that main identified the materials and judgment points before sending the prompt.
2. Include enough background and related context for the model to avoid guessing.
3. Ask a non-leading analysis question.
4. Define a scope that is neither too broad nor too narrow.
5. Provide or rely on a fixed, parser-friendly output contract when combined with the API review runner template.
6. Avoid credentials, personal data, or unrelated confidential material.
7. Keep prompt-review target, proxy judgment target, source materials, and out-of-scope operations distinct.

### User Review Requirements Fit

The prompt draft must:

1. Preserve the user instruction to use proxy_model for judgment.
2. Preserve the later user correction that the newly created prompt-review mechanism must be used before proxy_model judgment.
3. Map those requirements into the review task, required checks, out of scope, and finding policy.
4. Avoid narrowing the requested review so that any C1-C7 cluster is silently omitted.
5. Avoid broadening the requested review into direct edits, implementation, commit, push, `spec.json` updates, or gate completion.
6. Avoid replacing the requested proxy judgment with a generic design review.
7. Mark assumptions explicitly when the user requirement is ambiguous.

### Proxy Decision Requirements

The prompt draft must:

1. Ask proxy_model to decide cluster validity, final label, adopted / rejected findings, required design response, and downstream risk.
2. Allow proxy_model to confirm, weaken, strengthen, split, merge, or reject clusters instead of forcing a closed choice.
3. Include source finding IDs and enough source finding content for traceability.
4. Include model-result context and target identity for the v2 review-run.
5. Include upstream requirements context for Requirement 13 through 16.
6. Include current design context relevant to each cluster.
7. Keep proxy_model from authorizing human-only or irreversible operations.
8. Produce output that can be converted into proxy decision YAML without losing cluster / finding traceability.

### Vertical Intent Transfer Requirements

Because this is a design triad-review decision, the prompt draft must:

1. Limit target judgment to the current design phase artifact and the C1-C7 review clusters.
2. Use requirements material only for background and intent-transfer checking.
3. Include upstream purpose, responsibility boundaries, acceptance criteria, forbidden actions, unresolved items, and intended design transfer where relevant.
4. Prevent the model from judging downstream tasks or implementation correctness unless downstream invention would be forced by a design omission.

## Finding Policy

- Report `CRITICAL` if the draft prompt would authorize or imply authorization of commit, push, `spec.json` update, phase transition, gate completion, direct edits, or human-only approval.
- Report `CRITICAL` if the draft prompt would violate a user-stated prohibited action or authority limit.
- Report `ERROR` if the draft prompt omits, weakens, broadens, or replaces the user-stated proxy judgment requirement.
- Report `ERROR` if the draft prompt would likely cause proxy_model to judge the wrong target, rely only on main's labels, omit any C1-C7 cluster, miss required upstream-transfer obligations, or produce output unusable as proxy decision evidence.
- Report `WARN` if the draft prompt is usable but has avoidable ambiguity, framing bias, incomplete source-material presentation, weak target/source/out-of-scope separation, or incomplete mapping from user requirements to checks.
- Report `INFO` for minor wording or ergonomics improvements.
- Return `findings: []` only if the draft prompt is safe to use for the intended proxy_model judgment.

## Output Contract

Return YAML only with top-level key `findings`.

Each finding must include:

- `severity`: CRITICAL, ERROR, WARN, or INFO
- `target_location`: specific section in the prompt draft
- `description`: concise finding summary
- `rationale`: why this matters for proxy decision prompt quality

If there are no findings, return exactly:

findings: []
