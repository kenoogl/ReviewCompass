---
criteria_id: wm-implementation-mwp0-reason-2026-06-27
phase: implementation
stage: triad-review
---

# workflow-management implementation review — MWP-0: reason vs reasons separation

## Review Task

Review the target files for: MWP-0 T-020 prior deferred item (b) — reason vs reasons semantic separation.

Primary judgment question:

Is the semantic distinction between the `reason` field inside `next_action` (described in design §5.3 as a common field for all kind values) and the top-level `reasons` array (one of the 5 required fields in the response) sufficiently defined in the schema and upstream design documents, and is the deferred item (b) from T-020 addressed?

Do not combine multiple independent judgments in this prompt. This review covers only the reason vs reasons separation. if/then constraints and kind value separation are reviewed in separate criteria.

## Review Target

The authoritative target is the file set supplied by the review runner.

- `.reviewcompass/schema/next_action_response.schema.json`
- `design-section-5-2-5-3-excerpt.md` (verbatim excerpt from `.reviewcompass/specs/workflow-management/design.md` §5.2 and §5.3, covering the reason/reasons fields and next_action required field list)

Do not treat this criteria file or any author-written summary as a substitute for the target files.

## Source Materials

### mwp0-reason-upstream-intent

Purpose: T-020 deferred item (b) text for background context.
The authoritative design document content is provided as `design-section-5-2-5-3-excerpt.md` in the review target above.
Use this section for background intent only.

T-020 先送り事項(b):

```
next_action 内の reason フィールドと最上位の reasons 配列の責務差を設計書と実装で明確化する。
```

T-020 完了条件一覧（reason に関連する条件の明示なし）:

```
1. next --json の kind 値域が7値に限定されること
2. commit-preflight サブコマンドが3値の kind を返すこと
3. スキーマの if/then 制約の失敗テストが作成され通過すること
4. WORKFLOW_NAVIGATION.md の更新
5. 廃止表現の統一

先送り事項(b)（reason vs reasons の責務明確化）に対応する完了条件は T-020 完了条件一覧に明示されていない。
```

## Required Checks

1. Check whether `next_action_response.schema.json` defines a `reason` field within `next_action.properties` or `next_action.required`, and whether this matches the intent described in design §5.3 (all-kind common field).
2. Check whether the top-level `reasons` array defined in the schema has a schema-level description or differentiation from the inner `reason` field.
3. Check whether the deferred item (b) from T-020 — "clarify the responsibility difference between the inner reason field and the top-level reasons array in design and implementation" — is addressed by either the schema (`next_action_response.schema.json`) or the design document excerpt (`design-section-5-2-5-3-excerpt.md`).
4. Check whether the presence or absence of `reason` in the schema matches what the design document (`design-section-5-2-5-3-excerpt.md` §5.3 common fields table) specifies. If the schema omits `reason` from `next_action.required` or `next_action.properties` while the design lists it as a common field, determine whether that omission is documented as intentional anywhere in the target files.

## Out Of Scope

- if/then field constraints — separate criteria
- kind value separation — separate criteria
- Commit, push, spec.json update, phase completion, or human approval delegation

## Finding Policy

- Use CRITICAL for a contradiction that breaks the schema's required field contract.
- Use ERROR for an unaddressed T-020 deferred item (b) where the required clarification is missing from both schema and upstream documents, or for a discrepancy between design §5.3 and the schema that is not intentional and not documented.
- Use WARN for meaningful ambiguity, undocumented intentional omission, or incomplete traceability between design §5.3 and schema.
- Use INFO only for minor non-blocking improvements.
- Use precise target locations such as `path` or `path:section`.
- Return `findings: []` only when the reason vs reasons distinction is sufficiently defined and T-020 deferred item (b) is verifiably addressed.
