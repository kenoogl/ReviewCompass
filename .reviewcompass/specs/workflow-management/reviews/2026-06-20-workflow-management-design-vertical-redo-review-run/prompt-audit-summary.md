# Prompt Audit Summary

review_run_id: `2026-06-20-workflow-management-design-vertical-redo-review-run`
audited_artifacts:
- `review-target.md`
- `prompts/gpt-5.4.round-1.prompt.md`
- `prompts/claude-sonnet-4-6.round-1.prompt.md`
- `prompts/gemini-3.1-pro-preview.round-1.prompt.md`
audit_date: 2026-06-20
audit_scope: Review the API review prompt quality before accepting the design triad-review result.

## Verdict

The review intent and check list are appropriate, but the generated API prompts are not strong enough to accept the `findings: []` result as a design triad-review completion basis.

The main issue is target materialization. The prompt asks models to review `design.md`, but the actual `# Target document` is `review-target.md`, not the current `design.md` body. The current design is represented only as a short summary. This can make models validate the summary rather than independently inspect the design document.

## Findings

### PA-001: Target document is the review wrapper, not `design.md`

Severity: ERROR

Evidence:
- `prompts/gpt-5.4.round-1.prompt.md` sets `# Target path` to `.reviewcompass/specs/workflow-management/reviews/2026-06-20-workflow-management-design-vertical-redo-review-run/review-target.md`.
- The `# Target document` section repeats `review-target.md`.
- `target-manifest.yaml` records only `review-target.md`.

Why this matters:

The review purpose is to verify whether `design.md` carries Requirement 13 through Requirement 16. A model can only do that reliably if the relevant `design.md` text is included as target material, not only summarized by the prompt author.

### PA-002: Criteria and target contain the same author-written summary

Severity: WARN

Evidence:
- The same `review-target.md` content is passed as `--criteria-file` and `--target`.
- The prompt therefore contains the review author's framing twice: once under `# Criteria` and once under `# Target document`.

Why this matters:

This increases framing bias. The models may check whether the summary is self-consistent instead of checking whether the underlying design text actually supports the summary.

### PA-003: Source documents are path-listed, but not materially included

Severity: WARN

Evidence:
- `source_documents` lists `requirements.md`, `design.md`, `spec.json`, the reopen YAML, the classification record, and the session guide.
- The prompt includes structured summaries for requirements and design, but not the actual relevant excerpts from `design.md` or the reopen YAML.

Why this matters:

The vertical intent transfer discipline requires enough source material for the model to judge without guessing. Summaries help, but they are weaker than concrete excerpts when the question is traceability and omission detection.

## What Was Good

- The prompt clearly explains why the review is being rerun.
- The prompt identifies the two high-risk design-authority questions: registry/contract authority and proxy/human boundary.
- The required checks are specific and aligned with vertical intent transfer.
- The output contract is strict and parser-friendly.
- The adversarial role uses `claude-sonnet-4-6`, matching the user instruction.

## Recommendation

Do not mark `stages/design.yaml#triad-review` complete from this run alone.

Prepare a corrected review bundle and rerun the API review with:

- `--target .reviewcompass/specs/workflow-management/design.md`
- `--criteria-file` pointing to a review prompt / criteria file that includes the upstream requirements summary, current reopen context, required checks, out-of-scope rules, and finding policy
- optionally additional target files when supported, such as `requirements.md` and the reopen YAML, or concrete excerpts embedded in the criteria file

The corrected `target-manifest.yaml` should include `design.md` at minimum. The review target should not be only the prompt wrapper.

## Stop Point

This prompt audit invalidates the current no-findings review run as a sufficient gate-completion basis. Do not advance design triad-review, update `spec.json` to `design.triad-review=true`, or move the reopen gate until a corrected review run is completed or the user explicitly decides to accept the weaker evidence.
