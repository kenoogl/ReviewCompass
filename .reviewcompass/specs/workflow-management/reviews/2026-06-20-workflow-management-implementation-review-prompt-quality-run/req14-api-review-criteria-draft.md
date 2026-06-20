---
criteria_id: workflow-management-implementation-req14-review-2026-06-20-draft
phase: implementation.triad-review
review_target: .reviewcompass/specs/workflow-management/reviews/2026-06-20-workflow-management-implementation-review-run/req14-review-target-manifest.md
intended_actual_run_dir: .reviewcompass/specs/workflow-management/reviews/2026-06-20-workflow-management-implementation-req14-review-run
intended_variant: implementation_review_independent_3way_codex_operator
---

# Req 14 Implementation Review Criteria Draft

## Review Task

Primary judgment question:

Does the Req 14 implementation correctly preserve the approved requirements → design → tasks intent for approval gates, side-track stack, and workflow-state snapshots, without creating an approval/proxy bypass or unintended state mutation path?

## User Review Requirements

This is one item-specific prompt for `workflow-management / implementation / triad-review`.

- Review purpose: defect detection for Req 14 implementation.
- Review object: Req 14 schema, modules, CLI exposure, and tests.
- Review focus: approval/proxy boundary, decision consumption, digest/target binding, side-track scope and depth, snapshot drift detection, read-only CLI boundaries.
- Scope boundaries: do not review Req 15 or Req 16 except where `check-workflow-action.py` wiring creates a direct boundary issue.
- Prohibited actions: do not authorize commit, push, phase completion, approval, proxy application, or spec.json update.

## Review Target

The authoritative target file list is `req14-review-target-manifest.md`. The actual run must pass that manifest and every file listed there as target files, so the model sees current file contents rather than path stubs.

Human-readable target summary: approval/side-track/snapshot schemas, their three modules, `check-workflow-action.py` CLI wiring for `workflow-snapshot` and `side-track-stack current`, and four focused test files. If this summary and the manifest differ, the manifest is authoritative and the review should report the mismatch.

## Source Materials

Requirement 14 requires:

- approval gate records with decision scope, target operation, target required action, artifact digest, staged file set digest, source digest, next-action expectation, and consumed state;
- proxy / human boundaries where `human_only` cannot be satisfied by proxy decision;
- side-track stack with allowed files, max depth, return conditions, and mainline restoration;
- workflow-state snapshot containing current work, side tracks, git tree summary, post-write manifest summary, and workflow state summary;
- drift detection for pending/completed gates, staged file set, operation contract, and snapshot evidence.

Design intent:

- read-only operations must stay read-only: `workflow-snapshot` and `side-track-stack current` must not mutate files;
- mutating helper functions, if present in modules, may only be accepted when they are bounded by explicit operation contract / caller responsibility and are not exposed by the read-only CLI;
- decision records must fail closed on target mismatch, digest mismatch, unresolved/non-approved decision, or human-only boundary.

Tasks intent:

- T-017 required red tests before implementation;
- tests must include negative cases for `binding_kind=none`, target operation mismatch, digest mismatch, side-track allowed_files/max_depth, and snapshot completed gate / operation contract drift.
- TDD ordering is background only for this API review. Judge current test and implementation content; do not reconstruct git history.

Verification before review:

- Structured evidence:
  - command: `.venv/bin/python3 -m pytest tests/workflow-management/test_approval_gate.py tests/workflow-management/test_side_track_stack.py tests/workflow-management/test_workflow_state_snapshot.py tests/workflow-management/test_workflow_snapshot_cli.py -q`
  - observed result: `21 passed`
  - scope: approval gate, side-track stack, workflow-state snapshot, workflow-snapshot CLI.
- Full workflow-management test sweep:
  - command: `.venv/bin/python3 -m pytest tests/workflow-management -q`
  - observed result: `55 passed`
  - scope: all workflow-management focused tests present at implementation drafting completion.

## Required Checks

1. Check that approval records fail closed for missing or mismatched target operation, required action, digest, decision scope, and consumed state.
2. Check that proxy decisions cannot satisfy `human_only` gates or approval-required target operations.
3. Check that side-track stack constraints cannot be bypassed by missing allowed files, excessive depth, or ambiguous return condition.
4. Check that snapshot output has at least these structured evidence groups: `current_work`, `active_side_tracks`, `git_tree_summary`, `post_write_manifest_summary`, and `workflow_state_summary`; and that tests cover completed gate / operation contract drift.
5. Check that read-only CLI commands in scope do not write files or consume decisions.
6. Check that tests include explicit negative coverage for the fail-closed boundaries listed above.

## Out Of Scope

- Req 15 structured prompt audit.
- Req 16 implementation phase plan and proxy triage decision machine.
- Approval of phase movement or any spec.json update.

## Finding Policy

Return YAML only, without Markdown fences.

Use `CRITICAL` for approval/proxy bypass or unintended mutation by read-only CLI. Use `ERROR` for fail-closed defects or missing required evidence fields. Use `WARN` for meaningful test/evidence coverage gaps. Use `INFO` for minor maintainability or wording issues that do not affect safety or auditability.

Return the parser-compatible YAML shape defined by the review runner. Return `findings: []` only when no actionable implementation issue is found for Req 14.
