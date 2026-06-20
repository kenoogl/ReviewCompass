# Prompt Quality Summary

review_run_id: `2026-06-20-workflow-management-design-vertical-redo-prompt-quality-run`
side_track: `stages/in-progress/maintenance-2026-06-20-api-review-prompt-quality.yaml`
target_prompt: `design-review-criteria-draft.md`
status: approved_for_corrected_design_review_run

## Flow

1. Main created `design-review-criteria-draft.md` as the corrected design review criteria.
2. Adversarial review used `anthropic-api / claude-sonnet-4-6`.
3. Adversarial found 5 issues: 3 WARN and 2 INFO.
4. Main revised the prompt draft to address all 5 issues.
5. Judgment review used `gemini-api / gemini-3.1-pro-preview` with the adversarial parsed findings as prior findings.
6. Judgment returned `findings: []`.

## Adversarial Findings And Resolution

| item | severity | resolution |
|---|---|---|
| Path-only source material risk in front matter | WARN | Front matter now says it is provenance only and lists embedded material keys. |
| Prior failure explanation did not explicitly forbid repeating the target-selection error | WARN | Added explicit instruction that `design.md` is the sole review target. |
| Required Check 9 referenced Requirement 12 without including its content | WARN | Added Requirement 12 registry / preflight context. |
| Unsupported additions were not mapped to severity | INFO | Added ERROR policy for unsupported design additions that constrain downstream work. |
| Out-of-scope wording could suppress findings about commit/push boundaries | INFO | Reworded to prohibit the model from authorizing those actions while still allowing findings about boundary preservation. |

## Judgment Result

`gemini-3.1-pro-preview` returned `findings: []`, so the revised prompt is approved for the corrected design triad-review API run.

The corrected design review must use:

- `--target .reviewcompass/specs/workflow-management/design.md`
- `--criteria-file .reviewcompass/specs/workflow-management/reviews/2026-06-20-workflow-management-design-vertical-redo-prompt-quality-run/design-review-criteria-draft.md`

## Boundary

This prompt-quality approval does not itself complete `stages/design.yaml#triad-review`, update `spec.json`, move the reopen gate, commit, or push.
