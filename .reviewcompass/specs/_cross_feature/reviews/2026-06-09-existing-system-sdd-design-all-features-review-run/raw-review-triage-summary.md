# Design Pre-Drafting Gap Audit Summary

## Scope

- Reopen: `reopen-procedure-2026-06-09-existing-system-sdd-code-drift`
- Intended phase gate: `stages/design.yaml#triad-review`
- Review run: `2026-06-09-existing-system-sdd-design-all-features-review-run`
- Target: design-stage impact of the existing-system SDD / code drift intent across all features

## Inputs

- `.reviewcompass/specs/_cross_feature/reviews/2026-06-09-existing-system-sdd-design-all-features-review-run/review-target.md`
- `.reviewcompass/specs/_cross_feature/reviews/2026-06-09-existing-system-sdd-design-all-features-review-run/triage.yaml`
- `.reviewcompass/specs/conformance-evaluation/design.md`
- `.reviewcompass/specs/workflow-management/design.md`
- `stages/in-progress/reopen-procedure-2026-06-09-existing-system-sdd-code-drift.yaml`

## Raw Review Result

Three role reviews were collected, but the run is not treated as the formal design triad-review. It audited the state before design drafting and found that drafting had not yet been performed.

- `claude-sonnet-4-6`: 16 findings: 6 CRITICAL, 3 ERROR, 5 WARN, 2 INFO.
- `gpt-5.4`: 7 findings: 2 ERROR, 3 WARN, 2 INFO.
- `gemini-3.1-pro-preview`: 3 findings: 2 ERROR, 1 INFO.

## Triage Summary

### CE design is stale against Requirement 10

Decision: must-fix.

`conformance-evaluation/design.md` still says requirements.md has 9 requirements and does not define Requirement 10. It needs a design model for the existing-system / post-hoc intent mode, including inputs, output candidate fields, classification values, tasks boundary, workflow-management handoff, and `XDI-CE-002` traceability.

### WM design is stale against Requirement 9

Decision: must-fix.

`workflow-management/design.md` still says requirements.md has 8 requirements and does not define Requirement 9. It needs a design model for post-hoc intent downstream propagation, CE evaluation record intake, `downstream_impact_decisions`, conflict stop points, side-track distinction, and `XDI-WM-002` traceability.

### CE / WM boundary must be explicit in both designs

Decision: must-fix as part of the two direct design updates.

CE should extract and classify evidence-backed candidates. WM should consume those records through the formal reopen procedure and own downstream gate decisions. The handoff contract must be stated on both sides.

### Tasks boundary must remain narrow

Decision: must-fix in CE design.

CE may use tasks.md as a reference input and may emit downstream impact candidates, but must not infer or recreate tasks.md as a formal output.

### Indirect features

Decision: no immediate design.md body change is required for foundation, runtime, evaluation, analysis, or self-improvement.

The review confirms all seven features are in scope. The indirect features should remain in the design-stage review-wave / alignment checks, but the blocking design edits are in the two direct features.

## Recommendation

Do not complete `stages/design.yaml#triad-review` yet. Treat this run as a pre-drafting gap audit.

Next work should update:

- `.reviewcompass/specs/conformance-evaluation/design.md`
- `.reviewcompass/specs/workflow-management/design.md`

After those fixes, rerun or re-check design triad-review before moving to design review-wave.
