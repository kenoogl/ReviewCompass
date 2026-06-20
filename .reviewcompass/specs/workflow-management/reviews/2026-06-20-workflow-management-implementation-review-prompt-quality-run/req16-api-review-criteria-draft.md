---
criteria_id: workflow-management-implementation-req16-review-2026-06-20-draft
phase: implementation.triad-review
review_target: .reviewcompass/specs/workflow-management/reviews/2026-06-20-workflow-management-implementation-review-run/req16-review-target-manifest.md
intended_actual_run_dir: .reviewcompass/specs/workflow-management/reviews/2026-06-20-workflow-management-implementation-req16-review-run
intended_variant: implementation_review_independent_3way_codex_operator
---

# Req 16 Implementation Review Criteria Draft

## Review Task

Primary judgment question:

Does the Req 16 implementation correctly provide read-only implementation phase controls and proxy triage decision checks that preserve human-required boundaries and active reopen / impact review scope separation?

## User Review Requirements

This is one item-specific prompt for `workflow-management / implementation / triad-review`.

- Review purpose: defect detection for Req 16 implementation.
- Review object: implementation phase schema/plan, operation-list, proxy triage decision schema/checks, review-wave consumer impact checks, and CLI wiring.
- Review focus: Phase 0–6 coverage, read-only operation-list and implementation-phase-check, fixed human-required predicate order, proxy decision evidence completeness/coverage, approval scope mismatch, active reopen scope versus `spec.json.reopened`, unresolved review-wave impact blocking.
- Scope boundaries: do not review Req 14 or Req 15 except where proxy triage checks consume approval/prompt evidence as source material.
- Prohibited actions: do not authorize commit, push, phase completion, approval, proxy application, or spec.json update.

## Review Target

The authoritative target file list is `req16-review-target-manifest.md`. The actual run must pass that manifest and every file listed there as target files. The inline summary below is for human readability only; if it differs from the manifest, report the mismatch.

Human-readable target summary: implementation phase schema/plan; proxy triage decision schema; implementation phase checker; operation-list builder; proxy triage decision checker; CLI wiring for `implementation-phase-check`, `operation-list`, and `proxy-triage-decision-check`; and five focused T-019 test files.

## Source Materials

Requirement 16 requires:

- Phase 0–6 implementation plan and schema, with entry criteria, exit criteria, allowed operations, forbidden operations, required tests, and commit boundary;
- Phase 2 read-only `operation-list --json` that reports operation `canonical_commands`, `effect_kind`, `approval_required`, `sequence`, and `pending_conflicts` without changing `next --json`;
- proxy triage decision schema containing raw response, parsed findings, decision prompt, proxy raw response, candidate decisions, selected decision, reasoning summary, final application target, and approval scope;
- human-required predicate based on evidence completeness, finding/cluster coverage, operation contract, approval gate record, review-wave impact, and active reopen / impact review scope;
- fixed priority where human-only decision, unresolved approval gate, `approval_required=true` operation, and unresolved review-wave impact override proxy labels like leave-as-is or proxy-approved;
- `spec.json.reopened` treated as history, not active reopen scope.

Design intent:

- `implementation-phase-check`, `operation-list`, and `proxy-triage-decision-check` are read-only CLI commands and must not mutate workflow state, review-run artifacts, approvals, or spec.json;
- proxy decision checks may return `DEVIATION` and block proxy apply, but they do not apply fixes or triage decisions;
- active reopen scope must come from reopen records, while `spec.json.reopened` remains historical context.
- Req 14 source evidence expected by proxy checks: approval gate record fields include `decision_scope`, `decision`, `decided_by`, `target_operation_id`, `target_required_action`, `binding_kind`, digests, and `consumed`.
- Req 15 source evidence expected by proxy/phase checks: structured prompt evidence fields include prompt manifest path/sha256, source artifact path/sha256, operation contract ID/sha256, and postcondition/on_completion compatibility status.

Tasks intent:

- T-019 required red tests first and implementation without altering those tests;
- tests must cover Phase 0–6 coverage, read-only operation-list preserving `next --json`, proxy evidence completeness, human-required priority, coverage mismatch, approval scope mismatch, fixed predicate order, and review-wave consumer impact blocking.

Verification before review:

- Structured evidence:
  - command: `.venv/bin/python3 -m pytest tests/workflow-management/test_implementation_phase_plan.py tests/workflow-management/test_operation_list_read_only.py tests/workflow-management/test_proxy_triage_decision_machine.py tests/workflow-management/test_review_wave_consumer_impact.py tests/workflow-management/test_implementation_phase_cli.py -q`
  - observed result: `13 passed`
  - scope: phase plan, operation-list read-only behavior, proxy triage decision checks, review-wave consumer impact, CLI.
- Related operation contract evidence:
  - command: `.venv/bin/python3 -m pytest tests/workflow-management/test_operation_contract_cli.py tests/workflow-management/test_operation_contract_schema.py tests/workflow-management/test_required_action_contract_mapping.py -q`
  - observed result: `12 passed`
  - scope: operation contract/schema/required_action connection.
- CLI evidence:
  - command: `.venv/bin/python3 tools/check-workflow-action.py implementation-phase-check --feature workflow-management --json`
  - observed result: `verdict=OK`
  - command: `.venv/bin/python3 tools/check-workflow-action.py operation-list --json`
  - observed result: `verdict=OK`, `operation_mode=read_only`.

## Required Checks

1. Check Phase 0–6 plan coverage and whether `active_phase` / criteria fields are meaningful enough for implementation control.
2. Check that `operation-list` is read-only and preserves `next --json` behavior.
3. Check that proxy triage decision schema and checker fail closed on missing raw/prompt/candidate/selected/reason/target evidence.
4. Check that human-required predicate priority cannot be bypassed by proxy-selected `leave-as-is` or `proxy_approved`.
5. Check that approval scope mismatch and coverage mismatch return `DEVIATION`.
6. Check that `spec.json.reopened` is not treated as active reopen scope.
7. Check that unresolved review-wave consumer impact blocks proxy apply unless evidence includes: a carry-forward register entry or equivalent structured register data, downstream impact decisions, and `spec_recheck.impacted_downstream_phases`.
8. Check that tests cover each listed fail-closed boundary.

## Out Of Scope

- General implementation of actual proxy apply or triage mutation.
- Req 14 approval gate internals except as source evidence for proxy blocking.
- Req 15 prompt audit internals except as source evidence for structured prompt controls.
- Any phase movement or approval.

## Finding Policy

Return YAML only, without Markdown fences.

Use `CRITICAL` for proxy or phase controls that would bypass human-required evidence or mutate state through read-only commands. Use `ERROR` for fail-closed or evidence completeness defects. Use `WARN` for meaningful plan, coverage, or auditability gaps. Use `INFO` for minor maintainability or wording issues that do not affect safety or auditability.

Return the parser-compatible YAML shape defined by the review runner. Return `findings: []` only when no actionable implementation issue is found for Req 16.
