# Requirements Triad Review Target: Workflow Management Requirement 13-16 Vertical Redo

## Review Target

This review judges only `.reviewcompass/specs/workflow-management/requirements.md`, specifically Requirement 13 through Requirement 16 and the directly related change intent / traceability text.

Do not judge `design.md` or `tasks.md` as review targets in this run. They may be mentioned only as downstream context if needed to detect unsupported requirements-level additions or missing requirements-level intent.

## Source Materials

Use these source materials as upstream decision materials for intent-transfer analysis:

- `docs/reviews/reopen-classification-2026-06-19-wm-requirement-13-16-vertical-redo.md`
- `docs/notes/2026-06-18-integrated-design-selection-execution-layers.md`
- `docs/notes/working/2026-06-18-mechanized-workflow-execution-design.md`
- `docs/notes/working/2026-06-19-integrated-design-requirements-missing.md`
- `docs/operations/SESSION_WORKFLOW_GUIDE.md#vertical-intent-transfer-review`

## Required Check

Independently review whether the upstream decision materials' purpose, responsibility boundaries, acceptance criteria, and forbidden actions have been inherited into Requirement 13 through Requirement 16 without omission, weakening, unsupported additions, or drift.

Pay particular attention to:

- Requirement 13: operation contract vocabulary, required_action mapping, single source of truth boundary between operation contracts and registry/preflight, read-only confirmation boundary, and fail-closed treatment for missing or stale contract references.
- Requirement 14: approval gate semantics, side track stack, workflow-state snapshot, read-only versus mutating operations, and proxy_model versus human-only decision boundaries.
- Requirement 15: structured effective prompt as a language-task specification, separation from mechanical tasks, machine-checkable prompt audit, and LLM judge audit as non-approving auxiliary analysis.
- Requirement 16: Phase 0 through Phase 6 ordering, phase completion conditions, no cross-phase implementation mixing, active reopen scope versus historical reopened flags, impact review scope, and proxy_model triage decision applicability predicates.

## Finding Policy

Return findings as YAML with a top-level `findings` list. Each finding must include:

- `severity`: CRITICAL, ERROR, WARN, or INFO
- `target_location`: file and section/requirement
- `description`: concrete issue
- `rationale`: why it matters
- `recommendation`: what should change

Use `ERROR` for omissions, weakened requirements, unsupported additions, or boundary drift that could make the requirements phase unsafe to approve.
Use `WARN` for ambiguity or traceability weakness that should be fixed before downstream design/tasks review if it affects later implementation readiness.
Use `INFO` only for non-blocking observations.

If there are no substantive findings, return `findings: []`.

## Out Of Scope

- Correctness of `design.md`
- Correctness or implementation-readiness of `tasks.md`
- Whether design/tasks already carry the requirements correctly
- Implementation code changes
- Commit, push, spec.json phase movement, or approval decisions

## Sensitive Information Check

No API keys, access tokens, passwords, personal contact information, or non-public third-party confidential data are intentionally included in this review target.
