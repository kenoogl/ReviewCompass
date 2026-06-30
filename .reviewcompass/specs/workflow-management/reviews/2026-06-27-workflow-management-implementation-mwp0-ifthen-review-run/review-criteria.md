---
criteria_id: wm-implementation-mwp0-ifthen-2026-06-27
phase: implementation
stage: triad-review
---

# workflow-management implementation review — MWP-0: if/then constraint completeness

## Review Task

Review the target files for: MWP-0 T-020 if/then constraint completeness.

Primary judgment question:

Do the if/then constraints added to `next_action_response.schema.json` in allOf entries ①②③⑤ implement all field constraints specified in 受入 11(6)①②③⑤ without omission, weakening, or unsupported addition, and does the test class `SchemaIfThenConstraintTests` sufficiently cover the specified constraints?

Do not combine multiple independent judgments in this prompt. This review covers only if/then constraint completeness. Kind value separation and reason/reasons separation are reviewed in separate criteria.

## Review Target

The authoritative target is the file set supplied by the review runner.

- `.reviewcompass/schema/next_action_response.schema.json`
- `tests/tools/test_t020_kind_redesign.py`

Do not treat this criteria file or any author-written summary as a substitute for the target files.

## Source Materials

### mwp0-if-then-upstream-intent

Purpose: Requirement 2 / design / tasks intent for if/then field constraints on required_action values.
Use as intent-transfer evidence and background only. Do not treat as a replacement for target files.

受入 11(6) — required_action 値ごとのフィールド制約（原文）:

```
① commit_stop_point の時：active_gate=null・phase=null・stage=null・blocked_by.type="commit_stop_point"
② run_reopen_pending_gate の時：active_gate 非 null・phase/stage は active_gate と一致・blocked_by=null
③ run_reopen_drafting の時：active_gate は stages/<phase>.yaml#drafting 形式・phase/stage はその drafting 単位と一致
④ repair_workflow_state の時（T-015 実装済み、本レビュー対象外）
⑤ wait_for_human_decision の時：blocked_by.type で停止理由を区別
⑥ run_maintenance の時（T-015 実装済み、本レビュー対象外）

上記①〜⑥の制約は D-003 §4.2 で確定している制約の全てであり、これ以外の required_action 種別には
確定した追加フィールド制約はない（universal 必須フィールドのみが適用される）。
```

設計 §5.2 — if/then 制約の配置方針:

```
受入 11(6) の制約①②③⑤は if/then 構文で next_action の allOf 内に定義する（MWP-0 T-020 の責務）。
```

T-020 先送り事項(a) — 完了条件 3:

```
(a) 受入 11(6)①②③⑤の required_action 値ごとのフィールド制約を next_action_response.schema.json の
    if/then 構文で定義する（④の repair_reasons と⑥の action_parameters は T-015 完了条件2で対処済みのため除外）。

完了条件 3: スキーマの if/then 制約（先送り事項(a)）の失敗テストが作成され、実装で通過する。
```

## Required Checks

1. Check each of ①②③⑤ in the allOf section: does the if/then entry enforce all and only the constraints stated in 受入 11(6) for that required_action value?
2. Check the SchemaIfThenConstraintTests class in the test file: does it cover the failure cases for each constraint clause stated in 受入 11(6)①②③⑤?
3. Check that the constraints for ④ and ⑥ (T-015 implemented) are present but are not weakened or removed by the new entries.
4. Check that no if/then entry adds constraints not specified in 受入 11(6) or design §5.2.

## Out Of Scope

- Kind value separation (7 values vs 3 values) — separate criteria
- reason vs reasons semantic separation — separate criteria
- Commit, push, spec.json update, phase completion, or human approval delegation

## Finding Policy

- Use CRITICAL for a constraint that bypasses a required_action boundary or allows a forbidden state.
- Use ERROR for a missing constraint clause, a weakened constraint, or a test gap that leaves a constraint unverifiable.
- Use WARN for meaningful ambiguity, weak traceability between requirement and schema clause, or partial coverage.
- Use INFO only for minor non-blocking improvements.
- Use precise target locations such as `path`, `path:allOf[n]`, or `path:class.method`.
- Return `findings: []` only when every constraint in 受入 11(6)①②③⑤ is fully and accurately implemented and tested.
