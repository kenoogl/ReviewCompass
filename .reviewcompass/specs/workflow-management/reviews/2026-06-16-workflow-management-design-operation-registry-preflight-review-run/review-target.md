# workflow-management design triad-review target

run_id: 2026-06-16-workflow-management-design-operation-registry-preflight-review-run
phase: design
gate: stages/design.yaml#triad-review
criteria: workflow_management_operation_registry_preflight_design_reopen_triad_review

## Review Scope

This triad-review covers the workflow-management design update for the 2026-06-16 R-0 reopen: operation registry / preflight.

Review whether `design.md` correctly implements the approved Requirement 12 r2 without overstepping into tasks or implementation.

Key approved requirements:

- Operation registry / preflight is owned by workflow-management.
- Requirement 12 extends existing Requirement 2 `next --json` behavior; it does not create a competing `next` source of truth.
- `reopen_scope` and `impact_review_scope` must be distinct and machine-readable.
- `next --json` must uniquely identify the active reopen state.
- Preflight Phase 1 is read-only and must not create review-run directories, manifests, approval records, session records, commits, deployment outputs, or export outputs.
- Runner-enabled operation is Phase 2 and must be separated from read-only preflight.
- Judgments must be LLM / provider / model independent.

## Source Documents

- `.reviewcompass/specs/workflow-management/requirements.md`
- `.reviewcompass/specs/workflow-management/design.md`
- `docs/reviews/reopen-classification-2026-06-16-wm-operation-registry-preflight.md`
- `stages/in-progress/reopen-procedure-2026-06-16.yaml`
- `.reviewcompass/specs/workflow-management/reviews/2026-06-16-workflow-management-requirements-operation-registry-preflight-review-run-r2/triage.yaml`
- `.reviewcompass/specs/_cross_feature/reviews/2026-06-16-requirements-operation-registry-preflight-reopen-alignment-r2.md`

## Design Delta

The design now adds:

```text
Requirement 12 設計モデル：operation registry / preflight（Req 12）
```

The new section defines:

1. `stages/operation-registry.yaml` as the operation registry location.
2. Operation contract fields, including canonical invocation and workflow binding.
3. Read-only preflight response schema.
4. Verdict and fail-closed handling.
5. Command validation via parser / parser adapter.
6. Worktree, pending, and integrity conflict separation.
7. Review artifact preflight including bundle / manifest / criteria / document-type / approval / drift checks.
8. Serial-only commit approval chain behavior.
9. Current-session formal record guard.
10. Nested issue handling.
11. Deployment / export preflight.
12. Reopen scope / impact review scope and `next` state uniqueness.
13. LLM / provider / model independence.
14. Phase 1 / Phase 2 boundary.

The design also updates:

- Overview / goals to include Requirement 12.
- Requirements traceability table for Requirement 12.
- XDI-WM-004 for operation registry / preflight, avoiding collision with existing XDI-WM-003.
- Change Intent for the 2026-06-16 R-0 design update.

## Review Questions

1. Does the design fully cover Requirement 12 acceptance criteria 1-13?
2. Is `stages/operation-registry.yaml` a reasonable design-level location and ownership boundary?
3. Is the read-only preflight / runner-enabled operation split clear enough?
4. Does the design preserve Requirement 2 ownership of `next --json` while extending it for state uniqueness?
5. Does the design make `reopen_scope` and `impact_review_scope` traceable enough to determine flag false/true behavior later?
6. Are review artifact, bundle, manifest, approval, criteria, document-type, and drift checks sufficiently covered without becoming implementation detail?
7. Does the design keep LLM / provider / model names out of pass/fail conditions?
8. Are there any design-level gaps before moving to design review-wave?
9. Did the XDI numbering change avoid collision and keep requirements / design aligned?

## Expected Output

Return structured findings only. Use severity `ERROR` for blockers, `WARN` for corrections that should be made before design review-wave, and `INFO` for non-blocking observations.
