# workflow-management design triad-review target r2

run_id: 2026-06-16-workflow-management-design-operation-registry-preflight-review-run-r2
phase: design
gate: stages/design.yaml#triad-review
criteria: workflow_management_operation_registry_preflight_design_reopen_triad_review_r2
supersedes: 2026-06-16-workflow-management-design-operation-registry-preflight-review-run

## Review Scope

This triad-review covers the workflow-management design update for the 2026-06-16 R-0 reopen: operation registry / preflight.

The previous design review run is superseded because its target summarized the design but did not include the normative design text. This r2 target includes the actual design excerpts needed to verify Requirement 12.

## Source Documents

- `.reviewcompass/specs/workflow-management/requirements.md`
- `.reviewcompass/specs/workflow-management/design.md`
- `docs/reviews/reopen-classification-2026-06-16-wm-operation-registry-preflight.md`
- `stages/in-progress/reopen-procedure-2026-06-16.yaml`
- `.reviewcompass/specs/workflow-management/reviews/2026-06-16-workflow-management-requirements-operation-registry-preflight-review-run-r2/triage.yaml`
- `.reviewcompass/specs/_cross_feature/reviews/2026-06-16-requirements-operation-registry-preflight-reopen-alignment-r2.md`

## Requirement 12 Acceptance Summary

Requirement 12 requires operation registry / preflight for:

1. operation registry
2. read-only preflight
3. common response schema and verdicts
4. command validation
5. worktree / pending / integrity conflict detection
6. review artifact / bundle preflight
7. serial_only commit approval chain
8. current-session formal record guard
9. nested issue handling
10. deployment / export preflight
11. all feature impact review scope and reopen scope separation
12. LLM / provider / model independence
13. `next --json` state uniqueness as an extension of Requirement 2

## Design Excerpt: Operation Contract

From `design.md` §Requirement 12 設計モデル:

```yaml
operation_id: string
kind: irreversible | review_artifact | workflow_state | evidence_capture | deployment_export
canonical_invocation:
  entrypoint: string
  subcommand: string
  options: [string]
  positional_args: [string]
  execution_context: repo_root | target_app_root | external_output
workflow_binding:
  phase: intent | feature-partitioning | requirements | design | tasks | implementation | null
  stage: drafting | triad-review | review-wave | alignment | approval | null
  gate: string | null
  next_action_kind: string | null
required_inputs: [string]
target_identity: [string]
planned_outputs: [string]
sequence_mode: parallel_ok | serial_only
worktree_policy: string
pending_conflict_policy: string
artifact_policy: string
vocabulary_refs: [string]
```

The design states that workflow-bound operations must identify phase, stage, gate, or `next_action.kind`, and that unknown kind, unknown sequence mode, nonexistent entrypoint, or parser / parser-adapter mismatch is a registry definition error.

## Design Excerpt: Preflight Response

```yaml
schema_version: string
operation_id: string
verdict: OK | WARN | DEVIATION
allowed_verdicts: [OK, WARN, DEVIATION]
sequence_mode: parallel_ok | serial_only
allowed_sequence_modes: [parallel_ok, serial_only]
state_refs:
  next_action: object | null
  workflow_state_files: [string]
  git_index: object | null
required_inputs: [string]
missing_inputs: [string]
template_available: boolean
target_identity: [string]
worktree_state: object
pending_conflicts: [object]
integrity_conflicts: [object]
checks: [object]
planned_outputs: [string]
canonical_commands: [string]
next_step: string
```

The design says workflow-state-dependent operations include active state dimensions in `state_refs.next_action`: current mainline, `required_action`, phase, stage, `reopen_scope`, `impact_review_scope`, direct / indirect features, flag policy, `next_pending_gate`, `next_drafting_gate`, `pending_gates`, `completed_gates`, superseded gate existence, and referenced state files.

The design says preflight is read-only and does not create review-run directory, manifest, approval record, session record, commit, deployment output, or export output.

## Design Excerpt: Fail-Closed Conditions

The design makes the following at least `DEVIATION`:

- missing required inputs
- canonical command / option / entrypoint mismatch with parser or parser adapter
- overwrite-protection policy violation
- serial_only operation executed out of order or in parallel
- approval-chain nonce / target digest / staged file set digest mismatch, expiry, consumed, invalidated, or wrong-target record
- current-session formal record request
- scope drift without side-track / follow-up / blocker record
- mismatch between `next` active state dimensions and operation contract workflow binding

## Design Excerpt: Specific Operation Families

Review artifact preflight initial operations:

- `post_write_review`
- `review_run_create`
- `triage_decide`
- `document_type_preflight`
- `review_criteria_preflight`
- `post_write_manifest_coverage_preflight`
- `approval_record_preflight`
- `bundle_preflight`

Deployment / export preflight covers deployment smoke, deploy package build, and runtime bundle export, including planned output files, existing outputs, overwrite policy, external app root writes, and existing bundle / smoke-run / app file conflicts.

## Design Excerpt: `next` State Uniqueness

The design states:

```text
next --json は Requirement 2 が所有する。Requirement 12 は、その出力を operation preflight が一意に参照できるよう拡張する。
```

`reopen_in_progress` must include:

- current mainline
- `required_action`
- phase / stage
- `reopen_scope`
- `impact_review_scope`
- direct / indirect features
- flag policy
- `next_pending_gate`
- `next_drafting_gate`
- `pending_gates`
- `completed_gates`
- superseded gate existence
- referenced state files

The design defines:

```text
reopen_scope は正本を再オープンして flag を false に戻す feature、
impact_review_scope は正本変更要否だけを確認し flag を維持する feature
```

It also requires consistency with `feature_impact_decisions`, `spec.json`, `pending_gates`, `drafting_completed_gates`, and `downstream_impact_decisions`.

## Design Excerpt: Phase Boundary

The design states:

```text
Phase 1: read-only registry / preflight. 成果物を作らず、operation 可否と衝突を返す。
Phase 2: runner-enabled operation. Phase 1 の preflight が OK または明示許可された WARN の場合のみ、実際の artifact 作成・更新を行う。
```

Implementation should TDD Phase 1 first. Phase 2 is separate.

## Design Excerpt: Traceability And XDI

The design adds traceability rows for Requirement 12 acceptance criteria 1-13 to §Req 12 設計モデル. It adds:

```text
XDI-WM-004: operation registry / preflight 契約
```

This avoids collision with existing:

```text
XDI-WM-003: 配布側複数 LLM 入口の配布契約
```

The requirements document was also updated to reference `XDI-WM-004`.

## Review Questions

1. Does the design fully cover Requirement 12 acceptance criteria 1-13?
2. Is the operation registry location and ownership boundary appropriate for workflow-management?
3. Is the read-only preflight / runner-enabled operation split clear enough?
4. Does the design preserve Requirement 2 ownership of `next --json` while extending it for state uniqueness?
5. Does the design make `reopen_scope` and `impact_review_scope` traceable enough to determine flag false/true behavior later?
6. Are review artifact, bundle, manifest, approval, criteria, document-type, and drift checks sufficiently covered without becoming implementation detail?
7. Does the design keep LLM / provider / model names out of pass/fail conditions?
8. Are there any design-level gaps before moving to design review-wave?
9. Did XDI numbering avoid collision and keep requirements / design aligned?
10. Is any part of the design too implementation-specific for design phase?

## Expected Output

Return structured findings only. Use severity `ERROR` for blockers, `WARN` for corrections that should be made before design review-wave, and `INFO` for non-blocking observations.
