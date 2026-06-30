---
criteria_id: wm-implementation-mwp0-kind-sep-2026-06-27
phase: implementation
stage: triad-review
---

# workflow-management implementation review — MWP-0: kind value separation

## Review Task

Review the target files for: MWP-0 kind value separation between `next --json` and `commit-preflight`.

Primary judgment question:

Does the implementation ensure that `next --json` outputs only the 7 specified kind values and `commit-preflight` outputs only the 3 specified kind values, as required by 受入 12 and T-020 completion conditions 1 and 2?

Do not combine multiple independent judgments in this prompt. This review covers only kind value separation. if/then constraint completeness and reason/reasons separation are reviewed in separate criteria.

## Review Target

The authoritative target is the file set supplied by the review runner.

- `.reviewcompass/schema/next_action_response.schema.json`
- `.reviewcompass/schema/commit_preflight_response.schema.json`
- `commit-preflight-implementation-excerpt.py` (extracted from `tools/check-workflow-action.py` lines 4151-4223)
- `tests/tools/test_t020_kind_redesign.py`

**Note on `next --json` implementation**: The `cmd_next` function in `tools/check-workflow-action.py` is several hundred lines long and is not included as a target. The `next_action_response.schema.json` schema enum and the test classes `NextActionSchemaKindValueTests` and `NextActionKindBehaviorTests` in `test_t020_kind_redesign.py` are the primary verification artifacts for the `next --json` kind constraint. If the schema enum is correct and the tests verify it, that constitutes the implementable scope of check for this review.

**Note on delegated functions in the excerpt**: The excerpt for `_commit_preflight_next_action` contains two function calls whose implementations are not provided — `build_in_progress_next_action` (line 4154) and `resolve_normal_workflow_commit_stop_point_action` (line 4215). When those functions' return kind values cannot be determined from the provided material, report that as WARN rather than ERROR.

Do not treat this criteria file or any author-written summary as a substitute for the target files.

## Source Materials

### mwp0-kind-separation-upstream-intent

Purpose: Requirement 2 受入 12 and T-020 completion conditions 1–2 as upstream intent for kind value separation.
Use as intent-transfer evidence and background only. Do not treat as a replacement for target files.

受入 12 — kind 値分離の仕様（原文）:

```
本機能は commit_candidate、commit_mixing_risk、commit_unit_stale の3種類の判定を next --json の
kind から除外し、commit-preflight サブコマンドの出力にのみ含める。これらの判定は「作業の現在地カテゴリ」
ではなく「コミット操作の前確認」であり、next --json の kind は作業の現在地のみを示す7種類
（completed / in_progress / blocking_in_progress / verification_pending /
  reopen_in_progress / feature_definition_required / unknown）に限定する。
```

T-020 完了条件 1–2:

```
1. next --json の kind 値域が7値に限定され、旧3値が出力されないことを pytest で確認できる。
2. commit-preflight サブコマンドが3値の kind を返し、他の kind を返さないことを pytest で確認できる。
```

### kind-value-constants

```
next --json の許容 kind 値（7つ）:
  in_progress, blocking_in_progress, verification_pending,
  reopen_in_progress, feature_definition_required, completed, unknown

commit-preflight の許容 kind 値（3つ）:
  commit_candidate, commit_mixing_risk, commit_unit_stale
```

## Required Checks

1. Check that `next_action_response.schema.json` defines exactly the 7 permitted kind values in the enum.
2. Check that `commit_preflight_response.schema.json` defines exactly the 3 permitted kind values in the enum.
3. Check that the `_commit_preflight_next_action` implementation in the excerpt can only return kind values permitted for commit-preflight under 受入 12. Trace all code paths. For delegated functions whose implementation is not in the target, report whether the kind they produce is determinable or indeterminate and use WARN for indeterminate cases.
4. Check that the test classes `NextActionSchemaKindValueTests`, `CommitPreflightSchemaTests`, `NextActionKindBehaviorTests`, and `CommitPreflightKindBehaviorTests` in `test_t020_kind_redesign.py` cover the key directions of T-020 completion conditions 1 and 2.
5. Check whether the test `test_commit_preflight_kind_is_always_commit_related` reflects the constraint in 受入 12 that commit-preflight must return only the 3 specified kind values. Specifically, determine whether the assertIn condition in that test is consistent with the 3-value constraint in 受入 12.

## Out Of Scope

- if/then field constraints (①②③⑤) — separate criteria
- reason vs reasons semantic separation — separate criteria
- Commit, push, spec.json update, phase completion, or human approval delegation

## Finding Policy

- Use CRITICAL for a code path that definitively violates the kind value boundary stated in 受入 12.
- Use ERROR for a schema enum mismatch, a missing test direction, a test assertion that contradicts the acceptance criterion, or a code path that makes the kind separation unverifiable.
- Use WARN for meaningful ambiguity, weak test traceability, or a code path where the kind value cannot be determined from the provided material.
- Use INFO only for minor non-blocking improvements.
- Use precise target locations such as `path`, `path:function`, or `path:class.method`.
- Return `findings: []` only when kind separation is fully and correctly implemented and verified.
